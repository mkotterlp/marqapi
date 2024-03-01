import requests
import time
import json
import os


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


def save_new_tokens(access_token, refresh_token):
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, 'tokens.json')
    with open(file_path, 'w') as token_file:
        json.dump(tokens, token_file, indent=4)
    print(f"Tokens saved to {file_path}")

def refresh_access_token(refresh_token):
    url = "https://users.app.Marq.com/oauth2/refreshToken"
    payload = {"refresh_token": refresh_token, "client_id": client_id, "client_secret": client_secret, "grant_type": "refresh_token"}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        token_response = response.json()
        new_access_token = token_response.get('access_token')
        new_refresh_token = token_response.get('refresh_token')
        # Save the new tokens immediately
        save_new_tokens(new_access_token, new_refresh_token)
        return new_access_token, new_refresh_token
    else:
        print(f"Failed to refresh token: {response.status_code}, {response.text}")
        return None, None

# Main execution
try:
    # Assume tokens are initially obtained and saved in 'tokens.json'
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')

    # Example of using the tokens for an API call
    exportresponse = create_export_job(access_token, project_id, file_type, dpi)
    if exportresponse:
        self_uri = exportresponse['selfUri']
        print("Export job created, waiting for completion...")
        final_url = wait_for_job_completion(access_token, self_uri, 5, 60)
        if final_url:
            print(f"Export completed. Download URL: {final_url}")
        else:
            print("Failed to complete export. Attempting to refresh token...")
            # Refresh the token if the export job fails due to token expiration
            access_token, refresh_token = refresh_access_token(refresh_token)
            if access_token and refresh_token:
                # Retry the export job with the new access token
                exportresponse = create_export_job(access_token, project_id, file_type, dpi)
                if exportresponse:
                    self_uri = exportresponse['selfUri']
                    print("Retry: Export job created, waiting for completion...")
                    final_url = wait_for_job_completion(access_token, self_uri, 5, 60)
                    if final_url:
                        print(f"Export completed after refresh. Download URL: {final_url}")
                    else:
                        print("Failed to complete export even after token refresh.")
            else:
                print("Token refresh failed. Exiting.")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
