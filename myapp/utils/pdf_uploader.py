import requests
import os
import cloudinary.uploader
import tempfile
from dotenv import load_dotenv

def upload_pdf(pdf_file, fileName ,folder='files'):
    """
    Uploads a PDF file (either a file object or a URL) to Cloudinary and returns the uploaded file's URL.
    """
    load_dotenv()
    
    try:
        # Load Cloudinary credentials from .env
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        
        if isinstance(pdf_file, str) and pdf_file.startswith("http"):
            # If the input is a URL, download the file
            response = requests.get(pdf_file, stream=True)
            if response.status_code != 200:
                return f"Error: Unable to download PDF from URL. Status Code: {response.status_code}"
            
            with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
                for chunk in response.iter_content(1024):
                    temp_file.write(chunk)
                temp_file.flush()
                
                # Upload the temporary file to Cloudinary
                upload_response = cloudinary.uploader.upload(
                    temp_file.name,
                    resource_type="raw",
                    folder=folder,
                    use_filename=True,
                    unique_filename=False,
                    access_mode="public"
                )
        else:
            # Upload file object (e.g., request.FILES["pdf"])
            upload_response = cloudinary.uploader.upload(
                pdf_file,
                resource_type="raw",
                folder=folder,
                use_filename=True,
                unique_filename=False,
                access_mode="public"
            )

        # Construct the direct-access URL
        public_id = upload_response.get("public_id")
        pdf_url = f"https://res.cloudinary.com/{cloud_name}/raw/upload/{fileName}.pdf"

        return pdf_url
    
    except Exception as e:
        return f"Error Uploading File: {e}"