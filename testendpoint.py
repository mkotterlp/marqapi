import requests

# Endpoint URL
endpoint_url = "https://marqapi-huoteml7uq-uc.a.run.app/generate"

# Data to send in the POST request
data = {
    "title": "Test Title",
    "description": "Test Description",
    "content": "Test Content",
    "image_url": "https://example.com/image.jpg"
}

# Make the POST request
response = requests.post(endpoint_url, json=data)

# Print the raw response content and headers
print("Status Code:", response.status_code)
print("Headers:", response.headers)
print("Body:", response.text)

# Attempt to parse JSON only if the content type is application/json
if 'application/json' in response.headers.get('Content-Type', ''):
    try:
        print("JSON Response:", response.json())
    except requests.exceptions.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
else:
    print("Response is not in JSON format.")
