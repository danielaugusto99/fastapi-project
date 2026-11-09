from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Project",
    description="API backend modular desenvolvida com FastAPI, PostgreSQL e Docker.",
    version="1.0.0",
)


@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "API rodando com sucesso!"}