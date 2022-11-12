import cv2 #type: ignore
import numpy as np
from dataclasses import dataclass
from math import pi, cos, sin, asin # pra girar o vetor

def nada (x): pass

def centro (x: int, y: int, w: int, h: int) -> tuple[int,int]:
    return (x+w//2, y+h//2)

@dataclass(slots=True)
class Cor ():
    MIN: np.ndarray
    MAX: np.ndarray

def achar_contornos (tela, cor: Cor, *, janela_debug: str = "") : #TODO: parametrizar constantes cv2.etc)
    _, mascara = cv2.threshold(cv2.inRange(tela, cor.MIN, cor.MAX), 254, 255, cv2.THRESH_BINARY) # oqq são esses 254, 255? #ver magic numbers
    contornos, _ = cv2.findContours(mascara, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

    if len(janela_debug): #TODO: ver se fazer assim mesmo
        cv2.imshow(janela_debug, mascara) #Exibe um janela com a máscara
    return contornos

@dataclass(slots=True)
class objeto_movel : #não usada
    x: int = 0; y: int = 0
    w: int = 0; h: int = 0
    dx:int = 0; dy:int = 0;

'''
TODO:
- arrumação:
    - deletar usada ou usar de verdade pra alguma coisa
    - classe pro menu (com inseridor e mostrador de trackbar, desligador de ui)
    - função de posição do retângulo id (recebe uma parte da tela (+ cor?))
    - *
    - **
- movimento:
    - astar
        - ver grade direitinho (mexer na função)
        - passar como uma área
    - movimentos em geral (estratégia de jogo, etc.)
    - integrar com a eletrônica (colocar o código de serial no movimento.py)
- geral:
    - ajustar area_bola, com o tamanho esperado certo em pixels
    - endireitar o vetor pra usar (em progresso) #(percebi que o tamanho varia de acordo com a posição na tela, investigar)
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

def ocupar_grade (grade, x:int,y:int,w:int,h:int, cor=100) -> None:
    #TODO: ocupar mais quadrados da grade pra cada obj
    centrado = centro(x,y,w,h)
    grade[int(centrado[1]//escala_grade)][int(centrado[0]//escala_grade)][0] = cor #seta o primeiro valor de cor do pixel

#vetor e dimensões do robô (mm)
altura_robo = 74#altura do retangulo maior
altura_id = 27  #altura do retângulo menor
distancia_centros = 22 #largura da fita

    #acha matriz de rotação #(teria como fazer menos conta aqui, mas como é só uma vez...)
seno_angulo_vetor = (altura_robo/2 - altura_id/2)/distancia_centros

while not (seno_angulo_vetor <= 1) : seno_angulo_vetor -=1 # deixa entre -1 e 1 #(mudar)
while not (seno_angulo_vetor >=-1) : seno_angulo_vetor +=1

angulo_vetor = pi/2 - asin(seno_angulo_vetor) #olhar isso do domínio
matriz_correção = np.array([
                           [cos(angulo_vetor), -sin(angulo_vetor)],
                           [sin(angulo_vetor),  cos(angulo_vetor)]
                           ])

#thresholds:
distancia = 300 # em milimetros

area_ret_time = 18000*(100**2)/(distancia**2) # formula(d) = (areapixelsmedida*distanciamedida^2)/(d)^2
area_roi_robo = area_ret_time*(7412/1200) #multiplica a "azul" pela proporção entre os retângulos pra achar o robo inteiro
area_ret_ID   = area_ret_time*(280/1200) # multiplica a "azul" pela proporção entre os retângulos pra achar a "rosa"

area_bola = area_ret_time*(280/1200)*3/2 # mudar pro valor de verdade da bola

tamanho_aumentar = int((area_roi_robo**(1/2))/2)
tolerancia = 50/100

    #cores (alterar de acordo com a cor utilizada no robo fisico)
ajuste_cor = 20
              #times 
azul    = Cor(np.array([100, 80, 80]),np.array([110,255,255]))
amarelo = Cor(np.array([26, 50, 50]), np.array([46,255,255]))
              #ids (ajustar (nesses só o verde ok))
verde = Cor(np.array([80, 50, 50]), np.array([90,255,255])) 
roxo  = Cor(np.array([80, 50, 50]), np.array([90,255,255]))
ciano = Cor(np.array([80, 50, 50]), np.array([90,255,255]))
rosa  = Cor(np.array([80, 50, 50]), np.array([90,255,255]))
vermelho = Cor(np.array([80, 50, 50]), np.array([90,255,255]))
              #(bola)
# cor_bola = Cor(np.array([ 0, 50, 50]), np.array([16,255,255]))
cor_bola = Cor(np.array([ 4, 50, 50]), np.array([ 7,255,255]))

# menu interativo  # atualizar o valor na definição da cor se achar um melhor
menu = np.zeros((1,400)); cv2.namedWindow("menu") #ver se com o '1' ainda funciona pra todo mundo (/ no windows)

cv2.createTrackbar("azul_min",   'menu',    azul.MIN[0],    azul.MIN[0] +ajuste_cor,nada) ; cv2.createTrackbar("azul_max",   'menu',    azul.MAX[0],    azul.MAX[0] +ajuste_cor,nada)
cv2.createTrackbar("amarelo_min",'menu', amarelo.MIN[0], amarelo.MIN[0] +ajuste_cor,nada) ; cv2.createTrackbar("amarelo_max",'menu', amarelo.MAX[0], amarelo.MAX[0] +ajuste_cor,nada)
cv2.createTrackbar("bola_min",   'menu',cor_bola.MIN[0],cor_bola.MIN[0] +ajuste_cor,nada) ; cv2.createTrackbar("bola_max",   'menu',cor_bola.MAX[0],cor_bola.MAX[0] +ajuste_cor,nada)
cv2.createTrackbar("verde_min",  'menu',   verde.MIN[0],   verde.MIN[0] +ajuste_cor,nada) ; cv2.createTrackbar("verde_max",  'menu',   verde.MAX[0],   verde.MAX[0] +ajuste_cor,nada) 
cv2.createTrackbar("distância",'menu',200,3000,nada) #acho que essa não tá servindo de nada pq a gente usa antes de poder mexer

# cor dos times
if time == 0: 
    cor_aliado = azul ; cor_oponente = amarelo
else:
    cor_aliado = amarelo ; cor_oponente = azul


while True: # Loop de repetição para ret e frame do vídeo
    ret, frame = cap.read() # alterar "tela" para "frame" e utilizar a linha de baixo caso necessário diminuir a resolução da imagem
    tela = cv2.resize(frame,(0,0),fx=1,fy=1)
    # Extrair a região de interesse:
    '''roi = frame[x:x+?,y:y+?] # neste caso foi utilizada toda a imagem, mas pode ser alterado'''
    
    cor_bola.MIN[0] = cv2.getTrackbarPos('bola_min',   'menu') ; cor_bola.MAX[0] = cv2.getTrackbarPos('bola_max',   'menu')
    azul.MIN[0]     = cv2.getTrackbarPos('azul_min',   'menu') ; azul.MAX[0]     = cv2.getTrackbarPos('azul_max',   'menu')
    amarelo.MIN[0]  = cv2.getTrackbarPos('amarelo_min','menu') ; amarelo.MAX[0]  = cv2.getTrackbarPos('amarelo_max','menu')
    verde.MIN[0]    = cv2.getTrackbarPos('verde_min',  'menu') ; verde.MAX[0]    = cv2.getTrackbarPos('verde_max',  'menu')
    distancia = cv2.getTrackbarPos('distância','menu')

    #1 Detecção dos jogadores e bola
    hsv = cv2.cvtColor(tela, cv2.COLOR_BGR2HSV) # A cores em HSV funcionam baseadas em hue, no caso do opencv, varia de 0 a 180º (diferente do padrão de 360º)

    contornos_aliados = achar_contornos(hsv, cor_aliado)#, janela_debug="mascara_aliados")
    contornos_bola    = achar_contornos(hsv, cor_bola)#, janela_debug="mascara_bola")
    contornos_oponentes = achar_contornos(hsv, cor_oponente)

    for cnt in contornos_bola:
        #Cálculo da área e remoção de elementos pequenos
        area = cv2.contourArea(cnt)

        if (area_bola*(1-tolerancia) <= area <= area_bola*1+tolerancia):
            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0) #ver magic numbers
            x_bola, y_bola, w_bola, h_bola = cv2.boundingRect(cnt)

            ocupar_grade(grade, x_bola,y_bola,w_bola,h_bola, cor=255)

            cv2.rectangle(tela, (x_bola, y_bola), (x_bola + w_bola, y_bola + h_bola), (0, 255, 0), 0)
            tela = cv2.putText(tela,str("bola"),(x_bola+40,y_bola-15),fonte,0.8,(255,255,0),2,cv2.LINE_AA)
 
    for cnt in contornos_aliados:

        area = cv2.contourArea(cnt)

        #Filtra retângulos com área muito distante da esperada
        if (area_ret_time*(1-tolerancia) <= area <= area_ret_time*(1+tolerancia)):

            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0) #ver magic numbers
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(tela, (x, y), (x + w, y + h), (255, 0, 0), 0)

            #TODO: usar dimensões do robô em vez de do retângulo
            ocupar_grade(grade, x,y,w,h, cor=150)

            roi = hsv[max(y-tamanho_aumentar,0) : min(y+h+tamanho_aumentar,altura_tela),  max(x-tamanho_aumentar,0) : min(x+w+tamanho_aumentar,largura_tela)] #clampa

            # detecção do num no time e direção do robô
            cv2.imshow("roi", roi) #Exibe a filmagem("roi") do vídeo

            numeroNoTime = 0

            #usar usada/roi aqui em vez de hsv?
            contornos_ID = achar_contornos(hsv, verde) # tem que fazer isso ser variável (por jogador, por conjunto de cores)
            # contornos_ID = achar_contornos(roi, (verde_min,verde_max)) # pra fazer assim precisa empurrar a posição pra perto do retâgulo de novo (ou talvez usar uma máscara)

            for cnt in contornos_ID:

                area = cv2.contourArea(cnt)

                #Filtra retângulos com área muito distante da esperada
                if (area_ret_ID*(1-tolerancia) <= area <= area_ret_ID*(1+tolerancia)):
                    cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
                    xID, yID, wID, hID = cv2.boundingRect(cnt)

                    cv2.rectangle(tela, (xID, yID), (xID + wID, yID + hID), (0, 0, 0), 0)

                    tela = cv2.putText(tela,str("id"),(xID,yID),fonte,0.8,(255,0,255),2,cv2.LINE_AA)

                    linha_dir = np.array([*centro(xID, yID, wID, hID), *centro(x,y,w,h)])
                    tela = cv2.arrowedLine(tela, linha_dir[:2], linha_dir[2:], (255,0,0),5)

                    #print(linha_dir)
                    #print(f"{linha_dir[0]-linha_dir[2])}, {str(linha_dir[0]-linha_dir[2]}")
                    vetor_normalizado = np.subtract(linha_dir[:2], linha_dir[2:])
                    #print(vetor_normalizado)
                    vetor_dir = np.dot(matriz_correção, vetor_normalizado)
                    #print(vetor_normalizado)
                    tela = cv2.arrowedLine(tela, (yID,int(vetor_dir[1])+yID), (xID,int(vetor_dir[0])+xID), (240,100,0),5)

                    #aqui ficavam os if-elses de direção

            tela = cv2.putText(tela,str(numeroNoTime+1),(x+40,y-15),fonte,0.8,(255,255,255),2,cv2.LINE_AA)

    for cnt in contornos_oponentes:

        area = cv2.contourArea(cnt)
        
        #Filtra retângulos com área muito distante da esperada
        if (area_ret_time*(1-tolerancia) <= area <= area_ret_time*(1+tolerancia)):
            cv2.drawContours(tela, [cnt], -1, (0, 255, 0),0)
            x, y, w, h = cv2.boundingRect(cnt)

            #TODO: usar dimensões do robô em vez de do retângulo
            ocupar_grade(grade, x,y,w,h, cor=80)

            cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 0, 255), 0)
            tela = cv2.putText(tela,str("oponente"),(x+40,y-15),fonte,0.8,(0,0,255),2,cv2.LINE_AA)

    cv2.imshow("menu", menu)
    #(ficava aqui mostrar a máscara dos aliados)
    cv2.imshow("tela", tela) #Exibe a filmagem("tela") do vídeo

    #cv2.imshow("grade", cv2.resize(grade,(0,0),fx=10,fy=10)) #Exibe a filmagem("grade") do vídeo
    grade = np.zeros([altura_tela//10,largura_tela//10,3]) # reseta

    #cv2.imshow("usada",usada)#Exibe a filmagem("ROI") do vídeo
    if cv2.waitKey(25) == ord('q'): break #tempo de exibição infinito (0) ou até se apertar a tecla q

cap.release()
cv2.destroyAllWindows()
