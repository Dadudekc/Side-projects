from fastapi import FastAPI
from app.api.v1.endpoints import project, self_improve

app = FastAPI()

app.include_router(project.router, prefix="/api/v1/projects")
app.include_router(self_improve.router, prefix="/api/v1/self-improve")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI_Architect API"}
