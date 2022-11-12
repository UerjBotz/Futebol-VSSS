import cv2
import numpy as np
from pyserialF import serialStart, serialRotate, serialClose #############################

Serial = serialStart('COM5',115200)  ###########################

cap = cv2.VideoCapture(0) # Camera (alterar numero caso camera esteja em outro valor)
fonte = cv2.FONT_HERSHEY_SIMPLEX
largura_tela = int(cap.get(3))
altura_tela  = int(cap.get(4))
bola_min  = np.array([ 0, 50, 50]) 
bola_max  = np.array([16,255,255])
girar = False

while True: # Loop de repetição para ret e frame do vídeo
    ret, frame = cap.read() # alterar "tela" para "frame" e utilizar a linha de baixo caso necessário diminuir a resolução da imagem
    tela = cv2.resize(frame,(0,0),fx=1,fy=1)
    # Extrair a região de interesse:
    '''roi =  frame[x:x+?,y:y+?] # neste caso foi utilizada toda a imagem, mas pode ser alterado'''

    #1 Detecção dos jogadores e bola
    hsv = cv2.cvtColor(tela, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)

    mascara_bola    = cv2.inRange(hsv, bola_min,bola_max)
    _, mascara_bola   = cv2.threshold(mascara_bola, 254, 255, cv2.THRESH_BINARY)
    contornos_bola, _ = cv2.findContours(mascara_bola, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contornos_bola:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)

        if area > 100: # ver se usar a tolerância

            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            x_bola, y_bola, w_bola, h_bola = cv2.boundingRect(cnt)
            cv2.rectangle(tela, (x_bola, y_bola), (x_bola + w_bola, y_bola + h_bola), (0, 255, 0), 0)
            tela = cv2.putText(tela,str("bola"),(x_bola+40,y_bola-15),fonte,0.8,(255,255,0),2,cv2.LINE_AA)
            girar = True
            serialRotate(Serial,girar)

        else:
            girar = False
            serialRotate(Serial,girar)

    cv2.imshow("tela", tela) #Exibe a filmagem("tela") do vídeo
    if cv2.waitKey(25) == ord('q'): break #tempo de exibição infinito (0) ou até se apertar a tecla q

cap.release()
cv2.destroyAllWindows()
serialClose(Serial)