"""

    FUNÇÕES UTEIS PARA CONVERSÃO DE IMAGEM ENTRE FORMATOS.

    A IMAGEM ORIGINAL PODE ESTAR NOS FORMATOS: BASE64, STR, ARRAY, FORMATO DE IMAGEM (PIL).

    A SAÍDA DA IMAGEM É NO FORMATO PIL.

    # Arguments
        imagem                     - Required : Imagem atual antes da formatação
                                                Imagem pode estar nos formatos PIL, Array,
                                                Base64 ou caminho da imagem (PIL | Array |
                                                                             BASE64 | String)
        nome_imagem                - Required : Nome da imagem atual (String)
        identificador              - Required : Identificador da chamada (Taskid) (String)

    # Returns
        img_pil                    - Required : Imagem convertida para formato PIL (PIL)

"""

__version__ = "2.0"
__author__ = """Patricia Catandi (CATANDI) & Oscar Bedoya (BEDOYAO) & Edson Mano (EDDANSA) &
                Lucas Menegheso (MENEFAR) & Fabio Andre Sonza (SONZAFA) & 
                Rafael Barbosa Ferreira (RBFRDTH) & Felipe Gomes Luttzolff (LUTTZOL) &
                Emerson V. Rafael (EMERVIN) & Henrique Fantinatti (HENRFAN)"""


import base64
import io
from inspect import stack

from dynaconf import settings
import numpy as np
from PIL import Image


def open_image_pil(image):

    """

        ESSA FUNÇÃO TEM COMO OBJETIVO, CONVETER STR -> FORMATO DE IMAGEM (PIL)

        # Arguments
            image                      - Required : Imagem atual antes da formatação
                                                    Imagem no formato caminho da imagem (String)

        # Returns
            img_pil                    - Required : Imagem convertida para formato PIL (PIL)

    """

    # INICIANDO A VARIÁVEL QUE RECEBERÁ A IMAGEM NO FORMATO PIL
    img_pil = "null"

    try:
        img_pil = Image.open(image)
    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    return img_pil


def base64_to_pil(image):

    """

        OS ESQUEMAS DE CODIFICAÇÃO BASE64 SÃO COMUMENTE USADOS QUANDO
        HÁ NECESSIDADE DE CODIFICAR DADOS BINÁRIOS, ESPECIALMENTE QUANDO
        ESSES DADOS PRECISAM SER ARMAZENADOS E TRANSFERIDOS POR MEIO DE MÍDIA
        PROJETADA PARA LIDAR COM TEXTO. ESSA CODIFICAÇÃO AJUDA A GARANTIR
        QUE OS DADOS PERMANEÇAM INTACTOS SEM MODIFICAÇÃO DURANTE O TRANSPORTE.

        ESSA FUNÇÃO TEM COMO OBJETIVO, CONVETER BASE64 -> FORMATO DE IMAGEM (PIL)

        # Arguments
            image                  - Required : Imagem que será decodificada
                                                de base64 (Base64)

        # Returns
            img_pil                - Required : Imagem convertida para formato PIL (PIL)

    """

    # INICIANDO A VARIÁVEL QUE RECEBERÁ A IMAGEM NO FORMATO PIL
    img_pil = "null"

    try:
        img_str = io.BytesIO(base64.b64encode(image))
        img_pil = Image.open(img_str, mode='r')

    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    return img_pil


def array_to_pil(image):

    """

        CRIA UMA MEMÓRIA DA IMAGEM A PARTIR DE UM OBJETO QUE EXPORTA
        A INTERFACE DO ARRAY (USANDO O PROTOCOLO DE BUFFER).

        ESSA FUNÇÃO TEM COMO OBJETIVO, CONVETER ARRAY -> FORMATO DE IMAGEM (PIL)

        # Arguments
            image                 - Required : Imagem atual antes da formatação
                                                Imagem no formato Array (Array)

        # Returns
            img_pil                - Required : Imagem convertida para formato PIL (PIL)

    """

    # INICIANDO A VARIÁVEL QUE RECEBERÁ A IMAGEM NO FORMATO PIL
    img_pil = "null"

    try:
        img_pil = Image.fromarray(image, mode='r')

    except Exception as ex:
        # print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))
        pass
        img_pil = image

    return img_pil


def str_to_base64(image):

    """

        OS ESQUEMAS DE CODIFICAÇÃO BASE64 SÃO COMUMENTE USADOS QUANDO
        HÁ NECESSIDADE DE CODIFICAR DADOS BINÁRIOS, ESPECIALMENTE QUANDO
        ESSES DADOS PRECISAM SER ARMAZENADOS E TRANSFERIDOS POR MEIO DE MÍDIA
        PROJETADA PARA LIDAR COM TEXTO. ESSA CODIFICAÇÃO AJUDA A GARANTIR
        QUE OS DADOS PERMANEÇAM INTACTOS SEM MODIFICAÇÃO DURANTE O TRANSPORTE.

        ESSA FUNÇÃO TEM COMO OBJETIVO, CONVETER STR -> BASE64

        # Arguments
            image                  - Required : Imagem que será decodificada de base 64 (Base64)

        # Returns
            img_pil                - Required : Imagem convertida para formato PIL (PIL)

    """

    # INICIANDO A VARIÁVEL QUE RECEBERÁ A IMAGEM NO FORMATO BASE64
    img_base64 = "null"

    try:
        img_base64 = image.encode("utf-8")

    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    return img_base64


def orchestra_read_image(image):

    """

        ORQUESTRA A CONVERSÃO DE IMAGEM ENTRE FORMATOS.

        A IMAGEM ORIGINAL PODE ESTAR NOS FORMATOS: BASE64, STR, ARRAY, FORMATO DE IMAGEM (PIL).

        A SAÍDA DA IMAGEM É NO FORMATO PIL.

        # Arguments
            image                  - Required : Imagem que será convertida.
                                                A imagem pode estar em formato PIL,
                                                array, base64 ou string (PIL | Array |
                                                                         Base64 | String)

        # Returns
            img_pil                - Required : Imagem em formato PIL (PIL)

    """

    # INICIANDO A VARIÁVEL QUE RECEBERÁ A IMAGEM NO FORMATO PIL
    img_pil = "null"

    try:
        # ORQUESTRA A CONVERSÃO DE IMAGEM

        if type(image) == bytes:

            """
            
                A IMAGEM ESTÁ EM FORMATO DE BYTES (BASE64)
                CONVERTE BASE64 -> PIL
            
            """

            img_pil = base64_to_pil(image)

        elif type(image) == str:

            """

                A IMAGEM ESTÁ EM FORMATO DE STRING
                CONVERTE STRING -> PIL

            """

            # APLICANDO O ENCODE UTF-8 NA IMAGEM (UNICODE)
            imagem = str_to_base64(image)
            img_pil = base64_to_pil(imagem)

            if img_pil == "null":
                img_pil = open_image_pil(imagem)


        elif type(image) is np.ndarray:

            """

                A IMAGEM ESTÁ EM FORMATO DE ARRAY
                CONVERTE ARRAY -> PIL

            """

            img_pil = array_to_pil(image)

        else:
            img_pil = image

    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    # RETORNANDO A IMAGEM CONVERTIDA
    return img_pil










