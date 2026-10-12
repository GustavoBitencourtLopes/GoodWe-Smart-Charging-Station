# veiculos.py
# MEMORIA DO SISTEMA
# Aqui ficam os dados de cada veiculo conectado a estacao.
# Durante a execucao, essas informacoes ficam guardadas na memoria RAM (SRAM)
# do Raspberry Pi Pico, que tem 264 KB.

# ---------------- Estados da recarga ----------------
# Cada estado e guardado como um numero inteiro (0 a 3).
# 4 estados cabem em apenas 2 bits: 00, 01, 10 e 11.
ATIVA = 0      # recebe 100% do que pediu         -> LED verde
REDUZIDA = 1   # recebe menos do que pediu        -> LED amarelo
ESPERA = 2     # nao recebe energia (aguardando)  -> LED vermelho
CHEIA = 3      # bateria em 100%, nao precisa     -> LEDs apagados

# O numero do estado e usado como posicao (indice) nestas listas:
NOME_ESTADO = ["RECARGA ATIVA", "RECARGA REDUZIDA", "AGUARDANDO", "BATERIA CHEIA"]  # Serial
NOME_LCD = ["ATIVA", "REDUZ", "PAUSA", "CHEIA"]  # LCD (so cabem 5 letras)

# ---------------- Dados iniciais da simulacao ----------------
# (identificacao, bateria em %, potencia solicitada em W)
DADOS_INICIAIS = [
    ("EV1", 20, 2000),
    ("EV2", 50, 2500),
    ("EV3", 80, 3000),
]


def criar_veiculos():
    """Monta a lista de veiculos a partir dos dados iniciais.
    E chamada no inicio e sempre que um cenario for reiniciado."""
    veiculos = []
    for identificacao, bateria, potencia in DADOS_INICIAIS:
        veiculos.append({
            "id": identificacao,
            "bateria": bateria,       # nivel da bateria (%)
            "solicitada": potencia,   # potencia que o carro pede (W)
            "recebida": 0,            # potencia liberada pelo controlador (W)
            "estado": ESPERA,         # comeca aguardando ate o algoritmo decidir
        })
    return veiculos


def demanda_total(veiculos):
    """Soma a potencia pedida pelos veiculos que ainda precisam carregar."""
    total = 0
    for v in veiculos:
        if v["bateria"] < 100:
            total += v["solicitada"]
    return total
