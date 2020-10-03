import read_config
import logging

def get_logger(): 
    '''
        Get the logger for logging the data.
    '''

    config = read_config.read_config()

    LOGFILENAME = config['GENERAL']['LOG']['DIR']+config['GENERAL']['LOG']['FILENAME']
    
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',filename=LOGFILENAME,filemode='w',level=logging.INFO, datefmt='%m/%d/%Y %H:%M:%S')

    return logging