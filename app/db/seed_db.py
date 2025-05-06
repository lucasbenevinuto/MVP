import logging
import datetime
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    User, Company, Team, UserTeam, TeamProject, Project, Property, ProjectTask, ProjectUpdate,
    ProjectStatus, PropertyStatus, PropertyType, 
    Client, ClientType, Lead, LeadStatus,
    Contract, ContractType, ContractStatus, ContractDocument,
    Expense, ExpenseCategory
)

logger = logging.getLogger(__name__)

def seed_db():
    """Semeia o banco de dados com dados de exemplo"""
    db = SessionLocal()
    try:
        # Verifica se já existem dados no sistema
        existing_company = db.query(Company).first()
        if existing_company:
            # Se já existirem dados básicos, apenas adiciona os novos
            _add_new_data(db)
        else:
            # Caso contrário, adiciona dados completos
            _add_sample_data(db)
        
        db.commit()
        logger.info("Dados de exemplo inseridos com sucesso")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao inserir dados: {e}")
        raise
    finally:
        db.close()

def _add_sample_data(db: Session):
    """Adiciona dados de exemplo em todas as tabelas"""
    
    # 1. Empresas
    company = Company(
        name="Construtora Modelo",
        document="12.345.678/0001-90",
        address="Av. Principal, 1000",
        phone="(11) 3456-7890",
        description="Empresa especializada em construção civil",
        logo_url="https://example.com/logo.png"
    )
    db.add(company)
    db.flush()  # Para obter o ID da empresa
    
    # 2. Usuários
    user_admin = User(
        email="admin@exemplo.com",
        username="admin",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Administrador",
        is_active=True,
        is_superuser=True,
        company_id=company.id
    )
    
    user_manager = User(
        email="gerente@exemplo.com",
        username="gerente",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Gerente de Projetos",
        is_active=True,
        is_superuser=False,
        company_id=company.id
    )
    
    user_sales = User(
        email="vendas@exemplo.com",
        username="vendas",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Vendedor",
        is_active=True,
        is_superuser=False,
        company_id=company.id
    )
    
    db.add_all([user_admin, user_manager, user_sales])
    db.flush()
    
    # 3. Equipes
    team_engineering = Team(
        name="Engenharia",
        description="Equipe de engenheiros e arquitetos",
        company_id=company.id,
        manager_id=user_manager.id
    )
    
    team_sales = Team(
        name="Vendas",
        description="Equipe de vendas imobiliárias",
        company_id=company.id,
        manager_id=user_sales.id
    )
    
    db.add_all([team_engineering, team_sales])
    db.flush()
    
    # 4. Relacionamento Usuário-Equipe
    user_team1 = UserTeam(user_id=user_admin.id, team_id=team_engineering.id, role="Diretor")
    user_team2 = UserTeam(user_id=user_manager.id, team_id=team_engineering.id, role="Engenheiro Chefe")
    user_team3 = UserTeam(user_id=user_sales.id, team_id=team_sales.id, role="Vendedor Sênior")
    
    db.add_all([user_team1, user_team2, user_team3])
    db.flush()
    
    # 5. Projetos
    project1 = Project(
        name="Residencial Harmonia",
        description="Condomínio residencial com 4 torres",
        address="Rua das Flores, 500",
        city="São Paulo",
        state="SP",
        zip_code="01234-567",
        total_area=10000.0,
        budget=5000000.0,
        start_date=datetime.date(2023, 1, 15),
        expected_end_date=datetime.date(2024, 12, 31),
        status=ProjectStatus.IN_PROGRESS,
        company_id=company.id,
        manager_id=user_manager.id
    )
    
    project2 = Project(
        name="Edifício Comercial Centro",
        description="Prédio comercial com 10 andares",
        address="Av. Central, 200",
        city="Rio de Janeiro",
        state="RJ",
        zip_code="20000-000",
        total_area=5000.0,
        budget=3000000.0,
        start_date=datetime.date(2023, 3, 10),
        expected_end_date=datetime.date(2024, 6, 30),
        status=ProjectStatus.IN_PROGRESS,
        company_id=company.id,
        manager_id=user_manager.id
    )
    
    db.add_all([project1, project2])
    db.flush()
    
    # 6. Equipes por Projeto
    team_project1 = TeamProject(team_id=team_engineering.id, project_id=project1.id)
    team_project2 = TeamProject(team_id=team_sales.id, project_id=project1.id)
    team_project3 = TeamProject(team_id=team_engineering.id, project_id=project2.id)
    team_project4 = TeamProject(team_id=team_sales.id, project_id=project2.id)
    
    db.add_all([team_project1, team_project2, team_project3, team_project4])
    db.flush()
    
    # 7. Tarefas dos Projetos
    task1 = ProjectTask(
        title="Fundação Torre A",
        description="Fundação da primeira torre",
        start_date=datetime.date(2023, 1, 20),
        end_date=datetime.date(2023, 3, 15),
        status="completed",
        project_id=project1.id,
        assignee_id=user_manager.id
    )
    
    task2 = ProjectTask(
        title="Estrutura Torre A",
        description="Construção da estrutura da primeira torre",
        start_date=datetime.date(2023, 3, 16),
        end_date=datetime.date(2023, 6, 30),
        status="in_progress",
        project_id=project1.id,
        assignee_id=user_manager.id
    )
    
    db.add_all([task1, task2])
    db.flush()
    
    # 8. Imóveis
    property1 = Property(
        name="Apartamento 101 - Torre A",
        description="Apartamento de 2 quartos",
        type=PropertyType.APARTMENT,
        status=PropertyStatus.STRUCTURE,
        address="Rua das Flores, 500 - Torre A, Apto 101",
        unit_number="101-A",
        floor=1,
        area=70.0,
        bedrooms=2,
        bathrooms=1,
        garage_spots=1,
        price=350000.0,
        construction_cost=200000.0,
        start_date=datetime.date(2023, 1, 20),
        expected_completion_date=datetime.date(2024, 6, 30),
        project_id=project1.id
    )
    
    property2 = Property(
        name="Apartamento 102 - Torre A",
        description="Apartamento de 3 quartos",
        type=PropertyType.APARTMENT,
        status=PropertyStatus.STRUCTURE,
        address="Rua das Flores, 500 - Torre A, Apto 102",
        unit_number="102-A",
        floor=1,
        area=90.0,
        bedrooms=3,
        bathrooms=2,
        garage_spots=1,
        price=450000.0,
        construction_cost=250000.0,
        start_date=datetime.date(2023, 1, 20),
        expected_completion_date=datetime.date(2024, 6, 30),
        project_id=project1.id
    )
    
    property3 = Property(
        name="Sala Comercial 101",
        description="Sala comercial de 50m²",
        type=PropertyType.COMMERCIAL,
        status=PropertyStatus.FOUNDATION,
        address="Av. Central, 200 - Sala 101",
        unit_number="101",
        floor=1,
        area=50.0,
        bedrooms=0,
        bathrooms=1,
        garage_spots=1,
        price=300000.0,
        construction_cost=150000.0,
        start_date=datetime.date(2023, 3, 10),
        expected_completion_date=datetime.date(2024, 3, 30),
        project_id=project2.id
    )
    
    db.add_all([property1, property2, property3])
    db.flush()
    
    # 9. Clientes (Nova tabela)
    client1 = Client(
        name="João Silva",
        client_type=ClientType.INDIVIDUAL,
        document="123.456.789-00",
        email="joao.silva@email.com",
        phone="(11) 99876-5432",
        address="Rua dos Clientes, 100",
        city="São Paulo",
        state="SP",
        zip_code="01234-567",
        notes="Cliente interessado em apartamentos de 2 quartos",
        company_id=company.id
    )
    
    client2 = Client(
        name="Maria Oliveira",
        client_type=ClientType.INDIVIDUAL,
        document="987.654.321-00",
        email="maria.oliveira@email.com",
        phone="(11) 98765-4321",
        address="Rua dos Compradores, 200",
        city="São Paulo",
        state="SP",
        zip_code="04567-890",
        notes="Cliente interessada em apartamentos de 3 quartos",
        company_id=company.id
    )
    
    client3 = Client(
        name="Empresa ABC Ltda",
        client_type=ClientType.COMPANY,
        document="98.765.432/0001-10",
        email="contato@empresaabc.com",
        phone="(11) 3456-7890",
        address="Av. Empresarial, 1000",
        city="Rio de Janeiro",
        state="RJ",
        zip_code="20000-000",
        notes="Empresa interessada em salas comerciais",
        company_id=company.id
    )
    
    db.add_all([client1, client2, client3])
    db.flush()
    
    # 10. Leads de Vendas (Nova tabela)
    lead1 = Lead(
        property_id=property1.id,
        client_id=client1.id,
        status=LeadStatus.NEGOTIATION,
        first_contact_date=datetime.date(2023, 2, 15),
        last_contact_date=datetime.date(2023, 3, 10),
        next_contact_date=datetime.date(2023, 3, 20),
        visit_date=datetime.date(2023, 2, 25),
        interest_level=4,
        budget=360000.0,
        notes="Cliente muito interessado, negociando valores",
        assigned_user_id=user_sales.id
    )
    
    lead2 = Lead(
        property_id=property2.id,
        client_id=client2.id,
        status=LeadStatus.PROPERTY_VISIT,
        first_contact_date=datetime.date(2023, 3, 5),
        last_contact_date=datetime.date(2023, 3, 15),
        next_contact_date=datetime.date(2023, 3, 25),
        visit_date=datetime.date(2023, 3, 15),
        interest_level=3,
        budget=440000.0,
        notes="Cliente visitou o imóvel, está avaliando proposta",
        assigned_user_id=user_sales.id
    )
    
    lead3 = Lead(
        property_id=property3.id,
        client_id=client3.id,
        status=LeadStatus.INITIAL_CONTACT,
        first_contact_date=datetime.date(2023, 3, 12),
        last_contact_date=datetime.date(2023, 3, 12),
        next_contact_date=datetime.date(2023, 3, 30),
        interest_level=2,
        budget=280000.0,
        notes="Empresa entrou em contato solicitando informações",
        assigned_user_id=user_sales.id
    )
    
    db.add_all([lead1, lead2, lead3])
    db.flush()
    
    # 11. Contratos (Nova tabela)
    contract1 = Contract(
        contract_number="CONT-2023-001",
        type=ContractType.SALE,
        description="Contrato de venda do Apartamento 101",
        client_id=client1.id,
        property_id=property1.id,
        signing_date=datetime.date(2023, 3, 18),
        expiration_date=datetime.date(2024, 3, 18),
        contract_value=350000.0,
        status=ContractStatus.ACTIVE,
        notes="Contrato assinado com financiamento bancário"
    )
    
    db.add(contract1)
    db.flush()
    
    # 12. Documentos de Contrato (Nova tabela)
    contract_doc1 = ContractDocument(
        filename="contrato_venda_apt101.pdf",
        description="Contrato de venda assinado",
        file_type="application/pdf",
        file_path="/documents/contracts/2023/001/contrato.pdf",
        contract_id=contract1.id
    )
    
    contract_doc2 = ContractDocument(
        filename="anexo_financiamento.pdf",
        description="Anexo de financiamento bancário",
        file_type="application/pdf",
        file_path="/documents/contracts/2023/001/anexo.pdf",
        contract_id=contract1.id
    )
    
    db.add_all([contract_doc1, contract_doc2])
    db.flush()
    
    # 13. Despesas (Nova tabela)
    expense1 = Expense(
        description="Compra de concreto",
        category=ExpenseCategory.MATERIALS,
        amount=50000.0,
        date=datetime.date(2023, 1, 25),
        supplier_name="Fornecedor de Materiais XYZ",
        supplier_document="12.345.678/0001-90",
        supplier_contact="(11) 3333-4444",
        receipt_path="/documents/expenses/2023/001/nota_fiscal.pdf",
        receipt_description="Nota fiscal nº 12345",
        notes="Compra de concreto para fundação Torre A",
        project_id=project1.id,
        property_id=None,  # Despesa geral do projeto
        created_by_id=user_manager.id
    )
    
    expense2 = Expense(
        description="Serviço de terraplanagem",
        category=ExpenseCategory.SERVICES,
        amount=30000.0,
        date=datetime.date(2023, 1, 18),
        supplier_name="Empresa de Terraplanagem",
        supplier_document="98.765.432/0001-10",
        receipt_path="/documents/expenses/2023/002/recibo.pdf",
        project_id=project1.id,
        created_by_id=user_manager.id
    )
    
    expense3 = Expense(
        description="Mão de obra - fundação",
        category=ExpenseCategory.LABOR,
        amount=20000.0,
        date=datetime.date(2023, 2, 5),
        supplier_name="Construtora Terceirizada",
        project_id=project1.id,
        created_by_id=user_manager.id
    )
    
    expense4 = Expense(
        description="Materiais elétricos - Apartamento 101",
        category=ExpenseCategory.MATERIALS,
        amount=5000.0,
        date=datetime.date(2023, 3, 10),
        project_id=project1.id,
        property_id=property1.id,  # Despesa específica do imóvel
        created_by_id=user_manager.id
    )
    
    db.add_all([expense1, expense2, expense3, expense4])
    db.flush()

