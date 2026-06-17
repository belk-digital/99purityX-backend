## 🛠 UV Installation (One Time Only)

```````````powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

After running above, close and reopen PowerShell, then check:

```uv --version


````🚀 Quick Start
1. Go to Backend Folder
2. Install Dependencies

`````uv sync

3. Activate Environment

``````.venv\Scripts\activate

4. Create Environment File

```````copy .env.example .env


5. Run Database Migrations

````````alembic upgrade head

6. Start Server
`````````uv run uvicorn app.main:app --reload --port 8000


``````````Test URLs
App: http://localhost:8000
API Docs: http://localhost:8000/docs
```````````
