from PROCESSINGS import functions_pre_processing
from UTILS.image_ocr import ocr_functions
from UTILS.image_read import read_image_gray
from UTILS.image_view import image_view_functions

input_dir = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\Jose_Clerton.png'

# REALIZANDO A LEITURA DA IMAGEM
image = read_image_gray(input_dir)

# APLICANDO O OCR SOBRE A IMAGEM
info_ocr = ocr_functions(type_return_ocr_input="COMPLETO",
                         visualiza_ocr_completo=True).Orquestra_OCR(image)

print(" ".join(info_ocr["text"].astype(str)))

# VISUALIZANDO A IMAGEM INICIAL
# image_view_functions.view_image(image)

# VISUALIZANDO O HISTOGRAMA DA IMAGEM INICIAL
functions_pre_processing.plot_histogram_image(image)

# APLICANDO O THRESHOLD - BINARY
val, thresh = functions_pre_processing.thresh_binary(image, 127)

# VISUALIZANDO A IMAGEM THRESH - BINARY
image_view_functions.view_image(thresh)

# APLICANDO O OCR SOBRE A IMAGEM
info_ocr = ocr_functions(type_return_ocr_input="COMPLETO",
                         visualiza_ocr_completo=True).Orquestra_OCR(thresh)

print(" ".join(info_ocr["text"].astype(str)))
