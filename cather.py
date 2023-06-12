import base64
import csv
from itertools import chain
import os
from re import L
import sys
from time import perf_counter
from typing import Tuple

import cv2
import numpy as np
from table_ocr.extract_cells import extract_cell_images_from_table
from table_ocr.extract_tables import find_tables
from table_ocr.ocr_image import crop_to_text, ocr_image
from tabulate import tabulate

from pos import Pos
from exceptions import CantRecogniseImage
from grid_formatter import format_grid
from field import Field


def open_table(name='table_test1.csv') -> Tuple[int, Pos]:
    with open(name, 'r') as f:
        reader = csv.reader(f)
        size = reader.line_num
        table = np.full((size, size), 0)
        for y, row in enumerate(reader):
            for x, s in enumerate(row):
                if s.isdigit():
                    assert len(s) == 1
                    num = int(s)
                    yield num, Pos(y, x)

def tess_config() -> str:
    d = os.path.dirname(sys.modules["table_ocr"].__file__)
    tessdata_dir = os.path.join(d, "tessdata")
    tess_args = ["--psm", "7", "-l", "table-ocr", "--tessdata-dir", tessdata_dir]

    return " ".join(tess_args)

def process_image(image_bytes: bytes) -> np.ndarray:
    image_np = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_np, flags=1)

    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    tables = find_tables(image_gray)
    if len(tables) != 1:
        raise CantRecogniseImage(f'Too much tables on image: {len(tables)}')
    rows = extract_cell_images_from_table(tables[0])

    # for y, row in enumerate(rows[:3]):
    #     for x, cell in enumerate(row):
    #         cv2.imshow(f"{x, y = }", cell)
    
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    height = len(rows)
    rows_width = [len(i) for i in rows]
    for width in rows_width:
        if width != height:
            raise CantRecogniseImage(f'Row too short {height = }, {width = }, {rows_width = }')

    config = tess_config()

    f = Field()

    result = np.zeros((height, height), dtype=np.uint8)
    for y, row in enumerate(rows):
        for x, cell in enumerate(row):
            if not is_empty(cell):
                croped = crop_to_text(cell)
                text = ocr_image(cell, config).strip()

                assert len(text) == 1
                f.add(int(text), Pos(y, x))
                # result[y, x] = int(text)
    
    return f
    # return str(result)[1:-1]
    return format_grid(result)


def is_empty(cell: np.ndarray) -> bool:
    BOUND = 0.999

    h, w = cell.shape
    _, cell_thresholded = cv2.threshold(cell, 127, 255, cv2.THRESH_BINARY)

    pixels_filled = cv2.countNonZero(cell_thresholded)
    filled_percent = pixels_filled / w / h
    return filled_percent >= BOUND



if __name__ == "__main__":
    name = 'images/test4.jpg'
    with open(name, 'rb') as f:
        now = perf_counter()
        table = process_image(f.read())
        elapsed = perf_counter() - now
    print(table)
    print(f'{elapsed = }')
    






def get_table_from_image(image):
    import os

    from table_ocr import extract_cells, extract_tables, ocr_image, ocr_to_csv

    # images = ["images/test2.png", "images/test1.jpg"]
    images = ['images/test3.png', ]
    tables = extract_tables.main(images)
    for inp, table_on_image in tables:
        for t in table_on_image:
            cells = extract_cells.main(t)
            files = list()
            for c in cells:
                files.append(ocr_image.main(c, None))
            csv_table = ocr_to_csv.main(files)
            csv_table = csv_table.replace('F', ' ')
            print(csv_table)
            _, name = os.path.split(inp)
            name, _, _ = name.rpartition('.')
            with open(f'images/table_{name}.csv', 'w') as f:
                f.write(csv_table)

