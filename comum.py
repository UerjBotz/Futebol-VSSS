from typing_extensions import TypeIs


## funções utilitárias
def clamp[Num](val: Num, MIN: Num, MAX: Num) -> Num:
    return min(MAX, max(MIN, val))
constrain = clamp

def dist[Num](a: tuple[Num,Num], b: tuple[Num,Num]) -> Num:
    x0, y0 = a; x1, y1 = b
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

def none(obj: object | None) -> TypeIs[None]:
    return obj is None
def some(obj: object | None) -> TypeIs[object]: #! bool? ver abaixo
    return not none(obj) #! checar se ainda inclui None (pq object)

