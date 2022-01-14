from os import access
import requests

class Github:

    @staticmethod
    def validate(auth_token):
        baseURL_AcessToken = "https://github.com/login/oauth/access_token"
        baseURLData = "https://api.github.com/user"
        baseURLMail = "https://api.github.com/user/emails"
        send_data = {
            "client_id" : "4070334dbe20cf539952",
            "client_secret" : "0abb240c2d9c8b063e35a8f812b48107a2c4aa0b",
            "code" : auth_token,
            "redirect_uri" : ""
        }
        try:
            res = requests.post(baseURL_AcessToken, data = send_data, headers = {
                "Accept": "application/json"
            })
            access_token = res.json()["access_token"]
            headers = {
                "Authorization" : f"token {access_token}"
            }
            response = requests.get(baseURLData, headers = headers)
            email_response = requests.get(baseURLMail, headers=headers)
            if "id" in response.json():
                send_data = {}
                for i in email_response.json():
                    if i["primary"]:
                        send_data["email"] = i["email"]
                        break
                send_data["username"] = response.json()["login"]
                send_data["name"] = response.json()["name"]
                return send_data
            else:
                return "The token is either invalid or has expired"
        except:
            return "The token is either invalid or has expired"