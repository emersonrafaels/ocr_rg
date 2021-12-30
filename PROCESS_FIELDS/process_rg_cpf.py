from inspect import stack

from dynaconf import settings

from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import applied_filter_not_intesection_list


class Execute_Process_RG_CPF():

    def __init__(self):

        # 1 - DEFININDO OS PATTERNS
        self.pattern_rg = settings.REGEX_RG
        self.pattern_cpf = settings.REGEX_CPF

        # 2 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()


    def get_values(self, text, pattern, filters_validate=[],
                   limit_values=None):
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


            # Returns
                list_result         - Required : Resultados dos matchs (List)

        """

        # INICIANDO AS VARIÁVEIS
        list_result = []

        try:
            # OBTENDO OS REGISTROS GERAIS
            list_result = self.orchestra_extract_infos.get_matchs_strings(text, pattern)

            if len(list_result):

                # FORMATANDO A LISTA DE REGISTROS GERAIS
                list_result = [value[-1] for value in list_result if not applied_filter_not_intesection_list([value[-1]],
                                                                                                             filters_validate,
                                                                                                             mode="FIND")]

                if limit_values:
                    list_result = list_result[:limit_values]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return list_result