import requests
import base64
from PIL import Image
import io

def test_deployment(base_url):
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Convert to base64
    base64_image = base64.b64encode(img_byte_arr).decode()
    
    # Test health endpoint
    health_response = requests.get(f"{base_url}/health")
    print("\n1. Health Check:")
    print(health_response.json())
    
    # Test image upload
    upload_response = requests.post(
        f"{base_url}/upload-image",
        json={"image": base64_image}
    )
    print("\n2. Upload Test:")
    print(upload_response.json())
    
    # Verify the uploaded image is accessible
    if upload_response.status_code == 200:
        image_url = upload_response.json()['url']
        image_response = requests.get(image_url)
        print("\n3. Image Accessibility:")
        print(f"Image URL accessible: {image_response.status_code == 200}")

if __name__ == "__main__":
    deployment_url = input("Enter your deployment URL (e.g., https://your-app.railway.app): ")
    test_deployment(deployment_url.rstrip('/')) 