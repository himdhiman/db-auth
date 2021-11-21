import requests

class Github:
    @staticmethod
    def validate(auth_token):
        baseURLData = "https://api.github.com/user"
        baseURLMail = "https://api.github.com/user/emails"
        try:
            headers = {
                "Authorization" : f"token {auth_token}"
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