def _add_new_data(db: Session):
    """Adiciona apenas dados nas novas tabelas, caso as tabelas básicas já tenham dados"""
    
    # Obtém uma empresa e usuários existentes
    company = db.query(Company).first()
    
    user_admin = db.query(User).filter(User.is_superuser == True).first()
    if not user_admin:
        user_admin = db.query(User).first()
    
    # Obtém projetos e imóveis existentes
    projects = db.query(Project).all()
    if not projects:
        logger.error("Nenhum projeto encontrado. Impossível adicionar dados relacionados.")
        return
    
    project = projects[0]
    
    properties = db.query(Property).all()
    if not properties:
        logger.error("Nenhum imóvel encontrado. Impossível adicionar dados relacionados.")
        return
    
    property = properties[0]
    
    # 1. Clientes
    client1 = Client(
        name="João Silva",
        client_type=ClientType.INDIVIDUAL,
        document="123.456.789-00",
        email="joao.silva@email.com",
        phone="(11) 99876-5432",
        address="Rua dos Clientes, 100",
        city="São Paulo",
        state="SP",
        zip_code="01234-567",
        notes="Cliente interessado em apartamentos de 2 quartos",
        company_id=company.id
    )
    
    client2 = Client(
        name="Empresa ABC Ltda",
        client_type=ClientType.COMPANY,
        document="98.765.432/0001-10",
        email="contato@empresaabc.com",
        phone="(11) 3456-7890",
        address="Av. Empresarial, 1000",
        city="Rio de Janeiro",
        state="RJ",
        zip_code="20000-000",
        notes="Empresa interessada em salas comerciais",
        company_id=company.id
    )
    
    db.add_all([client1, client2])
    db.flush()
    
    # 2. Leads
    lead1 = Lead(
        property_id=property.id,
        client_id=client1.id,
        status=LeadStatus.NEGOTIATION,
        first_contact_date=datetime.date(2023, 2, 15),
        last_contact_date=datetime.date(2023, 3, 10),
        next_contact_date=datetime.date(2023, 3, 20),
        visit_date=datetime.date(2023, 2, 25),
        interest_level=4,
        budget=360000.0,
        notes="Cliente muito interessado, negociando valores",
        assigned_user_id=user_admin.id
    )
    
    db.add(lead1)
    db.flush()
    
    # 3. Contratos
    contract1 = Contract(
        contract_number="CONT-2023-001",
        type=ContractType.SALE,
        description="Contrato de venda",
        client_id=client1.id,
        property_id=property.id,
        signing_date=datetime.date(2023, 3, 18),
        expiration_date=datetime.date(2024, 3, 18),
        contract_value=350000.0,
        status=ContractStatus.ACTIVE,
        notes="Contrato assinado com financiamento bancário"
    )
    
    db.add(contract1)
    db.flush()
    
    # 4. Documentos de Contrato
    contract_doc1 = ContractDocument(
        filename="contrato_venda.pdf",
        description="Contrato de venda assinado",
        file_type="application/pdf",
        file_path="/documents/contracts/2023/001/contrato.pdf",
        contract_id=contract1.id
    )
    
    db.add(contract_doc1)
    db.flush()
    
    # 5. Despesas
    expense1 = Expense(
        description="Compra de concreto",
        category=ExpenseCategory.MATERIALS,
        amount=50000.0,
        date=datetime.date(2023, 1, 25),
        supplier_name="Fornecedor de Materiais XYZ",
        supplier_document="12.345.678/0001-90",
        supplier_contact="(11) 3333-4444",
        receipt_path="/documents/expenses/2023/001/nota_fiscal.pdf",
        receipt_description="Nota fiscal nº 12345",
        notes="Compra de concreto para fundação",
        project_id=project.id,
        property_id=None,  # Despesa geral do projeto
        created_by_id=user_admin.id
    )
    
    expense2 = Expense(
        description="Materiais elétricos",
        category=ExpenseCategory.MATERIALS,
        amount=5000.0,
        date=datetime.date(2023, 3, 10),
        project_id=project.id,
        property_id=property.id,  # Despesa específica do imóvel
        created_by_id=user_admin.id
    )
    
    db.add_all([expense1, expense2])
    db.flush()

if __name__ == "__main__":
    seed_db() 