from serve import serve_api
from playwright.sync_api import sync_playwright

def test_valid_moves_http():
    with serve_api() as _:
        with sync_playwright() as p:
            context = p.request.new_context()
            response = context.get("http://localhost:8000/valid_moves?black_men=11,15&black_kings=19&white_men=30,31&white_kings=29&player_to_move=black")
            assert response.ok
            assert response.json()["output"] == "1,2,3"