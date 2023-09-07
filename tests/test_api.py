from fastapi.testclient import TestClient

from main import app


def test_legal_moves_success_three_kings_versus_two():
    client = TestClient(app)
    response = client.get(
        '/legal_moves/?to_move=white&bk=9&bk=27&wk=10&wk=15&wk=19')
    assert response.status_code == 200
    assert response.json() == {
        "captures": [],
        "moves": [[10, 6], [10, 7], [10, 14], [15, 11], [15, 18], [19, 16],
                  [19, 23], [19, 24]]
    }


def test_legal_captures_one_king_versus_two_breeches():
    client = TestClient(app)
    response = client.get('/legal_moves/?to_move=white&bk=15&bk=22&wk=18')
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


def test_checkerboard_state_at_start():
    client = TestClient(app)
    response = client.post('/end_session/')
    response = client.post('/create_session/')
    assert response.status_code == 200
    response = client.get('/cb_state/')
    assert response.status_code == 200
    assert response.json() == {
        "to_move": "black",
        "black_men": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "black_kings": [],
        "white_men": [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
        "white_kings": []
    }


def test_checkerboard_state_after_double_jump_to_crown():
    client = TestClient(app)
    response = client.post('/end_session/')
    response = client.post('/create_session/')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=11&end_sq=15')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=24&end_sq=20')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=8&end_sq=11')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=28&end_sq=24')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=10&end_sq=14')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=32&end_sq=28')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=4&end_sq=8')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=23&end_sq=18')
    assert response.status_code == 200
    response = client.post('/make_move/?start_sq=14&end_sq=32')
    assert response.status_code == 200
    response = client.get('/cb_state/')
    assert response.status_code == 200
    assert response.json() == {
        "to_move": "white",
        "black_men": [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 15],
        "black_kings": [32],
        "white_men": [20, 21, 22, 24, 25, 26, 28, 29, 30, 31],
        "white_kings": []
    }


def test_calc_move():
    client = TestClient(app)
    response = client.post('/end_session/')
    response = client.post('/create_session/')
    assert response.status_code == 200
    response = client.post('/calc_move/?search_time=5')
    assert response.status_code == 200
    assert response.json() == {
        "start_sq": 10,
        "end_sq": 15,
    }


def test_create_session():
    client = TestClient(app)
    response = client.post('/create_session/')
    assert response.status_code == 200
    json = response.json()
    assert json[
        'pdn'] == '[Event ""]\n' + \
                  '[Date ""]\n' + \
                  '[Black ""]\n' + \
                  '[White ""]\n' + \
                  '[Site ""]\n' + \
                  '[Result ""]\n' + \
                  '[BoardOrientation "white_on_top"]\n'


def test_create_session_with_fen():
    client = TestClient(app)
    # Captive Cossacks - Pask's SOIC p. 83, Diagram 57
    response = client.post(
        '/create_session/?fen=W:W26,K27:B17,K30')
    assert response.status_code == 200
    json = response.json()
    assert json[
        'pdn'] == '[Event ""]\n' + \
                  '[Date ""]\n' + \
                  '[Black ""]\n' + \
                  '[White ""]\n' + \
                  '[Site ""]\n' + \
                  '[Result ""]\n' + \
                  '[SetUp "1"]\n' + \
                  '[FEN "W:W26,K27:B17,K30"]\n' + \
                  '[BoardOrientation "white_on_top"]\n'


def test_end_session():
    client = TestClient(app)
    response = client.post('/end_session/')
    assert response.status_code == 200
    # now try to get the checkerboard state, which shouldn't be able to
    # be found in the database any longer.
    response = client.get('/cb_state/')
    assert response.status_code == 404
