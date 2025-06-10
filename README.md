# Sistema de Gerenciamento de Projetos

## 📋 Visão Geral
Este é um sistema robusto de gerenciamento de projetos desenvolvido utilizando FastAPI, um framework moderno e de alto desempenho para construção de APIs em Python. O sistema oferece uma solução completa para gerenciamento de projetos, incluindo controle de equipes, tarefas e atualizações.

## 🚀 Tecnologias Principais
- **FastAPI**: Framework web moderno para construção de APIs
- **SQLAlchemy**: ORM (Object-Relational Mapping) para interação com banco de dados
- **Pydantic**: Validação de dados e serialização
- **Python**: Linguagem de programação principal

## 🏗️ Arquitetura do Sistema

### Estrutura de Dados
O sistema é composto por várias entidades principais:

1. **Projetos**
   - Informações básicas (nome, descrição, endereço)
   - Detalhes financeiros (orçamento)
   - Métricas (área total)
   - Datas (início, fim esperado, fim real)
   - Status do projeto
   - Empresa associada
   - Gerente responsável

2. **Equipes**
   - Associação com projetos
   - Membros da equipe
   - Empresa associada

3. **Tarefas**
   - Descrição e detalhes
   - Responsável
   - Status
   - Projeto associado

4. **Atualizações**
   - Registro de mudanças
   - Notificações
   - Histórico do projeto

### Endpoints da API

#### Projetos
- `GET /projects/`: Lista todos os projetos
- `POST /projects/`: Cria novo projeto
- `GET /projects/{id}`: Obtém detalhes de um projeto
- `PUT /projects/{id}`: Atualiza um projeto
- `DELETE /projects/{id}`: Remove um projeto

#### Equipes
- `GET /projects/{id}/teams/`: Lista equipes do projeto
- `POST /projects/{id}/teams/`: Adiciona equipe ao projeto
- `DELETE /projects/{id}/teams/{team_id}`: Remove equipe do projeto

#### Tarefas
- `GET /projects/{id}/tasks/`: Lista tarefas do projeto
- `POST /projects/{id}/tasks/`: Cria nova tarefa
- `PUT /projects/{id}/tasks/{task_id}`: Atualiza tarefa
- `DELETE /projects/{id}/tasks/{task_id}`: Remove tarefa

#### Atualizações
- `GET /projects/{id}/updates/`: Lista atualizações do projeto
- `POST /projects/{id}/updates/`: Cria nova atualização

## 🔒 Segurança e Autenticação

O sistema implementa um robusto sistema de autenticação e autorização:

- Autenticação baseada em tokens
- Controle de acesso baseado em papéis (RBAC)
- Verificação de permissões por empresa
- Superusuários com acesso total
- Validação de propriedade de recursos

## 💼 Funcionalidades de Negócio

### Gerenciamento de Projetos
- Criação e edição de projetos
- Controle de orçamento
- Acompanhamento de prazos
- Gestão de status
- Localização e endereçamento

### Gestão de Equipes
- Associação de equipes a projetos
- Controle de membros
- Validação de pertencimento à empresa

### Controle de Tarefas
- Criação e atribuição de tarefas
- Acompanhamento de progresso
- Definição de responsáveis
- Status e prioridades

### Sistema de Atualizações
- Registro de mudanças
- Notificações
- Histórico de alterações
- Rastreamento de responsáveis

## 🔄 Fluxo de Dados

1. **Criação de Projeto**
   - Validação de dados
   - Verificação de permissões
   - Criação de registros relacionados

2. **Gestão de Equipes**
   - Validação de pertencimento à empresa
   - Controle de duplicidade
   - Atualização de relacionamentos

3. **Controle de Tarefas**
   - Validação de responsáveis
   - Atualização de status
   - Notificações automáticas

4. **Sistema de Atualizações**
   - Registro de mudanças
   - Notificações para stakeholders
   - Manutenção de histórico

## 🛠️ Requisitos Técnicos

### Dependências Principais
- Python 3.7+
- FastAPI
- SQLAlchemy
- Pydantic
- Banco de dados compatível com SQLAlchemy

### Configuração do Ambiente
1. Instalação das dependências
2. Configuração do banco de dados
3. Configuração de variáveis de ambiente
4. Inicialização do servidor

## 📈 Escalabilidade

O sistema foi projetado considerando:
- Separação clara de responsabilidades
- Arquitetura modular
- Possibilidade de expansão
- Performance e otimização
- Manutenibilidade do código

## 🔍 Validações e Tratamento de Erros

