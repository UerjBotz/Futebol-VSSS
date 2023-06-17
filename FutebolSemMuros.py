import cv2
import numpy as np
from detector import find, global_orientation

#from pyserialF import serialStart, serialRotate, serialClose #############################
#Serial = serialStart('COM5',115200)  ###########################

fonte = cv2.FONT_HERSHEY_SIMPLEX

# ====================  Camera e tela  ======================= #
cap = cv2.VideoCapture(0) # Camera (alterar numero caso camera esteja em outro valor) #shape: (480, 640, 3)
#cap = cv2.VideoCapture("http://192.168.43.195:81/stream",cv2.CAP_FFMPEG) # camera ip
largura_tela = int(cap.get(3))
altura_tela  = int(cap.get(4))

# ====================  Intervalos de cores  ======================= #

#bola_th_min  = np.array([ 0,  30, 210]) #np.array([ 0, 50, 50]) 
#bola_th_max  = np.array([25, 210, 255]) #np.array([16,255,255])

bola_th_min  = np.array([ 0, 150, 200]) #np.array([ 0, 50, 50]) 
bola_th_max  = np.array([20, 230, 255]) #np.array([16,255,255])

azul_th_min  = np.array([100, 100, 100]) #np.array([ 0, 50, 50])
azul_th_max  = np.array([110, 220, 255]) #np.array([16,255,255])

#verde_th_min  = np.array([75, 100, 100]) #np.array([ 0, 50, 50])
#verde_th_max  = np.array([85, 220, 255]) #np.array([16,255,255])
#verde_th_min  = np.array([65, 100,  50]) #np.array([ 0, 50, 50])
#verde_th_max  = np.array([85, 250, 255]) #np.array([16,255,255])

verde_th_min  = np.array([90, 150,  50]) #np.array([ 0, 50, 50])
verde_th_max  = np.array([100, 230, 255]) #np.array([16,255,255])


# ====================  outras variaveis  ======================= #

girar = False
PRINT_S = True
batata = 0

# ======================== LOOP =========================== #

while True:
    # ===== captura dos frames ===== #
    ret, frame = cap.read()
    tela = cv2.resize(frame,(0,0),fx=1,fy=1)
    tela_hsv = frame.copy()
    #shape: (480, 640, 3)
    
    # ===== Transformação do espaço de cores e filtragem de ruido ===== #
    tela_blur = cv2.GaussianBlur( tela, (7,7), cv2.BORDER_DEFAULT )
    #cv2.imshow("tela_blur", tela_blur)
    frame_hsv = cv2.cvtColor(tela_blur, cv2.COLOR_BGR2HSV)
    cv2.imshow("HSV", frame_hsv)

    # ==== Detecção dos elementos por cor e area ==== #
    find( frame_hsv, tela, bola_th_min, bola_th_max, tag = "bola", type="max" )
    cnt_azul = find( frame_hsv, tela, azul_th_min, azul_th_max, tag = "azul" )
    cnt_verde = find( frame_hsv, tela, verde_th_min, verde_th_max, tag = "verde" )

    global_orientation( tela, cnt_azul, cnt_verde, type = "rect" )

    h, s, b = cv2.split(frame_hsv)
    #blank = np.zeros( frame_hsv.shape[:2], dtype='uint8' )
    #cv2.imshow("h", h )
    #cv2.imshow("s", s )
    #cv2.imshow("b", b )
    #cv2.imshow("H color", cv2.merge([h,blank,blank]) )
    #cv2.imshow("S color", cv2.merge([blank,s,blank]) )
    #cv2.imshow("B color", cv2.merge([blank,blank,b]) )

    # ====== Captura da camera com as informações ===== #
    cv2.imshow("tela", tela)

    # ====== Condição para encerramento ===== #
    #tempo de exibição infinito (0) ou até se apertar a tecla q
    if cv2.waitKey(25) == ord('q'): break

cap.release()
cv2.destroyAllWindows()
#serialClose(Serial)





# Box azul: [[369 347]
#  [395 322]
#  [449 376]
#  [424 402]]
# Box azul: [[322 224]
#  [376 186]
#  [392 210]
#  [338 247]]
# Box verde: [[398 320]
#  [423 295]
#  [449 321]
#  [424 346]]
# Box verde: [[330 172]
#  [356 154]
#  [373 178]
#  [348 197]]
# p_ref: [array([[369, 347],
#        [395, 322],
#        [449, 376],
#        [424, 402]], dtype=int64), array([[322, 224],
#        [376, 186],
#        [392, 210],
#        [338, 247]], dtype=int64)]
# p_2: [array([[398, 320],
#        [423, 295],
#        [449, 321],
#        [424, 346]], dtype=int64), array([[330, 172],
#        [356, 154],
#        [373, 178],
#        [348, 197]], dtype=int64)]