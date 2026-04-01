from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
  """Dependency injection: cung cấp DB session cho mỗi request."""
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
