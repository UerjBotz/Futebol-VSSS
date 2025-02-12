import cv2   as cv
import numpy as np

from cmath import polar
from dataclasses import dataclass, field

from comum import *

def plot_arrow(img, center, v, hue=0):
    cv.arrowedLine(
        img,
        (center[0], center[1]),
        (v[0] + center[0], v[1] + center[1]),
        (hue, 255, 255),
        3,
        tipLength=0.2,
    )


def rect_coord(P: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    P = (P @ np.array([[1], [1j]]))[:, 0]
    center = np.mean(P)

    d = P - P[0]
    D = abs(d)
    sort = (-D).argsort()
    d = d[sort] # Dists ord.
    D = D[sort] # Dists ord.
    v = d[2] / D[2]

    return (np.array([center.real, center.imag], np.int64),
            np.array([v.real, v.imag], np.float64),
            np.array(D[1:3], np.int64))


def filtra_contornos(mask: np.ndarray, A_min: int, qtd_formas: int=0) -> tuple[np.ndarray, np.ndarray]:
    # Contornos
    contornos, _ = cv.findContours(mask, cv.RETR_TREE,
                                   cv.CHAIN_APPROX_SIMPLE)
    cnt_list = []
    area_list = []

    # Verificação dos contornos
    for cnt in contornos:
        area = cv.contourArea(cnt)
        if area > A_min:
            area_list += [area]
            cnt_list += [cnt]

    area_list = np.array(area_list)
    sort = (-area_list).argsort()
    cnt_list = [cnt_list[i] for i in sort]
    area_list = area_list[sort]

    if qtd_formas != 0:
        cnt_list  = cnt_list[:qtd_formas]
        area_list = area_list[:qtd_formas]

    return (cnt_list, area_list)


def match_contours(contours, shape="rect", tela=None): #TODO: tipos (principalmente saída)
    center_list = []
    dimension_list = []
    vector_list = []
    box_list = []
    for cnt in contours:
        if shape == "circle":
            center, radius = cv.minEnclosingCircle(cnt)
            dimension = np.array([int(radius), int(radius)], np.uint32)
            vector = np.array([0, 0], np.uint32)
            rect = cv.minAreaRect(cnt)
            box = np.intp(cv.boxPoints(rect))
            center = np.array(center, np.uint32)
            if tela is not None:
                cv.circle(tela, center,int(radius),(0,0,255),2)
        elif shape == "rect":
            rect = cv.minAreaRect(cnt)
            box = np.intp(cv.boxPoints(rect))
            center, vector, dimension = rect_coord(box)
            if tela is not None:
                plot_arrow(tela, center, np.array(50 * vector, np.int32))
        else: assert False

        vector_list += [vector]
        dimension_list += [dimension]
        center_list += [center]
        box_list += [box]
    return (center_list, dimension_list, vector_list, box_list)


def link_0(R, points, colors, v, dimension,
           tag=("black", "black"), tela=None, delta=10
) -> tuple[complex, tuple[str,str], complex]: # TODO: nome horrível, mudar. + tipos

    L_ref = 32.5 + 17.5j
    k = (dimension.real / 65 + dimension.imag / 30) / 2
    Z = k * L_ref

    if tela is not None:
        cv.circle(tela, complex_to_xy(R), 2, (55, 255, 255), 2)
        cv.circle(tela, complex_to_xy(R), 3, (151, 255, 255), 2)
        p1 = R + v * Z
        p2 = R + v * (Z.conj())
        cv.circle(tela, complex_to_xy(p1), 2, (55, 255, 255), 2)
        cv.circle(tela, complex_to_xy(p1), 3, (151, 255, 255), 2)
        cv.circle(tela, complex_to_xy(p2), 2, (55, 255, 255), 2)
        cv.circle(tela, complex_to_xy(p2), 3, (151, 255, 255), 2)
        p1 = R - v * Z
        p2 = R - v * (Z.conj())
        cv.circle(tela, complex_to_xy(p1), 2, (55, 255, 255), 2)
        cv.circle(tela, complex_to_xy(p1), 3, (151, 255, 255), 2)
        cv.circle(tela, complex_to_xy(p2), 2, (55, 255, 255), 2)
        cv.circle(tela, complex_to_xy(p2), 3, (151, 255, 255), 2)

    P = points
    T = (P - R) / v

    nota = abs(abs(T.real) - Z.real) + abs(abs(T.imag) - Z.imag)

    filtro = nota < delta
    nota = nota[filtro]
    colors = colors[filtro]
    T = T[filtro]

    filtro = nota.argsort()
    nota = nota[filtro]
    colors = colors[filtro]
    T = T[filtro]

    # decide quais os pontos escolhidos
    center = R
    for i, p in enumerate(T):
        A = T[i + 1 :] - p.conj()
        filtro = abs(A) < delta

        if True in filtro:
            c1 = colors[i]
            c2 = colors[i + 1 :][filtro][0]
            center = (p + T[i + 1 :][filtro][0]) / 4
            center = center * v + R
            v = center - R
            v = v / abs(v)
            if (p.real > 0) == (p.imag > 0):
                tag = (c1, c2)
            else:
                tag = (c2, c1)
            break

    cv.circle(tela, complex_to_xy(center), 3, (0, 255, 255), 2)
    cv.circle(tela, complex_to_xy(center), 30, (120, 255, 255), 2)
    plot_arrow(tela, complex_to_xy(center), complex_to_xy(50 * v), hue=60)

    # print( ' FIM tentativas ', tag )

    return (center, tag, v)


def sort_bots(dic: dict[int, dict]):
    a = sorted(dic.items(), key=lambda bot: bot[0])
    return {b[0]: b[1] for b in a}


matriz = np.ndarray
def inrange(A: matriz, h_min, h_max, s_min, v_min):
    C = np.logical_and(
        np.logical_and(A[:, :, 0] > h_min, A[:, :, 0] < h_max),
        np.logical_and(A[:, :, 1] > s_min, A[:, :, 2] > v_min),
    )
    return np.array(C, np.uint8)

@dataclass #! kw_only
class vision_conf():
    v_min:    int
    s_min:    int
    area_min: int
    delta:    int
    colors:   dict[str, dict[str, int]] # TODO: melhorar isso
    
    @staticmethod
    def from_dict(vs_in, vs_colors):
        return vision_conf(
            v_min    = vs_in["V min"],
            s_min    = vs_in["S min"],
            area_min = vs_in["area min"],
            delta    = vs_in["delta"],
            colors   = vs_colors,
        )

@dataclass(kw_only=True)
class ball_info():
    ok:        bool
    pos:       complex
    dimension: complex

@dataclass
class bot_info():
    id:          int
    pos:         complex
    orientation: float
    dimension:   complex
    vector:      complex
    colors:      tuple[str, str] # TODO: na verdade costuma ser uma lista (melhor mudar nos outros lugares do que aqui

@dataclass
class vision_info():
    ball:  ball_info = field(
        default_factory=lambda: ball_info(ok=False, pos=0, dimension=0)
    )
    teams: dict[str, dict[int, bot_info]] = field(
        default_factory=lambda: dict(team_yellow={}, team_blue={})
    )


def vision(img: np.ndarray, cfg: vision_conf, conv: int, desenhar=False) -> tuple[vision_info, dict]:
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # -------------------------------------------------------------------
    # OBTENÇÃO DAS INFORMAÇÕES DE CADA COR ------------------------------
    # CENTRO / VETOR DIRETOR / DIMENSÕES   ------------------------------
    # -------------------------------------------------------------------
    data_center = {}
    data_vector = {}
    data_dimension = {}
    # UMA COR DE CADA VEZ -----------------------------------------------

    tela = img.copy() if desenhar else None
    color_img = np.zeros(img.shape, np.uint8)

    for i, color in enumerate(cfg.colors["MEAN"]):
        # MASK ----------------------------------------------------------
        if cfg.colors["MIN"][color] < cfg.colors["MAX"][color]:
            mask = cv.inRange(
                hsv,
                (cfg.colors["MIN"][color], cfg.s_min, cfg.v_min),
                (cfg.colors["MAX"][color], 255, 255),
            )
        else:
            mask = cv.inRange(
                hsv, (cfg.colors["MIN"][color], cfg.s_min, cfg.v_min), (180, 255, 255)
            )
            mask |= cv.inRange(
                hsv, (0, cfg.s_min, cfg.v_min), (cfg.colors["MAX"][color], 255, 255)
            )
        color_img[np.array(mask, np.bool)] = [cfg.colors["MEAN"][color], 255, 255]
        # MASK ----------------------------------------------------------

        # OBTENÇÃO DAS INFORMAÇÕES DE CADA COR --------------------------
        # CENTRO / VETOR DIRETOR / DIMENSÕES   --------------------------
        if   color == "darkblue" or color == "yellow":
            shape = "rect"
            qtd_formas = 3
        elif color == "orange":
            shape = "circle"
            qtd_formas = 1
        else:
            shape = "rect"
            qtd_formas = 0

        contornos, area = filtra_contornos(mask, 5*cfg.area_min, qtd_formas) #! '5*'area_min???????
        center, dimension, vector, box = match_contours(
            contornos, shape=shape, tela=tela
        )

        data_center[color] = xy_to_complex(center)
        data_vector[color] = xy_to_complex(vector)
        data_dimension[color] = xy_to_complex(dimension)
        # ---------------------------------------------------------------

        # MARCAÇOES NA TELA ---------------------------------------------
        if desenhar:
            # cv.drawContours( hsv, contornos, -1, (color_hue_mean[i],255,255), 0 )
            if color == "orange" and len(center) > 0:
                cv.circle(tela, center[0], 5, (60, 255, 255), 2)
                cv.circle(tela, center[0], dimension[0][0], (60, 255, 255), 2)
                cv.circle(color_img, center[0], dimension[0][0], (60, 255, 255), 2)
            else:
                for p in center:
                    cv.circle(tela, p, 5, (cfg.colors["MEAN"][color], 255, 255), 2)
                for b in box:
                    cv.drawContours(tela, [b], 0, (cfg.colors["MEAN"][color], 255, 255), 2)

    # -------------------------------------------------------------------
    # SEGMENTAÇÃO DOS DADOS DE COR --------------------------------------
    # ORIENTAÇÃO GLOBAL ROBÔS E BOLA  -----------------------------------
    # -------------------------------------------------------------------

    game = vision_info()

    # Bola --------------------------------------------------------------
    if len(data_center["orange"]):
        game.ball = ball_info(
            ok=True,
            pos=data_center["orange"][0]*conv,
            dimension=data_dimension["orange"][0]*conv,
        )
    # -------------------------------------------------------------------

    # TRANSFORMA EM NUMPY ARRAY PARA FACILITAR O PROCESSAMENTO ----------
    SEG_COLORS = []
    SEG_POINTS = []
    for color in ("red", "blue", "green", "pink"): # TODO: tenho a impressão que isso aqui era meia linha só e tá 5
        SEG_COLORS = np.append(SEG_COLORS, np.array(len(data_center[color]) * [color]))
        SEG_POINTS = np.append(SEG_POINTS, np.array(data_center[color]))
    # -------------------------------------------------------------------

    tag2number = {
        "darkblue": 0,
        "yellow": 0,
        "red": 1,
        "green": 2,
        "blue": 3,
        "pink": 4,
    }
    # TODO: tirar esse if e fazer uma tuplatupla que nem naquele outro
    # SEGMENTAÇÕES DOS ROBÔS UM DE CADA VEZ -----------------------------
    for team in ("darkblue", "yellow"):
        gen_id = 50 #TODO: oqq é isso (generated id?)
        team_key = "team_yellow" if team == "yellow" else "team_blue"

        for i, ref in enumerate(data_center[team][:3]):
            center, tag, v = link_0(
                ref,
                SEG_POINTS,
                SEG_COLORS,
                data_vector[team][i],
                data_dimension[team][i],
                tag=(team, team),
                tela=tela,
                delta=cfg.delta,
            )
            
            # TODO: melhorar essa partezinha
            id = 10 * tag2number[tag[0]] + tag2number[tag[1]]
            if id == 0: 
                id = gen_id
                gen_id += 1

            game.teams[team_key][id] = bot_info(
                id=id,
                pos=center*conv,
                colors=tag,
                orientation=polar(v)[1],
                vector=v,
                dimension=data_dimension[team][i] * conv,
            )

        game.teams[team_key] = sort_bots(game.teams[team_key])
        # TODO: esse sort_bots^ provavelmente deveria ser sorted([bot for id, bot in game.teams[team_key].items()], key=lambda bot: bot["id"])

    # ATUALIZA OS MONITORES ---------------------------------------------
    img_data = dict(vision=tela, colors=color_img) if desenhar else \
               dict(vision=img,  colors=color_img)
    # img_data['monitor_color'].update_hsv(color_img)
    # img_data['monitor_mask' ].update_hsv(tela)
    # -------------------------------------------------------------------
    return (game, img_data)

