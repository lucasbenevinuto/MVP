import logging
from datetime import date
from sqlalchemy.orm import Session

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.models.team import Team, UserTeam
from app.models.project import Project, TeamProject, ProjectStatus
from app.models.property import Property, PropertyType, PropertyStatus

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data(db: Session):
    # Criar uma empresa
    company = Company(
        name="Construtora Teste",
        document="12.345.678/0001-99",
        address="Rua Teste, 123",
        phone="(11) 99999-9999",
        description="Empresa de teste para desenvolvimento",
        logo_url="https://example.com/logo.png"
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    logger.info(f"Empresa criada: {company.name}")

    # Criar usuário administrador
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Administrador",
        is_active=True,
        is_superuser=True,
        company_id=company.id
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    logger.info(f"Usuário administrador criado: {admin.username}")

    # Criar um gerente
    manager = User(
        email="gerente@example.com",
        username="gerente",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Gerente de Projetos",
        is_active=True,
        is_superuser=False,
        company_id=company.id
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    logger.info(f"Usuário gerente criado: {manager.username}")

    # Criar um time
    team = Team(
        name="Equipe de Engenharia",
        description="Equipe responsável pelos projetos de engenharia",
        company_id=company.id,
        manager_id=manager.id
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    logger.info(f"Equipe criada: {team.name}")

    # Adicionar gerente à equipe
    user_team = UserTeam(
        user_id=manager.id,
        team_id=team.id,
        role="Gerente de Engenharia"
    )
    db.add(user_team)
    db.commit()
    logger.info(f"Gerente adicionado à equipe")

    # Criar um projeto
    project = Project(
        name="Residencial Parque Verde",
        description="Condomínio residencial com 50 casas",
        address="Av. Principal, 1000",
        city="São Paulo",
        state="SP",
        zip_code="04000-000",
        total_area=10000.0,
        budget=5000000.0,
        start_date=date(2023, 1, 1),
        expected_end_date=date(2024, 12, 31),
        status=ProjectStatus.IN_PROGRESS,
        company_id=company.id,
        manager_id=manager.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    logger.info(f"Projeto criado: {project.name}")

    # Associar equipe ao projeto
    team_project = TeamProject(
        team_id=team.id,
        project_id=project.id
    )
    db.add(team_project)
    db.commit()
    logger.info(f"Equipe associada ao projeto")

    # Criar alguns imóveis no projeto
    for i in range(1, 6):
        property = Property(
            name=f"Casa {i}",
            description=f"Casa com 3 quartos - Unidade {i}",
            type=PropertyType.HOUSE,
            status=PropertyStatus.STRUCTURE if i <= 2 else PropertyStatus.FOUNDATION,
            address=f"Rua Interna {i}, Condomínio Parque Verde",
            unit_number=f"{i}",
            area=150.0,
            bedrooms=3,
            bathrooms=2,
            garage_spots=2,
            price=500000.0,
            construction_cost=300000.0,
            start_date=date(2023, 3, 1),
            expected_completion_date=date(2024, 6, 30),
            project_id=project.id
        )
        db.add(property)
    
    db.commit()
    logger.info(f"5 imóveis criados no projeto")

    logger.info("Dados de teste criados com sucesso!")

def main():
    try:
        # Inicializar o banco de dados (criar tabelas)
        logger.info("Inicializando banco de dados...")
        init_db()
        
        # Criar sessão e inserir dados de teste
        logger.info("Inserindo dados de teste...")
        db = SessionLocal()
        create_test_data(db)
        db.close()
        
        logger.info("Banco de dados criado e populado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        raise

if __name__ == "__main__":
    main() 