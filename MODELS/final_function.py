"""

    FUNÇÃO PARA ESCOLHA DA RESPOSTA FINAL DO MODELO

        1) RECEBE UM JSON/DICT CONTENDO AS RESPOSTAS DOS N MODELOS
        2) FILTRA OS MAIORES PERCENTUAIS DE CONFIANÇA POR CAMPO
        3) RETORNA OS VALORES DOS MAIORES PERCENTUAIS DE CONFIANÇA

     # Arguments
        list_result_models                  - Required : Respostas dos N modelos (Dict)

    # Returns
        final_results                       - Required : Valores dos maiores
                                                         percentuais de confiança
                                                         por campo (Dict)

"""

__version__ = "1.0"
__author__ = "Emerson V. Rafael (EMERVIN)"
__data_atualizacao__ = "25/05/2022"


from inspect import stack

from dynaconf import settings
import pandas as pd
import numpy as np

from UTILS.generic_functions import convert_to_date


def model_selection(list_result_models):

    """

        FUNÇÃO PARA ESCOLHA DA RESPOSTA FINAL DO MODELO

            1) RECEBE UM JSON/DICT CONTENDO AS RESPOSTAS DOS N MODELOS
            2) FILTRA OS MAIORES PERCENTUAIS DE CONFIANÇA POR CAMPO
            3) RETORNA OS VALORES DOS MAIORES PERCENTUAIS DE CONFIANÇA

         # Arguments
            list_result_models                  - Required : Respostas dos N modelos (Dict)

        # Returns
            final_results                       - Required : Valores dos maiores
                                                             percentuais de confiança
                                                             por campo (Dict)

    """

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
                final_results[field_model] = (results_df.loc[results_df.iloc[:,
                                                             1] == results_df.iloc[:,
                                                                   1].max(), :].head(1).values)[0]

            else:
                print("CHAVE NÃO ENCONTRADA: {}".format(field_model))

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return final_results


def choose_final_name(df_image):

    # DEIXANDO APENAS VARIÁVEIS DE INTERESSE E ORDENANDO PELO PERCENTUAL DE CONFIANÇA DOS NOMES
    df_id = df_image.loc[: ["NOME", "NOME_PERCENT"]].sort_values(by="NOME_PERCENT",
                                                                 ascending=False).reset_index(drop=True)

    # INICIALIZANDO CONTADOR E FLAG
    cont = 0
    flag = True

    # REALIZAR A INTERAÇÃO ENQUANTO A CONDIÇÃO NÃO ESTÁ SATISFEITA
    while flag:

        # OBTENDO O PERCENTUAL DE CONFIANÇA ATUAL
        curr_perc = df_id.NOME_PERCENT[cont]
        next_perc = 0

        # TENTA PEGAR O PROXIMO PERCENTUAL, CASO EXISTA
        try:
            next_perc = df_id.NOME_PERCENT[cont + 1]
        except:
            df_nomes_test = df_id.iloc[: (cont + 1), :]
            flag = False

        # VERIFICANDO SE O PERCENTUAL DE CONFIANÇA ATUAL É
        # DIFERENTE DO PRÓXIMO PERCENTUAL DE CONFIANÇA
        if (curr_perc != next_perc) and flag:
            df_nomes_test = df_id.iloc[: (cont + 2), :]
            flag = False

        # INCREMENTA O CONTADOR
        cont +=1

        # OBTENDO A DIMENSÃO DOS NOMES
        df_nomes_test["LEN_NOME"] = df_nomes_test.NOME.apply(lambda x: len(x.split()))

        # ORDENANDO PELA DIMENSÃO E PERCENTUAL DE CONFIANÇA
        df_nomes_test.sort_values(by=["LEN_NOME", "NOME_PERCENT"],
                                  ascending=False, inplace=True)
        df_nomes_test.reset_index(drop=True, inplace=True)

        # RETORNANDO MAIOR NOME ENTRE OS ELEGÍVEIS
        return (np.array(df_nomes_test.iloc[0].loc[["NOME", "NOME_PERCENT"]]).astype("object"))
