# Steganography Web App

A web application that hides a secret text message inside an image using LSB (Least Significant Bit) steganography, based on an existing Python reference script.

## What the app does

1. User picks an image from their computer.
2. User types a secret message.
3. User sets the output filename.
4. User picks the output file extension from a dropdown (PNG, BMP, TIFF).
5. App encodes the message into the image and lets the user download the result.

## Important technical constraint

The encoding **must use a lossless image format** (PNG, BMP, TIFF). JPEG re-compresses pixels and destroys the hidden bits, so it must NOT be offered as an output option. This is why the dropdown only lists lossless formats.

## Architecture

- **Backend**: Python (FastAPI). Reuses the LSB logic from the original reference script (`reference/image_encode.py`). Pillow (PIL) does the pixel work.
- **Frontend**: A single HTML page with a form (image picker, message textarea, filename input, extension dropdown) that posts to the backend and triggers a download.

The project is small — a web wrapper around proven encoding logic. Keep it simple. Do not over-engineer.

## How the original algorithm works (for reference)

- Each character becomes an 8-bit binary string.
- Three pixels (9 colour channels) store one character: 8 channels hold the 8 bits, the 9th channel is a continue/stop flag.
- Flag channel even = more data follows; odd = end of message.
- Decoding reads channel parity back into bits until it hits the stop flag.

## Files in this project

- `SPEC.md` — full product and UI specification
- `BACKEND.md` — backend implementation guide
- `FRONTEND.md` — frontend implementation guide
- `TASKS.md` — ordered build checklist
- `reference/image_encode.py` — the original CLI script to adapt

## Conventions

- Keep dependencies minimal: `fastapi`, `uvicorn`, `pillow`, `python-multipart`.
- Validate all user input on the backend (don't trust the form).
- No database, no auth, no accounts. Single-purpose tool.
