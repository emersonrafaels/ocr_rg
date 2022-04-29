from inspect import stack
import re

from dynaconf import settings

from CONFIG import config
from UTILS.extract_infos import Extract_Infos
from UTILS.generic_functions import read_txt, applied_filter_not_intesection_list, order_list_with_arguments
from UTILS.generic_functions import verify_find_intersection, remove_line_with_black_list_words
from PROCESS_FIELDS.process_confidence_percentage import get_confidence_percentage, get_average


class Execute_Process_Names():

    def __init__(self):

        # 1 - REALIZANDO A LEITURA DO BANCO DE DADOS DE NOMES - GENEROS
        self.data_first_names_gender = self.__get_data_names(config.DIR_DATA_FIRST_NAMES_GENDER,
                                                             value_split=",",
                                                             encoding='cp1252')

        # 2 - REALIZANDO A LEITURA DO BANCO DE DADOS DE SOBRENOMES
        self.data_last_names = self.__get_data_names(config.DIR_DATA_LAST_NAMES,
                                                     value_split="-",
                                                     encoding='utf8')

        # 3 - INICIANDO OS PERCENTUAIS DE MATCH DEFAULT
        self.default_percent_match = settings.DEFAULT_PERCENTUAL_MATCH_NAME

        # 4 - DEFININDO SE DEVE HAVER PRÉ PROCESSAMENTO DOS ITENS ANTES DO CÁLCULO DE SEMELHANÇA
        self.similarity_pre_processing = settings.DEFAULT_PRE_PROCESSING

        # 5 - INICIANDO A VARIÁVEL QUE CONTÉM O LIMIT NA CHAMADA DE MÁXIMAS SIMILARIDADES
        self.limit_result_best_similar = settings.DEFAULT_LIMIT_RESULT_BEST_SIMILAR

        # 6 - INICIANDO A VARIÁVEL QUE ARMAZENA
        # SE O PERCENTUAL DE CONFIANÇA DEVE SER CALCULADO COM MÉDIA PONDERADA
        self.confidence_weighted = settings.CONFIDENCE_WEIGHTED


    def create_text(self, x, y, z):

        x = x.split("\n")
        y = y.split("\n")
        z = z.split("\n")

        list_names = list(dict.fromkeys(x + y + z))

        text = "\n".join(list_names)

        return text


    def concatenate_names(self, info):

        text = Execute_Process_Names.create_text(self,
                                                 info["NOME"],
                                                 info["NOME_PAI"],
                                                 self["NOME_MAE"])

        # OBTENDO NOME, NOME DO PAI E NOME DA MÃE
        # UTILIZANDO O PROCESSO DE OBTENÇÃO DE NOME ATRAVÉS
        # DA ORQUESTRAÇÃO DE REGRAS PARA OBTENÇÃO DE NOMES
        nome, nome_pai, nome_mae = Execute_Process_Names.get_names(self, text=text)

        info["NOME"], info["NOME_PAI"], info["NOME_MAE"]= nome, nome_pai, nome_mae


    def get_confidence_names(self, name,
                             info_ocr=config.INFO_OCR_DEFAULT,
                             pattern=settings.REGEX_ONLY_LETTERS):

        """

            RETORNA O PERCENTUAL DE CONFIANÇA DA LEITURA DO NOME.

            A FUNÇÃO É UTILIZADA PARA CADA UM DOS NOMES OBTIDOS:
                1) NOME
                2) NOME_PAI
                3) NOME_MAE

            # Arguments
                name                 - Required : Nome para obter o percentual de confiança (String)
                info_ocr             - Required : Informações da leitura do OCR (DataFrame)
                pattern              - Required : Padrão de leitura regeX e pós processamentos (String)

            # Returns
                output               - Required : Lista contendo o nome e o
                                                  percentual de confiança da leitura (List)

        """

        # INICIANDO AS VARIÁVEIS AUXILIARES
        name_index = 0
        name_percentage_default = [name, 0]

        # CRIA UMA CÓPIA DO DATAFRAME DE INFORMAÇÕES DE LEITURA DO OCR
        info_ocr_copy = info_ocr.copy()

        # APLICA O PÓS PROCESSAMENTO NA COLUNA DO TEXTO
        info_ocr_copy["text"] = [re.sub(pattern=pattern,
                                        string=value_z,
                                        repl=" ").replace("  ", " ").strip() for value_z in info_ocr.text.fillna('')]
        
        # VERIFICA SE O NOME NÃO É VÁZIO
        if len(name.split()) > 0:

            try:
                # BUSCA O ÍNDICE DO PRIMEIRO NOME NO DATAFRAME
                name_index = info_ocr_copy.text.to_list().index(name.split()[0])

            except Exception as ex:
                print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

            # CRIA UMA LISTA CONTENDO CADA UM DOS NOMES COM SEU PERCENTUAL DE CONFIANÇA
            confidence = get_confidence_percentage(name.split(),
                                                   info_ocr_copy.iloc[name_index:,])

            # RETORNA UMA LISTA COM O NOME E O PERCENTUAL MÉDIO DE CONFIANÇA
            return [name, get_average(confidence,
                                      weighted=self.confidence_weighted)]

        else:
            return name_percentage_default


    def __get_data_names(self, dir_data, value_split, encoding):

        """

            1) REALIZA A LEITURA DO BANCO DE DADOS DE NOMES
            2) REALIZA A FORMAAÇÃO DA LISTA, DE ACORDO COM UM VALOR DE SPLIT DEFINIDO

            # Arguments
                dir_data              - Required : Diretório da base a ser lida (String)
                value_split           - Required : Caracter utilizada para split da lista (String)
                encoding              - Optional : Encoding utilizado (String)

            # Returns
                list_result          - Required : Lista resultado (List)

        """

        # INICIANDO A VARIÁVEL RESULTANTE
        list_result = []

        try:
            # REALIZANDO A LEITURA DO TXT CONTENDO OS DADOS
            validador, data = read_txt(dir_data, encoding)

            if validador:

                # REALIZANDO A CONVERSÃO
                list_result = [name_sex.split(value_split) for name_sex in data.split("\n") if "NOME" not in name_sex]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO A TUPLA CONTENDO O RESULTADO FINAL APÓS LEITURA E FORMATAÇÃO
        return list_result


    def get_first_name_valid(self, name_input, list_first_names=None):

        """

            1) RECEBE UMA STRING CONTENDO UM NOME COMPLTO
            2) RECEBE UMA LISTA DE NOMES
            3) VALIDA SE DENTRO OS VALORES DA STRING,
            HÁ ALGUM VÁLIDO COMO PRIMEIRO NOME.

            # Arguments
                name_input         - Required : Nome completo a ser analisado (String)
                list_first_names   - Optional : Lista de primeiros nomes e generos (List)

            # Returns
                first_name         - Required : Primeiro nome válido (String)
                gender             - Required : Gênero do nome validado (Char)

        """

        # INICIANDO AS VARIÁVEIS DE RETORNO
        result_similarity = result_similarity_default = (False, [('', 0)])
        first_name = ""
        gender = ""

        # VERIFICANDO A VARIÁVEL DE PRIMEIROS NOMES
        if list_first_names is None:
            list_first_names = self.data_first_names_gender

        for value_x in name_input.split(" "):

            if value_x != "" and len(value_x) >= 2:

                result_similarity = Extract_Infos.get_similitary(self,
                                                                 str(value_x).upper(),
                                                                 [str(value[0]).upper() for value in list_first_names],
                                                                 self.default_percent_match,
                                                                 self.similarity_pre_processing,
                                                                 self.limit_result_best_similar)

                if result_similarity[0]:

                    # VERIFICANDO SE O MATCH OCORREU PARA LEN(NOME) < 4, COM VALOR DE 100
                    # CASO NÃO TENHA SIDO, EXCLUI A OPÇÃO
                    if result_similarity[-1][0][-1] < 100 and len(value_x) <= 3:
                        # CASO RECUSADO, CONTINUA BUSCANDO UM NOME VÁLIDO
                        result_similarity = result_similarity_default
                        continue
                    else:
                        #print(result_similarity[-1])

                        # ARMAZENANDO O NOME SALVO
                        first_name = value_x

                        try:
                            # OBTENDO O GÊNERO
                            gender = [value[1].upper() for value in list_first_names if
                                      value[0].upper() == result_similarity[-1][0][0].upper()][0]
                        except Exception as ex:
                            # OBTENDO O GÊNERO
                            gender = [value[1].upper() for value in self.data_first_names_gender if
                                      value[0].upper() == result_similarity[-1][0][0][0].upper()][0]

                        return result_similarity, first_name, gender

        return result_similarity, first_name, gender


    def last_name_valid(self, complete_name_input, first_name_input, list_last_names=None):

        """

            1) RECEBE UMA STRING CONTENDO UM NOME COMPLTO
            2) RECEBE UMA LISTA DE SOBRENOMES
            3) VALIDA CADA UM DOS VALORES DO NOME,
            SE ESSE VALOR É UM SOBRENOME

            # Arguments
                complete_name_input  - Required : Nome completo a ser analisado (String)
                first_name_input     - Required : Primeiro nome validado (String)
                list_last_names      - Optional : Lista de sobrenomes (List)

            # Returns
                last_name          - Required : Sobrenomes válidos (String)
                gender             - Required : Gênero do nome validado (Char)

        """

        # INICIANDO A VARIÁVEL QUE OS SOBRENOMES VÁLIDOS
        last_name = ""

        # VERIFICANDO A  VARIÁVEL DE PRIMEIROS NOMES
        if list_last_names is None:
            list_last_names = self.data_last_names

        for value_x in complete_name_input.split(" "):

            # VALIDANDO SE É O PRIMEIRO NOME (ESSE NÃO SERÁ ANALISADO)
            if value_x != first_name_input and value_x not in ["DO", "DA", "DE",
                                                               "DI", "DOS", "DAS"]:

                # VALIDANDO SE É O PRIMEIRO NOME (ESSE NÃO SERÁ ANALISADO)
                if value_x != "" and len(value_x) >= 3:

                    result_similarity = Extract_Infos.get_similitary(self,
                                                                     value_x,
                                                                     [value[0] for value in list_last_names],
                                                                     self.default_percent_match,
                                                                     self.similarity_pre_processing,
                                                                     self.limit_result_best_similar)

                    if result_similarity[0]:
                        # print(value_x, result_similarity[-1])

                        # ARMAZENANDO O NOME SALVO
                        last_name += value_x + " "

            else:
                # ARMAZENANDO O NOME SALVO
                last_name += value_x + " "

        return last_name.strip()


    def orchestra_postprocess_names(self, info_extracted,
                                    filters_validate=[],
                                    pattern_only_letters=settings.REGEX_ONLY_LETTERS):

        """

            APLICA TÉCNICAS DE PÓS PROCESSAMENTO:

                1) RETIRA VALORES QUE NÃO SÃO NOME E/OU SOBRENOMES.

            # Arguments
                info_extracted       - Required : Textos a serem analisado (Dict)
                filters_validate     - Optional : Filtros e validações
                                                 a serem aplicadas (List)

                regex_only_letters   - Optional : Pattern a ser utilizado (Regex)

            # Returns
                output               - Required : Valor após processamento (String)

        """

        # INICIANDO O VALIDADOR DE FIM DA FUNÇÃO
        validador = False

        result_names = []

        dict_names = ["NOME", "NOME_MAE", "NOME_PAI"]

        for field in dict_names:

            validador = False

            # FILTRANDO O VALOR DO CAMPO ATUAL
            value_x = info_extracted[field]

            # MANTENDO APENAS LETRAS
            result_split = re.sub(pattern=pattern_only_letters,
                                  string=value_x,
                                  repl=" ").replace("  ", " ").strip()

            if not validador:

                # PERCORRENDO CADA PALAVRA CONTIDA NO TEXTO (SEPARANDO POR ESPAÇO)
                for value_y in result_split.split(" "):

                    # A STRING DEVE SER != "" E NÃO SER RESULTADO DE UM CAMPO ANTERIOR
                    if value_y != "" and not applied_filter_not_intesection_list(
                            [value_split for value_split in value_y.split(" ") if value_split != ""],
                            filters_validate + settings.WORDS_BLACK_LIST_NAMES_FIND,
                            mode="FIND", min_len=3):

                        # print("NOME: TESTANDO: {}".format(value_y))

                        # VALIDANDO SE É UM NOME VÁLIDO
                        result_valid_name = Execute_Process_Names.get_first_name_valid(self, value_y,
                                                                                       self.data_first_names_gender)

                        if result_valid_name[0][0]:
                            result_names.append([value_y, result_valid_name[0][1][0][-1], result_valid_name[2]])

                            if result_valid_name[0][-1][0][-1] == 100:
                                info_extracted[field] = value_x[value_x.find(result_valid_name[-2]):]
                                validador = True
                                break

            else:
                break

            if not validador:

                # ORDENANDO A LISTA E OBTENDO OS 3 VALORES DE MAIOR PERCENTUAL
                result_order_names = order_list_with_arguments(list_values=result_names,
                                                               number_column_order=1,
                                                               limit=1)

                if len(result_order_names):
                    info_extracted[field] = value_x[value_x.find(result_order_names[0][0]):]

                else:
                    info_extracted[field] = ""

        # CONCATENANDO NOMES
        info_extracted = Execute_Process_Names.concatenate_names(self, info_extracted)

        return info_extracted


    def find_nome_filiacao(self, text, pattern_find,
                           pattern_only_letters=settings.REGEX_ONLY_LETTERS,
                           limit=1):

        """

            VERIFICA SE NOME OU FILIAÇÃO (pattern_find)
            ESTÃO CONTIDOS NO TEXTO, CASO ESTEJAM
            OBTÉM UM NÚMERO SEGUINTE DE LINHAS (limit)

            # Arguments
                text                 - Required : Texto a ser analisado (String)
                filters_validate     - Optional : Filtros e validações
                                                  a serem aplicadas (List)
                pattern_only_letters - Optional : Pattern a ser utilizado (Regex)
                limit                - Optional : Número de linhas
                                                  seguintes desejadas (Integer)

            # Returns
                result               - Required : Nomes obtidos (List)

        """

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validador_verify_find_intersection = False

        # INICIANDO A VARIÁVEL AUXILIAR DE RESULTADO DE NOMES APÓS A VALIDAÇÃO
        result_names = []

        # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO FINAL
        result = ""

        # INICIANDO A VARIÁVEL DE RETORNO
        result_final = []

        try:
            # CRIAÇÃO DA LISTA AUXILIAR
            # A LISTA AUXILIAR RECEBERÁ APENAS VALORES NÃO VÁZIOS E COM TAMANHO MAIOR QUE 1
            list_aux = [value.strip() for value in text.split("\n") if
                        (value != "" and len(value.split(" ")) > 1) or verify_find_intersection(value, pattern_find)]

            # VERIFICANDO SE O PATTERN ESTÁ EM ALGUMA POSIÇÃO DO TEXTO
            validador_verify_find_intersection = [value for value in pattern_find if
                                                  verify_find_intersection(value, list_aux)]

            if validador_verify_find_intersection:

                # OBTENDO O VALOR DE INTERSECÇÃO (USANDO O PRIMEIRO VALOR VALIDADO)
                pattern_find = [value for value in list_aux if value.find(validador_verify_find_intersection[0]) != -1][
                    0]

                result = list(map(list_aux.__getitem__, range(list_aux.index(pattern_find) + 1,
                                                              list_aux.index(pattern_find) + 1 + limit,
                                                              1)))

                for value in result:

                    # REINICIANDO A VARIÁVEL DE RESULTNAMES
                    result_names = []

                    for value_y in value.split(" "):

                        # VALIDANDO SE É UM NOME VÁLIDO
                        result_valid_name = Execute_Process_Names.get_first_name_valid(self,
                                                                                       value_y)

                        if result_valid_name[0][0]:
                            result_names.append([value_y, result_valid_name[0][1][0][-1], result_valid_name[2]])

                            if result_valid_name[0][-1][0][-1] == 100:
                                break

                # ORDENANDO A LISTA E OBTENDO OS 3 VALORES DE MAIOR PERCENTUAL
                result_names = order_list_with_arguments(list_values=result_names,
                                                         number_column_order=1,
                                                         limit=1)

                # ATUALIZANDO O NOME FINAL
                result_names_slicing = value[value.find(result_names[0][0]):].split("\n")[0]

                # MANTENDO APENAS LETRAS
                result = re.sub(pattern=pattern_only_letters,
                                string=result_names_slicing,
                                repl=" ").replace("  ", " ").strip()

                result_final.append(result)

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return result_final


    def get_names(self, text, filters_validate=[],
                  pattern=settings.REGEX_ONLY_LETTERS):

        """

            ORQUESTRA A OBTENÇÃO DOS CAMPOS DE NOME.

            OS CAMPOS OBTIDOS SAO:
                1) NOME COMPLETO
                2) NOME DO PAI
                3) NOME DA MÃE

            RECEBE A OPÇÃO DE RETIRAR DA LISTA RESULTANTE
            VALORES DE UMA LISTA AUXILIAR ('list_validate')

            # Arguments
                text                 - Required : Texto a ser analisado (String)
                filters_validate     - Optional : Filtros e validações
                                                  a serem aplicadas (List)
                pattern              - Optional : Pattern a ser utilizado (Regex)


            # Returns
                result_names         - Required : Nomes obtidos (List)

        """

        # INICIANDO AS VARIÁVEIS
        nome = ""
        nome_pai = ""
        nome_mae = ""

        # INICIANDO O VALIDADOR DE FIM DA FUNÇÃO
        validador = False

        result_names = []

        # REALIZANDO A LIMPEZA DO TEXTO, RETIRANDO BLACKLIST
        text = remove_line_with_black_list_words(text, settings.WORDS_BLACK_LIST_NAMES_FIND)
        text = remove_line_with_black_list_words(text, settings.WORDS_BLACK_LIST_NAMES_EQUAL)

        try:

            for value_x in text.split("\n"):

                if not validador:

                    for value_y in value_x.split(" "):

                        # MANTENDO APENAS LETRAS
                        result_regex = re.sub(pattern=pattern,
                                              string=value_y,
                                              repl=" ").replace("  ", " ").strip()

                        # A STRING DEVE SER != "" E NÃO SER RESULTADO DE UM CAMPO ANTERIOR
                        if result_regex != "" and not applied_filter_not_intesection_list(
                                [value_split for value_split in result_regex.split(" ") if value_split != ""],
                                filters_validate + settings.WORDS_BLACK_LIST_NAMES_FIND,
                                mode="FIND", min_len=3):

                            # print("NOME: TESTANDO: {}".format(value_y))

                            # VALIDANDO SE É UM NOME VÁLIDO
                            result_valid_name = Execute_Process_Names.get_first_name_valid(self,
                                                                                           result_regex)

                            if result_valid_name[0][0]:
                                # NOME ORIGINAL, PERCENTUAL DE MATCH, SEXO
                                result_names.append([result_regex,
                                                     result_valid_name[0][1][0][-1],
                                                     result_valid_name[2]])

                                if result_valid_name[0][-1][0][-1] == 100:
                                    break

                                # VERIFICANDO SE JÁ HÁ 3 VALORES COM 100% DE SIMILARIDADE
                                if len(list(filter(lambda x: x == 100, [value[1] for value in result_names]))) >= 3:
                                    validador = True
                                    break

                else:
                    break

            # ORDENANDO A LISTA E OBTENDO OS 3 VALORES DE MAIOR PERCENTUAL
            result_names = order_list_with_arguments(list_values=result_names,
                                                     number_column_order=1,
                                                     limit=3)

            # OBTENDO OS VALORES DE NOME, NOME MÃE E NOME PAI
            if len(result_names) == 1:

                nome = text[text.find(result_names[0][0]):].split("\n")[0]

                # VERIFICANDO O GÊNERO
                if result_names[0][-1] == "M":

                    nome_pai = \
                        text[text.find(result_names[0][0]):].split("\n")[0].split(" E ")[0]
                    nome_mae = ""

                else:

                    nome_pai = ""
                    nome_mae = text[text.find(result_names[0][0]):].split("\n")[0]

            elif len(result_names) == 2:

                nome = text[text.find(result_names[0][0]):].split("\n")[0]

                text_ = " ".join([value for value in text.split("\n") if value !=
                                  [value_text for value_text in text.split("\n") if value_text.find(nome)!=-1][0]])

                # VERIFICANDO O GÊNERO
                if result_names[1][-1] == "M":

                    nome_pai = \
                        text_[text_.find(result_names[1][0]):].split("\n")[0].split(" E ")[0]
                    nome_mae = ""

                else:

                    nome_pai = ""
                    nome_mae = text_[text.find(result_names[1][0]):].split("\n")[0]

            elif len(result_names) > 2:

                nome = text[text.find(result_names[0][0]):].split("\n")[0]

                text_ = "\n".join([value for value in text.split("\n") if value !=
                                  [value_text for value_text in text.split("\n") if value_text.find(nome) != -1][0]])

                # VERIFICANDO O GÊNERO
                if result_names[1][-1] == "M":

                    nome_pai = \
                        text_[text_.find(result_names[1][0]):].split("\n")[0].split(" E ")[0]
                    nome_mae = text_[text_.find(result_names[2][0]):].split("\n")[0]

                else:

                    nome_pai = \
                        text_[text_.find(result_names[2][0]):].split("\n")[0].split(" E ")[0]
                    nome_mae = text_[text_.find(result_names[1][0]):].split("\n")[0]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # VALIDANDO SOBRENOMES
        dict_names = {}
        dict_names["NOME"] = nome
        dict_names["NOME_PAI"] = nome_pai
        dict_names["NOME_MAE"] = nome_mae

        for value_name in dict_names:

            # NOME - VALIDANDO O SOBRENOME - VERIFICANDO SE HÁ UM SOBRENOME UNITÁRIO
            dict_names[value_name] = Execute_Process_Names.find_last_name_text_unit(self,
                                                                                    nome=dict_names[value_name],
                                                                                    text=text,
                                                                                    list_last_names=None)

            if len(dict_names[value_name].split()) >= 1:

                # NOME - VALIDANDO O SOBRENOME - ANALISANDO SE OS SOBRENOMES SÃO VÁLIDOS
                dict_names[value_name] = Execute_Process_Names.last_name_valid(self,
                                                                               complete_name_input=dict_names[value_name],
                                                                               first_name_input=dict_names[value_name].split()[0],
                                                                               list_last_names=None)

        return dict_names["NOME"], dict_names["NOME_PAI"], dict_names["NOME_MAE"]


    def find_last_name_text_unit(self, nome, text, list_last_names=[],
                                 pattern_only_letters=settings.REGEX_ONLY_LETTERS):

        """

            VERIFICA SE O TEXTO SEGUINTE AO NOME REGISTRADO
            PODE SER UMA CONTINUAÇÃO DO SOBRENOME

            # Arguments
                nome                  - Required : Nome a ser analisado (String)
                text                  - Required : Texto completo obtido no OCR (String)
                list_last_names       - Optional : Lista com valores de sobrenome (List)
                pattern_only_letters  - Optional : Pattern a ser utilizado (Regex)

            # Returns
                nome                  - Required : Nome final (String)

        """

        # VERIFICANDO A VARIÁVEL DE PRIMEIROS NOMES
        if list_last_names is None:
            list_last_names = self.data_last_names

        # MANTENDO APENAS LETRAS NO TEXTO DO OCR
        text_wo_spaces = [re.sub(pattern=pattern_only_letters,
                                 string=text_split,
                                 repl=" ").replace("  ", " ").strip() for text_split in text.split("\n") if text_split != ""]

        # MANTENDO APENAS LETRAS NO NOME OBTIDO
        nome = re.sub(pattern=pattern_only_letters,
                      string=nome,
                      repl=" ").replace("  ", " ").strip()

        # OBTENDO O INDICE EM QUE O NOME APARECE
        try:
            if nome in text_wo_spaces:
                ind = text_wo_spaces.index(nome)
            else:
                return nome
        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            return nome

        if (ind + 1) < len(text_wo_spaces):
            ind += 1 # NOME CONSEGUINTE SERÁ O DE INTERESSE
            surname_candidate = text_wo_spaces[ind]

            # VERIFICANDO SE O NOME CANDIDATO É COMPOSTO APENAS POR UMA PALAVRA
            if len(surname_candidate.split()) == 1:
                result_similarity = Extract_Infos.get_similitary(self,
                                                                 surname_candidate,
                                                                 [value[0] for value in list_last_names],
                                                                 self.default_percent_match,
                                                                 self.similarity_pre_processing,
                                                                 self.limit_result_best_similar)

                if result_similarity[0]:
                    nome = nome + " " + surname_candidate

        return nome


    @staticmethod
    def choice_final_names(result_nome_alternativa_um,
                           result_filiacao_alternativa_um,
                           result_nome_alternativa_dois,
                           result_filiacao_alternativa_dois):

        """

           OSQUESTRA A DEFINIÇÃO DOS NOMES:

           1) NOME
           2) NOME DO PAI
           3) NOME DA MÃE

           A PARTIR DOS NOMES OBTIDOS ATRAVÉS DAS DUAS ALTERNATIVAS

           1) ALTERNATIVA 1 - PROCURANDO TERMOS COMO NOME/FILIAÇÃO
           2) ALTERNATIVA 2 - PERCORRENDO O TEXTO INTEIRO

            # Arguments
                result_nome_alternativa_um          - Required : Nome obtido na
                                                                 alternativa de execução um (String)
                result_filiacao_alternativa_um      - Required : Filiação obtida na
                                                                 alternativa de execução um (String)
                result_nome_alternativa_dois        - Required : Nome obtido na
                                                                 alternativa de execução dois (String)
                result_filiacao_alternativa_dois    - Required : Filiação obtida na
                                                                 alternativa de execução dois (String)

            # Returns
                nome                                - Required : Nome obtido (String)
                nome_pai                            - Required : Nome do pai obtido (String)
                nome_mae                            - Required : Nome da mãe obtido (String)

        """

        # INICIANDO AS VARIÁVEIS
        nome = ""
        nome_pai = ""
        nome_mae = ""

        try:
            print("ALTERNATIVA 1: NOME {} | FILIAÇÃO: {}".format(result_nome_alternativa_um,
                                                                 result_filiacao_alternativa_um))
            print("ALTERNATIVA 2: NOME {} | FILIAÇÃO: {}".format(result_nome_alternativa_dois,
                                                                 result_filiacao_alternativa_dois))

            # DEFININDO O NOME
            if len(result_nome_alternativa_um) > 0:
                nome = result_nome_alternativa_um[0]
            else:
                nome = result_nome_alternativa_dois[0]

            # DEFININDO FILIAÇÃO
            if len(result_filiacao_alternativa_um) == 2:
                # NOME DO PAI - ALTERNATIVA 1
                # NOME DA MÃE - ALTERNATIVA 1
                nome_pai, nome_mae = result_filiacao_alternativa_um[0], result_filiacao_alternativa_um[1]

            if len(result_filiacao_alternativa_um) == 1:
                # NOME DO PAI - ALTERNATIVA 1
                # NOME DA MÃE - ALTERNATIVA 2
                nome_pai, nome_mae = result_filiacao_alternativa_um[0], result_filiacao_alternativa_dois[1]

            else:
                # NOME DO PAI - ALTERNATIVA 2
                # NOME DA MÃE - ALTERNATIVA 2
                nome_pai, nome_mae = result_filiacao_alternativa_dois[0], result_filiacao_alternativa_dois[1]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return nome, nome_pai, nome_mae


    def orchestra_get_names(self, text, filters_validate=[], info_ocr=None, pattern=None):

        """

           ORQUESTRA A OBTENÇÃO DOS CAMPOS DE NOMES:

           PARA ISSO UTILIZA DUAS ALTERNATIVAS DIFERENTES:

           1) ALTERNATIVA 1 - PROCURANDO TERMOS COMO NOME/FILIAÇÃO
           2) ALTERNATIVA 2 - PERCORRENDO O TEXTO INTEIRO

           AO FINAL, É UTILIZADA A FUNÇÃO 'choice_final_names'
           PARA DEFINIÇÃO DOS NOMES FINAIS:

           1) NOME
           2) NOME DO PAI
           3) NOME DA MÃE

            # Arguments
                text                       - Required : Texto a ser analisado (String)
                filters_validate           - Optional : Filtros e validações
                                                  a serem aplicadas (List)

            # Returns
                nome                       - Required : Nome obtido (String)
                nome_pai                   - Required : Nome do pai obtido (String)
                nome_mae                   - Required : Nome da mãe obtido (String)

        """

        # INICIANDO A LISTA AUXILIAR PARA ARMAZENAR OS VALORES E OS PERCENTUAIS DE CONFIANÇA
        list_names_percent_confidence = []

        # VERIFICANDO SE É POSSÍVEL ENCONTRAR AS PALAVRAS NOMES E FILIAÇÃO - ALTERNATIVA 1
        nome_alternativa_um = Execute_Process_Names.find_nome_filiacao(self, text,
                                                                       pattern_find=settings.WORDS_LIST_NAMES,
                                                                       pattern_only_letters=settings.REGEX_ONLY_LETTERS,
                                                                       limit=1)

        filiacao_alternativa_um = Execute_Process_Names.find_nome_filiacao(self, text,
                                                                           pattern_find=settings.WORDS_LIST_FILIACAO,
                                                                           pattern_only_letters=settings.REGEX_ONLY_LETTERS,
                                                                           limit=1)

        # OBTENDO OS NOMES - ALTERNATIVA 2
        nome_alternativa_dois, nome_pai_alternativa_dois, \
        nome_mae_alternativa_dois = Execute_Process_Names.get_names(self,
                                                                    text,
                                                                    filters_validate,
                                                                    settings.REGEX_ONLY_LETTERS)

        # ENVIANDO OS NOMES OBTIDOS PARA DEFINIÇÃO DOS NOMES A SEREM UTILIZADOS
        nome, nome_pai, nome_mae = Execute_Process_Names.choice_final_names(nome_alternativa_um,
                                                                            filiacao_alternativa_um,
                                                                            [nome_alternativa_dois],
                                                                            [nome_pai_alternativa_dois, nome_mae_alternativa_dois])

        # OBENDO OS PERCENTUAIS DE CONFIANÇA
        for name in [nome, nome_pai, nome_mae]:
            list_names_percent_confidence.append(Execute_Process_Names.get_confidence_names(self,
                                                                                            name,
                                                                                            info_ocr,
                                                                                            pattern))

        nome, nome_pai, nome_mae = list_names_percent_confidence

        return nome, nome_pai, nome_mae