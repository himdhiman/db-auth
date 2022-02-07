import os, requests, json, ast, cloudinary.uploader


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


def create_user_notifcation(email, username, create=True):
    endpoint = os.environ.get("NOTIFICATION_SERVER")
    if create:
        requests.post(endpoint + "addUser/", data={"user": email, "username": username})
    else:
        requests.post(
            endpoint + "deleteUser/", data={"user": email, "username": username}
        )
    return
