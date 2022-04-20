import datetime

from UTILS.conectores_db.main import conectores
from UTILS.generic_functions import get_date_time_now
from MODELS.main_model_four import main_model
from UTILS.generic_functions import create_path, get_files_directory


def get_processed_files(dir_db_results):

    list_result = []

    try:
        caminho_bd_bds = dir_db_results
        ssql_bds = "SELECT ID_IMAGEM FROM TBL_PIXEL_TESTS WHERE TIPO_MODELO LIKE '%MODELO QUATRO%'"
        params_bds = (None,)
        tipo_query_bds = "SELECT"

        result_query = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)

        # FORMATANDO O RESULTADO OBTIDO
        list_result = [value[0] for value in result_query[1]]

    except Exception as ex:
        print(ex)

    return list_result


def get_shortened_name(name_file):

    try:
        return name_file.split("\\")[-1].split(".")[0]
    except Exception as ex:
        return datetime.datetime.now().strftime("%H%M%S%s%d%Y")


def insert_processed_image(dir_db_results, image, input_result,
                           dt_hr_inicio, dt_hr_fim):

    for idx, result in enumerate(input_result):

        # OBTÉM O NOME ENCURTADO
        name_short = get_shortened_name(image)

        caminho_bd_bds = dir_db_results
        ssql_bds = """INSERT INTO TBL_PIXEL_TESTS (
                                    ID_IMAGEM,
                                    TEXTO_OCR,
                                    RG,
                                    DATA_EXPED,
                                    NOME,
                                    NOME_PAI,
                                    NOME_MAE,
                                    DATA_NASC, 
                                    CPF,
                                    CIDADE_NASC,
                                    ESTADO_NASC,
                                    CIDADE_ORIGEM,
                                    ESTADO_ORIGEM,
                                    TIPO_MODELO, 
                                    DT_HR_INICIO,
                                    DT_HR_FIM
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        params_bds = (str(name_short), result[0],
                      ",".join(result[-1]["RG"]), result[-1]["DATA_EXPED"],
                      result[-1]["NOME"],
                      result[-1]["NOME_PAI"],
                      result[-1]["NOME_MAE"],
                      result[-1]["DATA_NASC"],
                      ",".join(result[-1]["CPF"]),
                      result[-1]["CIDADE_NASC"],
                      result[-1]["ESTADO_NASC"],
                      result[-1]["CIDADE_ORIGEM"],
                      result[-1]["ESTADO_ORIGEM"],
                      "MODELO QUATRO - RODADA {}".format(idx),
                      dt_hr_inicio, dt_hr_fim)
        tipo_query_bds = "INSERT"

        result_query = conectores().execute_query_sqlite(caminho_bd_bds, ssql_bds, params_bds, tipo_query_bds)

    return result_query


def orchestra_test(input_dir, output_dir, dir_db_results):

    # CRIANDO O DIRETÓRIO QUE RECEBERÁ AS IMAGENS PROCESSADAS
    validador = create_path(output_dir)

    if validador:

        # OBTENDO TODAS AS IMAGENS DA PASTA
        lista_imagens = get_files_directory(input_dir, [".png", "jpg"])

        # INICIANDO O CONTADOR
        contador = 1

        # OBTENDO AS IMAGENS JÁ PROCESSADAS
        imagens_anterior_processadas = get_processed_files(dir_db_results)

        # PERCORRENDO TODAS AS IMAGENS PARA OCR
        for image in lista_imagens:

            # VERIFICANDO SE A IMAGEM JÁ FOI PROCESSADA
            if not get_shortened_name(image) in []:
                print("IMAGEM ATUAL: {}".format(image))
                dt_hr_inicio = get_date_time_now("%d/%m/%Y %H:%M:%S")

                result_image = main_model(image)

                dt_hr_fim = get_date_time_now("%d/%m/%Y %H:%M:%S")

                _ = insert_processed_image(dir_bd_results, image, result_image,
                                           dt_hr_inicio, dt_hr_fim)


input_dir = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\Roberto_Guedes_Verso.png'
output_dir = r'RESULTADOS/MODEL_THREE'
dir_bd_results = r'DB_RG_OCR_TESTS.db'

# CHAMANDO O ORQUESTRADOR DE TESTES
orchestra_test(input_dir, output_dir, dir_bd_results)