import os
import time
import re
from datetime import datetime, timedelta

# ===========================
# VALIDADE DO SCRIPT
# ===========================

validade = datetime(2027, 2, 10)
agora = datetime.now()
dias_restantes = (validade - agora).days
if agora > validade:
    print(f"Script expirado em {validade.strftime('%d/%m/%Y')}. Encerrando...")
    time.sleep(20)
    exit()
if dias_restantes <= 5:
    print(
        f"Irá expirar em {dias_restantes} dia(s) "
        f"({validade.strftime('%d/%m/%Y')})."
    )
    time.sleep(10)

# ===========================
# CONFIGURAÇÕES
# ===========================

ARQUIVOS_PROBLEMA = r"B:\...\Arq"
DIAS_VERIFICADOS = 1
TEMPO_AUSENTE = 120

v_fixa = {
    "L": 5620,
    "A": 1200,
    "R": 700,
    "V": 500
}

faixa = [
    ((0.00, 1.00), {"L": 5200,
     "A": 4160, "R": 3120, "V": 2080}),
    # mais linhas
]


def expe(conteudo):
    for linha in conteudo:
        match = re.search(r"exp\s*([\d.,]+)", linha)
        if match:
            valor = match.group(1).replace(",", ".")
            try:
                return float(valor)
            except ValueError:
                return None
    return None


def faxa_velu(exp):
    for (min_val, max_val), velocidades in faixa:
        if min_val <= exp <= max_val:
            return velocidades
    return None


def alterar_arquivo(arquivo_path):
    try:
        with open(arquivo_path, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.readlines()

        expoor = expe(conteudo)
        if expoor is None:
            return False

        v_nova = faxa_velu(expoor)
        if v_nova is None:
            return False

        alterado = False
        alteracoes = set()

        for i, linha in enumerate(conteudo):
            for cor, vel_fixa in v_fixa.items():
                antigo = f"F{vel_fixa:.3f}"
                novo = f"F{v_nova[cor]:.3f}"
                if antigo in linha:
                    conteudo[i] = linha.replace(antigo, novo)
                    alterado = True
                    alteracoes.add((antigo, novo))

        if alterado:
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                f.writelines(conteudo)

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] {os.path.basename(arquivo_path)} _ Alterações feitas:")
            for ant, nov in alteracoes:
                print(f"            {ant} => {nov}")
            print()
            return True
        return False

    except Exception as e:
        print(f"[ERRO ao processar {arquivo_path}] {e}")
        return False


def arq_p_dt(pasta, DIAS_VERIFICADOS=DIAS_VERIFICADOS):
    limite = datetime.now() - timedelta(days=DIAS_VERIFICADOS)
    arquivos = []

    if not os.path.exists(pasta):
        print(f"[ERRO] CADE A PASTA O ANIMAL???: {pasta}")
        return arquivos

    for nome in os.listdir(pasta):
        if nome.lower().endswith('.cnc'):
            caminho = os.path.join(pasta, nome)
            modificado_em = datetime.fromtimestamp(os.path.getmtime(caminho))
            if modificado_em >= limite:
                arquivos.append(caminho)
    return arquivos


def monitorar():
    print("...\n")

    inicio_programa = time.time()
    ultimo_evento = inicio_programa
    aviso_enviado = False

    while True:
        try:
            houve_alteracao = False

            arquivos = arq_p_dt(ARQUIVOS_PROBLEMA, DIAS_VERIFICADOS)
            if arquivos:
                for caminho in arquivos:
                    if alterar_arquivo(caminho):
                        houve_alteracao = True

            agora = time.time()

            if houve_alteracao:
                ultimo_evento = agora
                aviso_enviado = False

            if not aviso_enviado and agora - ultimo_evento >= TEMPO_AUSENTE:
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] A mimir, nao tem alteracao...\n"
                )
                aviso_enviado = True

            time.sleep(5)

        except Exception as e:
            print(f"[ERRO geral] {e}")
            time.sleep(30)


if __name__ == "__main__":
    monitorar()
