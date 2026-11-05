import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="UNAL API Gateway")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/auth/login")
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

AUTH_SERVICE = "http://auth-service:8001"
USER_SERVICE = "http://user-service:8002"
FRIENDS_SERVICE = "http://friends-service:8003"
NOTIFICATIONS_SERVICE = "http://notifications-service:8004"

async def verify_token(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{AUTH_SERVICE}/verify", headers={"Authorization": f"Bearer {token}"})
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Token inválido")
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service no disponible")

@app.api_route("/auth/{path:path}", methods=["GET", "POST"])
async def auth_proxy(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        body = await request.body() if request.method == "POST" else None
        resp = await client.request(
            method=request.method,
            url=f"{AUTH_SERVICE}/{path}",
            content=body,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )
        return JSONResponse(content=resp.json(), status_code=resp.status_code)

@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(path: str, request: Request, token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        body = await request.body() if request.method in ["POST", "PUT"] else None
        params = dict(request.query_params)
        resp = await client.request(
            method=request.method,
            url=f"{USER_SERVICE}/{path}",
            content=body,
            params=params,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )
        return JSONResponse(content=resp.json(), status_code=resp.status_code)

@app.api_route("/friends/{path:path}", methods=["GET", "POST", "DELETE"])
async def friends_proxy(path: str, request: Request, token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        body = await request.body() if request.method == "POST" else None
        params = dict(request.query_params)
        resp = await client.request(
            method=request.method,
            url=f"{FRIENDS_SERVICE}/{path}",
            content=body,
            params=params,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )
        return JSONResponse(content=resp.json(), status_code=resp.status_code)

@app.api_route("/notifications/{path:path}", methods=["GET", "POST", "DELETE"])
async def notifications_proxy(path: str, request: Request, token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        body = await request.body() if request.method == "POST" else None
        params = dict(request.query_params)
        resp = await client.request(
            method=request.method,
            url=f"{NOTIFICATIONS_SERVICE}/{path}",
            content=body,
            params=params,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )
        return JSONResponse(content=resp.json(), status_code=resp.status_code)

@app.api_route("/profiles/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def profiles_proxy(path: str, request: Request, token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        body = await request.body() if request.method in ["POST", "PUT"] else None
        params = dict(request.query_params)
        resp = await client.request(
            method=request.method,
            url=f"{USER_SERVICE}/profiles/{path}",
            content=body,
            params=params,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )
        return JSONResponse(content=resp.json(), status_code=resp.status_code)