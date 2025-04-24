# Image Upload API

This is a FastAPI application that handles image uploads to AWS S3 via base64 encoded strings.

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your AWS credentials and configuration in the `.env` file

## Running the API

Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Usage

Send a POST request to `/upload-image` with a JSON body containing a base64 encoded image:

```json
{
    "image": "base64_encoded_image_string"
}
```

The API will respond with:
```json
{
    "success": true,
    "url": "https://your-bucket.s3.amazonaws.com/filename.png"
}
```

## Security Notes

- Never commit the `.env` file with real credentials
- Make sure to set up proper CORS and authentication if needed
- Consider implementing rate limiting for production use 