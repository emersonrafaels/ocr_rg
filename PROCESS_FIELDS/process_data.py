"""

    CLASSE PARA PROCESSAMENTO DOS CAMPOS DE FORMATO DATA.

    OS CAMPOS SÃO:
        1) DATA DE EXPEDIÇÃO
        2) DATA DE NASCIMENTO

    POSSUI FUNÇÕES PARA:
        1) OBTER DATAS CONTIDAS NO TEXTO

    # Arguments
        text                   - Required : Texto a ser analisado (String)
        pattern_data           - Required : Pattern a ser utilizado para
                                            obtenção das datas (Regex)
        info_ocr               - Optional : ImageData do OCR (DataFrame | Dict)

    # Returns
        data_exp               - Required : Data de expedição (String)
        data_nasc              - Required : Data de nascimento (String)

"""

__version__ = "1.0"
__author__ = "Emerson V. Rafael (EMERVIN)"
__data_atualizacao__ = "26/04/2022"


from inspect import stack

from dynaconf import settings

from CONFIG import config
from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import convert_to_date, remove_line_with_black_list_words, applied_filter_not_intesection_list
from PROCESS_FIELDS.process_confidence_percentage import get_confidence_percentage, get_average


class Execute_Process_Data():

    def __init__(self):

        # 1 - DEFININDO OS PATTERNS
        self.pattern_data = settings.REGEX_ONLY_DATES

        # 2 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()

        # 3 - DEFININDO CARACTERES NECESSÁRIOS EM DATES
        self.list_char_dates = settings.CHAR_DATES


    def get_result_datas(self, text, pattern_data, info_ocr=config.INFO_OCR_DEFAULT):

        """

            ORQUESTRA A OBTENÇÃO DAS DATAS DO DOCUMENTO:
                1) DATA DE EXPEDIÇÃO
                2) DATA DE NASCIMENTO

            # Arguments
                text                   - Required : Texto a ser analisado (String)
                pattern_data           - Required : Pattern a ser utilizado para
                                                    obtenção das datas (Regex)
                info_ocr               - Optional : ImageData do OCR (DataFrame | Dict)

            # Returns
                data_exp               - Required : Data de expedição (String)
                data_nasc              - Required : Data de nascimento (String)

        """

        # INICIANDO AS VARIÁVEIS
        data_exp = ["", 0]
        data_nasc = ["", 0]

        # REALIZANDO A LIMPEZA DO TEXTO, RETIRANDO BLACKLIST
        text = remove_line_with_black_list_words(text, settings.WORDS_BLACK_LIST_DATA)

        try:
            # OBTENDO DATAS
            datas = self.orchestra_extract_infos.get_matchs_strings(text, pattern_data)

            if len(datas):

                # MANTENDO APENAS VALORES COM '-', '/' OU '.'
                datas = [date_value[-1] for date_value in datas if applied_filter_not_intesection_list(self.list_char_dates,
                                                                                                       [date_value[-1]],
                                                                                                       mode="FIND",
                                                                                                       min_len=0)]

                # OBTENDO O PERCENTUAL DE CONFIANÇA DESSAS DATAS
                datas_confidence_percent = [[data, get_average(get_confidence_percentage(datas, info_ocr))] for data in datas]

                # FORMATANDO ESSAS DATAS PARA O FORMATO '/'
                datas_confidence_percent = [[str(date_value[0]).replace("-", "/").replace(".", "/"),
                                            date_value[1]] for date_value in datas_confidence_percent]

                # FORMATANDO AS DATAS PARA FORMATO DATE
                datas_format_date = [[convert_to_date(str(date_value[0]).upper(),
                                                     settings.DICT_MONTHS,
                                                     settings.REGEX_ONLY_LETTERS), date_value[1]]
                                     for date_value in datas_confidence_percent]

                # ORDENANDO AS DATAS
                # datas_format_date_order = sorted(datas_format_date)

                # OBTENDO OS VALORES DE DATA DE EXPEDIÇÃO DE DATA DE NASCIMENTO
                if len(datas) == 1:

                    data_exp = datas_confidence_percent[0]
                    data_nasc = datas_confidence_percent[0]

                elif len(datas) > 1:

                    data_exp = datas_confidence_percent[0]
                    data_nasc = datas_confidence_percent[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return data_exp, data_nasc