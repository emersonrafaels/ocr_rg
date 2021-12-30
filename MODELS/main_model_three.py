import re
from inspect import stack

from dynaconf import settings
import unidecode

from UTILS.extract_infos import Extract_Infos
from PROCESS_FIELDS.process_names import Execute_Process_Names
from PROCESS_FIELDS.process_location import Execute_Process_Location
from PROCESS_FIELDS.process_data import Execute_Process_Data
from PROCESS_FIELDS.process_rg_cpf import Execute_Process_RG_CPF
from model_pre_processing import Image_Pre_Processing
from UTILS.image_ocr import ocr_functions
from UTILS.image_read import read_image, read_image_gray
from UTILS.image_convert_format import orchestra_read_image
from UTILS.deep_check_orientation.deep_check_orientation import check_orientation


class model_three():

    def __init__(self, dir_image):

        # 1 - DEFININDO OS PATTERNS
        self.pattern_data = settings.REGEX_ONLY_DATES
        self.pattern_rg = settings.REGEX_RG
        self.pattern_cpf = settings.REGEX_CPF
        self.pattern_uf = settings.REGEX_UF

        # 2 - OBTENDO O LOCAL DA IMAGEM
        self.dir_image = dir_image
        
        # 3 - INSTANCIANDO AS OUTRAS CLASSES UTILIZADAS
        self.orchestra_extract_infos = Extract_Infos()
        self.orchestra_process_names = Execute_Process_Names()
        self.orchestra_process_location = Execute_Process_Location()


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
            _, rotations_number, image_rotate = check_orientation().orchesta_model(image)
        except Exception as ex:
            print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))
            image_rotate = image

        return image_rotate


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


    def orchestra_model(self):

        # APLICANDO O OCR NO DOCUMENTO INTEIRO - MODELO 3
        text = ocr_functions().Orquestra_OCR(self.dir_image)

        # INICIANDO AS VARIÁVEIS
        data_exp = ""
        data_nasc = ""
        list_result_rg = []
        list_result_cpf = []
        nome = ""
        nome_pai = ""
        nome_mae = ""
        cidade_nasc = ""
        estado_nasc = ""
        cidade_origem = ""
        estado_origem = ""

        #print(text)
        #print("-"*50)

        # OBTENDO AS DATAS
        data_exp, data_nasc = Execute_Process_Data().get_result_datas(text, self.pattern_data)

        # OBTENDO CPF
        list_result_cpf = Execute_Process_RG_CPF().get_values(text,
                                                              self.pattern_cpf,
                                                              limit_values=1)

        # OBTENDO RG (FILTRANDO VALORES QUE JÁ CONSTAM COMO CPF)
        list_result_rg = Execute_Process_RG_CPF().get_values(text,
                                                             self.pattern_rg,
                                                             filters_validate=list_result_cpf,
                                                             limit_values=1)

        # OBTENDO AS CIDADES-ESTADO
        cidade_nasc, estado_nasc, cidade_origem, estado_origem = Execute_Process_Location().get_result_location(text,
                                                                                                                self.pattern_uf)

        # RESULTADOS ATÉ ENTÃO
        results_ocr = [data_exp, data_nasc, cidade_nasc, estado_nasc, cidade_origem, estado_origem] + list_result_cpf + list_result_rg

        # OBTENDO OS NOMES
        nome, nome_pai, nome_mae = Execute_Process_Names().orchestra_get_names(text,
                                                                               results_ocr)

        # FORMATANDO O RESULTADO DOS CAMPOS NUMÉRICOS
        list_result_rg = [model_three.__postprocess_num(value_rg, settings.REGEX_ONLY_X_NUMBERS) for value_rg in list_result_rg]
        list_result_cpf = [model_three.__postprocess_num(value_cpf, settings.REGEX_ONLY_NUMBERS) for value_cpf in list_result_cpf]

        # FORMATANDO O RESULTADO DOS CAMPOS STRINGS
        nome = model_three.__postprocess_string(nome, settings.REGEX_ONLY_LETTERS)
        nome_pai = model_three.__postprocess_string(nome_pai, settings.REGEX_ONLY_LETTERS)
        nome_mae = model_three.__postprocess_string(nome_mae, settings.REGEX_ONLY_LETTERS)
        cidade_nasc = model_three.__postprocess_string(cidade_nasc, settings.REGEX_ONLY_LETTERS_DOT_DASH)
        estado_nasc = model_three.__postprocess_string(estado_nasc, settings.REGEX_ONLY_LETTERS)
        cidade_origem = model_three.__postprocess_string(cidade_origem, settings.REGEX_ONLY_LETTERS_DOT_DASH)
        estado_origem = model_three.__postprocess_string(estado_origem, settings.REGEX_ONLY_LETTERS)

        return text, data_exp, data_nasc, list_result_rg, list_result_cpf, \
               nome, nome_pai, nome_mae, \
               cidade_nasc, estado_nasc, cidade_origem, estado_origem



