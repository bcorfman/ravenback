from typing import Annotated, List

from fastapi import FastAPI, HTTPException, Query

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
    return {"output": "1,2,3"}
