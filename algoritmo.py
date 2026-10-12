# algoritmo.py
# PROCESSAMENTO: algoritmo de gerenciamento de energia da estacao.
#
# ESTRATEGIA: divisao proporcional com prioridade por bateria
#   1. Se a energia disponivel cobre a demanda -> todos recebem 100% (ATIVA)
#   2. Se nao cobre -> a energia e dividida proporcionalmente ao pedido
#      de cada veiculo (REDUZIDA)
#   3. Se alguma fatia ficar abaixo da POTENCIA_MINIMA, o veiculo com a
#      bateria MAIS CHEIA (o menos urgente) vai para ESPERA e a divisao
#      e refeita entre os que sobraram.
#
# Todas as contas usam numeros INTEIROS: o processador do Pico (ARM Cortex-M0+)
# nao tem unidade de ponto flutuante (FPU), entao contas com inteiros sao mais rapidas.
# A divisao inteira (//) arredonda para baixo, garantindo que a soma liberada
# NUNCA passe da energia disponivel.

from veiculos import ATIVA, REDUZIDA, ESPERA, CHEIA

# Abaixo deste valor a recarga nao vale a pena (carregadores reais tem uma corrente minima)
POTENCIA_MINIMA = 1000  # W


def distribuir_energia(veiculos, energia):
    """Decide quanto cada veiculo recebe. Altera os dados dos veiculos na memoria
    e devolve uma lista de textos explicando cada decisao tomada."""
    decisoes = []

    # ---- Passo 0: quem precisa carregar? ----
    candidatos = []
    for v in veiculos:
        v["recebida"] = 0
        if v["bateria"] >= 100:
            v["estado"] = CHEIA
        else:
            v["estado"] = ESPERA      # todos comecam em espera ate o algoritmo liberar
            candidatos.append(v)

    # ---- Prioridade: menor bateria primeiro ----
    candidatos.sort(key=lambda v: v["bateria"])

    while candidatos:
        demanda = 0
        for v in candidatos:
            demanda += v["solicitada"]

        # ---- Passo 1: energia suficiente para todos ----
        if energia >= demanda:
            for v in candidatos:
                v["recebida"] = v["solicitada"]
                v["estado"] = ATIVA
            decisoes.append("Energia {} W >= demanda {} W: todos recebem 100%".format(energia, demanda))
            break

        # ---- Passo 2: divisao proporcional ----
        fatias = []
        for v in candidatos:
            fatias.append(v["solicitada"] * energia // demanda)
        percentual = energia * 100 // demanda

        if min(fatias) >= POTENCIA_MINIMA:
            for i in range(len(candidatos)):
                candidatos[i]["recebida"] = fatias[i]
                candidatos[i]["estado"] = REDUZIDA
            decisoes.append("Energia {} W < demanda {} W: cada um recebe {}% do pedido".format(
                energia, demanda, percentual))
            break

        # ---- Passo 3: fatia pequena demais -> o menos urgente espera ----
        sai = candidatos.pop()  # ultimo da lista = maior bateria
        decisoes.append("Dividindo {} W, a menor fatia seria {} W (< {} W). {} ({}%) vai para espera".format(
            energia, min(fatias), POTENCIA_MINIMA, sai["id"], int(sai["bateria"])))

    if not candidatos:
        decisoes.append("Nenhum veiculo em recarga")

    return decisoes


def status_estacao(veiculos):
    """Resume a situacao geral da estacao."""
    estados = [v["estado"] for v in veiculos]
    if ESPERA in estados:
        return "RECARGA LIMITADA"
    if REDUZIDA in estados:
        return "RECARGA CONTROLADA"
    if ATIVA in estados:
        return "RECARGA ATIVA"
    return "ESTACAO OCIOSA"
