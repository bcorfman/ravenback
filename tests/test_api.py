import pytest
from httpx import AsyncClient

from checkers import app


@pytest.mark.anyio
async def test_legal_moves():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/legal_moves/?to_move=black")
    assert response.status_code == 200
    assert response.json() == {"output": "1,2,3"}
