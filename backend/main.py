import config
from api import location
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
    if x_token != "evelyn":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


@app.get("/")
def root():
    return {"data": "Singapore Analytics"}


app.include_router(location.router, prefix="/locations", dependencies=[Depends(get_token_header)])
