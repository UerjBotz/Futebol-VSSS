import cv2
import numpy as np


#H:32.55764119219941  W:65.19202405202648
#Center: [[523.  358.5]]
#Vx: [[510.5 369.5]]
#Vy: [[501. 334.]]
#Vetor diretor u: [[-0.75071352  0.66062789]]
#H:37.0  W:76.21679604916491
#Center: [[322. 301.]]
#Vx: [[304.5 307. ]]
#Vy: [[309.5 265. ]]
#Vetor diretor u: [[-0.94594595  0.32432432]]

fonte = cv2.FONT_HERSHEY_SIMPLEX

# ===========  Detecção de elementos por cor e área  ============= #
def find( im_hsv, tela, down, up, tag = "0", a_min = 600, type = "list"):
    
    # Mascara
    mask = cv2.inRange(im_hsv, down, up)
    cv2.imshow(tag, mask)
    
    # Contornos
    contornos, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    a_max = 0
    cnt_list = []

    # Verificação dos contornos
    for i, cnt in enumerate(contornos):
        area = cv2.contourArea(cnt)
        if( type == "list" ):
            if( area > a_min ):
                cnt_list += [ cnt ]
        
        if( area > a_max ):
            a_max = area
            
            if( type != "list" ):
                if( area > a_min ):
                    cnt_list += [ cnt ]

    for cnt in cnt_list:
        
        cv2.drawContours(tela, [cnt], -1, (0, 255, 0), 0)

        x_bola, y_bola, w_bola, h_bola = cv2.boundingRect(cnt)

        cv2.circle( tela, (x_bola+w_bola//2, y_bola+h_bola//2), 3, (0,0,255), -1)
        cv2.rectangle( tela, (x_bola, y_bola), (x_bola + w_bola, y_bola + h_bola), (0, 255, 0), 0 )
        cv2.putText( tela, tag, (x_bola+40,y_bola-15), fonte, 0.8, (255,255,0), 2, cv2.LINE_AA )
        cv2.putText( tela, tag+f'({a_max})', (x_bola+40,y_bola-15), fonte, 0.8, (255,255,0), 2, cv2.LINE_AA )

        if(tag == "bola"):
            (x,y),radius = cv2.minEnclosingCircle(cnt)
            center = (int(x),int(y))
            radius = int(radius)
            cv2.circle(tela,center,radius,(0,0,255),2)
        else:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(tela,[box],0,(0,0,255),2)
            #print(f'Box {tag}: {box}')

            #Box verde: [[186 212] [210 196] [226 221] [202 237]]
    
    return cnt_list


# ===========  Detecção da posição e orientação  ============= #
def cnt_box(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    return np.int0(box)

def cnt_point_list(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    return np.int0(box)

def dist_elements( R, A ):
    Col = A.shape[0]*R.shape[0]
    R2 = np.kron( R, np.ones((A.shape[0],1)) ) #print(REF)
    A2 = np.kron( np.ones((R.shape[0],1)), A )   #print("A2",A2)
    D = ( ((A2-R2)**2)@np.ones((2,1)) )**0.5
    N = np.arange(Col).reshape((Col,1))
    Dots = np.concatenate( ( N, R2, A2, D ), axis=1 )
    Dots = Dots[ Dots[:,5].argsort() ]
    #plt.plot( A.T[0], A.T[1], 'o' )
    #plt.plot( R.T[0], R.T[1], 'o' )
    #for i in range(1): plt.plot( [ Dots[i][1],Dots[i][3] ], [ Dots[i][2],Dots[i][4] ] )
    return Dots

def modulo(a):
    return ( (a**2)@np.array([[1],[1]]) )**0.5

def rect_data(A,tela=0):
    REF = A[0:1,:]
    M_REF = np.kron( REF, np.ones((4,1)) )
    A_ref = A-M_REF
    D_ref = modulo(A_ref)
    
    A_sort = np.concatenate( (D_ref,A), axis=1 )
    A_sort = A_sort[ A_sort[:,0].argsort() ]

    H = A_sort[1][0]
    W = A_sort[2][0]

    Vy = 0.5*(A_sort[1:2,1:]+REF) # min (lado menor)
    Vx = 0.5*(A_sort[2:3,1:]+REF) # mid (lado maior)
    
    CENTER = 0.5*(A_sort[3:4,1:]+REF) # max (diagonal)
    u = Vx-CENTER
    u = u/modulo(u) # Vetor diretor

    #print(f'H:{H}  W:{W}')
    #print(f'Center: {CENTER}')
    #print(f'Vx: {Vx}')
    #print(f'Vy: {Vy}')
    #print(f'Vetor diretor u: {u}')

    if( not (tela is 0) ):
        cv2.arrowedLine(tela,
                        (int(CENTER[0][0]),int(CENTER[0][1])),
                        (int(3*H*u[0][0]+CENTER[0][0]),int(3*H*u[0][1]+CENTER[0][1])),
                        (0,0,255),
                        2,
                        tipLength = 0.1)

    
    return [ CENTER, W, H, u ]

#p_ref: [
#           [array([[523. , 359.5]]), 66.60330322138685, 34.713109915419565, array([[-0.74899656,  0.66257388]])],
#           [array([[321.5, 299.5]]), 77.4919350642375, 35.11409973215888, array([[-0.93979342,  0.34174306]])]
# ]
#p_2: [
#       [array([[538.5, 322.5]]), 31.240998703626616, 29.832867780352597, array([[-0.77096175,  0.63688145]])],
#       [array([[280., 294.]]), 35.4400902933387, 33.52610922848042, array([[-0.95447998,  0.29827499]])]
# ]

# cordenadas de "p" em relação a um versor (v) e um ponto de origem (c). o sentido v equivale a x e jv a y.
def ref_cord( v, c, p ):
    #c = np.array(c)#.reshape((1,2))
    v = np.array(v).reshape((1,2))@np.array([[1],[1j]])
    v = v/np.abs(v)
    p = np.array(p).reshape((1,2))@np.array([[1],[1j]])
    c = np.array(c).reshape((1,2))@np.array([[1],[1j]])

    #arrow( [c,0,10,v], tela )
    
    p = (1j*(p-c)/v)[0][0]
    return [np.real(p),np.imag(p)]

def rot_matrix( a ):
    return np.array( [[np.c1os(a),-np.sin(a)],[np.sin(a),np.cos(a)]] )


def imag_xy(a):
    return a@np.array([[1],[1j]])
def xy_imag(a):
    return np.concatenate( (np.real(a),np.imag(a)), axis=1)

def box_2_cnt( R ):
    C = imag_xy(R[0])
    V = imag_xy(R[3])
    H = R[1]
    W = R[2]
    cnt = C + V*0.5*( np.array( [[1,1],[1,-1],[-1,1],[-1,-1]] )@np.array( [[H],[1j*W]] ) )
    cnt = xy_imag(cnt)
    #plt.plot( cnt.T[0], cnt.T[1], "o"  )
    return cnt

def arrow( R, tela, cor = (0,255,0) ):
    CENTER = np.int0(R[0][0])
    CENTER = (CENTER[0],CENTER[1])
    u = R[3][0]
    H = R[2]
    END = (int(2*H*u[0]+CENTER[0]),int(2*H*u[1]+CENTER[1]))

    #print( f"Center:{CENTER} to END:{END}" )
    #print( f"H:{H} to u:{u}" )

    tela = cv2.arrowedLine(tela, CENTER, END, cor, 2, tipLength = 0.1)


# D verde by ref[0]: [[263.55564483760094, 570.6521661491768], [66.15053411413703, 400.5802041440981]]
# D verde by ref[1]: [[175.65147153635814, 603.8921800441104], [5.743297087074922, 406.34607844928775]]

# D verde by ref[1]: [[175.24878025866832, 603.5694429323189], [5.717063553147, 406.3551000693343]]
# D verde by ref[0]: [[263.7995162037672, 569.8057131035855], [66.41359572398414, 400.5572318804184]]

# D verde by ref[1]: [[175.11583904768761, 603.3556488973762], [5.395373818003094, 406.3754121165778]]

# D verde by ref[1]: [[175.04255336660856, 603.448867862247], [5.688214217314368, 406.00936368107796]]
# D verde by ref[0]: [[262.8242212443897, 570.3706987310231], [66.0036911926033, 400.29739409407]]

# D verde by ref[1]: [[175.04255336660856, 603.448867862247], [5.688214217314368, 406.00936368107796]]

def global_orientation( tela, cnt_ref, cnt_2, type = "rect" ):
    box_data_ref = [ rect_data(np.array(cnt_box(cnt))) for cnt in cnt_ref ]
    box_data_2   = [ rect_data(np.array(cnt_box(cnt))) for cnt in cnt_2   ]

    verde = []
    
    if( len(box_data_ref) and len(box_data_2) ):
        for i,R in enumerate(box_data_ref):
            # Cordenadas do ponto verde em relação ao retangulo azul
            box_2_cord_ref = np.array( [ ref_cord(R[3],R[0],p[0]) for p in box_data_2 ] )
            #print( f"[{i}] verde cordenadas by ref: { box_2_cord_ref }" )

            # Erro entre o esperado e o real
            typical_dist = np.array( [17,38] )
            erro = np.array( [ np.sum( np.abs([np.abs(p)-typical_dist]) ) for p in box_2_cord_ref ] )
            print( f"[{i}] verde ERRO: {erro}" )

            # Retangulo verde com menor erro
            N = np.argmin( erro )
            ref_verde = box_2_cord_ref[N]
            verde += [ref_verde]
            print( f"[{i}] verde by ref[{i}]: {ref_verde}" )

            # Centro do retangulo
            C = np.int0(box_data_2[N][0][0])
            #print(C)
            C = ( C[0], C[1] )

            if( i == 0 ): cv2.circle( tela, C, 10, (0,255,0), 2) # 0 -> Green
            else: cv2.circle( tela, C, 10, (255,0,0), 2) # 1 -> Blue

            d = ref_verde[1]

            if( d < 0 ): box_data_ref[i][3] = -box_data_ref[i][3]

            box_data_ref[i][0] = box_data_ref[i][0] + 0.5*abs(d)*box_data_ref[i][3]
            box_data_ref[i][2] = abs(d)+box_data_ref[i][2]
            box_data_ref[i][1] = box_data_ref[i][2]

    
    for i,R in enumerate(box_data_ref):
        arrow( R, tela )
        cv2.drawContours(tela,[np.int0(box_2_cnt(R))],0,(255,0,255),2)
        if( i < len(verde) ):
            cv2.putText( tela, f'[{i}]: {verde[i]} {modulo(verde[i])}', (0,400+40*i), fonte, 0.5, (0,0,255), 1, cv2.LINE_AA )
    
    return box_data_ref

            #rect_data(R,tela)
            #D = dist_elements(R,p2)
            #print(f"D0: {D[0]}")
    #    np.concatenate( (R,R), axis=0 )
    #    np.kron( np.identity(4), R )