# SIH26103 Updated Green Dashboard

Green-and-white predictive project monitoring dashboard with 40+ project records from the uploaded July 2026 PAIMANA Flash Report.

Run backend:
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

Run frontend in another terminal:
cd frontend
npm install
npm run dev

Open the Vite URL shown in the terminal.
API docs: http://127.0.0.1:8000/docs

Demo credentials: admin/admin123, officer/officer123, manager/manager123.
