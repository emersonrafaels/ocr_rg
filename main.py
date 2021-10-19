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


from model_pre_processing import Image_Pre_Processing
from model_ocr import Execute_OCR_RG


if __name__ == "__main__":

    caminho_imagem = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\MariaEduarda_Copia.png'

    # DEFININDO A CLASSE DE PRÉ PROCESSAMENTO
    pre_processing = Image_Pre_Processing(blur_ksize=5, threshold_value=255, dilation_ksize=5, output_size=600)

    # DEFININDO AS PROPRIEDADES PARA A LEITURA DA IMAGEM (OCR)
    rg_reader = Execute_OCR_RG(pre_processing)

    # REALIZANDO O FLUXO COMPLETO
    output_rg = rg_reader.execute_pipeline_ocr(caminho_imagem)

    print(output_rg)