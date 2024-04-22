import datetime
import os
import sqlite3
from typing import Annotated

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# load environment variables
load_dotenv()
CAPTCHA_SITE_KEY = os.environ["CAPTCHA_SITE_KEY"]


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
    url = f"/api/v0/ascents?page={page+1}&rows={rows}&sort_by={sort_by}"
    return templates.TemplateResponse(
        "table_data.html",
        {"request": request, "data": table_data, "url": url},
    )


@app.get("/api/v0/routeForm", response_class=HTMLResponse)
async def get_route_form(request: Request):
    return templates.TemplateResponse(
        "new_route_form.html",
        {"request": request, "CAPTCHA_SITE_KEY": CAPTCHA_SITE_KEY},
    )


@app.post("/api/v0/submitRoute", response_class=HTMLResponse)
async def submit_new_route(
    request: Request,
    route_name: Annotated[str, Form()],
    crag_name: Annotated[str, Form()],
    country: Annotated[str, Form()],
    date: Annotated[datetime.date, Form()],
    sport_grade: Annotated[str, Form()],
    evidence: Annotated[str, Form()],
):

    query = """
    INSERT INTO submission (
    zlaggableName, cragName, countryName, date, "O-grade", difficulty)
    VALUES (?, ?, ?, ?, ?, ?)"""
    data = (
        route_name,
        crag_name,
        country,
        date.isoformat(),
        sport_grade,
        evidence,
    )
    cursor.execute(query, data)
    return templates.TemplateResponse("form_submit_success.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
