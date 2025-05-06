from typing import Any, Dict, Optional, Union, List
import logging

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            company_id=obj_in.company_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        logger.info(f"Tentativa de autenticação para o email: {email}")
        user = self.get_by_email(db, email=email)
        if not user:
            logger.warning(f"Usuário não encontrado para o email: {email}")
            return None
        logger.info(f"Usuário encontrado, verificando senha. Hash armazenado: {user.hashed_password}")
        try:
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Senha incorreta para o usuário: {email}")
                return None
            logger.info(f"Autenticação bem-sucedida para o usuário: {email}")
            return user
        except Exception as e:
            logger.error(f"Erro durante a verificação da senha: {str(e)}")
            return None

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser
    
    def get_company_users(self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).filter(User.company_id == company_id).offset(skip).limit(limit).all()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash armazenado."""
        from app.core.security import verify_password as verify_pwd
        return verify_pwd(password, hashed_password)


user = CRUDUser(User) 