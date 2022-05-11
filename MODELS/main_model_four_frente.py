"""

    SERVIÇO PARA REALIZAÇÃO DE OCR DE UM DOCUMENTO DE IDENTIDADE: RG

    UTILIZA TÉCNICAS DE VISÃO COMPUTACIONAL PARA OBTER:

    1) ORGÃO EMISSOR

    MODELO UTILIZADO: BOUNDING BOX RECURSIVO.

    # Arguments
        object                  - Required : Imagem para aplicação do OCR (Base64 | Path | Numpy Array)
    # Returns
        output_rg               - Required : Textos dos campos do RG após aplicação das
                                             técnicas de pré processamento,
                                             OCR e pós processamento (String)

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "15/02/2022"


import re
from inspect import stack

from dynaconf import settings
import unidecode

from UTILS.extract_infos import Extract_Infos
from model_pre_processing import Image_Pre_Processing
from UTILS.image_ocr import ocr_functions
from UTILS.image_read import read_image, read_image_gray
from UTILS.image_view import image_view_functions
from UTILS.image_convert_format import orchestra_read_image
from PROCESS_FIELDS.process_orgao_emissor import Execute_Orgao_Emissor
from UTILS.deep_check_orientation.deep_check_orientation import check_orientation


class model_four_frente():

    def __init__(self, dir_image):

        # 1 - DEFININDO OS PATTERNS

        # 2 - OBTENDO O LOCAL DA IMAGEM
        self.dir_image = dir_image

        # 3 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()


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
            _, rotations_number, image_rotate_vert = check_orientation().orchesta_model(image)

            # A IMAGEM ESTÁ COM O ROSTO NO ÂNGULO CORRETO, ENTÃO DEVEMOS ROTACIONAR 90º
            # COM ESSA ROTAÇÃO, OBTEREMOS O TEXTO
            image_rotate = check_orientation.get_image_correct_orientation(image_rotate_vert, 3)

            # VISUALIZANDO A IMAGEM ROTACIONADA
            image_view_functions.view_image_with_coordinates(image_rotate,
                                                             window_name="IMAGEM ROTACIONADA")

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


    def orchestra_model(self):

        # APLICANDO O OCR NO DOCUMENTO INTEIRO - MODELO 3
        info_ocr = ocr_functions(type_return_ocr_input="COMPLETO").Orquestra_OCR(self.dir_image)

        _, text = ocr_functions.convert_resultado_ocr_completo(info_ocr)

        # INICIANDO AS VARIÁVEIS
        orgao_emissor = ""

        print(text)
        print("-"*50)

        # OBTENDO O ORGÃO EMISSOR
        result_similarity_orgao_emissor, orgao_emissor, sigla = Execute_Orgao_Emissor().get_orgao_emissor(text,
                                                                                                          list_orgao_emissor=None)

        return text, orgao_emissor, sigla


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
        img_rgb = Execute_Orgao_Emissor.rotate_image(img_rgb)

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

        print("-" * 50)
        print("MODELO QUATRO - FRENTE - RODADA: {} - {}".format(idx, image))

        text, orgao_emissor, sigla = model_four_frente(dict_images[image]).orchestra_model()

        # ARMAZENANDO O RESULTADO
        print("RESULTADO OBTIDO - RODADA: {} - {}".format(idx, image))
        print("ORGÃO EMISSOR: {} - SIGLA: {}".format(orgao_emissor, sigla))

        result_model.append([text, orgao_emissor, sigla])

    return result_model


image = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\GilmarAlmeida_frente.jpg'
main_model(image)