"""

    FUNÇÕES PARA REALIZAÇÃO DE OCR DE UMA IMAGEM.
    O OCR PERMITIRÁ TRANSCREVER A IMAGEM.
    CONVERSÃO IMAGEM PARA TEXTO.

    # Arguments
        object                  - Required : Imagem para aplicação do OCR (String | Object)
    # Returns
        texto_obtido            - Required : Texto obtido após aplicação da técnica de OCR (String)

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "28/10/2021"


from inspect import stack

import cv2
from dynaconf import settings
import pytesseract

from UTILS.generic_functions import converte_int
from UTILS.image_view import image_view_functions
from UTILS.image_convert_format import orchestra_read_image


class ocr_functions():

    """

        FUNÇÕES PARA REALIZAÇÃO DE OCR DE UMA IMAGEM.
        O OCR PERMITIRÁ TRANSCREVER A IMAGEM.
        CONVERSÃO IMAGEM PARA TEXTO.

        # Arguments
            imagem_atual            - Required : Imagem para aplicação do OCR (String | Object)
            lang_padrao             - Optional : Linguagem que será utilizada no OCR (String)
            config_tesseract_psm    - Optional : Configuração do tesseract.
                                                 É possível passar um valor
                                                 específico de PSM. (String | Integer)
            config_tesseract_oem    - Optional : Configuração do tesseract.
                                                 É possível passar um valor
                                                 específico de OEM. (String | Integer)
            tipo_retorno_ocr_input  - Optional : Tipo de retorno do ocr desejado (String)
        # Returns
            texto_ocr               - Required : Texto obtido após aplicação da técnica de OCR (String)

    """

    def __init__(self,
                 lang_padrao=settings.TESSERACT_LANG,
                 config_tesseract_psm=settings.TESSERACT_PSM,
                 config_tesseract_oem=settings.TESSERACT_OEM,
                 tipo_retorno_ocr_input=settings.TIPO_OCR,
                 visualiza_ocr_completo=settings.VISUALIZA_OCR_COMPLETO):


        # 1 - LINGUAGEM PADRÃO DO OCR
        self.lang_padrao = lang_padrao

        # 2 - CONFIG PSM DO TESSERACT
        self.config_tesseract_psm = config_tesseract_psm

        # 3 - CONFIG OEM DO TESSERACT
        self.config_tesseract_oem = config_tesseract_oem

        # 4 - LISTA DE TIPOS DE RETORNO DO OCR
        self.lista_tipos_retorno_ocr = ["TEXTO", "COMPLETO"]

        # 5 - TIPO DE RETORNO DO OCR SELECIONADA
        self.tipo_retorno_ocr = tipo_retorno_ocr_input
        self.visualiza_ocr_completo = visualiza_ocr_completo


    @staticmethod
    def converte_bgr_rgb(imagem_para_conversao_rgb):

        """

            CONVERTE UMA IMAGEM DE FORMATO BGR PARA RGB.
            PARA A CONVERSÃO, UTILIZA OPENCV - CVTCOLOR (ARGS: cv2.COLOR_BGR2RGB)

            # Arguments
                imagem_para_conversao_rgb        - Required : Imagem para aplicação da conversão (Object)
            # Returns
                validador                        - Required : Validador de execução da função (Boolean)
                rgb                              - Required : Imagem após conversãO RGB (Object)

        """

        # INICIANDO O VALIDADOR
        validador = False

        try:
            rgb = cv2.cvtColor(imagem_para_conversao_rgb, cv2.COLOR_BGR2RGB)

            validador = True

            return validador, rgb

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))
            return validador, imagem_para_conversao_rgb


    def tesseract_lang_disponiveis(self):

        """

            OBTÉM A LISTA DE LINGUAGENS DISPONÍVEIS.
            UTILIZA TESSERACT - GET LANGUAGES

            # Arguments

            # Returns
                validador                        - Required : Validador de execução da função (Boolean)
                lista_linguagens_tesseract       - Required : Lista de lang disponíveis (List)

        """

        # INICIANDO O VALIDADOR
        validador = False

        # INICIANDO A VARIÁVEL DE LINGUAGENS DISPONÍVEIS
        lista_linguagens_tesseract = []

        try:
            lista_linguagens_tesseract = pytesseract.get_languages(config='')

            validador = True

        except Exception as ex:
            print("A LINGUAGEM SELECIONADA NÃO ESTÁ DISPONÍVEL")
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return lista_linguagens_tesseract


    @staticmethod
    def obtem_tesseract_psm_oem(valor_config_psm, valor_config_oem):

        """
        Modos de segmentação de página:
           0 Orientação e detecção de script (OSD) apenas.
           1 Segmentação de página automática com OSD.
           2 Segmentação automática de página, mas sem OSD ou OCR.
           3 Segmentação de página totalmente automática, mas sem OSD. (Padrão)
           4 Considere uma única coluna de texto de tamanhos variáveis.
           5 Considere um único bloco uniforme de texto alinhado verticalmente.
           6 Considere um único bloco de texto uniforme.
           7 Trate a imagem como uma única linha de texto.
           8 Trate a imagem como uma única palavra.
           9 Trate a imagem como uma única palavra em um círculo.
          10 Trate a imagem como um único caractere.
          11 Texto esparso. Encontre o máximo de texto possível em nenhuma ordem específica.
          12 Texto esparso com OSD.
          13 Linha bruta. Trate a imagem como uma única linha de texto,
             contornando hacks que são específicos do Tesseract.
        """

        """
        Modo do motor:
            0 Legacy Engine somente
            1 Neural Nets LSTM Engine somente
            2 Legacy + LSTM engines
            3 Padrão, o que estiver disponível
        """

        # INICIANDO O VALIDADOR
        validador = False

        # INICIANDO A VARIÁVEL DE CONFIG PSM
        valor_psm_oem_tesseract = 'tessdata'

        # CONVERTENDO OS VALORES PARA INT

        try:
            # VERIFICANDO SE O VALOR DE PSM E OEM ENCONTRA-SE DENTRE AS CONFIGS
            if converte_int(valor_config_psm) in range(14) and converte_int(valor_config_oem) in range(4):

                # CONVERTENDO O VALOR DO ARGUMENTO (INT) PARA
                # FORMA ESPERADA PELO TESSERACT

                valor_psm_oem_tesseract = 'tessdata --psm {} --oem {}'.format(str(valor_config_psm),
                                                                              str(valor_config_oem))

                validador = True

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return valor_psm_oem_tesseract


    def obtem_orientacao_imagem(self, caminho_imagem_atual = None):

        """

            DETECTA E RETORNA A ORIENTAÇÃO DA IMAGEM.


            # Arguments
                caminho_imagem_atual        - Required : Caminho da imagem atual (String)
            # Returns
                validador                   - Required : Validador de execução da função (Boolean)
                valor_orientacao            - Required : Propriedades de orientação da imagem (String)

        """

        """ Page number,
            Orientation in degrees,
            Rotate,
            Orientation confidence,
            Script,
            Script confidence
        """

        # INICIANDO O VALIDADOR
        validador = False

        # INICIANDO A VARIÁVEL QUE ARMAZENARÁ A ORIENTAÇÃO
        valor_orientacao = {}

        # VERIFICANDO SE UMA NOVA IMAGEM FOI PASSADA COMO ARGUMENTO DA CHAMADA DA FUNÇÃO
        if caminho_imagem_atual is None:
            caminho_imagem_atual = self.imagem_atual

        try:

            # ORQUESTRANDO A LEITURA DA IMAGEM
            imagem_atual = orchestra_read_image(caminho_imagem_atual)

            valor_orientacao = pytesseract.image_to_osd(imagem_atual)
            validador = True

        except Exception as ex:
            print("NÃO FOI POSSÍVEL DETECTAR A ORIENTAÇÃO DA PÁGINA")
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validador, valor_orientacao


    def set_config_tesseract(self):

        """

            OBTÉM AS INFORMAÇÕES DA IMAGEM APÓS APLICAÇÃO DO OCR.
            ESSA FUNÇÃO TRAZ TODAS AS INFORMAÇÕES CONTIDAS NO TEXTO ABAIXO.
            POSIÇÕES DOS TEXTOS ENCONTRATOS, NÍVEL DE CONFIANÇA E TEXTOS.


            # Arguments
                imagem_rgb                  - Required : Imagem para aplicação do ocr (Object)
            # Returns
                validador                   - Required : Validador de execução da função (Boolean)
                infos_ocr                   - Required : Informações obtidas no OCR (Dict)

        """

        # INICIANDO O VALIDADOR
        validador = False

        try:
            # VERIFICANDO SE A LINGUAGEM SELECIONADA, ESTÁ DISPONÍVEL
            if self.lang_padrao not in ocr_functions.tesseract_lang_disponiveis(self):
                # COMO A LINGUAGEM SELECIONADA NÃO ESTÁ DISPONÍVEL
                # UTILIZAREMOS A VERSÃO ENGLISH
                self.lang_padrao = 'eng'

            # VERIFICANDO A CONFIGURAÇÃO PSM - OEM
            self.config_tesseract_psm_oem = ocr_functions.obtem_tesseract_psm_oem(self.config_tesseract_psm,
                                                                                  self.config_tesseract_oem)


            validador = True

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validador


    @staticmethod
    def convert_resultado_ocr_completo(input_result_ocr):

        """

            APÓS A REALIZAÇÃO DO OCR COMPLETO (POR BOUNDING BOX),
            ESSA FUNÇÃO CONCATENA O TEXTO, RESULTANDO EM UMA ÚNICA STRING.

            # Arguments
                input_result_ocr              - Required : Resultado do OCR (List)
            # Returns
                list_result                   - Required : Resultado do OCR (List)
                text_result                   - Required : Resulado do OCR concatenado
                                                           em uma única string (String)

        """

        # INICIANDO AS VARIÁVEIS QUE ARMAZENARÃO O RESULTADO FINAL
        string_atual = ""
        list_result = []

        # CONCATENANDO O RESULTADO DO OCR (CONTIDO NO CAMPO 'text' DO DICT)
        result_ocr = " ".join(input_result_ocr["text"])

        # PERCORRENDO O TEXTO CONCATENADO E REALIZANDO AS QUEBRAS DE LINHA
        for value in str(result_ocr).strip().split(" "):

            text_valid = False

            if str(value).strip() != "":
                string_atual = string_atual + " " + value
                text_valid = True
            else:
                text_valid = False
                list_result.append(str(string_atual).strip())
                string_atual = ""

        # FORMATANDO PARA RESULTADO EM FORMATO TEXTO
        text_result = "\n".join(list_result)

        # RETORNANDO O RESULTADO DO OCR
        # LISTA CONTENDO CADA UM DOS TEXTOS
        # TEXTO CONTENDO O TEXTO COM QUEBRA DE LINHAS
        return list_result, text_result


    def realizar_ocr_retorno_completo(self, imagem_rgb):

        """

            OBTÉM AS INFORMAÇÕES DA IMAGEM APÓS APLICAÇÃO DO OCR.
            ESSA FUNÇÃO TRAZ TODAS AS INFORMAÇÕES CONTIDAS NO TEXTO ABAIXO.
            POSIÇÕES DOS TEXTOS ENCONTRATOS, NÍVEL DE CONFIANÇA E TEXTOS.


            # Arguments
                imagem_rgb                  - Required : Imagem para aplicação do ocr (Object)
            # Returns
                validador                   - Required : Validador de execução da função (Boolean)
                infos_ocr                   - Required : Informações obtidas no OCR (Dict)

        """

        """
        - lock_num = Número do bloco atual. Quando o tesseract faz o OCR,
        ele divide a imagem em várias regiões, o que pode variar de
        acordo com os parametros do PSM e também outros critérios próprios do algoritmo.
        Cada bloco é uma região

        - conf = confiança da predição (de 0 a 100. -1 significa que não foi reconhecido texto)

        - height = altura do bloco de texto detectada (ou seja, da caixa delimitadora)

        - left = coordenada x onde inicia a caixa delimitadora

        - level = o level (nível) corresponde à categoria do bloco detectado. são 5 valores possiveis:
          1. página
          2. bloco
          3. parágrafo
          4. linha
          5. palavra

        Portanto, se foi retornado o valor 5 significa que o bloco detectado é texto, se foi 4 significa que o que foi detectado é uma linha

        - line_num = número da linha do que foi detectado (inicia com 0)

        - page_num = o índice da página onde o item foi detectado. Na maioria dos casos sempre haverá uma página só

        - text = o resultado do reconhecimento

        - top = coordenada y onde a caixa delimitadora começa

        - width = largura do bloco de texto atual detectado

        - word_num = numero da palavra (indice) dentro do bloco atual"""

        # INICIANDO O VALIDADOR
        validador = False

        # INICIANDO A VARIÁVEL INFORMAÇÕES DE OCR
        infos_ocr = {}

        try:
            # REALIZANDO O OCR SOBRE A IMAGEM
            infos_ocr = pytesseract.image_to_data(imagem_rgb,
                                                  lang=self.lang_padrao,
                                                  config=self.config_tesseract_psm,
                                                  output_type=pytesseract.Output.DICT)

            validador = True

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validador, infos_ocr


    def realizar_ocr(self, imagem_rgb):

        """

            REALIZA A APLICAÇÃO DE OCR SOBRE UMA IMAGEM.
            O OCR PERMITIRÁ TRANSCREVER A IMAGEM.
            CONVERSÃO IMAGEM PARA TEXTO.

            # Arguments
                imagem_rgb                  - Required : Imagem para aplicação do ocr (Object)
            # Returns
                validador                   - Required : Validador de execução da função (Boolean)
                texto                       - Required : Texto obtido (String)

        """

        # INICIANDO O VALIDADOR
        validador = False

        # INICIANDO A VARIÁVEL TEXTO
        texto = ""

        try:
            # REALIZANDO O OCR SOBRE A IMAGEM
            texto = pytesseract.image_to_string(imagem_rgb,
                                                lang=self.lang_padrao,
                                                config=self.config_tesseract_psm)

            validador = True


        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validador, texto


    def orquestra_tipo_leitura_ocr(self, imagem_rgb):

        """

            ORQUESTRA A APLICAÇÃO DE OCR SOBRE UMA IMAGEM.
            SELECIONA QUAL FUNÇÃO SERÁ UTILIZADA.
            UMA OPÇÃO RETORNARÁ APENAS O RESULTADO TEXTUAL DO OCR.
            OUTRA OPÇÃO RETORNARÁ TODAS AS INFORMAÇÕES DO OCR.


            # Arguments
                imagem_rgb                  - Required : Imagem para aplicação do ocr (Object)
            # Returns
                validador                   - Required : Validador de execução da função (Boolean)
                retorno_ocr                 - Required : Retorno do OCR (String | Dict)

        """

        # INICIANDO AS VARIÁVEIS DE RETORNO
        validador = False
        retorno_ocr = None

        if self.tipo_retorno_ocr == self.lista_tipos_retorno_ocr[0]:
            # O RETORNO SERÁ APENAS O TEXTUAL
            validador, retorno_ocr = ocr_functions.realizar_ocr(self, imagem_rgb)

        elif self.tipo_retorno_ocr == self.lista_tipos_retorno_ocr[1]:
            # O RETORNO SERÁ UM DICT CONTENDO TODAS AS INFORMAÇÕES
            validador, retorno_ocr = ocr_functions.realizar_ocr_retorno_completo(self, imagem_rgb)

        else:
            print("NÃO FOI INFORMADA NENHUMA OPÇÃO VÁLIDA DE RETORNO DO OCR")

        return validador, retorno_ocr


    def Orquestra_OCR(self, image):

        # INICIANDO O VALIDADOR
        validador = False

        # OBTENDO A ORIENTAÇÃO DA IMAGEM
        # validador, resultado_orientacao = ocr_functions.obtem_orientacao_imagem(self, image)

        # REALIZANDO A LEITURA DA IMAGEM
        img_ocr = orchestra_read_image(image)

        # DEFININDO AS CONFIGURAÇÕES DO OCR - TESSERACT
        validador = ocr_functions.set_config_tesseract(self)

        validador, retorno_ocr = ocr_functions.orquestra_tipo_leitura_ocr(self, img_ocr)

        if validador is False:
            print("NÃO FOI POSSÍVEL APLICAR O OCR")

        return retorno_ocr

