import json


def read_config(): 
    '''
        Reading the default configurations
    '''
    CONFIG_PATH="auto-email-service/config/email-config.json"
    with open(CONFIG_PATH,'r') as f:
        config = json.load(f)
    
    #print("Reading config from file: {}".format(CONFIG_PATH))
    return config