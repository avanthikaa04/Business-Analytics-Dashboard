
from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import get_connection, initialize_database

app = FastAPI(title="Business Analytics Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        clauses.append("order_datetime >= %s")
        params.append(f"{start_date} 00:00:00")

    if end_date:
        clauses.append("order_datetime < %s")
        params.append(
            f"{date.fromisoformat(end_date) + timedelta(days=1)} 00:00:00"
        )

    for column, value in [
        ("outlet_name", outlet),
        ("brand", brand),
        ("category", category),
        ("order_type", order_type),
        ("settlement", settlement)
    ]:
        if value:
            clauses.append(f"{column} = %s")
            params.append(value)

    return (" WHERE " + " AND ".join(clauses) if clauses else ""), params


def fetch_all(sql, params=()):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


def filter_args(start_date, end_date, outlet, brand, category, order_type, settlement):
    return build_filters(start_date, end_date, outlet, brand, category, order_type, settlement)


@app.get("/")
def root():
    return {"message": "Business Analytics Dashboard API", "docs": "/docs"}


@app.get("/health")
def health():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM order_lines")
            count = cursor.fetchone()["count"]
    return {"status": "ok", "records": count}


@app.get("/api/filters")
def filters():
    result = {}

    columns = {
        "outlets": "outlet_name",
        "brands": "brand",
        "categories": "category",
        "order_types": "order_type",
        "settlements": "settlement"
    }

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for key, column in columns.items():
                cursor.execute(
                    f"SELECT DISTINCT {column} FROM order_lines "
                    f"WHERE {column} <> '' ORDER BY {column}"
                )
                result[key] = [r[column] for r in cursor.fetchall()]

            cursor.execute("""
                SELECT
                    MIN(LEFT(order_datetime, 10)) AS min_date,
                    MAX(LEFT(order_datetime, 10)) AS max_date
                FROM order_lines
            """)
            dates = cursor.fetchone()

    result["min_date"] = dates["min_date"]
    result["max_date"] = dates["max_date"]
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
        SELECT LEFT(order_datetime, 10) AS day,
               SUM(price * quantity) AS revenue,
               COUNT(DISTINCT bill_no) AS orders
        FROM order_lines {where}
        GROUP BY LEFT(order_datetime, 10)
        ORDER BY day
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
        SELECT category, SUM(price * quantity) AS revenue,
               SUM(quantity) AS quantity
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
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None
):
    where, params = filter_args(start_date, end_date, outlet, brand, category, order_type, settlement)

    if search:
        where += (" AND " if where else " WHERE ") + (
            "(bill_no LIKE %s OR item LIKE %s OR outlet_name LIKE %s)"
        )
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) AS total FROM order_lines {where}", params
            )
            total = cursor.fetchone()["total"]

            cursor.execute(f"""
                SELECT bill_no, outlet_name, order_datetime, category, order_type,
                       item, price, quantity, settlement, brand,
                       (price * quantity) AS revenue
                FROM order_lines {where}
                ORDER BY order_datetime DESC, id DESC
                LIMIT %s OFFSET %s
            """, params + [page_size, (page - 1) * page_size])

            rows = cursor.fetchall()

    return {
        "items": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