def main_model(dir_image):

    # INICIANDO A VARIÁVEL CONTENDO A LISTA DE IMAGENS A SER ENVIADA
    dict_images = {}

    # INICIANDO A VARIÁVEL QUE ARMAZENARÁ O RESULTADO DO MODELO
    result_model = []

    # REALIZANDO A LEITURA DA IMAGEM - RGB
    img_rgb = read_image(dir_image)

    if settings.ROTATE_IMAGE:
        # REALIZANDO A ROTAÇÃO DA IMAGEM
        # ATUALIZANDO A IMAGEM RGB COM A IMAGEM ROTACIONADA
        img_rgb = model_three.rotate_image(img_rgb)

    # REALIZANDO A LEITURA DA IMAGEM - ESCALA DE CINZA
    img_gray = read_image_gray(img_rgb)

    if settings.PRE_PROC_IMAGE:

        # DEFININDO A CLASSE DE PRÉ PROCESSAMENTO
        # UTILIZA-SE A IMAGEM RGB
        img_original, cropped_image, warped_img = Image_Pre_Processing(settings.BLUR_KSIZE,
                                                                       settings.THRESHOLD_MAX_COLOR_VALUE,
                                                                       settings.DILATION_KSIZE,
                                                                       settings.WIDTH_RESIZE,
                                                                       settings.OUTPUT_SIZE).orchestra_pre_processing(
            img_gray)

    # CONSTRUINDO A LISTA DE IMAGENS A SEREM ENVIADAS
    dict_images["IMAGEM_ORIGINAL_GRAY"] = img_gray
    dict_images["IMAGEM_ORIGINAL_RGB"] = img_rgb

    # VERIFICANDO SE É NECESSÁRIO ENVIAR A IMAGEM ROTACIONADA + IMAGEM ROTACIONADA EM 180
    if settings.DUPLO_CHECK_ROTATE:

        """
            ENVIA:
                1) IMAGEM EM ESCALA DE CINZA
                2) IMAGEM ESCALA DE CINZA ROTACIONADA EM 180º
                3) IMAGEM NA COR ORIGINAL
                4) IMAGEM NA COR ORIGINAL ROTACIONADA EM 180º
        """

        dict_images["IMAGEM_ORIGINAL_GRAY_DUPLO_CHECK"] = check_orientation.get_image_correct_orientation(img_gray, 2)
        dict_images["IMAGEM_ORIGINAL_RGB_DUPLO_CHECK"] = check_orientation.get_image_correct_orientation(img_rgb, 2)

    if settings.PRE_PROC_IMAGE:

        """
            ENVIA:
                1) IMAGEM CROPPADA EM ESCALA DE CINZA
                2) IMAGEM CROPPADA NA COR ORIGINAL
        """

        dict_images["IMAGEM_CROPPED_GRAY"] = cropped_image
        dict_images["IMAGEM_CROPPED_GRAY_DUPLO_CHECK"] = check_orientation.get_image_correct_orientation(cropped_image,
                                                                                                         2)

    # ENVIANDO A IMAGEM ORIGINAL E A IMAGEM EM PRETO E BRANCO
    for idx, image in enumerate(dict_images):

        # INICIANDO AS VARIÁVEL QUE ARMAZENARÁ O RESULTADO DA RODADA
        info_doc = {}

        print("-" * 50)
        print("MODELO TRÊS - RODADA: {} - {}".format(idx, image))

        text, data_exp, data_nasc, list_result_rg, list_result_cpf, \
        nome, nome_pai, nome_mae, \
        cidade_nasc, estado_nasc, cidade_origem, estado_origem = model_three(dict_images[image]).orchestra_model()

        # ARMAZENANDO OS RESULTADOS NO DICT DE RESULTADO
        info_doc['RG'] = list_result_rg
        info_doc['DATA_EXPED'] = data_exp
        info_doc['NOME'] = nome
        info_doc['NOME_MAE'] = nome_mae
        info_doc['NOME_PAI'] = nome_pai
        info_doc['DATA_NASC'] = data_nasc
        info_doc['CPF'] = list_result_cpf
        info_doc['CIDADE_NASC'] = cidade_nasc
        info_doc['ESTADO_NASC'] = estado_nasc
        info_doc['CIDADE_ORIGEM'] = cidade_origem
        info_doc['ESTADO_ORIGEM'] = estado_origem

        # VISUALIZANDO OS RESULTADOS
        print("RESULTADO OBTIDO - RODADA: {} - {}".format(idx, image))
        print(info_doc)

        # ARMAZENANDO O RESULTADO
        result_model.append([text, info_doc])

    return result_model






