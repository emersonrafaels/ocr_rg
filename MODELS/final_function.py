"""

    FUNÇÃO PARA ESCOLHA DA RESPOSTA FINAL DO MODELO

        1) RECEBE UM JSON/DICT CONTENDO AS RESPOSTAS DOS N MODELOS
        2) FILTRA OS MAIORES PERCENTUAIS DE CONFIANÇA POR CAMPO
        3) RETORNA OS VALORES DOS MAIORES PERCENTUAIS DE CONFIANÇA

    FORNECE FUNÇÃO PARA CALCULAR A MÉDIA, DADA UMA LISTA DE PALAVRAS E PERCENTUAIS DE CONFIANÇA.

     # Arguments
        list_result_models                  - Required : Respostas dos N modelos (Dict)

    # Returns
        final_results                       - Required : Valores dos maiores
                                                         percentuais de confiança
                                                         por campo (Dict)

"""

__version__ = "1.0"
__author__ = "Emerson V. Rafael (EMERVIN)"
__data_atualizacao__ = "10/05/2022"


from inspect import stack

from dynaconf import settings
import pandas as pd


def model_selection(list_result_models):

    print(list_result_models)

    # INICIANDO O DICT QUE ARMAZENARÁ O RESULTADO DA FUNÇÃO
    final_results = {}

    try:
        # PERCORRENDO CADA UM DOS CAMPOS ACEITOS PELO MODELO
        for field_model in settings.FIELDS:

            # VERIFICANDO SE O CAMPO ESTÁ NO DICT
            if field_model in list_result_models[0].keys():

                # CRIANDO UM DATAFRAME CONTENDO TODOS OS RESULTADOS PARA O CAMPO
                results_df = pd.DataFrame([list_result_[field_model] for list_result_ in list_result_models])

                # OBTENDO O VALOR MÁXIMO DO PERCENTUAL DE CONFIANÇA
                final_results[field_model] = (results_df.loc[results_df.iloc[:, 1] == results_df.iloc[:, 1].max(), :].head(1).values)[0]

            else:
                print("CHAVE NÃO ENCONTRADA: {}".format(field_model))

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return final_results

