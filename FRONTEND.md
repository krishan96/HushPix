# Frontend Guide

## Approach

One static HTML file (`static/index.html`) with inline CSS and JS. No build step, no framework. It has two sections — **Encode** (posts to `/encode`, triggers a download) and **Decode** (posts to `/decode`, shows the hidden message on the page).

Put them in two tabs, or just two stacked panels with a heading each — whichever is simpler. Place the file in a `static/` folder so the backend can serve it.

## Required form fields

- Image picker: `<input type="file" id="image" accept="image/*" required>`
- Secret message: `<textarea id="message" required></textarea>`
- Output filename: `<input type="text" id="filename" placeholder="my_secret_image" required>`
- Format dropdown:

```html
<select id="extension">
  <option value="png" selected>PNG (recommended)</option>
  <option value="bmp">BMP</option>
  <option value="tiff">TIFF</option>
</select>
```

- Encode button: `<button type="submit">Encode</button>`
- A status area: `<p id="status"></p>` for success/error messages.

## Submit logic

Use `fetch` with `FormData`. On success the response is a binary blob — turn it into a download. On failure, read the JSON error and show it.

```html
<script>
const form = document.getElementById("form");
const statusEl = document.getElementById("status");
const btn = form.querySelector("button");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.textContent = "Encoding…";
  btn.disabled = true;

  const data = new FormData();
  data.append("image", document.getElementById("image").files[0]);
  data.append("message", document.getElementById("message").value);
  data.append("filename", document.getElementById("filename").value);
  data.append("extension", document.getElementById("extension").value);

  try {
    const res = await fetch("/encode", { method: "POST", body: data });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Something went wrong." }));
      statusEl.textContent = "Error: " + (err.detail || "Encoding failed.");
      return;
    }

    // Trigger download
    const blob = await res.blob();
    const disposition = res.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="(.+?)"/);
    const name = match ? match[1] : "encoded.png";

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    URL.revokeObjectURL(url);

    statusEl.textContent = "Done — downloaded " + name;
  } catch {
    statusEl.textContent = "Error: could not reach the server.";
  } finally {
    btn.disabled = false;
  }
});
</script>
```

## Decode section

A second file picker and a Decode button that posts to `/decode`. The response is JSON, not a file — show the message in a read-only textarea.

```html
<h2>Decode</h2>
<form id="decodeForm">
  <input type="file" id="decodeImage" accept="image/*" required>
  <button type="submit">Decode</button>
</form>
<textarea id="decodeResult" readonly placeholder="Hidden message will appear here"></textarea>
<button id="copyBtn" type="button">Copy</button>
<p id="decodeStatus"></p>

<script>
const decodeForm = document.getElementById("decodeForm");
const decodeResult = document.getElementById("decodeResult");
const decodeStatus = document.getElementById("decodeStatus");
const decodeBtn = decodeForm.querySelector("button");

decodeForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  decodeStatus.textContent = "Decoding…";
  decodeResult.value = "";
  decodeBtn.disabled = true;

  const data = new FormData();
  data.append("image", document.getElementById("decodeImage").files[0]);

  try {
    const res = await fetch("/decode", { method: "POST", body: data });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Decoding failed." }));
      decodeStatus.textContent = "Error: " + (err.detail || "Decoding failed.");
      return;
    }
    const result = await res.json();
    if (result.found) {
      decodeResult.value = result.message;
      decodeStatus.textContent = "Message found.";
    } else {
      decodeStatus.textContent = "No valid message found in this image.";
    }
  } catch {
    decodeStatus.textContent = "Error: could not reach the server.";
  } finally {
    decodeBtn.disabled = false;
  }
});

document.getElementById("copyBtn").addEventListener("click", () => {
  decodeResult.select();
  navigator.clipboard.writeText(decodeResult.value);
});
</script>
```

## Nice-to-haves (optional)

- Show a thumbnail preview when an image is picked (`URL.createObjectURL` on the file).
- Show a live character counter and, once an image is picked, the max capacity for it.
- Add a short note under the dropdown: "Lossless formats only — JPEG would destroy the hidden message."

## Keep it simple

Plain HTML/CSS/JS is enough. Don't pull in React or a bundler for a single form.
