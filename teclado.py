import termios, select, sys, tty
import atexit

from queue import Queue

ESC       = '\x1b'
BACKSPACE = '\x7f'

fila = Queue[str]()

# adaptado de https://stackoverflow.com/a/10079805
def ler_para_sempre(fila_teclado=fila): #! não deve funcionar no windows
    conf_term_antiga = termios.tcgetattr(sys.stdin)

    @atexit.register
    def resetar_terminal():
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, conf_term_antiga)

    try:
      tty.setcbreak(sys.stdin.fileno())
      while True:
          if select.select([sys.stdin], [], [], 0) != \
                          ([sys.stdin], [], []): continue
          fila_teclado.put(sys.stdin.read(1))
          #! lidar com sequências iniciadas por ESC (ex: setas, del)*

    finally: resetar_terminal()

#!* esboço:
# def gera_sempre:
#     ...
#     while True:
#         if ... select ...: yield None
#         yield sys.stdin.read(1)
#     ...
# def ler_pra_sempre:
#     seq = False
#     for t in gera_sempre():
#       if t == ESC:
#           esc = True
#       elif some(t):
#           if seq:
#               t = ESC + t
#               seq = False
#           fila.put(t)
#       elif seq:
#           fila.put(ESC)
#           seq = False

