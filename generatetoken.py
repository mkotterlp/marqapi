import requests
import webbrowser
import urllib.parse
import json
import os

# Client credentials
client_id = 'dC50593I67kJo52vE2x98XoeSP_B7rWk48Hv7LNM'
client_secret = 'Rv7E8Iu0UnFsu0NbkGv2qyZwxJuBowVLUDPxpFqXhkNpB-LCskTvjyRcQx1K8qJHvwXSvVc56luTOgO7yj4z'
redirect_uri = 'https://app.marq.com/oauth2/clients/dC50593I67kJo52vE2x98XoeSP_B7rWk48Hv7LNM/redirect'
scopes = ['project.content', 'offline_access']

def open_authorization_url(client_id, redirect_uri, scopes):
    encoded_scope_string = urllib.parse.quote_plus(' '.join(scopes))
    encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')
    authorization_url = f"https://app.marq.com/oauth2/authorizeAccount?response_type=code&client_id={client_id}&scope={encoded_scope_string}&redirect_uri={encoded_redirect_uri}"
    webbrowser.open(authorization_url)

def get_tokens(client_id, client_secret, code, redirect_uri):
    token_url = 'https://users.app.marq.com/oauth2/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(token_url, data=token_data)
    if response.status_code == 200:
        print("Tokens successfully retrieved.")
        return response.json()  # Returns the entire token response
    else:
        print(f"Failed to get tokens: {response.status_code}, {response.text}")
        return None

def save_tokens_to_file(tokens):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, 'tokens.json')
    with open(file_path, 'w') as token_file:
        json.dump(tokens, token_file, indent=4)
    print(f"Tokens saved to {file_path}")

# Main execution
if __name__ == "__main__":
    open_authorization_url(client_id, redirect_uri, scopes)
    # You'll manually copy the authorization code from the redirect URI
    authorization_code = input("Enter the authorization code: ")
    token_response = get_tokens(client_id, client_secret, authorization_code, redirect_uri)
    if token_response:
        save_tokens_to_file(token_response)
    else:
        print("Failed to obtain tokens.")
