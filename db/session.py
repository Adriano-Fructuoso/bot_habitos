import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da URL do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')

# Se não estiver configurado, usa SQLite para testes
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"
    print("⚠️ DATABASE_URL não configurada, usando SQLite para testes")

# Cria o engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # Set to True para debug SQL
    # Configurações específicas para PostgreSQL
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,  # Recicla conexões a cada hora
    pool_timeout=30
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
    from models.models import User, Habit, DailyLog, Badge
    Base.metadata.create_all(bind=engine)

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Conexão com banco de dados estabelecida com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco de dados: {e}")
        return False 