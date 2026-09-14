from fastapi import FastAPI
from blogforge_ai.api.routes.blog import app
app = FastAPI()

app.include_router()
