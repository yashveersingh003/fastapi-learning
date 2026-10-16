# FastAPI Task Management API

A containerized REST API built with FastAPI and PostgreSQL, featuring JWT authentication, task management, database migrations, automated tests, and continuous integration.

## Live Demo

- **API:** https://fastapi-learning-api-3nfs.onrender.com/
- **Interactive API Documentation:** https://fastapi-learning-api-3nfs.onrender.com//docs
- **Health Check:** https://fastapi-learning-api-3nfs.onrender.com//health

## Features

- User registration and login
- JWT access tokens and refresh tokens
- Protected endpoints and role-based authorization
- Task creation, retrieval, updating, and deletion
- Task filtering, sorting, and pagination
- PostgreSQL database with SQLAlchemy
- Database schema migrations with Alembic
- Automated testing with Pytest
- Docker containerization
- GitHub Actions continuous integration

## Tech Stack

Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic · JWT · Pytest · Docker · GitHub Actions · Render · Neon

## Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/yashveersingh003/fastapi-learning.git
   cd fastapi-learning
   ```

2. Create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv venv
   ```

   Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Create a local `.env` file with your development configuration:

   ```env
   SECRET_KEY=your-local-secret
   DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=fastapi_db
   ```

   Use your own local PostgreSQL credentials. Never commit `.env` or real secrets to GitHub.

4. Apply database migrations:

   ```bash
   alembic upgrade head
   ```

5. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Open the interactive documentation at http://127.0.0.1:8000/docs.

## Run Tests

```bash
python -m pytest -q
```

GitHub Actions automatically runs the test suite on pushes to `main` and pull requests targeting `main`.

## Deployment

- **Application hosting:** Render
- **Database hosting:** Neon PostgreSQL
- **Containerization:** Docker
- **Database migrations:** Alembic

## Security Notes

- Keep secrets and database credentials out of source control.
- Use strong, unique secrets in production.
- Use HTTPS and securely manage production environment variables.

## Author

Yashveer Singh

GitHub: https://github.com/yashveersingh003
