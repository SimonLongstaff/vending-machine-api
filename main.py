from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from database_utils import bootstrap_database
from routes.products_routes import router as products_router
from routes.vending_machine_routes import router as vending_machine_router

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5173/",
    "http://localhost:5173/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bootstrap_database()

app.include_router(products_router)
app.include_router(vending_machine_router)
