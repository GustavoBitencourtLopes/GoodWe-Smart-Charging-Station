# lcd_i2c.py
# Driver simples para display LCD (HD44780) com modulo I2C (chip PCF8574).
# O LCD recebe os dados em "modo 4 bits": cada byte e enviado em 2 metades (nibbles).
# Bits do PCF8574: P0 = RS, P1 = RW, P2 = EN (enable), P3 = luz de fundo, P4..P7 = dados D4..D7
#
# ATENCAO: o LCD nao mostra acentos (a, c com cedilha etc.). Escreva sem acento.

import time


class LcdI2C:
    RS = 0x01         # 0b00000001 -> 0 = comando, 1 = caractere
    EN = 0x04         # 0b00000100 -> pulso que "confirma" o dado
    BACKLIGHT = 0x08  # 0b00001000 -> luz de fundo ligada

    def __init__(self, i2c, addr=0x27, linhas=4, colunas=20):
        self.i2c = i2c
        self.addr = addr
        self.linhas = linhas
        self.colunas = colunas
        time.sleep_ms(50)
        # Sequencia de inicializacao exigida pelo HD44780 para entrar em modo 4 bits
        for _ in range(3):
            self._escrever_nibble(0x30)
            time.sleep_ms(5)
        self._escrever_nibble(0x20)
        time.sleep_ms(1)
        self._comando(0x28)  # modo 4 bits, multiplas linhas, fonte 5x8
        self._comando(0x0C)  # display ligado, cursor desligado
        self._comando(0x06)  # cursor anda para a direita apos cada caractere
        self.limpar()

    def _enviar_pcf(self, dado):
        self.i2c.writeto(self.addr, bytes([dado | self.BACKLIGHT]))

    def _escrever_nibble(self, nibble, rs=0):
        dado = (nibble & 0xF0) | rs
        self._enviar_pcf(dado | self.EN)  # EN = 1
        self._enviar_pcf(dado)            # EN = 0 -> LCD le o dado

    def _escrever_byte(self, valor, rs):
        self._escrever_nibble(valor & 0xF0, rs)         # metade alta
        self._escrever_nibble((valor << 4) & 0xF0, rs)  # metade baixa

    def _comando(self, cmd):
        self._escrever_byte(cmd, 0)
        if cmd <= 3:
            time.sleep_ms(2)

    def limpar(self):
        self._comando(0x01)
        time.sleep_ms(2)

    def mover(self, coluna, linha):
        # Endereco de memoria (DDRAM) onde cada linha comeca num LCD 20x4
        inicio_linha = [0x00, 0x40, 0x14, 0x54]
        self._comando(0x80 | (inicio_linha[linha] + coluna))

    def escrever(self, texto):
        for ch in texto:
            self._escrever_byte(ord(ch), self.RS)

    def escrever_linha(self, linha, texto):
        # Escreve a linha inteira e completa com espacos (apaga o texto antigo)
        texto = texto[:self.colunas]
        self.mover(0, linha)
        self.escrever(texto + " " * (self.colunas - len(texto)))
