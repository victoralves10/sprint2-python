# Victor Alves Lopes RM561833

import os
import json
import oracledb
import pandas as pd
from datetime import datetime, date
from tabulate import tabulate

# ==========================================================
#   INSTRUÇÕES PARA EXECUTAR O PROGRAMA
# ==========================================================
# 1. Execute o comando SQL abaixo no 'Oracle SQL Developer' para criar as tabelas necessárias.
# 2. Instale as bibliotecas exigidas no terminal:
    # pip install oracledb
    # pip install tabulate
    # pip install pandas
    # ou pip install oracledb tabulate pandas

# ==========================================================
#   COMANDO SQL PARA ORACLE
# ==========================================================
"""
CREATE TABLE T_VEICULOS (
    id_veiculo INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo VARCHAR2(50) NOT NULL,
    marca VARCHAR2(100) NOT NULL,
    modelo VARCHAR2(100) NOT NULL,
    ano_fabricacao INT NOT NULL,
    placa VARCHAR2(10) NOT NULL UNIQUE,
    cor VARCHAR2(30),
    combustivel VARCHAR2(20),
    quilometragem INT DEFAULT 0,
    status VARCHAR2(20) DEFAULT 'Disponível',
    valor_diaria NUMBER(10, 2) NOT NULL,
    data_aquisicao DATE DEFAULT SYSDATE NOT NULL,
    data_cadastro TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    data_ultima_atualizacao TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE OR REPLACE TRIGGER trg_t_veiculos_atualizacao
BEFORE UPDATE ON T_VEICULOS
FOR EACH ROW
BEGIN
    :NEW.data_ultima_atualizacao := SYSTIMESTAMP;
END;
/
"""

# Após isso, o código estará pronto para ser executado.

# Execute o programa pelo arquivo principal: checkpoint6-python.py
# (no terminal: python checkpoint6-python.py)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# ==========================================================
#   SUBALGORITMOS
# ==========================================================

# ==========================================================
#   APRESENTAÇÃO
# ==========================================================

# limpa a tela do terminal dependendo do sistema.
def limpar_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")

