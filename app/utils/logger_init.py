import logging


logging.basicConfig(
        level=logging.DEBUG,
        filename='main_log.log',
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s'
    )
logger = logging.getLogger("proof_of_click_app")
logger.setLevel(logging.DEBUG)
