from dataclasses import astuple, dataclass

import numpy as np
from tabulate import tabulate
from grid_formatter import format_grid

# from cather import open_table
from pos import Pos


class NumberRepeats(Exception):
    pass

class Solved(Exception):
    pass

class PlaceAlreadyTaken(Exception):
    pass

class NumberBig(Exception):
    pass




class Field:
    def __init__(self, shape = (3, 3)) -> None:
        self.shape = shape
        self.size = shape[0] * shape[1]
        self.max_value = self.size
        self.field = np.full((self.size, self.size), 0)


    def from_file(self, file: str):
        for num, pos in open_table(file):
            self.add(num, pos)

    def __str__(self) -> str:
        to_print = np.where(self.field, self.field, '_')
        return format_grid(to_print)
        return str(tabulate(to_print, tablefmt="fancy_grid"))

    def add(self, num: int, pos: Pos) -> None:
        if num > self.max_value:
            raise NumberBig(f'Can`t put {num= } in table with {self.max_value= }')
        if self.field[astuple(pos)] != 0 :
            raise PlaceAlreadyTaken(f'Can`t put {num= } in {pos= }\n{self}')

        self.field[astuple(pos)] = num
        self.check()

    def check_group(self, group: np.ndarray, offset= Pos) -> None:
        nums, counts = np.unique(group, return_counts=True)
        for i in np.nonzero(counts-1)[0]:
            if nums[i] != 0:
                errors = [Pos(*i) + offset for i in np.argwhere(group == nums[i])]

                raise NumberRepeats(f"Finded repeated {nums[i]} on {errors}\n{self}")

    def check(self) -> None:
        for i in range(self.size):
            row = np.expand_dims(self.field[i, :], axis=0)
            self.check_group(row, offset=Pos(y=i, x=0))
            column = np.expand_dims(self.field[:, i], axis=1)
            self.check_group(column, offset=Pos(y=0, x=i))

        for y, row_of_cells in enumerate(np.vsplit(self.field, self.shape[0])):
            for x, cell in enumerate(np.hsplit(row_of_cells, self.shape[1])):
                self.check_group(cell, offset=Pos(y=y*3, x=x*3))
        
        if self.field.all():
            raise Solved('All cells filled')
    

if __name__ == "__main__":
    f = Field()
    f.add(1, Pos(0, 0))
    f.add(1, Pos(y=0, x=6))
    print(f)
