from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import get_connection, initialize_database

app = FastAPI(title="Business Analytics Dashboard API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your deployed frontend domain before production.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    initialize_database()

def build_filters(start_date, end_date, outlet, brand, category, order_type, settlement):
    clauses, params = [], []
    if start_date:
        clauses.append("order_datetime >= ?")
        params.append(f"{start_date} 00:00:00")
    if end_date:
        clauses.append("order_datetime < ?")
        params.append(f"{date.fromisoformat(end_date) + timedelta(days=1)} 00:00:00")
    for column, value in [
        ("outlet_name", outlet), ("brand", brand), ("category", category),
        ("order_type", order_type), ("settlement", settlement)
    ]:
        if value:
            clauses.append(f"{column} = ?")
            params.append(value)
    return (" WHERE " + " AND ".join(clauses) if clauses else ""), params

def fetch_all(sql, params=()):
    with get_connection() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]

def filter_args(start_date, end_date, outlet, brand, category, order_type, settlement):
    return build_filters(start_date, end_date, outlet, brand, category, order_type, settlement)

@app.get("/")
def root():
    return {"message": "Business Analytics Dashboard API", "docs": "/docs"}

@app.get("/health")
def health():
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM order_lines").fetchone()[0]
    return {"status": "ok", "records": count}

@app.get("/api/filters")
def filters():
    result = {}
    columns = {
        "outlets": "outlet_name", "brands": "brand", "categories": "category",
        "order_types": "order_type", "settlements": "settlement"
    }
    with get_connection() as conn:
        for key, column in columns.items():
            result[key] = [r[0] for r in conn.execute(
                f"SELECT DISTINCT {column} FROM order_lines WHERE {column} <> '' ORDER BY {column}"
            ).fetchall()]
        dates = conn.execute(
            "SELECT MIN(date(order_datetime)), MAX(date(order_datetime)) FROM order_lines"
        ).fetchone()
    result["min_date"], result["max_date"] = dates[0], dates[1]
    return result

@app.get("/api/overview")
def overview(
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    outlet: Optional[str] = None, brand: Optional[str] = None,
    category: Optional[str] = None, order_type: Optional[str] = None,
    settlement: Optional[str] = None
):
    where, params = filter_args(start_date, end_date, outlet, brand, category, order_type, settlement)
    rows = fetch_all(f"""
        SELECT COUNT(*) AS total_records,
               COUNT(DISTINCT bill_no) AS total_orders,
               COALESCE(SUM(price * quantity), 0) AS total_revenue,
               COALESCE(SUM(quantity), 0) AS total_quantity
        FROM order_lines {where}
    """, params)
    data = rows[0]
    data["average_order_value"] = (
        data["total_revenue"] / data["total_orders"] if data["total_orders"] else 0
    )
    return data

@app.get("/api/revenue-trend")
def revenue_trend(
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    outlet: Optional[str] = None, brand: Optional[str] = None,
    category: Optional[str] = None, order_type: Optional[str] = None,
    settlement: Optional[str] = None
):
    where, params = filter_args(start_date, end_date, outlet, brand, category, order_type, settlement)
    return fetch_all(f"""
        SELECT date(order_datetime) AS day, SUM(price * quantity) AS revenue,
               COUNT(DISTINCT bill_no) AS orders
        FROM order_lines {where}
        GROUP BY date(order_datetime) ORDER BY day
    """, params)

@app.get("/api/category-breakdown")
def category_breakdown(
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    outlet: Optional[str] = None, brand: Optional[str] = None,
    category: Optional[str] = None, order_type: Optional[str] = None,
    settlement: Optional[str] = None
):
    where, params = filter_args(start_date, end_date, outlet, brand, category, order_type, settlement)
    return fetch_all(f"""
        SELECT category, SUM(price * quantity) AS revenue, SUM(quantity) AS quantity
        FROM order_lines {where}
        GROUP BY category ORDER BY revenue DESC
    """, params)

@app.get("/api/order-types")
def order_types(
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    outlet: Optional[str] = None, brand: Optional[str] = None,
    category: Optional[str] = None, order_type: Optional[str] = None,
    settlement: Optional[str] = None
):
    where, params = filter_args(start_date, end_date, outlet, brand, category, order_type, settlement)
    return fetch_all(f"""
        SELECT order_type, COUNT(DISTINCT bill_no) AS orders
        FROM order_lines {where}
        GROUP BY order_type ORDER BY orders DESC
    """, params)

@app.get("/api/top-outlets")
def top_outlets(
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    outlet: Optional[str] = None, brand: Optional[str] = None,
    category: Optional[str] = None, order_type: Optional[str] = None,
    settlement: Optional[str] = None
):
    where, params = filter_args(start_date, end_date, outlet, brand, category, order_type, settlement)
    return fetch_all(f"""
        SELECT outlet_name, SUM(price * quantity) AS revenue,
               COUNT(DISTINCT bill_no) AS orders
        FROM order_lines {where}
        GROUP BY outlet_name ORDER BY revenue DESC LIMIT 10
    """, params)

@app.get("/api/orders")
def orders(
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    outlet: Optional[str] = None, brand: Optional[str] = None,
    category: Optional[str] = None, order_type: Optional[str] = None,
    settlement: Optional[str] = None,
    page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None
):
    where, params = filter_args(start_date, end_date, outlet, brand, category, order_type, settlement)
    if search:
        where += (" AND " if where else " WHERE ") + "(bill_no LIKE ? OR item LIKE ? OR outlet_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    with get_connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM order_lines {where}", params).fetchone()[0]
        rows = [dict(row) for row in conn.execute(f"""
            SELECT bill_no, outlet_name, order_datetime, category, order_type,
                   item, price, quantity, settlement, brand,
                   (price * quantity) AS revenue
            FROM order_lines {where}
            ORDER BY order_datetime DESC, id DESC LIMIT ? OFFSET ?
        """, params + [page_size, (page - 1) * page_size]).fetchall()]
    return {"items": rows, "total": total, "page": page, "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size}
