import re
from inspect import stack

from dynaconf import settings
import unidecode

from CONFIG import config
from PROCESS_FIELDS.process_names import Execute_Process_Names
from PROCESS_FIELDS.process_location import Execute_Process_Location
from PROCESS_FIELDS.process_data import Execute_Process_Data
from PROCESS_FIELDS.process_rg_cpf import Execute_Process_RG_CPF


class Pos_Processing_Fields():

    def __init__(self):

        # 1 - DEFININDO OS PATTERNS
        self.pattern_data = settings.REGEX_ONLY_DATES
        self.pattern_rg = settings.REGEX_RG
        self.pattern_cpf = settings.REGEX_CPF
        self.pattern_uf = settings.REGEX_UF


    @staticmethod
    def __postprocess_string(field, regex_only_letters=settings.REGEX_ONLY_LETTERS):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) MANTÉM APENAS LETRAS
                2) RETIRA ESPAÇOS EM EXCESSO

            # Arguments
                field                - Required : Valor a ser pós processado (String)
                regex_only_letters   -  Required : Pattern a ser utilizado (Regex)

            # Returns
                output               - Required : Valor após processamento (String)

        """

        try:
            # MANTENDO APENAS LETRAS E TORNANDO O TEXTO UPPERCASE
            output = re.sub(regex_only_letters, " ", field).strip().upper()

            # RETIRANDO ESPAÇOS DESNECESSÁRIOS
            output = re.sub(' +', ' ', output)

            # RETIRANDO OS ACENTOS
            output = unidecode.unidecode(output)

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    @staticmethod
    def __postprocess_num(field, regex_only_x_numbers=settings.REGEX_ONLY_X_NUMBERS):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) MANTÉM APENAS LETRAS, NÚMEROS, PONTOS ('.') BARRAS ('/') E TRAÇOS ('-')
                2) RETIRA ESPAÇOS EM EXCESSO

            # Arguments
                field                - Required : Valor a ser pós processado (String)
                regex_only_letters   -  Required : Pattern a ser utilizado (Regex)

            # Returns
                output               - Required : Valor após processamento (String)

        """

        try:
            # SUBSTITUINDO '/' POR '-'
            output = re.sub(r"/", "-", field)

            # SUBSTITUINDO ',' POR '.'
            output = output.replace(",", ".")

            # MANTENDO APENAS A LETRA X E NÚMEROS
            output = re.sub(regex_only_x_numbers, "", field).replace("  ", " ").strip()

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            output = field

        return output


    def orchestra_pos_processing_get_fields(self, text, info_ocr=config.INFO_OCR_DEFAULT):

        # OBTENDO AS DATAS
        data_exp, data_nasc = Execute_Process_Data().get_result_datas(text,
                                                                      self.pattern_data,
                                                                      info_ocr=info_ocr)

        # OBTENDO CPF
        list_result_cpf = Execute_Process_RG_CPF().get_values(text,
                                                              self.pattern_cpf,
                                                              limit_values=1,
                                                              info_ocr=info_ocr)

        # OBTENDO RG (FILTRANDO VALORES QUE JÁ CONSTAM COMO CPF)
        list_result_rg = Execute_Process_RG_CPF().get_values(text,
                                                             self.pattern_rg,
                                                             filters_validate=[list_result_cpf[0][0]],
                                                             limit_values=1,
                                                             info_ocr=info_ocr)

        # OBTENDO AS CIDADES-ESTADO
        cidade_nasc, \
        estado_nasc, \
        cidade_origem, \
        estado_origem = Execute_Process_Location().get_result_location(text,
                                                                       self.pattern_uf,
                                                                       info_ocr=info_ocr)

        # RESULTADOS ATÉ ENTÃO
        # RESULTADOS ATÉ ENTÃO
        results_ocr = [data_exp[0], data_nasc[0],
                       cidade_nasc[0], estado_nasc[0],
                       cidade_origem[0], estado_origem[0],
                       list_result_rg[0][0],
                       list_result_cpf[0][0]]

        # OBTENDO OS NOMES
        nome, nome_pai, nome_mae = Execute_Process_Names().orchestra_get_names(text,
                                                                               results_ocr,
                                                                               info_ocr=info_ocr)

        # FORMATANDO O RESULTADO DOS CAMPOS NUMÉRICOS
        list_result_rg = [Pos_Processing_Fields.__postprocess_num(list_result_rg[0][0], settings.REGEX_ONLY_X_NUMBERS),
                          round(list_result_rg[0][1], settings.ARREND_PERCENTAGE_CONFIDENCE)]
        list_result_cpf = [Pos_Processing_Fields.__postprocess_num(list_result_cpf[0][0], settings.REGEX_ONLY_NUMBERS),
                           round(list_result_cpf[0][1], settings.ARREND_PERCENTAGE_CONFIDENCE)]

        # FORMATANDO O RESULTADO DOS CAMPOS DATAS
        data_exp = [data_exp[0], round(data_exp[1], settings.ARREND_PERCENTAGE_CONFIDENCE)]
        data_nasc = [data_nasc[0], round(data_nasc[1], settings.ARREND_PERCENTAGE_CONFIDENCE)]

        # FORMATANDO O RESULTADO DOS CAMPOS STRINGS
        nome = [Pos_Processing_Fields.__postprocess_string(nome[0], settings.REGEX_ONLY_LETTERS),
                round(float(nome[1]), settings.ARREND_PERCENTAGE_CONFIDENCE)]
        nome_pai = [Pos_Processing_Fields.__postprocess_string(nome_pai[0], settings.REGEX_ONLY_LETTERS),
                    round(float(nome_pai[1]), settings.ARREND_PERCENTAGE_CONFIDENCE)]
        nome_mae = [Pos_Processing_Fields.__postprocess_string(nome_mae[0], settings.REGEX_ONLY_LETTERS),
                    round(float(nome_mae[1]), settings.ARREND_PERCENTAGE_CONFIDENCE)]
        cidade_nasc = [Pos_Processing_Fields.__postprocess_string(cidade_nasc[0], settings.REGEX_ONLY_LETTERS),
                       round(float(cidade_nasc[1]), settings.ARREND_PERCENTAGE_CONFIDENCE)]
        estado_nasc = [Pos_Processing_Fields.__postprocess_string(estado_nasc[0], settings.REGEX_ONLY_LETTERS),
                       round(float(estado_nasc[1]), settings.ARREND_PERCENTAGE_CONFIDENCE)]
        cidade_origem = [Pos_Processing_Fields.__postprocess_string(cidade_origem[0], settings.REGEX_ONLY_LETTERS),
                         round(float(cidade_origem[1]), settings.ARREND_PERCENTAGE_CONFIDENCE)]
        estado_origem = [Pos_Processing_Fields.__postprocess_string(estado_origem[0], settings.REGEX_ONLY_LETTERS),
                         round(float(estado_origem[1]), settings.ARREND_PERCENTAGE_CONFIDENCE)]

        return text, data_exp, data_nasc, list_result_rg, list_result_cpf, \
               nome, nome_pai, nome_mae, \
               cidade_nasc, estado_nasc, cidade_origem, estado_origem