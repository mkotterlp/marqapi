from flask import Flask, request, jsonify, make_response
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
        title = data.get('title', 'View my listing')
        description = data.get('description', 'View my listing')
        image_url = data.get('image_url', '')
        pdf_url = data.get('pdf_url', '')
        email = data.get('email', '')
        property_id = data.get('property_id', '')
        property_address = data.get('property_address', '')
        filename = f"{uuid.uuid4()}.html"
        webpage_url = f"https://marqsocial.web.app/files/{filename}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <meta property="og:url" content="{webpage_url}" />
            <meta property="og:type" content="website" />
            <meta property="og:title" content="{title}" />
            <meta property="og:image" content="{image_url}" />
            <meta property="og:description" content="{description}" />
            <meta property="og:image:alt" content="Real estate listing photo">
            <meta property="fb:app_id" content="1158479231981260">
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap" rel="stylesheet">
            <style>
                * {{
                    font-family: 'Poppins', sans-serif;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    font-family: 'Poppins', sans-serif;
                    font-weight: 600; 
                }}
                p {{
                    font-family: 'Poppins', sans-serif;
                    font-weight: 400;  
                    margin:0px;
                }}
                .svg-icon {{
                    width:100%;
                    height:30px;
                }} 
                .request-form {{
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 300px;
                    background: white;
                    padding: 15px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                    z-index: 1000;
                }}
                .request-form h3 {{
                    margin-top: 0;
                }}
                .request-form form {{
                    display: flex;
                    flex-direction: column;
                }}
                .request-form input,
                .request-form textarea,
                .request-form button {{
                    margin: 5px 0;
                    padding: 10px;
                }}
                .request-form button {{
                    background-color: #EE3524;
                    color: white;
                    border: none;
                    cursor: pointer;
                }}
                .request-form button:hover {{
                    background-color: #e56559;
                }}
                #pdfViewer {{
                    width: 100%;
                    overflow-x: auto;
                    overflow-y: hidden;
                    white-space: nowrap;
                    text-align: center;
                    scroll-behavior: smooth;
                }}
                .navigation {{ 
                    text-align: center; 
                    position: fixed;
                    bottom: 0;
                    width: 100%;
                }}
                .button {{
                    cursor: pointer;
                    padding: 10px;
                    margin: 5px;
                    background-color: #212121;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }}
                .button:disabled {{
                    background-color: #ccc;
                }}
                .button:hover:not(:disabled) {{
                    background-color: #5d636b;
                }}
                canvas {{
                    display: inline-block;
                }}
            </style>
        </head>
        <body>
            <div id="requestForm" class="request-form">
                <h3>Request info on this property</h3>
                <h4>{property_address}</h4>
                <form id="leadForm">
                    <input type="email" id="lead_email" name="lead_email" placeholder="Your email" required />
                    <input type="text" id="lead_name" name="lead_name" placeholder="Your name" required />
                    <input type="text" id="lead_phone" name="lead_phone" placeholder="Your phone number" required />
                    <textarea id="lead_message" name="lead_message" placeholder="Message"></textarea>
                    <input type="hidden" id="email" name="email" value="{email}" />
                    <input type="hidden" id="property_id" name="property_id" value="{property_id}" />
                    <input type="hidden" id="webpage_url" name="webpage_url" value="{webpage_url}" />
                    <button type="submit">Request info</button>
                </form>
            </div>
            <div id="pdfViewer"></div>
            <div class="navigation">
                <button id="prevPage" class="button"><svg class="svg-icon" style="vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"><path d="M725.333333 469.333333H401.493333l140.8-140.373333a42.666667 42.666667 0 1 0-60.586666-60.586667l-213.333334 213.333334a42.666667 42.666667 0 0 0-8.96 14.08 42.666667 42.666667 0 0 0 0 32.426666 42.666667 42.666667 0 0 0 8.96 14.08l213.333334 213.333334a42.666667 42.666667 0 0 0 60.586666 0 42.666667 42.666667 0 0 0 0-60.586667L401.493333 554.666667H725.333333a42.666667 42.666667 0 0 0 0-85.333334z"  /></svg></button>
                <button id="nextPage" class="button"><svg class="svg-icon" style="vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"><path d="M764.586667 495.786667a42.666667 42.666667 0 0 0-8.96-14.08l-213.333334-213.333334a42.666667 42.666667 0 0 0-60.586666 60.586667l140.8 140.373333H298.666667a42.666667 42.666667 0 0 0 0 85.333334h323.84l-140.8 140.373333a42.666667 42.666667 0 0 0 0 60.586667 42.666667 42.666667 0 0 0 60.586666 0l213.333334-213.333334a42.666667 42.666667 0 0 0 8.96-14.08 42.666667 42.666667 0 0 0 0-32.426666z"  /></svg></button>
            </div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js"></script>
            <script>
                var pdfUrl = "{pdf_url}";
                async function renderPdf(url) {{
                    try {{
                        const pdfData = await fetch(url);
                        if (!pdfData.ok) {{
                            throw new Error('Failed to fetch the PDF. Status: ' + pdfData.status);
                        }}
                        const pdfBlob = await pdfData.blob();
                        const arrayBuffer = await pdfBlob.arrayBuffer();
                        const loadingTask = pdfjsLib.getDocument({{data: arrayBuffer}});
                        const pdfDocument = await loadingTask.promise;
                        let currentPageIndex = 0;
                        const numPages = pdfDocument.numPages;
                        for (let pageNumber = 1; pageNumber <= numPages; pageNumber++) {{
                            const page = await pdfDocument.getPage(pageNumber);
                            const scale = 1.0;
                            const canvas = document.createElement("canvas");
                            canvas.id = 'page-' + pageNumber;
                            const context = canvas.getContext("2d");
                            const viewport = page.getViewport({{scale}});
                            canvas.width = viewport.width;
                            canvas.height = viewport.height;
                            const renderContext = {{
                                canvasContext: context,
                                viewport: viewport
                            }};
                            await page.render(renderContext).promise;
                            document.getElementById("pdfViewer").appendChild(canvas);
                        }}
                        updateNavigation(); // Initial call to set the button state correctly
                        document.getElementById('pdfViewer').addEventListener('scroll', () => {{
                            updateNavigation();
                        }});
                        document.getElementById('nextPage').addEventListener('click', () => {{
                            scrollPdfViewer('next');
                        }});
                        document.getElementById('prevPage').addEventListener('click', () => {{
                            scrollPdfViewer('prev');
                        }});
                    }} catch (error) {{
                        console.error('Error rendering PDF:', error);
                    }}
                }}
                renderPdf(pdfUrl);
                function updateNavigation() {{
                    const pdfViewer = document.getElementById("pdfViewer");
                    const atStart = pdfViewer.scrollLeft === 0;
                    const atEnd = pdfViewer.scrollLeft + pdfViewer.offsetWidth >= pdfViewer.scrollWidth;
                    document.getElementById('prevPage').disabled = atStart;
                    document.getElementById('nextPage').disabled = atEnd;
                }}
                function scrollPdfViewer(direction) {{
                    const pdfViewer = document.getElementById("pdfViewer");
                    const scrollAmount = pdfViewer.offsetWidth - 100; // Adjust the 100 to add some margin if needed
                    if (direction === 'next' && !document.getElementById('nextPage').disabled) {{
                        pdfViewer.scrollLeft += scrollAmount;
                    }} else if (direction === 'prev' && !document.getElementById('prevPage').disabled) {{
                        pdfViewer.scrollLeft -= scrollAmount;
                    }}
                }}
                document.getElementById('leadForm').addEventListener('submit', function(event) {{
                    event.preventDefault();
                    const form = document.getElementById('requestForm');
                    const payload = {{
                        email: document.getElementById('email').value,
                        property_id: document.getElementById('property_id').value,
                        webpage_url: document.getElementById('webpage_url').value,
                        lead_email: document.getElementById('lead_email').value,
                        lead_phone: document.getElementById('lead_phone').value,
                        lead_message: document.getElementById('lead_message').value,
                        lead_name: document.getElementById('lead_name').value,
                    }};
                    fetch('https://serhant.fastgenapp.com/submit-lead', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify(payload),
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        console.log('Success:', data);
                        form.style.display = 'none';
                        const successMessage = document.createElement('div');
                        successMessage.textContent = 'Your request has been submitted successfully!';
                        successMessage.style.position = 'fixed';
                        successMessage.style.bottom = '20px';
                        successMessage.style.right = '20px';
                        successMessage.style.backgroundColor = 'white';
                        successMessage.style.padding = '15px';
                        successMessage.style.borderRadius = '8px';
                        successMessage.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
                        document.body.appendChild(successMessage);
                    }})
                    .catch((error) => {{
                        console.error('Error:', error);
                    }});
                }});
            </script>
        </body>
        </html>
        """



        blob = bucket.blob(filename)
        blob.upload_from_string(html_content, content_type='text/html')
        logging.info(f"HTML file created and uploaded successfully: {blob.public_url}")
        webpage_url = f"https://marqsocial.web.app/files/{filename}"
        return jsonify({'url': webpage_url})
    except Exception as e:
        logging.error(f"Error occurred in generate_page: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/generate-images', methods=['POST'])
def generate_images_page():
    try:
        client = storage.Client()
        bucket = client.bucket('runapps_default-wwdwyp')

        data = request.json
        image_urls = data.get('image_urls', [])
        title = data.get('title', 'View Images')
        filename = f"{uuid.uuid4()}.html"
        webpage_url = f"https://marqsocial.web.app/files/{filename}"

        # Generate the HTML content dynamically based on the image URLs
        images_html = ''.join([f'<img src="{url}" style="width:100%;margin-bottom:10px;" />' for url in image_urls])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap" rel="stylesheet">
            <style>
                * {{
                    font-family: 'Poppins', sans-serif;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div>
                {images_html}
            </div>
        </body>
        </html>
        """

        # Upload the HTML content to the Google Cloud Storage
        blob = bucket.blob(filename)
        blob.upload_from_string(html_content, content_type='text/html')
        logging.info(f"HTML file with images created and uploaded successfully: {blob.public_url}")

        return jsonify({'url': webpage_url})
    except Exception as e:
        logging.error(f"Error occurred in generate_images_page: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        client = storage.Client()
        bucket = client.bucket('runapps_default-wwdwyp')
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
        pdf_blob.upload_from_string(pdf_content, content_type='application/pdf')
        webpage_url = f"https://marqsocial.web.app/pdfs/{filename}"
        return jsonify({'pdf_url': webpage_url})
    
    except Exception as e:
        logging.error(f"Error occurred in generate_pdf: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/upload-image', methods=['POST'])
def upload_image():
    try:
        client = storage.Client()
        bucket = client.bucket('runapps_default-wwdwyp')
        data = request.json
        temp_img_url = data.get('temp_img_url')

        if not temp_img_url:
            return jsonify({'error': 'No image URL provided'}), 400

        # Download the image from the provided URL
        response = requests.get(temp_img_url)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to download image'}), 500

        image_content = response.content
        client = storage.Client()
        bucket = client.bucket('runapps_default-wwdwyp')

        # Generate a unique filename for the image
        filename = f"{uuid.uuid4()}.jpg"  # Or use another file extension as needed
        image_blob = bucket.blob(filename)

        # Upload the image to Google Cloud Storage
        image_blob.upload_from_string(image_content, content_type='image/jpeg')  # Adjust content_type based on the image

        # Generate a branded URL pointing to the Flask route for serving the image
        webpage_url = f"https://marqsocial.web.app/images/{filename}"
        return jsonify({'image_url': webpage_url})
    except Exception as e:
        logging.error(f"Error occurred in upload_image: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/files/<filename>')
def serve_file(filename):
    client = storage.Client()
    bucket = client.bucket('runapps_default-wwdwyp')
    blob = bucket.blob(filename)
    response = make_response(blob.download_as_bytes())
    response.headers.set('Content-Type', 'text/html')
    response.headers.set('Content-Disposition', f'inline; filename={filename}')
    return response

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket('runapps_default-wwdwyp')
    blob = bucket.blob(filename)
    if blob.exists():
        response = make_response(blob.download_as_bytes())
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', 'inline; filename=' + filename)
        return response
    else:
        return "File not found", 404

@app.route('/images/<filename>')
def serve_image(filename):
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket('runapps_default-wwdwyp')
    blob = bucket.blob(filename)
    if blob.exists():
        response = make_response(blob.download_as_bytes())
        response.headers.set('Content-Type', 'image/jpeg')  # Adjust the content type based on your image format
        response.headers.set('Content-Disposition', 'inline; filename=' + filename)
        return response
    else:
        return "File not found", 404


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
