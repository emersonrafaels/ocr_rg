from inspect import stack

from dynaconf import settings

from CONFIG import config
from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import applied_filter_not_intesection_list
from PROCESS_FIELDS.process_confidence_percentage import get_confidence_percentage, get_average


class Execute_Process_RG_CPF():

    def __init__(self):

        # 1 - DEFININDO OS PATTERNS
        self.pattern_rg = settings.REGEX_RG
        self.pattern_cpf = settings.REGEX_CPF

        # 2 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()


    def get_values(self, text, pattern, filters_validate=[],
                   limit_values=None, info_ocr=config.INFO_OCR_DEFAULT):

        """

            ORQUESTRA A OBTENÇÃO DE VALORES EM UM TEXTO, DE ACORDO COM UM PATTERN.

            RECEBE A OPÇÃO DE RETIRAR DA LISTA RESULTANTE
            VALORES DE UMA LISTA AUXILIAR ('list_validate')

            # Arguments
                text                - Required : Texto a ser analisado (String)
                pattern             - Required : Pattern a ser utilizado para
                                                 obtenção dos dados (Regex)
                filters_validate    - Optional : Filtros e validações
                                                 a serem aplicadas (List)
                limit_values        - Optional : Limite de valores desejados (Integer)
                info_ocr            - Optional : ImageData do OCR (DataFrame | Dict)

            # Returns
                list_result         - Required : Resultados dos matchs (List)

        """

        # INICIANDO AS VARIÁVEIS
        list_result = []
        list_result_percentage_confidence = [["", 0]]
        list_result_percentage_confidence_default = [["", 0]]

        try:
            # OBTENDO OS REGISTROS GERAIS
            list_result = self.orchestra_extract_infos.get_matchs_strings(text, pattern)

            if len(list_result):

                # FORMATANDO A LISTA DE REGISTROS GERAIS OU CPFS
                list_result = [value[-1] for value in list_result if not applied_filter_not_intesection_list([value[-1]],
                                                                                                             filters_validate,
                                                                                                             mode="FIND")]

                if limit_values:
                    list_result = list_result[:limit_values]

                if limit_values:
                    # OBTENDO O PERCENTUAL DE CONFIANÇA DESSES VALORES
                    list_result_percentage_confidence = [[value_result, get_average(get_confidence_percentage(value_result, info_ocr))]
                                                         for value_result in list_result]

                else:
                    list_result_percentage_confidence = list_result_percentage_confidence_default

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            list_result_percentage_confidence = list_result_percentage_confidence_default

        return list_result_percentage_confidence