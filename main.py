from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import re

app = FastAPI()

ALLOWED = {"png": "PNG", "bmp": "BMP", "tiff": "TIFF"}
MAX_UPLOAD = 10 * 1024 * 1024  # 10 MB


def genData(data):
    """Converts input text into a list of 8-bit binary strings."""
    return [format(ord(i), '08b') for i in data]


def modPix(pix, data):
    """Modifies pixel values to encode the binary data."""
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        pixels = [value for value in next(imdata)[:3] + next(imdata)[:3] + next(imdata)[:3]]

        # Modify pixel values based on binary data
        for j in range(8):
            if datalist[i][j] == '0' and pixels[j] % 2 != 0:
                pixels[j] -= 1
            elif datalist[i][j] == '1' and pixels[j] % 2 == 0:
                pixels[j] = pixels[j] - 1 if pixels[j] != 0 else pixels[j] + 1

        # Set termination flag (last pixel even means continue, odd means stop)
        if i == lendata - 1:
            pixels[-1] |= 1  # Make odd (stop flag)
        else:
            pixels[-1] &= ~1  # Make even (continue flag)

        yield tuple(pixels[:3])
        yield tuple(pixels[3:6])
        yield tuple(pixels[6:9])


def encode_enc(newimg, data):
    """Encodes the modified pixel data into the new image."""
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        x = 0 if x == w - 1 else x + 1
        y += 1 if x == 0 else 0


def encode_message(image: Image.Image, message: str) -> Image.Image:
    """Encodes a message into a copy of the image and returns it."""
    newimg = image.copy()
    encode_enc(newimg, message)
    return newimg


def decode_message(image: Image.Image) -> str:
    """Decodes a hidden message from an image."""
    imgdata = iter(image.getdata())
    chars = []
    try:
        while True:
            pixels = [v for v in next(imgdata)[:3] + next(imgdata)[:3] + next(imgdata)[:3]]
            binstr = ''.join('1' if p % 2 else '0' for p in pixels[:8])
            chars.append(chr(int(binstr, 2)))
            if pixels[-1] % 2 != 0:  # stop flag
                break
    except StopIteration:
        pass  # ran out of pixels — no valid stop flag found
    text = ''.join(chars)
    # Guard against junk from an image with no real message
    if not text or any(ord(c) < 9 for c in text):
        return ""
    return text


def safe_name(name: str) -> str:
    """Sanitizes filename and strips extension."""
    name = name.rsplit(".", 1)[0]  # drop any extension
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

    encoded = encode_message(img, message)

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

    message = decode_message(img)
    if not message:
        return {"message": "", "found": False}
    return {"message": message, "found": True}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
