"""

    FUNÇÕES UTEIS PARA CODIFICAÇÃO E DECODIFICAÇÃO DE BASE64.

    A SAÍDA DA DECODIFICAÇÃO É NO FORMATO ARQUIVO IMAGEM (SALVO NA PASTA RAIZ).

    # Arguments
        file_base64                - Required : Input no formato Base64 (BASE64)

    # Returns
        built_pdf                  - Required : Caminho/Nome do arquivo gerado (String)

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "08/03/2022"


import base64
from inspect import stack
import imghdr
import mimetypes
import os

import magic

import execute_log


def base64_get_extension(file_base64_decode):

    """

         ESSA FUNÇÃO RETORNA O TIPO DA IMAGEM DECODIFICADA DO BASE64.

         PARA OBTER A EXTENSÃO UTILIZA-SE O MIMETYPE:
            Adivinha a extensão de um arquivo com base em seu tipo MIME, fornecido por tipo .
            O valor de retorno é uma string que fornece uma
            extensão de nome de arquivo, incluindo o ponto inicial ( '.')

         # Arguments
            file_base64_decode          - Required : Input no formato Base64 Decodificado (Stromg)

        # Returns
            extension                  - Required : Extensão da imagem decodificada (String)

    """

    extension = None

    try:
        # OBTENDO A EXTENSÃO
        mime_type = magic.from_buffer(file_base64_decode, mime=True)
        extension = mimetypes.guess_extension(mime_type)

    except Exception as ex:
        execute_log.error("ERRO NA FUNÇÃO {} - {]".format(stack()[0][3], ex))

    return extension


def base64_to_image(file_base64):

    """

         ESSA FUNÇÃO TEM COMO OBJETIVO, CONVERTER FORMATO DE INPUT (BASE64) -> IMAGE (PNG)

         O ARQUIVO OBTIDO (PNG) É SALVO NA MÁQUINA QUE ESTÁ EXECUTANDO O MODELO.

         # Arguments
            file_base64                - Required : Input no formato Base64 (BASE64)

        # Returns
            built_image                - Required : Caminho/Nome do arquivo gerado (String)

    """

    # FORMATANDO O NOME DE SAVE DO ARQUIVO PNG
    built_image = os.path.join(os.getcwd(), "INPUT_BASE64.PNG")

    # REALIZANDO A ABERTURA DE UM ARQUIVO (QUE SERÁ ESCRITO NA MÁQUINA)
    with open(built_image, "wb") as image_base64:

        try:
            # DECODOFICANDO A BASE64, ARMAZENANDO-O NO OBJETO ABERTO
            # ESCREVENDO NA MÁQUINA

            result_decode = base64.b64decode(file_base64.decode())

            # OBTENDO A EXTENSÃO DO ARQUIVO
            extension = base64_get_extension(result_decode)

            image_base64.write(result_decode)

        except Exception as ex:
            execute_log.error("ERRO NA FUNÇÃO {} - {]".format(stack()[0][3], ex))

    return built_image


def image_to_base64(file_image):

    """

         ESSA FUNÇÃO TEM COMO OBJETIVO, CONVERTER FORMATO DE INPUT (PNG) -> BASE64

         O ARQUIVO OBTIDO (PNG) É SALVO NA MÁQUINA QUE ESTÁ EXECUTANDO O MODELO.

         # Arguments
            file_image                - Required : Caminho do arquivo
                                                   no formato imagem (String)

        # Returns
            built_base64              - Required : Valor no formato Base64 (BASE64)

    """

    # INICIANDO A VARIÁVEL QUE RECEBERÁ O VALOR DA BASE64
    built_base64 = None

    try:
        # DECODOFICANDO A BASE64, ARMAZENANDO-O NO OBJETO ABERTO
        # ESCREVENDO NA MÁQUINA
        built_base64 = base64.b64encode(open(file_image, 'rb').read())

    except Exception as ex:
        execute_log.error("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return built_base64