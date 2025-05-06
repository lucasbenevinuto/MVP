FROM python:3.9-slim

WORKDIR /app

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements primeiro para aproveitar o cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Criar script para inicializar o banco de dados com o admin
RUN echo 'import os\nimport sys\nimport traceback\nsys.path.append("/app")\n\nfrom app.db.init_db import init_db\nfrom app.db.seed_db import seed_db\n\ndef main():\n    try:\n        print("Criando tabelas do banco de dados...")\n        init_db()\n        print("Tabelas criadas com sucesso!")\n        print("Inserindo dados iniciais...")\n        seed_db()\n        print("Dados inseridos com sucesso!")\n    except Exception as e:\n        print(f"ERRO: {e}")\n        print("Detalhes do erro:")\n        traceback.print_exc()\n        sys.exit(1)\n\nif __name__ == "__main__":\n    main()\n' > /app/create_admin.py

# Copiar o restante do código
COPY . .

EXPOSE 8000

# O comando será definido no docker-compose
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 