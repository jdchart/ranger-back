from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import db
from .routes_user import router as user_routes

def create_app(**kwargs) -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins = [
            f"http://localhost:{kwargs.get('port', 5173)}",
            f"https://localhost:{kwargs.get('port', 5173)}"
        ],
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"],
    )

    print("Initializing database...")

    app.include_router(user_routes)

    print("Running app...")

    return app