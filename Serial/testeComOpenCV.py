import cv2
import numpy as np
from pyserialF import serialStart, serialBlink, serialClose

Serial = serialStart('COM5',9600)

time = 0 # 0 para time azul, 1 para time amarelo
cap = cv2.VideoCapture(0) # Camera

font = cv2.FONT_HERSHEY_SIMPLEX
width = int(cap.get(3))
height = int(cap.get(4))
# print(width,height)

deteccoes = np.array([])
lower_blue = np.array([100, 50,50])# array da cor mais clara time azul (alterar para a cor utilizada no robo físico)
upper_blue = np.array([150, 255, 255])# array da cor mais escura time azul (alterar para a cor utilizada no robo físico)
lower_yellow = np.array([10, 50,50])# array da cor mais clara time amarelo (alterar para a cor utilizada no robo físico)
upper_yellow = np.array([46, 255, 255])# array da cor mais escura time amarelo (alterar para a cor utilizada no robo físico)
lower_teamColor = np.array([164, 50,50])# array da cor mais clara do membro do time
upper_teamColor = np.array([174, 255, 255])# array da cor mais escura do membro do time

#thresholds:
distancia = 500 # em milimetros
areaAzul = 18000*(100**2)/(distancia**2) # formula(d) = (areapixelsmedida*distanciamedida^2)/(d)^2
areaRosa = areaAzul*(280/1200) # multiplica a azul pela proporção entre os retângulos pra achar a rosa
areaRobo = areaAzul*(7412/1200) #multiplica a azul pela proporção entre os retângulos pra achar o robo inteiro
tamanhoAumentar = int((areaRobo**(1/2))/2)
tolerancia = 50/100

print(tamanhoAumentar)
if time == 0:
    lower_color = lower_blue
    upper_color = upper_blue
else:
    lower_color = lower_yellow
    upper_color = upper_yellow

while True:# Loop de repetição para ret e frame do vídeo
    ret, frame = cap.read() # alterar "roi" para "frame" e utilizar a linha de baixo caso necessário diminuir a resolução da imagem
    roi = cv2.resize(frame,(0,0),fx=1,fy=1)

    # Extrair a região de interesse:
    '''roi =  frame[x:x+?,y:y+?] # neste caso foi utilizada toda a imagem, mas pode ser alterado'''
    
    #1 Detecção dos membros da equipe:
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
    mask = cv2.inRange(hsv, lower_color, upper_color) # máscara para detecção de um objeto
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    result = cv2.bitwise_and(roi, roi, mask=mask)
    cv2.imshow("usada",result)#Exibe a filmagem("ROI") do vídeo
    contornos, _ =  cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contornos) == 0:
        serialBlink(Serial,"B")
    for cnt in contornos:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        cv2.drawContours(roi, [cnt], -1, (0, 255, 0),0)
        if( area > 1):

            #print(area) #debug
            serialBlink(Serial,"A")
            cv2.drawContours(roi, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
            cv2.rectangle(roi, (x, y), (x + w, y + h), (255, 0, 0), 0)
            np.append(deteccoes,[x,y,w,h])

            usada = roi[max(y-tamanhoAumentar,0) : min(y+h+tamanhoAumentar,height),  max(x-tamanhoAumentar,0): min(x+w+tamanhoAumentar,width)] #clampa
            if len(usada) == 0 or len(usada[0]) == 0: # resolvendo bugs de gravação
                break

            # detecção do num no time
            #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
            hsvNum = cv2.cvtColor(usada, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
            maskNum = cv2.inRange(hsvNum, lower_teamColor, upper_teamColor) # máscara para detecção de um objeto
            Num, maskNum = cv2.threshold(maskNum, 254, 255, cv2.THRESH_BINARY)
            resultNum = cv2.bitwise_and(usada, usada, mask=maskNum)
            contornosNum, Num =  cv2.findContours(maskNum, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            numeroNoTime = 0
            for cntNum in contornosNum:
                areaNum = cv2.contourArea(cntNum)
                if(areaRosa*(1-tolerancia) <= areaNum <= areaRosa*(1+tolerancia)):
                    cv2.drawContours(usada, [cntNum], -1, (255, 255, 255),0)
                    xnum, ynum, wnum, hnum = cv2.boundingRect(cntNum)
                    #cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
                    cv2.rectangle(usada, (xnum, ynum), (xnum + wnum, ynum + hnum), (0, 0, 255), 3)
                    numeroNoTime += 1
            roi = cv2.putText(roi,str(numeroNoTime+1),(x+40,y-15),font,0.8,(255,255,255),2,cv2.LINE_AA)
        else:
            serialBlink(Serial,"B")
            break            

    'print(deteccoes)'
    cv2.imshow("Mask", mask)#Exibe a máscara("Mask") do vídeo
    cv2.imshow("ROI",roi)#Exibe a filmagem("ROI") do vídeo
    #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
    if cv2.waitKey(25) == ord('q'):#tempo de exibição infinito (0) ou até se apertar a tecla q
        break
cap.release()
cv2.destroyAllWindows()
serialClose(Serial)
