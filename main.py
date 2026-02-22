from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv
import bcrypt
import os
import uuid
from schemas import IssueCreate, UserCreate, UserLogin

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


@app.get("/")
def home():
    return {"ok": True}


@app.post("/signup")
def signup(user: UserCreate):
    try:
        existing = supabase.table("app_user").select("user_id").eq("email", user.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered.")

        role = supabase.table("role").select("role_id").eq("role_name", "citizen").execute()
        if not role.data:
            raise HTTPException(status_code=500, detail="Citizen role not found.")
        role_id = role.data[0]["role_id"]

        hashed = hash_password(user.password)

        res = supabase.table("app_user").insert({
            "full_name":            user.full_name,
            "email":                user.email,
            "phone": user.phone if user.phone else None,
            "password":             hashed,
            "role_id":              role_id,
            "is_anonymous_allowed": True,
        }).execute()

        new_user = res.data[0]
        return {
            "ok":      True,
            "user_id": new_user["user_id"],
            "name":    new_user["full_name"],
            "email":   new_user["email"],
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


@app.post("/login")
def login(user: UserLogin):
    try:
        res = supabase.table("app_user").select("*").eq("email", user.email).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="No account found with this email.")

        db_user = res.data[0]

        if not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Incorrect password.")

        return {
            "ok":      True,
            "user_id": db_user["user_id"],
            "name":    db_user["full_name"],
            "email":   db_user["email"],
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


@app.get("/categories")
def get_categories():
    res = supabase.table("categories").select("category_id, category_name").execute()
    return res.data


@app.get("/departments")
def get_departments():
    res = supabase.table("departments").select("department_id, department_name").execute()
    return res.data


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        file_name  = f"{uuid.uuid4()}-{file.filename}"
        supabase.storage.from_("issue-images").upload(
            file_name, file_bytes, {"content-type": file.content_type}
        )
        public_url = supabase.storage.from_("issue-images").get_public_url(file_name)
        return {"url": public_url}
    except Exception as e:
        return {"error": str(e)}


@app.post("/create-issue")
def create_issue(issue: IssueCreate):
    try:
        issue_data = supabase.table("issue").insert({
            "title":             issue.title,
            "description":       issue.description,
            "category_id":       issue.category_id,
            "department_id":     issue.department_id,
            "location_id":       issue.location_id,
            "user_id":           issue.user_id,
            "current_status_id": issue.current_status_id,
        }).execute()

        issue_id = issue_data.data[0]["issue_id"]

        supabase.table("issue_history").insert({
            "issue_id":   issue_id,
            "status_id":  issue.current_status_id,
            "updated_by": None,
            "remarks":    issue.remarks,
        }).execute()

        for img_url in issue.images:
            supabase.table("issue_image").insert({
                "issue_id":  issue_id,
                "image_url": img_url,
            }).execute()

        return {"ok": True, "issue_id": issue_id}

    except Exception as e:
        return {"error": str(e)}