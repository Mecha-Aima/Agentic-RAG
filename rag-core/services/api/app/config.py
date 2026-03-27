from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration from environment variables.
    """

    ENV: str = "prod"
    LOG_LEVEL: str = "INFO"

    # Database (RDS PostgreSQL free tier)
    DATABASE_URL: str

    # Redis (in-cluster or local)
    REDIS_URL: str

    # Vector DB (Qdrant)
    QDRANT_HOST: str = "qdrant-svc"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "rag_collection"

    # Graph DB (Neo4j AuraDB Free recommended)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str

    # AWS S3
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str

    # LLM (Groq free tier — replaces Ray Serve + vLLM)
    GROQ_API_KEY: str

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
