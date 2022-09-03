from fastapi import FastAPI, Query
from pydantic import Required


app = FastAPI()

# example - http://localhost:8000/legal_moves/?to_move=black&bm=11&bm=15&bk=19&bk=4&wm=30&wm=31&wk=29")
@app.get("/legal_moves/")
async def legal_moves(to_move: str=Query(default=Required, title="Player to move", 
                                         regex=r"\b(black|white)\b",
                                         description="black or white are valid selections"),
                      bm: list[int]=Query(default=None, title="Black men", description="Squares with black men", ge=1, le=32), 
                      bk: list[int]=Query(default=None, title="Black kings", description="Squares with black kings", ge=1, le=32), 
                      wm: list[int]=Query(default=None, title="White men", description="Squares with white men", ge=1, le=32), 
                      wk: list[int]=Query(default=None, title="White kings", description="Squares with white kings", ge=1, le=32)):
        return {"output": "1,2,3"}


if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["localhost:8000"]

    asyncio.run(serve(app, config))

