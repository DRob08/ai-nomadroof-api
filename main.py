# main.py
from fastapi import FastAPI
from routers import bookings, agent
from routers import ip  # or whatever you called the file


app = FastAPI()

app.include_router(ip.router)

app.include_router(bookings.router, prefix="/api")
app.include_router(agent.router, prefix="/api")