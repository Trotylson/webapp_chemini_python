from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
from routers import user, login, auth, common, warehouse, openAPI
from libs.database import ENGINE
from libs.models import Base


Base.metadata.create_all(bind=ENGINE)

app = FastAPI(title="eRR0r_!", version="1.0", docs_url="/chemini-api", redoc_url="/chemini-redoc")
app.mount("/static", StaticFiles(directory="static"), name="static")

# origins = [
#     "*"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


app.include_router(common.router)
app.include_router(user.router)
app.include_router(login.router)
app.include_router(auth.router)
app.include_router(warehouse.router)
app.include_router(openAPI.router)
    