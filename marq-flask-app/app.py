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
        pdf_url = data.get('pdf_url', '')

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
            <meta property="og:image:alt" content="Real estate listing photo">
            <meta property="fb:app_id" content="1158479231981260">
        </head>
        <body>
            <h1>{title}</h1>
            <div id="pdfViewer"></div>
            <p>{content}</p>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js"></script>
            <script>
                var pdfUrl = "{pdf_url}";
                async function renderPdf(url) {{
                    const pdfData = await fetch(url);
                    const pdfBlob = await pdfData.blob();
                    const loadingTask = pdfjsLib.getDocument(pdfBlob);
                    const pdfDocument = await loadingTask.promise;
                    const numPages = pdfDocument.numPages;
                    for (let pageNumber = 1; pageNumber <= numPages; pageNumber++) {{
                        const page = await pdfDocument.getPage(pageNumber);
                        const scale = 1.0;
                        const canvas = document.createElement("canvas");
                        const context = canvas.getContext("2d");
                        const viewport = page.getViewport({{ scale }});
                        canvas.width = viewport.width;
                        canvas.height = viewport.height;
                        const renderContext = {{
                            canvasContext: context,
                            viewport: viewport
                        }};
                        await page.render(renderContext).promise;
                        document.getElementById("pdfViewer").appendChild(canvas);
                    }}
                }}
                renderPdf(pdfUrl);
            </script>
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

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        pdf_url = data.get('pdf_url', '')

        if not pdf_url:
            return jsonify({'error': 'No PDF URL provided'}), 400

        # Generate a unique filename for the PDF file
        filename = f"{uuid.uuid4()}.pdf"

        # Download the PDF from the URL
        response = requests.get(pdf_url)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to download PDF from URL'}), 500

        pdf_content = response.content

        # Upload the PDF content to Google Cloud Storage
        client = storage.Client()
        bucket = client.bucket('runapps_default-wwdwyp')
        pdf_blob = bucket.blob(filename)
        pdf_blob.upload_from_string(pdf_content)

        return jsonify({'pdf_url': pdf_blob.public_url})
    
    except Exception as e:
        logging.error(f"Error occurred in generate_pdf: {str(e)}")
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

        return jsonify({'image_url': image_blob.public_url})
    except Exception as e:
        logging.error(f"Error occurred in upload_image: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
