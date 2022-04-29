from inspect import stack

from dynaconf import settings
import re

from CONFIG import config
from UTILS.conectores_db.main import conectores
from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import drop_duplicates_list, order_list_with_arguments
from PROCESS_FIELDS.process_confidence_percentage import get_confidence_percentage, get_average


class Execute_Process_Location():

    def __init__(self):

        # 1 - DEFININDO DE-PARA DE ESTADO-CIDADE
        self.CITY_STATE = self.__get_uf_state()

        # 2 - INICIANDO OS PERCENTUAIS DE MATCH DEFAULT
        self.default_percent_match = settings.DEFAULT_PERCENTUAL_MATCH

        # 3 - DEFININDO SE DEVE HAVER PRÉ PROCESSAMENTO DOS ITENS ANTES DO CÁLCULO DE SEMELHANÇA
        self.similarity_pre_processing = settings.DEFAULT_PRE_PROCESSING

        # 4 - INICIANDO A VARIÁVEL QUE CONTÉM O LIMIT NA CHAMADA DE MÁXIMAS SIMILARIDADES
        self.limit_result_best_similar = settings.DEFAULT_LIMIT_RESULT_BEST_SIMILAR

        self.regex_only_letters_dot_dash = Extract_Infos().get_value_regex("REGEX_ONLY_LETTERS_DOT_DASH")

        # 5 - INSTANCIANDO O OBJETO DA CLASSE DE EXTRAÇÃO DE INFOS
        self.orchestra_extract_infos = Extract_Infos()


    def __get_uf_state(self):

        """

            OBTÉM TODAS OS MUNICIPIOS/ESTADOS DISPONÍVEIS NA BASE DO IBGE.

            # Arguments

            # Returns
                df_municipios_uf             - Required : Lista contendo municipios/estados (List)

        """

        # INICIANDO A VARIÁVEL RESULTANTE
        df_municipios_uf = []

        try:
            # DEFININDO OS PARÂMETROS DE CONEXÃO
            caminho_bd_bds = config.DIR_BD_OCR
            ssql_bds = settings.QUERY_MUNICIPIOS_UF
            params_bds = (None,)
            tipo_query_bds = settings.QUERY_TYPE_MUNICIPIOS_UF

            # EXECUTANDO A QUERY E OBTENDO O RESULTADO
            df_municipios_uf = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO A TUPLA CONTENDO (MUNICIPIO, UF, ESTADO)
        return df_municipios_uf


    def get_uf_similitary(self, field):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO: PARA CAMPOS ESTADO

                1) MANTÉM APENAS LETRAS, PONTOS ('.') E TRAÇOS ('-')
                2) RETIRA ESPAÇOS EM EXCESSO
                3) OBTEM A MÁXIMA SIMILARIDADE

            # Arguments
                field              - Required : Valor a ser pós processado (String)

            # Returns
                state              - Required : Estado após processamento (String)

        """

        # INICIANDO AS VARIÁVEIS RESULTANTES DE CIDADE E ESTADO
        state = ""

        # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ O MAX MATCH DE SIMILARIDADE
        max_similarity = 0
        result_similarity = (False, [])

        field = re.sub(r",", ".", field)
        field = re.sub(r"=", "-", field)

        # TRATANDO O VALOR DO CAMPO
        field = re.sub(self.regex_only_letters_dot_dash, " ", field).replace("  ", " ").strip()

        if field != "":
            list_values_similitary = drop_duplicates_list([str(value[1]).upper() for value in self.CITY_STATE])

            # OBTENDO O VALOR DE SIMILARIDADE
            result_similarity = Extract_Infos().get_similitary(field,
                                                               list_values_similitary,
                                                               self.default_percent_match,
                                                               self.similarity_pre_processing,
                                                               self.limit_result_best_similar)

        # RETORNANDO OS VALORES SIMILARIDADE PARA O ESTADO
        return result_similarity


    def get_city_similitary(self, field):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO: PARA CAMPOS CIDADE

                1) MANTÉM APENAS LETRAS, PONTOS ('.') E TRAÇOS ('-')
                2) RETIRA ESPAÇOS EM EXCESSO
                3) OBTEM A MÁXIMA SIMILARIDADE


            # Arguments
                field              - Required : Valor a ser pós processado (String)

            # Returns
                state              - Required : Estado após processamento (String)

        """

        # INICIANDO AS VARIÁVEIS RESULTANTES DE CIDADE E ESTADO
        city = ""

        # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ O MAX MATCH DE SIMILARIDADE
        max_similarity = 0
        result_max_similarity = []

        field = re.sub(r",", ".", field)
        field = re.sub(r"=", "-", field)

        # TRATANDO O VALOR DO CAMPO
        field = re.sub(self.regex_only_letters_dot_dash, " ", field).replace("  ", " ").strip()

        list_values_similitary = drop_duplicates_list([str(value[0]).upper() for value in self.CITY_STATE])

        # OBTENDO O VALOR DE SIMILARIDADE
        result_similarity = Extract_Infos().get_similitary(field,
                                                           list_values_similitary,
                                                           self.default_percent_match,
                                                           self.similarity_pre_processing,
                                                           self.limit_result_best_similar)

        # RETORNANDO OS VALORES SIMILARIDADE PARA O ESTADO
        return result_similarity


    def orchestra_postprocess_location(self, field):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO: PARA CAMPOS CIDADE - ESTADO

                1) MANTÉM APENAS LETRAS, PONTOS ('.') E TRAÇOS ('-')
                2) RETIRA ESPAÇOS EM EXCESSO

            NORMALMENTE CIDADE E ESTADO VEM PRÓXIMOS UM AO OUTRO
            EX: CIDADE-UF

            NESSE CASO, SEPARA-SE OS VALORES POR " " E "-".

                3) SPLIT POR " " E "-"
                4) CADA UM DOS VALORES É ENVIADO PARA OBTER A MÁXIMA SIMILARIDADE
                5) PRIMEIRO OBTÉM-SE O UF COM MAIOR SIMILARIDADE
                6) FILTRAM-SE AS CIDADES REFERENTES A ESSE UF
                7) OBTÉM-SE A CIDADE COM MAIOR SIMILARIDADE

            # Arguments
                field              - Required : Valor a ser pós processado (String)

            # Returns
                city               - Required : Cidade após processamento (String)
                state              - Required : Estado após processamento (String)

        """

        # INICIANDO AS VARIÁVEIS RESULTANTES DE CIDADE E ESTADO
        city = state = ""

        # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ O MAX MATCH DE SIMILARIDADE
        max_similarity = 0
        result_max_similarity = []

        field = re.sub(r",", ".", field)
        field = re.sub(r"=", "-", field)

        # TRATANDO O VALOR DO CAMPO
        field = re.sub(self.regex_only_letters_dot_dash, " ", field).replace("  ", " ").strip()

        # OBTENDO ESTADO - CIDADE
        for current_field in ["state", "city"]:

            if current_field == "state":
                # OBTENDO OS VALORES DE UF PARA COMPARAR
                list_values_similitary = drop_duplicates_list([value[1] for value in self.CITY_STATE])

            else:
                # OBTENDO OS VALORES DE CIDADES PARA COMPARAR
                # VERIFICANDO SE HÁ UM ESTADO DEFINIDO
                if state != "":
                    list_values_similitary = drop_duplicates_list([value[0] for value in self.CITY_STATE if value[1] == state])
                else:
                    list_values_similitary = drop_duplicates_list([value[0] for value in self.CITY_STATE])

            # OBTENDO O VALOR DE MÁXIMA SIMILARIDADE
            result_max_similarity = self.orchestra_extract_infos.get_max_similarity(field, list_values_similitary)

            # VERIFICANDO SE HOUVE RESULTADO DE SIMILARIDADE
            if result_max_similarity[-1] == 0:
                result_max_similarity = ["", 0]

            if current_field == "state":
                # OBTENDO O VALOR RESULTANTE
                state = result_max_similarity[0]

            else:
                # OBTENDO O VALOR RESULTANTE
                city = result_max_similarity[0]

        # RETORNANDO OS VALORES DE ESTADO E CIDADE
        return city, state


    def get_uf(self, text, pattern_uf):

        """

            ORQUESTRA A OBTENÇÃO DOS CAMPOS DE ESTADOS
            PARA ISSO, REALIZA UM PATTERN DE UF SOBRE O TEXTO.
            COM O RESULTADO DO PATTERN, OBTÉM AS UFS DE MAIOR SIMILARIDADE.

            # Arguments
                text                              - Required : Texto a ser analisado (String)
                pattern_uf                        - Required : Pattern a ser utilizado para
                                                               obtenção das uf (Regex)

            # Returns
                list_values_result_pattern        - Required : UF's obtidos a partir do pattern (List)
                result_ufs                        - Required : UF's obtidas com
                                                               maiores percentuais de match (List)

        """

        # INICIANDO AS VARIÁVEIS DE RETORNO
        list_values_result_pattern = []
        result_ufs = []

        try:
            # OBTENDO POSSIVEIS UFS
            ufs = self.orchestra_extract_infos.get_matchs_strings(text, pattern_uf)

            # ARMAZENANDO AS POSSÍVEIS UFS
            list_values_result_pattern = ufs

            # PERCORRENDO CADA POSSÍVEL UF
            for value_x in [value[-1] for value in ufs]:

                # MANTENDO APENAS LETRAS
                result_regex = re.sub(pattern=settings.REGEX_ONLY_LETTERS,
                                      string=value_x,
                                      repl=" ").replace("  ", " ").strip()

                # REALIZANDO UM SPLIT, CASO POSSUA '-'
                for value_y in result_regex.split("-"):

                    # VERIFICANDO SE NÃO TRATA-SE DE UM CONECTOR DE FRASES
                    if value_y not in ["DA", "DE", "DI", "DO"] and value_y != "":

                        #print("UF: TESTANDO: {}".format(value_y))

                        # VALIDANDO SE É UM UF VÁLIDO
                        result_valid_uf = Execute_Process_Location.get_uf_similitary(self, value_y)

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

        return list_values_result_pattern, result_ufs


    def get_city(self, text, list_cities,
                 pattern=settings.REGEX_ONLY_LETTERS,
                 info_ocr=config.INFO_OCR_DEFAULT):

        """

            ORQUESTRA A OBTENÇÃO DOS CAMPOS DE CIDADES
            OBTÉM AS CIDADES DE MAIOR SIMILARIDADE.

            RETORNA CIDADES, PERCENTUAIS DE MATCH E PERCENTUAL DE CONFIANÇA.


            # Arguments
                text                   - Required : Texto a ser analisado (String)
                list_cities            - Required : Lista de possíveis cidades (List)
                pattern                - Optional : Pattern a ser utilizado (Regex)
                info_ocr               - Optional : ImageData do OCR (DataFrame | Dict)

            # Returns
                result_cities          - Required : Cidades obtidas (List)

        """

        # INICIANDO A VARIÁVEL DE RETORNO
        result_cities = []

        try:
            # PERCORRENDO CADA POSSÍVEL CIDADE
            for value_x in list_cities:

                # RETIRANDO ESPAÇOS EM BRANCO ANTES E DEPOIS DA STRING
                result_regex = re.sub(pattern=pattern,
                                      string=value_x,
                                      repl=" ").replace("  ", " ").strip()

                #print("CIDADE: TESTANDO: {}".format(value_x))

                # VALIDANDO SE É UMA CIDADE VÁLIDA
                result_valid_city = Execute_Process_Location.get_city_similitary(self, result_regex)

                # CASO SEJA VÁLIDO, SALVA NO RESULTADO DE UF's
                if result_valid_city[0]:
                    # result_cities = [valor, levenshtein_distance, mean(confidence_percentage)]
                    result_cities.append([result_regex,
                                          result_valid_city[-1][0],
                                          result_valid_city[-1][0][-1],
                                          get_average(get_confidence_percentage(value_x, info_ocr))])

            # ORDENANDO A LISTA PARA OBTER OS VALORES COM MAIOR
            # PERCENTUAL DE PROXIMIDADE COM UMA UF VÁLIDA
            result_cities = order_list_with_arguments(list_values=result_cities,
                                                      number_column_order=2,
                                                      limit=2)

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return result_cities


    def get_result_location(self, text, pattern_uf, info_ocr):

        """

            ORQUESTRA A OBTENÇÃO DOS CAMPOS DE LOCALIZAÇÃO DO DOCUMENTO:
                1) CIDADE E ESTADO DE NASCIMENTO
                2) CIDADE E ESTADO DE ORIGEM

            # Arguments
                text                   - Required : Texto a ser analisado (String)
                pattern_uf             - Required : Pattern a ser utilizado para
                                                    obtenção das uf (Regex)
                info_ocr               - Optional : ImageData do OCR (DataFrame | Dict)

            # Returns
                cidade_nasc            - Required : Cidade de nascimento (String)
                estado_nasc            - Required : Estado de nascimento (String)
                cidade_origem          - Required : Cidade de origem (String)
                estado_origem          - Required : Estado de origem (String)

        """

        # INICIANDO AS VARIÁVEIS
        cidade_nasc = ["", 0]
        estado_nasc = ["", 0]
        cidade_origem = ["", 0]
        estado_origem = ["", 0]

        # INICIANDO A VARIÁVEL PARA ARMAZENAMENTO DOS
        # RESULTADOS COM PERCENTUAIS DE CONFIANÇA
        list_result_percentage_confidence = []

        try:
            # OBTENDO AS UNIDADES FEDERATIVAS (ESTADOS)
            # result_uf = [valor, levenshtein_distance]
            list_values_result_pattern, result_uf = Execute_Process_Location.get_uf(self, text, pattern_uf)

            # OBTENDO AS UNIDADES FEDERATIVAS (ESTADOS)
            # result_uf = [valor, levenshtein_distance, confidence_percentage]
            result_uf = [[value_uf, get_confidence_percentage(value_uf[0], info_ocr)] for value_uf in result_uf]

            if len(result_uf):

                # SEPARANDO EM ESTADO DE NASCIMENTO E ESTADO DE ORIGEM
                if len(result_uf) == 1:

                    estado_nasc = result_uf[0][-1][0]
                    estado_origem = result_uf[0][-1][0]

                    # OBTENDO A FRASE NO A UF ESTÁ CONTIDA
                    # A CIDADE ESTÁ NA MESMA STRING
                    """line_city = [value for value in self.orchestra_extract_infos.get_matchs_line(text, pattern_uf) if
                                 result_uf[0][0] in value[-1]]"""

                elif len(result_uf) == 2:

                    estado_nasc = result_uf[0][-1][0]
                    estado_origem = result_uf[1][-1][0]

                    # OBTENDO A FRASE NO A UF ESTÁ CONTIDA
                    # A CIDADE ESTÁ NA MESMA STRING
                    """line_city = [value for value in self.orchestra_extract_infos.get_matchs_line(text, pattern_uf) if
                                 result_uf[0][0] in value[-1] or result_uf[1][0] in value[-1]]"""

                # OBTENDO A FRASE NO A UF ESTÁ CONTIDA
                # A CIDADE ESTÁ NA MESMA STRING
                line_city = self.orchestra_extract_infos.get_matchs_line(text, pattern_uf)

                # FORMATANDO POSSIVEIS CIDADES (RETIRA A UF DO ESTADO, APENAS MANTENDO A CIDADE)
                line_city_format = [value[0][:value[1]] for value in line_city]

                # OBTENDO AS CIDADES
                result_city = Execute_Process_Location.get_city(self,
                                                                text=text,
                                                                list_cities=line_city_format,
                                                                pattern=settings.REGEX_ONLY_LETTERS,
                                                                info_ocr=info_ocr)

                if len(result_city) == 1:

                    cidade_nasc = [result_city[0][1][0], result_city[0][3]]
                    cidade_origem = [result_city[0][1][0], result_city[0][3]]

                elif len(result_city) == 2:

                    cidade_nasc = [result_city[0][1][0], result_city[0][3]]
                    cidade_origem = [result_city[1][1][0], result_city[1][3]]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return cidade_nasc, estado_nasc, cidade_origem, estado_origem