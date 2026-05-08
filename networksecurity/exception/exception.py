import sys
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details: sys):
        self.error_message = error_message
        _, _, exc_tb = error_details.exc_info()

        self.line_no = exc_tb.tb_lineno
        self.file_name = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return "Error occured in python script [{0}] file: [{1}] line number: [{2}]".format(
            self.error_message, self.file_name, self.line_no
        )
if __name__ == "__main__":
    try:
        logger.logging.info("This is a test log message.")
        a = 1 / 0
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
