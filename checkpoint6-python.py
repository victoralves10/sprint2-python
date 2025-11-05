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
    # pip install requests
    # pip install pandas

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
# (no terminal: checkpoint6-python.py)

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

    campos_select = ", ".join(_colunas_exibir)
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

    campos_select = ", ".join(_colunas_exibir)
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
def verifica_tabela(_conexao: oracledb.Connection, nome_tabela: str) -> bool:
    cur = _conexao.cursor()
    try:
        cur.execute(f"SELECT 1 FROM {nome_tabela} WHERE ROWNUM = 1")
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
        if not verifica_tabela(_conexao, "T_VEICULOS"):
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
Escolha: """
    tipos_combustivel = {
        1: "Gasolina",
        2: "Etanol",
        3: "Flex",
        4: "Diesel",
        5: "Elétrico"
    }
    opcao_combustivel = obter_inteiro_em_intervalo(mensagem_combustivel, 1, 5)
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

        # Formatação de datas e timestamps
        df[col] = df[col].apply(
            lambda v: v.strftime("%d/%m/%Y %H:%M")
            if isinstance(v, datetime)
            else v.strftime("%d/%m/%Y")
            if isinstance(v, date)
            else v
        )

        # Quebra de linhas em textos longos
        df[col] = df[col].astype(str).apply(
            lambda texto: "\n".join([texto[i:i+largura_max] for i in range(0, len(texto), largura_max)])
        )

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


# ==================== PROGRAMA PRINCIPAL ====================

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
    exibir_titulo_centralizado("LOCADORA DE VEÍCULOS", 60)
    print("""
1. Registrar novo veículo
2. Consultar registros
3. Atualizar informações
4. Remover veículo
5. Limpar todos os registros
6. Exportações 

0. Sair
""")
    escolha_menu = obter_inteiro_em_intervalo("Escolha: ", 0, 6)

    match escolha_menu:
        case 0:
            limpar_terminal()
            print("\nPrograma encerrado. Até logo!\n")
            conectado = False

        case 1:
            limpar_terminal()
            exibir_titulo_centralizado("FICHA DE CADASTRO", 60)
            dados_do_registro = solicitar_dados_cadastro_veiculo()
            sucesso = inserir_novo_veiculo(conn, dados_do_registro)
            if sucesso:
                print("\nVeículo registrado com sucesso!")
            input("\nPressione ENTER para continuar...")

        case 2:
            todos_veiculos = buscar_todos_veiculos_como_dicionario(conn)

            if not todos_veiculos:
                limpar_terminal()
                exibir_titulo_centralizado("CONSULTA / LISTA DE VEÍCULOS", 60)
                print("\nNenhum veículo encontrado.\n")
                input("\nPressione ENTER para continuar...")
                continue

            escolha_submenu = -1
            while escolha_submenu != 0:
                limpar_terminal()
                exibir_titulo_centralizado("CONSULTA / LISTA DE VEÍCULOS", 60)
                print("""
1. Listar todos os veículos
2. Consultar veículo por ID
3. Pesquisar por texto
4. Pesquisar por número

0. Voltar ao menu principal
""")
                escolha_submenu = obter_inteiro_em_intervalo("Escolha: ", 0, 4)

                match escolha_submenu:
                    case 0:
                        break

                    case 1:
                        limpar_terminal()
                        exibir_titulo_centralizado("LISTA DE TODOS OS VEÍCULOS", 60)
                        tabela_formatada = formatar_lista_veiculos_em_tabela(todos_veiculos)
                        if tabela_formatada:
                            print(tabela_formatada)
                        else:
                            print("\nNenhum veículo encontrado.\n")
                        input("\nPressione ENTER para continuar...")

                    case 2:
                        id_veiculo_consulta = -1
                        while id_veiculo_consulta != 0:
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA DE VEÍCULO POR ID", 60)
                            tabela_previa = buscar_resumo_veiculos(conn)

                            if tabela_previa:
                                print("\nESCOLHA O ID DO VEÍCULO QUE DESEJA CONSULTAR:\n")
                                print(tabela_previa)
                                print("\nDIGITE '0' PARA VOLTAR AO MENU PRINCIPAL\n")
                                id_veiculo_consulta = obter_inteiro("\nDigite o ID do veículo: ")
                            else:
                                id_veiculo_consulta = 0
                                continue

                            if id_veiculo_consulta == 0:
                                break

                            tabela_detalhes = buscar_detalhes_veiculo_por_id(conn, id_veiculo_consulta)
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA DE VEÍCULO POR ID", 60)

                            if tabela_detalhes:
                                print(tabela_detalhes)
                            else:
                                print("\nNenhum veículo encontrado com esse ID.\n")

                            input("\nPressione ENTER para continuar...")

                    case 3:
                        limpar_terminal()
                        exibir_titulo_centralizado("CONSULTA DE VEÍCULO POR TEXTO", 60)
                        mensagem_campo_texto = """
