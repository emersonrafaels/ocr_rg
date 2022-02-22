"""

    FUNÇÕES UTEIS PARA PRÉ PROCESSAMENTO DA IMAGEM, ANTES DA APLICAÇÃO DO OCR.

    1. A IMAGEM É LIDA EM ESCALA DE CINZA;
    2. GAUSSIAN BLUR É EXECUTADO PARA REMOVER QUALQUER RUÍDO DISPONÍVEL;
    3. O LIMIAR ADAPTATIVO É APLICADO À IMAGEM BORRADA;
    4. ENCONTRAMOS O CONTORNO CUJA ÁREA É MAIOR, POIS REPRESENTA O QUADRO DO DOCUMENTO;
    5. COM O CONTORNO ENCONTRADO NA ÚLTIMA ETAPA, CRIAMOS UMA MÁSCARA COM A ÁREA REPRESENTADA PELA MOLDURA;
    6. USANDO ESTA MÁSCARA, PODEMOS ENCONTRAR OS QUATRO CANTOS DO DOCUMENTO DE IDENTIFICAÇÃO NA IMAGEM ORIGINAL;
    7. PORTANTO, APLICAMOS DEWARPING E TRANSFORMAMOS NOSSA PERSPECTIVA,
    DE FORMA QUE OS QUATRO CANTOS DO DOCUMENTO SEJAM IGUAIS À IMAGEM.

    # Arguments
        object                  - Required : Imagem para aplicação do OCR (Base64 | Path | Numpy Array)
    # Returns
        output_rg               - Required : Textos dos campos do RG após aplicação das
                                             técnicas de pré processamento,
                                             OCR e pós processamento (String)

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "16/10/2021"


from inspect import stack

import cv2
from dynaconf import settings
import numpy as np
import imutils

from UTILS.generic_functions import get_date_time_now
from UTILS.image_read import read_image_gray
from UTILS.image_view import image_view_functions


class Image_Pre_Processing(object):

    def __init__(self, blur_ksize=5, threshold_max_color_value=255,
                 dilation_ksize=5, width_resize=600, output_size=600):

        # 1 - DEFININDO O TAMANHO DO KERNEL GAUSSIANO PARA DESFOQUE
        self.__blur_ksize = blur_ksize

        # 2 - DEFININDO O VALOR DE PIXEL QUE SERÁ USADO COMO LIMIAR
        self.__threshold_max_color_value = threshold_max_color_value

        # 3 - DEFININDO O TAMANHO DO KERNEL GAUSSIANO PARA DILATAÇÃO
        self.__dilation_ksize = dilation_ksize

        # 4 - LARGURA PARA RESIZE DA IMAGEM
        self.__width = width_resize

        # 5 - TAMANHO DE SAÍDA DA IMAGEM (QUADRADA)
        self.__output_size = output_size


    @property
    def blur_ksize(self):

        """

            PROPRIEDADE DO PROCEDIMENTO DE DESFOQUE (BLUR).

            ESSA PROPRIEDADE SERÁ USADA PARA UM FILTRO PASSA-BAIXA
            PARA REDUZIR A QUANTIDADE DE RUÍDO E DETALHES EM UMA IMAGEM.

            AO REDUZIR OS DETALHES EM UMA IMAGEM, PODEMOS ENCONTRAR
            MAIS FACILMENTE OS OBJETOS NOS QUAIS ESTAMOS INTERESSADOS (NO CASO APENAS O RG).

            A DETECÇÃO DE BORDAS, TÊM MELHOR DESEMPENHO SE A
            IMAGEM PRIMEIRO FOR SUAVIZADA OU DESFOCADA.

            A PROPRIEDADE '__blur_ksize' É TAMANHO DO KERNEL GAUSSIANO [ALTURA LARGURA].
            A ALTURA E A LARGURA DEVEM SER ÍMPARES E PODEM TER VALORES DIFERENTES.

            # Arguments

            # Returns
                self.__blur_ksize        - Required : Propriedade, somente leitura, do blur
                                                      Define o tamanho do kernel gaussiano (Integer)

        """

        return self.__blur_ksize


    @property
    def threshold_value(self):

        """

            PROPRIEDADE DO PROCEDIMENTO DE SEPARAÇÃO DE PLANO DE FUNDO E PRIMEIRO PLANO.

            ESSA PROPRIEDADE SERÁ USADA PARA DEFINIR UM VALOR DE LIMIAR

            NAS TÉCNICAS DE LIMIARIZAÇÃO GLOBAL, O MESMO VALOR DE T É USADO PARA TESTAR
            TODOS OS PIXELS NA IMAGEM DE ENTRADA, SEGMENTANDO-OS EM PRIMEIRO E SEGUNDO PLANO.

            O PROBLEMA AQUI É QUE TER APENAS UM VALOR DE T PODE NÃO SER SUFICIENTE,
            DEVIDO ÀS VARIAÇÕES NAS CONDIÇÕES DE ILUMINAÇÃO, SOMBRAS, ETC.,
            PODE SER QUE UM VALOR DE T FUNCIONE PARA UMA CERTA P
            ARTE DA IMAGEM DE ENTRADA, MAS FALHE TOTALMENTE EM UM SEGMENTO DIFERENTE.

            O LIMIAR ADAPTATIVO CONSIDERA UM PEQUENO CONJUNTO
            DE PIXELS VIZINHOS POR VEZ, CALCULA T PARA
            AQUELA REGIÃO LOCAL ESPECÍFICA E, EM SEGUIDA, REALIZA A SEGMENTAÇÃO.

            # Arguments

            # Returns
                self.__threshold_max_color_value     - Required : Propriedade,
                                                      somente leitura, do valor de pixel que será
                                                      convertido após aplicação da
                                                      técnica de limiar (Integer)

        """

        return self.__threshold_max_color_value


    @property
    def dilation_ksize(self):

        """

            

            # Arguments

            # Returns
                self.dilation_ksize        - Required : Propriedade, somente leitura,
                                                        do kernel de dilatação (Integer)

        """

        return self.__dilation_ksize


    @property
    def output_size(self):

        return self.__output_size


    def _resize_image(self, img):

        """

            FUNÇÃO RESPONSÁVEL POR REALIZAR O REDIMENSIONAMENTO DA IMAGEM.

            É ESPERADO QUE AS IMAGENS ESTEJAM COM LARGURA/COMPRIMENTO, SEMELHANTES
            AO DO VALOR 'self.__width'.

            # Arguments
                img                    - Required : Imagem para processamento (Array)

            # Returns
                image_resize           - Required : Imagem após processamento do resize (Array)

        """


        try:
            # OBTENDO A RAZÃO ENTRE O VALOR DE LARGURA (DESEJADO) E ALTURA
            r = self.__width / img.shape[0]

            # REDIMENSIONANDO A ALTURA, E SETANDO A LARGURA COM O VALOR DESEJADO
            dim = (int(img.shape[1] * r), self.__width)

            # REALIZANDO O RESIZE DA IMAGEM COM AS NOVAS DIMENSÕES
            image_resize = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

            print("OCR RG - RESIZE DA IMAGEM APLICADO COM SUCESSO - {}".format(get_date_time_now("%d/%m/%Y %H:%M:%S")))

            return image_resize

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))
            return img


    def _smoothing_blurring(self, img):

        """

            O DESFOQUE GAUSSIANO É SEMELHANTE AO DESFOQUE MÉDIO,
            MAS EM VEZ DE USAR UMA MÉDIA SIMPLES,
            ESTAMOS USANDO UMA MÉDIA PONDERADA,
            ONDE OS PIXELS DA VIZINHANÇA QUE ESTÃO MAIS PRÓXIMOS DO PIXEL CENTRAL
            CONTRIBUEM COM MAIS “PESO” PARA A MÉDIA.

            A SUAVIZAÇÃO GAUSSIANA É USADA PARA REMOVER O RUÍDO QUE
            SEGUE APROXIMADAMENTE UMA DISTRIBUIÇÃO GAUSSIANA.

            O RESULTADO FINAL É QUE NOSSA IMAGEM FICA MENOS DESFOCADA,
            PORÉM MAIS "DESFOCADA NATURALMENTE".. ALÉM DISSO, COM BASE NESSA PONDERAÇÃO,
            SEREMOS CAPAZES DE PRESERVAR MAIS AS BORDAS EM NOSSA
            IMAGEM EM COMPARAÇÃO COM A SUAVIZAÇÃO MÉDIA.

            # Arguments
                img                    - Required : Imagem para processamento (Array)

            # Returns
                blur                   - Required : Imagem após processamento do desfoque (Array)

        """

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validator = True

        try:
            blur = cv2.GaussianBlur(img, (self.__blur_ksize, self.__blur_ksize), 0)

            print("OCR RG - TÉCNICA DE DESFOQUE GAUSSIANO APLICADO COM SUCESSO - {}".format(get_date_time_now("%d/%m/%Y %H:%M:%S")))

            validator = True

            return validator, blur

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validator, img


    def _threshold_image(self, img):

        """

            O LIMIAR ADAPTATIVO CONSIDERA UM PEQUENO CONJUNTO
            DE PIXELS VIZINHOS POR VEZ, CALCULA T PARA
            AQUELA REGIÃO LOCAL ESPECÍFICA E, EM SEGUIDA, REALIZA A SEGMENTAÇÃO.

            O SEGUNDO PARÂMETRO DA FUNÇÃO É O VALOR DO LIMITE DE SAÍDA, OU SEJA, PIXEL <= T TORNARA-SE ESSE VALOR DE PIXEL.
                EX: SE PIXEL <= T, o PIXEL TORNA-SE BRANCO (255)

            O TERCEIRO ARGUMENTO É O MÉTODO DE LIMIAR ADAPTATIVO. AQUI NÓS
            FORNECEMOS UM VALOR DE CV2.ADAPTIVE_THRESH_GAUSSIAN_C
            PARA INDICAR QUE ESTAMOS USANDO A MÉDIA GAUSSIANA DA VIZINHANÇA
            LOCAL DO PIXEL PARA CALCULAR NOSSO VALOR LIMITE DE T.

            O QUARTO VALOR É O MÉTODO DE LIMIAR, AQUI PASSAMOS UM VALOR
            DE CV2.THRESH_BINARY_INV PARA INDICAR QUE QUALQUER VALOR DE PIXEL QUE PASSE NO
            TESTE DE LIMITE TERÁ UM VALOR DE SAÍDA DE 0. CASO CONTRÁRIO, TERÁ UM VALOR DE 255.

            O QUINTO PARÂMETRO É O TAMANHO DE NOSSA VIZINHANÇA DE PIXEL,
            AQUI VOCÊ PODE VER QUE IREMOS CALCULAR O VALOR MÉDIO DA INTENSIDADE
            DO PIXEL EM TONS DE CINZA DE CADA SUB-REGIÃO 11 × 11 NA IMAGEM PARA CALCULAR NOSSO VALOR LIMITE.

            O ARGUMENTO FINAL PARA CV2.ADAPTIVETHRESHOLD É A CONSTANTE C
            QUE PERMITE SIMPLESMENTE AJUSTAR O VALOR LIMITE.

            # Arguments
                img                    - Required : Imagem para processamento (Array)

            # Returns
                thresh                 - Required : Imagem após processamento do limiar (Array)

        """

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validator = True

        try:
            thresh = cv2.adaptiveThreshold(img, self.__threshold_max_color_value,
                                           cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY_INV, settings.THRESHOLD_KSIZE,
                                           settings.SUBTRACT_FROM_MEAN)

            print("OCR RG - TÉCNICA DE LIMIAR ADAPTATIVO APLICADO COM SUCESSO - {}".format(get_date_time_now("%d/%m/%Y %H:%M:%S")))

            validator = True

            return validator, thresh

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validator, img


    def __preprocess_blur_threshold_img(self, img):

        """

            REALIZA A ORQUESTRAÇÃO DE DUAS TÉCNICAS DE PRÉ PROCESSAMENTO DA IMAGEM.

            1) APLICA AS TÉCNICAS DE DESFOQUE (GAUSSIANBLUR)
            2) APLICA LIMIAR DOS PLANOS DA IMAGEM (ADAPTIVETHRESHOLD)

            # Arguments
                img                    - Required : Imagem para processamento (Array)

            # Returns
                thresh                - Required : Imagem após ambos processamentos (Array)

        """

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validator = False

        print("OCR RG - INICIANDO O PRÉ PROCESSAMENTO DA IMAGEM - {}".format(get_date_time_now("%d/%m/%Y %H:%M:%S")))

        try:
            # REALIZANDO O DESFOQUE GAUSSIANO
            validator, blur = Image_Pre_Processing._smoothing_blurring(self, img)

            if validator:

                # APLICANDO O LIMIAR PARA MELHOR SEPARAÇÃO DE PLANO PRINCIPAL E FUNDO
                validator, thresh = Image_Pre_Processing._threshold_image(self, blur)

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validator, thresh


    def __get_max_contour(self, img):

        """

            REALIZA A OBTENÇÃO DO CONTORNO DE MAIOR ÁREA DA FIGURA.

            O OBJETIVO É ENCONTRAR O MÁXIMO CONTORNO, PARA OBTER APENAS O DOCUMENTO DE IDENTIIFAÇÃO,
            RETIRANDO POSSÍVEIS OUTROS OBJETOS OU
            CASOS NO QUAL O DOCUMENTO POSSA ESTAR SCANEADO EM UMA FOLHA SULFITE.

            1) OBTÉM TODOS OS CONTORNOS
            2) OBTÉM O CONTORNO DE MÁXIMA ÁREA.

            # Arguments
                img                - Required : Imagem para processamento (Array)

            # Returns
                roi                - Required : Área de interesse (Array)

        """

        # INICIANDO A VARIAVEL QUE ARMAZENARÁ O VALOR DE MÁXIMA ÁREA DE CONTORNO
        roi = max_area = 0

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validator = False

        print("OCR RG - BUSCANDO O DOCUMENTO NA IMAGEM - {}".format(get_date_time_now("%d/%m/%Y %H:%M:%S")))

        try:
            # OBTENDO TODOS OS CONTORNOS
            contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            # PERCORRENDO TODOS OS CONTORNOS
            for contour in contours:

                # OBTENDO O TAMANHO DA ÁREA DO CONTORNO
                area = cv2.contourArea(contour)

                # VERIFICANDO SE O VALOR É MAIOR DO QUE ATUALMENTE É A MÁXIMA ÁREA
                if area > max_area:

                    # CASO VALOR ATUAL SEJA MAIOR QUE A MÁXIMA ÁREA, O VALOR DA MÁXIMA ÁREA É ATUALIZADO
                    max_area = area

                    # ROI ARMAZENA O CONTORNO
                    roi = contour

            validator = True

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validator, roi


    def __crop_image_countour(self, img, contour):

        """

            REALIZA O CROP DA IMAGEM ORIGINAL COM BASE NO CONTORNO DE MÁXIMA ÁREA ENCONTRADO.

            # Arguments
                img                 - Required : Imagem para processamento (Array)
                contour             - Required : Valor do contorno da imagem (Array)

            # Returns
                mask                - Required : Imagem com a máscara de contornos (Array)

        """

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validator = False

        # INICIANDO AS VARIÁVEIS QUE ARMAZENARÃO A LISTA DE CONTORNOS NA HORIZONTAL E VERTICAL
        x, y = [], []

        print("OCR RG - CROPPANDO O DOCUMENTO NA IMAGEM - {}".format(get_date_time_now("%d/%m/%Y %H:%M:%S")))

        try:
            for contour_line in contour:
                x.append(contour_line[0][0])
                y.append(contour_line[0][1])

            # OBTENDO OS VALORES MIN E MÁXIMO DE CADA EIXO
            x1, x2, y1, y2 = min(x), max(x), min(y), max(y)

            # APLICANDO O CROP NA IMAGEM
            image_cropped_contour = img[y1:y2, x1:x2]

            validator = True

            print("OCR RG - CROP REALIZADO COM SUCESSO - {}".format(get_date_time_now("%d/%m/%Y %H:%M:%S")))

            return validator, image_cropped_contour

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validator, img


    def __generate_mask(self, img, contour):

        """

            REALIZA A CRIAÇÃO DA MÁSCARA DE CONTORNO DA MÁXIMA ÁREA DE CONTORNO.

            A TÉCNICA DE DILATAÇÃO É APLICADA PARA ACENTUAR A MÁSCARA.

            # Arguments
                img                 - Required : Imagem para processamento (Array)
                contour             - Required : Valor do contorno da imagem (Array)

            # Returns
                mask                - Required : Imagem com a máscara de contornos (Array)

        """

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validator = False

        try:
            # CRIA A MÁSCARA DO TAMANHO DA IMAGEM, COM TODOS OS VALORES 0 (PRETO)
            mask = np.zeros(img.shape, dtype=np.uint8)

            # mask: imagem utilizada
            # contour: contorno a ser feito,
            # nesse caso o resultado da função de máx area de contorno
            # 0: o índice do contorno a ser utilizado
            # 255: a cor do contorno
            # -1: esperassura do contorno
            cv2.drawContours(mask, [contour], 0, 255, -1)
            cv2.drawContours(mask, [contour], 0, 0, 2)

            # REALIZANDO A DILATAÇÃO PARA AUMENTAR A MÁSCARA DE CONTORNO
            mask = cv2.dilate(mask, (self.__dilation_ksize, self.__dilation_ksize), iterations=10)

            print("OCR RG - MASK DE CONTORNO APLICADO COM SUCESSO - {}".format(get_date_time_now("%d/%m/%Y %H:%M:%S")))

            validator = True

            return validator, mask

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validator, img


    def __find_corners(self, mask):


        """

            OPENCV TEM UMA FUNÇÃO, CV2.GOODFEATURESTOTRACK ().
            ELE ENCONTRA N CANTOS MAIS FORTES NA IMAGEM PELO MÉTODO SHI-TOMASI (OU DETECÇÃO DE CANTO HARRIS).
            COMO DE COSTUME, A IMAGEM DEVE SER UMA IMAGEM EM TONS DE CINZA.

            EM SEGUIDA, ESPECIFICA-SE O NÚMERO DE CANTOS QUE DESEJA ENCONTRAR (4).

            EM SEGUIDA, ESPECIFICA-SE O NÍVEL DE QUALIDADE, QUE É UM VALOR ENTRE 0-1 (0.01)
            QUE DENOTA A QUALIDADE MÍNIMA DE CANTO ABAIXO DA QUAL TODOS SÃO REJEITADOS.

            EM SEGUIDA, FORNECE-SE A DISTÂNCIA EUCLIDIANA MÍNIMA ENTRE OS CANTOS DETECTADOS (10).

            COM TODAS ESSAS INFORMAÇÕES, A FUNÇÃO ENCONTRA CANTOS NA IMAGEM.
            TODOS OS CANTOS ABAIXO DO NÍVEL DE QUALIDADE SÃO REJEITADOS.
            EM SEGUIDA, ELE CLASSIFICA OS CANTOS RESTANTES COM BASE NA QUALIDADE NA ORDEM DECRESCENTE.
            ENTÃO, A FUNÇÃO PEGA O PRIMEIRO CANTO MAIS FORTE,
            DESCARTA TODOS OS CANTOS PRÓXIMOS NA FAIXA DE DISTÂNCIA MÍNIMA E RETORNA N CANTOS MAIS FORTES.

            # Arguments
                mask                - Required : Imagem com a máscara de contornos (Array)

            # Returns
                validator           - Required : Validador de execução da função (Boolean)
                result_corners      - Required : Resultado contendo a lista de cantos da imagem (Array)


        """

        # INICIANDO O VALIDADOR DA FUNÇÃO
        validator = False

        try:
            # OBTENDO OS CANTOS DA IMAGEM
            corners = cv2.goodFeaturesToTrack(mask, 4, 0.01, 10)

            # CONVERTENDO OS VALORES EM INT64
            corners = np.int0(corners)

            # CONVERTENDO OS VALORES DE CANTOS PARA FLOAT E REALIZANDO O RESHAPE
            result_corners = np.float32(corners.reshape(-1, 2))

            validator = True

            return validator, result_corners

        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return validator, None


    def __find_new_corners(self, v, high_value=600):

        idx = np.zeros(v.shape)
        v_copy = v.copy()
        x = v_copy[:,0]
        x_sorted = np.sort(v_copy[:,0])
        y = v_copy[:,1]
        x_array = []
        for element in x:
            for i, sorted_element in enumerate(x_sorted):
                if element == sorted_element:
                    x_array.append(i)
        #idx[:,0] = x_array
        idx[:, 0] = x_array[:4]
        idx[:,1] = y.argsort()
        return np.float32((idx>1)*high_value)


    def orchestra_pre_processing(self, image):

        """

            1) A IMAGEM É LIDA EM ESCALA DE CINZA;
            2) O GAUSSIAN BLUR É EXECUTADO PARA REMOVER QUALQUER RUÍDO DISPONÍVEL;
            3) O LIMIAR ADAPTATIVO É APLICADO À IMAGEM BORRADA;
            4) ENCONTRAMOS O CONTORNO CUJA ÁREA É MAIOR, POIS REPRESENTA O QUADRO DO DOCUMENTO;
            5) COM O CONTORNO ENCONTRADO NA ÚLTIMA ETAPA, CRIAMOS UMA MÁSCARA COM A ÁREA REPRESENTADA PELA MOLDURA;
            6) USANDO ESTA MÁSCARA, PODEMOS ENCONTRAR OS QUATRO CANTOS DO DOCUMENTO DE IDENTIFICAÇÃO NA IMAGEM ORIGINAL;
            7) PORTANTO, APLICAMOS O DEWARPING E TRANSFORMAMOS NOSSA PERSPECTIVA, DE FORMA QUE OS QUATRO CANTOS DO DOCUMENTO SEJAM IGUAIS À IMAGEM.

            img = image_crooped_contour = image_warped

            # Arguments
                dir_image                 - Required : Imagem a ser lida (String)

            # Returns
                img                       - Required : Imagem lida em escala de cinza (Array)
                image_cropped_contour     - Required : Imagem após aplicação
                                                       do crop de contornos (Array)
                image_warped              - Required : Imagem após aplicação
                                                       da técnica de skew (Array)


        """

        # INICIANDO AS VARIÁVEIS QUE SERÃO RETORNADAS
        image_cropped_contour = image_warped = None

        if not image is None:

            while max(image.shape) > 2000:
                image = cv2.pyrDown(image)

            # REALIZANDO O REDIMENSIONAMENTO DA IMAGEM
            if image.shape[1] > self.__width:
                image = self._resize_image(image)

            # REALIZANDO O PRÉ PROCESSAMENTO DA IMAGEM COM BLURRING
            validator, preproc_img = self.__preprocess_blur_threshold_img(image)

            if validator:

                # ENCONTRAMOS O CONTORNO CUJA ÁREA É MAIOR, POIS REPRESENTA O QUADRO DO DOCUMENTO;
                validator, contour = self.__get_max_contour(preproc_img)

                if validator:

                    # COM O CONTORNO ENCONTRADO A ÚLTIMA ETAPA, REALIZAMOS O CROP DA IMAGEM
                    validator, image_cropped_contour = self.__crop_image_countour(image, contour)

                    # COM O CONTORNO ENCONTRADO NA ÚLTIMA ETAPA, CRIAMOS UMA MÁSCARA COM A ÁREA REPRESENTADA PELA MOLDURA;
                    validator, mask = self.__generate_mask(image, contour)

                    if validator:

                        # USANDO ESTA MÁSCARA, PODEMOS ENCONTRAR OS QUATRO CANTOS DO DOCUMENTO DE IDENTIFICAÇÃO NA IMAGEM ORIGINAL;
                        _, pts1 = self.__find_corners(mask)

                        pts2 = self.__find_new_corners(pts1, high_value=self.__output_size)

                        # APLICAMOS O DEWARPING E TRANSFORMAMOS NOSSA PERSPECTIVA, DE FORMA QUE OS QUATRO CANTOS DO DOCUMENTO SEJAM IGUAIS À IMAGEM.
                        M = cv2.getPerspectiveTransform(pts1, pts2)
                        image_warped = cv2.warpPerspective(image, M, (self.__output_size, self.__output_size))

                else:
                    image_cropped_contour = image_warped = image


        # VISUALIZANDO A IMAGEM APÓS O PRÉ PROCESSAMENTO
        #image_view_functions.view_image(image, window_name="ORIGINAL")
        #image_view_functions.view_image(image_cropped_contour, window_name="CROPPED")
        #image_view_functions.view_image(image_warped, window_name="WARPED")

        return image, image_cropped_contour, image_warped