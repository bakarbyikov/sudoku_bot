from typing import List, Tuple
from itertools import product
from tabulate import tabulate
import numpy as np

from cather import open_table

class Field:

    def __init__(self, size = 9) -> None:
        self.size = size
        self.field = np.full((size, size, size), True)
        self.filled = set()
    
    def add(self, num: int, pos: Tuple[int, int]) -> None:
        self.filled.add(pos)
        x, y = pos

        self.field[pos] = False

        self.field[:, y, num-1] = False
        self.field[x, :, num-1] = False

        c_x, c_y = x//3*3, y//3*3
        self.field[c_x:c_x+3, c_y:c_y+3, num-1] = False

        self.field[x, y, num-1] = True
    
    def num_in_pos(self, x: int, y: int):
        return self.field[x, y].nonzero()[0][0] + 1

    
    def find(self):
        sums = self.field.sum(2)
        for x, y in product(range(self.size), repeat=2):
            if (x, y) in self.filled:
                continue
            if sums[x, y] == 1:
                num = self.num_in_pos(x, y)
                self.add(num, (x, y))
                print(f"No more numbers on {pos=}, so i put {num}")

    
    def check_group(self, cells: List[Tuple[int, int]]):
        for i in range(self.size):
            v = sum(self.field[x, y, i] for x, y in cells)
            if v == 1:
                for x, y in cells:
                    if self.field[x, y, i]:
                        yield (x, y), i+1
                        break

    
    def find_digits(self):
        targets = list()

        for i in range(self.size):
            row = [(i, j) for j in range(self.size)]
            column = [(j, i) for j in range(self.size)]
            targets.append(row)
            targets.append(column)
        
        for x, y in product(range(0, self.size, 3), repeat=2):
            cell = []
            for o_x, o_y in product(range(3), repeat=2):
                cell.append((x+o_x, y+o_y))
            targets.append(cell)
            


        for t in targets:
            for pos, num in self.check_group(t):
                if pos in self.filled:
                    continue
                print(f"I sure we can put {num} to {pos=}")
                self.add(num, pos)



    def __str__(self) -> str:
        to_print = np.full((self.size, self.size), ' ')
        for x, y in product(range(self.size), repeat=2):
            if (x, y) in self.filled:
                to_print[x, y] = self.num_in_pos(x, y)


        return str(tabulate(to_print, tablefmt="fancy_grid"))


if __name__ == "__main__":
    f = Field()

    for num, pos in open_table():
        f.add(num, pos)
    for i in range(4):
        print(f)
        print(f'attempt {i}, filled: {len(f.filled)}')
        
        f.find_digits()
        # f.find()
