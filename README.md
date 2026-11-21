# Business Analytics Dashboard

A full-stack restaurant analytics dashboard built using the supplied restaurant sales dataset containing 300,000 order-line records. The application provides interactive business metrics, revenue trends, category analysis, outlet comparisons, order-type breakdowns, and searchable order records.

## Live application

- **Frontend:** https://business-analytics-dashboard-fronte.vercel.app/
- **Backend API:** https://business-analytics-dashboard-1-pr6z.onrender.com
- **API health check:** https://business-analytics-dashboard-1-pr6z.onrender.com/health
- **GitHub repository:** https://github.com/avanthikaa04/Business-Analytics-Dashboard

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL (Neon) |
| Database driver | psycopg |
| Data processing | Pandas, OpenPyXL |
| Frontend deployment | Vercel |
| Backend deployment | Render |

## Dataset overview

The supplied Excel workbook was inspected and used as the source for the dashboard.

| Metric | Value |
|---|---:|
| Order-line records | 300,000 |
| Unique bills/orders | 110,478 |
| Total revenue | ₹69,480,952 |
| Total quantity | 434,448 |
| Average order value | ₹628.91 |
| Date range | 17 June 2025 – 16 June 2026 |
| Brand | Burger Town |
| Outlets | 6 |

The dataset contains these fields:

`BillNo`, `Outlet_Name`, `Order_Datetime`, `Group`, `Order_Type`, `Item`, `Price`, `Quantity`, `Settlement`, and `Brand`.

**Important data interpretation:** Each row represents an order line, not necessarily a complete bill. A single bill can contain multiple items and therefore multiple rows. The dashboard calculates the number of orders using distinct bill numbers rather than counting rows. Revenue is calculated as `Price × Quantity` for each line item and then aggregated.

## Dashboard features

- KPI summary including total revenue, unique orders, average order value, line-item records, and total quantity.
- Revenue trend over time.
- Revenue breakdown by menu category.
- Unique orders grouped by order type.
- Top outlets ranked by revenue.
- Filter options for date range, outlet, brand, category, order type, and settlement.
- Searchable and paginated order-line data.
- Backend API endpoints that return aggregated chart data instead of sending the entire dataset to the browser.

## Architecture

```text
Supplied Excel workbook
        |
        v
Data inspection and processing
        |
        v
Local data preparation / migration
        |
        v
Neon PostgreSQL database
        |
        v
FastAPI backend (Render)
        |
        v
React + Vite frontend (Vercel)
```

The frontend communicates with the FastAPI backend through HTTP API requests. The backend queries PostgreSQL and returns either aggregated results for charts and KPI cards or paginated records for the data table.

## Database and design decisions

### Why PostgreSQL with Neon?

The dashboard uses PostgreSQL hosted on Neon for its deployed database. PostgreSQL provides relational querying, aggregation, indexing, and support for concurrent application requests. Neon provides a managed PostgreSQL service, so a separate database server does not need to be maintained for this assessment.

The source data was prepared locally and migrated to Neon in batches of 5,000 records. The migration was designed to avoid loading all records into memory or inserting the entire dataset in one operation. The deployed backend connects to PostgreSQL using the `DATABASE_URL` environment variable.

Indexes are used on commonly queried fields, including order date/time, bill number, outlet, category, order type, and brand, to support filtering and aggregation.

### Data handling and assumptions

1. The Excel workbook was inspected to understand its columns, date range, and record count.
2. Each source row is treated as one order line.
3. Revenue is calculated as `price * quantity`.
4. Unique orders are counted using distinct bill numbers because one bill may contain multiple order lines.
5. The `BillNo` identifier is stored as text to preserve its identifier format.
6. The `Settlement` field is treated as the settlement/payment dimension provided by the source dataset.
7. The source workbook and database credentials are not committed to the public repository.

## Backend API

The backend exposes the following endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /` | Basic API response |
| `GET /health` | API status and database record count |
| `GET /api/filters` | Available filter values and date range |
| `GET /api/overview` | Dashboard KPI summary |
| `GET /api/revenue-trend` | Revenue trend over time |
| `GET /api/category-breakdown` | Revenue and quantity grouped by category |
| `GET /api/order-types` | Unique orders grouped by order type |
| `GET /api/top-outlets` | Top outlets ranked by revenue |
| `GET /api/orders` | Searchable, paginated order-line records |

Analytics endpoints support the available dashboard filters, such as date range, outlet, brand, category, order type, and settlement, where applicable.

Interactive API documentation is available at:

`https://business-analytics-dashboard-1-pr6z.onrender.com/docs`

## Run locally

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- A PostgreSQL database (for example, a Neon database)

### 1. Clone the repository

```bash
git clone https://github.com/avanthikaa04/Business-Analytics-Dashboard.git
cd Business-Analytics-Dashboard
```

### 2. Configure the backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your own PostgreSQL connection string:

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST/DATABASE?sslmode=require
```

Replace the example values with the connection details from your own PostgreSQL database. Do not commit `.env` or share database credentials publicly.

Start the backend from the `backend` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

The local API will be available at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`.

**Data requirement:** The database must contain the dashboard dataset for the analytics endpoints to return the same results as the live application. The original workbook and local migration utility are not included in the public repository.

### 3. Configure and run the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

## Deployment

### Backend — Render

The FastAPI backend is deployed on Render.

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `DATABASE_URL` (configured privately in the Render service)

### Database — Neon

The application uses a Neon PostgreSQL database. The backend reads its connection string from the `DATABASE_URL` environment variable. Database credentials are not stored in the source code or public repository.

### Frontend — Vercel

The React + Vite frontend is deployed on Vercel.

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_URL`, set to the deployed Render backend URL.

## Performance considerations

- PostgreSQL performs filtering and aggregation on the backend.
- Indexes are created for commonly filtered and queried columns.
- Chart endpoints return grouped results rather than all 300,000 source rows.
- The orders endpoint uses pagination to limit the amount of data returned per request.
- The frontend requests only the data needed for the selected dashboard view and filters.

## Limitations and possible improvements

- The public repository does not include the original Excel workbook, database dump, or database credentials.
- Reproducing the exact populated dashboard locally requires loading the source dataset into a PostgreSQL database.
- Authentication and role-based access are not implemented.
- Further improvements could include automated tests, caching frequently requested aggregates, background data refresh jobs, and stricter production CORS configuration.

## Submission links

- **GitHub:** https://github.com/avanthikaa04/Business-Analytics-Dashboard
- **Live dashboard:** https://business-analytics-dashboard-fronte.vercel.app/
- **Backend API:** https://business-analytics-dashboard-1-pr6z.onrender.com

---

**Developed by:** Sri Avanthikaa
