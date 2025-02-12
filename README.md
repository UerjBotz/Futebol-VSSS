# FUTDERJ
Time de futebol de robôs VSS (_Very Small Size Soccer_) da UERJBotz.

# Iniciando
O gerenciamento do time (o chamado "alto nível") roda em python enquanto o firmware dos robôs é escrito em c++ usando a IDE do Arduino.

No momento, o hardware necessário para replicar o projeto são 3 Vespas para os robôs e um esp32 comum para o transmissor (+ motores, baterias, o computador, a câmera etc).

## Alto nível

Recomendamos o uso de um ambiente virtual python.
Inicializamos a pasta do ambiente virtual com o nome `.venv`.

### Requerimentos
- Linux
- Python 3.12.3

### Dependências
```
pip install -r requirements.txt
```

# Uso
Rode:
```
python3 main.py [y/b] # dependendo da cor do time
```
Se usando venv, como descrito, pode-se também rodar:
```
./main.py [y/b] # dependendo da cor do time
```

Além disso, os módulos `transmissor` e `controle` podem também ser usados como scripts realizando versões de linha de comando das suas respectivas funções.

