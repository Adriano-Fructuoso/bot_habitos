import logging
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.session import get_db
from models.models import ProcessedCallback

logger = logging.getLogger(__name__)


def is_duplicate_callback(callback_id: str, db: Session) -> bool:
    """
    Verifica se um callback já foi processado.
    Retorna True se for duplicado, False se for novo.
    """
    try:
        # Tenta inserir o callback
        obj = ProcessedCallback(callback_id=callback_id)
        db.add(obj)
        db.commit()
        logger.debug(f"Callback {callback_id} processado pela primeira vez")
        return False

    except IntegrityError:
        # Callback já existe
        db.rollback()
        logger.warning(f"Callback {callback_id} já foi processado (duplicado)")
        return True

    except Exception as e:
        # Erro inesperado
        db.rollback()
        logger.error(f"Erro ao verificar callback {callback_id}: {e}")
        # Em caso de erro, permite o processamento (fail-safe)
        return False


def cleanup_old_callbacks(minutes: int = 15, db: Session = None):
    """
    Remove callbacks antigos da tabela.
    """
    if db is None:
        db = next(get_db())

    try:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        deleted_count = (
            db.query(ProcessedCallback)
            .filter(ProcessedCallback.created_at < cutoff)
            .delete()
        )
        db.commit()

        if deleted_count > 0:
            logger.info(
                f"Removidos {deleted_count} callbacks antigos (mais de {minutes} minutos)"
            )
        else:
            logger.debug("Nenhum callback antigo encontrado para remoção")

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao limpar callbacks antigos: {e}")
    finally:
        if db is not None:
            db.close()
