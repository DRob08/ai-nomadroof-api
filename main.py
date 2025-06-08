# main.py
from fastapi import FastAPI
from routers import bookings, agent, property, contact
from fastapi.middleware.cors import CORSMiddleware
import logging


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3001"],  # <-- Frontend URL
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookings.router, prefix="/api")
app.include_router(agent.router, prefix="/api/agent")
app.include_router(property.router, prefix="/api/property")
app.include_router(contact.router, prefix="/api")

logging.basicConfig(level=logging.INFO)