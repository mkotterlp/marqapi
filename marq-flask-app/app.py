from flask import Flask, request, jsonify
import uuid
import os
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

# New endpoint to return the image URL
@app.route('/image-url/<filename>')
def get_image_url(filename):
    try:
        client = storage.Client()
        bucket = client.bucket('runapps_default-wwdwyp')
        blob = bucket.blob(filename)

        # Ensure the blob exists and is public
        if not blob.exists():
            return jsonify({'error': 'File not found'}), 404

        # Construct the public URL for the blob
        image_url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"
        return jsonify({'image_url': image_url})
    except Exception as e:
        logging.error(f"Failed to fetch image URL: {str(e)}")
        return jsonify({'error': 'Failed to fetch image URL'}), 500


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
