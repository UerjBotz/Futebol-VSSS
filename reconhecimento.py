import cv2
import numpy as np

import movimento

def centro (x, y, w, h):
    return (x+w//2, y+h//2)

blank = np.zeros((400,400))

def nothing (x): pass

'''
TODO:
- deletar detecções e integrar o teste grade
- deletar usada
- passar pelo centro pro astar
- tirar os ifs e deixar só o vetor que a gente descobriu como achar
- adicionar outras cores e inserir no loop
    - ajustar e pôr slider
- ver regras
    - ver regras de cor (/+quantidade)
- ver membro do time
'''

time = 0 # 0 para time azul, 1 para time amarelo
cap = cv2.VideoCapture(0) # Camera (alterar numero caso camera esteja em outro valor)

font = cv2.FONT_HERSHEY_SIMPLEX
width  = int(cap.get(3))
height = int(cap.get(4))
escalaGrade = 10 #quase não usada no código. problemas.
grade = np.zeros([height//10, width//10,3]) #inicializar grade pro a*

deteccoes  = np.array([]) #deletar
lower_blue = np.array([100, 80, 80])# array da cor mais clara time azul (alterar para a cor utilizada no robo físico)
upper_blue = np.array([110,255,255])# array da cor mais escura time azul (alterar para a cor utilizada no robo físico)
lower_yellow = np.array([26, 50, 50])# array da cor mais clara time amarelo (alterar para a cor utilizada no robo físico)
upper_yellow = np.array([46,255,255])# array da cor mais escura time amarelo (alterar para a cor utilizada no robo físico)

lower_ball  = np.array([ 0, 50, 50])
upper_ball  = np.array([16,255,255])
lower_green = np.array([80, 50, 50])
upper_green = np.array([90,255,255])
lower_roxo = np.array([80, 50, 50])
upper_roxo  = np.array([90,255,255])
lower_ciano = np.array([80, 50, 50])
upper_ciano = np.array([90,255,255])
lower_vermelho = np.array([80, 50, 50])
upper_vermelho = np.array([90,255,255])
lower_rosa = np.array([80, 50, 50])
upper_rosa = np.array([90,255,255])


#thresholds:
distancia = 300 # em milimetros
areaAzul = 18000*(100**2)/(distancia**2) # formula(d) = (areapixelsmedida*distanciamedida^2)/(d)^2
areaRosa = areaAzul*(280/1200) # multiplica a azul pela proporção entre os retângulos pra achar a rosa
areaRobo = areaAzul*(7412/1200) #multiplica a azul pela proporção entre os retângulos pra achar o robo inteiro
tamanhoAumentar = int((areaRobo**(1/2))/2)
tolerancia = 50/100

# vetor direção #(não usado. mudar) #deletar
normalx = np.array([width,height]) ; normaly = np.array([0,0])
direcao1x = np.array([0,0]) ; direcao1y = np.array([0,0])
direcao1x = np.clip(direcao1x,0,height) ; direcao1y = np.clip(direcao1x,0,height)

# menu interativo
cv2.namedWindow("blank") # alterar primeiro valor que aparece para atualizar valores encontrados nas mascaras
cv2.createTrackbar("azul_min","blank",102,120,nothing)  ; cv2.createTrackbar("azul_max","blank",110,120,nothing)
cv2.createTrackbar("amarelo_min","blank",24,40,nothing) ; cv2.createTrackbar("amarelo_max","blank",34,40,nothing)
cv2.createTrackbar("bola_min","blank",10,30,nothing)    ; cv2.createTrackbar("bola_max","blank",20,30,nothing)
cv2.createTrackbar("verde_min","blank",80,100,nothing)  ; cv2.createTrackbar("verde_max","blank",90,100,nothing) 
cv2.createTrackbar("distância","blank",200,3000,nothing)

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
    
    lower_blue[0]   = cv2.getTrackbarPos('azul_min', 'blank')    ; upper_blue[0] = cv2.getTrackbarPos('azul_max', 'blank')
    lower_yellow[0] = cv2.getTrackbarPos('amarelo_min', 'blank') ; upper_yellow[0] = cv2.getTrackbarPos('amarelo_max', 'blank')
    lower_ball[0]   = cv2.getTrackbarPos('bola_min', 'blank')    ; upper_ball[0] = cv2.getTrackbarPos('bola_max', 'blank')
    lower_green[0]  = cv2.getTrackbarPos('verde_min', 'blank')   ; upper_green[0] = cv2.getTrackbarPos('verde_max', 'blank')
    distancia = cv2.getTrackbarPos('distância','blank')

    #1 Detecção dos membros da equipe:
    hsv = cv2.cvtColor(tela, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
    mask = cv2.inRange(hsv, lower_color, upper_color) # máscara para detecção de um objeto
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contornos, _ =  cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    maskBall = cv2.inRange(hsv,lower_ball,upper_ball)
    maskEnemy = cv2.inRange(hsv,lower_enemy,upper_enemy)
    _, maskBall = cv2.threshold(maskBall, 254, 255, cv2.THRESH_BINARY)
    _, maskEnemy = cv2.threshold(maskEnemy, 254, 255, cv2.THRESH_BINARY)
    contornoBall, _ =  cv2.findContours(maskBall, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contornosEnemy, _ =  cv2.findContours(maskEnemy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    maskDir = cv2.inRange(hsv,lower_green,upper_green)
    _, maskDir = cv2.threshold(maskDir, 254, 255, cv2.THRESH_BINARY)
    contornoDir, _ =  cv2.findContours(maskDir, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    bola = [0,0,0,0]

    for cnt in contornoBall:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)

        if area > 100: # ver se usar a tolerância
            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            xbola, ybola, wbola, hbola = cv2.boundingRect(cnt)
            bola[0] = xbola ; bola[1] = ybola ; bola[2] = wbola ; bola[3] = hbola
            cv2.rectangle(tela, (xbola, ybola), (xbola + wbola, ybola + hbola), (0, 255, 0), 0)
            np.append(deteccoes,[xbola,ybola,wbola,hbola])
            tela = cv2.putText(tela,str("ball"),(xbola+40,ybola-15),font,0.8,(255,255,0),2,cv2.LINE_AA)
            grade[ybola//10][xbola//10][0] = 255 #seta o primeiro valor de cor do pixel
 
    for cnt in contornos:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        if(areaAzul*(1-tolerancia) <= area <= areaAzul*(1+tolerancia)):

            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(tela, (x, y), (x + w, y + h), (255, 0, 0), 0)
            np.append(deteccoes,[x,y,w,h])

            centrado = centro(x,y,w,h)
            grade[int(centrado[1]//escalaGrade)][int(centrado[0]//escalaGrade)][0] = 150 #seta o primeiro valor de cor do pixel

            hsvNum = hsv[max(y-tamanhoAumentar,0) : min(y+h+tamanhoAumentar,height),  max(x-tamanhoAumentar,0): min(x+w+tamanhoAumentar,width)] #clampa

            # detecção do num no time
            cv2.imshow("usada", hsvNum)#Exibe a filmagem("tela") do vídeo

            numeroNoTime = 0

            maskDir = cv2.inRange(hsv,lower_green,upper_green)
            _, maskDir = cv2.threshold(maskDir, 254, 255, cv2.THRESH_BINARY)
            contornoDir, _ =  cv2.findContours(maskDir, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
                    
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

                    firstLine = [(xDir+(wDir//2)),(yDir + (hDir//2)),(x+(w//2)),(y+(h//2))]
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
            grade[y//10][x//10][0] = 80 #seta o primeiro valor de cor do pixel

            #cv2.rectangle(tela, (x,y), (x +w, y +h), (0, 255, 0), 3) #debug? ver
            cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 0, 255), 0)
            np.append(deteccoes,[x,y,w,h])
            tela = cv2.putText(tela,str("enemy"),(x+40,y-15),font,0.8,(0,0,255),2,cv2.LINE_AA)

    'print(deteccoes)'
    cv2.imshow("blank", blank)
    cv2.imshow("Mask", mask) #Exibe a máscara("Mask") do vídeo
    cv2.imshow("tela", tela) #Exibe a filmagem("tela") do vídeo

    cv2.imshow("grade", cv2.resize(grade,(0,0),fx=10,fy=10)) #Exibe a filmagem("grade") do vídeo
    grade = np.zeros([height//10,width//10,3]) # reseta

    #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
    if cv2.waitKey(25) == ord('q'): break #tempo de exibição infinito (0) ou até se apertar a tecla q

cap.release()
cv2.destroyAllWindows()
