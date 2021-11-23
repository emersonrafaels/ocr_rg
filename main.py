"""

    SERVIÇO PARA REALIZAÇÃO DE OCR DE UM DOCUMENTO DE IDENTIDADE: RG

    UTILIZA TÉCNICAS DE VISÃO COMPUTACIONAL PARA OBTER:

    1) REGISTRO GERAL (RG)
    2) DATA DE EXPEDIÇÃO
    3) NOME
    4) NOME DO PAI
    5) NOME DA MÃE
    6) DATA DE NASCIMENTO
    7) CPF
    8) CIDADE ORIGEM
    9) ESTADO ORIGEM.

    # Arguments
        object                  - Required : Imagem para aplicação do OCR (Base64 | Path | Numpy Array)
    # Returns
        output_rg               - Required : Textos dos campos do RG após aplicação das
                                             técnicas de pré processamento,
                                             OCR e pós processamento (String)

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "05/11/2021"


from dynaconf import settings

from model_pre_processing import Image_Pre_Processing
from model_ocr import Execute_OCR_RG


def main_ocr_rg(image):

    # DEFININDO A CLASSE DE PRÉ PROCESSAMENTO
    pre_processing = Image_Pre_Processing(settings.BLUR_KSIZE,
                                          settings.THRESHOLD_MAX_COLOR_VALUE,
                                          settings.DILATION_KSIZE,
                                          settings.WIDTH_RESIZE,
                                          settings.OUTPUT_SIZE)

    # DEFININDO AS PROPRIEDADES PARA A LEITURA DA IMAGEM (OCR)
    rg_reader = Execute_OCR_RG(pre_processing)

    # REALIZANDO O FLUXO COMPLETO
    output_rg_field, output_rg_doc = rg_reader.execute_pipeline_ocr(image)

    print("RESULTADO - MODELO 2:")
    print(output_rg_field)
    print("RESULTADO - MODELO 3:")
    print(output_rg_doc)


if __name__ == "__main__":

    caminho_imagem = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\Roberto_Guedes_Verso.png'

    main_ocr_rg(caminho_imagem)

