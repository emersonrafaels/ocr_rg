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
__data_atualizacao__ = "05/11/2021"


from inspect import stack

from dynaconf import settings

from model_pre_processing import Image_Pre_Processing
from model_ocr import Execute_OCR_RG
from UTILS.image_read import read_image, read_image_gray
from UTILS.image_convert_format import orchestra_read_image
from UTILS.deep_check_orientation.deep_check_orientation import check_orientation


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


def main_model(dir_image):

    # INICIANDO A VARIÁVEL CONTENDO A LISTA DE IMAGENS A SER ENVIADA
    list_images = []

    # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO DO MODELO
    result_model = []

    if settings.ROTATE_IMAGE:
        # REALIZANDO A ROTAÇÃO DA IMAGEM
        input_image = rotate_image(dir_image)
    else:
        input_image = dir_image

    # OBTENDO AS IMAGENS A SEREM ENVIADAS
    img_rotate_gray = read_image_gray(input_image)
    img_rotate_rgb = orchestra_read_image(input_image)

    # VERIFICANDO SE É NECESSÁRIO ENVIAR A IMAGEM ROTACIONADA + IMAGEM ROTACIONADA EM 180
    if settings.DUPLO_CHECK_ROTATE:

        """
            ENVIA:
                1) IMAGEM EM ESCALA DE CINZA
                2) IMAGEM ESCALA DE CINZA ROTACIONADA EM 180º
                3) IMAGEM NA COR ORIGINAL
                4) IMAGEM NA COR ORIGINAL ROTACIONADA EM 180º
        """

        list_images = [img_rotate_gray,
                       check_orientation.get_image_correct_orientation(img_rotate_gray, 2),
                       img_rotate_rgb,
                       check_orientation.get_image_correct_orientation(img_rotate_rgb, 2)]

    else:

        """
            ENVIA:
                1) IMAGEM EM ESCALA DE CINZA
                2) IMAGEM NA COR ORIGINAL
        """

        list_images = [img_rotate_gray,
                       img_rotate_rgb]

    # ENVIANDO A IMAGEM ORIGINAL E A IMAGEM EM PRETO E BRANCO
    for idx, image in enumerate(list_images):

        # INICIANDO AS VARIÁVEL QUE ARMAZENARÁ O RESULTADO DA RODADA
        info_doc = {}

        print("-" * 50)
        print("MODELO TRÊS - RODADA: {}".format(idx))

        # DEFININDO A CLASSE DE PRÉ PROCESSAMENTO
        pre_processing = Image_Pre_Processing(settings.BLUR_KSIZE,
                                              settings.THRESHOLD_MAX_COLOR_VALUE,
                                              settings.DILATION_KSIZE,
                                              settings.WIDTH_RESIZE,
                                              settings.OUTPUT_SIZE)

        # DEFININDO AS PROPRIEDADES PARA A LEITURA DA IMAGEM (OCR)
        rg_reader = Execute_OCR_RG(pre_processing)

        # REALIZANDO O FLUXO COMPLETO
        info_doc = rg_reader.execute_pipeline_ocr(image)

        # ARMAZENANDO O RESULTADO
        print("RESULTADO OBTIDO - RODADA: {}".format(idx))
        print(info_doc)

        result_model.append(["", info_doc])

    return result_model
