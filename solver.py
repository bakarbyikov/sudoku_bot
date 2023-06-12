import os
from copy import deepcopy
from itertools import chain, count, product
from time import perf_counter
from typing import Tuple

import numpy as np
from loguru import logger

from field import Field, Solved, astuple
from pos import Pos


class Solver:

    def __init__(self, field: Field) -> None:
        self.field = field
        self.size = self.field.size
        self.variants = np.full((self.size, self.size, self.field.max_value), True)
        self.count_variants()
    

    def count_variants(self) -> None:
        for y, x in np.argwhere(self.field.field):
            num = self.field.field[y, x]
            self.add(num, Pos(y, x))
    

    def add(self, num: int, pos: Pos) -> None:
        self.variants[astuple(pos)] = False

        self.variants[:, pos.x, num-1] = False
        self.variants[pos.y, :, num-1] = False

        c_x, c_y = pos.x//3*3, pos.y//3*3
        self.variants[c_y:c_y+3, c_x:c_x+3, num-1] = False

    
    def num_on_pos(self, pos: Pos) -> list[int]:
        num = np.argwhere(self.variants[astuple(pos)]) + 1
        # assert len(num) == 1
        return num[:, 0]

    
    def find(self) -> Tuple[int, Pos]:
        for y, x in product(range(self.size), repeat=2):
            if np.sum(self.variants[y, x]) == 1:
                pos = Pos(y, x)
                num = self.num_on_pos(pos)
                assert len(num) == 1, f'{num = } {self.variants[y, x] = }'
                # logger.info(f"Finded that at {(y, x)= } only one num available {num= }")
                yield num, pos
    
    
    def find_digits(self) -> Tuple[int, Pos]:
        for i in range(self.size):
            row = np.expand_dims(self.variants[i, :], axis=0)
            yield from self.check_group(row, offset=Pos(y=i, x=0))
            column = np.expand_dims(self.variants[:, i], axis=1)
            yield from self.check_group(column, offset=Pos(y=0, x=i))

        for y, row_of_cells in enumerate(np.vsplit(self.variants, self.field.shape[0])):
            for x, cell in enumerate(np.hsplit(row_of_cells, self.field.shape[1])):
                yield from self.check_group(cell, offset=Pos(y=y*3, x=x*3))

    
    def check_group(self, group: np.ndarray, offset: Pos) -> None:
        for i in range(self.field.max_value):
            pos_to_put_num = np.argwhere(group[:, :, i])
            if len(pos_to_put_num) == 1:
                pos = Pos(*pos_to_put_num[0]) + offset
                num = i + 1
                # logger.info(f"Finded that {num= } can only be plased on {pos= }")
                yield num, pos

        
    def solve(self):
        filled = 0
        for loop in count():
            new_filled = len(np.argwhere(self.field.field))
            if new_filled - filled == 0:
                break
            filled = new_filled

            # logger.info(f"{loop= }, solved {filled / self.size**2 *100:0.2f}%")

            try:
                for num, pos in chain(self.find(), self.find_digits()):
                    self.field.add(num, pos)
                    self.add(num, pos)
            except Solved:
                return self.field
        return self.do_reqursion()
    
    def do_reqursion(self):
        sums = np.sum(self.variants, axis=2)
        min_n = np.min(np.where(sums>0, sums, self.size+1))
        if min_n == self.size+1:
            return
        min_pos = Pos(*np.argwhere(sums==min_n)[0])
        for i in self.num_on_pos(min_pos):
            s = deepcopy(self)
            s.field.add(i, min_pos)
            s.add(i, min_pos)
            res = s.solve()
            if res is not None:
                return res


def solve(name):
    f = Field()
    f.from_file(name)
    # print(f)

    s = Solver(f)

    # now = perf_counter()
    res = s.solve()
    # print(f"elapsed: {perf_counter() - now}")
    # print(res)
    return res


@logger.catch
def test_all():
    test_dir = 'test_tables'
    for table in os.listdir(test_dir):
        if not table.endswith('.csv'):
            continue

        full_path = os.path.join(test_dir, table)
        logger.info(f"Solving {table}")
        now = perf_counter()
        res = solve(full_path)
        try:
            res.check()
        except Solved:
            logger.success(f"All done! elapsed {perf_counter() - now}")
        else:
            logger.error(f"Can`t solve. elapsed {perf_counter() - now}")

@logger.catch
def main():
    name = "table_test_evil.csv"
    # name = "table_test1.csv"
    
    f = Field()
    f.from_file(name)
    print(f)

    s = Solver(f)

    now = perf_counter()
    res = s.solve()
    print(f"elapsed: {perf_counter() - now}")
    print(res)

if __name__ == "__main__":
    test_all()
