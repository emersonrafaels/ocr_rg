from inspect import stack

from dynaconf import settings
import re

from UTILS.conectores_db.main import conectores
from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import drop_duplicates_list, read_txt


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
            caminho_bd_bds = settings.DIR_BD_OCR
            ssql_bds = settings.QUERY_MUNICIPIOS_UF
            params_bds = (None,)
            tipo_query_bds = settings.QUERY_TYPE_MUNICIPIOS_UF

            # EXECUTANDO A QUERY E OBTENDO O RESULTADO
            df_municipios_uf = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO A TUPLA CONTENDO (MUNICIPIO, UF, ESTADO)
        return df_municipios_uf


    def get_uf(self, field):

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
        result_max_similarity = []

        field = re.sub(r",", ".", field)
        field = re.sub(r"=", "-", field)

        # TRATANDO O VALOR DO CAMPO
        field = re.sub(self.regex_only_letters_dot_dash, " ", field).replace("  ", " ").strip()

        list_values_similitary = drop_duplicates_list([value[1] for value in self.CITY_STATE])

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

            if current_field == "state":
                # OBTENDO O VALOR RESULTANTE
                state = result_max_similarity[0]

            else:
                # OBTENDO O VALOR RESULTANTE
                city = result_max_similarity[0]

        # RETORNANDO OS VALORES DE ESTADO E CIDADE
        return city, state


    def __postprocess_location_old(self, field):

        # INICIANDO AS VARIÁVEIS RESULTANTES DE CIDADE E ESTADO
        city = state = ""

        field = re.sub(r",", ".", field)
        field = re.sub(r"=", "-", field)

        # TRATANDO O VALOR DO CAMPO
        field = re.sub(self.regex_only_letters_dot_dash, " ", field).replace("  ", " ").strip()

        for value in field.split(" "):

            # OBTENDO A CIDADE E O ESTADO CONTIDO NO TEXTO
            result_similarity = self.orchestra_extract_infos.get_similitary(value,
                                                                            [value[0] for value in self.CITY_STATE],
                                                                            self.default_percent_match,
                                                                            self.similarity_pre_processing,
                                                                            self.limit_result_best_similar)

            if result_similarity[0]:
                print(result_similarity)

        try:
            result_split = field.split("-")

            if len(result_split) == 1:
                city = result_split[0]
            elif len(result_split) >= 2:
                city, state = result_split[0], result_split[1]

            # TRATANDO O VALOR DA CIDADE
            city = re.sub(self.regex_only_letters, " ", city).replace("  ", " ").strip()

            # OBTENDO O ESTADO\
            list_result_state = [key for key in self.CITY_STATE if (self.CITY_STATE[key] == city)]
            if len(list_result_state) > 0:
                state = list_result_state[0]

            # RETIRANDO ESPAÇOS ANTES E APÓS OS VALORES OBTIDOS
            city = city.strip()
            state = state.strip()

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            city = field
            state = ''

        return city, state