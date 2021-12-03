from inspect import stack
import re

from dynaconf import settings

from CONFIG import config
from UTILS.conectores_db.main import conectores
from UTILS.check_similarity import Check_Similarity

class Extract_Infos():

    def __init__(self):

        # 1 - DEFININDO REGEX
        self.regex = self.__get_regex()

        # 2 - INICIANDO OS PERCENTUAIS DE MATCH DEFAULT
        self.default_percent_match = settings.DEFAULT_PERCENTUAL_MATCH

        # 3 - DEFININDO SE DEVE HAVER PRÉ PROCESSAMENTO DOS ITENS ANTES DO CÁLCULO DE SEMELHANÇA
        self.similarity_pre_processing = settings.DEFAULT_PRE_PROCESSING

        # 4 - INICIANDO A VARIÁVEL QUE CONTÉM O LIMIT NA CHAMADA DE MÁXIMAS SIMILARIDADES
        self.limit_result_best_similar = settings.DEFAULT_LIMIT_RESULT_BEST_SIMILAR


    def __get_regex(self):

        """

            OBTÉM TODOS OS REGEX DISPONÍVEIS NO BANCO DE DADOS

            # Arguments

            # Returns
                list_regex             - Required : Lista contendo os regex disponíveis (List)

        """

        # INICIANDO A VARIÁVEL RESULTANTE
        list_regex = []

        try:
            # DEFININDO OS PARÂMETROS DE CONEXÃO
            caminho_bd_bds = config.DIR_BD_OCR
            ssql_bds = settings.QUERY_REGEX
            params_bds = (None,)
            tipo_query_bds = settings.QUERY_TYPE_REGEX

            # EXECUTANDO A QUERY E OBTENDO O RESULTADO
            list_regex = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO A TUPLA CONTENDO (MUNICIPIO, UF, ESTADO)
        return list_regex


    def get_value_regex(self, current_regex):

        """

            OBTÉM O VALOR DE UMA REGEX (CURRENT_REGEX)
            DENTRE A LISTA DE REGEX DISPONÍVEIS

            # Arguments
                current_regex          - Required : Valor da regex buscada (String)

            # Returns
                value_regex            - Required : Valor da regex buscada (String)

        """

        # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O VALOR DA REGEX
        value_regex = ""

        try:
            # PROCURANDO O VALOR DE REGEX DENTRO A LISTA DE REGEX DISPONÍVEIS
            value_regex = [value for value in self.regex if value[0] == current_regex]

            if len(value_regex):
                value_regex = value_regex[0][-1]
            else:
                value_regex = settings[current_regex]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO A TUPLA CONTENDO O VALOR DO REGEX
        return value_regex


    def applied_validate_filter(self, match_analysis, filters_validate):

        """

            VERIFICA SE HÁ FILTROS/VALIDAÇÕES A SEREM APLICADOS NO MATCH DO CAMPO ATUAL.

            EXEMPLOS DE VALIDAÇÕES:

            VALIDAÇÃO DE CPF, VALIDAÇÃO DE CNPJ, VALIDAÇÃO DE IMEI.

            # Arguments
                match_analysis              - Required : Valor para ser
                                                         analisado (String)
                filters_validate            - Required : Filtros ativos para o
                                                         campo atual (List)


            # Returns
                result_filter_validate      - Required : Resultados após aplicação
                                                         dos filtros/validações (Boolean)

        """

        # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO DO FILTRO/VALIDAÇÃO
        result_filter_validate = []

        if False in result_filter_validate:
            return False

        return True


    def get_matchs_line(self, text, field_pattern, filters_validate=[]):

        """

            FUNÇÃO RESPONSÁVEL POR ORQUESTRAR OS MATCHS
            ANALISANDO LINHA A LINHA

            RECEBE O TEXTO ANALISADO: text
            RECEBE O PATTERN: field_pattern

            # Arguments
                text             - Required : Texto analisado (String)
                field_pattern    - Required : Pattern a ser utilizado (Regex)
                fields_validate  - Optional : Filtros e validações
                                              a serem aplicadas (List)

            # Returns
                matchs_text      - Required : Resultado do modelo
                                              com os matchs (List)

        """

        matchs_strings = []

        try:
            # SPLITANDO O TEXTO A CADA QUEBRA DE LINHA
            # COM ISSO, OBTEMOS LINHA POR LINHA
            for text_line in text.split("\n"):

                # REALIZANDO O MATCH
                for match in re.finditer(pattern=re.compile(field_pattern,
                                                            re.IGNORECASE),
                                         string=text_line):

                    # VERIFICANDO SE HÁ FILTROS A SEREM FEITOS
                    if Extract_Infos.applied_validate_filter(self, match[0], filters_validate):

                        # REALIZANDO O MATCH
                        matchs_strings.append([text_line, match.start(), match.end(), match[0]])

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return matchs_strings


    def get_matchs_strings(self, text, field_pattern, filters_validate=[]):

        """

            FUNÇÃO RESPONSÁVEL POR ORQUESTRAR OS MATCHS
            ANALISANDO O TEXTO POR COMPLETO.

            RECEBE O TEXTO ANALISADO: text
            RECEBE O PATTERN: field_pattern

            # Arguments
                text             - Required : Texto analisado (String)
                field_pattern    - Required : Pattern a ser utilizado (Regex)
                fields_validate  - Optional : Filtros e validações
                                              a serem aplicadas (List)

            # Returns
                matchs_text      - Required : Resultado do modelo
                                              com os matchs (List)

        """

        matchs_text = []

        try:
            # REALIZANDO O MATCH
            for match in re.finditer(pattern=re.compile(field_pattern,
                                                        re.IGNORECASE),
                                     string=text):

                # VERIFICANDO SE HÁ FILTROS A SEREM FEITOS
                if Extract_Infos.applied_validate_filter(self, match[0], filters_validate):

                    # REALIZANDO O MATCH
                    matchs_text.append([match.start(), match.end(), match[0]])

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return matchs_text


    def decorator_valid_similarity(func):

        """

            ORQUESTRA A CHAMADA DA FUNÇÃO DE CÁLCULO DE SIMILARIDADE ITEM A ITEM.

            # Arguments
                search                     - Required : Palavra a ser comparada
                                                        ou utilizada como base para obter
                                                        as similaridades
                                                        dentre as possibilidades (String)

                list_choices               - Required : Palavra ser comparada com a query ou a lista
                                                        de palavras a serem comparadas
                                                        com a query (String | List)

                percent_match              - Required : Somente serão retornados
                                                        os itens acima do
                                                        percentual de match (Integer)

                pre_processing             - Optional : Definindo se deve haver
                                                        pré processamento (Boolean)

                limit                      - Optional : Limite de resultados
                                                        de similaridade (Integer)

            # Returns
                percentual_similarity      - Required : Percentual de similaridade (String | List)

        """


        def valid_value_similarity(self, search, list_choices, percent_match, pre_processing, limit):

            # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO DE SIMILARIDADES
            # APÓS FILTRO POR PERCENTUAL DE MATCH ESPERADO
            result_valid_similarity = []
            validator_similarity = False

            # VALIDANDO O LIMITE ENVIADO
            if limit is False:
                limit = None

            try:
                # OBTENDO AS SIMILARIDADES ENTRE O ITEM PROCURADO E A LISTA DE ITENS
                result_similarity = Check_Similarity.get_values_similarity(query=search,
                                                                           choices=list_choices,
                                                                           pre_processing=pre_processing,
                                                                           limit=limit)

                # VALIDANDO OS ITENS QUE ESTÃO ACIMA DO PERCENTUAL DE SIMILARIDADE ENVIADO
                result_valid_similarity = [value for value in result_similarity if value[1] > percent_match]

                if len(result_valid_similarity) > 0:
                    validator_similarity = True

            except Exception as ex:
                print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

            return validator_similarity, result_valid_similarity

        return valid_value_similarity


    @decorator_valid_similarity
    def get_similitary(self):

        pass


    def get_min_dif_len_letters(text, list_values):

        # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ A VARIÁVEL COM A
        # MENOR QUANTIDADE DE DIFERENÇA DE QUANTIDADE ENTRE AS STRINGS
        min_dif_len_letters = 100
        result_max_similarity = []

        if len(list_values):

            for value in list_values:

                # CALCULANDO A DIFERENÇA DE QUANTIDADE DE LETRAS
                dif_len_string = abs(len(value[0]) - len(value[1][0]))

                if dif_len_string < min_dif_len_letters:

                    # ARMAZENANDO O RESULTADO
                    result_max_similarity = value[-1]

                    # ATUALIZANDO O VALOR DE MÍNIMA DIFERENÇA DE TAMANHO DA STRING
                    min_dif_len_letters = dif_len_string
        else:
            # RETORNA-SE O TEXTO CONTENDO O MAIOR NÚMERO DE CARACTERES
            result_max_similarity = [max(text.split(" "), key=len), 0]

        # RETORNANDO O VALOR DE MÁXIMA SIMILARIDADE
        return result_max_similarity


    def get_max_similarity(self, text, list_values_similitary):

        """

            RECEBE UMA STRING, SEPARA-SE OS VALORES POR " " E "-".

                1) SPLIT POR " " E "-"
                2) CADA UM DOS VALORES É ENVIADO PARA OBTER A MÁXIMA SIMILARIDADE
                3) RETORNA O VALOR DE MAIOR SIMILARIDADE

            # Arguments
                text                       - Required : Texto a ser processado (String)
                list_values_similitary     - Required : Lista de valores possíveis (List)

            # Returns
                result_max_similarity      - Required : Valor de máxima similaridade com o texto (String)

        """

        # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ O MAX MATCH DE SIMILARIDADE
        max_similarity = 0
        result_max_similarity = []

        # REALIZANDO A QUEBRA POR ESPAÇOS E - E PERCORRENDO CADA UM DOS VALORES
        for value_x in text.split(" "):

            for value_j in value_x.split("-"):

                if value_j != "":

                    # OBTENDO O VALOR DE MAIOR SIMILARIDADE
                    result_similarity = Extract_Infos.get_similitary(self,
                                                                     value_j,
                                                                     list_values_similitary,
                                                                     self.default_percent_match,
                                                                     self.similarity_pre_processing,
                                                                     self.limit_result_best_similar)

                    if result_similarity[0]:

                        # PERCORRENDO TODOS OS RESULTADOS DE RETORNO DE SIMILARIDADE
                        for result in result_similarity[-1]:

                            if result[-1] >= max_similarity:

                                # ARMAZENANDO O RESULTADO
                                result_max_similarity.append([value_j, result])

                                # ATUALIZANDO O VALOR DE MÁXIMA SIMILARIDADE
                                max_similarity = result[-1]

                                if max_similarity == 100:
                                    # RETORNANDO O VALOR DE MÁXIMA SIMILARIDADE
                                    return result

        # RETORNANDO O VALOR DE MÁXIMA SIMILARIDADE
        return Extract_Infos.get_min_dif_len_letters(text, result_max_similarity)
