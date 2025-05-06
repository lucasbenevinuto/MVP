from fastapi import APIRouter

from app.api.endpoints import login, users, companies, teams, projects, properties, contracts, expenses, clients, leads, dashboard

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"]) 