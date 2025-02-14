import logging
import os


def setup_logger():
    """ Configura e retorna um objeto de log. """
    logger = logging.getLogger('spotify_personalized_daily_drive')
    logger.setLevel(logging.DEBUG)

    # Cria handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('app.log')
    c_handler.setLevel(logging.WARNING)
    f_handler.setLevel(logging.DEBUG)

    # Cria formatos e adiciona aos handlers
    format = logging.Formatter("[%(asctime)s] %(name)s - %(levelname)s: '%(message)s'")
    c_handler.setFormatter(format)
    f_handler.setFormatter(format)

    # Adiciona os handlers no log
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


logger = setup_logger()

if __name__ == "__main__":
    logger.debug("Isso é uma mensagem de depuração.")
    logger.info("Isso é uma informação.")
    logger.warning("Isso é um aviso!")
    logger.error("Isso é um erro!")
    logger.critical("Isso é um erro crítico!")