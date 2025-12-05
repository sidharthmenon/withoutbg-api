"""FastAPI backend for withoutbg web application."""

import io
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import uvicorn
from fastapi.security import APIKeyHeader

# Import withoutbg package (install via: uv sync or pip install -e ../../../packages/python)
from withoutbg import WithoutBG, __version__
from withoutbg.exceptions import WithoutBGError

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="withoutbg API",
    description="AI-powered background removal API",
    version=__version__,
)

# CORS middleware for local development and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # Expose header for blob downloads
)

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get API token from environment
raw_tokens = os.getenv("API_TOKEN", "")
API_TOKENS = {t.strip() for t in raw_tokens.split(",") if t.strip()}  # convert to set for fast lookup

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify API key from request header.
    Supports multiple keys provided as CSV in API_TOKENS env.
    """
    # If no tokens set → allow all requests (dev mode)
    if not API_TOKENS:
        print("⚠ WARNING: No API_TOKENS set. API authentication is DISABLED.")
        return True

    # No token provided
    if api_key is None:
        raise HTTPException(
            status_code=401,
            detail="API key missing. Provide header: X-API-Key",
        )

    # Token invalid
    if api_key not in API_TOKENS:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )

    return True


# Static files directory (frontend build)
STATIC_DIR = Path(__file__).parent.parent.parent / "static"

# Global model instance (initialized at startup, reused for all requests)
_model: Optional[WithoutBG] = None

@app.on_event("startup")
async def startup_event():
    """Initialize models at startup for optimal performance."""
    global _model
    print("Loading Open Source models...")
    _model = WithoutBG.opensource()
    print("✓ Models loaded and ready for inference!")

    # Log API token status
    if API_TOKENS:
        print(f"✓ API authentication enabled (token configured)")
    else:
        print("⚠ API authentication disabled (no API_TOKEN in environment)")

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "service": "withoutbg-api",
        "models_loaded": _model is not None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "service": "withoutbg-api",
        "models_loaded": _model is not None
    }


@app.post("/remove-background", dependencies=[Depends(verify_api_key)])
async def remove_background_endpoint(
    file: UploadFile = File(...),
    format: str = Form("png"),
    quality: int = Form(95),
):
    """
    Remove background from a single image.
    
    Args:
        file: Image file to process
        format: Output format (png, jpg, webp)
        quality: Quality for JPEG output (1-100)
    
    Returns:
        Processed image with background removed
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read uploaded file
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents))
        
        # Process image using appropriate model
        # Use pre-loaded opensource model (fast!)
        if _model is None:
            raise HTTPException(
                status_code=503,
                detail="Models not loaded. Server may still be starting up."
            )
        result = _model.remove_background(input_image)
        
        # Convert result to bytes
        output_buffer = io.BytesIO()
        
        # Handle format conversion
        if format.lower() in ["jpg", "jpeg"]:
            # Convert RGBA to RGB for JPEG
            if result.mode == "RGBA":
                rgb_image = Image.new("RGB", result.size, (255, 255, 255))
                rgb_image.paste(result, mask=result.split()[3])
                rgb_image.save(output_buffer, format="JPEG", quality=quality)
            else:
                result.save(output_buffer, format="JPEG", quality=quality)
            media_type = "image/jpeg"
        elif format.lower() == "webp":
            result.save(output_buffer, format="WEBP", quality=quality)
            media_type = "image/webp"
        else:  # PNG
            result.save(output_buffer, format="PNG")
            media_type = "image/png"
        
        output_buffer.seek(0)
        
        return Response(
            content=output_buffer.getvalue(),
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename=withoutbg.{format}"
            }
        )
        
    except WithoutBGError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)