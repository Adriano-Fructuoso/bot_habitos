import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Carrega variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./habit_bot.db")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if IS_SQLITE else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    **({"pool_size": 5, "max_overflow": 10} if not IS_SQLITE else {}),
)

# Cria a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def get_db():
    """Função para obter uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""

    Base.metadata.create_all(bind=engine)


def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com banco de dados estabelecida com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco de dados: {e}")
        return False
