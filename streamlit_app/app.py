import streamlit as st
import requests
import json
from streamlit_cookies_manager import CookiesManager

# API URL
API_URL = "http://localhost:8000"

# Initialize cookies manager
cookies = CookiesManager()

def init_session_state():
    """Initialize session state variables"""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"

def login(username, password):
    """Login to the API"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/login/access-token",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user_id = data.get("user_id", "")
            st.session_state.username = username
            st.session_state.is_admin = data.get("is_admin", False)
            st.session_state.current_page = "dashboard"
            return True
        else:
            st.error("Invalid username or password")
            return False
    except Exception as e:
        st.error(f"Error during login: {e}")
        return False

def logout():
    """Logout and clear session state"""
    st.session_state.token = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_admin = False
    st.session_state.current_page = "login"

def auth_header():
    """Return authorization header with token"""
    return {"Authorization": f"Bearer {st.session_state.token}"}

def nav_to(page):
    """Navigate to a specific page"""
    st.session_state.current_page = page

def login_page():
    """Login page UI"""
    st.title("Imóveis App - Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username and password:
                login(username, password)
            else:
                st.error("Please enter both username and password")

def dashboard_page():
    """Main dashboard page after login"""
    st.title(f"Welcome, {st.session_state.username}!")
    
    st.sidebar.title("Navigation")
    if st.sidebar.button("Properties"):
        nav_to("properties")
    if st.sidebar.button("Users"):
        nav_to("users")
    if st.sidebar.button("Companies"):
        nav_to("companies")
    if st.sidebar.button("Teams"):
        nav_to("teams")
    if st.sidebar.button("Projects"):
        nav_to("projects")
    if st.sidebar.button("Logout"):
        logout()
    
    st.write("Select an option from the sidebar to manage data.")

def fetch_data(endpoint, with_auth=True):
    """Fetch data from API"""
    try:
        headers = auth_header() if with_auth else {}
        response = requests.get(f"{API_URL}/api/v1/{endpoint}/", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def create_item(endpoint, data, with_auth=True):
    """Create an item via API"""
    try:
        headers = auth_header() if with_auth else {}
        headers["Content-Type"] = "application/json"
        response = requests.post(
            f"{API_URL}/api/v1/{endpoint}/",
            headers=headers,
            json=data
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error creating item: {response.status_code}")
            if response.text:
                st.error(response.text)
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def update_item(endpoint, item_id, data, with_auth=True):
    """Update an item via API"""
    try:
        headers = auth_header() if with_auth else {}
        headers["Content-Type"] = "application/json"
        response = requests.put(
            f"{API_URL}/api/v1/{endpoint}/{item_id}",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error updating item: {response.status_code}")
            if response.text:
                st.error(response.text)
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def delete_item(endpoint, item_id, with_auth=True):
    """Delete an item via API"""
    try:
        headers = auth_header() if with_auth else {}
        response = requests.delete(
            f"{API_URL}/api/v1/{endpoint}/{item_id}",
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            return True
        else:
            st.error(f"Error deleting item: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def properties_page():
    """Properties management page"""
    st.title("Property Management")
    
    # Fetch properties data
    properties = fetch_data("properties")
    
    if properties:
        # Display properties in a table
        property_data = []
        for prop in properties:
            property_data.append([
                prop["id"],
                prop["name"],
                prop["address"],
                prop["price"]
            ])
        
        st.dataframe(
            property_data,
            column_names=["ID", "Name", "Address", "Price"],
            use_container_width=True
        )
    
    # Create new property
    with st.expander("Add New Property"):
        with st.form("new_property_form"):
            name = st.text_input("Property Name")
            address = st.text_input("Address")
            price = st.number_input("Price", min_value=0.0, format="%f")
            description = st.text_area("Description")
            
            submit = st.form_submit_button("Add Property")
            
            if submit:
                if name and address and price:
                    new_property = {
                        "name": name,
                        "address": address,
                        "price": price,
                        "description": description
                    }
                    
                    result = create_item("properties", new_property)
                    if result:
                        st.success("Property added successfully!")
                        st.experimental_rerun()
                else:
                    st.error("Please fill in all required fields")

def users_page():
    """Users management page"""
    st.title("User Management")
    
    # Only admins can access this page
    if not st.session_state.is_admin:
        st.warning("You need admin privileges to access this page")
        return
    
    # Fetch users data
    users = fetch_data("users")
    
    if users:
        # Display users in a table
        user_data = []
        for user in users:
            user_data.append([
                user["id"],
                user["username"],
                user["email"],
                "Yes" if user.get("is_admin", False) else "No"
            ])
        
        st.dataframe(
            user_data,
            column_names=["ID", "Username", "Email", "Admin"],
            use_container_width=True
        )
    
    # Create new user
    with st.expander("Add New User"):
        with st.form("new_user_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            is_admin = st.checkbox("Is Admin")
            
            submit = st.form_submit_button("Add User")
            
            if submit:
                if username and email and password:
                    new_user = {
                        "username": username,
                        "email": email,
                        "password": password,
                        "is_admin": is_admin
                    }
                    
                    result = create_item("users", new_user)
                    if result:
                        st.success("User added successfully!")
                        st.experimental_rerun()
                else:
                    st.error("Please fill in all required fields")

def companies_page():
    """Companies management page"""
    st.title("Company Management")
    
    # Fetch companies data
    companies = fetch_data("companies")
    
    if companies:
        # Display companies in a table
        company_data = []
        for company in companies:
            company_data.append([
                company["id"],
                company["name"],
                company["address"],
                company["email"]
            ])
        
        st.dataframe(
            company_data,
            column_names=["ID", "Name", "Address", "Email"],
            use_container_width=True
        )
    
    # Create new company
    with st.expander("Add New Company"):
        with st.form("new_company_form"):
            name = st.text_input("Company Name")
            address = st.text_input("Address")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            
            submit = st.form_submit_button("Add Company")
            
            if submit:
                if name and email:
                    new_company = {
                        "name": name,
                        "address": address,
                        "email": email,
                        "phone": phone
                    }
                    
                    result = create_item("companies", new_company)
                    if result:
                        st.success("Company added successfully!")
                        st.experimental_rerun()
                else:
                    st.error("Please fill in all required fields")

def teams_page():
    """Teams management page"""
    st.title("Team Management")
    
    # Fetch teams data
    teams = fetch_data("teams")
    
    if teams:
        # Display teams in a table
        team_data = []
        for team in teams:
            team_data.append([
                team["id"],
                team["name"],
                team.get("company_id", "N/A")
            ])
        
        st.dataframe(
            team_data,
            column_names=["ID", "Name", "Company ID"],
            use_container_width=True
        )
    
    # Create new team
    with st.expander("Add New Team"):
        with st.form("new_team_form"):
            name = st.text_input("Team Name")
            
            # Fetch companies for dropdown
            companies = fetch_data("companies")
            company_options = {c["name"]: c["id"] for c in companies} if companies else {}
            company_name = st.selectbox("Company", list(company_options.keys()))
            
            submit = st.form_submit_button("Add Team")
            
            if submit:
                if name and company_name:
                    new_team = {
                        "name": name,
                        "company_id": company_options[company_name]
                    }
                    
                    result = create_item("teams", new_team)
                    if result:
                        st.success("Team added successfully!")
                        st.experimental_rerun()
                else:
                    st.error("Please fill in all required fields")

def projects_page():
    """Projects management page"""
    st.title("Project Management")
    
    # Fetch projects data
    projects = fetch_data("projects")
    
    if projects:
        # Display projects in a table
        project_data = []
        for project in projects:
            project_data.append([
                project["id"],
                project["name"],
                project.get("description", ""),
                project.get("team_id", "N/A")
            ])
        
        st.dataframe(
            project_data,
            column_names=["ID", "Name", "Description", "Team ID"],
            use_container_width=True
        )
    
    # Create new project
    with st.expander("Add New Project"):
        with st.form("new_project_form"):
            name = st.text_input("Project Name")
            description = st.text_area("Description")
            
            # Fetch teams for dropdown
            teams = fetch_data("teams")
            team_options = {t["name"]: t["id"] for t in teams} if teams else {}
            team_name = st.selectbox("Team", list(team_options.keys()))
            
            submit = st.form_submit_button("Add Project")
            
            if submit:
                if name and team_name:
                    new_project = {
                        "name": name,
                        "description": description,
                        "team_id": team_options[team_name]
                    }
                    
                    result = create_item("projects", new_project)
                    if result:
                        st.success("Project added successfully!")
                        st.experimental_rerun()
                else:
                    st.error("Please fill in all required fields")

def main():
    """Main function to run the app"""
    st.set_page_config(
        page_title="Imóveis App",
        page_icon="🏢",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # Check if user is logged in
    if st.session_state.token is None:
        login_page()
    else:
        # Navigation sidebar
        with st.sidebar:
            st.title(f"Hello, {st.session_state.username}")
            st.divider()
            
            if st.button("Dashboard"):
                nav_to("dashboard")
            if st.button("Properties"):
                nav_to("properties")
            if st.button("Companies"):
                nav_to("companies")
            if st.button("Teams"):
                nav_to("teams")
            if st.button("Projects"):
                nav_to("projects")
            if st.session_state.is_admin and st.button("Users"):
                nav_to("users")
            
            st.divider()
            if st.button("Logout"):
                logout()
        
        # Display current page
        if st.session_state.current_page == "dashboard":
            dashboard_page()
        elif st.session_state.current_page == "properties":
            properties_page()
        elif st.session_state.current_page == "users":
            users_page()
        elif st.session_state.current_page == "companies":
            companies_page()
        elif st.session_state.current_page == "teams":
            teams_page()
        elif st.session_state.current_page == "projects":
            projects_page()

if __name__ == "__main__":
    main() 