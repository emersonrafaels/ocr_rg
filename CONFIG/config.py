import os

from dynaconf import settings
import pandas as pd


# OBTENDO O DIRETÓRIO CONTENDO O BANCO DE DADOS
DIR_BD_OCR = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), settings.DIR_BD_OCR)

# OBTENDO O DIRETÓRIO CONTENDO O BANCO DE DADOS CONTENDO SOBRENOMES
DIR_DATA_LAST_NAMES = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), settings.DIR_DATA_LAST_NAMES)

# OBTENDO O DIRETÓRIO CONTENDO O BANCO DE DADOS CONTENDO NOMES E GÊNEROS
DIR_DATA_FIRST_NAMES_GENDER = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), settings.DIR_DATA_FIRST_NAMES_GENDER)

# OBTENDO O DIRETÓRIO CONTENDO O BANCO DE DADOS CONTENDO ORGÃOS EMISSORES
DIR_DATA_ORGAOS_EMISSOR = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), settings.DIR_DATA_ORGAOS_EMISSOR)

# INICIALIZANDO O DATAFRAME DEFAULT DE INFO_OCR
INFO_OCR_DEFAULT = pd.DataFrame([["", 0]], columns=["text", "conf"])