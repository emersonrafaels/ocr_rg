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
    def view_image(img_atual, nome_janela="IMAGEM ATUAL"):

        """

            FUNÇÃO PARA VISUALIZAÇÃO DE UMA IMAGEM.
            A VISUALIZAÇÃO UTILIZA O WINDOWFRAME DO OPENCV - FUNÇÃO IMSHOW.


            # Arguments
                img_atual            - Required : Imagem a ser visualizada (Object)
                nome_janela          - Required : Nome que será usada como
                                                  título da janela de exibição
                                                  da imagem (String)
            # Returns

        """

        try:
            # MOSTRANDO IMAGEM ATUAL
            cv2.imshow(nome_janela, img_atual)

            # AGUARDA A AÇÃO DO USUÁRIO DE FECHAR A JANELA DE IMAGEM
            cv2.waitKey(0)

            # DESTRUINDO A JANELA DE IMAGEM
            cv2.destroyAllWindows()
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
            x1 = bounding_positions['x1']
            y1 = bounding_positions['y1']
            x2 = bounding_positions['x2']
            y2 = bounding_positions['y2']

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            return img
        except Exception as ex:
            print(ex)
            return img


    @staticmethod
    def put_text_image(texto, x, y, img, fonte, tamanho_texto=32, cor=(0, 0, 255)):

        try:
            fonte = ImageFont.truetype(fonte, tamanho_texto)

            img_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            draw.text((x, y - tamanho_texto), texto, font=fonte, fill=cor)
            img = np.array(img_pil)
        except Exception as ex:
            print(ex)

        return img
