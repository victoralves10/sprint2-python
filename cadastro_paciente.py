import os
import re
import json
from datetime import datetime, date


import oracledb
import pandas as pd
import requests
from tabulate import tabulate

# ==========================================================
# INSTRUÇÕES PARA EXECUTAR O PROGRAMA
# ==========================================================
# Execute o comando SQL abaixo no 'Oracle SQL Developer' para criar as tabelas necessárias.
# Instale as bibliotecas exigidas no terminal:
    # pip install oracledb
    # pip install pandas
    # pip install tabulate

# COMANDO SQL PARA ORACLE
"""
-- Tabela de Pacientes
CREATE TABLE T_PACIENTE (
    ID_PACIENTE        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NM_COMPLETO        VARCHAR2(150) NOT NULL,
    DT_NASCIMENTO      DATE NOT NULL,
    SEXO               CHAR(1) NOT NULL,
    CPF                VARCHAR2(11),
    RG                 VARCHAR2(9),
    ESTADO_CIVIL       VARCHAR2(20),
    BRASILEIRO         CHAR(1),  -- S/N
    CEP                VARCHAR2(8),
    RUA                VARCHAR2(100),
    BAIRRO             VARCHAR2(50),
    CIDADE             VARCHAR2(50),
    ESTADO             CHAR(2),
    NUMERO_ENDERECO    NUMBER,
    CELULAR            VARCHAR2(11),
    EMAIL              VARCHAR2(100),
    CONVENIO           CHAR(1),   -- S/N

    -- Campos de consulta
    DT_HORA_CONSULTA   TIMESTAMP,
    TIPO_CONSULTA      VARCHAR2(20),
    ESPECIALIDADE      VARCHAR2(50),
    STATUS_CONSULTA    VARCHAR2(20)
);
"""
# Após isso, o código estará pronto para ser executado.

# ==========================================================
#   SUBALGORITMOS
# ==========================================================

# ==========================================================
#   EXIBIÇÃO
# ==========================================================

# limpa a tela do terminal dependendo do sistema.
def limpar_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")

