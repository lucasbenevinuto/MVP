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