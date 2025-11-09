# ==========================================================
#   INSTRUÇÕES PARA EXECUTAR O PROGRAMA
# ==========================================================
# 1  -   Execute o comando SQL abaixo no 'Oracle SQL Developer' para criar as tabelas necessárias.
# 2  -   Instale as bibliotecas exigidas no terminal:
#         pip install oracledb
#         pip install tabulate
#         pip install requests
#         pip install pandas

# COMANDO SQL PARA ORACLE:

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
    STATUS_CONSULTA    VARCHAR2(20),

    -- Controle de registro
    DT_CADASTRO        DATE DEFAULT SYSDATE,
    DT_ULTIMA_ATUALIZACAO TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- Trigger para atualizar automaticamente DT_ULTIMA_ATUALIZACAO
CREATE OR REPLACE TRIGGER trg_t_paciente_atualizacao
BEFORE UPDATE ON T_PACIENTE
FOR EACH ROW
BEGIN
    :NEW.DT_ULTIMA_ATUALIZACAO := SYSTIMESTAMP;
END;
"""

# Este programa utiliza a API pública do ViaCEP para consultar informações de endereços
# a partir do CEP informado pelo usuário.
# A API retorna dados como: Logradouro, Bairro, Cidade, Estado e outros dados relacionados ao CEP.

# Após isso, o código estará pronto para ser executado.

# Execute o programa pelo arquivo principal: main.py
# (no terminal: python main.py)

from cadastro_paciente import *

campos_msg = """SELECIONE OS CAMPOS QUE DESEJA VISUALIZAR:

=== DADOS PESSOAIS ===        === ENDEREÇO ===           === CONTATO / CONVÊNIO ===
1  - ID DO PACIENTE           9  - CEP                  15 - CELULAR
2  - NOME COMPLETO            10 - RUA                  16 - EMAIL
3  - DATA DE NASCIMENTO       11 - NÚMERO DO ENDEREÇO   17 - CONVÊNIO (S/N)
4  - SEXO                     12 - BAIRRO
5  - CPF                      13 - CIDADE
6  - RG                       14 - ESTADO
7  - ESTADO CIVIL
8  - BRASILEIRO (S/N)

=== CONSULTA MÉDICA ===        === CONTROLE DE REGISTRO ===
18 - DATA E HORA DA CONSULTA   22 - DATA DE CADASTRO
19 - TIPO DE CONSULTA          23 - DATA DA ÚLTIMA ATUALIZAÇÃO
20 - ESPECIALIDADE
21 - STATUS DA CONSULTA

- Digite os números dos campos separados por vírgula (por exemplo: 1,2,5,21,22,23)
- Para selecionar todos os campos, digite: A

