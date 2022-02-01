import json, ast, cloudinary.uploader


def convert_to_list(data):
    try:
        return_data = ast.literal_eval(data)
    except:
        qery_list = json.dumps(data)
        return_data = ast.literal_eval(qery_list)
    return return_data


def delete_cloudinary_image(public_id):
    cloudinary.uploader.destroy(public_id, resource_type="image")
    return
