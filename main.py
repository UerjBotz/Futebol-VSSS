import comunicação as transmissor
from receptor import Client

visão = Client()
deve_parar = False
while not (deve_parar):
  try:
    posições = visão.receive_frame()
    print(posições)

  except KeyboardInterrupt:
    deve_parar = True

transmissor.finalizar()