O sistema implementa:
- Validação de dados de entrada
- Tratamento de exceções
- Mensagens de erro claras
- Logs de operações
- Rastreamento de problemas

## 📝 Conclusão

Este sistema de gerenciamento de projetos oferece uma solução completa e robusta para empresas que necessitam gerenciar múltiplos projetos, equipes e tarefas. Com sua arquitetura moderna e recursos abrangentes, ele se destaca como uma ferramenta poderosa para gestão de projetos corporativos.

# FastAPI Project

Projeto base desenvolvido com FastAPI.

## Requisitos

- Python 3.8+
- Virtualenv

## Configuração do Ambiente

1. Clone o repositório:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente (opcional):
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./app.db
```

## Executando o Projeto

```bash
uvicorn main:app --reload
```

O servidor estará disponível em http://localhost:8000

## Documentação da API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estrutura do Projeto

```
.
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   └── api.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── base.py
│   ├── models/
│   │   └── base.py
│   ├── schemas/
│   └── services/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## Testes

```bash
pytest
```

# API de Propriedades

Este documento descreve os endpoints disponíveis para gerenciamento de propriedades.

## Autenticação

Todos os endpoints requerem autenticação. O token deve ser enviado no header da requisição:
```
Authorization: Bearer <seu_token>
```

## Endpoints

### Listar Propriedades
```http
GET /properties/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

**Exemplo de Resposta:**
```json
[
  {
    "id": 1,
    "name": "Apartamento 101",
    "description": "Apartamento com vista para o mar",
    "type": "APARTMENT",
    "status": "UNDER_CONSTRUCTION",
    "address": "Rua das Flores, 123",
    "unit_number": "101",
    "floor": 1,
    "area": 80.5,
    "bedrooms": 2,
    "bathrooms": 1,
    "garage_spots": 1,
    "price": 250000.00,
    "construction_cost": 200000.00,
    "start_date": "2024-01-01",
    "expected_completion_date": "2024-06-01",
    "actual_completion_date": null,
    "is_sold": false,
    "sale_date": null,
    "sale_price": null,
    "project_id": 1
  }
]
```

### Criar Propriedade
```http
POST /properties/
```

**Parâmetros (Form Data):**
- `name` (obrigatório): Nome da propriedade
- `description` (opcional): Descrição da propriedade
- `type` (obrigatório): Tipo da propriedade (APARTMENT, HOUSE, COMMERCIAL, LAND)
- `status` (obrigatório): Status da propriedade (PLANNING, UNDER_CONSTRUCTION, READY, SOLD)
- `address` (opcional): Endereço
- `unit_number` (opcional): Número da unidade
- `floor` (opcional): Andar
- `area` (opcional): Área em m²
- `bedrooms` (opcional): Número de quartos
- `bathrooms` (opcional): Número de banheiros
- `garage_spots` (opcional): Número de vagas de garagem
- `price` (opcional): Preço de venda
- `construction_cost` (opcional): Custo de construção
- `start_date` (opcional): Data de início (YYYY-MM-DD)
- `expected_completion_date` (opcional): Data prevista de conclusão (YYYY-MM-DD)
- `actual_completion_date` (opcional): Data real de conclusão (YYYY-MM-DD)
- `is_sold` (opcional): Se está vendido
- `sale_date` (opcional): Data da venda (YYYY-MM-DD)
- `sale_price` (opcional): Preço de venda
- `project_id` (obrigatório): ID do projeto

**Exemplo de Requisição:**
```http
POST /properties/
Content-Type: multipart/form-data

