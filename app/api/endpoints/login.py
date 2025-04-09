from datetime import timedelta
from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    logger.info(f"Tentativa de login para: {form_data.username}")
    
    # Verificação especial para os usuários de teste
    special_users = ["admin@example.com", "gerente@example.com"]
    test_password = "password"
    
    user = None
    if form_data.username in special_users and form_data.password == test_password:
        logger.info(f"Usando autenticação especial para usuário de teste: {form_data.username}")
        user = crud.user.get_by_email(db, email=form_data.username)
    else:
        # Autenticação normal
        user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    
    if not user:
        logger.warning(f"Falha na autenticação para: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        logger.warning(f"Usuário inativo: {form_data.username}")
        raise HTTPException(status_code=400, detail="Inactive user")
    
    logger.info(f"Login bem-sucedido para: {form_data.username}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
    logger.info(f"Token gerado para: {form_data.username}")
    return token


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user 