Escolha o campo textual para buscar:
1. TIPO
2. MARCA
3. MODELO
4. PLACA
5. COR
6. COMBUSTIVEL
7. STATUS
"""
                        print(mensagem_campo_texto)
                        campo_escolhido = obter_inteiro_em_intervalo("Campo: ", 1, 7)
                        campos_textuais = {
                            1: "TIPO", 2: "MARCA", 3: "MODELO",
                            4: "PLACA", 5: "COR", 6: "COMBUSTIVEL", 7: "STATUS"
                        }
                        campo = campos_textuais[campo_escolhido]

                        texto_busca = input("\nDigite o texto para buscar: ").strip()
                        tabela_detalhes = buscar_veiculo_por_str(conn, campo, texto_busca)

                        limpar_terminal()
                        exibir_titulo_centralizado("RESULTADO DA BUSCA", 60)
                        if tabela_detalhes:
                            print(tabela_detalhes)
                        else:
                            print("\nNenhum veículo encontrado com esse parâmetro.\n")
                        input("\nPressione ENTER para continuar...")

                    case 4:
                        limpar_terminal()
                        exibir_titulo_centralizado("CONSULTA DE VEÍCULO POR NÚMERO", 60)
                        mensagem_campo = """
Escolha o campo numérico para buscar:
1. ID_VEICULO
2. ANO_FABRICACAO
3. QUILOMETRAGEM
4. VALOR_DIARIA
"""
                        print(mensagem_campo)
                        campo_escolhido = obter_inteiro_em_intervalo("Campo: ", 1, 4)
                        campos_numericos = {1: "ID_VEICULO", 2: "ANO_FABRICACAO", 3: "QUILOMETRAGEM", 4: "VALOR_DIARIA"}
                        campo = campos_numericos[campo_escolhido]

                        mensagem_operador = """
Escolha o operador:
1. Igual (=)
2. Maior (>)
3. Menor (<)
4. Maior ou igual (>=)
5. Menor ou igual (<=)
6. Diferente (!=)
"""
                        print(mensagem_operador)
                        opcao_operador = obter_inteiro_em_intervalo("Operador: ", 1, 6)

                        valor = obter_inteiro("\nDigite o valor numérico: ")
                        operadores = {1: "=", 2: ">", 3: "<", 4: ">=", 5: "<=", 6: "!="}
                        tabela_detalhes = buscar_veiculo_por_int(conn, campo, operadores[opcao_operador], valor)

                        limpar_terminal()
                        exibir_titulo_centralizado("RESULTADO DA BUSCA POR NÚMERO", 60)
                        if tabela_detalhes:
                            print(tabela_detalhes)
                        else:
                            print("\nNenhum veículo encontrado com esse critério.\n")
                        input("\nPressione ENTER para continuar...")

        case 3:
            id_veiculo_atualizar = -1
            while id_veiculo_atualizar != 0:
                limpar_terminal()
                exibir_titulo_centralizado("ATUALIZAR VEÍCULO", 60)
                tabela_previa = buscar_resumo_veiculos(conn)
                if tabela_previa:
                    print("\nESCOLHA O ID DO VEÍCULO QUE DESEJA ATUALIZAR:\n")
                    print(tabela_previa)
                    print("\nDIGITE '0' PARA VOLTAR AO MENU PRINCIPAL\n")
                    id_veiculo_atualizar = obter_inteiro("\nDigite o ID do veículo: ")
                else:
                    id_veiculo_atualizar = 0
                    continue

                if id_veiculo_atualizar == 0:
                    break

                tabela_detalhes = buscar_detalhes_veiculo_por_id(conn, id_veiculo_atualizar)
                limpar_terminal()
                exibir_titulo_centralizado("ATUALIZAR VEÍCULO", 60)

                if tabela_detalhes:
                    print("DADOS ATUAIS")
                    print(tabela_detalhes)
                    print("\nDigite os novos dados do veículo:\n")
                    novos_dados = solicitar_dados_cadastro_veiculo()
                    sucesso_atualizacao = atualizar_dados_veiculo(conn, novos_dados, id_veiculo_atualizar)
                    if sucesso_atualizacao:
                        print("\nVeículo atualizado com sucesso!")
                    else:
                        print("\nErro ao atualizar o veículo.\n")
                else:
                    print("\nNenhum veículo encontrado com esse ID.\n")

                input("\nPressione ENTER para continuar...")

        case 4:
            id_veiculo_remover = -1
            while id_veiculo_remover != 0:
                limpar_terminal()
                exibir_titulo_centralizado("REMOVER VEÍCULO", 60)
                tabela_previa = buscar_resumo_veiculos(conn)
                if tabela_previa:
                    print("\nESCOLHA O ID DO VEÍCULO QUE DESEJA REMOVER:\n")
                    print(tabela_previa)
                    print("\nDIGITE '0' PARA VOLTAR AO MENU PRINCIPAL\n")
                    id_veiculo_remover = obter_inteiro("\nDigite o ID do veículo: ")
                else:
                    id_veiculo_remover = 0
                    continue

                if id_veiculo_remover == 0:
                    break

                tabela_detalhes = buscar_detalhes_veiculo_por_id(conn, id_veiculo_remover)
                limpar_terminal()
                exibir_titulo_centralizado("REMOVER VEÍCULO", 60)

                if tabela_detalhes:
                    print("DADOS ATUAIS")
                    print(tabela_detalhes)
                    escolha = obter_sim_ou_nao("\nDESEJA EXCLUIR ESSE REGISTRO? (S/N): ")
                    if escolha:
                        sucesso = excluir_veiculo_por_id(conn, id_veiculo_remover)
                        if sucesso:
                            print("\nVeículo removido com sucesso!")
                        else:
                            print("\nErro ao remover o veículo.\n")
                    else:
                        print("\nRemoção cancelada pelo usuário.\n")
                else:
                    print("\nNenhum veículo encontrado com esse ID.\n")
                input("\nPressione ENTER para continuar...")

        case 5:
            limpar_terminal()
            exibir_titulo_centralizado("REMOVER TODOS OS REGISTROS", 60)
            tabela_previa = buscar_resumo_veiculos(conn)
            if tabela_previa:
                print("\nREGISTROS ATUAIS\n")
                print(tabela_previa)
                confirmacao = obter_sim_ou_nao("\nCONFIRMA A EXCLUSÃO DE TODOS OS VEÍCULOS? [S/N]? ")
                if confirmacao:
                    sucesso = excluir_todos_veiculos(conn)
                    if sucesso:
                        print("\nTODOS OS REGISTROS FORAM REMOVIDOS\n")
                else:
                    print("\nOperação cancelada...")
            input("\nPressione ENTER para continuar...")

        case 6:
            todos_veiculos = buscar_todos_veiculos_como_dicionario(conn)
            if not todos_veiculos:
                limpar_terminal()
                exibir_titulo_centralizado("EXPORTAÇÃO DE DADOS", 60)
                print("\nNenhum veículo encontrado para exportar.\n")
                input("\nPressione ENTER para continuar...")
                continue

            escolha_export = -1
            while escolha_export != 0:
                limpar_terminal()
                exibir_titulo_centralizado("EXPORTAÇÃO DE DADOS", 60)
                print("""
