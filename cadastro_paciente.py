import os
import re
import json
from datetime import datetime, date

import oracledb
import requests
from tabulate import tabulate

# ==========================================================
#   INSTRUÇÕES PARA EXECUTAR O PROGRAMA
# ==========================================================
# Execute o comando SQL abaixo no 'Oracle SQL Developer' para criar as tabelas necessárias.
# Instale as bibliotecas exigidas no terminal:
    # pip install oracledb
    # pip install tabulate
    # pip install requests

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

# Execute o programa pelo arquivo principal: main.py
# (no terminal: python main.py)


# ==========================================================
#   SUBALGORITMOS
# ==========================================================

# ==========================================================
#   EXIBIÇÃO
# ==========================================================

def limpar_terminal() -> None:
    """Limpa a tela do terminal, compatível com Windows e Unix."""
    os.system("cls" if os.name == "nt" else "clear")

def exibir_titulo_centralizado(_texto: str, _largura_caracteres: int) -> None:
    """Mostra um título centralizado com linhas decorativas acima e abaixo."""
    print("=-" * (_largura_caracteres // 2))
    print(_texto.center(_largura_caracteres))
    print("=-" * (_largura_caracteres // 2), "\n")

def imprimir_linha_separadora(simbolo: str, quantidade: int) -> None:
    """Mostra uma linha formada pela repetição de um símbolo."""
    print()
    print(simbolo * quantidade)
    print()

# ==========================================================
#   VALIDAÇÃO DE DADOS (TIPOS BÁSICOS)
# ==========================================================

def obter_int(_msg: str = None) -> int:
    """Obtém um número inteiro digitado pelo usuário, com mensagem opcional."""
    _msg = _msg or ""
    entrada_int = None
    while entrada_int is None:
        try:
            entrada_int = int(input(_msg).strip())
        except ValueError:
            entrada_int = None
    return entrada_int

def obter_float(_msg: str = None) -> float:
    """Obtém um número float digitado pelo usuário, com mensagem opcional."""
    _msg = _msg or ""
    entrada_float = None
    while entrada_float is None:
        try:
            entrada_float = float(input(_msg).strip())
        except ValueError:
            entrada_float = None
    return entrada_float

def obter_data(_msg: str = None) -> datetime:
    """Obtém um uma data digitado pelo usuário, com mensagem opcional. ex 00/00/0000"""
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

def obter_sim_nao(_msg: str = None) -> bool:
    """Pergunta ao usuário uma questão de Sim/Não e retorna True para 'S' ou False para 'N', com mensagem personalizável."""
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

def obter_int_invervalado(_msg: str, _min: int, _max: int) -> int:
    """Solicita ao usuário um número inteiro entre os valores mínimos e máximos informados, com mensagem personalizável."""
    entrada_valida = False
    while not entrada_valida:
        entrada_numero = obter_int(_msg)
        if _min <= entrada_numero <= _max:
            entrada_valida = True
        else:
            continue
    return entrada_numero

# ==========================================================
#   VALIDAÇÃO DE DADOS PARA CADASTRO (PACIENTE)
# ==========================================================

def obter_nome(_msg: str = None) -> str:
    """Solicita ao usuário um nome (ou texto) e garante que o campo não fique vazio, com mensagem personalizável."""
    _msg = _msg or ""
    entrada_str = ""
    while not entrada_str:
        entrada_str = str(input(_msg)).strip()
    return entrada_str

def obter_sexo(_msg: str = None) -> str:
    """Solicita ao usuário o sexo e retorna 'M' para masculino ou 'F' para feminino, com mensagem personalizável."""
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

def obter_cpf(_msg: str = None) -> str:
    """Solicita ao usuário um CPF no formato numérico (11 dígitos) e valida a entrada, com mensagem personalizável. ex 12345678901"""
    _msg = _msg or ""
    cpf = ""
    while not (cpf.isdigit() and len(cpf) == 11):
        cpf = input(_msg).strip()
    return cpf

def obter_rg(_msg: str = None) -> str:
    """Obtém um número de RG (somente números, 9 dígitos) com mensagem personalizável. ex 123456789"""
    _msg = _msg or ""
    rg = ""
    while not (rg.isdigit() and len(rg) == 9):
        rg = str(input(_msg).strip())
    return rg

def obter_estado_civil(_msg: str = None) -> str:
    """Retorna o estado civil escolhido pelo usuário; recebe o menu numerado por parâmetro"""
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

def obter_endereco(_msg: str = None) -> dict:
    """Consulta a API ViaCEP com o CEP informado e retorna o endereço completo, com mensagem personalizável. ex 12345678.
    API pública ViaCEP (https://viacep.com.br)."""
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

def obter_cep(_endereco: dict) -> str:
    """Retorna o CEP do endereço obtido pela função obter_endereco()."""
    return _endereco.get("cep", "")

def obter_rua(_endereco: dict) -> str:
    """Retorna o logradouro do endereço obtido pela função obter_endereco()."""
    return _endereco.get("logradouro", "")

def obter_bairro(_endereco: dict) -> str:
    """Retorna o bairro do endereço obtido pela função obter_endereco()."""
    return _endereco.get("bairro", "")

def obter_cidade(_endereco: dict) -> str:
    """Retorna a cidade do endereço obtido pela função obter_endereco()."""
    return _endereco.get("cidade", "")

def obter_estado(_endereco: dict) -> str:
    """Retorna o estado do endereço obtido pela função obter_endereco()."""
    return _endereco.get("estado", "")

def obter_telefone(_msg: str = None) -> str:
    """Valida o telefone usando regex, garantindo 11 dígitos numéricos, com mensagem personalizável. ex 10123456789"""
    _msg = _msg or ""
    telefone = ""
    padrao = re.compile(r"^\d{11}$")

    while not padrao.match(telefone):
        telefone = str(input(_msg)).strip().replace(" ", "").replace("-", "")
    return telefone


def obter_email(_msg: str = None) -> str:
    """Valida e retorna um e-mail usando regex, garantindo formato correto (ex: nome@dominio.com)."""
    _msg = _msg or ""
    padrao = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    email = ""

    while not padrao.match(email):
        email = input(_msg).strip().lower()
    return email

# ==========================================================
#   VALIDAÇÃO DE DADOS PARA CADASTRO (CONSULTA)
# ==========================================================

def obter_data_consulta(_msg: str = None) -> datetime:
    """Obtém a data e hora da consulta no formato dd/mm/aaaa hh:mm."""
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

def obter_tipo_consulta(_msg: str = None) -> str:
    """Retorna o tipo de consulta escolhido pelo usuário; recebe o menu numerado por parâmetro, se desejado."""
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

def obter_especialidade(_msg: str = None) -> str:
    """Retorna a especialidade médica escolhida pelo usuário; recebe o menu numerado por parâmetro, se desejado."""
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

def obter_status_consulta(_msg: str = None) -> str:
    """Retorna o status da consulta escolhido pelo usuário; recebe o menu numerado por parâmetro, se desejado."""
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
    """Solicita e retorna todos os dados do paciente e da consulta em formato de dicionário."""

    # ========= DADOS DO PACIENTE =========
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

    # ========= DADOS DA CONSULTA =========
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

    # ========= RETORNO =========
    return {
        # Dados do paciente
        "nome_completo": nome_completo,
        "data_nascimento": data_nascimento,
        "sexo": sexo,
        "cpf": cpf[:11],
        "rg": rg[:9],
        "estado_civil": estado_civil[:20],
        "brasileiro": "S" if brasileiro else "N",
        "cep": obter_cep(endereco).replace("-", ""), # remove hífen
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

def solicita_campos(colunas: dict, _numeros: list) -> str:
    """Retorna os nomes das colunas selecionadas a partir dos números informados."""
    nomes = []
    for i in _numeros:
        if i in colunas:
            nomes.append(colunas[i])
    return ", ".join(nomes)

def menu_selecao_colunas(colunas: dict, _msg, _titulo) -> list:
    """Exibe um menu para o usuário selecionar colunas, permite escolher todas ('A') ou sair ('0').
    _titulo é para a função exibir_titulo_centralizado
    _msg é para a mensagem do ménu
    colunas é as colunas para exibir
    """

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

def imprimir_pacientes_tabulate(lista_de_pacientes: list, largura_max: int = 20) -> None:
    """Imprime pacientes em formato de tabela formatada."""
    lista_formatada = []

    for paciente in lista_de_pacientes:
        registro = {}

        for k, v in paciente.items():
            if v is None:
                registro[k] = ""

            elif isinstance(v, datetime):
                if v.time() == datetime.min.time():
                    registro[k] = v.strftime("%d/%m/%Y")
                else:
                    registro[k] = v.strftime("%d/%m/%Y %H:%M")

            elif isinstance(v, date):
                registro[k] = v.strftime("%d/%m/%Y")

            else:
                texto = str(v)
                linhas = []
                for i in range(0, len(texto), largura_max):
                    linhas.append(texto[i:i+largura_max])
                registro[k] = "\n".join(linhas)

        lista_formatada.append(registro)

    print(
        tabulate(
            lista_formatada,
            headers="keys",
            tablefmt="fancy_grid",
            numalign="right",
            stralign="left"
        )
    )

# ==========================================================
#   CRUD BANCO DE DADOS
# ==========================================================

# ========= CONEXÃO BANCO DE DADOS =========
def conectar_oracledb(_user: str, _password: str, _dsn: str) -> tuple[bool, any]:
    """Tenta conectar ao Oracle e retorna (True, conexão) ou (False, erro)."""
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
def verifica_tabela(_conexao: oracledb.Connection, nome_tabela: str) -> bool:
    """Verifica se a tabela possui registros e retorna True ou False."""
    cur = _conexao.cursor()
    try:
        cur.execute(f"SELECT 1 FROM {nome_tabela} WHERE ROWNUM = 1")
        resultado = cur.fetchone() # pegar apenas uma linha
        return bool(resultado)
    finally:
        cur.close()

# ========= INSERIR PACIENTE =========
def inserir_paciente(_conexao: oracledb.Connection, _dados_paciente: dict) -> tuple[bool, any]:
    """Insere um paciente no banco e retorna (True, None) se sucesso ou (False, erro) se falhar."""
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

# ========= UPDATE PACIENTE =========
def atualizar_paciente(_conexao: oracledb.Connection, _id_paciente: int, _dados_paciente: dict) -> tuple[bool, any]:
    """Atualiza os dados de um paciente pelo ID e retorna (True, None) ou (False, erro)."""
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

# ========= SELECT PACIENTE =========
def buscar_todos_pacientes_como_dicionario(_conexao: oracledb.Connection, colunas: dict, _numeros_colunas: list = None) -> list:
    """Busca todos os pacientes e retorna uma lista de dicionários com seus dados formatados."""
    
    # Se não foram passadas colunas, usa todas as chaves do dicionário 'colunas'
    if not _numeros_colunas:
        _numeros_colunas = []

        # Preenche '_numeros_colunas' com todos os índices disponíveis
        for key in colunas.keys():
            _numeros_colunas.append(key)

    # Monta a string das colunas que serão selecionadas na query
    campos_selecionados = ""
    for i, col in enumerate(_numeros_colunas):

        # Adiciona a coluna, separando por vírgula se não for a primeira
        if i == 0:
            campos_selecionados += colunas[col]
        else:
            campos_selecionados += ", " + colunas[col]

    # Executa a query e obtém os resultados
    cur = _conexao.cursor()
    cur.execute(f"SELECT {campos_selecionados} FROM T_PACIENTE")

    # Pega os nomes das colunas do resultado e transforma em maiúsculas
    nomes_colunas = []
    for col in cur.description:
        nomes_colunas.append(col[0].upper())

    # Busca todas as linhas retornadas pelo banco e fecha o cursor
    resultados_db = cur.fetchall()
    cur.close()

    # Constrói uma lista de dicionários, um para cada paciente
    lista_de_pacientes = []
    for linha in resultados_db:
        registro = {}
        for i in range(len(linha)):
            chave = nomes_colunas[i]
            valor = linha[i]

            # Converter data de nascimento para datetime.date (somente dia/mês/ano)
            if chave == "DT_NASCIMENTO" and isinstance(valor, datetime):
                registro[chave] = valor.date()  # só dia/mês/ano
            else:
                registro[chave] = valor
        lista_de_pacientes.append(registro)

    # Retorna a lista completa de pacientes como dicionários
    return lista_de_pacientes

# ========= SELECT PACIENTE POR TEXTO =========
def buscar_paciente_por_texto(_conexao: oracledb.Connection, _campo_where: str, _texto: str, _colunas_exibir: list) -> list:
    """Busca pacientes por texto em um campo e retorna lista de dicionários."""
    
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
        
        nomes_colunas = []
        for col in cur.description:
            nomes_colunas.append(col[0].upper())
            
    except Exception as e:
        print(f"\nErro ao executar consulta SQL: {e}\n")
        cur.close()
        return []
    finally:
        cur.close()

    lista_pacientes = []
    for linha in resultados:
        registro = {}
        i = 0
        for valor in linha:
            chave = nomes_colunas[i]
            registro[chave] = valor
            i += 1
        lista_pacientes.append(registro)

    return lista_pacientes

# ========= SELECT PACIENTE POR NÚMERO =========
def buscar_paciente_por_numero(_conexao: oracledb.Connection, _campo: str, _operador: str, _valor: int, _colunas_exibir: list) -> list:
    """Busca pacientes por valor numérico em um campo usando operador e retorna lista de dicionários."""
    
    campos_select = ", ".join(_colunas_exibir)
    cur = _conexao.cursor()
    comando_sql = f"SELECT {campos_select} FROM T_PACIENTE WHERE {_campo} {_operador} :valor"

    try:
        cur.execute(comando_sql, {"valor": _valor})
        resultados = cur.fetchall()
        
        # For à moda antiga para nomes das colunas
        nomes_colunas = []
        for col in cur.description:
            nomes_colunas.append(col[0].upper())
            
    except Exception as e:
        print(f"\nErro ao executar consulta SQL: {e}\n")
        cur.close()
        return []
    finally:
        cur.close()

    # For à moda antiga para criar lista de dicionários
    lista_pacientes = []
    for linha in resultados:
        registro = {}
        i = 0
        for valor in linha:
            chave = nomes_colunas[i]
            registro[chave] = valor
            i += 1
        lista_pacientes.append(registro)

    return lista_pacientes

# ========= DELETE PACIENTE =========
def deletar_paciente(_conexao: oracledb.Connection, _id_paciente: int) -> tuple[bool, any]:
    """Remove paciente pelo ID e retorna status da operação."""
    try:
        comando_sql = "DELETE FROM T_PACIENTE WHERE ID_PACIENTE = :id"
        cur = _conexao.cursor()
        cur.execute(comando_sql, {"id": _id_paciente})
        # Verifica se alguma linha foi afetada
        if cur.rowcount == 0: # verifica quantas linhas foram realmente deletadas.
            _conexao.rollback()
            cur.close()
            return (False, "Nenhum paciente encontrado com este ID para remover.")

        _conexao.commit()
        cur.close()
        return (True, None)
    except Exception as e:
        return (False, e)

# ========= DELETE TODOS OS PACIENTES =========
def limpar_todos_pacientes(_conexao: oracledb.Connection) -> tuple[bool, any]:
    """Apaga todos os pacientes do banco e retorna status da operação."""
    try:
        comando_sql = "DELETE FROM T_PACIENTE"
        cur = _conexao.cursor()
        cur.execute(comando_sql)
        
        _conexao.commit()
        cur.close()
        
        return (True, None)

    except Exception as e:
        return (False, e)

# ==========================================================
#   EXPORTAR PACIENTES PARA JSON
# ==========================================================

def exportar_para_json(_conexao: oracledb.Connection, _colunas: list, _nome_arquivo: str = "pacientes.json") -> tuple[bool, any]:
    #  """Exporta pacientes para JSON e retorna (True, None) se bem-sucedido ou (False, erro) se falhar."""
    try:
        colunas_dict = {}
        for i, c in enumerate(_colunas):
            colunas_dict[i + 1] = c

        indices = list(range(1, len(_colunas) + 1))

        lista_pacientes = buscar_todos_pacientes_como_dicionario(_conexao, colunas_dict, indices)


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
