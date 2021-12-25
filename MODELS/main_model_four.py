import re
from inspect import stack

from dynaconf import settings
import unidecode

from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import convert_to_date, applied_filter_not_intesection_list, order_list_with_arguments
from UTILS.generic_functions import verify_find_intersection
from PROCESS_FIELDS.process_names import Execute_Process_Names
from PROCESS_FIELDS.process_location import Execute_Process_Location
from model_pre_processing import Image_Pre_Processing
from UTILS.image_ocr import ocr_functions
from UTILS.image_read import read_image, read_image_gray
from UTILS.image_convert_format import orchestra_read_image
from UTILS.deep_check_orientation.deep_check_orientation import check_orientation


class model_four():

    def __init__(self, dir_image):

        # 1 - DEFININDO OS PATTERNS
        self.pattern_data = settings.REGEX_ONLY_DATES
        self.pattern_rg = settings.REGEX_RG
        self.pattern_cpf = settings.REGEX_CPF
        self.pattern_uf = settings.REGEX_UF

        # 2 - OBTENDO O LOCAL DA IMAGEM
        self.dir_image = dir_image
        
        # 3 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()
        self.orchestra_process_names = Execute_Process_Names()
        self.orchestra_process_location = Execute_Process_Location()


    def rotate_image(image):

        """

            APLICA A ROTAÇÃO CORRETA NA IMAGEM.

            # Arguments
                image                - Required : Imagem a ser rotacionada corretamente (String)

            # Returns
                output               - Required : Valor após processamento (String)

        """

        # INICIANDO A VARIÁVEL RESULTADO
        image_rotate = []

        try:
            _, rotations_number, image_rotate = check_orientation().orchesta_model(image)
        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            image_rotate = image

        return image_rotate


    @staticmethod
    def __postprocess_string(field, regex_only_letters=settings.REGEX_ONLY_LETTERS):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) MANTÉM APENAS LETRAS
                2) RETIRA ESPAÇOS EM EXCESSO

            # Arguments
                field                - Required : Valor a ser pós processado (String)
                regex_only_letters   -  Required : Pattern a ser utilizado (Regex)

            # Returns
                output               - Required : Valor após processamento (String)

        """

        try:
            # MANTENDO APENAS LETRAS E TORNANDO O TEXTO UPPERCASE
            output = re.sub(regex_only_letters, " ", field).strip().upper()

            # RETIRANDO ESPAÇOS DESNECESSÁRIOS
            output = re.sub(' +', ' ', output)

            # RETIRANDO OS ACENTOS
            output = unidecode.unidecode(output)

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    @staticmethod
    def __postprocess_num(field, regex_only_x_numbers=settings.REGEX_ONLY_X_NUMBERS):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) MANTÉM APENAS LETRAS, NÚMEROS, PONTOS ('.') BARRAS ('/') E TRAÇOS ('-')
                2) RETIRA ESPAÇOS EM EXCESSO

            # Arguments
                field                - Required : Valor a ser pós processado (String)
                regex_only_letters   -  Required : Pattern a ser utilizado (Regex)

            # Returns
                output               - Required : Valor após processamento (String)

        """

        try:
            # SUBSTITUINDO '/' POR '-'
            output = re.sub(r"/", "-", field)

            # SUBSTITUINDO ',' POR '.'
            output = output.replace(",", ".")

            # MANTENDO APENAS A LETRA X E NÚMEROS
            output = re.sub(regex_only_x_numbers, "", field).replace("  ", " ").strip()

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    def find_nome_filiacao(self, text, pattern_find, limit=1):

        """

            VERIFICA SE NOME OU FILIAÇÃO (pattern_find)
            ESTÃO CONTIDOS NO TEXTO, CASO ESTEJAM
            OBTÉM UM NÚMERO SEGUINTE DE LINHAS (limit)

            # Arguments
                text                 - Required : Texto a ser analisado (String)
                filters_validate     - Optional : Filtros e validações
                                                  a serem aplicadas (List)
                limit                - Optional : Número de linhas
                                                  seguintes desejadas (Integer)


            # Returns
                result               - Required : Nomes obtidos (List)

        """

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validador_verify_find_intersection = False

        # INICIANDO A VARIÁVEL AUXILIAR DE RESULTADO DE NOMES APÓS A VALIDAÇÃO
        result_names = []

        # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO FINAL
        result = ""

        # INICIANDO A VARIÁVEL DE RETORNO
        result_final = []

        try:
            # CRIAÇÃO DA LISTA AUXILIAR
            # A LISTA AUXILIAR RECEBERÁ APENAS VALORES NÃO VÁZIOS E COM TAMANHO MAIOR QUE 1
            list_aux = [value.strip() for value in text.split("\n") if (value != "" and len(value.split(" ")) > 1) or verify_find_intersection(value, pattern_find)]

            # VERIFICANDO SE O PATTERN ESTÁ EM ALGUMA POSIÇÃO DO TEXTO
            validador_verify_find_intersection = [value for value in pattern_find if verify_find_intersection(value, list_aux)]

            if validador_verify_find_intersection:

                # OBTENDO O VALOR DE INTERSECÇÃO (USANDO O PRIMEIRO VALOR VALIDADO)
                pattern_find = validador_verify_find_intersection[0]

                result = list(map(list_aux.__getitem__, range(list_aux.index(pattern_find) + 1,
                                                                list_aux.index(pattern_find) + 1 + limit,
                                                                1)))

                for value in result:

                    # REINICIANDO A VARIÁVEL DE RESULTNAMES
                    result_names = []

                    for value_y in value.split(" "):

                        # VALIDANDO SE É UM NOME VÁLIDO
                        result_valid_name = self.orchestra_process_names.get_first_name_valid(value_y)

                        if result_valid_name[0][0]:
                            result_names.append([value_y, result_valid_name[0][1][0][-1], result_valid_name[2]])

                            if result_valid_name[0][-1][0][-1] == 100:
                                break

                # ORDENANDO A LISTA E OBTENDO OS 3 VALORES DE MAIOR PERCENTUAL
                result_names = order_list_with_arguments(list_values=result_names,
                                                         number_column_order=1,
                                                         limit=1)

                # ATUALIZANDO O NOME FINAL
                result = value[value.find(result_names[0][0]):].split("\n")[0]

                result_final.append(result)

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return result_final


    def get_names(self, text, filters_validate=[],
                  pattern_only_letters=settings.REGEX_ONLY_LETTERS):

        """

            ORQUESTRA A OBTENÇÃO DOS CAMPOS DE NOME.

            OS CAMPOS OBTIDOS SAO:
                1) NOME COMPLETO
                2) NOME DO PAI
                3) NOME DA MÃE

            RECEBE A OPÇÃO DE RETIRAR DA LISTA RESULTANTE
            VALORES DE UMA LISTA AUXILIAR ('list_validate')

            # Arguments
                text                 - Required : Texto a ser analisado (String)
                filters_validate     - Optional : Filtros e validações
                                                  a serem aplicadas (List)
                regex_only_letters   - Optional : Pattern a ser utilizado (Regex)


            # Returns
                result_names         - Required : Nomes obtidos (List)

        """

        # INICIANDO AS VARIÁVEIS
        nome = ""
        nome_pai = ""
        nome_mae = ""

        # INICIANDO O VALIDADOR DE FIM DA FUNÇÃO
        validador = False

        result_names = []

        # MANTENDO APENAS LETRAS
        text_only_letters = re.sub(pattern=pattern_only_letters,
                                   string=text,
                                   repl=" ").replace("  ", " ").strip()

        try:

            for result_split in text_only_letters.split("\n"):

                if not validador:

                    for value_x in result_split.split(" E "):

                        for value_y in value_x.split(" "):

                            # A STRING DEVE SER != "" E NÃO SER RESULTADO DE UM CAMPO ANTERIOR
                            if value_y != "" and not applied_filter_not_intesection_list(
                                    [value_split for value_split in value_y.split(" ") if value_split != ""],
                                    filters_validate + settings.WORDS_BLACK_LIST_NAMES,
                                    mode="FIND", min_len=3):

                                #print("NOME: TESTANDO: {}".format(value_y))

                                # VALIDANDO SE É UM NOME VÁLIDO
                                result_valid_name = self.orchestra_process_names.get_first_name_valid(value_y)

                                if result_valid_name[0][0]:
                                    result_names.append([value_y, result_valid_name[0][1][0][-1], result_valid_name[2]])

                                    if result_valid_name[0][-1][0][-1] == 100:
                                        break

                                    # VERIFICANDO SE JÁ HÁ 3 VALORES COM 100% DE SIMILARIDADE
                                    if len(list(filter(lambda x: x == 100, [value[1] for value in result_names]))) >= 3:
                                        validador = True
                                        break

                else:
                    break

            # ORDENANDO A LISTA E OBTENDO OS 3 VALORES DE MAIOR PERCENTUAL
            result_names = order_list_with_arguments(list_values=result_names,
                                                     number_column_order=1,
                                                     limit=3)

            # OBTENDO OS VALORES DE NOME, NOME MÃE E NOME PAI
            if len(result_names) == 1:

                nome = text_only_letters[text_only_letters.find(result_names[0][0]):].split("\n")[0]

                # VERIFICANDO O GÊNERO
                if result_names[0][-1] == "M":

                    nome_pai = text_only_letters[text_only_letters.find(result_names[0][0]):].split("\n")[0].split(" E ")[0]
                    nome_mae = ""

                else:

                    nome_pai = ""
                    nome_mae = text_only_letters[text_only_letters.find(result_names[0][0]):].split("\n")[0]

            elif len(result_names) == 2:

                nome = text_only_letters[text_only_letters.find(result_names[0][0]):].split("\n")[0]

                # VERIFICANDO O GÊNERO
                if result_names[1][-1] == "M":

                    nome_pai = text_only_letters[text_only_letters.find(result_names[1][0]):].split("\n")[0].split(" E ")[0]
                    nome_mae = ""

                else:

                    nome_pai = ""
                    nome_mae = text_only_letters[text_only_letters.find(result_names[1][0]):].split("\n")[0]

            elif len(result_names) > 2:

                nome = text_only_letters[text_only_letters.find(result_names[0][0]):].split("\n")[0]

                # VERIFICANDO O GÊNERO
                if result_names[1][-1] == "M":

                    nome_pai = text_only_letters[text_only_letters.find(result_names[1][0]):].split("\n")[0].split(" E ")[0]
                    nome_mae = text_only_letters[text_only_letters.find(result_names[2][0]):].split("\n")[0]

                else:

                    nome_pai = text_only_letters[text_only_letters.find(result_names[2][0]):].split("\n")[0].split(" E ")[0]
                    nome_mae = text_only_letters[text_only_letters.find(result_names[1][0]):].split("\n")[0]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return nome, nome_pai, nome_mae


    @staticmethod
    def choice_final_names(result_nome_alternativa_um,
                           result_filiacao_alternativa_um,
                           result_nome_alternativa_dois,
                           result_filiacao_alternativa_dois):

        """

           OSQUESTRA A DEFINIÇÃO DOS NOMES:

           1) NOME
           2) NOME DO PAI
           3) NOME DA MÃE

           A PARTIR DOS NOMES OBTIDOS ATRAVÉS DAS DUAS ALTERNATIVAS

           1) ALTERNATIVA 1 - PROCURANDO TERMOS COMO NOME/FILIAÇÃO
           2) ALTERNATIVA 2 - PERCORRENDO O TEXTO INTEIRO

            # Arguments
                result_nome_alternativa_um          - Required : Nome obtido na
                                                                 alternativa de execução um (String)
                result_filiacao_alternativa_um      - Required : Filiação obtida na
                                                                 alternativa de execução um (String)
                result_nome_alternativa_dois        - Required : Nome obtido na
                                                                 alternativa de execução dois (String)
                result_filiacao_alternativa_dois    - Required : Filiação obtida na
                                                                 alternativa de execução dois (String)

            # Returns
                nome                                - Required : Nome obtido (String)
                nome_pai                            - Required : Nome do pai obtido (String)
                nome_mae                            - Required : Nome da mãe obtido (String)

        """

        # INICIANDO AS VARIÁVEIS
        nome = ""
        nome_pai = ""
        nome_mae = ""

        try:
            print("ALTERNATIVA 1: NOME {} | FILIAÇÃO: {}".format(result_nome_alternativa_um, result_filiacao_alternativa_um))
            print("ALTERNATIVA 2: NOME {} | FILIAÇÃO: {}".format(result_nome_alternativa_dois, result_filiacao_alternativa_dois))

            # DEFININDO O NOME
            if len(result_nome_alternativa_um) > 0:
                nome = result_nome_alternativa_um[0]
            else:
                nome = result_nome_alternativa_dois[0]

            # DEFININDO FILIAÇÃO
            if len(result_filiacao_alternativa_um) == 2:
                # NOME DO PAI - ALTERNATIVA 1
                # NOME DA MÃE - ALTERNATIVA 1
                nome_pai, nome_mae = result_filiacao_alternativa_um[0], result_filiacao_alternativa_um[1]
            if len(result_filiacao_alternativa_um) == 1:
                # NOME DO PAI - ALTERNATIVA 1
                # NOME DA MÃE - ALTERNATIVA 2
                nome_pai, nome_mae = result_filiacao_alternativa_um[0], result_filiacao_alternativa_dois[1]
            else:
                # NOME DO PAI - ALTERNATIVA 2
                # NOME DA MÃE - ALTERNATIVA 2
                nome_pai, nome_mae = result_filiacao_alternativa_dois[0], result_filiacao_alternativa_dois[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return nome, nome_pai, nome_mae


    def orchestra_get_names(self, text, filters_validate=[]):

        """

           OSQUESTRA A OBTENÇÃO DOS CAMPOS DE NOMES:

           PARA ISSO UTILIZA DUAS ALTERNATIVAS DIFERENTES:

           1) ALTERNATIVA 1 - PROCURANDO TERMOS COMO NOME/FILIAÇÃO
           2) ALTERNATIVA 2 - PERCORRENDO O TEXTO INTEIRO

           AO FINAL, É UTILIZADA A FUNÇÃO 'choice_final_names'
           PARA DEFINIÇÃO DOS NOMES FINAIS:

           1) NOME
           2) NOME DO PAI
           3) NOME DA MÃE

            # Arguments
                text                       - Required : Texto a ser analisado (String)
                filters_validate           - Optional : Filtros e validações
                                                  a serem aplicadas (List)

            # Returns
                nome                       - Required : Nome obtido (String)
                nome_pai                   - Required : Nome do pai obtido (String)
                nome_mae                   - Required : Nome da mãe obtido (String)

        """

        # VERIFICANDO SE É POSSÍVEL ENCONTRAR AS PALAVRAS NOMES E FILIAÇÃO - ALTERNATIVA 1
        nome_alternativa_um = model_four.find_nome_filiacao(self, text,
                                                            pattern_find=settings.WORDS_LIST_NAMES,
                                                            limit=1)

        filiacao_alternativa_um = model_four.find_nome_filiacao(self, text,
                                                                pattern_find=settings.WORDS_LIST_FILIACAO,
                                                                limit=1)

        # OBTENDO OS NOMES - ALTERNATIVA 2
        nome_alternativa_dois, nome_pai_alternativa_dois, \
        nome_mae_alternativa_dois =  model_four.get_names(self,
                                                          text,
                                                          filters_validate,
                                                          settings.REGEX_ONLY_LETTERS)

        # ENVIANDO OS NOMES OBTIDOS PARA DEFINIÇÃO DOS NOMES A SEREM UTILIZADOS
        nome, nome_pai, nome_mae = model_four.choice_final_names(nome_alternativa_um,
                                                                 filiacao_alternativa_um,
                                                                 [nome_alternativa_dois],
                                                                 [nome_pai_alternativa_dois, nome_mae_alternativa_dois])

        return nome, nome_pai, nome_mae


    def get_uf(self, text, pattern_uf):

        """

            ORQUESTRA A OBTENÇÃO DOS CAMPOS DE ESTADOS
            PARA ISSO, REALIZA UM PATTERN DE UF SOBRE O TEXTO.
            COM O RESULTADO DO PATTERN, OBTÉM AS UFS DE MAIOR SIMILARIDADE.

            # Arguments
                text                   - Required : Texto a ser analisado (String)
                pattern_uf             - Required : Pattern a ser utilizado para
                                                    obtenção das uf (Regex)

            # Returns
                result_ufs             - Required : UF's obtidas (List)

        """

        result_ufs = []

        try:
            # OBTENDO POSSIVEIS UFS
            ufs = Extract_Infos().get_matchs_strings(text, pattern_uf)

            # PERCORRENDO CADA POSSÍVEL UF
            for value_x in [value[-1] for value in ufs]:

                # RETIRANDO ESPAÇOS EM BRANCO ANTES E DEPOIS DA STRING
                value_x = value_x.strip()

                # REALIZANDO UM SPLIT, CASO POSSUA '-'
                for value_y in value_x.split("-"):

                    # VERIFICANDO SE NÃO TRATA-SE DE UM CONECTOR DE FRASES
                    if value_y not in ["DA", "DE", "DI", "DO"] and value_y != "":

                        #print("UF: TESTANDO: {}".format(value_y))

                        # VALIDANDO SE É UM UF VÁLIDO
                        result_valid_uf = self.orchestra_process_location.get_uf_similitary(value_y)

                        # CASO SEJA VÁLIDO, SALVA NO RESULTADO DE UF's
                        if result_valid_uf[0]:
                            result_ufs.append([value_y, result_valid_uf[-1][0]])

            # ORDENANDO A LISTA PARA OBTER OS VALORES COM MAIOR
            # PERCENTUAL DE PROXIMIDADE COM UMA UF VÁLIDA
            result_ufs = order_list_with_arguments(list_values=result_ufs,
                                                   number_column_order=1,
                                                   limit=2)
        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return result_ufs


    def get_city(self, text, list_cities):

        """

            ORQUESTRA A OBTENÇÃO DOS CAMPOS DE CIDADES
            OBTÉM AS CIDADES DE MAIOR SIMILARIDADE.


            # Arguments
                text                   - Required : Texto a ser analisado (String)
                list_cities            - Required : Lista de possíveis cidades (List)

            # Returns
                result_cities          - Required : Cidades obtidas (List)

        """

        result_cities = []

        try:
            # PERCORRENDO CADA POSSÍVEL CIDADE
            for value_x in list_cities:

                # RETIRANDO ESPAÇOS EM BRANCO ANTES E DEPOIS DA STRING
                value_x = value_x.strip()

                #print("CIDADE: TESTANDO: {}".format(value_x))

                # VALIDANDO SE É UMA CIDADE VÁLIDA
                result_valid_city = self.orchestra_process_location.get_city_similitary(value_x)

                # CASO SEJA VÁLIDO, SALVA NO RESULTADO DE UF's
                if result_valid_city[0]:
                    result_cities.append([value_x, result_valid_city[-1][0]])

            # ORDENANDO A LISTA PARA OBTER OS VALORES COM MAIOR
            # PERCENTUAL DE PROXIMIDADE COM UMA UF VÁLIDA
            result_cities = order_list_with_arguments(list_values=result_cities,
                                                      number_column_order=1,
                                                      limit=2)

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return result_cities


    def get_result_location(self, text, pattern_uf):

        """

            ORQUESTRA A OBTENÇÃO DOS CAMPOS DE LOCALIZAÇÃO DO DOCUMENTO:
                1) CIDADE E ESTADO DE NASCIMENTO
                2) CIDADE E ESTADO DE ORIGEM

            # Arguments
                text                   - Required : Texto a ser analisado (String)
                pattern_uf             - Required : Pattern a ser utilizado para
                                                    obtenção das uf (Regex)

            # Returns
                cidade_nasc            - Required : Cidade de nascimento (String)
                estado_nasc            - Required : Estado de nascimento (String)
                cidade_origem          - Required : Cidade de origem (String)
                estado_origem          - Required : Estado de origem (String)

        """

        # INICIANDO AS VARIÁVEIS
        cidade_nasc = ""
        estado_nasc = ""
        cidade_origem = ""
        estado_origem = ""

        try:
            # OBTENDO AS UNIDADES FEDERATIVAS (ESTADOS)
            result_uf = model_four.get_uf(self, text, pattern_uf)

            if len(result_uf):

                # SEPARANDO EM ESTADO DE NASCIMENTO E ESTADO DE ORIGEM
                if len(result_uf) == 1:

                    estado_nasc = result_uf[0][1][0]
                    estado_origem = result_uf[0][1][0]

                    # OBTENDO A FRASE NO A UF ESTÁ CONTIDA
                    # A CIDADE ESTÁ NA MESMA STRING
                    line_city = [value for value in self.orchestra_extract_infos.get_matchs_line(text, pattern_uf) if
                                 result_uf[0][0] in value[-1]]

                elif len(result_uf) == 2:

                    estado_nasc = result_uf[0][1][0]
                    estado_origem = result_uf[1][1][0]

                    # OBTENDO A FRASE NO A UF ESTÁ CONTIDA
                    # A CIDADE ESTÁ NA MESMA STRING
                    line_city = [value for value in self.orchestra_extract_infos.get_matchs_line(text, pattern_uf) if
                                 result_uf[0][0] in value[-1] or result_uf[1][0] in value[-1]]

                # FORMATANDO POSSIVEIS CIDADES (RETIRA A UF DO ESTADO, APENAS MANTENDO A CIDADE)
                line_city_format = [value[0][:value[1]] for value in line_city]

                # OBTENDO AS CIDADES
                result_city = model_four.get_city(self, text, line_city_format)

                if len(result_city) == 1:

                    cidade_nasc = result_city[0][1][0]
                    cidade_origem = result_city[0][1][0]

                elif len(result_city) == 2:

                    cidade_nasc = result_city[0][1][0]
                    cidade_origem = result_city[1][1][0]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return cidade_nasc, estado_nasc, cidade_origem, estado_origem


    def get_result_datas(self, text, pattern_data):

        """

            ORQUESTRA A OBTENÇÃO DAS DATAS DO DOCUMENTO:
                1) DATA DE EXPEDIÇÃO
                2) DATA DE NASCIMENTO

            # Arguments
                text                   - Required : Texto a ser analisado (String)
                pattern_data           - Required : Pattern a ser utilizado para
                                                    obtenção das datas (Regex)

            # Returns
                data_exp               - Required : Data de expedição (String)
                data_nasc              - Required : Data de nascimento (String)

        """

        # INICIANDO AS VARIÁVEIS
        data_exp = ""
        data_nasc = ""

        try:
            # OBTENDO DATAS
            datas = self.orchestra_extract_infos.get_matchs_strings(text, pattern_data)

            if len(datas):

                # FORMATANDO AS DATAS PARA FORMATO DATE
                datas_format_date = [convert_to_date(str(date_value[-1]).upper(),
                                                     settings.DICT_MONTHS,
                                                     settings.REGEX_ONLY_LETTERS) for date_value in datas]

                # ORDENANDO AS DATAS
                datas_format_date_order = sorted(datas_format_date)

                # OBTENDO OS VALORES DE DATA DE EXPEDIÇÃO DE DATA DE NASCIMENTO
                if len(datas) == 1:

                    data_exp = datas[0][-1]
                    data_nasc = datas[0][-1]

                elif len(datas) > 1:

                    data_exp = datas[0][-1]
                    data_nasc = datas[1][-1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return data_exp, data_nasc


    def get_values(self, text, pattern, filters_validate=[],
                   limit_values=None):

        """

            ORQUESTRA A OBTENÇÃO DE VALORES EM UM TEXTO, DE ACORDO COM UM PATTERN.

            RECEBE A OPÇÃO DE RETIRAR DA LISTA RESULTANTE
            VALORES DE UMA LISTA AUXILIAR ('list_validate')

            # Arguments
                text                - Required : Texto a ser analisado (String)
                pattern             - Required : Pattern a ser utilizado para
                                                 obtenção dos dados (Regex)
                filters_validate    - Optional : Filtros e validações
                                                 a serem aplicadas (List)
                limit_values        - Optional : Limite de valores desejados (Integer)


            # Returns
                list_result         - Required : Resultados dos matchs (List)

        """

        # INICIANDO AS VARIÁVEIS
        list_result = []

        try:
            # OBTENDO OS REGISTROS GERAIS
            list_result = self.orchestra_extract_infos.get_matchs_strings(text, pattern)

            if len(list_result):

                # FORMATANDO A LISTA DE REGISTROS GERAIS
                list_result = [value[-1] for value in list_result if not applied_filter_not_intesection_list([value[-1]],
                                                                                                              filters_validate,
                                                                                                              mode="FIND")]

                if limit_values:
                    list_result = list_result[:limit_values]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return list_result


    def orchestra_model(self):

        # APLICANDO O OCR NO DOCUMENTO INTEIRO - MODELO 3
        info_ocr = ocr_functions(tipo_retorno_ocr_input="COMPLETO").Orquestra_OCR(self.dir_image)

        _, text = ocr_functions.convert_resultado_ocr_completo(info_ocr)

        # INICIANDO AS VARIÁVEIS
        data_exp = ""
        data_nasc = ""
        list_result_rg = []
        list_result_cpf = []
        nome = ""
        nome_pai = ""
        nome_mae = ""
        cidade_nasc = ""
        estado_nasc = ""
        cidade_origem = ""
        estado_origem = ""

        #print(text)
        #print("-"*50)

        # OBTENDO AS DATAS
        data_exp, data_nasc = model_four.get_result_datas(self, text, self.pattern_data)

        # OBTENDO CPF
        list_result_cpf = model_four.get_values(self, text, self.pattern_cpf,
                                                limit_values=1)

        # OBTENDO RG (FILTRANDO VALORES QUE JÁ CONSTAM COMO CPF)
        list_result_rg = model_four.get_values(self, text, self.pattern_rg,
                                               filters_validate=list_result_cpf,
                                               limit_values=1)

        # OBTENDO AS CIDADES-ESTADO
        cidade_nasc, estado_nasc, cidade_origem, estado_origem = model_four.get_result_location(self, text,
                                                                                                self.pattern_uf)

        # RESULTADOS ATÉ ENTÃO
        results_ocr = [data_exp, data_nasc, cidade_nasc, estado_nasc, cidade_origem, estado_origem] + list_result_cpf + list_result_rg

        # OBTENDO OS NOMES
        nome, nome_pai, nome_mae = model_four.orchestra_get_names(self, text, results_ocr)

        # FORMATANDO O RESULTADO DOS CAMPOS NUMÉRICOS
        list_result_rg = [model_four.__postprocess_num(value_rg, settings.REGEX_ONLY_X_NUMBERS) for value_rg in list_result_rg]
        list_result_cpf = [model_four.__postprocess_num(value_cpf, settings.REGEX_ONLY_NUMBERS) for value_cpf in list_result_cpf]

        # FORMATANDO O RESULTADO DOS CAMPOS STRINGS
        nome = model_four.__postprocess_string(nome, settings.REGEX_ONLY_LETTERS)
        nome_pai = model_four.__postprocess_string(nome_pai, settings.REGEX_ONLY_LETTERS)
        nome_mae = model_four.__postprocess_string(nome_mae, settings.REGEX_ONLY_LETTERS)
        cidade_nasc = model_four.__postprocess_string(cidade_nasc, settings.REGEX_ONLY_LETTERS_DOT_DASH)
        estado_nasc = model_four.__postprocess_string(estado_nasc, settings.REGEX_ONLY_LETTERS)
        cidade_origem = model_four.__postprocess_string(cidade_origem, settings.REGEX_ONLY_LETTERS_DOT_DASH)
        estado_origem = model_four.__postprocess_string(estado_origem, settings.REGEX_ONLY_LETTERS)

        return text, data_exp, data_nasc, list_result_rg, list_result_cpf, \
               nome, nome_pai, nome_mae, \
               cidade_nasc, estado_nasc, cidade_origem, estado_origem



def main_model(dir_image):

    # INICIANDO A VARIÁVEL CONTENDO A LISTA DE IMAGENS A SER ENVIADA
    dict_images = {}

    # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO DO MODELO
    result_model = []

    # REALIZANDO A LEITURA DA IMAGEM - RGB
    img_rgb = read_image(dir_image)

    if settings.ROTATE_IMAGE:
        # REALIZANDO A ROTAÇÃO DA IMAGEM
        # ATUALIZANDO A IMAGEM RGB COM A IMAGEM ROTACIONADA
        img_rgb = model_four.rotate_image(img_rgb)

    # REALIZANDO A LEITURA DA IMAGEM - ESCALA DE CINZA
    img_gray = read_image_gray(img_rgb)

    if settings.PRE_PROC_IMAGE:

        # DEFININDO A CLASSE DE PRÉ PROCESSAMENTO
        # UTILIZA-SE A IMAGEM RGB
        img_original, cropped_image, warped_img = Image_Pre_Processing(settings.BLUR_KSIZE,
                                                                       settings.THRESHOLD_MAX_COLOR_VALUE,
                                                                       settings.DILATION_KSIZE,
                                                                       settings.WIDTH_RESIZE,
                                                                       settings.OUTPUT_SIZE).orchestra_pre_processing(
            img_gray)

    # CONSTRUINDO A LISTA DE IMAGENS A SEREM ENVIADAS
    dict_images["IMAGEM_ORIGINAL_GRAY"] = img_gray
    dict_images["IMAGEM_ORIGINAL_RGB"] = img_rgb

    # VERIFICANDO SE É NECESSÁRIO ENVIAR A IMAGEM ROTACIONADA + IMAGEM ROTACIONADA EM 180
    if settings.DUPLO_CHECK_ROTATE:

        """
            ENVIA:
                1) IMAGEM EM ESCALA DE CINZA
                2) IMAGEM ESCALA DE CINZA ROTACIONADA EM 180º
                3) IMAGEM NA COR ORIGINAL
                4) IMAGEM NA COR ORIGINAL ROTACIONADA EM 180º
        """

        dict_images["IMAGEM_ORIGINAL_GRAY_DUPLO_CHECK"] = check_orientation.get_image_correct_orientation(img_gray, 2)
        dict_images["IMAGEM_ORIGINAL_RGB_DUPLO_CHECK"] = check_orientation.get_image_correct_orientation(img_rgb, 2)

    if settings.PRE_PROC_IMAGE:

        """
            ENVIA:
                1) IMAGEM CROPPADA EM ESCALA DE CINZA
                2) IMAGEM CROPPADA NA COR ORIGINAL
        """

        dict_images["IMAGEM_CROPPED_GRAY"] = cropped_image
        dict_images["IMAGEM_CROPPED_GRAY_DUPLO_CHECK"] = check_orientation.get_image_correct_orientation(cropped_image,
                                                                                                         2)

    # ENVIANDO A IMAGEM ORIGINAL E A IMAGEM EM PRETO E BRANCO
    for idx, image in enumerate(dict_images):

        # INICIANDO AS VARIÁVEL QUE ARMAZENARÁ O RESULTADO DA RODADA
        info_doc = {}

        print("-" * 50)
        print("MODELO QUATRO - RODADA: {} - {}".format(idx, image))

        text, data_exp, data_nasc, list_result_rg, list_result_cpf, \
        nome, nome_pai, nome_mae, \
        cidade_nasc, estado_nasc, cidade_origem, estado_origem = model_four(dict_images[image]).orchestra_model()

        # ARMAZENANDO OS RESULTADOS NO DICT DE RESULTADO
        info_doc['RG'] = list_result_rg
        info_doc['DATA_EXPED'] = data_exp
        info_doc['NOME'] = nome
        info_doc['NOME_MAE'] = nome_mae
        info_doc['NOME_PAI'] = nome_pai
        info_doc['DATA_NASC'] = data_nasc
        info_doc['CPF'] = list_result_cpf
        info_doc['CIDADE_NASC'] = cidade_nasc
        info_doc['ESTADO_NASC'] = estado_nasc
        info_doc['CIDADE_ORIGEM'] = cidade_origem
        info_doc['ESTADO_ORIGEM'] = estado_origem

        # ARMAZENANDO O RESULTADO
        print("RESULTADO OBTIDO - RODADA: {} - {}".format(idx, image))
        print(info_doc)

        result_model.append([text, info_doc])

    return result_model






