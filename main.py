# main.py
from fastapi import FastAPI
from routers import bookings, agent



app = FastAPI()

app.include_router(bookings.router, prefix="/api")
app.include_router(agent.router, prefix="/api")