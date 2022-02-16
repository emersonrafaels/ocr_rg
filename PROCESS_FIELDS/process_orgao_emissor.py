import re
from inspect import stack

from dynaconf import settings
import unidecode
import pandas as pd

from CONFIG import config
from UTILS.extract_infos import Extract_Infos
from model_pre_processing import Image_Pre_Processing
from UTILS.image_ocr import ocr_functions
from UTILS.image_read import read_image, read_image_gray
from UTILS.image_view import image_view_functions
from UTILS.image_convert_format import orchestra_read_image
from UTILS.deep_check_orientation.deep_check_orientation import check_orientation


class Execute_Orgao_Emissor():

    def __init__(self):

        # 1 - REALIZANDO A LEITURA DO BANCO DE DADOS DE NOMES - GENEROS
        self.data_orgao_emissor = self.__get_orgao_emissor(config.DIR_DATA_ORGAOS_EMISSOR)

        # 2 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()


    def __get_orgao_emissor(self, dir_data):

        """

            1) REALIZA A LEITURA DO BANCO DE DADOS DE ORGÃOS EMISSORES

            # Arguments
                dir_data              - Required : Diretório da base a ser lida (String)

            # Returns
                list_result          - Required : Lista resultado (List)

        """

        # INICIANDO A VARIÁVEL RESULTANTE
        data = pd.DataFrame()

        try:
            # REALIZANDO A LEITURA DO TXT CONTENDO OS DADOS
            validador, data = pd.read_excel(dir_data, engine='openpyxl')

            if len(data):

                if "NOME" in data.columns:
                    data["NOME"] = data["NOME"].apply(lambda x: unidecode.unidecode(str(x)))

        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

        # RETORNANDO O DATAFRAME CONTENDO O RESULTADO FINAL APÓS LEITURA E FORMATAÇÃO
        return data


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
                orgao_emissor         - Required : Orgão emissor válido (String)
                sigla                 - Required : Sigla do orgão emissor validado (String)

        """

        # INICIANDO AS VARIÁVEIS DE RETORNO
        result_similarity = result_similarity_default = (False, [('', 0)])
        orgao_emissor = ""
        sigla = ""

        # VERIFICANDO A VARIÁVEL DE PRIMEIROS NOMES
        if list_orgao_emissor is None:
            list_orgao_emissor = self.data_orgao_emissor

        for value_x in text_input.split(" "):

            if value_x != "" and len(value_x) >= 2:

                result_similarity = Extract_Infos.get_similitary(self,
                                                                 str(value_x).upper(),
                                                                 [str(value[0]).upper() for value in list_orgao_emissor],
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

                        # ARMAZENANDO O ORGÃO EMISSOR SALVO
                        orgao_emissor = value_x

                        try:
                            # OBTENDO A SIGLA
                            sigla = [value[1].upper() for value in list_orgao_emissor if
                                      value[0].upper() == result_similarity[-1][0][0].upper()][0]
                        except Exception as ex:
                            # OBTENDO O GÊNERO
                            sigla = [value[1].upper() for value in self.data_first_names_gender if
                                      value[0].upper() == result_similarity[-1][0][0][0].upper()][0]

                        return result_similarity, orgao_emissor, sigla

        return result_similarity, orgao_emissor, sigla