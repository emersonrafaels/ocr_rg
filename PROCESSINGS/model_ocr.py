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
    10) ESTADO NASCIMENTO
    11) CIDADE NASCIMENTO
    12) ORGÃO EMISSOR

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
from os import getcwd, path
import unidecode
import re
import warnings

import cv2
from dynaconf import settings

from CONFIG import config
from PROCESSINGS.model_pos_processing import Pos_Processing_Fields
from PROCESS_FIELDS.process_names import Execute_Process_Names
from PROCESS_FIELDS.process_location import Execute_Process_Location
from UTILS.generic_functions import get_date_time_now, format_values_int, save_image
from UTILS.extract_infos import Extract_Infos
from UTILS.image_view import image_view_functions
from UTILS.image_ocr import ocr_functions
from UTILS.conectores_db.main import conectores

warnings.filterwarnings("ignore")


class Execute_OCR_RG(object):

    def __init__(self, side_document="VERSO"):

        # 1 - OBTENDO O LADO DO DOCUMENTO A SER LIDO
        self.side_document = side_document

        # 2 - DEFININDO A CLASSE PROPRIEDADE DE TAMANHO DE SAÍDA DA IMAGEM
        self.__output_size = settings.OUTPUT_SIZE

        # 3 - DEFININDO OS CAMPOS A SEREM LIDOS
        self.FIELDS = self.__get_fields()

        # 4 - OBTENDO AS COORDENADAS PARA CROP DOS CAMPOS
        self.COORDS = self.__get_coords()

        # 5 - INICIANDO O ORQUESTRADOR DE EXTRAÇÃO DE INFOS
        orchestra_extract_infos = Extract_Infos()

        # 6 - DEFINIDO OS REGEX
        # SELECIONA APENAS LETRAS
        self.regex_only_letters = orchestra_extract_infos.get_value_regex("REGEX_ONLY_LETTERS")

        # SELECIONA APENAS NÚMEROS
        self.regex_only_numbers = orchestra_extract_infos.get_value_regex("REGEX_ONLY_NUMBERS")

        # SELECIONA APENAS LETRAS E NÚMEROS
        self.regex_only_letters_numbers = orchestra_extract_infos.get_value_regex("REGEX_ONLY_LETTERS_NUMBERS")

        # SELECIONA APENAS LETRAS, PONTOS, BARRAS, TRAÇOS E NÚMEROS
        self.regex_only_letters_numbers_dot_bars_dashes = orchestra_extract_infos.get_value_regex("REGEX_ONLY_LETTERS_NUMBERS_DOT_BARS_DASHES")

        # SELECIONA APENAS A LETRA X, PONTOS, BARRAS, TRAÇOS E NÚMEROS
        self.regex_only_x_numbers_dot_bars_dashes = orchestra_extract_infos.get_value_regex("REGEX_ONLY_X_NUMBERS_DOT_BARS_DASHES")

        # SELECIONA APENAS A LETRA X E NÚMEROS
        self.regex_only_x_numbers = orchestra_extract_infos.get_value_regex("REGEX_ONLY_X_NUMBERS_DOT_BARS_DASHES")

        # SELECIONA APENAS DATAS
        self.regex_only_dates = orchestra_extract_infos.get_value_regex("REGEX_ONLY_DATES")

        # SELECIONA APENAS LETRAS, PONTO (.) E TRAÇO (-)
        self.regex_only_letters_dot_dash = orchestra_extract_infos.get_value_regex("REGEX_ONLY_LETTERS_DOT_DASH")

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
            caminho_bd_bds = config.DIR_BD_OCR
            ssql_bds = settings.QUERY_FIELDS

            # DEFININDO O PARÂMETRO PARA QUERY DOS CAMPOS ATIVOS
            if self.side_document == "FRENTE":
                params_bds = (0,)
            else:
                params_bds = (1,)

            tipo_query_bds = settings.QUERY_TYPE_FIELDS

            # EXECUTANDO A QUERY E OBTENDO O RESULTADO
            list_fields_active = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)
            result_list_fields_active = list_fields_active[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            result_list_fields_active = format_values_int(settings.FIELDS.values())

        # RETORNANDO A TUPLA CONTENDO OS CAMPOS DESEJADOS
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
            caminho_bd_bds = config.DIR_BD_OCR
            ssql_bds = settings.QUERY_COORD

            # DEFININDO O PARÂMETRO PARA QUERY DOS CAMPOS ATIVOS
            if self.side_document == "FRENTE":
                params_bds = (0,)
            else:
                params_bds = (1,)

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
            # MANTENDO APENAS LETRAS E TORNANDO O TEXTO UPPERCASE
            output = re.sub(self.regex_only_letters, " ", field).strip().upper()

            # RETIRANDO ESPAÇOS DESNECESSÁRIOS
            output = re.sub(' +', ' ', output)

            # RETIRANDO OS ACENTOS
            output = unidecode.unidecode(output)

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

        output = []

        try:
            # MANTENDO APENAS LETRAS, NÚMEROS, PONTOS ('.') BARRAS ('/') E TRAÇOS ('-')
            output = re.sub(self.regex_only_letters_numbers_dot_bars_dashes, "", field).replace("  ", " ").strip()

            # BUSCANDO MATCHS DE DATAS
            for match in re.finditer(self.regex_only_dates, output, re.MULTILINE):

                # REALIZANDO O MATCH
                output = match[0]

                return output

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    def orchestra_execute_ocr_model_two(self, img):

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
                list_result_ocr    - Required : Lista de textos obtidos no
                                                OCR de todos os campos (List)
                info_ocr           - Optional : DataFrame com as informações de
                                                leitura do OCR (DataFrame)

        """

        # INICIANDO O DICT QUE ARMAZENARÁ OS RESULTADOS DO OCR
        info_extracted = {}

        # INICIANDO O DICT DE POSIÇÕES
        bounding_positions = {}

        # INICIALIZANDO A LISTA QUE ARMAZENARÁ OS TEXTOS - RESULTADOS DOS OCR's OBTIDOS
        list_result_ocr = []

        # INICIALIZANDO O DATAFRAME QUE ARMAZENARÁ O INFO_OCR
        info_ocr = config.INFO_OCR_DEFAULT

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
            value_ocr = ocr_functions(type_return_ocr_input="TEXTO").Orquestra_OCR(roi)

            # OBTENDO O INFO_OCR
            # APLICANDO O OCR NO CROP - MODELO 2
            info_ocr_roi = ocr_functions(type_return_ocr_input="COMPLETO",
                                         type_output_image_data=settings.OUTPUT_TYPE_IMAGE_DATA).Orquestra_OCR(roi)

            # ARMAZENANDO O OCR OBTIDO
            list_result_ocr.append(value_ocr)

            # ARMAZENANDO O ROI SOBRE O DATAFRAME FINAL - INFO OCR
            info_ocr = info_ocr.append(info_ocr_roi)

            # VISUALIZANDO O BOUNDING BOX
            # image_view_functions.view_image_with_coordinates(image_view_functions.create_bounding_box(img, bounding_positions))

            # VISUALIZANDO O CROP
            # image_view_functions.view_image_with_coordinates(roi, window_name=field)

            # SALVANDO A IMAGEM
            save_image(roi, dir_save=path.join(getcwd(), "RESULTADO_OCR"),
                       name_save="{}{}{}".format(get_date_time_now("%d%m%Y%H%M%S"), field, ".png"))

            # ARMAZENANDO VALOR DO OCR E O PERCENTUAL DE CONFIANÇA
            info_extracted[field[0]] = [value_ocr, settings.DEFAULT_CONFIDENCE]

        return info_extracted, list_result_ocr, info_ocr


    def execute_ocr_box(self, img):

        """

            REALIZA O OCR NO DOCUMENTO USANDO BOUNDING BOX, PARA ISSO:
            
                1) DETECTA BOXES DE TEXTOS
                2) REALIZA O OCR SOBRE CADA UM DESSES BOXES

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

        # REALIZANDO O OCR (OBTENDO OS DADOS DO OCR)
        info_doc = ocr_functions(type_return_ocr_input="COMPLETO").Orquestra_OCR(img)

        # PERCORRENDO CADA UM DOS CAMPOS E OBTENDO AS SUAS RESPECTIVAS COORDENADAS
        for idx, box in enumerate(range(len(info_doc["text"]))):

            # FORMATANDO O TEXTO
            text = info_doc["text"][idx].strip()

            if text != "":

                # OBTENDO OS BOUNDING POSITIONS
                bounding_positions['x1'] = info_doc["left"][idx]
                bounding_positions['y1'] = info_doc["top"][idx]
                bounding_positions['x2'] = info_doc["width"][idx] + bounding_positions['x1']
                bounding_positions['y2'] = info_doc["height"][idx] + bounding_positions['y1']

                # APLICANDO O CROP
                roi = img[bounding_positions['y1']:bounding_positions['y2'],
                      bounding_positions['x1']:bounding_positions['x2']]


                # VISUALIZANDO O BOUNDING BOX
                image_view_functions.view_image_with_coordinates(image_view_functions.create_bounding_box(img,
                                                                                                          bounding_positions),
                                                                 window_name=text)

                # VISUALIZANDO O CROP
                # image_view_functions.view_image_with_coordinates(roi, window_name=text)

        return info_extracted


    def orchestra_pos_processing(self, info_extracted, info_ocr):

        """

            APLICA O PÓS PROCESSAMENTO PARA CADA UM DOS CAMPOS OBTIDOS.

            # Arguments
                info_extracted     - Required : Resultando contendo o OCR
                                                para cada um dos campos (Dict)
                info_ocr           - Optional : DataFrame com as informações de
                                                leitura do OCR (DataFrame)

            # Returns
                info_extracted     - Required : Resultando contendo o OCR
                                                para cada um dos campos
                                                após os pós processamentos (Dict)

        """

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS NUMÉRICOS

        for column in ["RG", "CPF"]:
            info_extracted[column][0] = self.__postprocess_num(info_extracted[column][0])
            info_extracted[column][0] = info_extracted[column][0].split(",")[0]

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS DATAS
        for column in ["DATA_EXPED", "DATA_NASC"]:
            info_extracted[column][0] = self.__postprocess_dates(info_extracted[column][0])

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS CIDADE E ESTADO ORIGEM
        info_extracted["CIDADE_ORIGEM"][0], \
        info_extracted["ESTADO_ORIGEM"][0] = Execute_Process_Location().orchestra_postprocess_location(
            info_extracted["CIDADE_ORIGEM"][0])

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS CIDADE E ESTADO NASCIMENTO
        info_extracted["CIDADE_NASC"][0], \
        info_extracted["ESTADO_NASC"][0] = Execute_Process_Location().orchestra_postprocess_location(
            info_extracted["CIDADE_NASC"][0])

        # RESULTADOS ATÉ ENTÃO
        results_ocr = [info_extracted["RG"][0], info_extracted["CPF"][0],
                       info_extracted["DATA_EXPED"][0], info_extracted["DATA_NASC"][0],
                       info_extracted["CIDADE_ORIGEM"][0], info_extracted["ESTADO_ORIGEM"][0],
                       info_extracted["CIDADE_NASC"][0], info_extracted["ESTADO_NASC"][0]]

        # APLICANDO PÓS PROCESSAMENTO DE NOMES
        info_extracted = Execute_Process_Names().orchestra_postprocess_names(info_extracted=info_extracted,
                                                                             info_ocr=info_ocr,
                                                                             filters_validate=results_ocr,
                                                                             pattern=settings.REGEX_ONLY_LETTERS)

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS TEXTUAIS
        for column in ["NOME", "NOME_MAE", "NOME_PAI", "CIDADE_ORIGEM",
                       "ESTADO_ORIGEM", "CIDADE_NASC", "ESTADO_NASC"]:
            info_extracted[column][0] = self.__postprocess_string(info_extracted[column][0])

        # APLICANDO O PÓS PROCESSAMENTO EM TODOS OS CAMPOS
        for column in info_extracted.keys():
            info_extracted[column][0] = info_extracted[column][0].replace("\n", "").strip()

        # RETORNANDO OS DADOS APÓS APLICAÇÃO DOS PÓS PROCESSAMENTOS
        return info_extracted


    def execute_pipeline_ocr(self, image):

        # INICIANDO O DICT QUE ARMAZENARÁ OS RESULTADOS DO OCR - CAMPO A CAMPO
        info_field = {}

        # INICIANDO A STRING QUE ARMAZENARÁ O RESULTADO O OCR - TEXTO OBTIDO
        text = []

        # INICIANDO O INFO_OCR
        info_ocr = config.INFO_OCR_DEFAULT

        # REALIZANDO O REDIMENSIONAMENTO DA IMAGEM CROPPED
        image_resize = cv2.resize(image, (self.__output_size, self.__output_size),
                                  interpolation=cv2.INTER_AREA)

        # APLICANDO O OCR - CAMPO A CAMPO
        info_field, list_result_text_ocr, info_ocr = self.orchestra_execute_ocr_model_two(image_resize)

        # CONVERTENDO A LISTA DE RESULTADO DE OCR PARA O FORMATO TEXTO
        text_result_ocr = '\n'.join(list_result_text_ocr)

        # REALIZANDO A OBTENÇÃO DOS CAMPOS
        text, data_exp, data_nasc, list_result_rg, list_result_cpf, \
        nome, nome_pai, nome_mae, \
        cidade_nasc, estado_nasc, cidade_origem, estado_origem = Pos_Processing_Fields().orchestra_pos_processing_get_fields(
            text_result_ocr, info_ocr)

        # RETORNANDO O RESULTADO OBTIDO
        return text, data_exp, data_nasc, list_result_rg, list_result_cpf, \
               nome, nome_pai, nome_mae, \
               cidade_nasc, estado_nasc, cidade_origem, estado_origem

        # RETORNANDO O RESULTADO OBTIDO
        return text_result_ocr, info_field