DIGITE SUA ESCOLHA: """

campos_dict = {
    1: "ID_PACIENTE",       2: "NM_COMPLETO",       3: "DT_NASCIMENTO",
    4: "SEXO",              5: "CPF",               6: "RG",
    7: "ESTADO_CIVIL",      8: "BRASILEIRO",        9: "CEP",
    10: "RUA",              11: "NUMERO_ENDERECO",  12: "BAIRRO",
    13: "CIDADE",           14: "ESTADO",           15: "CELULAR",
    16: "EMAIL",            17: "CONVENIO",         18: "DT_HORA_CONSULTA",
    19: "TIPO_CONSULTA",    20: "ESPECIALIDADE",    21: "STATUS_CONSULTA",
    22: "DT_CADASTRO",      23: "DT_ULTIMA_ATUALIZACAO"
}


try:
    user = "rm561833"
    password = "070406"
    dsn = "oracle.fiap.com.br:1521/ORCL"
    ok, conn = conectar_oracledb(user, password, dsn)
    conectado = bool(conn)
except Exception as e:
    conectado = False

while conectado:
    limpar_terminal()
    exibir_titulo_centralizado("AXCESS TECH - SISTEMA DE GERENCIAMENTO DE PACIENTE", 60)
    print("1 - REGISTRAR PACIENTE")
    print("2 - CONSULTAR REGISTROS")
    print("3 - ATUALIZAR REGISTROS")
    print("4 - REMOVER REGISTRO")
    print("5 - LIMPAR TODOS OS REGISTROS")
    print("6 - EXPORTAÇÃO PARA JSON")
    print("0 - SAIR")
    print("")

    escolha_menu = obter_int_intervalado("Escolha: ", "Entrada inválida.", 0, 6)

    match escolha_menu:

        case 0:  # SAIR
            limpar_terminal()
            print("\nPrograma encerrado. Até logo!\n")
            conectado = False

        case 1:  # REGISTRAR PACIENTE
            limpar_terminal()
            exibir_titulo_centralizado("MENU REGISTRO PACIENTE", 60)
            sucesso_dados, dados_registro = solicitar_dados_paciente()

            if sucesso_dados:
                sucesso, erro = insert_paciente(conn, dados_registro)
                if sucesso:
                    limpar_terminal()
                    print("\nPaciente registrado com sucesso!")
                else:
                    limpar_terminal()
                    print("\nErro ao registrar paciente!")
                    print(erro)
            else:
                limpar_terminal()
                print("\nErro ao coletar os dados do paciente!")

            input("\nAperte ENTER para voltar ao menu principal...")

        case 2:  # CONSULTAR REGISTROS
            resultado = verifica_tabela(conn, "T_PACIENTE")
            if resultado:
                escolha_submenu = -1
                while escolha_submenu != 0:
                    limpar_terminal()
                    exibir_titulo_centralizado("MENU CONSULTA PACIENTE", 60)
                    print("DESEJA FAZER SUA CONSULTA POR:")
                    print("1 - TODOS OS PACIENTES")
                    print("2 - POR ID DO PACIENTE")
                    print("3 - PESQUISA DE TEXTO")
                    print("4 - PESQUISA NUMÉRICA")
                    print("0 - VOLTAR\n")

                    escolha_submenu = obter_int_intervalado("Escolha: ", "Entrada inválida.", 0, 5)

                    match escolha_submenu:
                        case 0:  # VOLTAR
                            break

                        case 1:  # TODOS OS PACIENTES
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA - TODOS OS PACIENTES", 60)
                            texto, lista = obter_multiplas_opcoes_dict(
                                campos_msg,
                                "Erro! Escolha os campos separando os números por ',' .",
                                campos_dict
                            )

                            sucesso, busca = select_paciente(conn, texto)
                            if sucesso:
                                sucesso, tabela = imprimir_resultado_tabulate_oracle(busca)
                                if sucesso:
                                    limpar_terminal()
                                    exibir_titulo_centralizado("CONSULTA - TODOS OS PACIENTES", 60)
                                    print(tabela)
                                else:
                                    limpar_terminal()
                                    print("\nErro ao formatar os resultados:")
                                    print(tabela)
                            else:
                                limpar_terminal()
                                print("\nErro ao consultar pacientes no banco de dados:")
                                print(busca)

                            input("\nAperte ENTER para voltar ao menu de consulta...")

                        case 2:  # POR ID DO PACIENTE
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA - PACIENTE POR ID", 60)

                            # Obter preview dos pacientes existentes
                            sucesso_select, resultados_preview = select_paciente(
                                conn, "ID_PACIENTE, NM_COMPLETO, TIPO_CONSULTA, STATUS_CONSULTA"
                            )

                            if sucesso_select:
                                sucesso_preview, tabela_preview = imprimir_resultado_tabulate_oracle(resultados_preview)
                            else:
                                sucesso_preview = False
                                tabela_preview = f"Erro ao consultar pacientes: {resultados_preview}"

                            if sucesso_preview:
                                resp = True
                                while resp:
                                    limpar_terminal()
                                    exibir_titulo_centralizado("CONSULTA - PACIENTE POR ID", 60)
                                    print(tabela_preview)

                                    resp = obter_sim_nao("Deseja pesquisar consulta por ID? (S/N): ", "Erro. Digite S ou N.")
                                    if resp:
                                        _id_paciente = obter_int("\nDigite o ID do paciente: ", "ID inválido. Digite um número inteiro.")
                                        
                                        limpar_terminal()
                                        exibir_titulo_centralizado("CONSULTA - PACIENTE POR ID", 60)
                                        
                                        texto, lista = obter_multiplas_opcoes_dict(
                                            campos_msg,
                                            "Erro! Escolha os campos separando os números por ',' .",
                                            campos_dict
                                        )
                                        
                                        try:
                                            # Desempacotar corretamente a tupla retornada
                                            sucesso_select_id, resultados = select_paciente_por_id(conn, texto, _id_paciente)

                                            if not resultados:  # lista vazia
                                                limpar_terminal()
                                                print(f"\nNenhum paciente encontrado com ID {_id_paciente}.")
                                            else:
                                                sucesso, tabela = imprimir_resultado_tabulate_oracle(resultados)
                                                if sucesso:
                                                    limpar_terminal()
                                                    exibir_titulo_centralizado(f"PACIENTE - ID {_id_paciente}", 60)
                                                    print(tabela)
                                                else:
                                                    limpar_terminal()
                                                    print("\nErro ao formatar os resultados:")
                                                    print(tabela)

                                        except Exception as e:
                                            limpar_terminal()
                                            print("\nErro ao consultar paciente no banco de dados:")
                                            print(e)

                                        input("\nAperte ENTER para continuar...")
                                    else:
                                        break
                            else:
                                limpar_terminal()
                                print(f"\nNão foi possível exibir o preview dos pacientes.\n{tabela_preview}")
                                input("\nAperte ENTER para voltar ao menu principal...")

                        case 3:  # PESQUISA DE TEXTO
                            limpar_terminal()
                            exibir_titulo_centralizado("PESQUISA DE TEXTO - PACIENTES", 60)

                            # Preview dos pacientes para referência
                            sucesso_select, resultados_preview = select_paciente(
                                conn, "ID_PACIENTE, NM_COMPLETO, TIPO_CONSULTA, STATUS_CONSULTA"
                            )

                            if sucesso_select:
                                sucesso_preview, tabela_preview = imprimir_resultado_tabulate_oracle(resultados_preview)
                            else:
                                sucesso_preview = False
                                tabela_preview = f"Erro ao consultar pacientes: {resultados_preview}"

                            if sucesso_preview:
                                resp = True
                                while resp:
                                    limpar_terminal()
                                    exibir_titulo_centralizado("PESQUISA DE TEXTO - PACIENTES", 60)
                                    print(tabela_preview)

                                    resp = obter_sim_nao("Deseja pesquisar paciente por texto? (S/N): ", "Erro. Digite S ou N.")
                                    print("")
                                    if resp:
                                        # Campo para busca textual
                                        campo_busca_dict = {
                                            1: "NM_COMPLETO",
                                            2: "ESTADO_CIVIL",
                                            3: "RUA",
                                            4: "BAIRRO",
                                            5: "CIDADE",
                                            6: "EMAIL",
                                            7: "TIPO_CONSULTA",
                                            8: "ESPECIALIDADE",
                                            9: "STATUS_CONSULTA"
                                        }

                                        campo_busca = obter_opcao_dict(
                                            """Escolha o campo para pesquisar por texto:
