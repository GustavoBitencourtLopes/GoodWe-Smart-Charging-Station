# interface.py
# SAIDAS DO SISTEMA: LEDs, display LCD (via I2C) e Monitor Serial.

from machine import Pin, I2C
from lcd_i2c import LcdI2C
from veiculos import ATIVA, REDUZIDA, ESPERA, NOME_ESTADO, NOME_LCD

# ---------------- LEDs ----------------
# Um trio (verde, amarelo, vermelho) para cada veiculo, na mesma ordem da lista
LEDS = [
    (Pin(6, Pin.OUT), Pin(7, Pin.OUT), Pin(8, Pin.OUT)),     # EV1
    (Pin(9, Pin.OUT), Pin(10, Pin.OUT), Pin(11, Pin.OUT)),   # EV2
    (Pin(12, Pin.OUT), Pin(13, Pin.OUT), Pin(14, Pin.OUT)),  # EV3
]

# ---------------- LCD (barramento I2C) ----------------
ENDERECO_LCD = 0x27  # endereco do LCD no barramento I2C (hexadecimal)
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
encontrados = i2c.scan()
print("I2C encontrou:", [hex(e) for e in encontrados])
if ENDERECO_LCD not in encontrados:
    print("ERRO: LCD nao encontrado no endereco 0x27. Confira o diagram.json (SDA=GP4, SCL=GP5).")
lcd = LcdI2C(i2c, ENDERECO_LCD, 4, 20)


def atualizar_leds(veiculos):
    """Acende o LED que corresponde ao estado de cada veiculo."""
    for i, v in enumerate(veiculos):
        verde, amarelo, vermelho = LEDS[i]
        estado = v["estado"]
        verde.value(1 if estado == ATIVA else 0)
        amarelo.value(1 if estado == REDUZIDA else 0)
        vermelho.value(1 if estado == ESPERA else 0)
        # estado CHEIA: os tres LEDs ficam apagados


def lcd_pagina_veiculos(cabecalho, veiculos):
    """PAGINA 1 do LCD. Linha 0: modo e energia. Linhas 1 a 3: um veiculo por linha.
    Exemplo: 'CEN 2 5000W/7500W' e 'EV1  20% 1333W REDUZ'."""
    lcd.escrever_linha(0, cabecalho)
    for i, v in enumerate(veiculos):
        linha = "{} {:>3}% {:>4}W {}".format(
            v["id"], int(v["bateria"]), int(v["recebida"]), NOME_LCD[v["estado"]])
        lcd.escrever_linha(i + 1, linha)


def lcd_pagina_dados(status, energia):
    """PAGINA 2 do LCD: status da estacao e a energia em decimal, hexadecimal e binario."""
    energia = int(energia)
    lcd.escrever_linha(0, status)
    lcd.escrever_linha(1, "DEC {} W".format(energia))
    lcd.escrever_linha(2, "HEX 0x{:04X}".format(energia))
    lcd.escrever_linha(3, "BIN {:b}".format(energia))


def mostrar_serial(titulo, energia, demanda, status, veiculos, decisoes=None):
    """Imprime uma tabela completa no Monitor Serial, com as decisoes do algoritmo."""
    print()
    print("=" * 66)
    print(titulo)
    print("Energia disponivel: {} W | Demanda total: {} W".format(energia, demanda))
    print("Status da estacao: {}".format(status))
    if decisoes:
        print("Decisoes do algoritmo:")
        for d in decisoes:
            print("  -> " + d)
    print("-" * 66)
    print("{:<5}{:>9}{:>12}{:>12}   {}".format("EV", "Bateria", "Pedida", "Recebida", "Estado"))
    total = 0
    for v in veiculos:
        total += int(v["recebida"])
        print("{:<5}{:>8}%{:>10} W{:>10} W   {}".format(
            v["id"], int(v["bateria"]), v["solicitada"], int(v["recebida"]),
            NOME_ESTADO[v["estado"]]))
    print("Total liberado: {} W de {} W disponiveis".format(total, energia))
