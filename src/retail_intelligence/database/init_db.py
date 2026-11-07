
from retail_intelligence.database.base import Base
from retail_intelligence.database.connection import engine

# Import models so SQLAlchemy registers their table definitions.
from retail_intelligence.database import models


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

    for table_name in Base.metadata.tables:
        print(f"- {table_name}")


if __name__ == "__main__":
    initialize_database()
