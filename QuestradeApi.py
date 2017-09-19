import requests


class QuestradeApi(object):
    # class variables
    URL_AUTH = '' \
        + 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token='

    def __init__(self):
        self.refresh_token = 'put-it-in-file'
        self.access_token = 'will-be-determined'
        self.host = 'will-be-determined'

    def read_refresh_token_file(self):
        with open('refresh_token', 'r') as f:
            first_line = f.readline().strip()
            f.close()
            print('token from file:' + first_line)
        self.refresh_token = first_line

    def write_refresh_token_file(self):
        with open('refresh_token', 'w') as f:
            f.write(self.refresh_token)
            f.close()

    def get_refresh_token(self):
        # get refresh token
        self.read_refresh_token_file()
        url = QuestradeApi.URL_AUTH + self.refresh_token
        print('refresh_token: ' + url)
        response = requests.post(url)
        # print(r.text)
        # print(r.status_code)
        response.raise_for_status()
        response = response.json()
        # print json.dumps(response, indent=4)
        # update values
        self.host = response.get('api_server')
        self.refresh_token = response.get('refresh_token')
        self.access_token = response.get('access_token')
        # write the new refresh back to file
        self.write_refresh_token_file()

    def get_headers(self):
        return {"Authorization": "Bearer " + self.access_token}

    def get_accounts(self):
        url = self.host + 'v1/accounts/'
        print('get_accounts: ' + url)
        response = requests.get(url, headers=self.get_headers())
        return response

    def get_account_balance(self, account_number):
        url = self.host + 'v1/accounts/' + account_number + "/balances/"
        print('get_account_balance: ' + url)
        response = requests.get(url, headers=self.get_headers())
        return response

    def get_account_positions(self, account_number):
        url = self.host + 'v1/accounts/' + account_number + "/positions/"
        print('get_account_positions: ' + url)
        response = requests.get(url, headers=self.get_headers())
        return response
