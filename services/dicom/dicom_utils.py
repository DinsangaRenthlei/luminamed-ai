"""DICOM utilities for processing medical images."""
import pydicom
from PIL import Image
import numpy as np
import io
import base64
from typing import Tuple, Optional


def dicom_to_png(dicom_bytes: bytes) -> Tuple[bytes, dict]:
    """Convert DICOM to PNG and extract metadata."""
    dcm = pydicom.dcmread(io.BytesIO(dicom_bytes), force=True)
    
    try:
        # Try to extract pixel array
        pixel_array = dcm.pixel_array
    except Exception as e:
        # If pixel data fails, create a placeholder
        print(f"Warning: Could not extract pixel data: {e}")
        # Create a simple gray image as fallback
        pixel_array = np.ones((512, 512), dtype=np.uint8) * 128
    
    # Normalize to 0-255
    if pixel_array.max() > 255:
        pixel_array = ((pixel_array - pixel_array.min()) / 
                      (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
    
    # Convert to PIL Image
    if len(pixel_array.shape) == 3:
        # RGB image
        image = Image.fromarray(pixel_array)
    else:
        # Grayscale
        image = Image.fromarray(pixel_array, mode='L')
    
    # Convert to PNG bytes
    png_buffer = io.BytesIO()
    image.save(png_buffer, format='PNG')
    png_bytes = png_buffer.getvalue()
    
    # Get dimensions
    height, width = pixel_array.shape[:2]
    
    # Extract metadata safely
    metadata = {
        "patient_id": str(getattr(dcm, 'PatientID', 'Unknown')),
        "patient_name": str(getattr(dcm, 'PatientName', 'Unknown')),
        "study_date": str(getattr(dcm, 'StudyDate', 'Unknown')),
        "modality": str(getattr(dcm, 'Modality', 'Unknown')),
        "study_description": str(getattr(dcm, 'StudyDescription', '')),
        "image_width": int(getattr(dcm, 'Columns', width)),
        "image_height": int(getattr(dcm, 'Rows', height)),
    }
    
    return png_bytes, metadata


def extract_dicom_metadata(dicom_bytes: bytes) -> dict:
    """Extract metadata from DICOM file."""
    dcm = pydicom.dcmread(io.BytesIO(dicom_bytes), force=True)
    
    # Try to get dimensions from pixel array
    try:
        pixel_array = dcm.pixel_array
        height, width = pixel_array.shape[:2]
    except:
        # Fallback to default or attributes
        width = int(getattr(dcm, 'Columns', 512))
        height = int(getattr(dcm, 'Rows', 512))
    
    return {
        "patient_id": str(getattr(dcm, 'PatientID', 'Unknown')),
        "patient_name": str(getattr(dcm, 'PatientName', 'Unknown')),
        "study_date": str(getattr(dcm, 'StudyDate', 'Unknown')),
        "study_time": str(getattr(dcm, 'StudyTime', 'Unknown')),
        "modality": str(getattr(dcm, 'Modality', 'CT')),
        "body_part": str(getattr(dcm, 'BodyPartExamined', 'Unknown')),
        "study_description": str(getattr(dcm, 'StudyDescription', '')),
        "image_width": width,
        "image_height": height,
    }