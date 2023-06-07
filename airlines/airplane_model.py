from pydantic import BaseModel, root_validator
from typing import List


class Seat(BaseModel):
    id: int
    row: int
    column: int
    available: bool
    name: str
    seat_type: str = "economy"


class Airplane(BaseModel):
    model_name: str
    rows: int
    columns: int
    seats: List[Seat]

    @root_validator
    def validate_seats(cls, values):
        rows = values.get('rows')
        columns = values.get('columns')
        seats = values.get('seats')
        for seat in seats:
            if seat.row > rows:
                raise ValueError(f"Invalid row value. Too many row in seats: '{seat}'")
            if seat.column > columns:
                raise ValueError(f"Invalid column value. Too many column in seats in seats: '{seat}'")

        return values

    def get_types_seat(self):
        types_seat = set([seat.seat_type for seat in self.seats if seat.available])
        return types_seat


if __name__ == '__main__':
    col_to_name = {
        1: "А{row}",
        2: "B{row}",
        3: "C{row}",
        4: "pass",
        5: "D{row}",
        6: "E{row}",
        7: "F{row}",
    }
    id = 1
    seats = []
    for i in range(1, 31):
        for j in range(1, 8):
            seats.append(Seat(id=id, row=i, column=j,
                              available=True if j != 4 else False,
                              name=col_to_name[j].format(row=i)))
            id += 1

    airplane = Airplane(
        model_name="Boeing 737",
        rows=30,
        columns=7,
        seats=seats)
