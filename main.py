from typing import Annotated, Union

from deta import Deta
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from starlette.config import Config
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from game.checkers import Checkers, calc_ai_move
from parsing.PDN import PDNReader, PDNWriter, translate_to_fen
from util.globalconst import keymap

starlette_config = Config('env.txt')
app = FastAPI()
origins = '(http://localhost:6007)|(https://localhost:6007)(http://react-checkerboard.vercel.app)|(https://react-checkerboard.vercel.app)|(https://.*\.github\.dev:6007)'

app.add_middleware(CORSMiddleware, allow_origin_regex=origins,
                   allow_methods=["GET", "POST", "OPTIONS"],
                   allow_headers=["*"])
app.add_middleware(SessionMiddleware,
                   secret_key=starlette_config.get('SECRET_KEY'),
                   max_age=None,
                   same_site='Strict')


@app.post("/create_session")
async def create_session(fen: Annotated[
    Union[str, None],
    Query(title="String in Forsyth-Edwards Notation (FEN)",
          description="If string is None, then default is starting game " +
          "position, and black to move.")] = None):
    board = Checkers()
    state = board.curr_state
    if fen is not None:
        try:
            reader = PDNReader(None)
            game_params = reader.game_params_from_fen(fen)
            state.setup_game(game_params)
        except RuntimeError:
            raise HTTPException(status_code=422,
                                detail="Invalid FEN string")
    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state()
    fen = {
        "fen":
        translate_to_fen(next_to_move, black_men, white_men, black_kings, white_kings)
    }
    deta = Deta(starlette_config.get("DETA_SPACE_DATA_KEY"))
    db = deta.Base("raven_db")
    d = db.put(fen, "session")
    return JSONResponse(d)


@app.post("/end_session")
async def end_session():
    deta = Deta(starlette_config.get('DETA_SPACE_DATA_KEY'))
    db = deta.Base('raven_db')
    db.delete('session')


# example - http://localhost:8000/legal_moves?to_move=black&bm=11&bm=15&bk=19&bk=4&wm=30&wm=31&wk=29"
@app.get("/legal_moves")
async def legal_moves(fen: Annotated[
    Union[str, None],
    Query(title="String in Forsyth-Edwards Notation (FEN)",
          description="If string is None, then default is starting game " +
          "position, and black to move.")] = None):
    board = Checkers()
    state = board.curr_state
    if fen is not None:
        try:
            reader = PDNReader(None)
            game_params = reader.game_params_from_fen(fen)
            state.setup_game(game_params)
        except (SyntaxError, RuntimeError) as e:
            # exception message held in first element of args list
            raise HTTPException(status_code=422, detail=e.args[0])
        
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


@app.get("/cb_state")
async def get_checkerboard_state():
    deta = Deta(starlette_config.get('DETA_SPACE_DATA_KEY'))
    db = deta.Base('raven_db')
    result = db.get('session')
    if not result:
        return JSONResponse(status_code=404,
                            content={'message': 'Session not found.'})
    return JSONResponse({
        'fen': result['fen']
    })


# example - https://raven-1-j8079958.deta.app/make_move?start_sq=11&end_sq=15"
@app.post("/make_move")
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
    reader = PDNReader(None)
    game_params = reader.game_params_from_fen(result['fen'])
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
        return JSONResponse(
            status_code=404,
            content={
                'message':
                'Illegal move. Check squares, along with player turn.'
            })

    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state(
    )
    fen = {
        "fen":
        translate_to_fen(next_to_move, black_men, white_men, black_kings,
                         white_kings)
    }
    d = db.put(fen, "session")
    return JSONResponse(d)


# example - https://raven-1-j8079958.deta.app/calc_move?search_time=5"
@app.post("/calc_move/")
async def calc_move(search_time: Annotated[
    int,
    Query(title="Search time for AI (seconds)",
          description="Max search time (approximate) for AI to calculate its next move")]):
    deta = Deta(starlette_config.get('DETA_SPACE_DATA_KEY'))
    db = deta.Base('raven_db')
    result = db.get('session')
    if not result:
        return JSONResponse(status_code=404,
                            content={'message': 'Session not found.'})
    # restore game from session
    reader = PDNReader(None)
    game_params = reader.game_params_from_fen(result['fen'])
    board = Checkers()
    state = board.curr_state
    state.setup_game(game_params)
    move = calc_ai_move(board, search_time)
    if not move:
        return JSONResponse(
            status_code=404,
            content={'message': 'Could not find move within search time.'})
    state.make_move(move, False, False)
    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state(
    )
    pdn = {
        "pdn":
        PDNWriter.to_string('', '', '', '', '', '', next_to_move, black_men,
                            white_men, black_kings, white_kings, '',
                            'white_on_top', [])
    }
    db.put(pdn, "session")
    move_start = move.affected_squares[0][0]
    move_end = move.affected_squares[-1][0]
    move_dict = {"start_sq": keymap[move_start], "end_sq": keymap[move_end]}
    return JSONResponse(move_dict)
