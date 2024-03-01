import requests
import webbrowser
import urllib.parse
import time

# Client credentials
client_id = 'dC50593I67kJo52vE2x98XoeSP_B7rWk48Hv7LNM'
client_secret = 'Rv7E8Iu0UnFsu0NbkGv2qyZwxJuBowVLUDPxpFqXhkNpB-LCskTvjyRcQx1K8qJHvwXSvVc56luTOgO7yj4z'
redirect_uri = 'https://app.marq.com/oauth2/clients/dC50593I67kJo52vE2x98XoeSP_B7rWk48Hv7LNM/redirect'
scopes = ['project.content', 'offline_access']
savedtoken = 'oauth2/account-CcqvkA==-1kFTmunFfiaQexta6r8oApU4a-THYbJWIg3H2awbsea5GnoriZ7RPzzLcGnQkdVyMjDiO-TNR_LNvSDErjbW'

def open_authorization_url(client_id, redirect_uri, scopes):
    scope_string = ' '.join(scopes)
    encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')
    authorization_url = f"https://app.marq.com/oauth2/authorizeAccount?response_type=code&client_id={client_id}&scope={scope_string}&redirect_uri={encoded_redirect_uri}"
    webbrowser.open(authorization_url)

def refresh_access_token(refresh_token, client_id, client_secret):
    url = "https://users.app.Marq.com/oauth2/refreshToken"
    
    payload = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        token_response = response.json()
        new_access_token = token_response.get('access_token')
        new_refresh_token = token_response.get('refresh_token')
        expires_in = token_response.get('expires_in')  # The expiration time in milliseconds
        
        # Update your storage mechanism here with the new_access_token, new_refresh_token, and expires_in
        print("New access token: ", new_access_token)
        print("New refresh token: ", new_refresh_token)
        print("Expires in (ms): ", expires_in)
        
        return new_access_token, new_refresh_token, expires_in
    else:
        print(f"Failed to refresh token: {response.status_code}, {response.text}")
        return None, None, None

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
        token_response = response.json()
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        print(f"Token Response: {token_response}")
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")
        return access_token, refresh_token
    else:
        print(f"Failed to get token: {response.status_code}, {response.text}")
        try:
            error_info = response.json()
            print("Detailed error info:", error_info)
        except ValueError:
            print("Failed to decode error response.")
        return None

def list_projects(token, user_id, limit=20):
    project_url = f'https://api.marq.com/v1/users/{user_id}/projects?limit={limit}'
    headers = {'Authorization': f'Bearer {token}'}
    print(headers)
    response = requests.get(project_url, headers=headers)
    if response.status_code == 200:
        projects = response.json()
        for project in projects: 
            print(f"Project ID: {project['id']}, Project Name: {project['title']}")
        return projects
    else:
        print(f"Failed to list projects: {response.status_code}, {response.text}")
        return None

def create_export_job(token, project_id, file_type, dpi):
    export_url = f'https://api.marq.com/v1/projects/{project_id}/exportJobs'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print(headers)
    data = {
        'fileType': file_type,
        'dpi': dpi
    }
    response = requests.post(export_url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()  # Return the full JSON response
    else:
        print(f"Failed to create export job: {response}")
        return None



def wait_for_job_completion(token, self_uri, interval=5, timeout=60):
    """
    Polls the export job status every `interval` seconds until the job is completed,
    then returns the export URL. Uses the job's selfUri directly.
    """
    start_time = time.time()  # Record the start time
    while True:
        if time.time() - start_time > timeout:
            print("Maximum try duration exceeded. Exiting.")
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        response = requests.get(self_uri, headers=headers)
        if response.status_code == 200:
            job_status = response.json()
            print(f"Current job status: {job_status['status']}...")  # Debugging print
            if job_status['status'].lower() == 'ready':
                return job_status.get('exportUri')
            elif job_status['status'].lower() in ['failed', 'error']:
                print("Export job failed.")
                return None
        else:
            print(f"Failed to get export job status: {response.status_code}, {response.text}")
            return None
        
        time.sleep(interval)



# Project ID and export parameters
project_id = '7bd4bebc-ce96-40c0-a4fc-8ed6a5e123cc'
file_type = 'PDF'  
dpi = '300'  

# Main execution
try:
    open_authorization_url(client_id, redirect_uri, scopes)
    authorization_code = input("Enter the authorization code (or press Enter to open authorization URL): ")
    access_token, refresh_token = get_tokens(client_id, client_secret, authorization_code, redirect_uri)
    if not access_token:
          print("Token retrieval failed. Exiting.")
          exit(1)
    refresh_access_token(refresh_token, client_id, client_secret)
    exportresponse = create_export_job(access_token, project_id, file_type, dpi)
    if exportresponse:
        self_uri = exportresponse['selfUri'] 
        print("Export job created, waiting for completion...")
        final_url = wait_for_job_completion(access_token, self_uri, 5, 60)  # Pass interval and timeout correctly
        if final_url:
            print(f"Export completed. Download URL: {final_url}")
        else:
            print("Failed to complete export.")
except Exception as e:
    print(f"Error: {str(e)}")
