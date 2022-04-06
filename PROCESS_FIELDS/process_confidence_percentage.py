def get_confidence_percentage(list_values, info_ocr_image_data):

    # INICIANDO O VALOR DO PERCENTUAL DE CONFIANÇA
    result_confidence_percentage = []

    # VERIFICANDO SE O LIST_VALUES É UMA STRING OU LISTA
    if not isinstance(list_values, list):
        list_values = [list_values]

    for value_text in list_values:

        # OBTENDO O VALOR NO DATAFRAME DE INFO_OCR
        value_conf_percentage = info_ocr_image_data[info_ocr_image_data["text"].str.contains(value_text,
                                                                                             na=False)]["conf"].values[0]

        # REALIZANDO O APPEND NO RESULTADO FINAL
        result_confidence_percentage.append([value_text, value_conf_percentage])

    return result_confidence_percentage