from inspect import stack

from dynaconf import settings

from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import convert_to_date, remove_line_with_black_list_words


class Execute_Process_Data():

    def __init__(self):

        # 1 - DEFININDO OS PATTERNS
        self.pattern_data = settings.REGEX_ONLY_DATES

        # 2 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()


    def get_result_datas(self, text, pattern_data):

        """

            ORQUESTRA A OBTENÇÃO DAS DATAS DO DOCUMENTO:
                1) DATA DE EXPEDIÇÃO
                2) DATA DE NASCIMENTO

            # Arguments
                text                   - Required : Texto a ser analisado (String)
                pattern_data           - Required : Pattern a ser utilizado para
                                                    obtenção das datas (Regex)

            # Returns
                data_exp               - Required : Data de expedição (String)
                data_nasc              - Required : Data de nascimento (String)

        """

        # INICIANDO AS VARIÁVEIS
        data_exp = ""
        data_nasc = ""

        # REALIZANDO A LIMPEZA DO TEXTO, RETIRANDO BLACKLIST
        text = remove_line_with_black_list_words(text, settings.WORDS_BLACK_LIST_DATA)

        try:
            # OBTENDO DATAS
            datas = self.orchestra_extract_infos.get_matchs_strings(text, pattern_data)

            if len(datas):

                # FORMATANDO AS DATAS PARA FORMATO DATE
                datas_format_date = [convert_to_date(str(date_value[-1]).upper(),
                                                     settings.DICT_MONTHS,
                                                     settings.REGEX_ONLY_LETTERS) for date_value in datas]

                # ORDENANDO AS DATAS
                datas_format_date_order = sorted(datas_format_date)

                # OBTENDO OS VALORES DE DATA DE EXPEDIÇÃO DE DATA DE NASCIMENTO
                if len(datas) == 1:

                    data_exp = datas[0][-1]
                    data_nasc = datas[0][-1]

                elif len(datas) > 1:

                    data_exp = datas[0][-1]
                    data_nasc = datas[1][-1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return data_exp, data_nasc