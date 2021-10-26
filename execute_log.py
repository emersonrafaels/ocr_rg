"""

    FUNÇÕES RESPONSÁVEIS POR CRIAR, CONFIGURAR E REGISTAR LOGS.

    LOGS (LOGGING)

         DOIS LOGS SÃO CONFIGURADOS:
            - MANIPULADORES DE LOGS - ARQUIVO DE LOG (FILE)
            - MANIPULADORES DE LOGS - CONSOLE (TELA DO USUÁRIO) (STREAMHANDLER)

    LOGS (SQLITE)

        REALIZA:
            - CRIAÇÃO DO BANCO DE DADOS, CASO ELE NÃO EXISTA
            - CRIAÇÃO DA TABELA DE LOGS, CASO ELA NÃO EXISTA

    # Arguments

    # Returns
        validator              - Required : Validador de registro do log (Boolean)

"""

__version__ = "1.0"
__author__ = """Emerson V. Rafael (EMERVIN)"""
__data_atualizacao__ = "25/10/2021"

from inspect import stack
from os import path
import logging
import sqlite3

from dynaconf import settings

from UTILS.generic_functions import create_path, get_date_time_now, verify_exists


def configure_logging():

    """

        CONFIGURARANDO OS LOGS (LOGGING).

        DOIS LOGS SÃO CONFIGURADOS:
        - MANIPULADORES DE LOGS - ARQUIVO DE LOG (FILE)
        - MANIPULADORES DE LOGS - CONSOLE (TELA DO USUÁRIO) (STREAMHANDLER)

        # Arguments

        # Returns
            validator              - Required : Validador de registro do log (Boolean)

    """

    # INICIANDO O VALIDADOR DA FUNÇÃO
    validator = False

    # CONFIGURAÇÕES DE LOGS
    try:
        if settings.APPNAME not in settings.LOGGERS.keys():

            # CRIANDO O LOGGER
            logger = logging.getLogger(settings.APPNAME)

            # DEFININDO O LEVEL PARA LOGS
            # LOGS ACIMA DESSE LEVEL SERÃO REGISTRADOS
            logger.setLevel(settings.LOGLEVEL)

            if not len(logger.handles):

                # DEFININDO O LOCAL DO ARQUIVO E LOG
                dir_filename = path.join(settings.DIR_SAVE_LOGS, settings.LOG_FILENAME)

                # CRIANDO OS MANIPULADORES DE LOGS - ARQUIVO DE LOG
                fh = logging.FileHandler(dir_filename)
                fh.setLevel(settings.LOGLEVEL_FILE)

                # CRIANDO OS MANIPULADORES DE LOGS - CONSOLE (TELA DO USUÁRIO)
                ch = logging.StreamHandler()
                ch.setLevel(settings.LOGLEVEL_CONSOLE)

                # CRIANDO OS FORMATOS DE LOGS
                formatter_f = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
                formatter_c = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

                # ATRIBUINDO OS FORMATOS DE LOGS PARA CADA UM DOS HANDLERS
                fh.setFormatter(formatter_f)
                ch.setFormatter(formatter_c)

                # ADICIONANDO OS HANDLERS AO LOGGER (QUE CONTERÁ DOIS HANDLERS)
                logger.addHandler(fh)
                logger.addHandler(ch)

            settings.LOGGERS[settings.APPNAME] = logger

            validator = True

    except Exception as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return validator


def configure_log_bd():

    """

        CONFIGURARANDO OS LOGS (SQLITE).

        REALIZA:
            - CRIAÇÃO DO BANCO DE DADOS, CASO ELE NÃO EXISTA
            - CRIAÇÃO DA TABELA DE LOGS, CASO ELA NÃO EXISTA

        # Arguments

        # Returns
            validator              - Required : Validador de registro do log (Boolean)

    """

    # INICIANDO O VALIDADOR DA FUNÇÃO
    validator = False

    # CONFIGURAÇÕES DE LOGS
    try:
        # REALIZANDO A CONVERSÃO COM O BANCO DE DADOS
        # SE O BANCO DE DADOS NÃO EXISTIR, ELE SERÁ CRIADO AUTOMATICAMENTE

        # DEFININDO OS PARÂMETROS DE CONEXÃO
        dir_bd_logs = path.join(settings.DIR_SAVE_LOGS, settings.DB_LOGS)
        conn = sqlite3.connect(dir_bd_logs)

        # INICIANDO O CURSOR COM O BANCO DE DADOS
        cur = conn.cursor()

        # CRIANDO A TABELA QUE ARMAZENARÁ OS LOGS, CASO ELA NÃO EXISTA
        cur.execute("""CREATE TABLE IF NOT EXISTS tb_log
                    (ID INTEGER PRIMARY KEY AUTOINCREMENT, 
                    log_splunk TEXT, 
                    tipo TEXT, 
                    data REAL, 
                    flag_enviado""")

        conn.commit()

        # REALIZANDO O FECHAMENTO DO CURSOR E DA CONEXÃO
        cur.close()
        conn.close()

        validator = True

    except sqlite3.Error as ex:
        print("ERRO NA FUNÇÃO {} - {}".format(stack()[0][3], ex))

    return validator


def start_log():

    """

        INICIANDO CONFURAÇÃO DOS LOGS (SQLITE).

            - LOGGING
            - BANCO DE DADOS (SQLITE3)

        # Arguments

        # Returns
            validator              - Required : Validador de registro do log (Boolean)

    """

    # INICIANDO O VALIDADOR DA FUNÇÃO
    validator = False

    # VERIFICANDO SE O DIRETÓRIO DE SAVE DOS LOGS EXISTE
    validator = verify_exists(settings.DIR_SAVE_LOGS)

    if validator is False:

        # CRIANDO O DIRETÓRIO DE SAVE DOS LOGS
        validator = create_path(settings.DIR_SAVE_LOG)

    if validator:

        # CONFIGURANDO O USO DA LOGGING (REGISTROS NO ARQUIVO DE LOG E NO CONSOLE)
        validator = configure_logging()

        if validator:

            # CONFIGURANDO O USO DO BANCO DE DADOS (SQLITE)
            validator = configure_log_bd()

    return validator