"""

    SERVIÇO PARA REALIZAÇÃO DE OCR DE UM DOCUMENTO DE IDENTIDADE: RG

    UTILIZA TÉCNICAS DE VISÃO COMPUTACIONAL PARA OBTER:

    1) REGISTRO GERAL (RG)
    2) DATA DE EXPEDIÇÃO
    3) NOME
    4) NOME DO PAI
    5) NOME DA MÃE
    6) DATA DE NASCIMENTO
    7) CPF
    8) CIDADE ORIGEM
    9) ESTADO ORIGEM.

    # Arguments
        object                  - Required : Imagem para aplicação do OCR (Base64 | Path | Numpy Array)
    # Returns
        output_rg               - Required : Textos dos campos do RG após aplicação das
                                             técnicas de pré processamento,
                                             OCR e pós processamento (String)

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "16/10/2021"


from inspect import stack
import re
import warnings

import cv2
from dynaconf import settings

from UTILS.check_similarity import Check_Similarity
from UTILS.generic_functions import format_values_int, drop_duplicates_list
from UTILS.image_view import image_view_functions
from UTILS.image_ocr import ocr_functions
from UTILS.conectores_db.main import conectores

warnings.filterwarnings("ignore")


class Execute_OCR_RG(object):

    def __init__(self, pre_processing):

        # 1 - DEFININDO A CLASSE DE PRÉ PROCESSAMENTO E SUAS PROPRIEDADES
        self.__pre_processing = pre_processing

        # 2 - DEFININDO A CLASSE PROPRIEDADE DE TAMANHO DE SAÍDA DA IMAGEM
        self.__output_size = self.__pre_processing.output_size

        # 3 - DEFININDO OS CAMPOS A SEREM LIDOS
        self.FIELDS = self.__get_fields()

        # 4 - OBTENDO AS COORDENADAS PARA CROP DOS CAMPOS
        self.COORDS = self.__get_coords()

        # 5 - DEFININDO DE-PARA DE ESTADO-CIDADE
        self.CITY_STATE = self.__get_uf_state()

        # 6 - DEFININDO REGEX

        # SELECIONA APENAS LETRAS
        self.regex_only_letters = settings.REGEX_ONLY_LETTERS

        # SELECIONA APENAS NÚMEROS
        self.regex_only_numbers = settings.REGEX_ONLY_NUMBERS

        # SELECIONA APENAS LETRAS E NÚMEROS
        self.regex_only_letters_numbers = settings.REGEX_ONLY_LETTERS_NUMBERS

        # SELECIONA APENAS LETRAS, PONTOS, BARRAS, TRAÇOS E NÚMEROS
        self.regex_only_letters_numbers_dot_bars_dashes = settings.REGEX_ONLY_LETTERS_NUMBERS_DOT_BARS_DASHES

        # SELECIONA APENAS A LETRA X, PONTOS, BARRAS, TRAÇOS E NÚMEROS
        self.regex_only_x_numbers_dot_bars_dashes = settings.REGEX_ONLY_X_NUMBERS_DOT_BARS_DASHES

        # SELECIONA APENAS A LETRA X E NÚMEROS
        self.regex_only_x_numbers = settings.REGEX_ONLY_X_NUMBERS

        # SELECIONA APENAS DATAS
        self.regex_only_dates = settings.REGEX_ONLY_DATES

        # SELECIONA APENAS LETRAS, PONTO (.) E TRAÇO (-)
        self.regex_only_letters_dot_dash = settings.REGEX_ONLY_LETTERS_DOT_DASH

        # 7 - INICIANDO OS PERCENTUAIS DE MATCH DEFAULT
        self.default_percent_match = settings.DEFAULT_PERCENTUAL_MATCH

        # 8 - DEFININDO SE DEVE HAVER PRÉ PROCESSAMENTO DOS ITENS ANTES DO CÁLCULO DE SEMELHANÇA
        self.similarity_pre_processing = settings.DEFAULT_PRE_PROCESSING

        # 9 - INICIANDO A VARIÁVEL QUE CONTÉM O LIMIT NA CHAMADA DE MÁXIMAS SIMILARIDADES
        self.limit_result_best_similar = settings.DEFAULT_LIMIT_RESULT_BEST_SIMILAR


    @property
    def output_size(self):

        return self.__output_size


    def __get_fields(self):

        """

            OBTÉM TODOS OS CAMPOS ATIVOS (ACEITOS) PELO MODELO DE OCR RG.

            # Arguments

            # Returns
                result_list_fields_active       - Required : Lista contendo os
                                                             campos ativos de RG (List)

        """

        # INICIANDO A VARIÁVEL DE RESULTADO
        result_list_fields_active = []

        try:
            # DEFININDO OS PARÂMETROS DE CONEXÃO
            caminho_bd_bds = settings.DIR_BD_OCR
            ssql_bds = settings.QUERY_FIELDS
            params_bds = (None,)
            tipo_query_bds = settings.QUERY_TYPE_FIELDS

            # EXECUTANDO A QUERY E OBTENDO O RESULTADO
            list_fields_active = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)
            result_list_fields_active = list_fields_active[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            result_list_fields_active = format_values_int(settings.FIELDS.values())

        # RETORNANDO A TUPLA CONTENDO (MUNICIPIO, UF, ESTADO)
        return result_list_fields_active


    def __get_coords(self):

        """

            OBTÉM TODAS AS COORDENADAS PARA CROP DOS CAMPOS DO DOCUMENTO.

            ESSAS COORDENADAS SÃO UTILIZADAS NA FUNÇÃO DE ORQUESTRAÇÃO DO OCR.

            # Arguments

            # Returns
                coords             - Required : Lista contendo campos e
                                                coordenadas para crop (List)

        """

        # INICIANDO A VARIÁVEL DE RESULTADO
        result_coords = []

        try:
            # DEFININDO OS PARÂMETROS DE CONEXÃO
            caminho_bd_bds = settings.DIR_BD_OCR
            ssql_bds = settings.QUERY_COORD
            params_bds = (None,)
            tipo_query_bds = settings.QUERY_TYPE_COORD

            # EXECUTANDO A QUERY E OBTENDO O RESULTADO
            result = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            result = format_values_int(settings.COORDS.values())

        # FORMATANDO O RESULTADO NO FORMATO DE LISTA
        try:
            for field, nome_template, x1, y1, x2, y2, doc_verso in result:

                # VERIFICANDO SE O CAMPO ENCONTRA-SE ATIVO NESSE MODELO
                if field in [value[0] for value in self.FIELDS]:

                    x1 //= int(600/self.__output_size)
                    y1 //= int(600/self.__output_size)
                    x2 //= int(600/self.__output_size)
                    y2 //= int(600/self.__output_size)
                    result_coords.append([field, nome_template, doc_verso, (x1, y1), (x2, y2)])

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO A TUPLA CONTENDO (MUNICIPIO, UF, ESTADO)
        return result_coords


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


    def decorator_valid_similarity(func):

        """

            ORQUESTRA A CHAMADA DA FUNÇÃO DE CÁLCULO DE SIMILARIDADE ITEM A ITEM.

            # Arguments
                search                     - Required : Palavra a ser comparada
                                                        ou utilizada como base para obter
                                                        as similaridades
                                                        dentre as possibilidades (String)

                list_choices               - Required : Palavra ser comparada com a query ou a lista
                                                        de palavras a serem comparadas
                                                        com a query (String | List)

                percent_match              - Required : Somente serão retornados
                                                        os itens acima do
                                                        percentual de match (Integer)

                pre_processing             - Optional : Definindo se deve haver
                                                        pré processamento (Boolean)

                limit                      - Optional : Limite de resultados
                                                        de similaridade (Integer)

            # Returns
                percentual_similarity      - Required : Percentual de similaridade (String | List)

        """


        def valid_value_similarity(self, search, list_choices, percent_match, pre_processing, limit):

            # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO DE SIMILARIDADES
            # APÓS FILTRO POR PERCENTUAL DE MATCH ESPERADO
            result_valid_similarity = []
            validator_similarity = False

            # VALIDANDO O LIMITE ENVIADO
            if limit is False:
                limit = None

            try:
                # OBTENDO AS SIMILARIDADES ENTRE O ITEM PROCURADO E A LISTA DE ITENS
                result_similarity = Check_Similarity.get_values_similarity(query=search,
                                                                           choices=list_choices,
                                                                           pre_processing=pre_processing,
                                                                           limit=limit)

                # VALIDANDO OS ITENS QUE ESTÃO ACIMA DO PERCENTUAL DE SIMILARIDADE ENVIADO
                result_valid_similarity = [value for value in result_similarity if value[1] > percent_match]

                if len(result_valid_similarity) > 0:
                    validator_similarity = True

            except Exception as ex:
                print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

            return validator_similarity, result_valid_similarity

        return valid_value_similarity


    @decorator_valid_similarity
    def get_similitary(self):

        pass


    def __postprocess_string(self, field):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) MANTÉM APENAS LETRAS
                2) RETIRA ESPAÇOS EM EXCESSO

            # Arguments
                field              - Required : Valor a ser pós processado (String)

            # Returns
                output             - Required : Valor após processamento (String)

        """

        try:
            # MANTENDO APENAS LETRAS
            output = re.sub(self.regex_only_letters, " ", field).replace("  ", " ").strip()
        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    def __postprocess_num_rg(self, field):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) MANTÉM APENAS LETRAS, NÚMEROS, PONTOS ('.') BARRAS ('/') E TRAÇOS ('-')
                2) RETIRA ESPAÇOS EM EXCESSO

            # Arguments
                field              - Required : Valor a ser pós processado (String)

            # Returns
                output             - Required : Valor após processamento (String)

        """

        try:
            # MANTENDO APENAS LETRAS, NÚMEROS, PONTOS ('.') BARRAS ('/') E TRAÇOS ('-')
            output = re.sub(self.regex_only_x_numbers_dot_bars_dashes, "", field).replace("  ", " ").strip()

            # SUBSTITUINDO '/' POR '-'
            output = re.sub(r"/", "-", output)

            # VERIFICANDO SE "-" CONSTA NO TEXTO EXTRAIDO PELO OCR
            if "-" in output:
                preffix = output.split("-")[0]
                suffix = "-" + output.split("-")[-1]
            else:
                preffix = output
                suffix = ""

            # APLICANDO REGRAS DE VALIDAÇÃO DO NÚMERO DE RG
            out_pre = ""

            for i, digit in enumerate(preffix[::-1]):
                if i%3==0:
                    out_pre += "."
                out_pre += digit

            out_pre = out_pre[::-1].strip(".")

            # FORMATANDO O OUTPUT FINAL, USANDO A COMBINAÇÃO DA VALIDAÇÃO E DO SUFFIXO
            output = out_pre + suffix

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    def __postprocess_num(self, field):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) MANTÉM APENAS LETRAS, NÚMEROS, PONTOS ('.') BARRAS ('/') E TRAÇOS ('-')
                2) RETIRA ESPAÇOS EM EXCESSO

            # Arguments
                field              - Required : Valor a ser pós processado (String)

            # Returns
                output             - Required : Valor após processamento (String)

        """

        try:
            # SUBSTITUINDO '/' POR '-'
            output = re.sub(r"/", "-", field)

            # SUBSTITUINDO ',' POR '.'
            output = output.replace(",", ".")

            # MANTENDO APENAS A LETRA X E NÚMEROS
            output = re.sub(self.regex_only_x_numbers, "", field).replace("  ", " ").strip()

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    def __postprocess_dates(self, field):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO: PARA CAMPOS DATA

                1) MANTÉM APENAS LETRAS, NÚMEROS, PONTOS ('.') BARRAS ('/') E TRAÇOS ('-')
                2) RETIRA ESPAÇOS EM EXCESSO

            # Arguments
                field              - Required : Valor a ser pós processado (String)

            # Returns
                output             - Required : Valor após processamento (String)

        """

        try:
            # MANTENDO APENAS LETRAS, NÚMEROS, PONTOS ('.') BARRAS ('/') E TRAÇOS ('-')
            output = re.sub(self.regex_only_letters_numbers_dot_bars_dashes, "", field).replace("  ", " ").strip()

            # BUSCANDO MATCHS DE DATAS
            match = re.match(self.regex_only_dates, output)

            if match:
                output = match[0]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    @staticmethod
    def get_best_distance_levenshtein_ocr(list_values):

        # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ A VARIÁVEL COM A
        # MENOR QUANTIDADE DE DIFERENÇA DE QUANTIDADE ENTRE AS STRINGS
        min_dif_len_letters = 100
        result_max_similarity = []

        for value in list_values:

            # CALCULANDO A DIFERENÇA DE QUANTIDADE DE LETRAS
            dif_len_string = abs(len(value[0]) - len(value[1][0]))

            if dif_len_string < min_dif_len_letters:

                # ARMAZENANDO O RESULTADO
                result_max_similarity = value

                # ATUALIZANDO O VALOR DE MÍNIMA DIFERENÇA DE TAMANHO DA STRING
                min_dif_len_letters = dif_len_string

        # RETORNANDO O VALOR DE MÁXIMA SIMILARIDADE
        return result_max_similarity


    def get_max_similarity(self, text, list_values_similitary):

        """

            RECEBE UMA STRING, SEPARA-SE OS VALORES POR " " E "-".

                1) SPLIT POR " " E "-"
                2) CADA UM DOS VALORES É ENVIADO PARA OBTER A MÁXIMA SIMILARIDADE
                3) RETORNA O VALOR DE MAIOR SIMILARIDADE

            # Arguments
                text                       - Required : Texto a ser processado (String)
                list_values_similitary     - Required : Lista de valores possíveis (List)

            # Returns
                result_max_similarity      - Required : Valor de máxima similaridade com o texto (String)

        """

        # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ O MAX MATCH DE SIMILARIDADE
        max_similarity = 0
        result_max_similarity = []

        # REALIZANDO A QUEBRA POR ESPAÇOS E - E PERCORRENDO CADA UM DOS VALORES
        for value_x in text.split(" "):

            for value_j in value_x.split("-"):

                if value_j != "":

                    # OBTENDO A CIDADE E O ESTADO CONTIDO NO TEXTO
                    result_similarity = Execute_OCR_RG.get_similitary(self,
                                                                      value_j,
                                                                      list_values_similitary,
                                                                      self.default_percent_match,
                                                                      self.similarity_pre_processing,
                                                                      self.limit_result_best_similar)

                    if result_similarity[0]:

                        if result_similarity[1][0][1] >= max_similarity:

                            # ARMAZENANDO O RESULTADO
                            result_max_similarity.append([value_j, result_similarity[1][0]])

                            # ATUALIZANDO O VALOR DE MÁXIMA SIMILARIDADE
                            max_similarity = result_max_similarity[-1][1][1]

                            if max_similarity == 100:
                                # RETORNANDO O VALOR DE MÁXIMA SIMILARIDADE
                                return result_max_similarity[-1][1]

        # RETORNANDO O VALOR DE MÁXIMA SIMILARIDADE
        return Execute_OCR_RG.get_best_distance_levenshtein_ocr(result_max_similarity)[-1]


    def __postprocess_location(self, field):

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
            result_max_similarity = Execute_OCR_RG.get_max_similarity(self, field, list_values_similitary)

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
            result_similarity = Execute_OCR_RG.get_similitary(self,
                                                              value,
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


    def execute_ocr(self, img):

        """

            REALIZA O OCR NO DOCUMENTO, PARA ISSO:
                1) PERCORRE CADA UM DOS CAMPOS DESEJADOS
                2) PARA CADA UM DOS CAMPOS, REALIZA O CROP (MASK)
                   USANDO AS COORDENADAS ESPERADAS PARA O CAMPO
                3) APÓS O CROP, APLICA O TESSERACT

            # Arguments
                img                - Required : Imagem para aplicar o OCR (Array)

            # Returns
                info_extracted     - Required : Resultando contendo o OCR
                                                para cada um dos campos (Dict)

        """

        # INICIANDO O DICT QUE ARMAZENARÁ OS RESULTADOS DO OCR
        info_extracted = {}

        # INICIANDO O DICT DE POSIÇÕES
        bounding_positions = {}

        # PERCORRENDO CADA UM DOS CAMPOS E OBTENDO AS SUAS RESPECTIVAS COORDENADAS
        for field in self.COORDS:

            # OBTENDO OS BOUNDING POSITIONS
            bounding_positions['x1'] = field[3][0]
            bounding_positions['y1'] = field[3][1]
            bounding_positions['x2'] = field[4][0]
            bounding_positions['y2'] = field[4][1]

            # APLICANDO O CROP
            roi = img[bounding_positions['y1']:bounding_positions['y2'],
                  bounding_positions['x1']:bounding_positions['x2']]

            # REALIZANDO O OCR
            info_extracted[field[0]] = ocr_functions().Orquestra_OCR(roi)

            # VISUALIZANDO O BOUNDING BOX
            # image_view_functions.view_image_with_coordinates(image_view_functions.create_bounding_box(img, bounding_positions))

            # VISUALIZANDO O CROP
            # image_view_functions.view_image_with_coordinates(roi, window_name=field)

        return info_extracted


    def orchestra_pos_processing(self, info_extracted):

        """

            APLICA O PÓS PROCESSAMENTO PARA CADA UM DOS CAMPOS OBTIDOS.

            # Arguments
                info_extracted     - Required : Resultando contendo o OCR
                                                para cada um dos campos (Dict)

            # Returns
                info_extracted     - Required : Resultando contendo o OCR
                                                para cada um dos campos
                                                após os pós processamentos (Dict)

        """

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS TEXTUAIS
        for column in ["NOME", "NOME_MAE", "NOME_PAI"]:
            info_extracted[column] = self.__postprocess_string(info_extracted[column])

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS NUMÉRICOS
        for column in ["RG", "CPF"]:
            info_extracted[column] = self.__postprocess_num(info_extracted[column])

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS DATAS
        for column in ["DATA_EXPED", "DATA_NASC"]:
            info_extracted[column] = self.__postprocess_dates(info_extracted[column])

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS CIDADE E ESTADO ORIGEM
        info_extracted["CIDADE_ORIGEM"], info_extracted["ESTADO_ORIGEM"] = self.__postprocess_location(
            info_extracted["CIDADE_ORIGEM"])

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS CIDADE E ESTADO NASCIMENTO
        info_extracted["CIDADE_NASC"], info_extracted["ESTADO_NASC"] = self.__postprocess_location(
            info_extracted["CIDADE_NASC"])

        # RETORNANDO OS DADOS APÓS APLICAÇÃO DOS PÓS PROCESSAMENTOS
        return info_extracted


    def execute_pipeline_ocr(self, img_path):

        # INICIANDO O DICT QUE ARMAZENARÁ OS RESULTADOS DO OCR - CAMPO A CAMPO
        info_field = {}

        # INICIANDO A STRING QUE ARMAZENARÁ O RESULTADO O OCR - DOCUMENTO INTEIRO
        info_doc = ""

        # REALIZANDO O PRÉ PROCESSAMENTO
        img_original, cropped_image, warped_img = self.__pre_processing.run(img_path)

        # REALIZANDO O REDIMENSIONAMENTO DA IMAGEM CROPPED
        cropped_image = cv2.resize(cropped_image, (600, 600),
                                   interpolation=cv2.INTER_AREA)

        # VISUALIZANDO A IMAGEM APÓS O PRÉ PROCESSAMENTO
        image_view_functions.view_image(img_original, window_name="ORIGINAL")
        image_view_functions.view_image(cropped_image, window_name="CROPPED")
        image_view_functions.view_image(warped_img, window_name="WARPED")

        # APLICANDO O OCR - CAMPO A CAMPO
        info_field = self.execute_ocr(cropped_image)

        # APLICANDO O PÓS PROCESSAMENTO EM CADA UM DOS CAMPOS
        info_field = self.orchestra_pos_processing(info_field)

        # APLICANDO O OCR NO DOCUMENTO INTEIRO
        info_doc = ocr_functions().Orquestra_OCR(img_original)

        return info_field, info_doc