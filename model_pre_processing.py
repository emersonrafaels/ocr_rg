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
import numpy


class Image_Pre_Processing(object):

    def __init__(self, blur_ksize=5, threshold_value=195,
                 dilation_ksize=5, output_size=600):

        self.__blur_ksize = blur_ksize
        self.__dilation_ksize = dilation_ksize
        self.__output_size = output_size
        self.__threshold_value = threshold_value


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

            # Arguments

            # Returns
                self.__blur_ksize        - Required : Propriedade, somente leitura, do blur (Integer)

        """

        return self.__blur_ksize


    @property
    def dilation_ksize(self):

        return self.__dilation_ksize


    @property
    def output_size(self):

        return self.__output_size


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
                self.__threshold_value        - Required : Propriedade, somente leitura, do limiar (Integer)

        """

        return self.__threshold_value


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

        blur = cv2.GaussianBlur(img, (self.__blur_ksize, self.__blur_ksize), 0)

        return blur


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
                blur                   - Required : Imagem após processamento do limiar (Array)

        """

        thresh = cv2.adaptiveThreshold(img, self.__threshold_value, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 1)

        return thresh


    def __preprocess_blur_threshold_img(self, img):

        """

            REALIZA O PRÉ PROCESSAMENTO DA IMAGEM.

            APLICA AS TÉCNICAS DE DESFOQUE (GAUSSIANBLUR)
            E LIMIAR DOS PLANOS DA IMAGEM (ADAPTIVETHRESHOLD)

            # Arguments
                img                    - Required : Imagem para processamento (Array)

            # Returns
                thresh                - Required : Imagem após ambos processamentos (Array)

        """

        # REALIZANDO O DESFOQUE GAUSSIANO
        blur = Image_Pre_Processing._smoothing_blurring(self, img)

        # APLICANDO O LIMIAR PARA MELHOR SEPARAÇÃO DE PLANO PRINCIPAL E FUNDO
        thresh = Image_Pre_Processing._threshold_image(self, blur)

        return thresh


    def __get_contour(self, img):

        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        max_area = -np.inf
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                roi = contour
        return roi


    def __generate_mask(self, img, contour):

        mask = np.zeros(img.shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], 0, 255, -1)
        cv2.drawContours(mask, [contour], 0, 0, 2)
        mask = cv2.dilate(mask, (self.__dilation_ksize, self.__dilation_ksize), iterations=10)
        return mask


    def __find_corners(self, mask):

        corners = cv2.goodFeaturesToTrack(mask, 4, 0.01, 10)
        corners = np.int0(corners)
        return np.float32(corners.reshape(-1,2))


    def __find_new_corners(self, v, high_value=600):

        idx = np.zeros(v.shape)
        v_copy = v.copy()
        x = v_copy[:,0]
        x_sorted = np.sort(v_copy[:,0])
        y = v_copy[:,1]
        x_array = []
        for element in x:
            for i, sorted_element in enumerate(x_sorted):
                if element==sorted_element:
                    x_array.append(i)
        idx[:,0] = x_array
        idx[:,1] = y.argsort()
        return np.float32((idx>1)*high_value)


    def run(self, img_path):

        """

            1) A IMAGEM É LIDA EM ESCALA DE CINZA;
            2) O GAUSSIAN BLUR É EXECUTADO PARA REMOVER QUALQUER RUÍDO DISPONÍVEL;
            3) O LIMIAR ADAPTATIVO É APLICADO À IMAGEM BORRADA;
            4) ENCONTRAMOS O CONTORNO CUJA ÁREA É MAIOR, POIS REPRESENTA O QUADRO DO DOCUMENTO;
            5) COM O CONTORNO ENCONTRADO NA ÚLTIMA ETAPA, CRIAMOS UMA MÁSCARA COM A ÁREA REPRESENTADA PELA MOLDURA;
            6) USANDO ESTA MÁSCARA, PODEMOS ENCONTRAR OS QUATRO CANTOS DO DOCUMENTO DE IDENTIFICAÇÃO NA IMAGEM ORIGINAL;
            7) PORTANTO, APLICAMOS O DEWARPING E TRANSFORMAMOS NOSSA PERSPECTIVA, DE FORMA QUE OS QUATRO CANTOS DO DOCUMENTO SEJAM IGUAIS À IMAGEM.


        """

        # REALIZANDO A LEITURA DA IMAGEM EM ESCALA DE CINZA
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        while max(img.shape) > 2000:
            img = cv2.pyrDown(img)

        # REALIZANDO O PRÉ PROCESSAMENTO DA IMAGEM COM
        preproc_img = self.__preprocess_blur_threshold_img(img)

        # ENCONTRAMOS O CONTORNO CUJA ÁREA É MAIOR, POIS REPRESENTA O QUADRO DO DOCUMENTO;
        contour = self.__get_contour(preproc_img)

        # COM O CONTORNO ENCONTRADO NA ÚLTIMA ETAPA, CRIAMOS UMA MÁSCARA COM A ÁREA REPRESENTADA PELA MOLDURA;
        mask = self.__generate_mask(img, contour)

        # USANDO ESTA MÁSCARA, PODEMOS ENCONTRAR OS QUATRO CANTOS DO DOCUMENTO DE IDENTIFICAÇÃO NA IMAGEM ORIGINAL;
        pts1 = self.__find_corners(mask)
        pts2 = self.__find_new_corners(pts1, high_value=self.__output_size)

        # APLICAMOS O DEWARPING E TRANSFORMAMOS NOSSA PERSPECTIVA, DE FORMA QUE OS QUATRO CANTOS DO DOCUMENTO SEJAM IGUAIS À IMAGEM.
        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(img, M, (self.__output_size, self.__output_size))

        return dst