1 - Nome
2 - Estado Civil
3 - Rua
4 - Bairro
5 - Cidade
6 - E-mail
7 - Tipo de Consulta
8 - Especialidade
9 - Status da Consulta
Escolha: """,
                                            "Opção inválida!",
                                            campo_busca_dict
                                        )

                                        texto_pesquisa = obter_texto("\nDigite o texto a ser pesquisado: ", "Entrada inválida!")

                                        limpar_terminal()
                                        exibir_titulo_centralizado("PESQUISA DE TEXTO - PACIENTES", 60)
                                        # Seleção de colunas para exibição
                                        texto_colunas, lista_colunas = obter_multiplas_opcoes_dict(
                                            campos_msg,
                                            "Erro! Escolha os campos separando os números por ',' .",
                                            campos_dict
                                        )

                                        # Buscar pacientes
                                        resultados = buscar_paciente_por_texto(conn, campo_busca, texto_pesquisa, texto_colunas)

                                        if not resultados:
                                            limpar_terminal()
                                            print(f"\nNenhum paciente encontrado com '{texto_pesquisa}' no campo {campo_busca}.")
                                        else:
                                            sucesso, tabela = imprimir_resultado_tabulate_oracle(resultados)
                                            if sucesso:
                                                limpar_terminal()
                                                exibir_titulo_centralizado(f"RESULTADOS DA PESQUISA - {campo_busca}", 60)
                                                print(tabela)
                                            else:
                                                limpar_terminal()
                                                print("\nErro ao formatar os resultados:")
                                                print(tabela)

                                        input("\nAperte ENTER para continuar...")
                                    else:
                                        break
                            else:
                                limpar_terminal()
                                print(f"\nNão foi possível exibir o preview dos pacientes.\n{tabela_preview}")
                                input("\nAperte ENTER para voltar ao menu principal...")

                        case 4:  # PESQUISA NUMÉRICA
                            limpar_terminal()
                            exibir_titulo_centralizado("PESQUISA NUMÉRICA - PACIENTES", 60)

                            # Preview dos pacientes para referência
                            sucesso_select, resultados_preview = select_paciente(
                                conn, "ID_PACIENTE, NM_COMPLETO, TIPO_CONSULTA, STATUS_CONSULTA"
                            )

                            if sucesso_select:
                                sucesso_preview, tabela_preview = imprimir_resultado_tabulate_oracle(resultados_preview)
                            else:
                                sucesso_preview = False
                                tabela_preview = f"Erro ao consultar pacientes: {resultados_preview}"

                            if sucesso_preview:
                                resp = True
                                while resp:
                                    limpar_terminal()
                                    exibir_titulo_centralizado("PESQUISA NUMÉRICA - PACIENTES", 60)
                                    print(tabela_preview)

                                    resp = obter_sim_nao("Deseja pesquisar paciente por valor numérico? (S/N): ", "Erro. Digite S ou N.")
                                    if not resp:
                                        break

                                    # Escolher o campo numérico para pesquisa
                                    campo_busca_dict = {1:"ID_PACIENTE",2:"NUMERO_ENDERECO"}
                                    print()
                                    campo_busca = obter_opcao_dict(
                                        """Escolha o campo numérico para pesquisar:
