from inspect import stack

from pydantic import validate_arguments, ValidationError

from MODELS.main_model_three import main_model as main_model_tree_verso
from MODELS.main_model_three_frente import main_model as main_model_three_frente


@validate_arguments
def orchestrator_model(tipo_documento: str,
                       verso: bool,
                       imagem: bytes):

    """

        FUNÇÃO RESPONSÁVEL POR ORQUESTRAR A CHAMADA DO MODELO

        REALIZA A ORQUESTRAÇÃO
            - MODELO TRÊS - FRENTE
            - MODELO TRÊS - VERSO

        RETORNA O RESULTADO DO MODELO

        # Arguments:
            kwargs               - Required : Argumentos do modelo (Dict)

        # Returns:
            result_model         - Required : Resultado do modelo (Json)

    """

    result_model = None

    try:
        if tipo_documento == "RG":

            if verso == True:
                # IMAGEM ENVIADA É RG - VERSO
                print("RG - VERSO")
                result_model = main_model_tree_verso(imagem)
            elif verso == False:
                # IMAGEM ENVIADA É RG - FRENTE
                print("RG - FRENTE")
                result_model = main_model_three_frente(imagem)
            else:
                print("O PARÂMETRO 'verso' DEVE SER TRUE OU FALSE")

        else:
            print("O PARÂMETRO 'tipo_documento' DEVE SER RG")

    except ValidationError as exc:
        print(exc)

    return result_model


def main_orchestrator_model(kwargs):

    """

        FUNÇÃO RESPONSÁVEL POR ORQUESTRAR A CHAMADA DO MODELO

        # Arguments:
            kwargs               - Required : Argumentos do modelo (Dict)

        # Returns:
            result_model         - Required : Resultado do modelo (Json)

    """

    result_model = None

    try:
        # REALIZANDO A CHAMADA DO MODELO
        result_model = orchestrator_model(**kwargs)

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return result_model