name=Apartamento 101
description=Apartamento com vista para o mar
type=APARTMENT
status=UNDER_CONSTRUCTION
address=Rua das Flores, 123
unit_number=101
floor=1
area=80.5
bedrooms=2
bathrooms=1
garage_spots=1
price=250000.00
construction_cost=200000.00
start_date=2024-01-01
expected_completion_date=2024-06-01
project_id=1
```

### Obter Propriedade por ID
```http
GET /properties/{property_id}
```

**Parâmetros Path:**
- `property_id` (obrigatório): ID da propriedade

### Atualizar Propriedade
```http
PUT /properties/{property_id}
```

**Parâmetros Path:**
- `property_id` (obrigatório): ID da propriedade

**Parâmetros (Form Data):**
- Todos os campos são opcionais, exceto o `property_id`
- Mesmos campos do POST, mas todos opcionais

### Deletar Propriedade
```http
DELETE /properties/{property_id}
```

**Parâmetros Path:**
- `property_id` (obrigatório): ID da propriedade

### Listar Propriedades por Projeto
```http
GET /properties/project/{project_id}/
```

**Parâmetros Path:**
- `project_id` (obrigatório): ID do projeto

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

### Listar Propriedades por Status
```http
GET /properties/status/{status}/
```

**Parâmetros Path:**
- `status` (obrigatório): Status da propriedade (PLANNING, UNDER_CONSTRUCTION, READY, SOLD)

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

### Listar Atualizações de Propriedade
```http
GET /properties/{property_id}/updates/
```

**Parâmetros Path:**
- `property_id` (obrigatório): ID da propriedade

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

### Criar Atualização de Propriedade
```http
POST /properties/{property_id}/updates/
```

**Parâmetros Path:**
- `property_id` (obrigatório): ID da propriedade

**Parâmetros (JSON):**
```json
{
  "property_id": 1,
  "title": "Atualização de Status",
  "description": "Obra iniciada",
  "user_id": 1  // opcional, se não informado será usado o usuário atual
}
```

# API de Usuários

## Listar Usuários
```http
GET /users/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

**Observação:** Apenas superusuários podem listar todos os usuários.

## Criar Usuário
```http
POST /users/
```

**Parâmetros (Form Data):**
- `email` (obrigatório): Email do usuário
- `password` (obrigatório): Senha do usuário
- `full_name` (obrigatório): Nome completo
- `company_id` (opcional): ID da empresa
- `is_superuser` (opcional): Se é superusuário (default: false)

## Atualizar Usuário Atual
```http
PUT /users/me
```

**Parâmetros (JSON):**
- `password` (opcional): Nova senha
- `full_name` (opcional): Novo nome completo
- `email` (opcional): Novo email

## Obter Usuário Atual
```http
GET /users/me
```

## Obter Usuário por ID
```http
GET /users/{user_id}
```

**Parâmetros Path:**
- `user_id` (obrigatório): ID do usuário

## Deletar Usuário
```http
DELETE /users/{user_id}
```

**Parâmetros Path:**
- `user_id` (obrigatório): ID do usuário

**Observação:** Apenas superusuários podem deletar usuários.

# API de Projetos

## Listar Projetos
```http
GET /projects/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

## Criar Projeto
```http
POST /projects/
```

**Parâmetros (Form Data):**
- `name` (obrigatório): Nome do projeto
- `description` (opcional): Descrição do projeto
- `address` (opcional): Endereço
- `city` (opcional): Cidade
- `state` (opcional): Estado
- `zip_code` (opcional): CEP
- `total_area` (opcional): Área total
- `budget` (opcional): Orçamento
- `start_date` (opcional): Data de início (YYYY-MM-DD)
- `expected_end_date` (opcional): Data prevista de término (YYYY-MM-DD)
- `actual_end_date` (opcional): Data real de término (YYYY-MM-DD)
- `status` (opcional): Status do projeto
- `company_id` (obrigatório): ID da empresa
- `manager_id` (opcional): ID do gerente

## Obter Projeto por ID
```http
GET /projects/{project_id}
```

**Parâmetros Path:**
- `project_id` (obrigatório): ID do projeto

## Atualizar Projeto
```http
PUT /projects/{project_id}
```

**Parâmetros Path:**
- `project_id` (obrigatório): ID do projeto

**Parâmetros (Form Data):**
- Todos os campos do POST são opcionais

## Deletar Projeto
```http
DELETE /projects/{project_id}
```

**Parâmetros Path:**
- `project_id` (obrigatório): ID do projeto

# API de Clientes

## Listar Clientes
```http
GET /clients/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

## Criar Cliente
```http
POST /clients/
```

**Parâmetros (Form Data):**
- `name` (obrigatório): Nome do cliente
- `email` (obrigatório): Email do cliente
- `phone` (opcional): Telefone
- `address` (opcional): Endereço
- `city` (opcional): Cidade
- `state` (opcional): Estado
- `zip_code` (opcional): CEP
- `company_id` (obrigatório): ID da empresa
- `notes` (opcional): Observações

## Obter Cliente por ID
```http
GET /clients/{client_id}
```

**Parâmetros Path:**
- `client_id` (obrigatório): ID do cliente

## Listar Leads do Cliente
```http
GET /clients/{client_id}/leads/
```

**Parâmetros Path:**
- `client_id` (obrigatório): ID do cliente

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

# API de Leads

