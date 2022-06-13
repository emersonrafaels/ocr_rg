from dynaconf import settings

from UTILS.base64_encode_decode import base64_to_image, isbase64
from UTILS import generic_functions


def orchestra_get_files(input_file):

    """

        FUNÇÃO PARA ORQUESTRAR A OBTENÇÃO DOS ARQUIVOS NO QUAL A API DEVE ATUAR.

        PODE SER ENVIADO:
        1) CAMINHO DE UM ARQUIVO ESPECÍFICO
        2) DIRETÓRIO CONTENDO VÁRIOS ARQUIVOS
        3) INPUT EM BASE64

        ESSA FUNÇÃO É RESPONSÁVEL POR CHAMAR A FUNÇÃO DE OBTER TODOS OS ARQUIVOS NO DIRETÓRIO,
        CASO SEJA ENVIADO UM DIRETÓRIO.

        # Arguments
            input_file                       - Required : Caminho do(s) arquivo(s) a serme lidos.
                                                          Pode ser enviado um Path (String) ou Base64 (String)
            input_type                      - Required : Tipo do input (String)

        # Returns
            list_files_result                - Required : Caminho do(s) arquivo(s) listados. (List)

    """

    # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O TIPO DE INPUT
    input_type = None

    # VERIFICANDO SE O ARGUMENTO ENVIADO É UMA BASE64
    validator_base64, result_base64 = isbase64(input_file)

    if validator_base64:

        # O INPUT É UMA BASE64
        # CHAMA-SE AQ FUNÇÃO PARA DECODIFICAR A BASE64

        input_type = "BYTES"

        return input_type, base64_to_image(result_base64)

    # VERIFICANDO SE O ARGUMENTO ENVIADO É O CAMINHO DE UM ARQUIVO
    elif str(input_file).find(".") != -1:
        # O INPUT É UM ARQUIVO

        input_type = "ARCHIVE"

        return input_type, input_file

    # VERIFICANDO SE O ARGUMENTO ENVIADO É UMA LISTA
    elif isinstance(input_file, list):

        # O RETORNO É BASE64
        input_type = "BYTES"

        return input_type, [base64_to_image(file) for file in input_file if type(file) == bytes]

    else:
        # O INPUT É UM DIRETÓRIO
        # CHAMA-SE A FUNÇÃO PARA OBTER TODOS OS ARQUIVOS NO DIRETÓRIO

        input_type = "DIRECTORY"

        return input_type, generic_functions.get_files_directory(input_file,
                                                                 settings.FORMAT_TYPES_ACCEPTED)