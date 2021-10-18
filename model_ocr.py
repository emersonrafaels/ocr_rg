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

import pytesseract

from utils.image_view import image_view_functions

warnings.filterwarnings("ignore")


class Execute_OCR_RG(object):

    def __init__(self, pre_processing):

        # 1 - DEFININDO A CLASSE DE PRÉ PROCESSAMENTO E SUAS PROPRIEDADES
        self.__pre_processing = pre_processing

        # 2 - DEFININDO A CLASSE PROPRIEDADE DE TAMANHO DE SAÍDA DA IMAGEM
        self.__output_size = self.__pre_processing.output_size

        # 3 - OBTENDO A INSTÂMNCIA DO TESSERACT
        self.__tesseract = pytesseract

        # 4 - DEFININDO OS CAMPOS A SEREM LIDOS
        self.FIELDS = ["RG", "DATA_EXPED", "NOME", "NOME_MAE", "NOME_PAI",
                       "DATA_NASC", "CPF", "CIDADE_ORIGEM"]

        # 5 - OBTENDO AS COORDENADAS PARA CROP DOS CAMPOS
        self.COORDS = self.__get_coords()

        # 6 - DEFININDO DE-PARA DE ESTADO-CIDADE
        self.UF_TO_STATE = {
                'AC': 'Acre',
                'AL': 'Alagoas',
                'AP': 'Amapá',
                'AM': 'Amazonas',
                'BA': 'Bahia',
                'CE': 'Ceará',
                'DF': 'Distrito Federal',
                'ES': 'Espírito Santo',
                'GO': 'Goiás',
                'MA': 'Maranhão',
                'MT': 'Mato Grosso',
                'MS': 'Mato Grosso do Sul',
                'MG': 'Minas Gerais',
                'PA': 'Pará',
                'PB': 'Paraíba',
                'PR': 'Paraná',
                'PE': 'Pernambuco',
                'PI': 'Piauí',
                'RJ': 'Rio de Janeiro',
                'RN': 'Rio Grande do Norte',
                'RS': 'Rio Grande do Sul',
                'RO': 'Rondônia',
                'RR': 'Roraima',
                'SC': 'Santa Catarina',
                'SP': 'São Paulo',
                'SE': 'Sergipe',
                'TO': 'Tocantins'
        }

        # 6 - DEFININDO REGEX
        self.regex_only_letters = r'[^A-zÀ-ù]'
        self.regex_only_numbers = r'[^\d]'
        self.regex_only_dates = r'[0-9]{2}(\/|-)(\w){2}(\w)?(\/|-)[0-9]{4}'
        self.regex_only_letters_dot_dash = '[^(A-zÀ-ù)(\-)(.)]'


    @property
    def output_size(self):

        return self.__output_size


    def __get_coords(self):

        nrg_xy = [(87, 35), (280, 96)]
        exped_xy = [(400, 35), (540, 110)]
        nome_xy = [(21, 80), (566, 173)]
        mae_xy = [(21, 240), (566, 300)]
        pai_xy = [(21, 206), (566, 234)]
        natal_xy = [(15, 310), (394, 380)]
        nasc_xy = [(400, 310), (558, 380)]
        cpf_xy = [(20, 450), (240, 520)]
        coords_default = [nrg_xy, exped_xy, nome_xy, mae_xy, pai_xy, nasc_xy, cpf_xy, natal_xy]
        coords = []
        for ((x1, y1), (x2, y2)) in coords_default:
            x1 //= int(600/self.__output_size)
            y1 //= int(600/self.__output_size)
            x2 //= int(600/self.__output_size)
            y2 //= int(600/self.__output_size)
            coords.append([(x1, y1), (x2, y2)])
        return coords


    def __postprocess_string(self, field):

        try:
            output = re.sub(self.regex_only_letters, " ", field).replace("  ", " ").strip()
        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    def __postprocess_num(self, field):

        output = re.sub(r"[^\d|\-|\/]", "", field)
        output = re.sub(r"/", "-", output)

        if "-" in output:
            preffix = output.split("-")[0]
            suffix = "-"+output.split("-")[-1]
        else:
            preffix = output
            suffix = ""
        out_pre = ""
        for i, digit in enumerate(preffix[::-1]):
            if i%3==0:
                out_pre+="."
            out_pre+=digit
        out_pre = out_pre[::-1].strip(".")
        return out_pre+suffix


    def __postprocess_location(self, field):

        # INICIANDO AS VARIÁVEIS RESULTANTES DE CIDADE E ESTADO
        city = state = ""

        field = re.sub(r",", ".", field)
        field = re.sub(r"=", "-", field)

        # TRATANDO O VALOR DO CAMPO
        field = re.sub(self.regex_only_letters_dot_dash, " ", field).replace("  ", " ").strip()

        try:
            result_split = field.split("-")

            if len(result_split) == 1:
                city = result_split[0]
            elif len(result_split) >= 2:
                city, state = result_split[0], result_split[1]

            # TRATANDO O VALOR DA CIDADE
            city = re.sub(self.regex_only_letters, " ", city).replace("  ", " ").strip()

            # OBTENDO O ESTADO
            list_result_state = [key for key in self.UF_TO_STATE if (self.UF_TO_STATE[key] == city)]
            if len(list_result_state) > 0:
                state = list_result_state[0]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            city = field
            state = ''

        return city, state


    def __execute_ocr(self, img):

        # INICIANDO O DICT QUE ARMAZENARÁ OS RESULTADOS DO OCR
        info_extracted = {}

        # INICIANDO O DICT DE POSIÇÕES
        bounding_positions = {}

        for field, ((x1, y1), (x2, y2)) in zip(self.FIELDS, self.COORDS):

            bounding_positions['x1'] = x1
            bounding_positions['y1'] = y1
            bounding_positions['x2'] = x2
            bounding_positions['y2'] = y2

            # APLICANDO O CROP
            roi = img[y1:y2, x1:x2]

            # VISUALIZANDO O BOUNDING BOX
            # image_view_functions.view_image(image_view_functions.create_bounding_box(img, bounding_positions))

            # VISUALIZANDO O CROP
            # image_view_functions.view_image(roi)

            # REALIZANDO O OCR
            info_extracted[field] = self.__tesseract.image_to_string(roi).strip()

        return info_extracted


    def execute_pipeline_ocr(self, img_path):

        # INICIANDO O DICT QUE ARMAZENARÁ OS RESULTADOS DO OCR
        info_extracted = {}

        # REALIZANDO O PRÉ PROCESSAMENTO
        img_original, cropped_image, warped_img = self.__pre_processing.run(img_path)

        # VISUALIZANDO A IMAGEM APÓS O PRÉ PROCESSAMENTO
        image_view_functions.view_image(img_original, nome_janela="ORIGINAL")
        image_view_functions.view_image(cropped_image, nome_janela="CROPPED")
        image_view_functions.view_image(warped_img, nome_janela="WARPED")

        # APLICANDO O OCR
        info_extracted = self.__execute_ocr(warped_img)

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS TEXTUAIS
        for column in ["NOME", "NOME_MAE", "NOME_PAI"]:
            info_extracted[column] = self.__postprocess_string(info_extracted[column])

        # APLICANDO PÓS PROCESSAMENTO NOS CAMPOS NUMÉRICOS
        for column in ["RG", "CPF"]:
            info_extracted[column] = self.__postprocess_num(info_extracted[column])

        info_extracted["CIDADE_ORIGEM"], info_extracted["UF_ORIGEM"] = self.__postprocess_location(info_extracted["CIDADE_ORIGEM"])

        return info_extracted