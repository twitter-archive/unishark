import logging
import unishark

formatter = logging.Formatter('%(levelname)s: %(message)s')
handler = logging.StreamHandler(stream=unishark.out)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)