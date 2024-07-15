import json
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Crear la URL de conexión a la base de datos
URL_DATABASE = "postgresql://postgres.srkyeytlicogoypkdhow:8HEdl7thmsVplYLt@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
engine = create_engine(URL_DATABASE)  # Crear la conexión a la base de datos

# Si se quiere usar SQLite en lugar de PostgreSQL, se puede usar el siguiente código
# URL_DATABASE = "sqlite:///./Crafters.db"
# engine = create_engine(URL_DATABASE, connect_args={"check_same_thread": False})

# Crear una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    Function to get a database session.

    Returns:
        Session: The database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# Crear una clase base para las clases de la base de datos
Base = declarative_base()
