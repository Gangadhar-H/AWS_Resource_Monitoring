# Cloud Cost Monitor (MCA Minor Project)

Read-only tool that finds idle / underutilised cloud resources (AWS in the MVP),
estimates monthly cost and potential savings, and shows them on a dashboard.

## Run (two terminals)
**Backend** (http://localhost:8000/docs)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add READ-ONLY AWS keys + region
uvicorn app.main:app --reload
```
**Frontend** (http://localhost:5173)
```bash
cd frontend
npm install
npm run dev
```
Click **Scan Now** on the dashboard. Backend tests: `cd backend && pytest` (mocked AWS).

See `backend/README.md` for the API, rules and IAM permissions.
