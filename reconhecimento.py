from constantes import faixa

from cv2 import threshold, inRange, findContours, imshow #type: ignore
from cv2 import THRESH_BINARY, RETR_TREE, CHAIN_APPROX_SIMPLE #type: ignore

from dataclasses import dataclass

@dataclass(slots=True)
class objeto_movel : #não usada
    x: int = 0; y: int = 0
    w: int = 0; h: int = 0
    dx:int = 0; dy:int = 0;

def achar_contornos (tela, cor: faixa, *, janela_debug: str = "") : #TODO: parametrizar constantes cv2.etc)
    _, mascara = threshold(inRange(tela, cor.MIN, cor.MAX), 254, 255, THRESH_BINARY) # oqq são esses 254, 255? #ver magic numbers
    contornos, _ = findContours(mascara, RETR_TREE, CHAIN_APPROX_SIMPLE) 

    if len(janela_debug): #TODO: ver se fazer assim mesmo
        imshow(janela_debug, mascara) #Exibe um janela com a máscara
    return contornos