from inspect import stack

from dynaconf import settings
import unidecode
import pandas as pd

from CONFIG import config
from UTILS.extract_infos import Extract_Infos
from UTILS.image_view import image_view_functions
from UTILS.deep_check_orientation.deep_check_orientation import check_orientation
from UTILS.generic_functions import order_list_with_arguments


class Execute_Orgao_Emissor():

    def __init__(self):

        # 1 - REALIZANDO A LEITURA DO BANCO DE DADOS DE ORGÃOS EMISSORES
        self.data_orgao_emissor = self.__get_dataset_orgao_emissor(config.DIR_DATA_ORGAOS_EMISSOR)

        # 2 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()

        # 3 - INICIANDO OS PERCENTUAIS DE MATCH DEFAULT
        self.default_percent_match = settings.DEFAULT_PERCENTUAL_MATCH_ORGAO_EMISSOR

        # 4 - DEFININDO SE DEVE HAVER PRÉ PROCESSAMENTO DOS ITENS ANTES DO CÁLCULO DE SEMELHANÇA
        self.similarity_pre_processing = settings.DEFAULT_PRE_PROCESSING

        # 5 - INICIANDO A VARIÁVEL QUE CONTÉM O LIMIT NA CHAMADA DE MÁXIMAS SIMILARIDADES
        self.limit_result_best_similar = settings.DEFAULT_LIMIT_RESULT_BEST_SIMILAR


    def __get_dataset_orgao_emissor(self, dir_data):

        """

            1) REALIZA A LEITURA DO BANCO DE DADOS DE ORGÃOS EMISSORES

            # Arguments
                dir_data              - Required : Diretório da base a ser lida (String)

            # Returns
                list_result          - Required : Lista resultado (List)

        """

        # INICIANDO A VARIÁVEL RESULTANTE
        list_result = []

        try:
            # REALIZANDO A LEITURA DO TXT CONTENDO OS DADOS
            data = pd.read_excel(dir_data, engine='openpyxl')

            if len(data):

                if "NOME" in data.columns:
                    data["NOME"] = data["NOME"].apply(lambda x: unidecode.unidecode(str(x)))

                list_result = data.to_records().tolist()

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO A TUPLA CONTENDO O RESULTADO FINAL APÓS LEITURA E FORMATAÇÃO
        return list_result


    def rotate_image(image):

        """

            APLICA A ROTAÇÃO CORRETA NA IMAGEM.

            # Arguments
                image                - Required : Imagem a ser rotacionada corretamente (String)

            # Returns
                output               - Required : Valor após processamento (String)

        """

        # INICIANDO A VARIÁVEL RESULTADO
        image_rotate = []

        try:
            _, rotations_number, image_rotate_vert = check_orientation().orchesta_model(image)

            # A IMAGEM ESTÁ COM O ROSTO NO ÂNGULO CORRETO, ENTÃO DEVEMOS ROTACIONAR 90º
            # COM ESSA ROTAÇÃO, OBTEREMOS O TEXTO
            image_rotate = check_orientation.get_image_correct_orientation(image_rotate_vert, 3)

            # VISUALIZANDO A IMAGEM ROTACIONADA
            image_view_functions.view_image_with_coordinates(image_rotate,
                                                             window_name="IMAGEM ROTACIONADA")

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            image_rotate = image

        return image_rotate


    def get_orgao_emissor(self, text_input, list_orgao_emissor=None):

        """

            1) RECEBE UMA STRING CONTENDO UM TEXTO
            2) RECEBE UMA LISTA DE ORGÃOS EMISSORES
            3) VALIDA SE DENTRO OS VALORES DA STRING,
            HÁ ALGUM VÁLIDO COMO ORGÃO EMISSOR.

            # Arguments
                name_input            - Required : Texto a ser analisado (String)
                list_orgao_emissor    - Optional : Lista de orgãos emissores (List)

            # Returns
                result_orgao_emissor  - Required : Lista com os resultados de similaridade (List)
                orgao_emissor         - Required : Orgão emissor válido (String)

        """

        # INICIANDO AS VARIÁVEIS DE RETORNO
        result_similarity = result_similarity_default = (False, [('', 0)])
        result_orgao_emissor = []

        # VERIFICANDO A VARIÁVEL DE ORGÃOS EMISSORES
        if list_orgao_emissor is None:
            list_orgao_emissor = self.data_orgao_emissor

        for value_x in text_input.split("\n"):

            if value_x != "":

                result_similarity = Extract_Infos.get_similitary(self,
                                                                 str(value_x).upper(),
                                                                 [str(value[2]).upper() for value in list_orgao_emissor],
                                                                 self.default_percent_match,
                                                                 self.similarity_pre_processing,
                                                                 self.limit_result_best_similar)

                if result_similarity[0]:

                    # VERIFICANDO SE O MATCH OCORREU PARA LEN(NOME) < 4, COM VALOR DE 100
                    # CASO NÃO TENHA SIDO, EXCLUI A OPÇÃO

                    result_orgao_emissor.append([value_x, result_similarity[-1][0]])
                    
                    if result_similarity[-1][0][-1] < 100:
                        
                        # CASO RECUSADO, CONTINUA BUSCANDO UM NOME VÁLIDO
                        result_similarity = result_similarity_default
                        continue
                        
                    else:
                        #print(result_similarity[-1])

                        # ARMAZENANDO O ORGÃO EMISSOR SALVO
                        orgao_emissor = value_x

                        return result_orgao_emissor, orgao_emissor

        # ORDENANDO A LISTA PARA OBTER OS VALORES COM MAIOR
        # PERCENTUAL DE PROXIMIDADE COM UM ORGÃO EMISSOR VÁLID0
        result_similarity = order_list_with_arguments(list_values=result_orgao_emissor,
                                                      number_column_order=1,
                                                      limit=1)

        orgao_emissor = result_similarity[-1][1][0]

        return result_orgao_emissor, orgao_emissor


    def get_sigla(self, orgao_emissor, list_orgao_emissor=None):

        """

            1) RECEBE UM ORGÃO EMISSOR PROCURADO
            2) RECEBE UMA LISTA DE ORGÃOS EMISSORES
            3) OBTÉM A SIGLA DESSE ORGÃO EMISSOR

            # Arguments
                orgao_emissor         - Required : Orgão emissor a ser buscado (String)
                list_orgao_emissor    - Optional : Lista de orgãos emissores (List)

            # Returns
                sigla                 - Required : Sigla do orgão emissor buscado (String)

        """

        # INICIANDO A VARIÁVEL DE RETORNO
        sigla = ""

        try:
            # VERIFICANDO A VARIÁVEL DE ORGÃOS EMISSORES
            if list_orgao_emissor is None:
                list_orgao_emissor = self.data_orgao_emissor

            # OBTENDO A SIGLA
            sigla = [orgao[1] for orgao in list_orgao_emissor if orgao[2].upper() == orgao_emissor]

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        return sigla


    def orchestra_orgao_emissor_sigla(self, text_input):

        """

            FUNÇÃO RESPONSÁVEL POR ORQUESTRAR A OBTENÇÃO DO ORGÃO EMISSOR E SIGLA

            # Arguments
                text_input            - Required : Texto a ser analisado (String)

            # Returns
                result_orgao_emissor  - Required : Lista com os resultados de similaridade (List)
                orgao_emissor         - Required : Orgão emissor válido (String)
                sigla                 - Required : Sigla do orgão emissor buscado (String)

        """

        # INICIANDO AS VARIÁVEIS DE RETORNO
        result_similarity = None
        orgao_emissor = ""
        sigla = ""

        # OBTENDO O ORGÃO EMISSOR
        result_similarity, orgao_emissor = Execute_Orgao_Emissor.get_orgao_emissor(self, text_input)

        # OBTENDO A SIGLA
        sigla = Execute_Orgao_Emissor.get_sigla(self, orgao_emissor)

        # RETORNANDO TODOS OS VALORES
        return result_similarity, orgao_emissor, sigla