import json, ast

def convert_to_list(data):
    try:
        return_data = ast.literal_eval(data)
    except:
        qery_list = json.dumps(data)
        return_data = ast.literal_eval(qery_list)
    return return_data