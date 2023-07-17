from typing import Annotated, List

from fastapi import FastAPI, HTTPException, Query

from game.checkers import Checkers
from util.globalconst import BLACK, KING, MAN, WHITE, square_map

app = FastAPI()


# example - http://localhost:8000/legal_moves/?to_move=black&bm=11&bm=15&bk=19&bk=4&wm=30&wm=31&wk=29")
@app.get("/legal_moves/")
async def legal_moves(to_move: Annotated[str, Query(title="Player to move", pattern=r"\b(black|white)\b",
                                                    description="black or white are valid selections")],
                      bm: Annotated[List[int], Query(title="Black men",
                                                     description="Squares with black men")] = [],
                      bk: Annotated[List[int], Query(title="Black kings", description="Squares with black kings")] = [],
                      wm: Annotated[List[int], Query(title="White men", description="Squares with white men")] = [],
                      wk: Annotated[List[int], Query(title="White kings",
                                                     description="Squares with white kings")] = []):
    sbm, sbk, swm, swk = set(bm), set(bk), set(wm), set(wk)
    if len(bm) != len(sbm):
        raise HTTPException(status_code=422, detail="Repeated values for black men")
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

    state = Checkers()
    state.clear()
    sq = state.squares
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
    state.to_move = to_move
    return {"legal_moves": str(state.legal_moves())}
