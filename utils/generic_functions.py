"""

    FUNÇÕES GENÉRICAS UTILIZANDO PYTHON.

    # Arguments

    # Returns


"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "04/07/2021"


import datetime
from inspect import stack
from operator import itemgetter
from os import path, makedirs
import re
import time

from numpy import array
import pandas as pd


def verify_exists(dir):

    """

        FUNÇÃO PARA VERIFICAR SE DIRETÓRIO (PATH) EXISTE.

        # Arguments
            dir                   - Required : Diretório a ser verificado (String)

        # Returns
            validator             - Required : Validador da função (Boolean)

    """

    # INICIANDO O VALIDADOR DA FUNÇÃO
    validator = False

    try:
        validator = path.exists(dir)
    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    return validator


def create_path(dir):

    """

        FUNÇÃO PARA CRIAR UM DIRETÓRIO (PATH).

        # Arguments
            dir                   - Required : Diretório a ser criado (String)

        # Returns
            validator             - Required : Validador da função (Boolean)

    """

    # INICIANDO O VALIDADOR DA FUNÇÃO
    validator = False

    try:
        # REALIZANDO A CRIAÇÃO DO DIRETÓRIO
        makedirs(dir)

        validator = True
    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

    return validator


def converte_int(valor_para_converter):

    """

        FUNÇÃO GENÉRICA PARA CONVERTER UM VALOR PARA FORMATO INTEIRO.


        # Arguments
            valor_para_converter              - Required : Valor para converter (Object)

        # Returns
            valor_para_converter              - Required : Valor após conversão (Integer)

    """

    try:
        if isinstance(valor_para_converter, int):
            return valor_para_converter
        else:
            return int(valor_para_converter)
    except Exception as ex:
        print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))
        return None


def read_txt(data_dir, encoding=None):

    """

        REALIZA LEITURA DA BASE (TXT)

        # Arguments
            data_dir                      - Required : Diretório da base a ser lida (String)
            encoding                      - Optional : Encoding utilizado (String)

        # Returns
            validador                     - Required : Validação da função (Boolean)
            data                          - Required : Dados lidos (List)

    """

    # INICIANDO O VALIDADOR
    validador = False

    # INICIANDO A LISTA QUE ARMAZENARÁ O RESULTADO DA LEITURA
    data = []

    try:
        if encoding is not None:
            data = open(data_dir, 'r', encoding=encoding).read()
        else:
            data = open(data_dir, 'r').read()

        validador = True
    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return validador, data


def read_csv(data_dir):

    """

        REALIZA LEITURA DA BASE (CSV)

        # Arguments
            data_dir                      - Required : Diretório da base a ser lida (String)

        # Returns
            validador                     - Required : Validação da função (Boolean)
            dataframe                     - Required : Base lida (DataFrame)

    """

    # INICIANDO O VALIDADOR
    validador = False

    # INICIANDO O DATAFRAME DE RESULTADO DA LEITURA
    dataframe = pd.DataFrame()

    try:
        dataframe = pd.read_csv(data_dir, encoding='utf-8')

        validador = True
    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return validador, dataframe


def save_excel(dataframe_to_save, data_dir):

    """

        REALIZA SAVE DA BASE (CSV)

        # Arguments
            dataframe_to_save             - Required : Base a ser salva (DataFrame)
            data_dir                      - Required : Diretório da base a ser salva (String)

        # Returns
            validador                     - Required : Validação da função (Boolean)

    """

    # INICIANDO O VALIDADOR
    validador = False

    try:
        dataframe_to_save.to_excel(data_dir, index=None)

        validador = True
    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return validador


def format_values_int(list_input):

    """

        RECEBE UMA LISTA, PERCORRE OS SEUS VALORES.
        VERIFICA SE HÁ VALORES (EM FORMATO STRING
        QUE PODEM SER CONVERTIDOS PARA INT).


        # Arguments
            list_input             - Required : Lista a ser percorrida (List)

        # Returns
            list_result            - Required : Lista após formatação (List)

    """

    # INICIANDO A LISTA RESULTANTE
    list_result = []

    try:
        for value_x in list_input:

            # INICIANDO A LISTA AUXILIAR
            list_aux = []

            for value_j in value_x:

                if value_j.isdigit():
                    value_j = int(value_j)

                # SALVANDO O VALOR NA LISTA AUXILIAR
                list_aux.append(value_j)

            # SALVANDO A LISTA AUXILIAR, NA LISTA FINAL
            list_result.append(list_aux)

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    # RETORNANDO A LISTA RESULTANTE
    return list_result


def get_date_time_now(return_type):

    """

        OBTÉM TODOS OS POSSÍVEIS RETORNOS DE DATA E TEMPO.

        # Arguments
            return_type                    - Required : Formato de retorno. (String)

        # Returns

    """

    """%d/%m/%Y %H:%M:%S | %Y-%m-%d %H:%M:%S
    Dia: %d
    Mês: %
    Ano: %Y
    Data: %Y/%m/%d

    Hora: %H
    Minuto: %M
    Segundo: %S"""

    try:
        ts = time.time()
        stfim = datetime.datetime.fromtimestamp(ts).strftime(return_type)

        return stfim
    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
        return datetime.datetime.now()


def drop_duplicates_list(input_list):

    """

        RETIRA VALORES DUPLICADOS EM UMA LISTA.

        # Arguments
            input_list             - Required : Lista a ser percorrida (List)

        # Returns
            list_result            - Required : Lista após formatação (List)

    """

    return list(set(input_list))


def replace_month_letters_to_number(value_string, dict_months, pattern_only_leters):

    """

        REALIZA A CONVERSÃO (CASO EXISTA A NECESSIDADE) DE MESES (EX: 'FEV') PARA NÚMERO (EX: '02')

        # Arguments
            value_string           - Required : Valor a ser convertido (String)
            dict_months            - Required : Meses e sua respectiva ordem numérica (Dict)
            pattern_only_leters    - Optional : Pattern para manter apenas letras na string (Regex)

        # Returns
            value_date             - Required : Valor após conversão (Date)

    """

    # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO FINAL
    result_date = ""

    try:
        # VERIFICANDO SE HÁ LETRAS NA DATA (EX: 01/MAR/2021):
        result_only_letters = re.sub(pattern_only_leters, " ", value_string).replace("  ", " ").strip()

        if len(result_only_letters):

            # BUSCANDO REALIZAR UM SPLIT NA DATA
            result_split = value_string.split("/")

            # VERIFICANDO SE PARTE DA STRING CONTÉM UM MÊS VÁLIDO
            result_verified_month = [str(value) for value in result_split if
                                     str(value).upper() in [month for month in dict_months]]

            if result_verified_month:
                result_date = value_string.replace(result_verified_month[0],
                                                   str(dict_months[result_verified_month[0]]).zfill(2))

                return result_date

        return value_string

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
        result_date = value_string

    return result_date


def applied_filter_not_intesection_list(list_a, list_b,
                                        mode="FIND", min_len=1):

    """

        FUNÇÃO PARA OBTER OS VALORES DA LISTA_A QUE ESTÃO CONTIDOS NA LISTA_B.

        PARA ESTAR CONTIDO, HÁ DUAS OPÇÕES:
            1) FIND: BASTA PARTE DA STRING ESTAR DENTRO DE ALGUM DOS VALORES DA LIST_B.
            2) EQUAL: TODA PARTE DA STRING DEVE ESTAR 100% IGUAL A ALGUM DOS VALORES DA LIST_B

        # Arguments
            list_a                       - Required : Lista 'a' para ser analistada (List)
            list_b                       - Required : Lista 'b' para ser comparada (List)
            mode                         - Optional : Modo de comparação. O padrão é equal. (String)
            min_len                      - Optional : Número min de caracteres
                                                      para teste de validação (Integer)

        # Returns
            return_intersection          - Required : Valor após conversão (Date)

    """

    return_intersection = []

    try:
        # PERCORRENDO OS ELEMENTOS DA LISTA_A
        for value_list_a in list_a:

            # PERCORRENDO OS ELEMENTOS DA LISTA_b
            for value_list_b in list_b:

                if value_list_a != "" and value_list_b != "" and \
                        len(value_list_a) > min_len and len(value_list_b) > min_len:

                    if str(mode).upper() == "FIND":

                        if value_list_b.find(value_list_a)!=-1:

                            # OCORREU INTERSECCÇÃO
                            return_intersection.append(value_list_a)

                    else:
                        # MODO EQUAL
                        if value_list_b == value_list_a:

                            # OCORREU INTERSECCÇÃO
                            return_intersection.append(value_list_a)

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))


    return return_intersection


def convert_to_date(input_value, dict_months, pattern_only_leters):

    """

        FUNÇÃO PARA CONVERTER UMA STRING EM FORMATO DATE.

        # Arguments
            input_value            - Required : Valor para ser convertido (String)
            dict_months            - Required : Meses e sua respectiva ordem numérica (Dict)
            pattern_only_leters    - Optional : Pattern para manter apenas letras na string (Regex)

        # Returns
            return_value           - Required : Valor após conversão (Date)

    """

    try:
        # VERIFICANDO SE HÁ LETRAS NA DATA (EX: 01/MAR/2021):
        # CASO HAJA, A FUNÇÃO REALIZARÁ A CONVERSÃO PARA NÚMERO
        input_value = replace_month_letters_to_number(input_value, dict_months, pattern_only_leters)

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    try:
        if isinstance(input_value, str):

            if len(input_value) == 10:

                # A DATA POSSUI FORMATO DD-MM-YYYY OU DD/MM/YYYY OU DD.MM.YYYY
                if "/" in input_value:
                    return datetime.datetime.strptime(input_value, "%d/%m/%Y").date()
                elif "-" in input_value:
                    return datetime.datetime.strptime(input_value, "%d-%m-%Y").date()
                elif "." in input_value:
                    return datetime.datetime.strptime(input_value, "%d.%m.%Y").date()

            # A DATA POSSUI FORMATO DD-MM-YY OU DD/MM/YY OU DD.MM.YY
            if "/" in input_value:
                return datetime.datetime.strptime(input_value, "%d/%m/%y").date()
            elif "-" in input_value:
                return datetime.datetime.strptime(input_value, "%d-%m-%y").date()
            elif "." in input_value:
                return datetime.datetime.strptime(input_value, "%d.%m.%y").date()

        if isinstance(input_value, datetime):
            return datetime.date()
        else:
            return datetime.datetime.now().date()

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return datetime.date(1900, 1, 1)


def order_list_with_arguments(list_values, number_column_order=1, limit=1):

    """

        FUNÇÃO PARA ORDENAR UMA LISTA E OBTER UM NÚMERO (LIMIT) DE ARGUMENTOS.

            1) ORDENA A LISTA USANDO UM DOS SEUS ARGUMENTOS (number_column_order)
            2) FILTRA A LISTA DE ACORDO COM UM NÚMERO DESEJADO DE ELEMENTOS (limit)

        # Arguments
            list_values                  - Required : Lista de valores para processar (List)
            number_column_order          - Optional : Qual o argumento deve ser usado
                                                      como parâmetro de ordenação (Integer)
            limit                        - Optional : Número desejado de argumentos
                                                      para retorno da função (Integer)

        # Returns
            return_list                 - Required : Lista resultado (List)

    """

    # INICIANDO A LISTA DE VARIÁVEL QUE ARMAZENARÁ OS INDEX RESULTANTES
    list_idx = []

    # VERIFICANDO SE O ARGUMENTO DE ORDENAÇÃO É UM NÚMERO INTEIRO
    if isinstance(number_column_order, str):
        if number_column_order.isdigit():
            number_column_order = int(number_column_order)
        else:
            number_column_order = 1

    # VERIFICANDO SE O VALOR DE LIMIT É UM NÚMERO INTEIRO
    if isinstance(limit, str):
        if limit.isdigit():
            limit = int(limit)
        else:
            limit = 1

    # ORDENANDO POR UM DOS VALORES DE ARGUMENTOS DA LISTA
    # FILTRANDO DE ACORDO COM O LIMITE DESEJADO
    list_result_filter = sorted(list_values, key=lambda row: (row[number_column_order]), reverse=True)[:limit]

    # PERCORRENDO A LISTA DE RESULTADOS, PARA FILTAR NA LISTA ORIGINAL
    # O OBJETIVO É MANTER NA LISTA ORIGINAL (MANTENDO A ORDEM DELA)
    for value in list_result_filter:
        list_idx.append(list_values.index(value))

    # MANTENDO APENAS OS IDX DESEJADOS
    return_list = array(list_values, dtype=object)[list_idx]

    # RETORNANDO O RESULTADO
    return return_list


