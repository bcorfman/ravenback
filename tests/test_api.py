import pytest
from httpx import AsyncClient

from main import app


async def test_legal_moves():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/legal_moves/?to_move=black")
    assert response.status_code == 200
    assert response.json() == {"output": "1,2,3"}


async def test_legal_moves_validation_error_illegal_player():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/legal_moves/?to_move=red")
    assert response.status_code == 422


async def test_legal_moves_validation_error_illegal_range():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/legal_moves/?to_move=black&bm=5&bk=33")
    assert response.status_code == 422
