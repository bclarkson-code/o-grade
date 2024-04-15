import datetime
import sqlite3

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

conn = sqlite3.connect("db.db")
cursor = conn.cursor()


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/v0/ascents", response_class=HTMLResponse)
async def get_table_data(
    request: Request, rows: int = 10, page: int = 0, sort_by: str = "date"
):
    # Query the 'ascents' table
    offset = page * rows
    query = f"""
    SELECT zlaggableName, cragName, countryName, date, "O-grade", difficulty
    FROM 'ascents'
    WHERE "O-grade" != "?"
    ORDER BY {sort_by} DESC
    LIMIT {rows}
    OFFSET {offset}
    """
    cursor.execute(query)
    table_data = cursor.fetchall()

    # Convert the tuples to dictionaries for easier access in the template
    table_data = [
        {
            "name": row[0],
            "crag": row[1],
            "country": row[2],
            "date": datetime.datetime.fromisoformat(row[3]).strftime("%Y-%m-%d"),
            "ograde": f"O-{row[4]}",
            "sportgrade": row[5],
        }
        for row in table_data
    ]
    url = f'/api/v0/ascents?page={page+1}&rows={rows}&sort_by={sort_by}'
    return templates.TemplateResponse(
        "table_data.html",
        {"request": request, "data": table_data, "url": url},
    )
