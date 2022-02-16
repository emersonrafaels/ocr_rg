from dynaconf import settings
import os

# OBTENDO O DIRETÓRIO CONTENDO O BANCO DE DADOS
DIR_BD_OCR = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), settings.DIR_BD_OCR)

DIR_DATA_LAST_NAMES = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), settings.DIR_DATA_LAST_NAMES)

DIR_DATA_FIRST_NAMES_GENDER = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), settings.DIR_DATA_FIRST_NAMES_GENDER)

DIR_DATA_ORGAOS_EMISSOR = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), settings.DIR_DATA_FIRST_NAMES_GENDER)