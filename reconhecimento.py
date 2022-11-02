import cv2
import numpy as np

import movimento

blank = np.zeros((400,400))

def nada (x): pass

def centro (x, y, w, h):
    return (x+w//2, y+h//2)

def achar_contornos (tela, cor: tuple, *, janela_debug: str = "") : #TODO: parametrizar constantes cv2.etc)
    cor_min, cor_max = cor

    _, mascara = cv2.threshold(cv2.inRange(tela, cor_min, cor_max), 254, 255, cv2.THRESH_BINARY) # oqq são esses 254, 255? #ver magic numbers
    contornos, _ = cv2.findContours(mascara, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

    if len(janela_debug): #TODO: ver se fazer assim mesmo
        cv2.imshow(janela_debug, mascara) #Exibe um janela com a máscara

    return contornos

'''
TODO:
- arrumação:
    - deletar usada ou usar de verdade pra alguma coisa
    - classe pro menu (com inseridor e mostrador de trackbar, desligador de ui)
    - *
    - **
- movimento:
    - astar
        - ver grade direitinho (+os outros obstáculos)
        - passar pelo centro (ou como uma área)
    - movimentos em geral (estratégia de jogo, etc.)
    - integrar com a eletrônica (mandar movimentos via ESP)
- geral:
    - adicionar area_bola, com o tamanho esperado em pixels
    - endireitar o vetor pra usar
    - vetor bola-robô
    - adicionar outras cores e inserir no loop
        - ajustar e pôr slider
        - *fazer função/classe pra isso
    - criar modos de jogo (plano: switch, argumentos de linha de comando)
    - ver regras
        - ver regras de cor (/+quantidade)
    - ver membro do time e "personalidade"
- propostas:
    - colocar TO-DO em outro arquivo (ver)
    - colocar menu de seleção de cores em outro módulo
    - **fazer arquivo main e transformar reconhecimento em uma biblioteca
    - classe janelas
        - ***fazer funções pra escrever na tela e adicionar opção de desligar
'''

time = 0 # 0 para time azul, 1 para time amarelo
cap = cv2.VideoCapture(0) # Camera (alterar numero caso camera esteja em outro valor)

fonte = cv2.FONT_HERSHEY_SIMPLEX

largura_tela = int(cap.get(3))
altura_tela  = int(cap.get(4))

escala_grade = 10 #quase não usada no código. problemas.
grade = np.zeros([altura_tela//10, largura_tela//10,3]) #inicializar grade pro a*

#cores (alterar de acordo com a cor utilizada no robo fisico)
              #times 
azul_min = np.array([100, 80, 80]) 
azul_max = np.array([110,255,255])  
amarelo_min = np.array([26, 50, 50]) 
amarelo_max = np.array([46,255,255])
              #bola
bola_min  = np.array([ 0, 50, 50]) 
bola_max  = np.array([16,255,255])
              #ids (ajustar)
verde_min = np.array([80, 50, 50])
verde_max = np.array([90,255,255]) #só ok até esse verde
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

area_ret_time = 18000*(100**2)/(distancia**2) # formula(d) = (areapixelsmedida*distanciamedida^2)/(d)^2
area_roi_robo = area_ret_time*(7412/1200) #multiplica a "azul" pela proporção entre os retângulos pra achar o robo inteiro
area_ret_ID   = area_ret_time*(280/1200) # multiplica a "azul" pela proporção entre os retângulos pra achar a "rosa"

tamanho_aumentar = int((area_roi_robo**(1/2))/2)
tolerancia = 50/100

# menu interativo  # alterar primeiro valor que aparece para atualizar valores encontrados nas mascaras
cv2.namedWindow("blank")
cv2.createTrackbar("azul_min","blank",102,120,nada)  ; cv2.createTrackbar("azul_max","blank",110,120,nada)
cv2.createTrackbar("amarelo_min","blank",24,40,nada) ; cv2.createTrackbar("amarelo_max","blank",34,40,nada)
cv2.createTrackbar("bola_min","blank",10,30,nada)    ; cv2.createTrackbar("bola_max","blank",20,30,nada)
cv2.createTrackbar("verde_min","blank",80,100,nada)  ; cv2.createTrackbar("verde_max","blank",90,100,nada) 
cv2.createTrackbar("distância","blank",200,3000,nada)

# cor dos times
if time == 0: 
    aliado_min = azul_min ; oponente_min = amarelo_min
    aliado_max = azul_max ; oponente_max = amarelo_max
else:
    aliado_min = amarelo_min ; oponente_min = azul_min
    aliado_max = amarelo_max ; oponente_max = azul_max


while True: # Loop de repetição para ret e frame do vídeo
    ret, frame = cap.read() # alterar "tela" para "frame" e utilizar a linha de baixo caso necessário diminuir a resolução da imagem
    tela = cv2.resize(frame,(0,0),fx=1,fy=1)
    # Extrair a região de interesse:
    '''roi = frame[x:x+?,y:y+?] # neste caso foi utilizada toda a imagem, mas pode ser alterado'''
    
    azul_min[0]    = cv2.getTrackbarPos('azul_min', 'blank')    ; azul_max[0]    = cv2.getTrackbarPos('azul_max', 'blank')
    amarelo_min[0] = cv2.getTrackbarPos('amarelo_min', 'blank') ; amarelo_max[0] = cv2.getTrackbarPos('amarelo_max', 'blank')
    bola_min[0]    = cv2.getTrackbarPos('bola_min', 'blank')    ; bola_max[0]    = cv2.getTrackbarPos('bola_max', 'blank')
    verde_min[0]   = cv2.getTrackbarPos('verde_min', 'blank')   ; verde_max[0]   = cv2.getTrackbarPos('verde_max', 'blank')
    distancia = cv2.getTrackbarPos('distância','blank')

    #1 Detecção dos jogadores e bola
    hsv = cv2.cvtColor(tela, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)

    contornos_aliados = achar_contornos(hsv, (aliado_min,aliado_max), janela_debug="mascara_aliados")
    contornos_bola    = achar_contornos(hsv, (bola_min,bola_max))
    contornos_oponentes = achar_contornos(hsv, (oponente_min,oponente_max))

    for cnt in contornos_bola:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)

        if area > 100: # ver se usar a tolerância
            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0) #ver magic numbers
            x_bola, y_bola, w_bola, h_bola = cv2.boundingRect(cnt)

            cv2.rectangle(tela, (x_bola, y_bola), (x_bola + w_bola, y_bola + h_bola), (0, 255, 0), 0)

            tela = cv2.putText(tela,str("bola"),(x_bola+40,y_bola-15),fonte,0.8,(255,255,0),2,cv2.LINE_AA)
            grade[y_bola//10][x_bola//10][0] = 255 #seta o primeiro valor de cor do pixel #colocar mais certinho isso
 
    for cnt in contornos_aliados:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        if (area_ret_time*(1-tolerancia) <= area <= area_ret_time*(1+tolerancia)):

            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0) #ver magic numbers
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(tela, (x, y), (x + w, y + h), (255, 0, 0), 0)

            centrado = centro(x,y,w,h)
            grade[int(centrado[1]//escala_grade)][int(centrado[0]//escala_grade)][0] = 150 #seta o primeiro valor de cor do pixel

            roi = hsv[max(y-tamanho_aumentar,0) : min(y+h+tamanho_aumentar,altura_tela),  max(x-tamanho_aumentar,0) : min(x+w+tamanho_aumentar,largura_tela)] #clampa

            # detecção do num no time
            cv2.imshow("roi", roi) #Exibe a filmagem("roi") do vídeo

            numeroNoTime = 0

            #usar usada/roi aqui em vez de hsv?
            contornos_ID = achar_contornos(hsv, (verde_min,verde_max)) # tem que fazer isso ser variável (por jogador, por conjunto de cores)
            # contornos_ID = achar_contornos(roi, (verde_min,verde_max)) # pra fazer assim precisa empurrar a posição pra perto do retâgulo de novo (ou talvez usar uma máscara)

            for cnt in contornos_ID:
                #Cálculo da área e remoção de elementos pequenos
                area = cv2.contourArea(cnt)

                if area > 100: #ver se usar a tolerância
                    cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
                    xID, yID, wID, hID = cv2.boundingRect(cnt)

                    cv2.rectangle(tela, (xID, yID), (xID + wID, yID + hID), (0, 0, 0), 0)

                    tela = cv2.putText(tela,str("Dir"),(xID+40,yID-15),fonte,0.8,(255,0,255),2,cv2.LINE_AA)

                    line = [(xID+(wID//2)),(yID + (hID//2)),(x+(w//2)),(y+(h//2))] #trocar isso por dois centrado() na linha seguinte
                    tela = cv2.arrowedLine(tela,(line[0],line[1]),(line[2],line[3]),(255,0,0),5)

                    #aqui ficavam os if-elses de direção

            tela = cv2.putText(tela,str(numeroNoTime+1),(x+40,y-15),fonte,0.8,(255,255,255),2,cv2.LINE_AA)

    for cnt in contornos_oponentes:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)
        
        if area > 100: #ver se usar a tolerância
            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)
            grade[y//10][x//10][0] = 80 #seta o primeiro valor de cor do pixel

            cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 0, 255), 0)
            tela = cv2.putText(tela,str("enemy"),(x+40,y-15),fonte,0.8,(0,0,255),2,cv2.LINE_AA)

    cv2.imshow("blank", blank) #se mudar o nome aqui o menu ainda aparece, só que separado
    #(ficava aqui mostrar a máscara dos aliados)
    cv2.imshow("tela", tela) #Exibe a filmagem("tela") do vídeo

    cv2.imshow("grade", cv2.resize(grade,(0,0),fx=10,fy=10)) #Exibe a filmagem("grade") do vídeo
    grade = np.zeros([altura_tela//10,largura_tela//10,3]) # reseta

    #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
    if cv2.waitKey(25) == ord('q'): break #tempo de exibição infinito (0) ou até se apertar a tecla q

cap.release()
cv2.destroyAllWindows()
