from typing import Tuple
from bs4 import BeautifulSoup


def open_table(name='table.html') -> Tuple[int, Tuple[int, int]]:
    with open(name, 'r') as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    table = soup.find_all("td")

    for cell in table:
        inp = cell.findChildren()[0]
        if 'value' in inp.attrs:
            pos = tuple(map(int, inp.attrs['id'][1:]))
            num = int(inp.attrs['value'])
            yield num, pos


import cv2
from table_ocr import extract_tables, extract_cells, ocr_image

images = ["images/test2.png", "images/test1.jpg"]
tables = extract_tables.main(images)
for inp, table_on_image in tables:
    for t in table_on_image:
        cells = extract_cells.main(t)
# ocr_image.main(cells)

