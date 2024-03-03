from flask import Flask, request, jsonify
import uuid
import os
import requests 
from google.cloud import storage
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/generate', methods=['POST'])
def generate_page():
    try:
        client = storage.Client()
        bucket = client.bucket('runapps_default-wwdwyp')

        data = request.json
        title = data.get('title', 'Default Title')
        description = data.get('description', 'Default Description')
        content = data.get('content', 'Default Content')
        image_url = data.get('image_url', '')

        filename = f"{uuid.uuid4()}.html"
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

        blob = bucket.blob(filename)
        blob.upload_from_string(html_content, content_type='text/html')
        logging.info(f"HTML file created and uploaded successfully: {blob.public_url}")
        return jsonify({'url': blob.public_url})
    except Exception as e:
        logging.error(f"Error occurred in generate_page: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/upload-image', methods=['POST'])
def upload_image():
    try:
        data = request.json
        temp_img_url = data.get('temp_img_url')
        userid = data.get('userid')  # Assuming you might want to use this for something specific

        if not temp_img_url:
            return jsonify({'error': 'No image URL provided'}), 400

        # Download the image from the provided URL
        response = requests.get(temp_img_url)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to download image'}), 500

        image_content = response.content
        client = storage.Client()
        bucket = client.bucket('runapps_default-wwdwyp')
        image_blob = bucket.blob(f"{uuid.uuid4()}.jpg")  # Or use another file extension as needed

        # Upload the image to Google Cloud Storage
        image_blob.upload_from_string(image_content, content_type='image/jpeg')  # Adjust content_type based on the image
        image_blob.make_public()  # Make the image publicly accessible

        return jsonify({'image_url': image_blob.public_url})
    except Exception as e:
        logging.error(f"Error occurred in upload_image: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
