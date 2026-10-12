# representacao.py
# REPRESENTACAO DE DADOS: mostra como os numeros usados pelo sistema
# sao representados no computador (decimal, hexadecimal e binario),
# alem de informacoes do processador e da memoria do Raspberry Pi Pico.

import gc
import machine
from veiculos import NOME_ESTADO


def em_bases(numero):
    """Ex.: 5000 -> 'DEC 5000  | HEX 0x1388 | BIN 1001110001000 (13 bits)'"""
    numero = int(numero)
    binario = "{:b}".format(numero)
    return "DEC {:<5} | HEX 0x{:04X} | BIN {} ({} bits)".format(
        numero, numero, binario, len(binario))


def info_sistema():
    """Informacoes do hardware, mostradas quando o sistema liga."""
    gc.collect()
    print("-" * 66)
    print("Processador: RP2040 (dual-core ARM Cortex-M0+)")
    print("Frequencia do clock: {} MHz".format(machine.freq() // 1000000))
    print("Memoria RAM (SRAM) livre: {} bytes".format(gc.mem_free()))
    print("-" * 66)


def mostrar(energia, veiculos, leitura_adc=None, endereco_lcd=0x27):
    """Mostra no Monitor Serial os dados da sessao em varias bases numericas."""
    print("Representacao dos dados:")
    print("  Energia disponivel  : " + em_bases(energia))
    for v in veiculos:
        print("  Bateria {}         : ".format(v["id"]) + em_bases(v["bateria"]))
    for v in veiculos:
        print("  Estado {}          : DEC {} | BIN {:02b} -> {}".format(
            v["id"], v["estado"], v["estado"], NOME_ESTADO[v["estado"]]))
    print("  Endereco I2C do LCD : " + em_bases(endereco_lcd))
    if leitura_adc is not None:
        print("  Leitura do ADC (16b): DEC {} | HEX 0x{:04X} | BIN {:016b}".format(
            leitura_adc, leitura_adc, leitura_adc))
    gc.collect()
    print("  Memoria RAM livre   : {} bytes".format(gc.mem_free()))
    print("=" * 66)
