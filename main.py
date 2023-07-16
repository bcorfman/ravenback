from fastapi import FastAPI, Query
from typing import Annotated, List

app = FastAPI()

# example - http://localhost:8000/legal_moves/?to_move=black&bm=11&bm=15&bk=19&bk=4&wm=30&wm=31&wk=29")
@app.get("/legal_moves/")
async def legal_moves(to_move: Annotated[str, Query(title="Player to move", pattern=r"\b(black|white)\b",
                                                    description="black or white are valid selections")],
                      bm: Annotated[List[int], Query(title="Black men", description="Squares with black men", 
                                                     ge=1, le=32)], 
                      bk: Annotated[List[int], Query(title="Black kings", description="Squares with black kings",
                                                     ge=1, le=32)], 
                      wm: Annotated[List[int], Query(title="White men", description="Squares with white men",
                                                     ge=1, le=32)], 
                      wk: Annotated[List[int], Query(title="White kings", description="Squares with white kings",
                                                     ge=1, le=32)]):
    return {"output": "1,2,3"}
