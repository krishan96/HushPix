# Build Tasks

Work through these in order. Check each off as you go.

## Setup

- [ ] Create project folder and a virtual environment.
- [ ] `pip install fastapi uvicorn pillow python-multipart`
- [ ] Create `reference/image_encode.py` and paste in the original script (kept for reference).
- [ ] Create a `static/` folder for the frontend.

## Backend (`main.py`)

- [ ] Port `genData`, `modPix`, `encode_enc` and the decode logic from the reference script — remove all `input()`/`print()`.
- [ ] Write `encode_message(image, message)` that returns the encoded `Image`.
- [ ] Write `decode_message(image)` that returns the hidden string (handle `StopIteration`, return "" if no valid message).
- [ ] Write `safe_name()` to sanitise the output filename.
- [ ] Build the `POST /encode` endpoint per BACKEND.md.
- [ ] Build the `POST /decode` endpoint — returns JSON `{message, found}`.
- [ ] Add validation: allowed extension, valid image, non-empty message, character range (≤255), capacity check.
- [ ] Convert input image to RGB before encoding and decoding.
- [ ] Return the encoded image as a streaming download with the right filename and extension.
- [ ] Mount `static/` as the frontend (after the API routes).

## Frontend (`static/index.html`)

- [ ] Build the encode form: image picker, message textarea, filename input, format dropdown, encode button, status area.
- [ ] Dropdown options: PNG (default), BMP, TIFF only.
- [ ] Wire up the encode `fetch` + `FormData` handler → trigger browser download.
- [ ] Build the decode form: image picker, decode button, read-only result textarea, copy button, status area.
- [ ] Wire up the decode handler → show the returned message (or "No message found").
- [ ] Show backend errors in the status areas.
- [ ] Disable buttons while a request is running.

## Test

- [ ] Encode a short message into a small PNG; confirm it downloads.
- [ ] Upload that downloaded image into the decode section; confirm the exact message comes back.
- [ ] Test each output format: PNG, BMP, TIFF — encode then decode each.
- [ ] Decode a plain image with no hidden message; confirm it shows "No message found" and doesn't crash.
- [ ] Test error cases: empty message, message too long for the image, no image selected, a non-image file.
- [ ] Confirm the filename and extension on the downloaded file match the user's choices.

## Polish (optional)

- [ ] Image thumbnail preview.
- [ ] Capacity / character counter.
- [ ] Basic styling.
