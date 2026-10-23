# Specification

## Goal

A single-page web app with two features:
- **Encode**: hide a secret text message in an image using LSB steganography, then download the encoded image.
- **Decode**: upload an encoded image and read the hidden message back out.

The page has two sections (or two tabs) — one for encoding, one for decoding.

## Encode flow

1. User selects an image via a file picker (`<input type="file">`).
2. User types a secret message into a text box (`<textarea>`).
3. User enters the desired output filename (without extension) in a text input.
4. User chooses the output extension from a dropdown.
5. User clicks **Encode**.
6. The browser downloads the encoded image with the chosen name and extension.

## Decode flow

1. User selects an encoded image via a file picker.
2. User clicks **Decode**.
3. The hidden message appears on the page in a read-only text area (with a copy button, ideally).
4. If the image has no hidden message, show a clear "No message found" result instead of crashing.

## UI elements (exact requirements)

**Encode section:**

| Element | Type | Notes |
|---|---|---|
| Image picker | `<input type="file" accept="image/*">` | Required. Accept common image types for input. |
| Secret message | `<textarea>` | Required. Non-empty. |
| Output filename | `<input type="text">` | Required. No extension needed — the dropdown supplies it. Strip any extension the user types. |
| Output format | `<select>` | Options: PNG, BMP, TIFF. Default PNG. |
| Encode button | `<button>` | Disabled while a request is in flight. |

**Decode section:**

| Element | Type | Notes |
|---|---|---|
| Image picker | `<input type="file" accept="image/*">` | Required. The encoded image to read. |
| Decode button | `<button>` | Disabled while a request is in flight. |
| Result area | `<textarea readonly>` | Shows the decoded message. Read-only. |
| Copy button | `<button>` | Optional. Copies the decoded message to clipboard. |

## Output format dropdown

Only **lossless** formats, because lossy compression destroys hidden bits:

- **PNG** (default, recommended)
- **BMP**
- **TIFF**

Do NOT include JPEG/JPG — it would silently corrupt the message.

## Validation rules

Backend must enforce all of these and return a clear error on failure:

- An image file was uploaded and is a valid image Pillow can open.
- The message is not empty.
- The message fits in the image. Capacity = `floor((width * height) / 3)` characters, since each character uses 3 pixels. Reject with a helpful message if the text is too long, stating the max characters for that image.
- The output extension is one of the allowed three.
- The message contains only characters in range 0–255 (the algorithm uses `ord()` into 8 bits). Reject characters above 255 (e.g. most emoji) with a clear message, OR document this limit in the UI.

## Error handling

- Show backend error messages to the user in a visible status area (not just a console log).
- Never crash the page on a failed request.

## Decode notes

- Decoding only works on **lossless** encoded images (PNG/BMP/TIFF). If someone uploads a JPEG or an image with no hidden data, the parity bits will be garbage — decode may return junk characters or hit an error. Handle this gracefully: if the decoded text looks like non-printable garbage, show "No valid message found in this image" rather than dumping junk.
- The decode loop reads until it hits the stop flag. On a plain image with no message, it may read until it runs out of pixels — wrap this so it fails cleanly (catch `StopIteration`) instead of throwing.

## Non-goals

- No user accounts, storage, or history.
- No image preview is required, but a small thumbnail preview of the selected image is a nice-to-have.

## Security notes

- Process the image in memory; don't write uploads to disk unless needed, and clean up if you do.
- Cap upload size (e.g. 10 MB) to avoid abuse.
- Sanitise the filename before using it in the download header.
