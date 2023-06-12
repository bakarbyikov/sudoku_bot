from dataclasses import dataclass


@dataclass(frozen=True, slots=True, )
class Pos:
    y: int
    x: int

    def __add__(self, value: 'Pos') -> 'Pos':
        return Pos(y=self.y+value.y, x=self.x+value.x,)