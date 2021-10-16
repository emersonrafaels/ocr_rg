"""

    FUNÇÕES PARA LEITURA DA IMAGEM.

    # Arguments
        object                  - Required : Imagem para leitura/visualização (String | Object)
    # Returns

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "15/10/2021"


from inspect import stack

import cv2
from PIL import Image


def read_image_gray(image_path):

    """

        FUNÇÃO PARA LEITURA DE UMA IMAGEM.

        # Arguments
            caminho_imagem       - Required : Caminho da imagem a ser lida (String)
        # Returns
            img                  - Required : Imagem após leitura (Array)

    """

    # INICIANDO O OBJETO DA IMAGEM
    img = None

    try:
        # A LEITURA É FEITA EM FORMATO RGB
        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    return img


def read_image_rgb(image_path):

    """

        FUNÇÃO PARA LEITURA DE UMA IMAGEM.

        # Arguments
            caminho_imagem       - Required : Caminho da imagem a ser lida (String)
        # Returns
            img                  - Required : Imagem após leitura (Array)

    """

    # INICIANDO O OBJETO DA IMAGEM
    img = None

    try:
        # A LEITURA É FEITA EM FORMATO RGB
        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    return img


def realiza_leitura_imagem(caminho_imagem):

    """

        FUNÇÃO PARA LEITURA DE UMA IMAGEM.

        # Arguments
            caminho_imagem       - Required : Caminho da imagem a ser lida (String)
        # Returns
            img                  - Required : Imagem após leitura (Object)

    """

    # INICIANDO O OBJETO DA IMAGEM
    img = None

    try:
        # UTILIZANDO O OPENCV PARA LEITURA DA IMAGEM
        # A LEITURA É FEITA EM FORMATO BGR
        img = cv2.imread(caminho_imagem)
    except Exception as ex:
        print(ex)

    return img


def realiza_leitura_imagem_pillow(caminho_imagem):

    """

        FUNÇÃO PARA LEITURA DE UMA IMAGEM.
        UTILIZA PIL - IMAGE

        # Arguments
            caminho_imagem       - Required : Caminho da imagem a ser lida (String)
        # Returns
            img                  - Required : Imagem após leitura (Object)

    """

    # INICIANDO O OBJETO DA IMAGEM
    img = None

    try:
        # UTILIZANDO O PILLOW PARA LEITURA DA IMAGEM
        # A LEITURA É FEITA EM FORMATO RGB
        img = Image.open(caminho_imagem)
    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    return img