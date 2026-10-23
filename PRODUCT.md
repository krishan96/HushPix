# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Teachers, students and anyone learning how LSB steganography works. The user is in a learning or demonstration situation: they encode a short message into an ordinary image, then decode it again to show the round trip. Confirmed by the owner (primary user: teaching or demonstration).

## Product Purpose

A public web app with two features: encode a secret text message into an image using least-significant-bit steganography and download the result, and decode a message back out of an encoded image. Success means a visitor can complete a full encode and decode round trip on the first try and understands from the screen why the output format matters.

## Positioning

Lossless-only output, enforced by the product rather than left to the user: the format choice offers only PNG, BMP and TIFF, because a lossy re-encode would silently destroy the hidden bits. No accounts, no storage and no history; uploads are processed in memory. Confirmed by the owner.

## Operating Context

Used in a browser, in one visit: pick an image, type a message, name the file, choose a format, download. Decode is the reverse, one image in and one message out. Images come from the visitor's own machine; the app runs on a Python backend (FastAPI with Pillow) and serves a single static page.

## Capabilities and Constraints

- Encode: image upload, message textarea, output filename without extension, format dropdown (PNG default, BMP, TIFF), download with the chosen name.
- Decode: image upload, read-only result area, copy-to-clipboard button, clean "no message found" result.
- Capacity: floor(width × height / 3) characters per image; the backend rejects over-long messages and states the limit.
- Characters limited to code points 0–255 (8-bit encoding); emoji and wider characters are rejected or the limit is documented in the UI.
- Upload size should be capped (around 10 MB) and uploads kept in memory.
- Filenames are sanitised before use in the download header.
- No JPEG output, ever.

## Brand Commitments

None fixed. The name is ImgSecrets; there is no logo, voice or visual identity to preserve. The owner confirmed no brand yet.

## Evidence on Hand

No case studies, testimonials, usage numbers or press. Sample content is not evidence and no proof claims should be invented. Future work must not fabricate usage figures or endorsements.

## Product Principles

- Teach the mechanism: the page should make it obvious why the format list is short and why the capacity is what it is.
- Keep the round trip the centre of the product: encode and decode are two halves of one lesson.
- Never fail silently: every error, limit and empty result is stated in plain words on the page.
- Stay small: no accounts, storage or history; the single purpose is the feature.

## Accessibility & Inclusion

WCAG 2.2 level AA, confirmed by the owner. No further accessibility requirements have been recorded.
