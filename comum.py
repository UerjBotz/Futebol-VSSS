from typing import Final
from typing_extensions import TypeIs

from threading import Event

import numpy as np
from   numpy.typing import NDArray


## constantes
largura_campo: Final[int] = 1700 #mm
altura_campo:  Final[int] = 1300 #mm
largura_gol:   Final[int] = 100  #mm
altura_gol:    Final[int] = 400  #mm

VEL_MAX: Final[int] = 100 #%
N_ROBÔS: Final[int] = 3

DIST_BLOCO:   Final[int]   = 100 #mm
FATOR_MATRIZ: Final[float] = 1/DIST_BLOCO


## funções utilitárias
def clamp[Num](val: Num, MIN: Num, MAX: Num) -> Num:
    return min(MAX, max(MIN, val))

def dist[Num](a: tuple[Num,Num], b: tuple[Num,Num]) -> float:
    x0, y0 = a; x1, y1 = b
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

def none(obj: object | None) -> TypeIs[None]:
    return obj is None
def some(obj: object | None) -> TypeIs[object]: #! bool? ver abaixo
    return not none(obj) #! checar se ainda inclui None (pq object)

def complex_to_tuple(pos: complex) -> tuple:
    return pos.real, pos.imag

def complex_to_xy(cp: complex):
    return np.array([cp.real, cp.imag], np.int32)

def xy_to_complex(points: NDArray): #! tipos
    if len(points) <= 0: return np.array([])
    return points @ np.array([[1], [1j]])[:, 0]


## classes utilitárias
class Evento(Event):
    __call__ = Event.is_set