1. ID_PACIENTE
2. NUMERO_ENDERECO"

Escolha: """,
                                        "Opção inválida!",
                                        campo_busca_dict
                                    )

                                    valor = obter_int("\nDigite o valor para pesquisa: ", "Entrada inválida. Digite um número inteiro.")

                                    print()
                                    operador = obter_opcao_dict(
                                        """Escolha o operador para pesquisa:
1. Igual (=)
2. Maior (>)
3. Menor (<)
4. Maior ou igual (>=)
5. Menor ou igual (<=)
6. Diferente (<>)
Escolha: """,
                                        "Opção inválida!",
                                        {1: "=", 2: ">", 3: "<", 4: ">=", 5: "<=", 6: "<>"}
                                    )


                                    # Seleção de colunas para exibição
                                    limpar_terminal()
                                    exibir_titulo_centralizado("PESQUISA NUMÉRICA - PACIENTES", 60)
                                    texto_colunas, lista_colunas = obter_multiplas_opcoes_dict(
                                        campos_msg,
                                        "Erro! Escolha os campos separando os números por ',' .",
                                        campos_dict
                                    )

                                    # Buscar pacientes
                                    resultados = buscar_paciente_por_numero(conn, campo_busca, operador, valor, texto_colunas)

                                    if not resultados:
                                        limpar_terminal()
                                        print(f"\nNenhum paciente encontrado com {campo_busca} {operador} {valor}.")
                                    else:
                                        sucesso, tabela = imprimir_resultado_tabulate_oracle(resultados)
                                        if sucesso:
                                            limpar_terminal()
                                            exibir_titulo_centralizado(f"RESULTADOS DA PESQUISA - {campo_busca}", 60)
                                            print(tabela)
                                        else:
                                            limpar_terminal()
                                            print("\nErro ao formatar os resultados:")
                                            print(tabela)

                                    input("\nAperte ENTER para continuar...")
                            else:
                                limpar_terminal()
                                print(f"\nNão foi possível exibir o preview dos pacientes.\n{tabela_preview}")
                                input("\nAperte ENTER para voltar ao menu principal...")

            else:
                limpar_terminal()
                print("\nNenhum registro encontrado na tabela T_PACIENTE para consulta.")
                input("\nAperte ENTER para voltar ao menu principal...")

        case 3:  # ATUALIZAR REGISTROS
            limpar_terminal()
            exibir_titulo_centralizado("ATUALIZAR REGISTROS", 60)

            # Preview dos pacientes para referência
            sucesso_select, resultados_preview = select_paciente(
                conn, "ID_PACIENTE, NM_COMPLETO, TIPO_CONSULTA, STATUS_CONSULTA"
            )

            if sucesso_select:
                sucesso_preview, tabela_preview = imprimir_resultado_tabulate_oracle(resultados_preview)
            else:
                sucesso_preview = False
                tabela_preview = f"Erro ao consultar pacientes: {resultados_preview}"

            if sucesso_preview:
                resp = True
                while resp:
                    limpar_terminal()
                    exibir_titulo_centralizado("ATUALIZAR REGISTROS", 60)
                    print(tabela_preview)

                    resp = obter_sim_nao("Deseja atualizar algum paciente? (S/N): ", "Erro. Digite S ou N.")
                    if not resp:
                        break

                    # Selecionar paciente pelo ID
                    _id_paciente = obter_int("\nDigite o ID do paciente que deseja atualizar: ", "ID inválido. Digite um número inteiro.")

                    # Buscar paciente específico
                    sucesso, resultados = select_paciente_por_id(conn, "*", _id_paciente)
                    if not resultados:
                        limpar_terminal()
                        print(f"\nNenhum paciente encontrado com ID {_id_paciente}.")
                        input("\nAperte ENTER para voltar ao menu de atualização...")
                        continue

                    # Exibir paciente selecionado verticalmente
                    limpar_terminal()
                    exibir_titulo_centralizado(f"PACIENTE - ID {_id_paciente}", 60)
                    imprimir_resultado_vertical_oracle(resultados)

                    # Dicionário de campos possíveis para atualização
                    campos_dict = {
                        1: "NM_COMPLETO",
                        2: "DATA_NASCIMENTO",
                        3: "SEXO",
                        4: "CPF",
                        5: "RG",
                        6: "ESTADO_CIVIL",
                        7: "BRASILEIRO",
                        8: "ENDERECO",
                        9: "NUMERO_ENDERECO",
                        10: "CELULAR",
                        11: "EMAIL",
                        12: "CONVENIO",
                        13: "DATA_HORA_CONSULTA",
                        14: "TIPO_CONSULTA",
                        15: "ESPECIALIDADE",
                        16: "STATUS_CONSULTA"
                    }

                    print()
                    # Escolher campo para atualizar
                    campo = obter_opcao_dict("""Escolha o campo que deseja atualizar:
