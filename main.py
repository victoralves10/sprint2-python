from cadastro_paciente import *

'''
limpar_terminal()

user = "rm561833"
password = "070406"
dsn = "oracle.fiap.com.br:1521/ORCL"

# Tenta conectar ao banco
sucesso, resultado = conectar_oracledb(user, password, dsn)

if not sucesso:
    print("Erro ao conectar ao banco de dados!\n")
    print("Detalhes:\n", resultado)
else:
    conn = resultado  # objeto de conexão
    conectado = True

# Loop do menu principal
while conectado:
    limpar_terminal()
    exibir_titulo_centralizado("AXCESS TECH - FICHA PACIENTE", 60)
    print("""
1. Cadastrar paciente
2. Consultar registros
3. Atualizar registros
4. Remover registros
5. Limpar todos os registros

0. Sair
""")

    escolha_menu = obter_int_invervalado("Escolha: ", 0, 5)

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

    match escolha_menu:
        case 0:
            limpar_terminal()
            print("\nPrograma encerrado. Até logo!\n")
            conectado = False

        case 1:
            limpar_terminal()
            exibir_titulo_centralizado("FICHA DE CADASTRO", 60)
            dados_do_registro = solicitar_dados_paciente()
            sucesso, erro = inserir_paciente(conn, dados_do_registro)

            if sucesso:
                print("\nPaciente registrado com sucesso!")
            else:
                print("\nErro ao registrar paciente!")
                print(erro)

            input("\nPressione ENTER para continuar...")

        case 2:
            if not verifica_tabela(conn, "T_PACIENTE"):
                limpar_terminal()
                exibir_titulo_centralizado("CONSULTA / LISTA DE PACIENTE", 60)
                print("\nNenhum paciente encontrado.\n")
                input("\nPressione ENTER para continuar...")
            else:
                escolha_submenu = -1
                while escolha_submenu != 0:
                    limpar_terminal()
                    exibir_titulo_centralizado("CONSULTA / LISTA DE PACIENTE", 60)
                    print("""
1. Listar todos os pacientes
2. Consultar paciente por ID
3. Pesquisar por texto
4. Pesquisar por número
5. Exportar para JSON

0. Voltar ao menu principal
""")
                    escolha_submenu = obter_int_invervalado("Escolha: ", 0, 5)

                    match escolha_submenu:
                        case 0:
                            break

                        case 1:
                            limpar_terminal()
                            exibir_titulo_centralizado("LISTA DE TODOS PACIENTE", 60)
                            msg = """ SELECIONE OS CAMPOS QUE DESEJA VER

1 - ID_PACIENTE         12 - CIDADE 
2 - NM_COMPLETO         13 - ESTADO
3 - DT_NASCIMENTO       14 - NUMERO_ENDERECO
4 - SEXO                15 - CELULAR
5 - CPF                 16 - EMAIL
6 - RG                  17 - CONVENIO
7 - ESTADO_CIVIL        18 - DT_HORA_CONSULTA
8 - BRASILEIRO          19 - TIPO_CONSULTA
9 - CEP                 20 - ESPECIALIDADE
10 - RUA                21 - STATUS_CONSULTA
11 - BAIRRO

Digite 'A' para selecionar todas ou '0' para finalizar a seleção.
"""
                            numeros_colunas = menu_selecao_colunas(colunas, msg, "LISTA DE TODOS PACIENTE")
                            if not numeros_colunas:
                                print("\nNenhuma coluna selecionada. Voltando ao menu...\n")
                                input("Pressione ENTER para continuar...")
                                continue

                            pacientes = buscar_todos_pacientes_como_dicionario(conn, colunas, numeros_colunas)

                            if pacientes:
                                limpar_terminal()
                                exibir_titulo_centralizado("LISTA DE TODOS PACIENTE", 60)
                                imprimir_pacientes_tabulate(pacientes)
                            else:
                                print("\nNenhum paciente encontrado.\n")

                            input("\nPressione ENTER para continuar...")

                        case 2:
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA DE PACIENTE POR ID", 60)

                            preview_colunas = {
                                1: "ID_PACIENTE",
                                2: "NM_COMPLETO",
                                3: "TIPO_CONSULTA",
                                4: "STATUS_CONSULTA"
                            }
                            numeros_preview = [1, 2, 3, 4]
                            pacientes_preview = buscar_todos_pacientes_como_dicionario(conn, preview_colunas, numeros_preview)

                            if not pacientes_preview:
                                print("\nNenhum paciente encontrado.\n")
                                input("\nPressione ENTER para continuar...")
                                continue

                            print("Lista de pacientes cadastrados (preview):\n")
                            imprimir_pacientes_tabulate(pacientes_preview)

                            continuar = True
                            while continuar:
                                id_escolhido = obter_int("\nDigite o ID do paciente que deseja consultar (0 para voltar): ")

                                if id_escolhido == 0:
                                    continuar = False
                                else:
                                    id_encontrado = False
                                    for paciente in pacientes_preview:
                                        if paciente.get("ID_PACIENTE") == id_escolhido:
                                            id_encontrado = True
                                            break
                                    if not id_encontrado:
                                        print(f"\nErro: nenhum paciente encontrado com ID {id_escolhido}.")
                                    else:
                                        continuar = False

                            if id_escolhido == 0:
                                continue

                            msg_colunas = """ SELECIONE OS CAMPOS QUE DESEJA VER
                            
1 - ID_PACIENTE         12 - CIDADE 
2 - NM_COMPLETO         13 - ESTADO
3 - DT_NASCIMENTO       14 - NUMERO_ENDERECO
4 - SEXO                15 - CELULAR
5 - CPF                 16 - EMAIL
6 - RG                  17 - CONVENIO
7 - ESTADO_CIVIL        18 - DT_HORA_CONSULTA
8 - BRASILEIRO          19 - TIPO_CONSULTA
9 - CEP                 20 - ESPECIALIDADE
10 - RUA                21 - STATUS_CONSULTA
11 - BAIRRO

Digite 'A' para selecionar todas ou '0' para finalizar a seleção.
"""
                            colunas_exibir_idx = menu_selecao_colunas(colunas, msg_colunas, "COLUNAS PARA EXIBIÇÃO")
                            if not colunas_exibir_idx:
                                print("\nNenhuma coluna selecionada. Voltando ao menu...\n")
                                input("Pressione ENTER para continuar...")
                                continue

                            colunas_exibir = [colunas[i] for i in colunas_exibir_idx]

                            cur = conn.cursor()
                            campos_select = ", ".join(colunas_exibir)
                            comando_sql = f"SELECT {campos_select} FROM T_PACIENTE WHERE ID_PACIENTE = :id"
                            cur.execute(comando_sql, {"id": id_escolhido})
                            resultados = cur.fetchall()
                            nomes_colunas = [col[0].upper() for col in cur.description]
                            cur.close()

                            lista_paciente = []
                            for linha in resultados:
                                registro = {nomes_colunas[i]: linha[i] for i in range(len(nomes_colunas))}
                                lista_paciente.append(registro)

                            limpar_terminal()
                            exibir_titulo_centralizado(f"RESULTADO DA CONSULTA - ID {id_escolhido}", 60)
                            if lista_paciente:
                                imprimir_pacientes_tabulate(lista_paciente)
                            else:
                                print("\nNenhum paciente encontrado.\n")

                            input("\nPressione ENTER para continuar...")

                        case 3:
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA DE PACIENTE POR TEXTO", 100)

                            campos_textuais = {
                                1: "NM_COMPLETO",
                                2: "ESTADO_CIVIL",
                                3: "BAIRRO",
                                4: "CIDADE",
                                5: "ESTADO",
                                6: "CELULAR",
                                7: "EMAIL",
                                8: "ESPECIALIDADE",
                                9: "STATUS_CONSULTA",
                                10: "TIPO_CONSULTA"
                            }
                            print("\nEscolha o campo textual para buscar:")
                            for k, v in campos_textuais.items():
                                print(f"{k}. {v}")

                            escolha_campo = obter_int_invervalado("Campo: ", 1, 10)
                            campo_where = campos_textuais[escolha_campo]

                            texto_busca = input("\nDigite o texto para buscar: ").strip()

                            msg_colunas = """ SELECIONE OS CAMPOS QUE DESEJA VER
                            
1 - ID_PACIENTE         12 - CIDADE 
2 - NM_COMPLETO         13 - ESTADO
3 - DT_NASCIMENTO       14 - NUMERO_ENDERECO
4 - SEXO                15 - CELULAR
5 - CPF                 16 - EMAIL
6 - RG                  17 - CONVENIO
7 - ESTADO_CIVIL        18 - DT_HORA_CONSULTA
8 - BRASILEIRO          19 - TIPO_CONSULTA
9 - CEP                 20 - ESPECIALIDADE
10 - RUA                21 - STATUS_CONSULTA
11 - BAIRRO

Digite 'A' para selecionar todas ou '0' para finalizar a seleção.
"""
                            colunas_exibir_idx = menu_selecao_colunas(colunas, msg_colunas, "COLUNAS PARA EXIBIÇÃO")
                            if not colunas_exibir_idx:
                                print("\nNenhuma coluna selecionada. Voltando ao menu...\n")
                                input("Pressione ENTER para continuar...")
                                continue
                            
                            colunas_exibir = [colunas[i] for i in colunas_exibir_idx]

                            pacientes = buscar_paciente_por_texto(conn, campo_where, texto_busca, colunas_exibir)

                            limpar_terminal()
                            exibir_titulo_centralizado("RESULTADO DA BUSCA", 100)
                            if pacientes:
                                imprimir_pacientes_tabulate(pacientes)
                            else:
                                print("\nNenhum paciente encontrado.\n")

                            input("\nPressione ENTER para continuar...")

                        case 4:
                            limpar_terminal()
                            exibir_titulo_centralizado("CONSULTA DE PACIENTE POR NÚMERO", 60)

                            campos_numericos = {
                                1: "ID_PACIENTE",
                                2: "NUMERO_ENDERECO"
                            }
                            print("Escolha o campo numérico para buscar:")
                            for k, v in campos_numericos.items():
                                print(f"{k}. {v}")

                            escolha_campo = obter_int_invervalado("Campo: ", 1, len(campos_numericos))
                            campo_where = campos_numericos[escolha_campo]

                            valor = obter_int(f"\nDigite o número para buscar em {campo_where}: ")

                            operadores = {1: "=", 2: ">", 3: "<", 4: ">=", 5: "<=", 6: "!="}
                            print("\nEscolha o operador:")
                            for k, v in operadores.items():
                                print(f"{k} - {v}")

                            opcao_operador = obter_int_invervalado("Operador: ", 1, 6)
                            operador = operadores[opcao_operador]

                            msg_colunas = """ SELECIONE OS CAMPOS QUE DESEJA VER
                            
1 - ID_PACIENTE         12 - CIDADE 
2 - NM_COMPLETO         13 - ESTADO
3 - DT_NASCIMENTO       14 - NUMERO_ENDERECO
4 - SEXO                15 - CELULAR
5 - CPF                 16 - EMAIL
6 - RG                  17 - CONVENIO
7 - ESTADO_CIVIL        18 - DT_HORA_CONSULTA
8 - BRASILEIRO          19 - TIPO_CONSULTA
9 - CEP                 20 - ESPECIALIDADE
10 - RUA                21 - STATUS_CONSULTA
11 - BAIRRO

Digite 'A' para selecionar todas ou '0' para finalizar a seleção.
"""
                            colunas_exibir_idx = menu_selecao_colunas(colunas, msg_colunas, "COLUNAS PARA EXIBIÇÃO")
                            if not colunas_exibir_idx:
                                print("\nNenhuma coluna selecionada. Voltando ao menu...\n")
                                input("Pressione ENTER para continuar...")
                                continue

                            colunas_exibir = [colunas[i] for i in colunas_exibir_idx]

                            pacientes = buscar_paciente_por_numero(conn, campo_where, operador, valor, colunas_exibir)

                            limpar_terminal()
                            exibir_titulo_centralizado("RESULTADO DA BUSCA POR NÚMERO", 60)
                            if pacientes:
                                imprimir_pacientes_tabulate(pacientes)
                            else:
                                print("\nNenhum paciente encontrado.\n")

                            input("\nPressione ENTER para continuar...")

                        case 5:
                            limpar_terminal()
                            exibir_titulo_centralizado("EXPORTAÇÃO PARA JSON", 60)

                            msg_colunas = """ SELECIONE OS CAMPOS QUE DESEJA VER
                            
1 - ID_PACIENTE         12 - CIDADE 
2 - NM_COMPLETO         13 - ESTADO
3 - DT_NASCIMENTO       14 - NUMERO_ENDERECO
4 - SEXO                15 - CELULAR
5 - CPF                 16 - EMAIL
6 - RG                  17 - CONVENIO
7 - ESTADO_CIVIL        18 - DT_HORA_CONSULTA
8 - BRASILEIRO          19 - TIPO_CONSULTA
9 - CEP                 20 - ESPECIALIDADE
10 - RUA                21 - STATUS_CONSULTA
11 - BAIRRO

Digite 'A' para selecionar todas ou '0' para finalizar a seleção.
"""
                            colunas_exibir_idx = menu_selecao_colunas(colunas, msg_colunas, "COLUNAS PARA EXPORTAÇÃO")

                            if not colunas_exibir_idx:
                                print("\nNenhuma coluna selecionada. Voltando ao menu...\n")
                                input("Pressione ENTER para continuar...")
                                continue

                            colunas_exibir = [colunas[i] for i in colunas_exibir_idx]

                            nome_arquivo = input("\nDigite o nome do arquivo (sem extensão): ").strip()
                            if not nome_arquivo:
                                print("\nNome inválido. Voltando ao menu...\n")
                                input("Pressione ENTER para continuar...")
                                continue

                            nome_arquivo = nome_arquivo + ".json"

                            sucesso, erro = exportar_para_json(conn, colunas_exibir, nome_arquivo)

                            limpar_terminal()
                            if sucesso:
                                print(f"\nArquivo '{nome_arquivo}' gerado com sucesso!\n")
                            else:
                                print(f"\nFalha ao gerar arquivo JSON: {erro}\n")

                            input("\nPressione ENTER para continuar...")
        case 3:
            limpar_terminal()
            exibir_titulo_centralizado("ATUALIZAÇÃO DE PACIENTE", 60)

            pacientes_preview = buscar_todos_pacientes_como_dicionario(conn, colunas, [1, 2, 21])
            if pacientes_preview:
                print("Lista de pacientes cadastrados (preview):\n")
                imprimir_pacientes_tabulate(pacientes_preview)
            else:
                print("Nenhum paciente cadastrado no sistema.")
                input("\nPressione ENTER para voltar ao menu...")
                continue

            print("\nDigite o ID do paciente que deseja atualizar.")
            print("Ou digite 0 para voltar ao menu anterior.\n")

            id_paciente = obter_int("ID do paciente: ")

            if id_paciente == 0:
                print("\nVoltando ao menu principal...")
                input("\nPressione ENTER para continuar...")
                limpar_terminal()
                continue

            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM T_PACIENTE WHERE ID_PACIENTE = :id", {"id": id_paciente})
            existe = cur.fetchone()[0]
            cur.close()

            if not existe:
                print(f"\nNenhum paciente encontrado com o ID {id_paciente}.")
                input("\nPressione ENTER para continuar...")
                continue

            limpar_terminal()
            exibir_titulo_centralizado("ATUALIZAÇÃO DE DADOS", 60)
            print(f"Atualizando paciente com ID: {id_paciente}\n")

            novos_dados = solicitar_dados_paciente()

            print("\nDeseja realmente atualizar os dados deste paciente?")
            if not obter_sim_nao("Confirmar atualização? [S/N]: "):
                print("\nOperação cancelada pelo usuário.")
                input("\nPressione ENTER para continuar...")
                continue

            sucesso, erro = atualizar_paciente(conn, id_paciente, novos_dados)

            if sucesso:
                print("\nPaciente atualizado com sucesso!")
            else:
                print(f"\nErro ao atualizar paciente: {erro}")

            input("\nPressione ENTER para continuar...")
            limpar_terminal()
        case 4:
            id_paciente_remover = -1

            if not verifica_tabela(conn, "T_PACIENTE"):
                limpar_terminal()
                exibir_titulo_centralizado("REMOVER REGISTROS", 60)
                print("\nNenhum paciente encontrado para remover.\n")
                input("\nPressione ENTER para continuar...")
                continue

            while id_paciente_remover != 0:
                limpar_terminal()
                exibir_titulo_centralizado("REMOVER REGISTROS", 60)

                colunas_preview = {1: "ID_PACIENTE", 2: "NM_COMPLETO", 3: "STATUS_CONSULTA"}
                pacientes_preview = buscar_todos_pacientes_como_dicionario(conn, colunas_preview, [1, 2, 3])

                if pacientes_preview:
                    print("\nESCOLHA O ID DO PACIENTE QUE DESEJA REMOVER:\n")
                    imprimir_pacientes_tabulate(pacientes_preview)
                    print("\nDIGITE '0' PARA VOLTAR AO MENU PRINCIPAL\n")
                    id_paciente_remover = obter_int("\nDigite o ID do paciente: ")
                else:
                    id_paciente_remover = 0
                    continue

                if id_paciente_remover == 0:
                    break

                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM T_PACIENTE WHERE ID_PACIENTE = :id", {"id": id_paciente_remover})
                existe = cur.fetchone()[0]
                cur.close()

                if not existe:
                    limpar_terminal()
                    exibir_titulo_centralizado("REMOVER REGISTROS", 60)
                    print(f"\nNenhum paciente encontrado com o ID {id_paciente_remover}.\n")
                    input("\nPressione ENTER para continuar...")
                    continue

                colunas_detalhes = [colunas[i] for i in range(1, 22)]
                cur = conn.cursor()
                campos_select = ", ".join(colunas_detalhes)
                comando_sql = f"SELECT {campos_select} FROM T_PACIENTE WHERE ID_PACIENTE = :id"
                cur.execute(comando_sql, {"id": id_paciente_remover})
                resultados = cur.fetchall()
                nomes_colunas = [col[0].upper() for col in cur.description]
                cur.close()

                lista_detalhes = []
                for linha in resultados:
                    registro = {nomes_colunas[i]: linha[i] for i in range(len(nomes_colunas))}
                    lista_detalhes.append(registro)

                limpar_terminal()
                exibir_titulo_centralizado(f"CONFIRMAÇÃO DE REMOÇÃO - ID {id_paciente_remover}", 60)

                if lista_detalhes:
                    print("DADOS ATUAIS")
                    imprimir_pacientes_tabulate(lista_detalhes)
                    escolha = obter_sim_nao("\nDESEJA EXCLUIR ESTE REGISTRO? (S/N): ")

                    if escolha:
                        sucesso, erro = deletar_paciente(conn, id_paciente_remover)
                        if sucesso:
                            print("\nPaciente removido com sucesso!")
                        else:
                            print(f"\nErro ao remover o paciente: {erro}\n")
                    else:
                        print("\nRemoção cancelada pelo usuário.\n")
                else:
                    print("\nNenhum paciente encontrado com esse ID.\n")

                input("\nPressione ENTER para continuar...")

        case 5:
            limpar_terminal()
            exibir_titulo_centralizado("REMOVER TODOS OS REGISTROS", 60)

            # Preview para verificar se há registros antes da confirmação
            colunas_preview = {1: "ID_PACIENTE", 2: "NM_COMPLETO", 3: "STATUS_CONSULTA"}
            pacientes_preview = buscar_todos_pacientes_como_dicionario(conn, colunas_preview, [1, 2, 3])

            if not pacientes_preview:
                print("\nNenhum paciente encontrado para ser removido.\n")
            else:
                print("\nATENÇÃO: VOCÊ ESTÁ PRESTES A EXCLUIR TODOS OS REGISTROS.\n")
                print("REGISTROS ATUAIS (PREVIEW):\n")
                imprimir_pacientes_tabulate(pacientes_preview)

                confirmacao = obter_sim_nao("\nCONFIRMA A EXCLUSÃO DE TODOS OS PACIENTES? [S]im ou [N]ÃO? ")

                if confirmacao:
                    sucesso, erro = limpar_todos_pacientes(conn)
                    if sucesso:
                        print("\nTODOS OS REGISTROS FORAM REMOVIDOS COM SUCESSO\n")
                    else:
                        print("\nErro ao remover os registros.\n")
                        print(f"Detalhes do erro: {erro}")
                else:
                    print("\nOperação cancelada pelo usuário.\n")

            input("\nPressione ENTER para continuar...")

'''
'''
limpar_terminal()
turnos = {
    1: "Dia",
    2: "Tarde",
    3: "Noite"
}

msg_turnos = """Turnos:
1 - Dia
2 - Tarde
3 - Noite
'A' para selecionar todas as opções
Entrada: """


resultado_str, resultado_lista = obter_multiplas_opcoes_dict(msg_turnos,"Entrada inválida. Digite números separados por vírgula.", turnos)

print("String retornada:", resultado_str)
print("Lista retornada:", resultado_lista)
'''


'''
status
realizada
absenteismo
cancelada


especialidade
cardiologia
neurologia
ortopedia
dermatologia
pediatria
oftalmologia
clinico geral

tipo consulta

retorno
emergencia
"rotina
exame
geral
'''
limpar_terminal()
sucesso, dados = solicitar_dados_paciente()

imprimir_pacientes_tabulate(dados)