import os
import subprocess
import tkinter as tk
from tkinter import simpledialog


# Функция для создания виртуальной среды
def create_virtual_env(project_path):
    venv_path = os.path.join(project_path, "venv")
    subprocess.run(["python", "-m", "venv", venv_path])
    return venv_path


# Функция для установки зависимостей
def install_dependencies(venv_path):
    pip_path = os.path.join(venv_path, "Scripts", "pip")
    subprocess.run([pip_path, "install", "fastapi", "uvicorn", "sqlalchemy", "alembic"])


# Функция для создания структуры проекта
def create_project_structure(project_path, api_name):
    app_dir = os.path.join(project_path, "app")
    os.makedirs(os.path.join(app_dir, "models"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "api", "v1"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "services"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "crud"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "schemas"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "migrations", "versions"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "tests"), exist_ok=True)

    # Создание файлов проекта
    with open(os.path.join(app_dir, "main.py"), "w") as f:
        f.write(f'''from fastapi import FastAPI
from app.api.v1 import user

app = FastAPI()

@app.get("/")
def read_root():
    return {{"message": "Welcome to {api_name}!"}}

# Подключение роутов
app.include_router(user.router)
''')

    with open(os.path.join(app_dir, "config.py"), "w") as f:
        f.write('''from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/db"

    class Config:
        env_file = ".env"

settings = Settings()
''')

    with open(os.path.join(app_dir, "database.py"), "w") as f:
        f.write('''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')

    with open(os.path.join(app_dir, "models", "user.py"), "w") as f:
        f.write('''from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
''')

    with open(os.path.join(app_dir, "schemas", "user_schema.py"), "w") as f:
        f.write('''from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class User(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True
''')

    with open(os.path.join(app_dir, "api", "v1", "user.py"), "w") as f:
        f.write('''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import user_schema
from app.models import user as user_model
from app.crud import user_crud
from app.database import get_db

router = APIRouter()

@router.post("/users/", response_model=user_schema.User)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db=db, user=user)
''')

    with open(os.path.join(app_dir, "crud", "user_crud.py"), "w") as f:
        f.write('''from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate

def create_user(db: Session, user: UserCreate):
    hashed_password = user.password  # В идеале используйте хэширование пароля
    db_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
''')

    with open(os.path.join(project_path, ".env"), "w") as f:
        f.write('''DATABASE_URL=postgresql://user:password@localhost/db
''')

    with open(os.path.join(project_path, "alembic.ini"), "w") as f:
        f.write('''# Alembic configuration
[alembic]
script_location = migrations
''')

    with open(os.path.join(project_path, "requirements.txt"), "w") as f:
        f.write('''fastapi
uvicorn
sqlalchemy
alembic
''')

    with open(os.path.join(project_path, "README.md"), "w") as f:
        f.write(f"# {api_name}\n\nThis is a FastAPI project.")


# Функция для создания проекта
def create_project():
    root = tk.Tk()
    root.withdraw()  # Скрыть главное окно Tkinter

    # Ввод названия проекта
    project_name = simpledialog.askstring("Input", "Enter the project name:")
    if not project_name:
        return
    project_path = os.path.join(os.getcwd(), project_name)

    # Ввод названия API
    api_name = simpledialog.askstring("Input", "Enter the API name:")
    if not api_name:
        return

    # Создание директории проекта
    os.makedirs(project_path, exist_ok=True)

    # Создание виртуальной среды
    venv_path = create_virtual_env(project_path)

    # Установка зависимостей
    install_dependencies(venv_path)

    # Создание структуры проекта
    create_project_structure(project_path, api_name)

    print(f"Project {project_name} created successfully at {project_path}")


if __name__ == "__main__":
    create_project()
