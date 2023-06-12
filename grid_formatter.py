import numpy as np
from tabulate import tabulate

def make_board_formatter():
    bar = '-------------\n'
    lnf = '|' +('{:}'*3 + '|')*3 + '\n'
    bft = bar + (lnf*3+bar)*3
    return (lambda bd:bft.format(*(el for rw in bd for el in rw)))

formater = make_board_formatter()

def format_grid(grid: np.ndarray) -> str:
    return formater(grid)

# def format_cell(cell: np.ndarray) -> str:
#     return '\n'.join(''.join(map(str, row)) for row in cell) 

# def format_grid(grid: np.ndarray) -> str:
#     h, w = grid.shape
#     cells_count = h//3, w//3

#     cells = list()
#     for y, row_of_cells in enumerate(np.vsplit(grid, cells_count[0])):
#         cells.append(list())
#         for x, cell in enumerate(np.hsplit(row_of_cells, cells_count[1])):
#             cells[-1].append(format_cell(cell))
    
#     return tabulate(cells, tablefmt="fancy_grid", ='left')
            
if __name__ == "__main__":
    grid = np.random.randint(0, 10, (9, 9))
    print(format_grid(grid))
    print(format_grid(grid).replace(' ', ''))

