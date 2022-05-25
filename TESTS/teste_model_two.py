import datetime

from UTILS.conectores_db.main import conectores
from UTILS.generic_functions import get_date_time_now
from MODELS.main_model_two import main_model
from UTILS.generic_functions import create_path, get_files_directory


def get_processed_files(dir_db_results):

    list_result = []

    try:
        caminho_bd_bds = dir_db_results
        ssql_bds = "SELECT ID_IMAGEM FROM TBL_PIXEL_TESTS WHERE TIPO_MODELO LIKE '%MODELO DOIS%'"
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
                                                    RG, RG_PERCENT,
                                                    DATA_EXPED, DATA_EXPED_PERCENT,
                                                    NOME, NOME_PERCENT,
                                                    NOME_PAI, NOME_PAI_PERCENT,
                                                    NOME_MAE, NOME_MAE_PERCENT,
                                                    DATA_NASC, DATA_NASC_PERCENT,
                                                    CPF, CPF_PERCENT,
                                                    CIDADE_NASC, CIDADE_NASC_PERCENT,
                                                    ESTADO_NASC, ESTADO_NASC_PERCENT,
                                                    CIDADE_ORIGEM, CIDADE_ORIGEM_PERCENT,
                                                    ESTADO_ORIGEM, ESTADO_ORIGEM_PERCENT,
                                                    TIPO_MODELO, 
                                                    DT_HR_INICIO,
                                                    DT_HR_FIM
                                                )
                                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        params_bds = (str(name_short), result[0],
                      result[-1]["RG"][0], result[-1]["RG"][1],
                      result[-1]["DATA_EXPED"][0], result[-1]["DATA_EXPED"][1],
                      result[-1]["NOME"][0], result[-1]["NOME"][1],
                      result[-1]["NOME_PAI"][0], result[-1]["NOME_PAI"][1],
                      result[-1]["NOME_MAE"][0], result[-1]["NOME_MAE"][1],
                      result[-1]["DATA_NASC"][0], result[-1]["DATA_NASC"][1],
                      result[-1]["CPF"][0], result[-1]["CPF"][1],
                      result[-1]["CIDADE_NASC"][0], result[-1]["CIDADE_NASC"][1],
                      result[-1]["ESTADO_NASC"][0], result[-1]["ESTADO_NASC"][1],
                      result[-1]["CIDADE_ORIGEM"][0], result[-1]["CIDADE_ORIGEM"][1],
                      result[-1]["ESTADO_ORIGEM"][0], result[-1]["ESTADO_ORIGEM"][1],
                      "MODELO DOIS - RODADA {}".format(idx),
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


input_dir = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\Jose_Clerton.png'
output_dir = r'RESULTADOS/MODEL_THREE'
dir_bd_results = r'DB_RG_OCR_TESTS.db'

# CHAMANDO O ORQUESTRADOR DE TESTES
orchestra_test(input_dir, output_dir, dir_bd_results)