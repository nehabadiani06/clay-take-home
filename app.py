import os
import base64
import uuid
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Image Upload API",
    description="API for uploading images to AWS S3",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to docs"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Check if the service is running and environment is configured."""
    try:
        # Test S3 connection
        s3 = get_s3_client()
        s3.list_buckets()
        
        return {
            "status": "healthy",
            "aws_configured": True,
            "s3_bucket": os.getenv('S3_BUCKET_NAME'),
            "aws_region": os.getenv('AWS_REGION')
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "aws_configured": bool(os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY')),
                "s3_bucket": os.getenv('S3_BUCKET_NAME'),
                "aws_region": os.getenv('AWS_REGION')
            }
        )

class ImageUpload(BaseModel):
    image: str = Field(..., description="Base64 encoded image string")

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
        logger.info("Starting image upload process")
        
        # Validate base64 string
        try:
            image_bytes = base64.b64decode(image_data.image)
        except Exception as e:
            logger.error(f"Base64 decoding failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid base64 image data")
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.png"
        logger.info(f"Generated filename: {filename}")
        
        # Get S3 client
        try:
            s3 = get_s3_client()
        except Exception as e:
            logger.error(f"S3 client creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initialize S3 client")
        
        # Upload to S3
        try:
            s3.put_object(
                Bucket=os.getenv('S3_BUCKET_NAME'),
                Key=filename,
                Body=image_bytes,
                ContentType="image/png"
            )
            logger.info("Successfully uploaded to S3")
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'NoSuchBucket':
                raise HTTPException(status_code=500, detail="S3 bucket does not exist")
            elif error_code == 'AccessDenied':
                raise HTTPException(status_code=500, detail="Access denied to S3 bucket")
            else:
                raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
        
        # Generate URL
        url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.amazonaws.com/{filename}"
        logger.info(f"Generated URL: {url}")
        
        return {"success": True, "url": url}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 10000))
    uvicorn.run(app, host="0.0.0.0", port=port) 