from flask import Flask, request, jsonify
import uuid
from google.cloud import storage

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_page():
    # Ensure that you have authenticated and set up Google Cloud Storage properly.
    client = storage.Client()
    bucket = client.bucket('runapps_default-wwdwyp')

    # Extract data from the POST request
    data = request.json
    title = data.get('title', 'Default Title')
    description = data.get('description', 'Default Description')
    content = data.get('content', 'Default Content')
    image_url = data.get('image_url', '')

    # Generate a unique filename for the HTML file
    filename = f"{uuid.uuid4()}.html"

    # Construct the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta property="og:url" content="https://storage.googleapis.com/{bucket.name}/{filename}" />
        <meta property="og:type" content="website" />
        <meta property="og:title" content="{title}" />
        <meta property="og:description" content="{description}" />
        <meta property="og:image" content="{image_url}" />
    </head>
    <body>
        <h1>{title}</h1>
        <p>{content}</p>
    </body>
    </html>
    """

    # Upload the HTML content to Google Cloud Storage
    blob = bucket.blob(filename)
    blob.upload_from_string(html_content, content_type='text/html')
    blob.make_public()  # Make the file publicly accessible

    # Return the URL to the generated page
    return jsonify({'url': blob.public_url})
