import unidecode

import pandas as pd


# OBTENDO A SEGUNDA BASE DE NOMES
dir_data_last_names_country = r'C:\Users\Emerson\Desktop\brainIAcs\OCR_RG\RG_OCR\BD_OCR_RG\DATASET_NOMES_GENERO.csv'
df_2 = pd.read_csv(dir_data_last_names_country, sep=",", encoding="cp1252")

dir_data_last_names = r'C:\Users\Emerson\Desktop\UFABC\Cursos\Python\Analytics\NLP\BASES\DATA_HARVARD_NAMES_GENDER\brazilNamesGenderRatio.csv'
df_1 = pd.read_csv(dir_data_last_names, sep=",", encoding="cp1252")
df_1 = df_1[["firstName", "female"]]
df_1.columns = ["NOME", "SEXO"]
df_1.replace({0: "M", 1: "F"}, inplace=True)

df_result = df_1.append(df_2)

df_result.to_csv("DATASET_NOMES_GENERO.csv", index=None, encoding="cp1252")