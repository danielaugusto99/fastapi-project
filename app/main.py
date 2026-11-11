from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os

# 1. Configuração do Banco de Dados PostgreSQL (usando variáveis de ambiente do docker-compose)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@postgres_db:5432/fastapi_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Modelo SQLAlchemy (Tabela no Banco de Dados)
class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

# Cria a tabela no banco automaticamente ao iniciar
Base.metadata.create_all(bind=engine)

# 3. Schemas Pydantic (Validação de Dados)
class TaskCreate(BaseModel):
    title: str
    description: str | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool

    model_config = ConfigDict(from_attributes=True)

# 4. Dependência para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Inicialização do FastAPI
app = FastAPI(
    title="API de Tarefas com FastAPI e PostgreSQL",
    version="1.0.0"
)

# --- Rotas da API ---

@app.get("/", summary="Raiz da API")
def read_root():
    return {"message": "Bem-vindo à API do FastAPI com PostgreSQL rodando no Docker!"}

@app.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Criar uma nova tarefa")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(title=task.title, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=list[TaskResponse], summary="Listar todas as tarefas")
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(TaskModel).offset(skip).limit(limit).all()
    return tasks

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar uma tarefa")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    db.delete(db_task)
    db.commit()
    return None