import os
import base64
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Check if the service is running and environment is configured."""
    return {
        "status": "healthy",
        "aws_configured": bool(os.getenv('AWS_ACCESS_KEY_ID') and 
                             os.getenv('AWS_SECRET_ACCESS_KEY')),
        "s3_bucket": os.getenv('S3_BUCKET_NAME'),
        "aws_region": os.getenv('AWS_REGION')
    }

class ImageUpload(BaseModel):
    image: str  # Base64 encoded image

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-2')
    )

@app.post("/upload-image")
async def upload_image(image_data: ImageUpload):
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.image)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.png"
        
        # Get S3 client
        s3 = get_s3_client()
        
        # Upload to S3
        s3.put_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=filename,
            Body=image_bytes,
            ContentType="image/png"
        )
        
        # Generate URL
        url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.amazonaws.com/{filename}"
        return {"success": True, "url": url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 