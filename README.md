# Business Analytics Dashboard

A full-stack restaurant analytics dashboard built from the supplied Excel dataset. It uses **React + Vite** for the interface, **FastAPI** for the API, and **SQLite** for local analytics storage.

## Dataset inspected

The supplied workbook (`backend/data/data.xlsx`) contains:

- **300,000 line-item rows**
- **110,478 unique bills/orders**
- **10 columns:** `BillNo`, `Outlet_Name`, `Order_Datetime`, `Group`, `Order_Type`, `Item`, `Price`, `Quantity`, `Settlement`, `Brand`
- Date range: **2025-06-17 to 2026-06-16**
- No missing values were found in the inspected columns.
- Revenue is calculated as `Price * Quantity` per line item. The sum across the workbook is **₹69,480,952**.

A bill can span multiple rows. Therefore, the dashboard counts orders using `COUNT(DISTINCT bill_no)`, not the number of rows.

## Features

- KPI cards: total revenue, unique orders, average order value, line-item records and units.
- Revenue trend by day.
- Revenue by menu category.
- Unique orders by order type.
- Top outlets ranked by revenue.
- Filters for date range, outlet, brand, category, order type and settlement/payment.
- Searchable, paginated line-item table.
- Export the currently visible table page to CSV.
- SQLite indexes for common filter columns and bill number.

## Architecture

```text
Excel workbook
    |
    v
Python / Pandas ETL (scripts/import_data.py)
    |
    v
SQLite database (order_lines table + indexes)
    |
    v
FastAPI endpoints (/api/overview, /api/revenue-trend, ...)
    |
    v
React + Recharts dashboard
```

### Why SQLite?

For this assessment dataset (300K rows), SQLite is a lightweight relational database that can be packaged with the backend and queried efficiently with indexes. It avoids the operational overhead of provisioning a separate database service. The backend performs aggregation in SQL and sends only summarized chart data to the browser; the browser never downloads all 300K rows.

For a multi-user production deployment with concurrent writes, larger growth, or distributed backend instances, PostgreSQL would be a stronger next step. SQLite is used here because the dataset is read-heavy and the assessment scope is time-limited.

### ETL decisions and assumptions

1. Pandas reads the Excel workbook and validates the required column names.
2. Dates are normalized to `YYYY-MM-DD HH:MM:SS`.
3. Price and quantity are converted to numeric values; rows missing required numeric/date fields are dropped.
4. Blank descriptive values are labeled `Unknown`.
5. The import is repeatable: the target table is cleared and reloaded on each run.
6. Each source row is treated as one order line. Line revenue is `price * quantity`.
7. `BillNo` is stored as text to preserve identifier formatting.
8. The provided `Settlement` field is displayed as the payment/channel dimension; the source may combine multiple settlement methods into one label.

## Run locally

### Requirements

- Python 3.10+
- Node.js 18+
- npm

### 1. Backend setup

Open a terminal in the project root:

```bash
cd backend
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\\Scripts\\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and import the Excel file:

```bash
pip install -r requirements.txt
python scripts/import_data.py
uvicorn app.main:app --reload --port 8000
```

API documentation: http://localhost:8000/docs  
Health check: http://localhost:8000/health

The default database path is `backend/data/analytics.db`. To use another path, set `DB_PATH`.

### 2. Frontend setup

Open a second terminal from the project root:

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Open the Vite URL shown in the terminal (normally http://localhost:5173).

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | API status and imported row count |
| `GET /api/filters` | Available filter values and date bounds |
| `GET /api/overview` | KPI summary |
| `GET /api/revenue-trend` | Daily revenue and order trend |
| `GET /api/category-breakdown` | Revenue and units by category |
| `GET /api/order-types` | Unique order count by order type |
| `GET /api/top-outlets` | Top 10 outlets by revenue |
| `GET /api/orders` | Paginated order-line records and search |

All analytics endpoints accept optional query parameters: `start_date`, `end_date`, `outlet`, `brand`, `category`, `order_type`, and `settlement`.

## Deployment

### Backend on Render

1. Push this repository to a **public GitHub repository**.
2. In Render, create a **New → Web Service** and connect the repository.
3. Set **Root Directory** to `backend`.
4. Set **Build Command** to `pip install -r requirements.txt`.
5. Set **Start Command** to `python scripts/import_data.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6. Deploy. The startup command imports the included workbook into SQLite before starting the API.
7. Copy the Render service URL, for example `https://your-api.onrender.com`.

Note: Render's free filesystem can be ephemeral. This project re-imports the workbook at service startup so the database can be recreated. On a paid/persistent deployment, set `DB_PATH` to a mounted persistent disk path and run the import command once when provisioning or updating the dataset.

### Frontend on Vercel

1. Import the same GitHub repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Vite**.
4. Build command: `npm run build`.
5. Output directory: `dist`.
6. Add environment variable `VITE_API_URL` with your deployed backend URL (no trailing slash).
7. Deploy and open the Vercel URL.

After deploying, verify the dashboard loads and test at least one filter. The API's CORS policy is open for assessment convenience; for a public production deployment, restrict `allow_origins` in `backend/app/main.py` to your Vercel domain.

## Performance notes

- SQL aggregates are calculated by SQLite, not in the browser.
- Database indexes are created for timestamp, bill number, outlet, category, order type and brand.
- The table API returns only 25 rows per page (maximum 100).
- Chart endpoints return grouped results rather than raw line items.
- Filter controls pass parameters to the backend so all displayed metrics use the same selected scope.

## Known scope / possible improvements

- The CSV action exports the current table page, not every matching row.
- Authentication and role-based access are not included because they are optional for this assessment.
- A future production version could use PostgreSQL, background ETL jobs, cached aggregates, automated tests and a restricted CORS allowlist.

## Submission checklist

- [ ] Push project to public GitHub.
- [ ] Deploy backend and confirm `/health` reports the imported record count.
- [ ] Deploy frontend with `VITE_API_URL`.
- [ ] Test date, outlet and category filters.
- [ ] Add the actual GitHub and live URLs to the assessment submission.
