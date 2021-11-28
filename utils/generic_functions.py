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
from os import path, makedirs
import re
import time

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


def convert_string_to_date(value_string, dict_months, pattern_only_leters):

    """

        REALIZA A CONVERSÃO DE UMA STRING EM FORMATO DATE.

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
        # CASO HAJA, A FUNÇÃO REALIZARÁ A CONVERSÃO PARA NÚMERO
        result_date = replace_month_letters_to_number(value_string, dict_months, pattern_only_leters)

        return result_date

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
        result_date = value_string

    return result_date

