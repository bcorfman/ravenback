import hug


@hug.get(examples="black_men=11,15&black_kings=19&white_men=30,31&white_kings=29&player_to_move=black")
@hug.local()
def valid_moves(black_men: hug.types.delimited_list(","), black_kings: hug.types.delimited_list(","),
                white_men: hug.types.delimited_list(","), white_kings: hug.types.delimited_list(","),
                player_to_move: hug.types.one_of(("black", "white"))):
        return {"output": "1,2,3"}