# mostra um título centralizado com linhas decorativas em cima e embaixo.
def exibir_titulo_centralizado(_texto: str, _largura_caracteres: int) -> None:
    print("=-" * (_largura_caracteres // 2))
    print(_texto.center(_largura_caracteres))
    print("=-" * (_largura_caracteres // 2), "\n")

# mostra uma linha repetindo o símbolo que passar.
def imprimir_linha_separadora(simbolo: str, quantidade: int) -> None:
    print()
    print(f"{simbolo * quantidade}")
    print()

# ==========================================================
#   VALIDAÇÃO DE DADOS
# ==========================================================
'''
# obter string com mensagem personalizável
def obter_str(_msg: str = None) -> str:
    _msg = _msg or ""
    entrada_str = ""
    while not entrada_str:
        entrada_str = str(input(_msg)).strip()
    return entrada_str
'''

# obter int com mensagem personalizável
def obter_int(_msg: str = None) -> int:
    _msg = _msg or ""
    entrada_int = None
    while entrada_int is None:
        try:
            entrada_int = int(input(_msg).strip())
        except ValueError:
            entrada_int = None
    return entrada_int

# obter float com mensagem personalizável
def obter_float(_msg: str = None) -> float:
    _msg = _msg or ""
    entrada_float = None
    while entrada_float is None:
        try:
            entrada_float = float(input(_msg).strip())
        except ValueError:
            entrada_float = None
    return entrada_float

# obter data com mensagem personalizável
def obter_data(_msg: str = None) -> datetime:
    _msg = _msg or ""
    data = None
    while data is None:
        data_str = str(input(_msg)).strip()
        if not data_str:
            continue
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y")
        except Exception:
            data = None
    return data.strftime("%d/%m/%Y")


# obter perguntar Sim ou Não retornando True ou False com mensagem personalizável
def obter_sim_nao(_msg: str = None) -> bool:
    _msg = _msg or ""
    entrada_sim_nao = ""
    resultado = False
    while entrada_sim_nao not in ["S", "N"]:
        entrada_sim_nao = str(input(_msg)).strip().upper()
        if not entrada_sim_nao:
            continue
        if entrada_sim_nao[0] == "S":
            resultado = True
        elif entrada_sim_nao[0] == "N":
            resultado = False
    return resultado

# obter um intervaldo de números retornando um número entre eles com mensagem personalizável
def obter_int_invervalado(_msg: str, _min: int, _max: int) -> int:
    entrada_valida = False
    while not entrada_valida:
        entrada_numero = obter_int(_msg)
        if _min <= entrada_numero <= _max:
            entrada_valida = True
        else:
            continue
    return entrada_numero

"""# obter opções com mensagem personalizável
def obter_opcoes(_msg: str = None, _opcoes: dict = None):
    _msg = _msg or ""
    if not _opcoes:
        return None

    escolha = None
    while escolha not in _opcoes:
        entrada = str(input(_msg).strip())
        if entrada in _opcoes:
            escolha = entrada
    return _opcoes[escolha]"""

# ==========================================================
#   VALIDAÇÃO DE DADOS PARA CADASTRO (PACIENTE)
# ==========================================================

# obter nome
def obter_nome(_msg: str = None) -> str:
    _msg = _msg or ""
    entrada_str = ""
    while not entrada_str:
        entrada_str = str(input(_msg)).strip()
    return entrada_str

# obter sexo
def obter_sexo(_msg: str = None) -> str:
    _msg = _msg or ""
    sexo = ""
    resultado = ""
    while sexo not in ['M', 'F']:
        sexo = input(_msg).strip().upper()
        if not sexo:
            continue
        if sexo[0] == 'M':
            resultado = 'M'
        elif sexo[0] == 'F':
            resultado = 'F'
    return resultado


# obter cpf ex(12345678901)
def obter_cpf(_msg: str = None) -> str:
    _msg = _msg or ""
    cpf = ""
    while not (cpf.isdigit() and len(cpf) == 11):
        cpf = input(_msg).strip()
    return cpf

# obter número rg ex(123456789)
def obter_rg(_msg: str = None) -> str:
    _msg = _msg or ""
    rg = ""
    while not (rg.isdigit() and len(rg) == 9):
        rg = str(input(_msg).strip())
    return rg

# obter estado civil
def obter_estado_civil(_msg: str = None) -> str:
    _msg = _msg or ""
    opcoes_estado_civil = {
        1: "solteiro",
        2: "casado",
        3: "divorciado",
        4: "viuvo"
    }

    escolha = ""
    while escolha not in opcoes_estado_civil:
        escolha = obter_int(_msg)

    return opcoes_estado_civil[escolha]

# obter endereco ex(12345678)
def obter_endereco(_msg: str = None) -> dict:
    _msg = _msg or ": "
    endereco = None

    while not endereco:
        cep = input(_msg).strip().replace("-", "")
        if len(cep) != 8 or not cep.isdigit():
            continue

        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            data = response.json()
            if "erro" in data:
                continue
            endereco = {
                "cep": data.get("cep", ""),
                "logradouro": data.get("logradouro", ""),
                "bairro": data.get("bairro", ""),
                "cidade": data.get("localidade", ""),
                "estado": data.get("uf", "")
            }
        except Exception:
            endereco = None

    return endereco

# obter CEP a partir do endereço
def obter_cep(_endereco: dict) -> str:
    return _endereco.get("cep", "")

# obter rua/logradouro a partir do endereço
def obter_rua(_endereco: dict) -> str:
    return _endereco.get("logradouro", "")

# obter bairro a partir do endereço
def obter_bairro(_endereco: dict) -> str:
    return _endereco.get("bairro", "")

# obter cidade a partir do endereço
def obter_cidade(_endereco: dict) -> str:
    return _endereco.get("cidade", "")

# obter estado a partir do endereço
def obter_estado(_endereco: dict) -> str:
    return _endereco.get("estado", "")

# obter telefone/celular com regex ex(11-978777404)
def obter_telefone(_msg: str = None) -> str:
    _msg = _msg or ""
    telefone = ""
    padrao = re.compile(r"^\d{11}$")

    while not padrao.match(telefone):
        telefone = str(input(_msg)).strip().replace(" ", "").replace("-", "")
    return telefone

# obter email
def obter_email(_msg: str = None) -> str:
    _msg = _msg or ""
    padrao = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    email = ""

    while not padrao.match(email):
        email = input(_msg).strip().lower()
    return email

# ==========================================================
#   VALIDAÇÃO DE DADOS PARA CADASTRO (CONSULTA)
# ==========================================================

# obter data da consulta: dd/mm/aaaa hh:mm
def obter_data_consulta(_msg: str = None) -> datetime:
    _msg = _msg or ""
    data = None
    while data is None:
        data_str = str(input(_msg)).strip()
        if not data_str:
            continue
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y %H:%M")
        except Exception:
            data = None
    return data.strftime("%d/%m/%Y %H:%M")

# obter tipo de consulta
def obter_tipo_consulta(_msg: str = None) -> str:
    _msg = _msg or ""
    opcoes_tipo_consulta = {
        1: "retorno",
        2: "emergencia",
        3: "rotina",
        4: "exame",
        5: "geral",
    }

    escolha = ""
    while escolha not in opcoes_tipo_consulta:
        escolha = obter_int(_msg)

    return opcoes_tipo_consulta[escolha]

# obter especialidade
def obter_especialidade(_msg: str = None) -> str:
    _msg = _msg or ""
    opcoes_especialidade = {
        1: "cardiologia",
        2: "neurologia",
        3: "ortopedia",
        4: "dermatologia",
        5: "pediatria",
        6: "oftalmologia",
        7: "clinico geral",
    }

    escolha = ""
    while escolha not in opcoes_especialidade:
        escolha = obter_int(_msg)

    return opcoes_especialidade[escolha]

# obter status consulta
def obter_status_consulta(_msg: str = None) -> str:
    _msg = _msg or ""
    opcoes_status_consulta = {
        1: "realizada",
        2: "cancelada",
        3: "absenteismo"
    }

    escolha = ""
    while escolha not in opcoes_status_consulta:
        escolha = obter_int(_msg)

    return opcoes_status_consulta[escolha]

# ==========================================================
#   SOLICITAÇÃO DE DADOS T_PACIENTE
# ==========================================================

def solicitar_dados_paciente() -> dict:
    # ================== DADOS DO PACIENTE ==================
    nome_completo = obter_nome("Nome do paciente: ")
    imprimir_linha_separadora("=-", 20)

    data_nascimento = obter_data("Data de nascimento (dd/mm/aaaa): ")
    imprimir_linha_separadora("=-", 20)

    sexo = obter_sexo("Sexo [M/F]: ")
    imprimir_linha_separadora("=-", 20)

    cpf = obter_cpf("CPF (somente números, ex: 12345678901): ")
    imprimir_linha_separadora("=-", 20)

    rg = obter_rg("RG (somente números, ex: 123456789): ")
    imprimir_linha_separadora("=-", 20)

    estado_civil = obter_estado_civil("""Estado civil
1 - Solteiro
2 - Casado
3 - Divorciado
4 - Viuvo
Escolha: """)
    imprimir_linha_separadora("=-", 20)

    brasileiro = obter_sim_nao("É brasileiro? [S/N]: ")
    imprimir_linha_separadora("=-", 20)

    endereco = obter_endereco("CEP (ex: 01310200): ")
    imprimir_linha_separadora("=-", 20)

    numero_endereco = obter_int("Número da residência (ex: 123): ")
    imprimir_linha_separadora("=-", 20)

    celular = obter_telefone("Celular (DDD + número — ex: 11987654321): ")
    imprimir_linha_separadora("=-", 20)

    email = obter_email("Informe o e-mail (exemplo: exemplo@email.com)\nE-mail: ")
    imprimir_linha_separadora("=-", 20)

    convenio = obter_sim_nao("Possui convênio/plano de saúde? [S/N]: ")
    imprimir_linha_separadora("=-", 20)

    # ================== DADOS DA CONSULTA ==================
    data_hora_consulta = obter_data_consulta("Digite a data e hora da consulta (exemplo: 25/10/2025 14:30)\nData e Hora: ")
    imprimir_linha_separadora("=-", 20)

    tipo_consulta = obter_tipo_consulta("""Tipo de consulta
1 - Retorno
2 - Emergencia
3 - Rotina
4 - Exame
5 - Geral
Escolha: """)
    imprimir_linha_separadora("=-", 20)

    especialidade = obter_especialidade("""Especialidade
1 - Cardiologia
2 - Neurologia
3 - Ortopedia
4 - Dermatologia
5 - Pediatria
6 - Oftalmologia
7 - Clínico Geral
Escolha: """)
    imprimir_linha_separadora("=-", 20)

    status_consulta = obter_status_consulta("""Status da consulta
1 - Realizada
2 - Cancelada
3 - Absenteísmo
Escolha: """)

    # ================== RETORNO ==================
    return {
        # Dados do paciente
        "nome_completo": nome_completo,#[:150],  # limita 150 caracteres
        "data_nascimento": data_nascimento,
        "sexo": sexo,
        "cpf": cpf[:11],  # garante 11 caracteres
        "rg": rg[:9],     # garante 9 caracteres
        "estado_civil": estado_civil[:20],
        "brasileiro": "S" if brasileiro else "N",
        "cep": obter_cep(endereco).replace("-", ""),  # remove hífen
        "rua": obter_rua(endereco)[:100],
        "bairro": obter_bairro(endereco)[:50],
        "cidade": obter_cidade(endereco)[:50],
        "estado": obter_estado(endereco)[:2],
        "numero_endereco": numero_endereco,
        "celular": celular[:11],
        "email": email[:100],
        "convenio": "S" if convenio else "N",
        # Dados da consulta
        "data_hora_consulta": data_hora_consulta,
        "tipo_consulta": tipo_consulta[:20],
        "especialidade": especialidade[:50],
        "status_consulta": status_consulta[:20]
    }


# ==========================================================
#   SOLICITAÇÃO DE COLUNAS DA TABELA PACIENTE
# ==========================================================

# função que escolhe quais campos da tabela serão escolhidos e retorna em lista
def solicita_campos(colunas: dict, _numeros: list) -> str:
    nomes = []
    for i in _numeros:
        if i in colunas:
            nomes.append(colunas[i])
    return ", ".join(nomes)

"""
# dicionário de colunas
colunas = {
    1: "ID_PACIENTE",
    2: "NM_COMPLETO",
    3: "DT_NASCIMENTO",
    4: "SEXO",
    5: "CPF",
    6: "RG",
    7: "ESTADO_CIVIL",
    8: "BRASILEIRO",
    9: "CEP",
    10: "RUA",
    11: "BAIRRO",
    12: "CIDADE",
    13: "ESTADO",
    14: "NUMERO_ENDERECO",
    15: "CELULAR",
    16: "EMAIL",
    17: "CONVENIO",
    18: "DT_HORA_CONSULTA",
    19: "TIPO_CONSULTA",
    20: "ESPECIALIDADE",
    21: "STATUS_CONSULTA"
}

# lista de índices escolhidos
_numeros = []

# loop de seleção
entrada = None
while entrada != "0":
    entrada = input("Digite o número da coluna (0 para sair, 'A' para todas): ").strip().upper()
    
    if entrada == "0":
        break
    elif entrada == "A":
        # seleciona todas as colunas
        _numeros = list(colunas.keys())
        break
    elif entrada.isdigit():
        num = int(entrada)
        if num in colunas and num not in _numeros:
            _numeros.append(num)



# exemplo de uso
campos_selecionados = solicita_campos(colunas, _numeros)
print("Colunas selecionadas:", campos_selecionados)
"""

# ==========================================================
#   CRUD BANCO DE DADOS
# ==========================================================

# ========= CONEXÃO BANCO DE DADOS =========
# tenta conectar ao banco de dados oracle. retorno: se a conexão for bem-sucedida: (True, None) - Se falhar: (False, mensagem de erro)
def conectar_oracledb(_user: str, _password: str, _dsn: str) -> tuple[bool, any]:
    retorno = None

    try:
        conexao_bd = oracledb.connect(
            user = _user,
            password = _password,
            dsn = _dsn
        )
    
        retorno = (True, conexao_bd) 

    except Exception as e:
        
        retorno = (False, e)
    
    return retorno


# ========= FUNÇÃO PARA VERIFICAR SE TABELA TEM DADOS =========
# verifica se a tabela possui pelo menos 1 registro. Retorna True se tiver dados, False se estiver vazia.
def verifica_tabela(_conexao: oracledb.Connection, nome_tabela: str) -> bool:
    """
    Verifica se a tabela possui pelo menos 1 registro.
    Retorna True se tiver dados, False se estiver vazia.
    """
    cur = _conexao.cursor()
    try:
        cur.execute(f"SELECT 1 FROM {nome_tabela} WHERE ROWNUM = 1")
        resultado = cur.fetchone()
        return bool(resultado)
    finally:
        cur.close()

# ========= INSERIR PACIENTE =========
# tenta inserir paciente no banco. retorna (True, None) se sucesso, (False, erro) se falhar
def inserir_paciente(_conexao: oracledb.Connection, _dados_paciente: dict) -> tuple[bool, any]:
    retorno = None
    try:
        comando_sql = """
        INSERT INTO T_PACIENTE (
            NM_COMPLETO, DT_NASCIMENTO, SEXO, CPF, RG, ESTADO_CIVIL, BRASILEIRO,
            CEP, RUA, BAIRRO, CIDADE, ESTADO, NUMERO_ENDERECO, CELULAR, EMAIL, CONVENIO,
            DT_HORA_CONSULTA, TIPO_CONSULTA, ESPECIALIDADE, STATUS_CONSULTA
        )
        VALUES (
            :nome_completo, TO_DATE(:data_nascimento, 'DD/MM/YYYY'), :sexo, :cpf, :rg, :estado_civil, :brasileiro,
            :cep, :rua, :bairro, :cidade, :estado, :numero_endereco, :celular, :email, :convenio,
            TO_TIMESTAMP(:data_hora_consulta, 'DD/MM/YYYY HH24:MI'), :tipo_consulta, :especialidade, :status_consulta
        )
        """
        cur = _conexao.cursor()
        cur.execute(comando_sql, _dados_paciente)
        _conexao.commit()
        cur.close()
        retorno = (True, None)
    except Exception as e:
        retorno = (False, e)
    return retorno

# ========= SELECT PACIENTE =========
# Busca todos os pacientes no banco e retorna uma lista de dicionários, cada dicionário representa um paciente.
def buscar_todos_pacientes_como_dicionario(_conexao: oracledb.Connection, colunas: dict, _numeros_colunas: list = None) -> list:
    """
    Retorna uma lista de dicionários com os pacientes, convertendo datas para datetime.
    """
    if not _numeros_colunas:
        _numeros_colunas = list(colunas.keys())

    campos_selecionados = ", ".join([colunas[i] for i in _numeros_colunas])

    cur = _conexao.cursor()
    cur.execute(f"SELECT {campos_selecionados} FROM T_PACIENTE")
    nomes_colunas = [col[0].upper() for col in cur.description]
    resultados_db = cur.fetchall()
    cur.close()

    lista_de_pacientes = []
    for linha in resultados_db:
        registro = {}
        for i, valor in enumerate(linha):
            chave = nomes_colunas[i]
            # Converter data de nascimento para datetime.date
            if chave == "DT_NASCIMENTO" and isinstance(valor, datetime):
                registro[chave] = valor.date()  # só dia/mês/ano
            else:
                registro[chave] = valor
        lista_de_pacientes.append(registro)

    return lista_de_pacientes

# ========= PRINT DADOS =========
def imprimir_pacientes_tabulate(lista_de_pacientes: list, largura_max: int = 20) -> None:
    lista_formatada = []

    for paciente in lista_de_pacientes:
        registro = {}
        for chave, valor in paciente.items():
            if valor is None:
                registro[chave] = ""
            elif isinstance(valor, datetime):
                registro[chave] = valor.strftime("%d/%m/%Y %H:%M")
            elif isinstance(valor, date):
                registro[chave] = valor.strftime("%d/%m/%Y")
            else:
                texto = str(valor)
                linhas = [texto[i:i+largura_max] for i in range(0, len(texto), largura_max)]
                registro[chave] = "\n".join(linhas)
        lista_formatada.append(registro)

    print(tabulate(
        lista_formatada, 
        headers="keys", 
        tablefmt="fancy_grid", 
        numalign="right",
        stralign="left"
    ))

# ==========================================================
# PROCEDIMENTO: MENU DE SELEÇÃO DE COLUNAS
# ==========================================================
def menu_selecao_colunas(colunas: dict, _msg, _titulo) -> list:
    """
    Procedimento que permite ao usuário selecionar colunas para exibir.
    Digitar 'A' seleciona todas, '0' encerra a seleção.
    Retorna a lista de índices escolhidos.
    """
    selecionadas = []
    entrada = ""

    while entrada != "0":
        limpar_terminal()  # limpa a tela a cada iteração

        # imprime o menu com as colunas
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

# ========= BUSCAR PACIENTE POR TEXTO =========
# Busca pacientes por texto em um campo específico e retorna lista de dicionários.
def buscar_paciente_por_texto(_conexao: oracledb.Connection, _campo_where: str, _texto: str, _colunas_exibir: list) -> list:
    """
    Busca pacientes por texto em um campo específico e retorna lista de dicionários.

    _conexao       : conexão Oracle
    _campo_where   : campo textual onde será feita a busca (WHERE)
    _texto         : texto a buscar
    _colunas_exibir: lista de nomes de colunas para exibir no SELECT

    Retorna lista de dicionários ou lista vazia se não houver resultados.
    """

    campos_validos = [
        "NM_COMPLETO", "ESTADO_CIVIL", "CEP", "RUA", "BAIRRO",
        "CIDADE", "ESTADO", "CELULAR", "EMAIL",
        "ESPECIALIDADE", "STATUS_CONSULTA", "TIPO_CONSULTA"
    ]

    if _campo_where.upper() not in campos_validos:
        print("\nErro: campo inválido para busca textual.\n")
        return []

    if not _colunas_exibir:
        print("\nErro: nenhuma coluna selecionada para exibição.\n")
        return []

    campos_select = ", ".join(_colunas_exibir)

    cur = _conexao.cursor()
    comando_sql = f"SELECT {campos_select} FROM T_PACIENTE WHERE UPPER({_campo_where}) LIKE :texto"

    try:
        cur.execute(comando_sql, {"texto": f"%{_texto.upper()}%"})
        resultados = cur.fetchall()
        nomes_colunas = [col[0].upper() for col in cur.description]
    except Exception as e:
        print(f"\nErro ao executar consulta SQL: {e}\n")
        cur.close()
        return []
    finally:
        cur.close()

    lista_pacientes = []
    for linha in resultados:
        registro = { nomes_colunas[i]: linha[i] for i in range(len(nomes_colunas)) }
        lista_pacientes.append(registro)

    return lista_pacientes

# ========= BUSCAR PACIENTE POR NÚMERO =========
# Busca pacientes por valor numérico em um campo específico usando um operador relacional.
def buscar_paciente_por_numero(_conexao: oracledb.Connection, _campo: str, _operador: str, _valor: int, _colunas_exibir: list) -> list:
    """
    Busca pacientes por valor numérico em um campo específico usando um operador.
    """
    campos_select = ", ".join(_colunas_exibir)
    cur = _conexao.cursor()
    comando_sql = f"SELECT {campos_select} FROM T_PACIENTE WHERE {_campo} {_operador} :valor"

    try:
        cur.execute(comando_sql, {"valor": _valor})
        resultados = cur.fetchall()
        nomes_colunas = [col[0].upper() for col in cur.description]
    except Exception as e:
        print(f"\nErro ao executar consulta SQL: {e}\n")
        cur.close()
        return []
    finally:
        cur.close()

    lista_pacientes = []
    for linha in resultados:
        registro = { nomes_colunas[i]: linha[i] for i in range(len(nomes_colunas)) }
        lista_pacientes.append(registro)

    return lista_pacientes

# ========= UPDATE PACIENTE =========
def atualizar_paciente(_conexao: oracledb.Connection, _id_paciente: int, _dados_paciente: dict) -> tuple[bool, any]:
    """
    Atualiza os dados de um paciente existente com base no ID.
    Retorna (True, None) se sucesso, (False, erro) se falhar.
    """
    try:
        comando_sql = """
        UPDATE T_PACIENTE
        SET
            NM_COMPLETO = :nome_completo,
            DT_NASCIMENTO = TO_DATE(:data_nascimento, 'DD/MM/YYYY'),
            SEXO = :sexo,
            CPF = :cpf,
            RG = :rg,
            ESTADO_CIVIL = :estado_civil,
            BRASILEIRO = :brasileiro,
            CEP = :cep,
            RUA = :rua,
            BAIRRO = :bairro,
            CIDADE = :cidade,
            ESTADO = :estado,
            NUMERO_ENDERECO = :numero_endereco,
            CELULAR = :celular,
            EMAIL = :email,
            CONVENIO = :convenio,
            DT_HORA_CONSULTA = TO_TIMESTAMP(:data_hora_consulta, 'DD/MM/YYYY HH24:MI'),
            TIPO_CONSULTA = :tipo_consulta,
            ESPECIALIDADE = :especialidade,
            STATUS_CONSULTA = :status_consulta
        WHERE ID_PACIENTE = :id_paciente
        """

        # adiciona o ID para o bind
        _dados_paciente["id_paciente"] = _id_paciente

        cur = _conexao.cursor()
        cur.execute(comando_sql, _dados_paciente)
        _conexao.commit()
        cur.close()

        return (True, None)
    except Exception as e:
        return (False, e)

# ==========================================================
# EXPORTAR PACIENTES PARA JSON
# ==========================================================

def exportar_para_json(_conexao: oracledb.Connection, _colunas: list, _nome_arquivo: str = "pacientes.json") -> tuple[bool, any]:
    """
    Exporta pacientes para arquivo JSON.
    Retorna (True, None) se sucesso, (False, erro) se falhar.
    """
    try:
        # Monta dicionário de colunas no formato esperado pela função de busca
        colunas_dict = {i + 1: c for i, c in enumerate(_colunas)}

        # Busca os pacientes
        lista_pacientes = buscar_todos_pacientes_como_dicionario(
            _conexao, colunas_dict, list(range(1, len(_colunas) + 1))
        )

        if not lista_pacientes:
            return (False, "Nenhum paciente encontrado para exportar.")

        # Converte datas para string legível, incluindo hora se houver
        for paciente in lista_pacientes:
            for chave, valor in paciente.items():
                if isinstance(valor, datetime):
                    paciente[chave] = valor.strftime("%d/%m/%Y %H:%M")
                elif isinstance(valor, date):
                    paciente[chave] = valor.strftime("%d/%m/%Y")

        # Grava o arquivo JSON
        with open(_nome_arquivo, "w", encoding="utf-8") as arquivo_json:
            json.dump(lista_pacientes, arquivo_json, ensure_ascii=False, indent=4)

        return (True, None)

    except Exception as e:
        return (False, e)

