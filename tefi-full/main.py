from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
import uuid
import os
import datetime

app = FastAPI(title="TEFI Local – Patent NO 349195")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sqlite_file_name = "tefi.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

class Property(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    address: str
    price_guide: int
    unique_code: str = str(uuid.uuid4())[:8]
    created_at: datetime.datetime = datetime.datetime.now()
    ended: bool = False

SQLModel.metadata.create_all(engine)

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    with Session(engine) as session:
        properties = session.exec(select(Property)).all()
    return templates.get_template("dashboard.html").render({"request": request, "properties": properties, "patent": "NO 349195"})

@app.post("/new-property")
async def new_property(address: str = Form(...), price_guide: str = Form(...)):
    price = int("".join(filter(str.isdigit, price_guide)))
    with Session(engine) as session:
        prop = Property(address=address, price_guide=price)
        session.add(prop)
        session.commit()
        session.refresh(prop)
    return RedirectResponse(url="/", status_code=303)

@app.get("/bud/{code}", response_class=HTMLResponse)
async def bidder_page(request: Request, code: str):
    with Session(engine) as session:
        prop = session.exec(select(Property).where(Property.unique_code == code)).first()
        if not prop:
            return HTMLResponse("Bolig ikke funnet – sjekk linken", status_code=404)
    return templates.get_template("bidder.html").render({"request": request, "prop": prop, "patent": "NO 349195"})

