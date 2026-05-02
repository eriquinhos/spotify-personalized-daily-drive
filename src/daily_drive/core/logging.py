import logging


def setup_logger(
    name: str = "spotify_personalized_daily_drive",
    log_file: str = "app.log",
    console_level: int = logging.WARNING,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    """Configura e retorna um logger com handler de console e de arquivo."""

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s: '%(message)s'"
    )

    # Handler de console
    c_handler = logging.StreamHandler()
    c_handler.setLevel(console_level)
    c_handler.setFormatter(formatter)
    logger.addHandler(c_handler)

    # Handler de arquivo
    f_handler = logging.FileHandler(log_file, encoding="utf-8")
    f_handler.setLevel(file_level)
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)

    return logger


if __name__ == "__main__":
    logger = setup_logger()

    logger.debug("Isso é uma mensagem de depuração.")
    logger.info("Isso é uma informação.")
    logger.warning("Isso é um aviso!")
    logger.error("Isso é um erro!")
    logger.critical("Isso é um erro crítico!")
