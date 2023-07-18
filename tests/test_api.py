from fastapi.testclient import TestClient

from main import app


def test_legal_moves_success_three_kings_versus_two():
    client = TestClient(app)
    response = client.get('/legal_moves/?to_move=white&bk=9&bk=27&wk=10&wk=15&wk=19')
    assert response.status_code == 200
    assert response.json() == {"captures": [],
                               "moves": [[10, 6], [10, 7], [10, 14], [15, 11], [15, 18], [19, 16], [19, 23], [19, 24]]}


def test_legal_captures_one_king_versus_two_breeches():
    client = TestClient(app)
    response = client.get(
        '/legal_moves/?to_move=white&bk=13&bk=22&wk=18')
    assert response.status_code == 200
    assert response.json() == {"captures": [[18, 11], [18, 25]], "moves": []}


def test_legal_moves_repeated_values_black_kings():
    client = TestClient(app)
    response = client.get(
        '/legal_moves/?to_move=white&bk=27&bk=27&wk=10&wk=15&wk=19')
    assert response.status_code == 422  # unprocessable content
    assert response.json() == {"detail": "Repeated values for black kings"}


def test_legal_moves_repeated_values_white_kings():
    client = TestClient(app)
    response = client.get(
        '/legal_moves/?to_move=white&bk=9&bk=27&wk=15&wk=15&wk=19')
    assert response.status_code == 422  # unprocessable content
    assert response.json() == {"detail": "Repeated values for white kings"}


def test_overlapping_checkers():
    client = TestClient(app)
    response = client.get(
        '/legal_moves/?to_move=white&bk=9&bk=27&wk=10&wk=15&wk=27')
    assert response.status_code == 422  # unprocessable content
    assert response.json() == {"detail": "Overlapping checker values"}


def test_checker_values_out_of_range():
    client = TestClient(app)
    response = client.get(
        '/legal_moves/?to_move=white&bk=9&bk=27&wk=15&wk=19&wk=0')
    assert response.status_code == 422  # unprocessable content
    assert response.json() == {
        "detail": "Valid checker values range from 1-32"
    }

    response = client.get(
        '/legal_moves/?to_move=white&bk=9&bk=27&wk=15&wk=19&wk=33')
    assert response.status_code == 422  # unprocessable content
    assert response.json() == {
        "detail": "Valid checker values range from 1-32"
    }