1 - Nome
2 - Data de Nascimento
3 - Sexo
4 - CPF
5 - RG
6 - Estado Civil
7 - Brasileiro?
8 - Endereço
9 - Número do Endereço
10 - Celular
11 - E-mail
12 - Convênio
13 - Data/Hora Consulta
14 - Tipo de Consulta
15 - Especialidade
16 - Status da Consulta
Escolha: """,
                        "Opção inválida!",
                        campos_dict
                    )

                    # Chamar a função de atualização
                    sucesso_update, erro = atualizar_coluna_paciente(conn, _id_paciente, campo)

                    if sucesso_update:
                        limpar_terminal()
                        print(f"\nCampo '{campo}' atualizado com sucesso!")
                    else:
                        limpar_terminal()
                        print(f"\nErro ao atualizar o campo '{campo}': {erro}")

                    input("\nAperte ENTER para continuar...")
            else:
                limpar_terminal()
                print(f"\nNão foi possível exibir o preview dos pacientes.\n{tabela_preview}")
                input("\nAperte ENTER para voltar ao menu principal...")



        case 4:  # REMOVER REGISTRO
            limpar_terminal()
            exibir_titulo_centralizado("REMOVER REGISTRO", 60)

            # Preview dos pacientes para referência
            sucesso_select, resultados_preview = select_paciente(
                conn, "ID_PACIENTE, NM_COMPLETO, TIPO_CONSULTA, STATUS_CONSULTA"
            )

            if sucesso_select:
                sucesso_preview, tabela_preview = imprimir_resultado_tabulate_oracle(resultados_preview)
            else:
                sucesso_preview = False
                tabela_preview = f"Erro ao consultar pacientes: {resultados_preview}"

            if sucesso_preview:
                resp = True
                while resp:
                    limpar_terminal()
                    exibir_titulo_centralizado("REMOVER REGISTRO", 60)
                    print(tabela_preview)

                    resp = obter_sim_nao("Deseja remover algum paciente por ID? (S/N): ", "Erro. Digite S ou N.")
                    if resp:
                        _id_paciente = obter_int("\nDigite o ID do paciente a ser removido: ", "ID inválido. Digite um número inteiro.")

                        confirmar = obter_sim_nao(f"\nTem certeza que deseja remover o paciente ID {_id_paciente}? (S/N): ", "Erro. Digite S ou N.")
                        if confirmar:
                            sucesso, erro = deletar_paciente(conn, _id_paciente)
                            if sucesso:
                                print(f"\nPaciente ID {_id_paciente} removido com sucesso!")
                            else:
                                print(f"\nErro ao remover paciente: {erro}")

                        input("\nAperte ENTER para continuar...")
                    else:
                        break
            else:
                limpar_terminal()
                print(f"\nNão foi possível exibir o preview dos pacientes.\n{tabela_preview}")
                input("\nAperte ENTER para voltar ao menu principal...")

        case 5:  # LIMPAR TODOS OS REGISTROS
            limpar_terminal()
            exibir_titulo_centralizado("LIMPAR TODOS OS REGISTROS", 60)

            confirmar = obter_sim_nao("Tem certeza que deseja apagar TODOS os registros de pacientes? (S/N): ", "Erro. Digite S ou N.")
            if confirmar:
                sucesso, erro = limpar_todos_pacientes(conn)
                if sucesso:
                    print("\nTodos os registros de pacientes foram apagados com sucesso!")
                else:
                    print(f"\nErro ao apagar registros: {erro}")
            else:
                print("\nOperação cancelada pelo usuário.")

            input("\nAperte ENTER para voltar ao menu principal...")
        case 6:  # EXPORTAÇÃO PARA JSON
            limpar_terminal()
            exibir_titulo_centralizado("EXPORTAÇÃO PARA JSON", 60)

            # Perguntar ao usuário o nome do arquivo (opcional)
            nome_arquivo = input("Digite o nome do arquivo para exportação (padrão: pacientes.json): ").strip()
            if not nome_arquivo:
                nome_arquivo = "pacientes.json"

            sucesso, erro = exportar_para_json(conn, nome_arquivo)

            if sucesso:
                print(f"\nExportação concluída com sucesso! Arquivo salvo como '{nome_arquivo}'.")
            else:
                print(f"\nErro ao exportar para JSON: {erro}")

            input("\nAperte ENTER para voltar ao menu principal...")