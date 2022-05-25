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

    MODELO UTILIZADO: MODELO DE MÁSCARAS

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


from inspect import stack

from dynaconf import settings

from PROCESSINGS.model_pre_processing import Image_Pre_Processing
from model_ocr import Execute_OCR_RG
from UTILS.image_read import read_image, read_image_gray
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
    dict_images = {}

    # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO DO MODELO
    result_model = []

    # REALIZANDO A LEITURA DA IMAGEM - RGB
    img_rgb = read_image(dir_image)

    if settings.ROTATE_IMAGE:
        # REALIZANDO A ROTAÇÃO DA IMAGEM
        # ATUALIZANDO A IMAGEM RGB COM A IMAGEM ROTACIONADA
        img_rgb = rotate_image(img_rgb)

    # REALIZANDO A LEITURA DA IMAGEM - ESCALA DE CINZA
    img_gray = read_image_gray(img_rgb)

    if settings.PRE_PROC_IMAGE:
        # DEFININDO A CLASSE DE PRÉ PROCESSAMENTO
        # UTILIZA-SE A IMAGEM RGB
        img_original, cropped_image, warped_img = Image_Pre_Processing(settings.BLUR_KSIZE,
                                                                       settings.THRESHOLD_MAX_COLOR_VALUE,
                                                                       settings.DILATION_KSIZE,
                                                                       settings.WIDTH_RESIZE,
                                                                       settings.OUTPUT_SIZE).orchestra_pre_processing(img_gray)

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
        dict_images["IMAGEM_CROPPED_GRAY_DUPLO_CHECK"] = check_orientation.get_image_correct_orientation(cropped_image, 2)

    # ENVIANDO A IMAGEM ORIGINAL E A IMAGEM EM PRETO E BRANCO
    for idx, image in enumerate(dict_images):

        # INICIANDO AS VARIÁVEL QUE ARMAZENARÁ O RESULTADO DA RODADA
        info_doc = {}

        print("-" * 50)
        print("MODELO DOIS - RODADA: {} - {}".format(idx, image))

        # DEFININDO AS PROPRIEDADES PARA A LEITURA DA IMAGEM (OCR)
        # REALIZANDO O OCR
        text, data_exp, data_nasc, list_result_rg, list_result_cpf, \
        nome, nome_pai, nome_mae, \
        cidade_nasc, estado_nasc, cidade_origem, estado_origem = Execute_OCR_RG(side_document="VERSO").execute_pipeline_ocr(dict_images[image])

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

        # VISUALIZANDO OS RESULTADOS
        print("RESULTADO OBTIDO - RODADA: {} - {}".format(idx, image))
        print(info_doc)

        result_model.append([text, info_doc])

    return result_model
