"""

    FUNÇÕES PARA VISUALIZAÇÃO DA IMAGEM.

    # Arguments
        object                  - Required : Imagem para leitura/visualização (String | Object)
    # Returns


"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "03/07/2021"


from inspect import stack

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import ImageFont, ImageDraw, Image


class image_view_functions():

    """

        FUNÇÕES PARA LEITURA E VISUALIZAÇÃO DA IMAGEM.

        # Arguments
            object                  - Required : Imagem para leitura/visualização (String | Object)
        # Returns


    """

    def __init__(self):

        self.texto_fonte = r'FONTES/calibri.ttf'


    @staticmethod
    def view_image(image, window_name="IMAGEM ATUAL"):

        """

            FUNÇÃO PARA VISUALIZAÇÃO DE UMA IMAGEM.
            A VISUALIZAÇÃO UTILIZA O WINDOWFRAME DO OPENCV - FUNÇÃO IMSHOW.


            # Arguments
                image                - Required : Imagem a ser visualizada (Object)
                window_name          - Required : Nome que será usada como
                                                  título da janela de exibição
                                                  da imagem (String)
            # Returns

        """

        try:
            # MOSTRANDO IMAGEM ATUAL
            cv2.imshow(window_name, image)

            # AGUARDA A AÇÃO DO USUÁRIO DE FECHAR A JANELA DE IMAGEM
            cv2.waitKey(0)

            # DESTRUINDO A JANELA DE IMAGEM
            cv2.destroyAllWindows()
        except Exception as ex:
            print(ex)


    @staticmethod
    def view_image_with_coordinates(image, window_name="IMAGEM ATUAL"):

        """

            FUNÇÃO PARA VISUALIZAÇÃO DE UMA IMAGEM.
            A VISUALIZAÇÃO UTILIZA O WINDOWFRAME DO PYPLOT - FUNÇÃO IMSHOW.


            # Arguments
                image                - Required : Imagem a ser visualizada (Object)
                window_name          - Required : Nome que será usada como
                                                  título da janela de exibição
                                                  da imagem (String)
            # Returns

        """

        try:
            # MOSTRANDO IMAGEM ATUAL
            plt.imshow(image)
            plt.title(window_name)

            # AGUARDA A AÇÃO DO USUÁRIO DE FECHAR A JANELA DE IMAGEM
            plt.show()

        except Exception as ex:
            print(ex)


    @staticmethod
    def create_bounding_box(img, bounding_positions, color=(0, 255, 0)):

        """

            FUNÇÃO PARA CRIAR UMA CAIXA DE TEXTO SOBRE UMA IMAGEM.
            RECEBE AS POSIÇÕES LEFT, TOP (POSIÇÕES DE INICIO DA CAIXA)
            RECEBE A LARGURA E ALTURA, PARA COMPLETAR A CAIXA.


            # Arguments
                img                  - Required : Imagem a ser aplicada a caixa (Object)
                bounding_positions   - Required : Dict contendo as posições (Dict)
                color                - Optional : Cor do contorno da caixa (Tuple)
            # Returns
                x                    - Required : Posição left (Integer)
                y                    - Required : Posição Top (Integer)
                img                   - Required : Imagem após aplicação da caixa (Object)

        """

        try:
            # OBTENDO AS POSIÇÕES PARA O BOUNDING BOX
            x1 = bounding_positions['x1']
            y1 = bounding_positions['y1']
            x2 = bounding_positions['x2']
            y2 = bounding_positions['y2']

            # DESENHNADO O BOUNDING BOX (RETANGULAR SOBRE A IMAGEM)
            # COR: color
            # ESPESSURA: 2
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            return img
        except Exception as ex:
            print(ex)
            return img


    @staticmethod
    def put_text_image(img, text, x, y, font,
                       text_size=32, color=(0, 0, 255)):

        """

            FUNÇÃO PARA ESCREVER UM TEXTO SOBRE UMA IMAGEM.
            RECEBE AS POSIÇÕES X, Y (POSIÇÕES DE INICIO DA ESCRITA)
            RECEBE A LARGURA E ALTURA, PARA COMPLETAR A CAIXA.


            # Arguments
                img                  - Required : Imagem a ser aplicada o texto (Object)
                text                 - Required : Texto a ser escrito (String)
                x                    - Required : Posição x de início do texto (Integer)
                y                    - Required : Posição y de início do texto (Integer)
                font                 - Required : Fonte desejada para a letra (Object)
                text_size            - Optional : Tamanho da letra (Integer)
                color                - Optional : Cor da letra em formato RGB(Tuple)
            # Returns
                x                    - Required : Posição left (Integer)
                y                    - Required : Posição Top (Integer)
                img                  - Required : Imagem após aplicação da caixa (Object)

        """

        try:
            font = ImageFont.truetype(font, text_size)

            img_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            draw.text((x, y), text, font=font, fill=color)
            img = np.array(img_pil)
        except Exception as ex:
            print(ex)

        return img
