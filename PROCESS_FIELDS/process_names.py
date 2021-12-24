from inspect import stack
import re

from dynaconf import settings

from CONFIG import config
from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import read_txt, applied_filter_not_intesection_list, order_list_with_arguments


class Execute_Process_Names():

    def __init__(self):

        # 1 - REALIZANDO A LEITURA DO BANCO DE DADOS DE NOMES - GENEROS
        self.data_first_names_gender = self.__get_data_names(config.DIR_DATA_FIRST_NAMES_GENDER,
                                                             value_split=",",
                                                             encoding='cp1252')

        # 2 - REALIZANDO A LEITURA DO BANCO DE DADOS DE SOBRENOMES
        self.data_last_names = self.__get_data_names(config.DIR_DATA_LAST_NAMES,
                                                     value_split="-",
                                                     encoding='utf8')

        # 3 - INICIANDO OS PERCENTUAIS DE MATCH DEFAULT
        self.default_percent_match = settings.DEFAULT_PERCENTUAL_MATCH_NAME

        # 4 - DEFININDO SE DEVE HAVER PRÉ PROCESSAMENTO DOS ITENS ANTES DO CÁLCULO DE SEMELHANÇA
        self.similarity_pre_processing = settings.DEFAULT_PRE_PROCESSING

        # 5 - INICIANDO A VARIÁVEL QUE CONTÉM O LIMIT NA CHAMADA DE MÁXIMAS SIMILARIDADES
        self.limit_result_best_similar = settings.DEFAULT_LIMIT_RESULT_BEST_SIMILAR


    def __get_data_names(self, dir_data, value_split, encoding):

        """

            1) REALIZA A LEITURA DO BANCO DE DADOS DE NOMES
            2) REALIZA A FORMAAÇÃO DA LISTA, DE ACORDO COM UM VALOR DE SPLIT DEFINIDO

            # Arguments
                dir_data              - Required : Diretório da base a ser lida (String)
                value_split           - Required : Caracter utilizada para split da lista (String)
                encoding              - Optional : Encoding utilizado (String)

            # Returns
                list_result          - Required : Lista resultado (List)

        """

        # INICIANDO A VARIÁVEL RESULTANTE
        list_result = []

        try:
            # REALIZANDO A LEITURA DO TXT CONTENDO OS DADOS
            validador, data = read_txt(dir_data, encoding)

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            print("TENTANDO NOVO ENCODING - {}".format("UTF8"))

            # REALIZANDO A LEITURA DO TXT CONTENDO OS DADOS USANDO UTF8
            validador, data = read_txt(dir_data, encoding)

        try:
            if validador:

                # REALIZANDO A CONVERSÃO
                list_result = [name_sex.split(value_split) for name_sex in data.split("\n")]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO A TUPLA CONTENDO O RESULTADO FINAL APÓS LEITURA E FORMATAÇÃO
        return list_result


    def get_first_name_valid(self, name_input, list_first_names=None):

        """

            1) RECEBE UMA STRING CONTENDO UM NOME COMPLTO
            2) RECEBE UMA LISTA DE NOMES
            3) VALIDA SE DENTRO OS VALORES DA STRING,
            HÁ ALGUM VÁLIDO COMO PRIMEIRO NOME.

            # Arguments
                name_input         - Required : Nome completo a ser analisado (String)
                list_first_names   - Optional : Lista de primeiros nomes e generos (List)

            # Returns
                first_name         - Required : Primeiro nome válido (String)
                gender             - Required : Gênero do nome validado (Char)

        """

        # INICIANDO AS VARIÁVEIS DE RETORNO
        result_similarity = result_similarity_default = (False, [('', 0)])
        first_name = ""
        gender = ""

        # VERIFICANDO A VARIÁVEL DE PRIMEIROS NOMES
        if list_first_names is None:
            list_first_names = self.data_first_names_gender

        for value_x in name_input.split(" "):

            if value_x != "" and len(value_x) >= 2:

                result_similarity = Extract_Infos.get_similitary(self,
                                                                 str(value_x).upper(),
                                                                 [str(value[0]).upper() for value in list_first_names],
                                                                 self.default_percent_match,
                                                                 self.similarity_pre_processing,
                                                                 self.limit_result_best_similar)

                if result_similarity[0]:

                    # VERIFICANDO SE O MATCH OCORREU PARA LEN(NOME) < 4, COM VALOR DE 100
                    # CASO NÃO TENHA SIDO, EXCLUI A OPÇÃO
                    if result_similarity[-1][0][-1] < 100 and len(value_x) <= 3:
                        # CASO RECUSADO, CONTINUA BUSCANDO UM NOME VÁLIDO
                        result_similarity = result_similarity_default
                        continue
                    else:
                        #print(result_similarity[-1])

                        # ARMAZENANDO O NOME SALVO
                        first_name = value_x

                        try:
                            # OBTENDO O GÊNERO
                            gender = [value[1].upper() for value in list_first_names if
                                      value[0].upper() == result_similarity[-1][0][0].upper()][0]
                        except Exception as ex:
                            # OBTENDO O GÊNERO
                            gender = [value[1].upper() for value in self.data_first_names_gender if
                                      value[0].upper() == result_similarity[-1][0][0][0].upper()][0]

                        return result_similarity, first_name, gender

        return result_similarity, first_name, gender


    def last_name_valid(self, complete_name_input, first_name_input, list_last_names=None):

        """

            1) RECEBE UMA STRING CONTENDO UM NOME COMPLTO
            2) RECEBE UMA LISTA DE SOBRENOMES
            3) VALIDA CADA UM DOS VALORES DO NOME,
            SE ESSE VALOR É UM SOBRENOME

            # Arguments
                complete_name_input  - Required : Nome completo a ser analisado (String)
                first_name_input     - Required : Primeiro nome validado (String)
                list_last_names      - Optional : Lista de sobrenomes (List)

            # Returns
                last_name          - Required : Sobrenomes válidos (String)
                gender             - Required : Gênero do nome validado (Char)

        """

        # INICIANDO A VARIÁVEL QUE OS SOBRENOMES VÁLIDOS
        last_name = ""

        # VERIFICANDO A  VARIÁVEL DE PRIMEIROS NOMES
        if list_last_names is None:
            list_last_names = self.data_last_names

        for value_x in complete_name_input.split(" "):

            # VALIDANDO SE É O PRIMEIRO NOME (ESSE NÃO SERÁ ANALISADO)
            if value_x != first_name_input and value_x not in ["DO", "DA", "DE", "DI"]:

                # VALIDANDO SE É O PRIMEIRO NOME (ESSE NÃO SERÁ ANALISADO)
                if value_x != "" and len(value_x) >= 3:

                    result_similarity = Extract_Infos.get_similitary(self,
                                                                     value_x,
                                                                     [value[0] for value in list_last_names],
                                                                     self.default_percent_match,
                                                                     self.similarity_pre_processing,
                                                                     self.limit_result_best_similar)

                    if result_similarity[0]:
                        # print(value_x, result_similarity[-1])

                        # ARMAZENANDO O NOME SALVO
                        last_name += value_x + " "

            else:
                # ARMAZENANDO O NOME SALVO
                last_name += value_x + " "

        return last_name.strip()


    def orchestra_postprocess_names(self, info_extracted,
                                    filters_validate=[],
                                    pattern_only_letters=settings.REGEX_ONLY_LETTERS):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) RETIRA VALORES QUE NÃO SÃO NOME E/OU SOBRENOMES.

            # Arguments
                info_extracted       - Required : Textos a serem analisado (Dict)
                filters_validate     - Optional : Filtros e validações
                                                 a serem aplicadas (List)

                regex_only_letters   - Optional : Pattern a ser utilizado (Regex)

            # Returns
                output               - Required : Valor após processamento (String)

        """

        # INICIANDO O VALIDADOR DE FIM DA FUNÇÃO
        validador = False

        result_names = []

        dict_names = ["NOME", "NOME_MAE", "NOME_PAI"]

        for field in dict_names:

            validador = False

            # FILTRANDO O VALOR DO CAMPO ATUAL
            value_x = info_extracted[field]

            # MANTENDO APENAS LETRAS
            result_split = re.sub(pattern=pattern_only_letters,
                                  string=value_x,
                                  repl=" ").replace("  ", " ").strip()

            if not validador:

                for value_y in result_split.split(" "):

                    # A STRING DEVE SER != "" E NÃO SER RESULTADO DE UM CAMPO ANTERIOR
                    if value_y != "" and not applied_filter_not_intesection_list(
                            [value_split for value_split in value_y.split(" ") if value_split != ""],
                            filters_validate + settings.WORDS_BLACK_LIST_NAMES,
                            mode="FIND", min_len=3):

                        # print("NOME: TESTANDO: {}".format(value_y))

                        # VALIDANDO SE É UM NOME VÁLIDO
                        result_valid_name = Execute_Process_Names.get_first_name_valid(self, value_y,
                                                                                       self.data_first_names_gender)

                        if result_valid_name[0][0]:
                            result_names.append([value_y, result_valid_name[0][1][0][-1], result_valid_name[2]])

                            if result_valid_name[0][-1][0][-1] == 100:
                                info_extracted[field] = value_x[value_x.find(result_valid_name[-2]):]
                                validador = True
                                break


            else:
                break

            if not validador:
                # ORDENANDO A LISTA E OBTENDO OS 3 VALORES DE MAIOR PERCENTUAL
                result_order_names = order_list_with_arguments(list_values=result_names,
                                                         number_column_order=1,
                                                         limit=1)

                if len(result_order_names):

                    info_extracted[field] = value_x[value_x.find(result_order_names[0][0]):]

                else:
                    info_extracted[field] = ""

        return info_extracted