# mostra um título centralizado com linhas decorativas em cima e embaixo.
def exibir_titulo_centralizado(_texto: str, _largura_caracteres: int) -> None:
    print("=-" * (_largura_caracteres // 2))
    print(_texto.center(_largura_caracteres))
    print("=-" * (_largura_caracteres // 2), "\n")

# imprime uma linha repetindo o símbolo que passar.
def imprimir_linha_separadora(simbolo: str, quantidade: int) -> None:
    print(f"{simbolo * quantidade}")

# ==========================================================
#   VALIDAÇÃO DE DADOS (TIPOS BÁSICOS)
# ==========================================================

# pede um texto pro usuário até ele digitar algo que não seja vazio.
def obter_texto(_mensagem: str) -> str:
    texto_entrada = None
    while not texto_entrada:
        texto_entrada = str(input(_mensagem)).strip()
        if not texto_entrada:
            print("\nErro! Digite novamente.\n")
    return texto_entrada

# pede um número inteiro até o usuário digitar certo.
def obter_inteiro(_mensagem: str) -> int:
    numero_inteiro = None
    while numero_inteiro is None:
        try:
            numero_inteiro = int(input(_mensagem).strip())
        except ValueError:
            print("\nErro! Digite um número válido.\n")
    return numero_inteiro

# pede um número decimal até digitar certo.
def obter_float(_mensagem: str) -> float:
    valor_float = None
    while valor_float is None:
        try:
            valor_float = float(input(_mensagem).strip())
        except ValueError:
            print("\nErro! Digite um número válido.\n")
    return valor_float

# pede uma data no formato DD/MM/AAAA e só aceita se for válida.
def obter_data(_mensagem: str) -> str:
    data_valida = None
    while data_valida is None:
        data_str = str(input(_mensagem)).strip()
        if not data_str:
            print("\nErro! Digite novamente.\n")
            continue
        try:
            data_valida = datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            print("\nErro! Digite uma data válida no formato DD/MM/AAAA.\n")
            data_valida = None
    return data_valida.strftime("%d/%m/%Y")

# pede S ou N e devolve True ou False.
def obter_sim_ou_nao(_mensagem: str) -> bool:
    resposta_sim_nao = ""
    while resposta_sim_nao not in ["S", "N"]:
        resposta_sim_nao = str(input(_mensagem)).strip().upper()
        if resposta_sim_nao in ["S", "N"]:
            return resposta_sim_nao[0] == "S"
        print("\nErro! Digite apenas S ou N.\n")
        continue

# pede um inteiro só aceitando se estiver entre os limites que você passar.
def obter_inteiro_em_intervalo(_mensagem: str, _minimo: int, _maximo: int) -> int:
    entrada_valida = False
    while not entrada_valida:
        entrada_numero = obter_inteiro(_mensagem)
        if _minimo <= entrada_numero <= _maximo:
            entrada_valida = True
        else:
            print(f"\nErro! Digite um número entre {_minimo} e {_maximo}.\n")
    return entrada_numero

# ==========================================================
#   BANCO DE DADOS
# ==========================================================

# ========= CONEXÃO BANCO DE DADOS =========
# tenta conectar ao banco Oracle e devolve a conexão ou None se der erro.
def conectar_oracledb(_usuario: str, _senha: str, _dsn_conexao: str) -> oracledb.Connection:
    try:
        conexao_bd = oracledb.connect(
            user=_usuario,
            password=_senha,
            dsn=_dsn_conexao
        )
        return conexao_bd
    except Exception as e:
        print(f"Erro ao conectar com banco.\n\n{e}")
        return None

# ========= INSERIR =========
# tenta salvar os dados do veículo no banco e retorna True se deu certo, False se deu erro.
def inserir_novo_veiculo(_conexao: oracledb.Connection, _dados_veiculo: dict) -> bool:
    try:
        comando_sql = """
INSERT INTO T_VEICULOS (
    tipo, marca, modelo, ano_fabricacao, placa, cor,
    combustivel, quilometragem, status, valor_diaria, data_aquisicao
)
VALUES (
    :tipo, :marca, :modelo, :ano_fabricacao, :placa, :cor,
    :combustivel, :quilometragem, :status, :valor_diaria, TO_DATE(:data_aquisicao, 'DD/MM/YYYY')
)
"""
        cur = _conexao.cursor()
        cur.execute(comando_sql, _dados_veiculo)
        _conexao.commit()
        cur.close()

        sucesso_cadastro = True

    except Exception as e:
        print(f"\nErro no cadastro.\n\n{e}")
        sucesso_cadastro = False

    return sucesso_cadastro

# ========= SELECT =========
# busca todos os veículos cadastrados no banco e devolve uma lista de dicionários.
def buscar_todos_veiculos_como_dicionario(_conexao: oracledb.Connection, colunas: dict, _numeros_colunas: list = None) -> list:
    if not _numeros_colunas:
        _numeros_colunas = list(colunas.keys())

    campos_lista = []
    for num in _numeros_colunas:
        campos_lista.append(colunas[num])
    campos = ", ".join(campos_lista)

    query = f"SELECT {campos} FROM T_VEICULOS"

    with _conexao.cursor() as cur:
        cur.execute(query)

        colunas_cursor = []
        for c in cur.description:
            colunas_cursor.append(c[0].lower())

        df = pd.DataFrame(cur.fetchall(), columns=colunas_cursor)

    return df.to_dict(orient="records")

# ========= SELECT POR TEXTO =========
# busca pacientes no banco filtrando por texto em um campo e devolve uma lista de dicionários.
def buscar_veiculo_por_texto(_conexao: oracledb.Connection, _campo_where: str, _texto: str, _colunas_exibir: list) -> list:
    # Campos válidos existentes na tabela T_VEICULOS
    campos_validos = [
        "TIPO", "MARCA", "MODELO", "ANO_FABRICACAO", "PLACA",
        "COR", "COMBUSTIVEL", "QUILOMETRAGEM", "STATUS",
        "VALOR_DIARIA", "DATA_AQUISICAO", "DATA_CADASTRO", "DATA_ULTIMA_ATUALIZACAO"
    ]

    if _campo_where.upper() not in campos_validos:
        print("\nErro: campo inválido para busca textual.\n")
        return []

    if not _colunas_exibir:
        print("\nErro: nenhuma coluna selecionada para exibição.\n")
        return []

    campos_lista = []
    for num in _colunas_exibir:
        campos_lista.append(colunas_dict[num])
    campos_select = ", ".join(campos_lista)

    comando_sql = f"SELECT {campos_select} FROM T_VEICULOS WHERE UPPER({_campo_where}) LIKE :texto"

    try:
        with _conexao.cursor() as cur:
            cur.execute(comando_sql, {"texto": f"%{_texto.upper()}%"})
            resultados = cur.fetchall()

            nomes_colunas = []
            for col in cur.description:
                nomes_colunas.append(col[0].lower())

            df = pd.DataFrame(resultados, columns=nomes_colunas)
            lista_veiculos = df.to_dict(orient="records")

        return lista_veiculos

    except Exception as e:
        print(f"\nErro ao executar consulta SQL: {e}\n")
        return []

# ========= SELECT POR NÚMERO =========
# busca veículos no banco filtrando por valor numérico em um campo (usando operador) e devolve uma lista de dicionários.
def buscar_veiculo_por_numero(_conexao: oracledb.Connection, _campo: str, _operador: str, _valor: int, _colunas_exibir: list) -> list:
    # Campos válidos existentes na tabela T_VEICULOS
    campos_validos = [
        "ANO_FABRICACAO", "QUILOMETRAGEM", "VALOR_DIARIA", "ID_VEICULO"
    ]

    if _campo.upper() not in campos_validos:
        print("\nErro: campo inválido para busca numérica.\n")
        return []

    if _operador not in ["=", ">", "<", ">=", "<=", "<>"]:
        print("\nErro: operador inválido. Use =, >, <, >=, <= ou <>.\n")
        return []

    if not _colunas_exibir:
        print("\nErro: nenhuma coluna selecionada para exibição.\n")
        return []

    campos_lista = []
    for num in _colunas_exibir:
        campos_lista.append(colunas_dict[num])

    campos_select = ", ".join(campos_lista)
    comando_sql = f"SELECT {campos_select} FROM T_VEICULOS WHERE {_campo} {_operador} :valor"

    try:
        with _conexao.cursor() as cur:
            cur.execute(comando_sql, {"valor": _valor})
            resultados = cur.fetchall()

            nomes_colunas = []
            for col in cur.description:
                nomes_colunas.append(col[0].lower())

            df = pd.DataFrame(resultados, columns=nomes_colunas)
            lista_veiculos = df.to_dict(orient="records")

        return lista_veiculos

    except Exception as e:
        print(f"\nErro ao executar consulta SQL: {e}\n")
        return []

# ========= FUNÇÃO PARA VERIFICAR SE TABELA TEM DADOS =========
# Verifica se a tabela possui registros e retorna True ou False.
def verifica_tabela(_conexao: oracledb.Connection, ) -> bool:
    cur = _conexao.cursor()
    try:
        cur.execute(f"SELECT 1 FROM T_VEICULOS WHERE ROWNUM = 1")
        resultado = cur.fetchone() # pegar apenas uma linha
        return bool(resultado)
    finally:
        cur.close()

# ========= SELECT POR ID =========
# busca um veículo específico no banco pelo id e devolve uma lista de dicionários.
def buscar_veiculo_por_id(_conexao: oracledb.Connection, colunas: dict, _numeros_colunas: list = None, _id_veiculo: int = None) -> list:
    if not _id_veiculo:
        print("\nErro: é necessário informar o ID do veículo.\n")
        return []

    if not _numeros_colunas:
        _numeros_colunas = list(colunas.keys())

    campos_lista = []
    for num in _numeros_colunas:
        campos_lista.append(colunas[num])
    campos = ", ".join(campos_lista)

    query = f"SELECT {campos} FROM T_VEICULOS WHERE id_veiculo = :id_veiculo"

    with _conexao.cursor() as cur:
        cur.execute(query, {"id_veiculo": _id_veiculo})

        colunas_cursor = []
        for c in cur.description:
            colunas_cursor.append(c[0].lower())

        df = pd.DataFrame(cur.fetchall(), columns=colunas_cursor)

    return df.to_dict(orient="records")

# ========= UPDATE =========
# tenta atualizar os dados de um veículo no banco pelo ID e retorna True se deu certo, False se deu erro.
def atualizar_dados_veiculo(_conexao: oracledb.Connection, _novos_dados: dict, _id_veiculo_alvo: int) -> bool:
    if not _id_veiculo_alvo:
        print("\nErro: é necessário informar o ID do veículo para atualizar.\n")
        return False

    try:
        comando_sql = """
UPDATE T_VEICULOS
SET tipo = :tipo,
    marca = :marca,
    modelo = :modelo,
    ano_fabricacao = :ano_fabricacao,
    placa = :placa,
    cor = :cor,
    combustivel = :combustivel,
    quilometragem = :quilometragem,
    status = :status,
    valor_diaria = :valor_diaria,
    data_aquisicao = TO_DATE(:data_aquisicao, 'DD/MM/YYYY')
WHERE id_veiculo = :id_veiculo
"""

        dados_para_bind = _novos_dados.copy()
        dados_para_bind["id_veiculo"] = _id_veiculo_alvo

        cur = _conexao.cursor()
        cur.execute(comando_sql, dados_para_bind)
        _conexao.commit()
        cur.close()

        sucesso_atualizacao = True

    except Exception as e:
        print(f"\nErro ao atualizar veículo.\n\n{e}")
        sucesso_atualizacao = False

    return sucesso_atualizacao

# ========= DELETE TODOS OS DADOS =========
# tenta excluir todos os veículos da tabela do banco de dados e retorna True se deu certo, False se deu erro.
def excluir_todos_veiculos(_conexao: oracledb.Connection) -> bool:
    try:
        if not verifica_tabela(_conexao):
            print("\nNenhum veículo encontrado para exclusão.\n")
            return False

        comando_sql = "DELETE FROM T_VEICULOS"
        cur = _conexao.cursor()
        cur.execute(comando_sql)
        _conexao.commit()
        cur.close()

        sucesso_exclusao = True

    except Exception as e:
        print(f"\nErro ao excluir veículos.\n\n{e}")
        sucesso_exclusao = False

    return sucesso_exclusao

# ========= DELETE PADRÃO =========
# tenta excluir um veículo da tabela do banco de dados pelo id e retorna True se deu certo, False se deu erro.
def excluir_veiculo_por_id(_conexao: oracledb.Connection, _id_veiculo: int) -> bool:
    if not _id_veiculo:
        print("\nErro: é necessário informar o ID do veículo para exclusão.\n")
        return False

    try:
        # verifica se o veículo existe antes de tentar excluir
        with _conexao.cursor() as cur:
            cur.execute("SELECT 1 FROM T_VEICULOS WHERE id_veiculo = :id", {"id": _id_veiculo})
            if not cur.fetchone():
                print(f"\nNenhum veículo encontrado com o ID {_id_veiculo}.\n")
                return False

            comando_sql = "DELETE FROM T_VEICULOS WHERE id_veiculo = :id_veiculo"
            cur.execute(comando_sql, {"id_veiculo": _id_veiculo})
            _conexao.commit()

        sucesso_remocao = True

    except Exception as e:
        print(f"\nErro na remoção.\n\n{e}")
        sucesso_remocao = False

    return sucesso_remocao

# ==========================================================
#   SOLICITAÇÃO DE DADOS 
# ==========================================================

# pede todos os dados do veículo pro usuário e devolve num dicionário.
def solicitar_dados_cadastro_veiculo() -> dict:
    tipo = obter_texto("\nTipo do veículo: ")
    marca = obter_texto("\nMarca: ")
    modelo = obter_texto("\nModelo: ")
    ano_fabricacao = obter_inteiro("\nAno de fabricação: ")
    placa = obter_texto("\nPlaca ex(ABC1D23): ")
    cor = obter_texto("\nCor: ")

    mensagem_combustivel = """\nCombustível (escolha uma opção):
1. Gasolina
2. Etanol
3. Flex
4. Diesel
5. Elétrico
6. Híbrido 
Escolha: """
    tipos_combustivel = {
        1: "Gasolina",
        2: "Etanol",
        3: "Flex",
        4: "Diesel",
        5: "Eletrico",
        6: "Hibrido"
    }
    opcao_combustivel = obter_inteiro_em_intervalo(mensagem_combustivel, 1, 6)
    combustivel = tipos_combustivel[opcao_combustivel]

    quilometragem = obter_inteiro("\nQuilometragem: ")

    mensagem_status = """\nStatus (escolha uma opção):
1. Disponível
2. Alugado
3. Manutenção
Escolha: """
    tipos_status = {
        1: "Disponível",
        2: "Alugado",
        3: "Manutenção"
    }
    opcao_status = obter_inteiro_em_intervalo(mensagem_status, 1, 3)
    status = tipos_status[opcao_status]

    valor_diaria = obter_float("\nValor da diária: ")
    data_aquisicao = obter_data("\nData de aquisição do veículo (DD/MM/YYYY): ")

    dados_veiculo = {
        "tipo": tipo,
        "marca": marca,
        "modelo": modelo,
        "ano_fabricacao": ano_fabricacao,
        "placa": placa,
        "cor": cor,
        "combustivel": combustivel,
        "quilometragem": quilometragem,
        "status": status,
        "valor_diaria": valor_diaria,
        "data_aquisicao": data_aquisicao
    }

    return dados_veiculo

# ==========================================================
#   SOLICITAÇÃO DE COLUNAS DA TABELA T_VEICULOS
# ==========================================================

# Retorna os nomes das colunas selecionadas a partir dos números informados.
def solicita_campos(colunas: dict, _numeros: list) -> str:
    nomes = []
    for i in _numeros:
        if i in colunas:
            nomes.append(colunas[i])
    return ", ".join(nomes)

def menu_selecao_colunas(colunas: dict, _msg, _titulo) -> list:

    selecionadas = []
    entrada = ""

    while entrada != "0":
        limpar_terminal()

        
        exibir_titulo_centralizado(_titulo, 60)
        print(_msg)

        entrada = input("Digite o número da coluna: ").strip().upper()

        if entrada == "0":
            break
        elif entrada == "A":
            selecionadas = list(colunas.keys())
            break
        elif entrada.isdigit():
            num = int(entrada)
            if num in colunas and num not in selecionadas:
                selecionadas.append(num)

    return selecionadas

# ==========================================================
#   VISUALIZAÇÃO DE DADOS (TABULATE)
# ==========================================================

# Imprime os veículos em formato de tabela formatada com o tabulate.
def imprimir_veiculos_tabulate(lista_de_veiculos: list, largura_max: int = 20) -> None:
    if not lista_de_veiculos:
        print("\nNenhum registro encontrado.\n")
        return

    # Cria DataFrame diretamente da lista
    df = pd.DataFrame(lista_de_veiculos)

    # Formata as colunas (datas e textos longos)
    for col in df.columns:
        # Substitui valores nulos
        df[col] = df[col].fillna("")

        textos_formatados = []

        for valor in df[col]:
            # Formatação de datas
            if isinstance(valor, datetime) or isinstance(valor, date):
                valor_formatado = valor.strftime("%d/%m/%Y")  # apenas data, sem hora
            else:
                valor_formatado = str(valor)

            # Quebra de linhas em textos longos
            partes = []
            i = 0
            while i < len(valor_formatado):
                partes.append(valor_formatado[i:i+largura_max])
                i += largura_max

            textos_formatados.append("\n".join(partes))

        df[col] = textos_formatados

    # Usa tabulate para exibir em formato bonito
    print(
        tabulate(
            df,
            headers="keys",
            tablefmt="fancy_grid",
            numalign="right",
            stralign="left",
            showindex=False
        )
    )

# ==========================================================
#   EXPORTAÇÃO 
# ==========================================================

# exporta lista de dicionários para Excel
def exportar_para_excel(lista_veiculos: list, nome_arquivo: str = "veiculos.xlsx") -> bool:
    try:
        if not lista_veiculos:
            print("Nenhum veículo para exportar.")
            return False

        df = pd.DataFrame(lista_veiculos)
        df.to_excel(nome_arquivo, index=False)
        return True
    except Exception as e:
        print(f"\nErro ao exportar para Excel: {e}")
        return False


# exporta lista de dicionários para CSV
def exportar_para_csv(lista_veiculos: list, nome_arquivo: str = "veiculos.csv") -> bool:
    try:
        if not lista_veiculos:
            print("Nenhum veículo para exportar.")
            return False

        df = pd.DataFrame(lista_veiculos)
        df.to_csv(nome_arquivo, index=False, sep=';')
        return True
    except Exception as e:
        print(f"\nErro ao exportar para CSV: {e}")
        return False


# exporta lista de dicionários para JSON
def exportar_para_json(lista_veiculos: list, nome_arquivo: str = "veiculos.json") -> bool:
    try:
        if not lista_veiculos:
            print("Nenhum veículo para exportar.")
            return False

        # converter datetime para string
        for veiculo in lista_veiculos:
            for chave, valor in veiculo.items():
                if isinstance(valor, (datetime, date)):
                    veiculo[chave] = valor.strftime("%d/%m/%Y")

        with open(nome_arquivo, "w", encoding="utf-8") as arquivo_json:
            json.dump(lista_veiculos, arquivo_json, ensure_ascii=False, indent=4)

        return True
    except Exception as e:
        print(f"\nErro ao exportar para JSON: {e}")
        return False

# ==========================================================
#   CAMPOS QUE DESEJA VER 
# ==========================================================
colunas_msg = """SELECIONE OS CAMPOS DE EXIBIÇÃO

1 - ID VEÍCULO                 8 - COMBUSTÍVEL
2 - TIPO                       9 - QUILOMETRAGEM
3 - MARCA                     10 - STATUS
4 - MODELO                    11 - VALOR DA DIÁRIA
5 - ANO DE FABRICAÇÃO         12 - DATA DE AQUISIÇÃO DO VEÍCULO
6 - PLACA                     13 - DATA DE CADASTRO 
7 - COR                       14 - DATA DA ÚLTIMA ATUALIZAÇÃO

DIGITE 'A' PARA SELECIONAR TODOS
DIGITE '0' PARA FINALIZAR SELEÇÃO
"""

colunas_dict = {
    1: "ID_VEICULO",        2: "TIPO",           3: "MARCA",
    4: "MODELO",            5: "ANO_FABRICACAO", 6: "PLACA",
    7: "COR",               8: "COMBUSTIVEL",    9: "QUILOMETRAGEM",
    10: "STATUS",           11: "VALOR_DIARIA",  12: "DATA_AQUISICAO",
    13: "DATA_CADASTRO",    14: "DATA_ULTIMA_ATUALIZACAO"
}

# ==========================================================
#   PROGRAMA PRINCIPAL 
# ==========================================================

try:
    user = "rm561833"
    password = "070406"
    dsn = "oracle.fiap.com.br:1521/ORCL"
    conn = conectar_oracledb(user, password, dsn)
    conectado = bool(conn)
except Exception as e:
    conectado = False

while conectado:
    limpar_terminal()
    exibir_titulo_centralizado("SISTEMA DE GERENCIAMENTO DE VEÍCULOS | LOCADORA", 60)
    print("1 - Cadastrar novo veículo")
    print("2 - Consultar veículos")
    print("3 - Atualizar veículo")
    print("4 - Excluir veículo")
    print("5 - Excluir todos os veículos")
    print("6 - Exportar veículos")
    print("\n0 - Sair\n")
    
    escolha_menu = obter_inteiro_em_intervalo("Escolha: ", 0, 6)

    match escolha_menu:

        case 0:
            limpar_terminal()
            print("\nPrograma encerrado. Até logo!\n")
            conectado = False

        case 1:
            limpar_terminal()
            exibir_titulo_centralizado("MENU CADASTRO DE VEÍCULOS", 60)
            dados_cadastro = solicitar_dados_cadastro_veiculo()
            sucesso = inserir_novo_veiculo(conn, dados_cadastro)
            if sucesso:
                print("\nVeículo cadastrado com sucesso!")
            input("\nPressione 'ENTER' para voltar...")
        
        case 2:
            limpar_terminal()
            exibir_titulo_centralizado("MENU CADASTRO DE VEÍCULOS", 60)

            if not verifica_tabela(conn):
                exibir_titulo_centralizado("MENU DE CONSULTA DE VEÍCULOS", 60)
                print("\nNenhum veículo encontrado.\n")
                input("\nPressione ENTER para voltar...")
            else:
                escolha_submenu = -1
                flag = True
                while flag:
                    limpar_terminal()
                    exibir_titulo_centralizado("MENU DE CONSULTA DE VEÍCULOS", 60)
                    print("1 - Consultar todos os veículos")
                    print("2 - Consultar por ID")
                    print("3 - Consultar por pesquisa de texto")
                    print("4 - Consultar por pesquisa numérica")
                    print("\n0 - Voltar para menu principal\n")
                
                    escolha_consulta = obter_inteiro_em_intervalo("Escolha: ", 0, 4)

                    match escolha_consulta:
                        case 0: # 0 - Voltar para menu principal
                            flag = False
                        
                        case 1: # 1 - Consultar todos os veículos
                            limpar_terminal()
                            exibir_titulo_centralizado("MENU DE CONSULTA DE VEÍCULOS", 60)
                            numeros_colunas = menu_selecao_colunas(colunas_dict, colunas_msg, "CONSULTA DE TODOS OS VEÍCULOS")

                            if not numeros_colunas:
                                print("\nNenhuma coluna selecionada.")
                                input("\nPressione ENTER para voltar para o menu de consultas")
                                flag = False
                                continue

                            veiculos = buscar_todos_veiculos_como_dicionario(conn, colunas_dict, numeros_colunas,)

                            if veiculos:
                                limpar_terminal()
                                exibir_titulo_centralizado("TODOS VEÍCULOS", 60)
                                imprimir_veiculos_tabulate(veiculos)
                            else:
                                print("\nNenhum veículo encontrado.")

                            input("\nPressione ENTER para voltar para o menu de consultas")
                        case 2: # 2 - Consultar por ID
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA DE VEÍCULO POR ID", 60)

                            colunas_preview = {1: "ID_VEICULO", 2: "TIPO", 3: "MODELO", 4: "STATUS"}
                            numeros_preview = [1, 2, 3, 4]
                            
                            veiculos_preview = buscar_todos_veiculos_como_dicionario(conn, colunas_preview, numeros_preview)

                            if not veiculos_preview:
                                print("\nNenhuma coluna selecionada.")
                                input("\nPressione ENTER para voltar ao menu de consultas")
                                continue

                            print("Escolha o ID do veículo que deseja consultar:")
                            imprimir_veiculos_tabulate(veiculos_preview)

                            continuar = True
                            while continuar:
                                print("\nDigite '0' para voltar ao menu de consultas")
                                id_escolhido = obter_inteiro("\nDigite o ID do veículo: ")

                                if id_escolhido == 0:
                                    continuar = False
                                else:
                                    id_encontrado = False
                                    for veiculo in veiculos_preview:
                                        if veiculo.get("ID_VEICULO") == id_escolhido:
                                            id_encontrado = True
                                            break
                                    if not id_encontrado:
                                        print(f"Erro: Nenhum veículo encontrado com ID {id_escolhido}")
                                    else:
                                        continuar = False
                                
                                if id_escolhido == 0:
                                    continue

                                numero_colunas_veiculo_id = menu_selecao_colunas(colunas_dict, colunas_msg,"CONSULTA DE VEÍCULOS POR ID")

                                if not numero_colunas_veiculo_id:
                                    print("\nNenhuma coluna selecionada.")
                                    input("\nPressione ENTER para voltar para o menu de consultas")
                                    continuar = False
                                    continue

                                veiculos = buscar_veiculo_por_id(conn, colunas_dict, _numeros_colunas=numero_colunas_veiculo_id, _id_veiculo=id_escolhido)

                                if veiculos:
                                    limpar_terminal()
                                    exibir_titulo_centralizado(f"VEÍCULO ID {id_escolhido}", 60)
                                    imprimir_veiculos_tabulate(veiculos)
                                    continuar = False
                                else:
                                    print("\nNenhum veículo encontrado.")

                                input("\nPressione ENTER para voltar para o menu de consultas")

                        case 3: # 3 - Consultar por pesquisa de texto
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTAR POR PESQUISA DE TEXTO", 60)

                            campos_texto = {
                                1: "TIPO",
                                2: "MARCA",
                                3: "MODELO",
                                4: "COR",
                                5: "COMBUSTIVEL",
                                6: "STATUS"
                            }

                            print("\nEscolha a coluna textual para buscar:\n")
                            for k, v in campos_texto.items():
                                print(f"{k} - {v}")
                            
                            escolha_campo = obter_inteiro_em_intervalo("Campo: ", 1, 6)
                            campo_where = campos_texto[escolha_campo]

                            print()
                            texto_busca = obter_texto(f"Digite o texto a ser buscado no campo {campo_where}: ")

                            numero_colunas_veiculo_texto = menu_selecao_colunas(colunas_dict, colunas_msg, "CONSULTA DE VEÍCULOS POR PESQUISA DE TEXTO")

                            if not numero_colunas_veiculo_texto:
                                print("\nNenhuma coluna selecionada.")
                                input("\nPressione ENTER para voltar para o menu de consultas")
                                continue

                            veiculos = buscar_veiculo_por_texto(conn, campo_where, texto_busca, numero_colunas_veiculo_texto)

                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA DE VEÍCULOS POR PESQUISA DE TEXTO", 60)
                            if veiculos:
                                imprimir_veiculos_tabulate(veiculos)
                            else:
                                print("\nNenhum veículo encontrado.") 
                            input("\nPressione ENTER para voltar para o menu de consultas")
                        
                        case 4: # 4 - Consultar por pesquisa numérica
                            limpar_terminal()       
                            exibir_titulo_centralizado("CONSULTA POR PESQUISA NUMÉRICA", 60)

                            campos_numericos = {
                                1: "ID_VEICULO",
                                2: "ANO_FABRICACAO",
                                3: "QUILOMETRAGEM",
                                4: "VALOR_DIARIA"
                            }

                            print("Escolha o campo numérico para buscar: ")
                            for k, v in campos_numericos.items():
                                print(f"{k} - {v}")

                            escolha_campo = obter_inteiro_em_intervalo("Campo: ", 1, 4)
                            campo_where = campos_numericos[escolha_campo]

                            print()
                            valor = obter_inteiro(f"Digite o número para buscar no campo {campo_where}: ")

                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTAR POR PESQUISA NUMÉRICA", 60)

                            operadores = {1: "=", 2: ">", 3: "<", 4: ">=", 5: "<=", 6: "<>"}

                            print("Escolha o operador:")
                            print("1. Igual (=)")
                            print("2. Maior (>)")
                            print("3. Menor (<)")
                            print("4. Maior ou igual (>=)")
                            print("5. Menor ou igual (<=)")
                            print("6. Diferente (<>)\n")

                            opcao_operador = obter_inteiro_em_intervalo(f"Operador para pesquisar '{valor}': ", 1, 6)

                            numero_colunas_veiculo_numerico = menu_selecao_colunas(colunas_dict, colunas_msg, "CONSULTA DE VEÍCULOS POR PESQUISA NÚMERICA")

                            if not numero_colunas_veiculo_numerico:
                                print("\nNenhuma coluna selecionada.")
                                input("\nPressione ENTER para voltar para o menu de consultas")
                                continue

                            veiculos = buscar_veiculo_por_numero(conn, campo_where, operadores[opcao_operador], valor, numero_colunas_veiculo_numerico)

                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA DE VEÍCULOS POR PESQUISA NÚMERICA", 60)
                            if veiculos:
                                imprimir_veiculos_tabulate(veiculos)
                            else:
                                print("\nNenhum veículo encontrado.") 
                            input("\nPressione ENTER para voltar para o menu de consultas")
        case 3:  # 3 - Atualizar veículo
            limpar_terminal()
            exibir_titulo_centralizado("ATUALIZAÇÃO DE VEÍCULO", 60)

            colunas_preview = {1: "ID_VEICULO", 2: "TIPO", 3: "MODELO", 4: "STATUS"}
            numeros_preview = [1, 2, 3, 4]

            veiculos_preview = buscar_todos_veiculos_como_dicionario(conn, colunas_preview, numeros_preview)
            if veiculos_preview:
                print("Escolha o ID do veículo que deseja atualizar:")
                imprimir_veiculos_tabulate(veiculos_preview)
                print("Digite '0' para cancelar")
            else:
                print("Nenhum veículo cadastrado no sistema.")
                input("\nPressione ENTER para voltar ao menu...")
                continue

            id_veiculo = obter_inteiro("\nDigite o ID do veículo: ")

            if id_veiculo == 0:
                print("\nVoltando ao menu principal...")
                input("\nPressione ENTER para continuar...")
                continue

            veiculo_atual = buscar_veiculo_por_id(conn, colunas_dict, list(colunas_dict.keys()), id_veiculo)
            if not veiculo_atual:
                print(f"\nErro: Nenhum veículo encontrado com ID {id_veiculo}.")
                input("\nPressione ENTER para voltar ao menu...")
                continue

            veiculo_atual = veiculo_atual[0]

            limpar_terminal()
            exibir_titulo_centralizado("ATUALIZAÇÃO DE VEÍCULO", 60)
            print("\nDados atuais do veículo selecionado:")
            imprimir_veiculos_tabulate([veiculo_atual])

            novos_dados = solicitar_dados_cadastro_veiculo()

            sucesso = atualizar_dados_veiculo(conn, novos_dados, id_veiculo)
            if sucesso:
                print("\nVeículo atualizado com sucesso!")
            else:
                print("\nFalha ao atualizar o veículo.")

            input("\nPressione ENTER para voltar ao menu principal...")
        
        case 4: # 4 - Excluir veículo
            id_veiculo_remover = -1

            while id_veiculo_remover != 0:
                limpar_terminal()
                exibir_titulo_centralizado("REMOÇÃO DE VEÍCULO", 60)

                colunas_preview = {1: "ID_VEICULO", 2: "TIPO", 3: "MODELO", 4: "STATUS"}
                numeros_preview = [1, 2, 3, 4]
                
                veiculos_preview = buscar_todos_veiculos_como_dicionario(conn, colunas_preview, numeros_preview)

                if not veiculos_preview:
                    print("\nNenhum veículo cadastrado no sistema.")
                    input("\nPressione ENTER para voltar ao menu...")
                    break

                print(":Escolha o ID do veículo que deseja excluir:")
                imprimir_veiculos_tabulate(veiculos_preview)
                print("Digite '0' para cancelar")

                id_veiculo_remover = obter_inteiro("\nDigite o ID do veículo: ")

                if id_veiculo_remover == 0:
                    print("\nVoltando ao menu principal...")
                    input("\nPressione ENTER para continuar...")
                    break

                veiculo_selecionado = buscar_veiculo_por_id(conn, colunas_dict, list(colunas_dict.keys()), id_veiculo_remover)

                if not veiculo_selecionado:
                    print(f"\nErro: Nenhum veículo encontrado com ID {id_veiculo_remover}.")
                    input("\nPressione ENTER para tentar novamente...")
                    continue

                limpar_terminal()
                exibir_titulo_centralizado(f"VEÍCULO ID {id_veiculo_remover}", 60)
                imprimir_veiculos_tabulate(veiculo_selecionado)

                confirmar = obter_sim_ou_nao("\nTem certeza que deseja excluir este veículo? (S/N): ")

                if confirmar:
                    sucesso = excluir_veiculo_por_id(conn, id_veiculo_remover)
                    if sucesso:
                        print("\nVeículo excluído com sucesso!")
                    else:
                        print("\nFalha ao excluir o veículo.")
                else:
                    print("\nExclusão cancelada pelo usuário.")

                input("\nPressione ENTER para voltar ao menu de remoção...")
        case 5:  # 5 - Excluir todos os veículos
            limpar_terminal()
            exibir_titulo_centralizado("EXCLUSÃO DE TODOS OS VEÍCULOS", 60)

            if not verifica_tabela(conn):
                print("\nNenhum veículo cadastrado no sistema.\n")
                input("\nPressione ENTER para voltar ao menu principal...")
                continue

            print("\nATENÇÃO: Esta ação excluirá TODOS os veículos cadastrados!\n")
            confirmar = obter_sim_ou_nao("Deseja realmente excluir todos os veículos? (S/N): ")

            if confirmar:
                sucesso = excluir_todos_veiculos(conn)
                if sucesso:
                    print("\nTodos os veículos foram excluídos com sucesso!")
                else:
                    print("\nFalha ao tentar excluir os veículos.")
            else:
                print("\nExclusão cancelada pelo usuário.")

            input("\nPressione ENTER para voltar ao menu principal...")

        case 6:
            limpar_terminal()
            exibir_titulo_centralizado("EXPORTAÇÃO", 60)

            if not verifica_tabela(conn):
                print("\nNenhum veículo cadastrado no sistema.\n")
                input("\nPressione ENTER para voltar ao menu principal...")
                continue

            print("1 - Gerar arquivo EXCEL")
            print("2 - Gerar arquivo CSV")
            print("3 - Gerar arquivo JSON")
            print("\n0 - Voltar para menu principal")

            escolha_export = obter_inteiro_em_intervalo("Escolha: ", 0, 3)

            match escolha_export:
                case 0:
                    continue

                case 1:  # Excel
                    limpar_terminal()
                    exibir_titulo_centralizado("EXPORTAÇÃO PARA EXCEL", 60)
                    nome_arquivo = obter_texto("Digite o nome do arquivo EXCEL (ex: veiculos.xlsx): ")
                    veiculos = buscar_todos_veiculos_como_dicionario(conn, colunas_dict)
                    sucesso = exportar_para_excel(veiculos, nome_arquivo)
                    if sucesso:
                        print(f"\nArquivo Excel '{nome_arquivo}' gerado com sucesso!")
                    input("\nPressione ENTER para voltar...")

                case 2:  # CSV
                    limpar_terminal()
                    exibir_titulo_centralizado("EXPORTAÇÃO PARA CSV", 60)
                    nome_arquivo = obter_texto("Digite o nome do arquivo CSV (ex: veiculos.csv): ")
                    veiculos = buscar_todos_veiculos_como_dicionario(conn, colunas_dict)
                    sucesso = exportar_para_csv(veiculos, nome_arquivo)
                    if sucesso:
                        print(f"\nArquivo CSV '{nome_arquivo}' gerado com sucesso!")
                    input("\nPressione ENTER para voltar...")

                case 3:  # JSON
                    limpar_terminal()
                    exibir_titulo_centralizado("EXPORTAÇÃO PARA JSON", 60)
                    nome_arquivo = obter_texto("Digite o nome do arquivo JSON (ex: veiculos.json): ")
                    veiculos = buscar_todos_veiculos_como_dicionario(conn, colunas_dict)
                    sucesso = exportar_para_json(veiculos, nome_arquivo)
                    if sucesso:
                        print(f"\nArquivo JSON '{nome_arquivo}' gerado com sucesso!")
                    input("\nPressione ENTER para voltar...")

if conn:
    conn.close()