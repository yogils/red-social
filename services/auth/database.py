from sqlmodel import create_engine, SQLModel
engine = create_engine("postgresql://postgres@auth-db:5432/unal_auth")
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)