from random import randrange
from typing import List, Tuple
from itertools import count, product
from tabulate import tabulate
import numpy as np
from loguru import logger

from cather import open_table


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

    def __str__(self) -> str:
        to_print = np.where(self.field, self.field, '_')
        return str(tabulate(to_print, tablefmt="fancy_grid"))
    
    def add(self, num: int, pos: Tuple[int, int]) -> None:
        if num > self.max_value:
            raise NumberBig(f'Can`t put {num= } in table with {self.max_value= }')
        if self.field[pos] != 0 :
            raise PlaceAlreadyTaken(f'Can`t put {num= } in {pos= }\n{self}')

        self.field[pos] = num
        self.check()
    

    def check_group(self, group: np.ndarray, offset= Tuple[int, int]) -> None:
        nums, counts = np.unique(group, return_counts=True)
        for i in np.nonzero(counts-1)[0]:
            if nums[i] != 0:
                errors = [tuple(i) for i in np.argwhere(group == nums[i]) + offset]

                raise NumberRepeats(f"Finded repeated {nums[i]} on {errors}\n{self}")


    def check(self) -> None:
        for i in range(self.size):
            row = np.expand_dims(self.field[i, :], axis=0)
            self.check_group(row, (i, 0)) #(y, x)
            column = np.expand_dims(self.field[:, i], axis=1)
            self.check_group(column, (0, i))

        for y, row_of_cells in enumerate(np.vsplit(self.field, self.shape[0])):
            for x, cell in enumerate(np.hsplit(row_of_cells, self.shape[1])):
                offset = (y*3, x*3)
                self.check_group(cell, offset)
        
        if self.field.all():
            raise Solved('All cells filled')

class Solver:

    def __init__(self, field: Field) -> None:
        self.field = field
        self.size = self.field.size
        self.variants = np.full((self.size, self.size, self.field.max_value), True)
        self.count_variants()
    

    def count_variants(self) -> None:
        for x, y in zip(*np.nonzero(self.field.field)):
            num = self.field.field[x, y]
            self.add(num, (x, y))
    

    def add(self, num: int, pos: Tuple[int, int]) -> None:
        y, x = pos
        self.variants[y, x] = False

        self.variants[:, x, num-1] = False
        self.variants[y, :, num-1] = False

        c_x, c_y = x//3*3, y//3*3
        self.variants[c_y:c_y+3, c_x:c_x+3, num-1] = False

    
    def num_on_pos(self, y: int, x: int):
        num = np.argwhere(self.variants[y, x])
        assert len(num) == 1
        return num[0][0] + 1

    
    def find(self):
        sums = self.variants.sum(2)
        for y, x in product(range(self.size), repeat=2):
            if sums[y, x] == 1:
                num = self.num_on_pos(y, x)
                logger.info(f"Finded that at {(y, x)= } only one num available {num= }")
                self.field.add(num, (y, x))
                self.add(num, (y, x))
    
    
    def find_digits(self) -> None:
        for i in range(self.size):
            row = np.expand_dims(self.variants[i, :], axis=0)
            self.check_group(row, (i, 0))
            column = np.expand_dims(self.variants[:, i], axis=1)
            self.check_group(column, (0, i))

        for y, row_of_cells in enumerate(np.vsplit(self.variants, self.field.shape[0])):
            for x, cell in enumerate(np.hsplit(row_of_cells, self.field.shape[1])):
                self.check_group(cell, (y*3, x*3))

    
    def check_group(self, cell: np.ndarray, offset: Tuple[int, int]) -> None:
        for i in range(self.field.max_value):
            pos_to_put_num = np.argwhere(cell[:, :, i])
            if len(pos_to_put_num) == 1:
                pos = tuple(pos_to_put_num[0] + offset)
                num = i + 1
                logger.info(f"Finded that {num= } can only be plased on {pos= }")
                self.field.add(num, pos)
                self.add(num, pos)


@logger.catch
def main():
    f = Field()

    for num, pos in open_table():
        f.add(num, pos)

    old_filled = 0
    s = Solver(f)
    for i in count():
        print(f)
        filled = len(f.field.nonzero()[0])
        if filled - old_filled == 0:
            break
        old_filled = filled
        print(f'attempt {i}, solved: {filled / f.size**2 *100:0.2f}%')
        
        s.find()
        s.find_digits()

if __name__ == "__main__":
    main()
