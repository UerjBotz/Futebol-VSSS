clamp = lambda v, m, M: max(m, min(v, M))
vec2i = tuple[int, int]

def atacar(): pass

def seguir_a_bola(pos_bola: vec2i, pos_defensor: vec2i, *, entrar_area: bool) -> vec2i:
  if not entrar_area:
    x_bola, y_bola = pos_bola
    if y_bola in range(0, 300) or y_bola in range(1300-300, 1300):
      return (clamp(x_bola, 250, 1700-250), y_bola)
  return pos_bola

def defender(pos_bola: vec2i, pos_defensor: vec2i) -> vec2i:
  x_bola, y_bola = pos_bola
  if x_bola >= 650:
    return (pos_defensor[0], y_bola)
  else:
    return seguir_a_bola(pos_bola, pos_defensor, entrar_area = False)

def guardar_gol(pos_bola: vec2i, pos_goleiro: vec2i) -> vec2i:
  pos = (pos_goleiro[0], pos_bola[1])
  return pos[0], clamp(pos[1], 300, 1300-300)

#def penalti_goleiro(pos_bola: vec2i, pos_goleiro: vec2i):
#  pos = (pos_goleiro[0], pos_bola[1])
#  return pos[0], clamp(pos[1], 300, 1300-300)

def parado(): 
  return (0,0)

def bola_livre(): pass
