import config
from api import recommender
from fastapi import Depends, FastAPI, Header, HTTPException
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title=config.TITLE,
    description=config.DESCRIPTION,
    version=config.VERSION,
)

# Set all CORS enabled origins
if config.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def get_token_header(x_token: str = Header(...)):
    if x_token != "recommender":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


@app.get("/")
def root():
    return {"data": "Recommender"}


app.include_router(
    recommender.router, prefix="/recommenders", dependencies=[Depends(get_token_header)]
)