1. Gerar arquivo EXCEL
2. Gerar arquivo CSV
3. Gerar arquivo JSON

0. Voltar para menu principal
""")
                escolha_export = obter_inteiro_em_intervalo("Escolha: ", 0, 3)

                match escolha_export:
                    case 0:
                        break
                    case 1:
                        limpar_terminal()
                        exibir_titulo_centralizado("EXPORTAÇÃO PARA EXCEL", 60)
                        nome_arquivo = obter_texto("\nDigite o nome do arquivo (sem extensão): ").strip()
                        if nome_arquivo:
                            sucesso = exportar_para_excel(todos_veiculos, nome_arquivo + ".xlsx")
                            if sucesso:
                                print(f"\nArquivo '{nome_arquivo}.xlsx' gerado com sucesso!\n")
                            else:
                                print("\nFalha ao gerar arquivo Excel.\n")
                        input("\nPressione ENTER para continuar...")
                    case 2:
                        limpar_terminal()
                        exibir_titulo_centralizado("EXPORTAÇÃO PARA CSV", 60)
                        nome_arquivo = obter_texto("\nDigite o nome do arquivo (sem extensão): ").strip()
                        if nome_arquivo:
                            sucesso = exportar_para_csv(todos_veiculos, nome_arquivo + ".csv")
                            if sucesso:
                                print(f"\nArquivo '{nome_arquivo}.csv' gerado com sucesso!\n")
                            else:
                                print("\nFalha ao gerar arquivo CSV.\n")
                        input("\nPressione ENTER para continuar...")
                    case 3:
                        limpar_terminal()
                        exibir_titulo_centralizado("EXPORTAÇÃO PARA JSON", 60)
                        nome_arquivo = obter_texto("\nDigite o nome do arquivo (sem extensão): ").strip()
                        if nome_arquivo:
                            sucesso = exportar_para_json(todos_veiculos, nome_arquivo + ".json")
                            if sucesso:
                                print(f"\nArquivo '{nome_arquivo}.json' gerado com sucesso!\n")
                            else:
                                print("\nFalha ao gerar arquivo JSON.\n")
                        input("\nPressione ENTER para continuar...")
