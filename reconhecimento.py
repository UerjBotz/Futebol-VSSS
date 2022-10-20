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

fonte = cv2.FONT_HERSHEY_SIMPLEX

largura_tela  = int(cap.get(3))
altura_tela = int(cap.get(4))

escala_grade = 10 #quase não usada no código. problemas.
grade = np.zeros([altura_tela//10, largura_tela//10,3]) #inicializar grade pro a*

deteccoes  = np.array([]) #deletar

#cores (alterar de acordo com a cor utilizada no robo fisico)
              #times 
azul_min = np.array([100, 80, 80]) 
azul_max = np.array([110,255,255])  
amarelo_min = np.array([26, 50, 50]) 
amarelo_max = np.array([46,255,255])
              #ids
bola_min  = np.array([ 0, 50, 50]) 
bola_max  = np.array([16,255,255])
verde_min = np.array([80, 50, 50])
verde_max = np.array([90,255,255])
roxo_min  = np.array([80, 50, 50])
roxo_max  = np.array([90,255,255])
ciano_min = np.array([80, 50, 50])
ciano_max = np.array([90,255,255])
vermelho_min = np.array([80, 50, 50])
vermelho_max = np.array([90,255,255])
rosa_min = np.array([80, 50, 50])
rosa_max = np.array([90,255,255])

#thresholds:
distancia = 300 # em milimetros

area_azul = 18000*(100**2)/(distancia**2) # formula(d) = (areapixelsmedida*distanciamedida^2)/(d)^2
area_rosa = area_azul*(280/1200) # multiplica a azul pela proporção entre os retângulos pra achar a rosa
area_robo = area_azul*(7412/1200) #multiplica a azul pela proporção entre os retângulos pra achar o robo inteiro

tamanho_aumentar = int((area_robo**(1/2))/2)
tolerancia = 50/100

# vetor direção #(não usado. mudar) #deletar
normalx = np.array([largura_tela,altura_tela]) ; normaly = np.array([0,0])
direcao1x = np.array([0,0]) ; direcao1y = np.array([0,0])
direcao1x = np.clip(direcao1x,0,altura_tela) ; direcao1y = np.clip(direcao1x,0,altura_tela)
 
# menu interativo
cv2.namedWindow("blank") # alterar primeiro valor que aparece para atualizar valores encontrados nas mascaras
cv2.createTrackbar("azul_min","blank",102,120,nothing)  ; cv2.createTrackbar("azul_max","blank",110,120,nothing)
cv2.createTrackbar("amarelo_min","blank",24,40,nothing) ; cv2.createTrackbar("amarelo_max","blank",34,40,nothing)
cv2.createTrackbar("bola_min","blank",10,30,nothing)    ; cv2.createTrackbar("bola_max","blank",20,30,nothing)
cv2.createTrackbar("verde_min","blank",80,100,nothing)  ; cv2.createTrackbar("verde_max","blank",90,100,nothing) 
cv2.createTrackbar("distância","blank",200,3000,nothing)

# cor dos times
if time == 0: 
    aliado_min = azul_min ; lower_enemy = amarelo_min
    aliado_max = azul_max ; upper_enemy = amarelo_max
else:
    aliado_min = amarelo_min ; lower_enemy = azul_min
    aliado_max = amarelo_max ; upper_enemy = azul_max


while True: # Loop de repetição para ret e frame do vídeo
    ret, frame = cap.read() # alterar "tela" para "frame" e utilizar a linha de baixo caso necessário diminuir a resolução da imagem
    tela = cv2.resize(frame,(0,0),fx=1,fy=1)
    # Extrair a região de interesse:
    '''roi =  frame[x:x+?,y:y+?] # neste caso foi utilizada toda a imagem, mas pode ser alterado'''
    
    azul_min[0]    = cv2.getTrackbarPos('azul_min', 'blank')    ; azul_max[0]    = cv2.getTrackbarPos('azul_max', 'blank')
    amarelo_min[0] = cv2.getTrackbarPos('amarelo_min', 'blank') ; amarelo_max[0] = cv2.getTrackbarPos('amarelo_max', 'blank')
    bola_min[0]    = cv2.getTrackbarPos('bola_min', 'blank')    ; bola_max[0]  = cv2.getTrackbarPos('bola_max', 'blank')
    verde_min[0]   = cv2.getTrackbarPos('verde_min', 'blank')   ; verde_max[0] = cv2.getTrackbarPos('verde_max', 'blank')
    distancia = cv2.getTrackbarPos('distância','blank')

    #1 Detecção dos membros da equipe:
    hsv = cv2.cvtColor(tela, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)
    mask = cv2.inRange(hsv, aliado_min, aliado_max) # máscara para detecção de um objeto
    
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    maskBall = cv2.inRange(hsv,bola_min,bola_max)
    maskEnemy = cv2.inRange(hsv,lower_enemy,upper_enemy)
    _, maskBall = cv2.threshold(maskBall, 254, 255, cv2.THRESH_BINARY)
    _, maskEnemy = cv2.threshold(maskEnemy, 254, 255, cv2.THRESH_BINARY)

    contornoBall, _ =  cv2.findContours(maskBall, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contornosEnemy, _ =  cv2.findContours(maskEnemy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    maskDir = cv2.inRange(hsv,verde_min,verde_max)
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
            tela = cv2.putText(tela,str("ball"),(xbola+40,ybola-15),fonte,0.8,(255,255,0),2,cv2.LINE_AA)
            grade[ybola//10][xbola//10][0] = 255 #seta o primeiro valor de cor do pixel
 
    for cnt in contornos:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        if(area_azul*(1-tolerancia) <= area <= area_azul*(1+tolerancia)):

            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(tela, (x, y), (x + w, y + h), (255, 0, 0), 0)
            np.append(deteccoes,[x,y,w,h])

            centrado = centro(x,y,w,h)
            grade[int(centrado[1]//escala_grade)][int(centrado[0]//escala_grade)][0] = 150 #seta o primeiro valor de cor do pixel

            hsvNum = hsv[max(y-tamanho_aumentar,0) : min(y+h+tamanho_aumentar,altura_tela),  max(x-tamanho_aumentar,0) : min(x+w+tamanho_aumentar,largura_tela)] #clampa

            # detecção do num no time
            cv2.imshow("usada", hsvNum)#Exibe a filmagem("tela") do vídeo

            numeroNoTime = 0

            maskDir = cv2.inRange(hsv,verde_min,verde_max)
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
                    tela = cv2.putText(tela,str("Dir"),(xDir+40,yDir-15),fonte,0.8,(255,0,255),2,cv2.LINE_AA)
                    '''direcao1x  = [(x+w//2),(y+h//2)] ; direcao1y = [(bola[0]+bola[2]//2),(bola[1]+bola[3]//2)]
                    tela = cv2.arrowedLine(tela,direcao1x,direcao1y,[255,255,255],5)'''

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

                
            tela = cv2.putText(tela,str(numeroNoTime+1),(x+40,y-15),fonte,0.8,(255,255,255),2,cv2.LINE_AA)

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
            tela = cv2.putText(tela,str("enemy"),(x+40,y-15),fonte,0.8,(0,0,255),2,cv2.LINE_AA)

    'print(deteccoes)'
    cv2.imshow("blank", blank)
    cv2.imshow("Mask", mask) #Exibe a máscara("Mask") do vídeo
    cv2.imshow("tela", tela) #Exibe a filmagem("tela") do vídeo

    cv2.imshow("grade", cv2.resize(grade,(0,0),fx=10,fy=10)) #Exibe a filmagem("grade") do vídeo
    grade = np.zeros([altura_tela//10,largura_tela//10,3]) # reseta

    #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
    if cv2.waitKey(25) == ord('q'): break #tempo de exibição infinito (0) ou até se apertar a tecla q

cap.release()
cv2.destroyAllWindows()
