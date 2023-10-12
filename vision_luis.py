from time import sleep
from receptor import Client
from google.protobuf.json_format import MessageToDict


class vision:

  jogadores = {
      "robotsYellow": [{
          "x": 0,
          "y": 0,
          "orientation": 0,
          "valid": False
      } for i in range(3)],
      "robotsBlue": [{
          "x": 0,
          "y": 0,
          "orientation": 0,
          "valid": False
      } for i in range(3)]
  }

  robots_id = {"robotsYellow": [0, 1, 2], "robotsBlue": [0, 1, 2]}

  bola = {"x": 0, "y": 0, "orientation": 0, "valid": False}

  self.team = "robotsBlue"
  self.team_opposing = "robotsYellow"

  def __init__(self, vision_ip='224.5.23.2', vision_port=10321) -> None:
    self.vision_ip = vision_ip
    self.vision_port = vision_port
    self.vision_client = Client(self.vision_ip, self.vision_port)
    pass

  def set_blue_team(self) -> None:
    self.team = "robotsBlue"
    self.team_opposing = "robotsYellow"
    pass

  def set_yellow_team(self) -> None:
    self.team = "robotsYellow"
    self.team_opposing = "robotsBlue"
    pass

  def set_robots_id(self, team, ids) -> None:
    self.robots_id[team] = ids
    pass

  def get_pos_bot(self, id_bot):
    return (self.jogadores[self.team][id_bot]['x'],
            self.jogadores[self.team][id_bot]['y'],
            self.jogadores[self.team][id_bot]['orientation'])

  def get_pos_ball(self):
    return (self.bola['x'], self.bola['y'])

  def validation(self,
                 id):  # 0 a 2 robôs do time 3 a 5 robôs outro time 6 bola
    if (id == 6):
      return self.bola['valid']
    elif (id < 3):
      return self.jogadores[self.team][id]['valid']
    else:
      
        
      return self.jogadores[self.team][id]['valid']

  def update(self, data):
    data = MessageToDict(self.vision_client.receive_frame().detection)

    #print(data)

    # considera todos invalidos
    for i in range(3):
      self.jogadores['robotsYellow'][i]['valid'] = False
      self.jogadores['robotsBlue'][i]['valid'] = False

    # As chaves
    times = ['robotsYellow', 'robotsBlue']
    pos_arg = ['x', 'y', 'orientation', 'valid']

    # Zera os estados
    for time in times:  # atualiza cada time
      if time in data:  # verifica se o time foi enviado
        for i, jogador in enumerate(data[time]):  # atualiza cada jogador
          local_id = i
          if (self.team == time
              ):  # se for o proprio time precisa indexar o jogador
            local_id = -1  # simboliza invalido
            if ('robot_id' in jogador):
              if (jogador['robot_id'] in self.robots_id[self.team]):
                local_id = self.robots_id[self.team].index(jogador['robot_id'])
          if local_id >= 0:
            for key in pos_arg:  # atualiza cada atributo
              if key == 'valid':
                self.jogadores[time][local_id][key] = True
              elif key in data[time][
                  local_id]:  # verifica se o atributo existe
                self.jogadores[time][local_id][key] = jogador[key]
              else:
                break

    pos_arg = ['x', 'y', 'valid']
    if ('balls' in data):
      for key in pos_arg:  # atualiza cada atributo
        if key == 'valid':
          self.bola[key] = True
        elif key in data['balls']:  # verifica se o atributo existe
          self.bola[key] = data['balls'][key]
        else:
          break
    return (self.jogadores, self.bola)
