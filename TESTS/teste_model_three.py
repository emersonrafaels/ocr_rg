from MODELS import main_model_three

import pandas as pd

input_model = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\Eliana_Donizete_verso.png'

gab = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\GABARITO.xlsx'

df_gab = pd.read_excel(gab, engine="openpyxl")

# 1 - CHAMANDO A FUNÇÃO ORQUESTRADORA PARA OCR - MODELO 3
info_doc_model_tree = main_model_three.main_model(input_model)

# 2 - LENDO O RESULTADO
print(info_doc_model_tree)