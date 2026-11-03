import httpx
from nicegui import app

GATEWAY_URL = "http://gateway:8000"

def get_headers():
    token = app.storage.user.get('token')
    return {"Authorization": f"Bearer {token}"} if token else {}

async def api_get(endpoint: str, params: dict = None):
    async with httpx.AsyncClient() as client:
        return await client.get(f"{GATEWAY_URL}{endpoint}", params=params, headers=get_headers())

async def api_post(endpoint: str, json: dict = None, data: dict = None, files: dict = None, params: dict = None):
    async with httpx.AsyncClient() as client:
        return await client.post(f"{GATEWAY_URL}{endpoint}", json=json, data=data, files=files, params=params, headers=get_headers())