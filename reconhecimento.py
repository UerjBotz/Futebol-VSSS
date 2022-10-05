# CODIGO DE RECONHECIMENTO DAS CORES, NECESSÁRIO ADICIONAR A COR AMARELA, ASSIM COMO DECIDIR QUAIS CORES UTILIZAR IDENTIFICAR CADA MEMBRO DA EQUIPE.
import cv2
import numpy as np

font = cv2.FONT_HERSHEY_SIMPLEX
cap = cv2.VideoCapture(0) # Camera

width = int(cap.get(3))
height = int(cap.get(4))
print(width,height)

deteccoes = np.array([])
lower_green = np.array([116, 50,50])# array da cor mais clara
upper_green = np.array([126, 255, 255])# array da cor mais escura
lower_greenNum = np.array([164, 50,50])# array da cor mais clara
upper_greenNum = np.array([174, 255, 255])# array da cor mais escura

while True:# Loop de repetição para ret e frame do vídeo
    ret, frame = cap.read()
    roi = cv2.resize(frame,(0,0),fx=1,fy=1)
    # Extrair a região de interesse:
    '''roi =  frame # neste caso foi utilizada toda a imagem, mas pode ser alterado'''
    
    #1 Detecção do Objeto:
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
    mask = cv2.inRange(hsv, lower_green, upper_green) # máscara para detecção de um objeto
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    result = cv2.bitwise_and(roi, roi, mask=mask)
    contornos, _ =  cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contornos:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        if(area > 700):
            cv2.drawContours(roi, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            #cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
            cv2.rectangle(roi, (x, y), (x + w, y + h), (255, 0, 0), 0)
            np.append(deteccoes,[x,y,w,h])
            usada =  roi[y-80: y+h+80,  x-80: x+w+80]
            #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
            if len(usada) == 0 or len(usada[0]) == 0: # resolvendo bugs de gravação
                break
            # detecção do num no time

            try:
                hsvNum = cv2.cvtColor(usada, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
            except OSError:
                print("error")
            else:
                maskNum = cv2.inRange(hsvNum, lower_greenNum, upper_greenNum) # máscara para detecção de um objeto
                Num, maskNum = cv2.threshold(maskNum, 254, 255, cv2.THRESH_BINARY)
                resultNum = cv2.bitwise_and(usada, usada, mask=maskNum)
                contornosNum, Num =  cv2.findContours(maskNum, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                numeroNoTime = 0
                for cntNum in contornosNum:
                    areaNum = cv2.contourArea(cntNum)
                    if(areaNum > 750):
                        cv2.drawContours(usada, [cntNum], -1, (255, 255, 255),0)
                        xnum, ynum, wnum, hnum = cv2.boundingRect(cntNum)
                        #cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
                        cv2.rectangle(usada, (xnum, ynum), (xnum + wnum, ynum + hnum), (0, 0, 255), 3)
                        numeroNoTime += 1
                roi = cv2.putText(roi,str(numeroNoTime+1),(x+40,y-15),font,0.8,(0,0,0),2,cv2.LINE_AA)
                    

    'print(deteccoes)'
    #cv2.imshow("Mask", mask)#Exibe a máscara("Mask") do vídeo
    cv2.imshow("ROI",roi)#Exibe a filmagem("ROI") do vídeo
    #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
    if cv2.waitKey(25) == ord('q'):#tempo de exibição infinito (0) ou até se apertar a tecla q
        break
cap.release()
cv2.destroyAllWindows()
