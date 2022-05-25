"""

    CLASSE CONTENDO FUNÇÕES PARA OBTENÇÃO DO
    PERCENTUAL DE CONFIANÇA DE UMA PALAVRA, DADO A EXTRAÇÃO DO OCR.

        1) RECEBE O DATAFRAME/DICT CONTENDO PALAVRAS E PERCENTUAIS DE CONFIANÇA
        2) FILTRA O PERCENTUAL DE CONFIANÇA DE UMA DETERMINADA LISTA DE PALAVRAS

    FORNECE FUNÇÃO PARA CALCULAR A MÉDIA, DADA UMA LISTA DE PALAVRAS E PERCENTUAIS DE CONFIANÇA.

     # Arguments
        list_values                         - Required : Palavras para obter
                                                         o percentual de confiança (List)
        info_ocr_image_data                 - Required : Coleção de dados
                                                         contendo palavras e
                                                         percentuais de confiança (DataFrame | Dict)

    # Returns
        result_confidence_percentage        - Required : Resultado contendo palavras
                                                         e percentuais de confiança (List)

"""

__version__ = "1.0"
__author__ = "Emerson V. Rafael (EMERVIN)"
__data_atualizacao__ = "26/04/2022"


import re
from inspect import stack


def get_confidence_percentage(list_values, info_ocr_image_data):

    """

        OBTÉM O PERCENTUAL DE CONFIANÇA DE UMA PALAVRA, DADO A EXTRAÇÃO DO OCR.

        1) RECEBE O DATAFRAME/DICT CONTENDO PALAVRAS E PERCENTUAIS DE CONFIANÇA
        2) FILTRA O PERCENTUAL DE CONFIANÇA DE UMA DETERMINADA LISTA DE PALAVRAS

        # Arguments
            list_values                         - Required : Palavras para obter
                                                             o percentual de confiança (List)
            info_ocr_image_data                 - Required : Coleção de dados
                                                             contendo palavras e
                                                             percentuais de confiança (DataFrame | Dict)

        # Returns
            result_confidence_percentage        - Required : Resultado contendo palavras
                                                             e percentuais de confiança (List)

    """

    # INICIANDO O VALOR DO PERCENTUAL DE CONFIANÇA
    result_confidence_percentage = []

    # VERIFICANDO SE O LIST_VALUES É UMA STRING OU LISTA
    if not isinstance(list_values, list):
        # CONVERTENDO A STRING EM LIST PELO SPLIT EM ESPAÇOS
        list_values = str(list_values).split(" ")

    # PERCORRENDO CADA UM DOS VALORES DA LISTA
    for value_text in list_values:

        # SEPARANDO O VALOR ATUAL ATRAVÉS DOS ESPAÇOS
        # CASO O VALOR NÃO POSSUA SEPARAÇÃO, APENAS UMA CONFIANÇA É OBTIDA
        # PARA O VALOR QUE POSSUI SEPARAÇÃO, É OBTIDA UMA CONFIANÇA
        # PARA CADA VALOR É OBTIDA UMA MÉDIA DE TODOS OS PERCENTUAIS

        for value_split in value_text.split(" "):

            try:
                # OBTENDO O VALOR NO DATAFRAME DE INFO_OCR
                filter_value = info_ocr_image_data[info_ocr_image_data["text"].astype(str).str.contains(value_split,
                                                                                                        na=False)]

                if not filter_value.empty:
                    # OBTENDO O VALOR DO PERCENTUAL DE CONFIANÇA
                    value_conf_percentage = filter_value["conf"].values[0]
                else:
                    value_conf_percentage = 0

                # REALIZANDO O APPEND NO RESULTADO FINAL
                result_confidence_percentage.append([value_split, value_conf_percentage])

            except re.error:
                result_confidence_percentage.append([value_text, 0])

            except Exception as ex:
                print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

                result_confidence_percentage.append([value_text, 0])

    # RETORNANDO A LISTA CONTENDO
    # [PALAVRA, PERCENTUAL DE CONFIANÇA]
    return result_confidence_percentage


def get_average(names_w_conf, weighted=True):

    """

        CALCULA O PERCENTUAL DE CONFIANÇA MÉDIO DA LEITURA DO NOME
        * O NOME CONTÉM O PERCENTUAL DE CONFIANÇA DE VÁRIAS PALAVRAS (QUE JUNTAS COMPÕEM O NOME)

        O PERCENTUAL DE CONFIANÇA PODE SER CALCULADO USANDO:
            1) weighted = True: Pondera-se o peso através do tamanho da palavra.
            2) weighted = False: A média é calculada apenas
                                 utilizando os percentuais de confiança individuais.

        # Arguments
            names_w_conf                        - Required : Lista de listas contendo
                                                             cada um dos nomes e seu
                                                             percentual de confiança (List)
            weighted                            - Required : Se deve ser considerada a média ponderada
                                                            (pelo tamanho do nome) (Boolean)

        # Returns
            output                            - Required : Percentual de confiança médio do nome (Float)

    """

    # INICIANDO AS VARIÁVEIS UTEIS
    avg = 0

    # LISTA DE LISTA COM O TAMANHO DO NOME (LEN) E O PERCENTUAL DE CONFIANÇA DA LEITURA
    len_w_conf = [[len(nome[0]), nome[1]] for nome in names_w_conf]

    try:
        if weighted:
            # MÉDIA PONDERADA
            avg = sum([len_w_conf[i][0]*len_w_conf[i][1] for i in range(len(len_w_conf))])/sum(len_w_conf[i][0] for i in range(len(len_w_conf)))

        else:
            # MÉDIA SIMPLES
            avg = sum(len_w_conf[i][1] for i in range(len(len_w_conf)))/len(len_w_conf)

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return avg