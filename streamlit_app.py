import streamlit as st
import requests
import json
from typing import Dict, List, Optional, Any
import datetime

# Configurações da API
API_URL = "http://localhost:8000/api/v1"

# Função para converter objetos data para string (para serialização JSON)
def json_serial(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# Funções para interagir com a API
def login(username: str, password: str) -> Optional[Dict]:
    try:
        response = requests.post(
            f"{API_URL}/login/access-token",
            data={"username": username, "password": password},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao fazer login: {str(e)}")
        return None

def get_headers(token: str) -> Dict:
    return {"Authorization": f"Bearer {token}"}

def api_get(endpoint: str, token: str, params: Dict = None) -> Optional[Any]:
    try:
        response = requests.get(
            f"{API_URL}/{endpoint}", 
            headers=get_headers(token),
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao acessar API ({endpoint}): {str(e)}")
        return None

def api_post(endpoint: str, token: str, data: Dict) -> Optional[Any]:
    try:
        response = requests.post(
            f"{API_URL}/{endpoint}", 
            headers=get_headers(token),
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao enviar dados para API ({endpoint}): {str(e)}")
        st.error(f"Detalhes: {response.text if 'response' in locals() else 'Sem resposta'}")
        return None

def api_put(endpoint: str, token: str, data: Dict) -> Optional[Any]:
    try:
        response = requests.put(
            f"{API_URL}/{endpoint}", 
            headers=get_headers(token),
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao atualizar dados na API ({endpoint}): {str(e)}")
        st.error(f"Detalhes: {response.text if 'response' in locals() else 'Sem resposta'}")
        return None

def api_delete(endpoint: str, token: str) -> bool:
    try:
        response = requests.delete(
            f"{API_URL}/{endpoint}", 
            headers=get_headers(token)
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        st.error(f"Erro ao excluir dados na API ({endpoint}): {str(e)}")
        st.error(f"Detalhes: {response.text if 'response' in locals() else 'Sem resposta'}")
        return False

# Interface de login
def login_form():
    st.title("Login")
    username = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    if st.button("Login"):
        if username and password:
            result = login(username, password)
            if result and "access_token" in result:
                st.session_state["token"] = result["access_token"]
                st.session_state["logged_in"] = True
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Falha no login. Verifique suas credenciais.")
        else:
            st.warning("Por favor, preencha email e senha.")

# Função para exibir os dados em uma tabela
def display_data_table(data: List[Dict], key_prefix: str):
    if not data:
        st.info("Nenhum dado encontrado.")
        return
    
    # Extrair as chaves do primeiro item
    keys = list(data[0].keys())
    
    # Criar colunas para cada chave e botões de ação
    cols = st.columns(len(keys) + 2)  # +2 para os botões Editar e Excluir
    
    # Cabeçalhos
    for i, key in enumerate(keys):
        cols[i].write(f"**{key}**")
    cols[-2].write("**Editar**")
    cols[-1].write("**Excluir**")
    
    # Dados
    for i, item in enumerate(data):
        row_cols = st.columns(len(keys) + 2)
        for j, key in enumerate(keys):
            value = item[key]
            # Limitar o comprimento do texto para exibição
            if isinstance(value, str) and len(value) > 20:
                display_value = value[:20] + "..."
            else:
                display_value = value
            row_cols[j].write(str(display_value))
        
        # Botões de ação com IDs mais específicos usando o ID real do item
        item_id = item.get('id', i)
        if row_cols[-2].button("✏️", key=f"{key_prefix}_edit_{item_id}_{i}"):
            st.session_state[f"{key_prefix}_edit_item"] = item
        
        if row_cols[-1].button("🗑️", key=f"{key_prefix}_delete_{item_id}_{i}"):
            st.session_state[f"{key_prefix}_delete_item"] = item

# Página principal do app
def main():
    st.set_page_config(page_title="Gerenciador de Projetos Imobiliários", page_icon="🏢", layout="wide")
    
    # Inicializar estado da sessão
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    # Menu lateral
    if st.session_state["logged_in"]:
        st.sidebar.title("Menu")
        page = st.sidebar.radio(
            "Selecione uma página:",
            ["Empresas", "Usuários", "Equipes", "Projetos", "Imóveis"]
        )
        
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state.pop("token", None)
            st.rerun()
    
    # Exibir interface de login ou a página selecionada
    if not st.session_state["logged_in"]:
        login_form()
    else:
        if page == "Empresas":
            companies_page()
        elif page == "Usuários":
            users_page()
        elif page == "Equipes":
            teams_page()
        elif page == "Projetos":
            projects_page()
        elif page == "Imóveis":
            properties_page()

# Página de empresas
def companies_page():
    st.title("Gerenciar Empresas")
    
    # Obter todas as empresas
    companies = api_get("companies", st.session_state["token"])
    
    # Componentes para adicionar/editar empresas
    with st.expander("Adicionar/Editar Empresa", expanded="company_edit_item" in st.session_state):
        company_form()
    
    # Exibir empresas existentes
    st.subheader("Empresas Existentes")
    if companies:
        display_data_table(companies, "company")
        
        # Processar exclusão
        if "company_delete_item" in st.session_state:
            company = st.session_state["company_delete_item"]
            st.warning(f"Tem certeza que deseja excluir a empresa {company['name']}?")
            
            # Debug para verificar o ID
            st.write(f"Debug - ID da empresa a ser excluída: {company['id']}")
            
            col1, col2 = st.columns(2)
            if col1.button("Confirmar Exclusão", key=f"confirm_delete_company_{company['id']}"):
                # Debug do processo de exclusão
                st.write("Tentando excluir a empresa...")
                endpoint = f"companies/{company['id']}"
                st.write(f"Endpoint de exclusão: {endpoint}")
                
                delete_success = api_delete(endpoint, st.session_state["token"])
                
                if delete_success:
                    st.success("Empresa excluída com sucesso!")
                    st.session_state.pop("company_delete_item", None)
                    st.rerun()
                else:
                    st.error("Falha ao excluir a empresa. Verifique os logs para mais detalhes.")
            
            if col2.button("Cancelar", key=f"cancel_delete_company_{company['id']}"):
                st.session_state.pop("company_delete_item", None)
                st.rerun()

def company_form():
    edit_mode = "company_edit_item" in st.session_state
    company = st.session_state.get("company_edit_item", {}) if edit_mode else {}
    
    with st.form("company_form"):
        name = st.text_input("Nome", value=company.get("name", ""))
        document = st.text_input("CNPJ", value=company.get("document", ""))
        address = st.text_input("Endereço", value=company.get("address", ""))
        phone = st.text_input("Telefone", value=company.get("phone", ""))
        description = st.text_area("Descrição", value=company.get("description", ""))
        logo_url = st.text_input("URL do Logo", value=company.get("logo_url", ""))
        
        submit_label = "Atualizar" if edit_mode else "Adicionar"
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            data = {
                "name": name,
                "document": document,
                "address": address,
                "phone": phone,
                "description": description,
                "logo_url": logo_url
            }
            
            if edit_mode:
                company_id = company["id"]
                result = api_put(f"companies/{company_id}", st.session_state["token"], data)
                if result:
                    st.success("Empresa atualizada com sucesso!")
                    st.session_state.pop("company_edit_item", None)
                    st.rerun()
            else:
                result = api_post("companies", st.session_state["token"], data)
                if result:
                    st.success("Empresa adicionada com sucesso!")
                    st.rerun()

# Página de usuários
def users_page():
    st.title("Gerenciar Usuários")
    
    # Obter todos os usuários
    users = api_get("users", st.session_state["token"])
    
    # Componentes para adicionar/editar usuários
    with st.expander("Adicionar/Editar Usuário", expanded="user_edit_item" in st.session_state):
        user_form()
    
    # Exibir usuários existentes
    st.subheader("Usuários Existentes")
    if users:
        display_data_table(users, "user")
        
        # Processar exclusão
        if "user_delete_item" in st.session_state:
            user = st.session_state["user_delete_item"]
            st.warning(f"Tem certeza que deseja excluir o usuário {user['email']}?")
            
            # Debug para verificar o ID
            st.write(f"Debug - ID do usuário a ser excluído: {user['id']}")
            
            col1, col2 = st.columns(2)
            if col1.button("Confirmar Exclusão", key=f"confirm_delete_user_{user['id']}"):
                # Debug do processo de exclusão
                st.write("Tentando excluir o usuário...")
                endpoint = f"users/{user['id']}"
                st.write(f"Endpoint de exclusão: {endpoint}")
                
                delete_success = api_delete(endpoint, st.session_state["token"])
                
                if delete_success:
                    st.success("Usuário excluído com sucesso!")
                    st.session_state.pop("user_delete_item", None)
                    st.rerun()
                else:
                    st.error("Falha ao excluir o usuário. Verifique os logs para mais detalhes.")
            
            if col2.button("Cancelar", key=f"cancel_delete_user_{user['id']}"):
                st.session_state.pop("user_delete_item", None)
                st.rerun()

def user_form():
    edit_mode = "user_edit_item" in st.session_state
    user = st.session_state.get("user_edit_item", {}) if edit_mode else {}
    
    # Obter empresas para o dropdown
    companies = api_get("companies", st.session_state["token"]) or []
    company_options = {company["id"]: company["name"] for company in companies}
    company_options[None] = "Nenhuma empresa"
    
    with st.form("user_form"):
        email = st.text_input("Email", value=user.get("email", ""))
        username = st.text_input("Username", value=user.get("username", ""))
        
        # Senha é obrigatória apenas ao criar novo usuário
        password = st.text_input("Senha", type="password") if not edit_mode else st.text_input("Senha (deixe em branco para manter a atual)", type="password")
        
        full_name = st.text_input("Nome Completo", value=user.get("full_name", ""))
        
        # Dropdown de empresas
        company_id = user.get("company_id")
        selected_company = st.selectbox(
            "Empresa",
            options=list(company_options.keys()),
            format_func=lambda x: company_options.get(x, "Nenhuma empresa"),
            index=list(company_options.keys()).index(company_id) if company_id in company_options else 0
        )
        
        is_active = st.checkbox("Ativo", value=user.get("is_active", True))
        is_superuser = st.checkbox("Superusuário", value=user.get("is_superuser", False))
        
        submit_label = "Atualizar" if edit_mode else "Adicionar"
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            data = {
                "email": email,
                "username": username,
                "full_name": full_name,
                "company_id": selected_company,
                "is_active": is_active,
                "is_superuser": is_superuser
            }
            
            # Adicionar senha apenas se fornecida
            if password:
                data["password"] = password
            
            if edit_mode:
                user_id = user["id"]
                result = api_put(f"users/{user_id}", st.session_state["token"], data)
                if result:
                    st.success("Usuário atualizado com sucesso!")
                    st.session_state.pop("user_edit_item", None)
                    st.rerun()
            else:
                # Senha é obrigatória para novos usuários
                if not password:
                    st.error("Por favor, forneça uma senha para o novo usuário.")
                    return
                    
                result = api_post("users", st.session_state["token"], data)
                if result:
                    st.success("Usuário adicionado com sucesso!")
                    st.rerun()

# Página de equipes
def teams_page():
    st.title("Gerenciar Equipes")
    
    # Obter todas as equipes
    teams = api_get("teams", st.session_state["token"])
    
    # Componentes para adicionar/editar equipes
    with st.expander("Adicionar/Editar Equipe", expanded="team_edit_item" in st.session_state):
        team_form()
    
    # Exibir equipes existentes
    st.subheader("Equipes Existentes")
    if teams:
        display_data_table(teams, "team")
        
        # Processar exclusão
        if "team_delete_item" in st.session_state:
            team = st.session_state["team_delete_item"]
            st.warning(f"Tem certeza que deseja excluir a equipe {team['name']}?")
            
            # Debug para verificar o ID
            st.write(f"Debug - ID da equipe a ser excluída: {team['id']}")
            
            col1, col2 = st.columns(2)
            if col1.button("Confirmar Exclusão", key=f"confirm_delete_team_{team['id']}"):
                # Debug do processo de exclusão
                st.write("Tentando excluir a equipe...")
                endpoint = f"teams/{team['id']}"
                st.write(f"Endpoint de exclusão: {endpoint}")
                
                delete_success = api_delete(endpoint, st.session_state["token"])
                
                if delete_success:
                    st.success("Equipe excluída com sucesso!")
                    st.session_state.pop("team_delete_item", None)
                    st.rerun()
                else:
                    st.error("Falha ao excluir a equipe. Verifique os logs para mais detalhes.")
            
            if col2.button("Cancelar", key=f"cancel_delete_team_{team['id']}"):
                st.session_state.pop("team_delete_item", None)
                st.rerun()
                        
    # Se uma equipe está selecionada, mostrar membros
    if "team_edit_item" in st.session_state:
        team = st.session_state["team_edit_item"]
        st.subheader(f"Membros da Equipe: {team['name']}")
        
        # Obter membros da equipe
        team_members = api_get(f"teams/{team['id']}/members", st.session_state["token"]) or []
        
        # Formulário para adicionar membro
        with st.expander("Adicionar Membro à Equipe"):
            add_team_member_form(team['id'])
        
        # Exibir membros
        if team_members:
            for member in team_members:
                cols = st.columns([3, 1])
                cols[0].write(f"**Usuário ID:** {member['user_id']} - **Função:** {member['role']}")
                if cols[1].button("Remover", key=f"remove_member_{member['id']}"):
                    if api_delete(f"teams/{team['id']}/members/{member['user_id']}", st.session_state["token"]):
                        st.success("Membro removido com sucesso!")
                        st.rerun()
        else:
            st.info("Esta equipe não possui membros.")

def team_form():
    edit_mode = "team_edit_item" in st.session_state
    team = st.session_state.get("team_edit_item", {}) if edit_mode else {}
    
    # Obter empresas e usuários para os dropdowns
    companies = api_get("companies", st.session_state["token"]) or []
    company_options = {company["id"]: company["name"] for company in companies}
    
    users = api_get("users", st.session_state["token"]) or []
    user_options = {user["id"]: f"{user['full_name']} ({user['email']})" for user in users}
    
    with st.form("team_form"):
        name = st.text_input("Nome", value=team.get("name", ""))
        description = st.text_area("Descrição", value=team.get("description", ""))
        
        # Dropdown de empresas
        company_id = team.get("company_id")
        if company_options:
            selected_company = st.selectbox(
                "Empresa",
                options=list(company_options.keys()),
                format_func=lambda x: company_options.get(x, ""),
                index=list(company_options.keys()).index(company_id) if company_id in company_options else 0
            )
        else:
            st.error("Nenhuma empresa disponível. Por favor, crie uma empresa primeiro.")
            return
        
        # Dropdown de gerentes
        manager_id = team.get("manager_id")
        if user_options:
            selected_manager = st.selectbox(
                "Gerente",
                options=list(user_options.keys()),
                format_func=lambda x: user_options.get(x, ""),
                index=list(user_options.keys()).index(manager_id) if manager_id in user_options else 0
            )
        else:
            st.error("Nenhum usuário disponível. Por favor, crie um usuário primeiro.")
            return
        
        submit_label = "Atualizar" if edit_mode else "Adicionar"
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            data = {
                "name": name,
                "description": description,
                "company_id": selected_company,
                "manager_id": selected_manager
            }
            
            if edit_mode:
                team_id = team["id"]
                result = api_put(f"teams/{team_id}", st.session_state["token"], data)
                if result:
                    st.success("Equipe atualizada com sucesso!")
                    st.session_state["team_edit_item"] = result  # Atualizar para mostrar membros
            else:
                result = api_post("teams", st.session_state["token"], data)
                if result:
                    st.success("Equipe adicionada com sucesso!")
                    st.session_state["team_edit_item"] = result  # Definir para mostrar membros
                    st.rerun()

def add_team_member_form(team_id):
    # Obter usuários para o dropdown
    users = api_get("users", st.session_state["token"]) or []
    user_options = {user["id"]: f"{user['full_name']} ({user['email']})" for user in users}
    
    with st.form("add_member_form"):
        if user_options:
            selected_user = st.selectbox(
                "Usuário",
                options=list(user_options.keys()),
                format_func=lambda x: user_options.get(x, "")
            )
        else:
            st.error("Nenhum usuário disponível.")
            return
        
        role = st.text_input("Função na Equipe", value="Membro")
        
        submitted = st.form_submit_button("Adicionar Membro")
        
        if submitted:
            data = {
                "user_id": selected_user,
                "team_id": team_id,
                "role": role
            }
            
            result = api_post(f"teams/{team_id}/members", st.session_state["token"], data)
            if result:
                st.success("Membro adicionado com sucesso!")
                st.rerun()

# Página de projetos
def projects_page():
    st.title("Gerenciar Projetos")
    
    # Obter todos os projetos
    projects = api_get("projects", st.session_state["token"])
    
    # Componentes para adicionar/editar projetos
    with st.expander("Adicionar/Editar Projeto", expanded="project_edit_item" in st.session_state):
        project_form()
    
    # Exibir projetos existentes
    st.subheader("Projetos Existentes")
    if projects:
        display_data_table(projects, "project")
        
        # Processar exclusão
        if "project_delete_item" in st.session_state:
            project = st.session_state["project_delete_item"]
            st.warning(f"Tem certeza que deseja excluir o projeto {project['name']}?")
            
            # Debug para verificar o ID
            st.write(f"Debug - ID do projeto a ser excluído: {project['id']}")
            
            col1, col2 = st.columns(2)
            if col1.button("Confirmar Exclusão", key=f"confirm_delete_project_{project['id']}"):
                # Debug do processo de exclusão
                st.write("Tentando excluir o projeto...")
                endpoint = f"projects/{project['id']}"
                st.write(f"Endpoint de exclusão: {endpoint}")
                
                delete_success = api_delete(endpoint, st.session_state["token"])
                
                if delete_success:
                    st.success("Projeto excluído com sucesso!")
                    st.session_state.pop("project_delete_item", None)
                    st.rerun()
                else:
                    st.error("Falha ao excluir o projeto. Verifique os logs para mais detalhes.")
            
            if col2.button("Cancelar", key=f"cancel_delete_project_{project['id']}"):
                st.session_state.pop("project_delete_item", None)
                st.rerun()

def project_form():
    edit_mode = "project_edit_item" in st.session_state
    project = st.session_state.get("project_edit_item", {}) if edit_mode else {}
    
    # Obter empresas e usuários para os dropdowns
    companies = api_get("companies", st.session_state["token"]) or []
    company_options = {company["id"]: company["name"] for company in companies}
    
    users = api_get("users", st.session_state["token"]) or []
    user_options = {user["id"]: f"{user['full_name']} ({user['email']})" for user in users}
    
    status_options = ["planning", "in_progress", "on_hold", "completed", "cancelled"]
    
    with st.form("project_form"):
        name = st.text_input("Nome", value=project.get("name", ""))
        description = st.text_area("Descrição", value=project.get("description", ""))
        address = st.text_input("Endereço", value=project.get("address", ""))
        city = st.text_input("Cidade", value=project.get("city", ""))
        state = st.text_input("Estado", value=project.get("state", ""))
        zip_code = st.text_input("CEP", value=project.get("zip_code", ""))
        
        col1, col2 = st.columns(2)
        with col1:
            total_area = st.number_input("Área Total (m²)", value=float(project.get("total_area", 0)) if project.get("total_area") else 0.0, min_value=0.0)
            budget = st.number_input("Orçamento (R$)", value=float(project.get("budget", 0)) if project.get("budget") else 0.0, min_value=0.0)
        
        with col2:
            start_date = st.date_input("Data de Início", value=datetime.datetime.now().date())
            expected_end_date = st.date_input("Data de Término Prevista", value=(datetime.datetime.now() + datetime.timedelta(days=365)).date())
            
        status = st.selectbox(
            "Status",
            options=status_options,
            index=status_options.index(project.get("status", "planning")) if project.get("status") in status_options else 0
        )
        
        # Dropdown de empresas
        company_id = project.get("company_id")
        if company_options:
            selected_company = st.selectbox(
                "Empresa",
                options=list(company_options.keys()),
                format_func=lambda x: company_options.get(x, ""),
                index=list(company_options.keys()).index(company_id) if company_id in company_options else 0
            )
        else:
            st.error("Nenhuma empresa disponível. Por favor, crie uma empresa primeiro.")
            return
        
        # Dropdown de gerentes
        manager_id = project.get("manager_id")
        if user_options:
            selected_manager = st.selectbox(
                "Gerente",
                options=list(user_options.keys()),
                format_func=lambda x: user_options.get(x, ""),
                index=list(user_options.keys()).index(manager_id) if manager_id in user_options else 0
            )
        else:
            st.error("Nenhum usuário disponível. Por favor, crie um usuário primeiro.")
            return
        
        submit_label = "Atualizar" if edit_mode else "Adicionar"
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            data = {
                "name": name,
                "description": description,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "total_area": total_area,
                "budget": budget,
                "start_date": start_date.isoformat(),
                "expected_end_date": expected_end_date.isoformat(),
                "status": status,
                "company_id": selected_company,
                "manager_id": selected_manager
            }
            
            if edit_mode:
                project_id = project["id"]
                result = api_put(f"projects/{project_id}", st.session_state["token"], data)
                if result:
                    st.success("Projeto atualizado com sucesso!")
                    st.session_state.pop("project_edit_item", None)
                    st.rerun()
            else:
                result = api_post("projects", st.session_state["token"], data)
                if result:
                    st.success("Projeto adicionado com sucesso!")
                    st.rerun()

# Página de imóveis
def properties_page():
    st.title("Gerenciar Imóveis")
    
    # Obter todos os imóveis
    properties = api_get("properties", st.session_state["token"])
    
    # Componentes para adicionar/editar imóveis
    with st.expander("Adicionar/Editar Imóvel", expanded="property_edit_item" in st.session_state):
        property_form()
    
    # Exibir imóveis existentes
    st.subheader("Imóveis Existentes")
    if properties:
        display_data_table(properties, "property")
        
        # Processar exclusão
        if "property_delete_item" in st.session_state:
            property_item = st.session_state["property_delete_item"]
            st.warning(f"Tem certeza que deseja excluir o imóvel {property_item['name']}?")
            
            # Adicionar debug para ver se o item foi selecionado corretamente
            st.write(f"Debug - ID do imóvel a ser excluído: {property_item['id']}")
            
            col1, col2 = st.columns(2)
            if col1.button("Confirmar Exclusão", key=f"confirm_delete_property_{property_item['id']}"):
                # Adicionar informações de debug para verificar se o botão está sendo acionado
                st.write("Tentando excluir o imóvel...")
                
                # Construir o endpoint correto
                endpoint = f"properties/{property_item['id']}"
                st.write(f"Endpoint de exclusão: {endpoint}")
                
                # Chamar a API para excluir
                delete_success = api_delete(endpoint, st.session_state["token"])
                
                if delete_success:
                    st.success("Imóvel excluído com sucesso!")
                    # Remover o item do estado da sessão
                    st.session_state.pop("property_delete_item", None)
                    st.rerun()
                else:
                    st.error("Falha ao excluir o imóvel. Verifique os logs para mais detalhes.")
            
            if col2.button("Cancelar", key=f"cancel_delete_property_{property_item['id']}"):
                st.session_state.pop("property_delete_item", None)
                st.rerun()

def property_form():
    edit_mode = "property_edit_item" in st.session_state
    property_item = st.session_state.get("property_edit_item", {}) if edit_mode else {}
    
    # Obter projetos para o dropdown
    projects = api_get("projects", st.session_state["token"]) or []
    project_options = {project["id"]: f"{project['name']} ({project['city']})" for project in projects}
    
    property_types = ["apartment", "house", "commercial", "land", "industrial"]
    property_statuses = ["planning", "foundation", "structure", "finishing", "completed", "sold"]
    
    with st.form("property_form"):
        name = st.text_input("Nome", value=property_item.get("name", ""))
        description = st.text_area("Descrição", value=property_item.get("description", ""))
        
        property_type = st.selectbox(
            "Tipo",
            options=property_types,
            index=property_types.index(property_item.get("type", "house")) if property_item.get("type") in property_types else 0
        )
        
        status = st.selectbox(
            "Status",
            options=property_statuses,
            index=property_statuses.index(property_item.get("status", "planning")) if property_item.get("status") in property_statuses else 0
        )
        
        address = st.text_input("Endereço", value=property_item.get("address", ""))
        unit_number = st.text_input("Número da Unidade", value=property_item.get("unit_number", ""))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            floor = st.number_input("Andar", value=int(property_item.get("floor", 0)) if property_item.get("floor") is not None else 0, min_value=0)
            area = st.number_input("Área (m²)", value=float(property_item.get("area", 0)) if property_item.get("area") else 0.0, min_value=0.0)
        
        with col2:
            bedrooms = st.number_input("Quartos", value=int(property_item.get("bedrooms", 0)) if property_item.get("bedrooms") is not None else 0, min_value=0)
            bathrooms = st.number_input("Banheiros", value=int(property_item.get("bathrooms", 0)) if property_item.get("bathrooms") is not None else 0, min_value=0)
        
        with col3:
            garage_spots = st.number_input("Vagas de Garagem", value=int(property_item.get("garage_spots", 0)) if property_item.get("garage_spots") is not None else 0, min_value=0)
        
        col1, col2 = st.columns(2)
        with col1:
            price = st.number_input("Preço (R$)", value=float(property_item.get("price", 0)) if property_item.get("price") else 0.0, min_value=0.0)
            construction_cost = st.number_input("Custo de Construção (R$)", value=float(property_item.get("construction_cost", 0)) if property_item.get("construction_cost") else 0.0, min_value=0.0)
        
        with col2:
            start_date = st.date_input("Data de Início", value=datetime.datetime.now().date())
            expected_completion_date = st.date_input("Data de Conclusão Prevista", value=(datetime.datetime.now() + datetime.timedelta(days=365)).date())
        
        is_sold = st.checkbox("Vendido", value=property_item.get("is_sold", False))
        
        if is_sold:
            col1, col2 = st.columns(2)
            with col1:
                sale_date = st.date_input("Data da Venda", value=datetime.datetime.now().date())
            with col2:
                sale_price = st.number_input("Preço de Venda (R$)", value=float(property_item.get("sale_price", 0)) if property_item.get("sale_price") else 0.0, min_value=0.0)
        else:
            sale_date = None
            sale_price = None
        
        # Dropdown de projetos
        project_id = property_item.get("project_id")
        if project_options:
            selected_project = st.selectbox(
                "Projeto",
                options=list(project_options.keys()),
                format_func=lambda x: project_options.get(x, ""),
                index=list(project_options.keys()).index(project_id) if project_id in project_options else 0
            )
        else:
            st.error("Nenhum projeto disponível. Por favor, crie um projeto primeiro.")
            return
        
        submit_label = "Atualizar" if edit_mode else "Adicionar"
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            data = {
                "name": name,
                "description": description,
                "type": property_type,
                "status": status,
                "address": address,
                "unit_number": unit_number,
                "floor": floor,
                "area": area,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "garage_spots": garage_spots,
                "price": price,
                "construction_cost": construction_cost,
                "start_date": start_date.isoformat(),
                "expected_completion_date": expected_completion_date.isoformat(),
                "is_sold": is_sold,
                "project_id": selected_project
            }
            
            if is_sold and sale_date and sale_price:
                data["sale_date"] = sale_date.isoformat()
                data["sale_price"] = sale_price
            
            if edit_mode:
                property_id = property_item["id"]
                result = api_put(f"properties/{property_id}", st.session_state["token"], data)
                if result:
                    st.success("Imóvel atualizado com sucesso!")
                    st.session_state.pop("property_edit_item", None)
                    st.rerun()
            else:
                result = api_post("properties", st.session_state["token"], data)
                if result:
                    st.success("Imóvel adicionado com sucesso!")
                    st.rerun()

if __name__ == "__main__":
    main() 