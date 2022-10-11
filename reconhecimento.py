import cv2
import numpy as np
import math

time = 0 # 0 para time azul, 1 para time amarelo
cap = cv2.VideoCapture(1) # Camera

font = cv2.FONT_HERSHEY_SIMPLEX
width = int(cap.get(3))
height = int(cap.get(4))
# print(width,height)

deteccoes = np.array([])
lower_blue = np.array([100, 50,50])# array da cor mais clara time azul (alterar para a cor utilizada no robo físico)
upper_blue = np.array([150, 255, 255])# array da cor mais escura time azul (alterar para a cor utilizada no robo físico)
lower_yellow = np.array([26, 50,50])# array da cor mais clara time amarelo (alterar para a cor utilizada no robo físico)
upper_yellow = np.array([46, 255, 255])# array da cor mais escura time amarelo (alterar para a cor utilizada no robo físico)
lower_teamColor = np.array([164, 50,50])# array da cor mais clara do membro do time
upper_teamColor = np.array([174, 255, 255])# array da cor mais escura do membro do time
lower_ball = np.array([0, 50,50])
upper_ball = np.array([16,255,255])
lower_green = np.array([80,50,50])
upper_green = np.array([90,255,255])

#thresholds:
distancia = 200 # em milimetros
areaAzul = 18000*(100**2)/(distancia**2) # formula(d) = (areapixelsmedida*distanciamedida^2)/(d)^2
areaRosa = areaAzul*(280/1200) # multiplica a azul pela proporção entre os retângulos pra achar a rosa
areaRobo = areaAzul*(7412/1200) #multiplica a azul pela proporção entre os retângulos pra achar o robo inteiro
tamanhoAumentar = int((areaRobo**(1/2))/2)
tolerancia = 50/100

# vetor direção
normalx = np.array([width,height]) ; normaly = np.array([0,0])
direcao1x = np.array([0,0]) ; direcao1y = np.array([0,0])
direcao1x = np.clip(direcao1x,0,height) ; direcao1y = np.clip(direcao1x,0,height)

#print(tamanhoAumentar)
if time == 0:
    lower_color = lower_blue ; lower_enemy = lower_yellow
    upper_color = upper_blue ; upper_enemy = upper_yellow
else:
    lower_color = lower_yellow ; lower_enemy = lower_blue
    upper_color = upper_yellow ; upper_enemy = upper_blue

