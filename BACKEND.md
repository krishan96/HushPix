# Backend Guide

## Stack

- Python 3.10+
- FastAPI (web framework)
- Uvicorn (server)
- Pillow (image processing)
- python-multipart (file upload support)

## Install

```bash
pip install fastapi uvicorn pillow python-multipart
```

## Adapt the reference algorithm

The original script (`reference/image_encode.py`) uses `input()`/`print()` for a CLI. Strip that out and keep the core encoding logic as pure functions that take data in and return an image out — no console I/O.

Port these from the reference, unchanged in logic:

- `genData(data)` — text → list of 8-bit binary strings.
- `modPix(pix, data)` — generator that yields modified pixel tuples.
- `encode_enc(newimg, data)` — writes modified pixels into a copy of the image.
- The `decode()` body — reads pixel parity back into characters until the stop flag.

Wrap encoding so the entry point is roughly:

```python
from PIL import Image
import io

def encode_message(image: Image.Image, message: str) -> Image.Image:
    newimg = image.copy()
    encode_enc(newimg, message)   # reuse ported logic
    return newimg
```

Wrap decoding the same way — take an image, return the string. The reference `decode()` uses `input()` to get the filename and can run off the end of the image on a file with no hidden message; fix both:

```python
def decode_message(image: Image.Image) -> str:
    imgdata = iter(image.getdata())
    chars = []
    try:
        while True:
            pixels = [v for v in next(imgdata)[:3] + next(imgdata)[:3] + next(imgdata)[:3]]
            binstr = ''.join('1' if p % 2 else '0' for p in pixels[:8])
            chars.append(chr(int(binstr, 2)))
            if pixels[-1] % 2 != 0:   # stop flag
                break
    except StopIteration:
        pass   # ran out of pixels — no valid stop flag found
    text = ''.join(chars)
    # Guard against junk from an image with no real message
    if not text or any(ord(c) < 9 for c in text):
        return ""
    return text
```

## Capacity check

Before encoding, verify the message fits:

```python
max_chars = (image.width * image.height) // 3
if len(message) > max_chars:
    raise ValueError(f"Message too long. This image holds up to {max_chars} characters.")
```

## Character range check

The algorithm assumes each character fits in 8 bits:

```python
if any(ord(c) > 255 for c in message):
    raise ValueError("Message contains unsupported characters (only basic Latin/extended ASCII allowed).")
```

## The endpoint

`POST /encode` — accepts multipart form data:

- `image`: UploadFile
- `message`: str (form field)
- `filename`: str (form field, no extension)
- `extension`: str (form field: "png" | "bmp" | "tiff")

Logic:

1. Validate `extension` is in the allowed set; reject otherwise.
2. Open the uploaded file with `Image.open()`; return a clear error if it isn't a valid image. Convert to `RGB` to guarantee 3 channels per pixel (`image = image.convert("RGB")`).
3. Validate message non-empty, character range, and capacity.
4. Encode.
5. Save the result into an in-memory buffer in the chosen format, then stream it back.

```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io, re

app = FastAPI()

ALLOWED = {"png": "PNG", "bmp": "BMP", "tiff": "TIFF"}
MAX_UPLOAD = 10 * 1024 * 1024  # 10 MB

def safe_name(name: str) -> str:
    name = name.rsplit(".", 1)[0]                 # drop any extension
    name = re.sub(r"[^A-Za-z0-9_\-]", "_", name)  # sanitise
    return name or "encoded"

@app.post("/encode")
async def encode(
    image: UploadFile = File(...),
    message: str = Form(...),
    filename: str = Form(...),
    extension: str = Form(...),
):
    ext = extension.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, "Unsupported output format.")

    raw = await image.read()
    if len(raw) > MAX_UPLOAD:
        raise HTTPException(400, "Image too large (max 10 MB).")

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Could not read that image file.")

    if not message:
        raise HTTPException(400, "Message is empty.")
    if any(ord(c) > 255 for c in message):
        raise HTTPException(400, "Message has unsupported characters (basic/extended ASCII only).")

    max_chars = (img.width * img.height) // 3
    if len(message) > max_chars:
        raise HTTPException(400, f"Message too long. This image holds up to {max_chars} characters.")

    encoded = encode_message(img, message)   # your ported logic

    buf = io.BytesIO()
    encoded.save(buf, ALLOWED[ext])
    buf.seek(0)

    out_name = f"{safe_name(filename)}.{ext}"
    return StreamingResponse(
        buf,
        media_type=f"image/{ext}",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )

@app.post("/decode")
async def decode(image: UploadFile = File(...)):
    raw = await image.read()
    if len(raw) > MAX_UPLOAD:
        raise HTTPException(400, "Image too large (max 10 MB).")

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Could not read that image file.")

    message = decode_message(img)   # your ported logic
    if not message:
        return {"message": "", "found": False}
    return {"message": message, "found": True}

# Serve the frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

## Run

```bash
uvicorn main:app --reload
```

Then open `http://localhost:8000`.

## Gotchas

- Mount `StaticFiles` **after** defining `/encode`, or the catch-all will swallow the API route.
- `convert("RGB")` is important — a palette or RGBA image breaks the 3-channel assumption in the pixel logic.
- The reference `modPix` reads pixels via `next(imdata)` three at a time; make sure the image has enough pixels (the capacity check covers this).
