from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from resumes import router as resumes_router
from optimization import router as optimization_router
from pdf import router as pdf_router
from dashboard import router as dashboard_router
from database import Base,engine
from userInfo import router as userInfo_router


Base.metadata.create_all(bind=engine)  # Add this to a script or main.py
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

app.include_router(auth_router)
app.include_router(resumes_router)
app.include_router(optimization_router)
app.include_router(pdf_router)
app.include_router(dashboard_router)
app.include_router(userInfo_router)