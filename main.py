import comunicação as transmissor
from receptor import Client

from google.protobuf.json_format import MessageToDict

N_ROBÔS = 3

visão = Client()
deve_parar = False

#transmissor.enviar([1000, 1000, 1000, 1000, 1000, 1000])
#exit()

info_campo = MessageToDict(visão.receive_frame().geometry)
robôs_amarelos = robôs_azuis = [{"robot_id": 0, "x": 0, "y": 0}]
while not (deve_parar):
  try:
    posições = MessageToDict(visão.receive_frame().detection)
    #print(posições)
    robôs_amarelos = posições['robotsYellow'] if 'robotsYellow' in posições else robôs_amarelos
    robôs_azuis = posições['robotsBlue'] if 'robotsBlue' in posições else robôs_azuis

    for robô in robôs_amarelos:
      print(f"amarelo: {robô['x']}, {robô['y']}")
    for robô in robôs_azuis:
      print(f"azul: {robô['x']}, {robô['y']}")

    #transmissor.enviar([1000, 1000, 1000, 1000, 1000, 1000])
    #transmissor.mover(vel_max, vel_max, robo=0)

  except KeyboardInterrupt:
    deve_parar = True

transmissor.finalizar()
