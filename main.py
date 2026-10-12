# main.py
# GoodWe Smart Charging Station - Sprint 4 (Arquitetura de Computadores)
#
# CICLO DO SISTEMA (repetido o tempo todo):
#   ENTRADA       -> le o botao e a energia disponivel
#   MEMORIA       -> dados dos veiculos ficam guardados na RAM (veiculos.py)
#   PROCESSAMENTO -> algoritmo decide a energia de cada veiculo (algoritmo.py)
#   SAIDA         -> LEDs, LCD e Monitor Serial (interface.py)
#
# CONTROLES:
#   Botao azul    -> troca o modo: CEN 1 -> CEN 2 -> CEN 3 -> SOLAR -> CEN 1 ...
#   Potenciometro -> no modo SOLAR, define a energia gerada (0 a 9000 W)

print("Iniciando GoodWe Smart Charging Station...")

import time
from machine import Pin, ADC
import interface
import representacao
from veiculos import criar_veiculos, demanda_total
from algoritmo import distribuir_energia, status_estacao

# ---------------- ENTRADAS ----------------
botao = Pin(16, Pin.IN, Pin.PULL_UP)   # solto = 1, apertado = 0
sensor_solar = ADC(Pin(26))            # potenciometro (simula a geracao solar)
led_placa = Pin(25, Pin.OUT)           # LED da propria placa: pisca = sistema rodando

# (rotulo no LCD, titulo no Serial, energia em W; None = vem do potenciometro)
MODOS = [
    ("CEN 1", "CENARIO 1 - ALTA DISPONIBILIDADE DE ENERGIA", 8000),
    ("CEN 2", "CENARIO 2 - DISPONIBILIDADE LIMITADA", 5000),
    ("CEN 3", "CENARIO 3 - BAIXA DISPONIBILIDADE DE ENERGIA", 2000),
    ("SOLAR", "MODO SOLAR - ENERGIA DEFINIDA PELO POTENCIOMETRO", None),
]
ENERGIA_MAX_SOLAR = 9000   # W
TEMPO_PAGINA_LCD = 4000    # ms que cada pagina do LCD fica na tela


def ler_energia_solar():
    """O ADC converte a tensao do potenciometro num numero de 0 a 65535.
    Esse numero e convertido para 0 a 9000 W, em passos de 100 W."""
    leitura = sensor_solar.read_u16()
    energia = (leitura * (ENERGIA_MAX_SOLAR // 100) // 65535) * 100
    return energia, leitura


representacao.info_sistema()
print("Aperte o botao azul para trocar de cenario.")

modo = 0
modo_anterior = -1
energia_anterior = -1
botao_anterior = 1
ultimo_clique = 0
pagina = 0
ultima_troca_pagina = time.ticks_ms()
ultimo_pisca = time.ticks_ms()
veiculos = criar_veiculos()
status = ""
demanda = 0
energia = 0

while True:
    agora = time.ticks_ms()
    atualizar_lcd = False

    # ---- 1. ENTRADA: botao (reage so no momento do clique, com debounce) ----
    leitura_botao = botao.value()
    if leitura_botao == 0 and botao_anterior == 1 and time.ticks_diff(agora, ultimo_clique) > 300:
        modo = (modo + 1) % len(MODOS)
        ultimo_clique = agora
    botao_anterior = leitura_botao

    # ---- 2. ENTRADA: energia disponivel ----
    rotulo, titulo, energia_fixa = MODOS[modo]
    leitura_adc = None
    if energia_fixa is None:
        energia, leitura_adc = ler_energia_solar()
    else:
        energia = energia_fixa

    # ---- 3. PROCESSAMENTO: so recalcula quando algo muda ----
    if energia != energia_anterior or modo != modo_anterior:
        veiculos = criar_veiculos()                       # MEMORIA: dados iniciais
        decisoes = distribuir_energia(veiculos, energia)  # algoritmo
        status = status_estacao(veiculos)
        demanda = demanda_total(veiculos)

        # ---- 4. SAIDAS ----
        interface.atualizar_leds(veiculos)
        interface.mostrar_serial(titulo, energia, demanda, status, veiculos, decisoes)
        representacao.mostrar(energia, veiculos, leitura_adc)

        energia_anterior = energia
        modo_anterior = modo
        pagina = 0
        ultima_troca_pagina = agora
        atualizar_lcd = True

    # ---- LCD alterna entre 2 paginas ----
    if time.ticks_diff(agora, ultima_troca_pagina) > TEMPO_PAGINA_LCD:
        pagina = 1 - pagina
        ultima_troca_pagina = agora
        atualizar_lcd = True

    if atualizar_lcd:
        if pagina == 0:
            cabecalho = "{} {:>4}W/{:>4}W".format(rotulo, energia, demanda)
            interface.lcd_pagina_veiculos(cabecalho, veiculos)
        else:
            interface.lcd_pagina_dados(status, energia)

    # ---- LED da placa pisca: mostra que o processador esta rodando ----
    if time.ticks_diff(agora, ultimo_pisca) > 500:
        led_placa.toggle()
        ultimo_pisca = agora

    time.sleep_ms(50)
