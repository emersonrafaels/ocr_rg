from datetime import datetime

import pandas as pd

from UTILS.conectores_db.main import conectores
from MODELS.final_function import model_selection
from UTILS.generic_functions import get_date_time_now


"-----------------------------------QUERY COM PARAMS-----------------------------------------------"

# DEFININDO OS PARÂMETROS DE CONEXÃO
caminho_bd_bds = r"TESTS\DB_RG_OCR_TESTS.db"
ssql_bds = "SELECT * FROM TBL_PIXEL_TESTS WHERE DT_HR_INICIO LIKE ?"
params_bds = ("10/05/2022%",)
tipo_query_bds = "SELECT"

dt_hr_inicio = get_date_time_now("%d/%m/%Y %H:%M:%S")

# EXECUTANDO A QUERY E OBTENDO O RESULTADO
_, result, result_columns = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)
df_test = pd.DataFrame(result, columns=result_columns)

list_result = []

ID_IMAGEM = "Jose_Clerton"

df_image = df_test[df_test["ID_IMAGEM"] == ID_IMAGEM]

# OBTENDO A LISTA DE RESULTADOS (CAMPO, PERCENT)
for idx, row in df_image.iterrows():

    result_model = {value.replace("_PERCENT", ""): (row[value.replace("_PERCENT", "")],
                                                    row[value]) for value in df_image.columns if value.find("PERCENT")!=-1}

    result["TIPO_MODELO"] = df_image.loc[idx, "TIPO_MODELO"]
    result["DT_HR_INICIO"] = df_image.loc[idx, "DT_HR_INICIO"]
    result["DT_HR_FIM"] = df_image.loc[idx, "DT_HR_FIM"]

    list_result.append(result_model)


dt_hr_fim = get_date_time_now("%d/%m/%Y %H:%M:%S")

result_final_function = model_selection(list_result)
result_final_function["TIPO_MODELO"] = "MODELO FINAL"
result_final_function["DT_HR_INICIO"] = dt_hr_inicio
result_final_function["DT_HR_FIM"] = dt_hr_fim
result_final_function["NOME"] = dt_hr_inicio
result_final_function["DATA_NASC"] = dt_hr_fim

print("-"*50)
print(result_final_function)