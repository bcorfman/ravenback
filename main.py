from typing import Annotated, List

from deta import Deta
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from game.checkers import Checkers
from parsing.PDN import PDNReader, PDNWriter
from util.globalconst import BLACK, KING, MAN, WHITE, keymap, square_map

starlette_config = Config('env.txt')

app = FastAPI()
app.add_middleware(SessionMiddleware,
                   secret_key=starlette_config.get('SECRET_KEY'),
                   max_age=None,
                   same_site='Strict')


@app.post("/create_session/")
async def create_session():
    board = Checkers()
    state = board.curr_state
    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state(
    )
    pdn = {
        "pdn":
        PDNWriter.to_string('', '', '', '', '', '', next_to_move, black_men,
                            white_men, black_kings, white_kings, '',
                            'white_on_top', [])
    }
    deta = Deta(starlette_config.get('DETA_SPACE_DATA_KEY'))
    db = deta.Base("raven_db")
    d = db.put(pdn, "session")
    return JSONResponse(d)


@app.post("/end_session/")
async def end_session():
    deta = Deta(starlette_config.get('DETA_SPACE_DATA_KEY'))
    db = deta.Base('raven_db')
    db.delete('session')


# example - http://localhost:8000/legal_moves/?to_move=black&bm=11&bm=15&bk=19&bk=4&wm=30&wm=31&wk=29")
@app.get("/legal_moves/")
async def legal_moves(
    to_move: Annotated[
        str,
        Query(title="Player to move",
              pattern=r"\b(black|white)\b",
              description="black or white are valid selections")],
    bm: Annotated[
        List[int],
        Query(title="Black men", description="Squares with black men")] = [],
    bk: Annotated[List[int],
                  Query(title="Black kings",
                        description="Squares with black kings")] = [],
    wm: Annotated[
        List[int],
        Query(title="White men", description="Squares with white men")] = [],
    wk: Annotated[List[int],
                  Query(title="White kings",
                        description="Squares with white kings")] = []):
    sbm, sbk, swm, swk = set(bm), set(bk), set(wm), set(wk)
    if len(bm) != len(sbm):
        raise HTTPException(status_code=422,
                            detail="Repeated values for black men")
    if len(bk) != len(sbk):
        raise HTTPException(status_code=422,
                            detail="Repeated values for black kings")
    if len(wm) != len(swm):
        raise HTTPException(status_code=422,
                            detail="Repeated values for white men")
    if len(wk) != len(swk):
        raise HTTPException(status_code=422,
                            detail="Repeated values for white kings")
    if len(bm + bk + wm + wk) != len(sbm | sbk | swm | swk):
        raise HTTPException(status_code=422,
                            detail="Overlapping checker values")
    if not all(1 <= e <= 32 for e in sbm | sbk | swm | swk):
        raise HTTPException(status_code=422,
                            detail="Valid checker values range from 1-32")

    board = Checkers()
    board.curr_state.clear()
    sq = board.curr_state.squares
    for item in wm:
        idx = square_map[item]
        sq[idx] = WHITE | MAN
    for item in wk:
        idx = square_map[item]
        sq[idx] = WHITE | KING
    for item in bm:
        idx = square_map[item]
        sq[idx] = BLACK | MAN
    for item in bk:
        idx = square_map[item]
        sq[idx] = BLACK | KING
    board.curr_state.to_move = BLACK if to_move == "black" else WHITE

    captures = []
    for capture in board.curr_state.captures:
        jump = []
        for affected_square in capture.affected_squares[::2]:
            jump.append(keymap[affected_square[0]])
        captures.append(jump)

    moves = []
    if not captures:
        for move in board.curr_state.moves:
            squares = []
            for affected_square in move.affected_squares:
                squares.append(keymap[affected_square[0]])
            moves.append(squares)
    captures.sort()
    moves.sort()
    return JSONResponse({"captures": captures, "moves": moves})


@app.get("/cb_state/")
async def get_checkerboard_state():
    deta = Deta(starlette_config.get('DETA_SPACE_DATA_KEY'))
    db = deta.Base('raven_db')
    result = db.get('session')
    if not result:
        return JSONResponse(status_code=404,
                            content={'message': 'Session not found.'})
    reader = PDNReader.from_string(result['pdn'])
    game_params = reader.read_game(0)
    board = Checkers()
    state = board.curr_state
    state.setup_game(game_params)
    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state(
    )

    return JSONResponse({
        'to_move': next_to_move,
        'black_men': black_men,
        'black_kings': black_kings,
        'white_men': white_men,
        'white_kings': white_kings
    })


@app.post("/make_move/")
async def make_move(
    start_sq: Annotated[
        int,
        Query(title="Starting square for move",
              description="Checker location where the move starts from")],
    end_sq: Annotated[
        int,
        Query(title="Ending square for move",
              description="Checker location where the move ends")]):
    deta = Deta(starlette_config.get('DETA_SPACE_DATA_KEY'))
    db = deta.Base('raven_db')
    result = db.get('session')
    if not result:
        return JSONResponse(status_code=404,
                            content={'message': 'Session not found.'})
    # restore game from session
    reader = PDNReader.from_string(result['pdn'])
    game_params = reader.read_game(0)
    board = Checkers()
    state = board.curr_state
    state.setup_game(game_params)
    # make the move (if it's valid), then save the session.
    legal_moves = state.captures or state.moves
    found_move = False
    for move in legal_moves:
        move_start = move.affected_squares[0][0]
        move_end = move.affected_squares[-1][0]
        if start_sq == keymap[move_start] and end_sq == keymap[move_end]:
            state.make_move(move, False, False)
            found_move = True
            break
    if not found_move:
        return JSONResponse(status_code=404, content={'message':
                                                      'Illegal move. Check squares, along with player turn.'})

    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state(
    )
    pdn = {
        "pdn":
        PDNWriter.to_string('', '', '', '', '', '', next_to_move, black_men,
                            white_men, black_kings, white_kings, '',
                            'white_on_top', [])
    }
    d = db.put(pdn, "session")
    return JSONResponse(d)
