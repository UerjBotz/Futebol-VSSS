import cv2
import numpy as np

'''
TODO:
- deletar detecções e integrar o teste grade
- passar pelo centro pro astar
- tirar os ifs e deixar só o vetor que a gente descobriu como achar
'''

time = 0 # 0 para time azul, 1 para time amarelo
cap = cv2.VideoCapture(0) # Camera (alterar numero caso camera esteja em outro valor)

font = cv2.FONT_HERSHEY_SIMPLEX
width = int(cap.get(3))
height = int(cap.get(4))
print(width//10,height//10)
blank = np.zeros((400,400))
#direction = 0
firstlinedetect = False #debug

deteccoes = np.array([])
lower_blue = np.array([100, 80, 80])# array da cor mais clara time azul (alterar para a cor utilizada no robo físico)
upper_blue = np.array([110,255,255])# array da cor mais escura time azul (alterar para a cor utilizada no robo físico)
lower_yellow = np.array([26, 50, 50])# array da cor mais clara time amarelo (alterar para a cor utilizada no robo físico)
upper_yellow = np.array([46,255,255])# array da cor mais escura time amarelo (alterar para a cor utilizada no robo físico)
lower_teamColor = np.array([110, 50, 50])# array da cor mais clara do membro do time
upper_teamColor = np.array([180,255,255])# array da cor mais escura do membro do time
lower_ball = np.array([0, 50,50])
upper_ball = np.array([16,255,255])
lower_green = np.array([80,50,50])
upper_green = np.array([90,255,255])

# menu interativo
def nothing(x): pass

cv2.namedWindow("blank") # alterar primeiro valor que aparece para atualizar valores encontrados nas mascaras
cv2.createTrackbar("lowerBlue","blank",102,120,nothing) ; cv2.createTrackbar("upperBlue","blank",110,120,nothing)
cv2.createTrackbar("lowerYellow","blank",24,40,nothing) ; cv2.createTrackbar("upperYellow","blank",34,40,nothing)
cv2.createTrackbar("lowerBall","blank",10,30,nothing) ; cv2.createTrackbar("upperBall","blank",20,30,nothing)
cv2.createTrackbar("lowerTeam","blank",10,180,nothing) ; cv2.createTrackbar("upperTeam","blank",18,180,nothing)
cv2.createTrackbar("lowerGreen","blank",80,100,nothing) ; cv2.createTrackbar("upperGreen","blank",90,100,nothing) 

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
    ret, frame = cap.read() # alterar "tela" para "frame" e utilizar a linha de baixo caso necessário diminuir a resolução da imagem
    tela = cv2.resize(frame,(0,0),fx=1,fy=1)
    # Extrair a região de interesse:
    '''roi =  frame[x:x+?,y:y+?] # neste caso foi utilizada toda a imagem, mas pode ser alterado'''
    
    lower_blue[0] = cv2.getTrackbarPos('lowerBlue', 'blank') ; upper_blue[0] = cv2.getTrackbarPos('upperBlue', 'blank')
    lower_yellow[0] = cv2.getTrackbarPos('lowerYellow', 'blank') ; upper_yellow[0] = cv2.getTrackbarPos('upperYellow', 'blank')
    lower_ball[0] = cv2.getTrackbarPos('lowerBall', 'blank') ; upper_ball[0] = cv2.getTrackbarPos('upperBall', 'blank')
    lower_teamColor[0] = cv2.getTrackbarPos('lowerTeam', 'blank') ; upper_teamColor[0] = cv2.getTrackbarPos('upperTeam', 'blank')
    lower_green[0] = cv2.getTrackbarPos('lowerGreen', 'blank') ; upper_green[0] = cv2.getTrackbarPos('upperGreen', 'blank')

    #1 Detecção dos membros da equipe:
    hsv = cv2.cvtColor(tela, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
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

        if area > 100: # ver se usar a tolerância
            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            xbola, ybola, wbola, hbola = cv2.boundingRect(cnt)
            bola[0] = xbola ; bola[1] = ybola ; bola[2] = wbola ; bola[3] = hbola
            #cv2.rectangle(tela, (x,y), (x +w, y +h), (0, 255, 0), 3)
            cv2.rectangle(tela, (xbola, ybola), (xbola + wbola, ybola + hbola), (0, 255, 0), 0)
            np.append(deteccoes,[xbola,ybola,wbola,hbola])
            tela = cv2.putText(tela,str("ball"),(xbola+40,ybola-15),font,0.8,(255,255,0),2,cv2.LINE_AA)

    #print(bola)

    for cnt in contornos:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        if(areaAzul*(1-tolerancia) <= area <= areaAzul*(1+tolerancia)):

            #print(area) #debug

            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            #cv2.rectangle(tela, (x,y), (x +w, y +h), (0, 255, 0), 3)
            cv2.rectangle(tela, (x, y), (x + w, y + h), (255, 0, 0), 0)
            np.append(deteccoes,[x,y,w,h])

            hsvNum = hsv[max(y-tamanhoAumentar,0) : min(y+h+tamanhoAumentar,height),  max(x-tamanhoAumentar,0): min(x+w+tamanhoAumentar,width)] #clampa
            '''if len(usada) == 0 or len(usada[0]) == 0: # resolvendo bugs de gravação
                break'''

            # detecção do num no time
            cv2.imshow("usada",hsvNum)#Exibe a filmagem("tela") do vídeo
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
                #if(areaRosa*(1-tolerancia) <= areaNum <= areaRosa*(1+tolerancia)):
                if(areaNum > 1):
                    cv2.drawContours(tela, [cntNum], -1, (255, 255, 255),0)
                    xnum, ynum, wnum, hnum = cv2.boundingRect(cntNum)
                    #cv2.rectangle(tela, (x,y), (x +w, y +h), (0, 255, 0), 3)
                    cv2.rectangle(tela, (xnum, ynum), (xnum + wnum, ynum + hnum), (0, 0, 255), 3)
                    numeroNoTime += 1
                    
            for cnt in contornoDir:
                #Cálculo da área e remoção de elementos pequenos
                area = cv2.contourArea(cnt)

                if area > 100: #ver se usar a tolerância
                    cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
                    xDir, yDir, wDir, hDir = cv2.boundingRect(cnt)
                    #cv2.rectangle(tela, (x,y), (x +w, y +h), (0, 255, 0), 3)
                    cv2.rectangle(tela, (xDir, yDir), (xDir + wDir, yDir + hDir), (0, 0, 0), 0)
                    np.append(deteccoes,[xDir,yDir,wDir,hDir])
                    tela = cv2.putText(tela,str("Dir"),(xDir+40,yDir-15),font,0.8,(255,0,255),2,cv2.LINE_AA)
                    '''direcao1x  = [(x+w//2),(y+h//2)] ; direcao1y = [(bola[0]+bola[2]//2),(bola[1]+bola[3]//2)]
                    tela = cv2.arrowedLine(tela,direcao1x,direcao1y,[255,255,255],5)'''

                    if firstlinedetect == False: #debug
                        firstLine = [(xDir+(wDir//2)),(yDir + (hDir//2)),(x+(w//2)),(y+(h//2))]
                        firstlinedetect = True
                    tela = cv2.arrowedLine(tela,(firstLine[0],firstLine[1]),(firstLine[2],firstLine[3]),(255,0,0),5)
                    line = [(xDir+(wDir//2)),(yDir + (hDir//2)),(x+(w//2)),(y+(h//2))]
                    tela = cv2.arrowedLine(tela,(line[0],line[1]),(line[2],line[3]),(255,0,0),5)


                    '''if y < (yDir - 5*y//100) and  x <= xDir <= x + w:
                        #print("left")
                        #print(bola[0])
                        if 0 < bola[0] <= x:
                            print("frente")
                        elif 0 < (x + w) <= bola[0]:
                            print("dar ré")
                        elif 0 < bola[1] <= y:
                            print("virar direita")
                        elif 0 < (y+h) <= bola[1]:
                            print("virar esquerda")

                    elif y > (yDir - 5*y//100) and (x - (20*w//100)) <= xDir <= (x + (20*w//100)):
                        #print("right")
                        if 0 < bola[0] <= x:
                            print("dar ré")
                        elif 0 < (x+w) <= bola[0]:
                            print("frente")
                        elif 0 < bola[1] <= y:
                            print("virar esquerda")
                        elif 0 < (y+h) <= bola[1]:
                            print("virar direita")
                        
                    elif x > (xDir -5*y//100) and y <= yDir <= y + h:
                        #print("up")
                        if 0 < bola[1] <= y:
                            print("frente")
                        elif 0 < (y+h) <= bola[1]:
                            print("dar ré")
                        elif 0 < bola[0] <= x:
                            print("virar esquerda")
                        elif 0 < (x+w) <= bola[0]:
                            print("virar direita")

                    elif x < (xDir -5*y//100) and (y - (20*h//100)) <= yDir <= (y + (20*h//100)):
                        #print("down")
                        if 0 < bola[1] <= y:
                            print("dar ré")
                        elif 0 < y <= bola[1]:
                            print("frente")
                        elif 0 < bola[0] <= x:
                            print("virar esquerda")
                        elif 0 < (x+w) <= bola[0]:
                            print("virar direita")'''

                
            tela = cv2.putText(tela,str(numeroNoTime+1),(x+40,y-15),font,0.8,(255,255,255),2,cv2.LINE_AA)

    for cnt in contornosEnemy:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        
        if area > 100: #ver se usar a tolerância
            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            #cv2.rectangle(tela, (x,y), (x +w, y +h), (0, 255, 0), 3) #debug? ver
            cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 0, 255), 0)
            np.append(deteccoes,[x,y,w,h])
            tela = cv2.putText(tela,str("enemy"),(x+40,y-15),font,0.8,(0,0,255),2,cv2.LINE_AA)

    'print(deteccoes)'
    cv2.imshow("blank", blank)
    cv2.imshow("Mask", mask) #Exibe a máscara("Mask") do vídeo
    cv2.imshow("tela", tela) #Exibe a filmagem("tela") do vídeo
    #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
    if cv2.waitKey(25) == ord('q'): break #tempo de exibição infinito (0) ou até se apertar a tecla q

cap.release()
cv2.destroyAllWindows()