while True:# Loop de repetição para ret e frame do vídeo
    ret, frame = cap.read() # alterar "roi" para "frame" e utilizar a linha de baixo caso necessário diminuir a resolução da imagem
    roi = cv2.resize(frame,(0,0),fx=1,fy=1)

    # Extrair a região de interesse:
    '''roi =  frame[x:x+?,y:y+?] # neste caso foi utilizada toda a imagem, mas pode ser alterado'''
    
    #1 Detecção dos membros da equipe:
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
    mask = cv2.inRange(hsv, lower_color, upper_color) # máscara para detecção de um objeto
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contornos, _ =  cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    maskBall = cv2.inRange(hsv,lower_ball,upper_ball)
    maskEnemy = cv2.inRange(hsv,lower_enemy,upper_enemy)
    testando, maskBall = cv2.threshold(maskBall, 254, 255, cv2.THRESH_BINARY)
    testando2, maskEnemy = cv2.threshold(maskEnemy, 254, 255, cv2.THRESH_BINARY)
    contornoBall, testando =  cv2.findContours(maskBall, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contornosEnemy, testando2 =  cv2.findContours(maskEnemy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    maskDir = cv2.inRange(hsv,lower_green,upper_green)
    testando3, maskDir = cv2.threshold(maskDir, 254, 255, cv2.THRESH_BINARY)
    contornoDir, testando3 =  cv2.findContours(maskDir, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    bola = [0,0,0,0]

    for cnt in contornoBall:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)

        if area > 100:

            cv2.drawContours(roi, [cnt], -1, (0, 255, 0),0)
            xbola, ybola, wbola, hbola = cv2.boundingRect(cnt)
            bola[0] = xbola ; bola[1] = ybola ; bola[2] = wbola ; bola[3] = hbola
            #cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
            cv2.rectangle(roi, (xbola, ybola), (xbola + wbola, ybola + hbola), (0, 255, 0), 0)
            np.append(deteccoes,[xbola,ybola,wbola,hbola])
            roi = cv2.putText(roi,str("ball"),(xbola+40,ybola-15),font,0.8,(255,255,0),2,cv2.LINE_AA)
    #print(bola)

    for cnt in contornos:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        if(areaAzul*(1-tolerancia) <= area <= areaAzul*(1+tolerancia)):

            #print(area) #debug

            cv2.drawContours(roi, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            #cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
            cv2.rectangle(roi, (x, y), (x + w, y + h), (255, 0, 0), 0)
            np.append(deteccoes,[x,y,w,h])

            hsvNum = hsv[max(y-tamanhoAumentar,0) : min(y+h+tamanhoAumentar,height),  max(x-tamanhoAumentar,0): min(x+w+tamanhoAumentar,width)] #clampa
            '''if len(usada) == 0 or len(usada[0]) == 0: # resolvendo bugs de gravação
                break'''

            # detecção do num no time
            #cv2.imshow("usada",hsv)#Exibe a filmagem("ROI") do vídeo
            #hsvNum = cv2.cvtColor(usada, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
            maskNum = cv2.inRange(hsvNum, lower_teamColor, upper_teamColor) # máscara para detecção de um objeto
            Num, maskNum = cv2.threshold(maskNum, 254, 255, cv2.THRESH_BINARY)
            contornosNum, Num =  cv2.findContours(maskNum, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            numeroNoTime = 0
            maskDir = cv2.inRange(hsv,lower_green,upper_green)
            testando3, maskDir = cv2.threshold(maskDir, 254, 255, cv2.THRESH_BINARY)
            contornoDir, testando3 =  cv2.findContours(maskDir, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for cntNum in contornosNum:
                areaNum = cv2.contourArea(cntNum)
                if(areaRosa*(1-tolerancia) <= areaNum <= areaRosa*(1+tolerancia)):
                    cv2.drawContours(roi, [cntNum], -1, (255, 255, 255),0)
                    xnum, ynum, wnum, hnum = cv2.boundingRect(cntNum)
                    #cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
                    cv2.rectangle(roi, (xnum, ynum), (xnum + wnum, ynum + hnum), (0, 0, 255), 3)
                    numeroNoTime += 1
            for cnt in contornoDir:
                #Cálculo da área e remoção de elementos pequenos
                area = cv2.contourArea(cnt)

                if area > 50:
                    cv2.drawContours(roi, [cnt], -1, (0, 255, 0),0)
                    xDir, yDir, wDir, hDir = cv2.boundingRect(cnt)
                    #cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
                    cv2.rectangle(roi, (xDir, yDir), (xDir + wDir, yDir + hDir), (0, 0, 0), 0)
                    np.append(deteccoes,[xDir,yDir,wDir,hDir])
                    roi = cv2.putText(roi,str("Dir"),(xDir+40,yDir-15),font,0.8,(255,0,255),2,cv2.LINE_AA)
                    direcao1x  = [(x+w//2),(y+h//2)] ; direcao1y = [(bola[0]+bola[2]//2),(bola[1]+bola[3]//2)]
                    #roi = cv2.arrowedLine(roi,direcao1x,direcao1y,[255,255,255],5)
                    if y > yDir:
                        print("left")
                    elif y < yDir:
                        print("right")
                
            roi = cv2.putText(roi,str(numeroNoTime+1),(x+40,y-15),font,0.8,(255,255,255),2,cv2.LINE_AA)

    for cnt in contornosEnemy:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        
        if area > 100:

            cv2.drawContours(roi, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            #cv2.rectangle(roi, (x,y), (x +w, y +h), (0, 255, 0), 3)
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 255), 0)
            np.append(deteccoes,[x,y,w,h])
            roi = cv2.putText(roi,str("enemy"),(x+40,y-15),font,0.8,(0,0,255),2,cv2.LINE_AA)

    'print(deteccoes)'
    cv2.imshow("Mask", mask)#Exibe a máscara("Mask") do vídeo
    cv2.imshow("ROI",roi)#Exibe a filmagem("ROI") do vídeo
    #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
    if cv2.waitKey(25) == ord('q'):#tempo de exibição infinito (0) ou até se apertar a tecla q
        break
cap.release()
cv2.destroyAllWindows()
