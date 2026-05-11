from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    print("Running app...")

    return app