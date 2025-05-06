import logging
from sqlalchemy.orm import Session

from app.db.base_class import Base
from app.db.session import engine
import app.models  # Importa todos os modelos para que o SQLAlchemy os registre


logger = logging.getLogger(__name__)


def init_db() -> None:
    """Inicializa o banco de dados criando todas as tabelas."""
    try:
        # Cria todas as tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise 