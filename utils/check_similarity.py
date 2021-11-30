"""

    MICROSERVIÇO PARA COMPARAÇÃO DE STRINGS USANDO
    A DISTÂNCIA DE LEVENSHTEIN: MÉTRICA PARA MEDIR A DISTÂNCIA
    ENTRE DUAS SEQUÊNCIAS DE PALAVRAS.

    EM OUTRAS PALAVRAS,
    MEDE-SE O NÚMERO MÍNIMO DE EDIÇÕES QUE VOCÊ PRECISA FAZER
    PARA ALTERAR UMA SEQUÊNCIA DE UMA PALAVRA NA OUTRA.

    ESSAS EDIÇÕES PODEM SER INSERÇÕES, EXCLUSÕES OU SUBSTITUIÇÕES.

    ESSE MICROSERVIÇO CONTÉM UMA SÉRIE DE FUNÇÕES
    PARA LIDAR COM A MEDIDA DE DISTÂNCIA:

    DISPONIBILIZANDO COMO OPÇÕES:

    1) PRÉ PROCESSAMENTO DAS STRINGS, ÚTIL PARA QUANDO ALGO TEM UMA VARIAÇÃO CONSIDERÁVEL DE GRAFIA
     EX: "EMERSON V. RAFAEL" COMPARADO COM "Emerson v. Rafael"

    2) EM UMA LISTA DE ESCOLHAS POSSÍVEIS (AQUI DEFINIDA COMO CHOICES),
    OBTER O VALOR DE MÁXIMA SIMILARIDADE
    A UMA DETERMINADA PALAVRA (AQUI DEFINIDA COMO QUERY)

    3) EM UMA LISTA DE ESCOLHAS POSSÍVEIS (AQUI DEFINIDA COMO CHOICES),
    OBTER TODOS OS PERCENTUAIS DE SIMILARIDADE.
    A UMA DETERMINADA PALAVRA (AQUI DEFINIDA COMO QUERY)

    # Arguments
        query                      - Required : Palavra a ser comparada
                                                ou utilizada como base para obter
                                                as similaridades
                                                dentre as possibilidades (String)

        choices                    - Required : Palavra ser comparada com a query ou a lista
                                                de palavras a serem comparadas
                                                com a query (Str | List)

        pre_processing             - Optional : Definindo se deve haver
                                                 pré processamento (Boolean)

    # Returns
        percentual_similarity      - Required : Percentual de similaridade (String | List)

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "06/10/2021"


from typing import Union
from pydantic import validate_arguments
from weighted_levenshtein import lev
from unidecode import unidecode


class Check_Similarity():

    def __init__(self):

        """

            MICROSERVIÇO PARA COMPARAÇÃO DE STRINGS USANDO
            A DISTÂNCIA DE LEVENSHTEIN: MÉTRICA PARA MEDIR A DISTÂNCIA
            ENTRE DUAS SEQUÊNCIAS DE PALAVRAS.

            EM OUTRAS PALAVRAS,
            MEDE-SE O NÚMERO MÍNIMO DE EDIÇÕES QUE VOCÊ PRECISA FAZER
            PARA ALTERAR UMA SEQUÊNCIA DE UMA PALAVRA NA OUTRA.

            ESSAS EDIÇÕES PODEM SER INSERÇÕES, EXCLUSÕES OU SUBSTITUIÇÕES.

            ESSE MICROSERVIÇO CONTÉM UMA SÉRIE DE FUNÇÕES
            PARA LIDAR COM A MEDIDA DE DISTÂNCIA:

            DISPONIBILIZANDO COMO OPÇÕES:

            1) PRÉ PROCESSAMENTO DAS STRINGS, ÚTIL PARA QUANDO ALGO TEM UMA VARIAÇÃO CONSIDERÁVEL DE GRAFIA
             EX: "EMERSON V. RAFAEL" COMPARADO COM "Emerson v. Rafael"

            2) EM UMA LISTA DE ESCOLHAS POSSÍVEIS (AQUI DEFINIDA COMO CHOICES),
            OBTER O VALOR DE MÁXIMA SIMILARIDADE
            A UMA DETERMINADA PALAVRA (AQUI DEFINIDA COMO QUERY)

            3) EM UMA LISTA DE ESCOLHAS POSSÍVEIS (AQUI DEFINIDA COMO CHOICES),
            OBTER TODOS OS PERCENTUAIS DE SIMILARIDADE.
            A UMA DETERMINADA PALAVRA (AQUI DEFINIDA COMO QUERY)

            # Arguments
                query                      - Required : Palavra a ser comparada
                                                        ou utilizada como base para obter
                                                        as similaridades
                                                        dentre as possibilidades (String)

                choices                    - Required : Palavra ser comparada com a query ou a lista
                                                        de palavras a serem comparadas
                                                        com a query (String | List)

                pre_processing             - Optional : Definindo se deve haver
                                                        pré processamento (Boolean)

                limit                      - Optional : Limite de resultados
                                                        de similaridade (Integer)

            # Returns
                percentual_similarity      - Required : Percentual de similaridade (String | List)

        """

        pass


    @staticmethod
    def pre_processing_string(value_to_processing):

        """

            REALIZA O PRÉ PROCESSAMENTO DAS STRINGS.

            PARA LISTAS ENVIADAS, UTILIZA LIST COMPREHESION
            PARA ATUALIZAR CADA UMA DAS STRINGS DA LISTA

            1) CONVERTE PARA LOWER CASE
            2) RETIRA ESPAÇOS EM BRANCO ANTES E DEPOIS DA STRING

            # Arguments
                value_to_processing         - Required : Valores para realizar
                                                         o pré processamento (String | List)

            # Returns
                value_processing             - Required : Valores após processamento (String | List)

        """

        if isinstance(value_to_processing, str):
            value_processing = value_to_processing.lower().strip()

            return value_processing

        elif isinstance(value_to_processing, list):
            value_processing = [str(value).lower().strip() for value in value_to_processing]

            return value_processing

        else:
            return value_to_processing


    @staticmethod
    def calculate_similitary(query: str, choices: Union[str, list],
                             pre_processing=False, limit=5):

        """

            OBTÉM OS VALORES DE SIMILARIDADE PARA TODOS OS ITENS DE CHOICES.

            1) COMPARA QUERY COM CADA ITEM DE CHOICES
            2) OBTÉM O VALOR DE SIMILARIDADE EM CADA COMPARAÇÃO
            3) RETORNA UMA LISTA DE TUPLAS CONTENDO ITEM E PERCENTUAL DE SIMILARIDADE.

            # Arguments
                query                      - Required : Palavra a ser comparada
                                                        ou utilizada como base para obter
                                                        as similaridades
                                                        dentre as possibilidades (String)

                choices                    - Required : Palavra ser comparada com a query ou a lista
                                                        de palavras a serem comparadas
                                                        com a query (String | List)

                pre_processing             - Optional : Definindo se deve haver
                                                        pré processamento (Boolean)

                limit                      - Optional : Limite de resultados
                                                        de similaridade (Integer)

            # Returns
                percentual_similarity      - Required : Percentual de similaridade (String | List)

        """

        # APLICANDO A DISTÂNCIA DE LEVENSHTEIN PARA CADA COMPAAÇÃO (QUERY - CHOICES)
        result_process_extract_similitary = [[value_choice,
                                              (1 - (lev(unidecode(query), unidecode(value_choice))/max(len(unidecode(query)),
                                                                                                       len(unidecode(value_choice)))))*100] for
                                              value_choice in choices]

        # ORDENANDO PELO PERCENTUAL DE SIMILARIDADE
        result_process_extract_similitary_order = sorted(result_process_extract_similitary, key=lambda row: (row[1]), reverse=True)

        # RETORNANDO DE ACORDO COM O LIMIT DESEJADO
        return result_process_extract_similitary_order[:limit]



    @staticmethod
    @validate_arguments
    def get_values_similarity(query: str, choices: Union[str, list],
                              pre_processing=False, limit=5):

        """

            OBTÉM OS VALORES DE SIMILARIDADE PARA TODOS OS ITENS DE CHOICES.

            1) COMPARA QUERY COM CADA ITEM DE CHOICES
            2) OBTÉM O VALOR DE SIMILARIDADE EM CADA COMPARAÇÃO
            3) RETORNA UMA LISTA DE TUPLAS CONTENDO ITEM E PERCENTUAL DE SIMILARIDADE.

            # Arguments
                query                      - Required : Palavra a ser comparada
                                                        ou utilizada como base para obter
                                                        as similaridades
                                                        dentre as possibilidades (String)

                choices                    - Required : Palavra ser comparada com a query ou a lista
                                                        de palavras a serem comparadas
                                                        com a query (String | List)

                pre_processing             - Optional : Definindo se deve haver
                                                        pré processamento (Boolean)

                limit                      - Optional : Limite de resultados
                                                        de similaridade (Integer)

            # Returns
                percentual_similarity      - Required : Percentual de similaridade (String | List)

        """

        # VERIFICANDO SE HÁ NECESSIDADE DE PRÉ PROCESSAMENTO
        if pre_processing:
            # REALIZANDO O PRÉ PROCESSAMENTO
            query = Check_Similarity.pre_processing_string(query)
            choices = Check_Similarity.pre_processing_string(choices)

        if isinstance(choices, str):
            choices = choices.split(",")

        # RETORNANDO A LISTA DE TUPLAS
        #(VALUE, PERCENTUAL_SIMILARIDADE)
        return Check_Similarity.calculate_similitary(query=query, choices=choices, limit=limit)


    @staticmethod
    def get_value_max_similarity(query: str, choices: Union[str, list],
                                 pre_processing=False, limit=5):

        """

            OBTÉM O ITEM QUE POSSUI MAIOR SIMILARIDADE À QUERY.

            1) COMPARA QUERY COM CADA ITEM DE CHOICES
            2) OBTÉM O VALOR DE SIMILARIDADE EM CADA COMPARAÇÃO
            3) SELECIONA A MAIOR SIMILARIDADE
            4) RETORNA UMA LISTA DE ÚNICO VALOR CONTENDO ITEM E
            PERCENTUAL DE MÁXIMA SIMILARIDADE.

            # Arguments
                query                      - Required : Palavra a ser comparada
                                                        ou utilizada como base para obter
                                                        as similaridades
                                                        dentre as possibilidades (String)

                choices                    - Required : Palavra ser comparada com a query ou a lista
                                                        de palavras a serem comparadas
                                                        com a query (String | List)

                pre_processing             - Optional : Definindo se deve haver
                                                        pré processamento (Boolean)

                limit                      - Optional : Limite de resultados
                                                        de similaridade (Integer)

            # Returns
                percentual_similarity      - Required : Percentual de similaridade (String | List)

        """

        # VERIFICANDO SE HÁ NECESSIDADE DE PRÉ PROCESSAMENTO
        if pre_processing:
            query = Check_Similarity.pre_processing_string(query)
            choices = Check_Similarity.pre_processing_string(choices)

        if isinstance(choices, str):
            choices = choices.split(",")

        # RETORNANDO A LISTA DE TUPLAS DE ÚNICO VALOR COM MÁXIMA SIMILARIDADE
        # (VALUE, PERCENTUAL_SIMILARIDADE)
        return Check_Similarity.calculate_similitary(query=query, choices=choices, limit=1)
