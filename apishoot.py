import requests

class CheminiAPI():
    def __init__(self):
        pass

    def autholizate(self, login, password):
        """
        Receive user token authentication.
        :param login: user login
        :param password: user password
        """
        payload = {
        "username": login,
        "password": password
        }

        token = requests.post(
            "http://localhost:8001/chemini-api/token", 
            headers={"Accept": "application/json"},
            json=payload
            )
        print(token.status_code)
        token = token.json()
        return token

    def get_user_info(self, auth_type:str, token:str):
        """
        Returns information about user from token.
        :param auth_type: authentication type
        :param token: user token
        """
        userinfo = requests.get(
            "http://localhost:8001/chemini-api/userinfo",
            headers={'Accept': 'application/json',
            'Authorization': f'{auth_type} {token}'}
        )
        print(userinfo.status_code)
        user_info = userinfo.json()
        return user_info




if __name__ == '__main__':
    chemini = CheminiAPI()
    token = chemini.autholizate("Damian", "damian")
    print(token)
    _token = token['access_token']
    token_type = token['token_type']

    print(_token, token_type)

    my_info = chemini.get_user_info(token_type, _token)
    print(my_info)
