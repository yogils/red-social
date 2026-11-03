from sqlmodel import create_engine, SQLModel

DATABASE_URL = "postgresql://postgres@users-db:5432/unal_users"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)