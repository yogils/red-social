from sqlmodel import create_engine

AUTH_DATABASE_URL = "postgresql://postgres@auth-db:5432/unal_auth"
USERS_DATABASE_URL = "postgresql://postgres@users-db:5432/unal_users"

auth_engine = create_engine(AUTH_DATABASE_URL)
users_engine = create_engine(USERS_DATABASE_URL)