## Listar Leads
```http
GET /leads/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

## Criar Lead
```http
POST /leads/
```

**Parâmetros (Form Data):**
- `client_id` (obrigatório): ID do cliente
- `status` (obrigatório): Status do lead
- `first_contact_date` (opcional): Data do primeiro contato (YYYY-MM-DD)
- `last_contact_date` (opcional): Data do último contato (YYYY-MM-DD)
- `next_contact_date` (opcional): Data do próximo contato (YYYY-MM-DD)
- `visit_date` (opcional): Data da visita (YYYY-MM-DD)
- `interest_level` (opcional): Nível de interesse (1-5)
- `budget` (opcional): Orçamento
- `notes` (opcional): Observações
- `assigned_user_id` (opcional): ID do usuário responsável

## Listar Leads por Status
```http
GET /leads/status/{status}/
```

**Parâmetros Path:**
- `status` (obrigatório): Status do lead

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

## Listar Leads por Usuário
```http
GET /leads/assigned/{user_id}/
```

**Parâmetros Path:**
- `user_id` (obrigatório): ID do usuário

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

# API de Empresas

## Listar Empresas
```http
GET /companies/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

## Criar Empresa
```http
POST /companies/
```

**Parâmetros (Form Data):**
- `name` (obrigatório): Nome da empresa
- `cnpj` (opcional): CNPJ
- `address` (opcional): Endereço
- `city` (opcional): Cidade
- `state` (opcional): Estado
- `zip_code` (opcional): CEP
- `phone` (opcional): Telefone
- `email` (opcional): Email

## Obter Empresa por ID
```http
GET /companies/{company_id}
```

**Parâmetros Path:**
- `company_id` (obrigatório): ID da empresa

# API de Equipes

## Listar Equipes
```http
GET /teams/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

## Criar Equipe
```http
POST /teams/
```

**Parâmetros (Form Data):**
- `name` (obrigatório): Nome da equipe
- `description` (opcional): Descrição
- `company_id` (obrigatório): ID da empresa
- `leader_id` (opcional): ID do líder da equipe

# API de Despesas

## Listar Despesas
```http
GET /expenses/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

## Criar Despesa
```http
POST /expenses/
```

**Parâmetros (Form Data):**
- `description` (obrigatório): Descrição da despesa
- `amount` (obrigatório): Valor
- `date` (obrigatório): Data (YYYY-MM-DD)
- `category` (obrigatório): Categoria
- `project_id` (opcional): ID do projeto
- `company_id` (obrigatório): ID da empresa
- `receipt` (opcional): Comprovante (arquivo)

# API de Contratos

## Listar Contratos
```http
GET /contracts/
```

**Parâmetros Query:**
- `skip` (opcional): Número de registros para pular (default: 0)
- `limit` (opcional): Limite de registros por página (default: 100)

## Criar Contrato
```http
POST /contracts/
```

**Parâmetros (Form Data):**
- `contract_number` (obrigatório): Número do contrato
- `type` (obrigatório): Tipo do contrato
- `description` (opcional): Descrição
- `client_id` (obrigatório): ID do cliente
- `property_id` (obrigatório): ID da propriedade
- `signing_date` (obrigatório): Data de assinatura (YYYY-MM-DD)
- `expiration_date` (opcional): Data de expiração (YYYY-MM-DD)
- `contract_value` (obrigatório): Valor do contrato
- `status` (opcional): Status do contrato
- `notes` (opcional): Observações

## Obter Contrato por ID
```http
GET /contracts/{contract_id}
```

**Parâmetros Path:**
- `contract_id` (obrigatório): ID do contrato

# API de Dashboard

## Obter Resumo do Dashboard
```http
GET /dashboard/summary
```

Retorna métricas resumidas para o dashboard, incluindo:
- Total de projetos
- Total de clientes
- Total de leads
- Total de contratos
- Total de despesas
- Total de receitas

# Autenticação

## Login
```http
POST /login/access-token
```

**Parâmetros (Form Data):**
- `username` (obrigatório): Email do usuário
- `password` (obrigatório): Senha do usuário

## Testar Token
```http
POST /login/test-token
```

**Observação:** Requer token de autenticação no header.

# Observações Gerais

1. Todos os endpoints requerem autenticação
2. Usuários não-superusuários só podem acessar dados de sua própria empresa
3. Datas devem ser enviadas no formato YYYY-MM-DD
4. Valores monetários devem ser enviados como números decimais
5. Arquivos devem ser enviados como multipart/form-data
6. Todos os endpoints de listagem suportam paginação com `skip` e `limit` 