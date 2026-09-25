const downloadButton = 
document.getElementById("downloadButton");
const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const cropCanvas = document.getElementById("cropCanvas");
const cropButton = document.getElementById("cropButton");

const ctx = cropCanvas.getContext("2d");

let croppedCanvas = null;
let startX = 0;
let startY = 0;
let endX = 0;
let endY = 0;
let isSelecting = false;

// Select image
imageInput.addEventListener("change", function () {
    const file = imageInput.files[0];

    if (file) {
        preview.src = URL.createObjectURL(file);

        preview.onload = function () {
            cropCanvas.width = preview.naturalWidth;
            cropCanvas.height = preview.naturalHeight;

            ctx.drawImage(preview, 0, 0);
        };
    }
});

// Start selection
cropCanvas.addEventListener("pointerdown", function (event) {
    const rect = cropCanvas.getBoundingClientRect();

    startX = event.clientX - rect.left;
    startY = event.clientY - rect.top;

    isSelecting = true;
    cropCanvas.setPointerCapture(event.pointerId);
});

// Finish selection
cropCanvas.addEventListener("pointerup", function (event) {
    if (!isSelecting) return;

    const rect = cropCanvas.getBoundingClientRect();

    endX = event.clientX - rect.left;
    endY = event.clientY - rect.top;

    const width = Math.abs(endX - startX);
    const height = Math.abs(endY - startY);

    alert(
        "Selected area: " +
        Math.round(width) +
        " × " +
        Math.round(height)
    );

    isSelecting = false;
});

// Crop image
cropButton.addEventListener("click", function () {
    if (startX === endX || startY === endY) {
        alert("Please select an area first.");
        return;
    }

    const x = Math.min(startX, endX);
    const y = Math.min(startY, endY);
    const width = Math.abs(endX - startX);
    const height = Math.abs(endY - startY);

     croppedCanvas = document.createElement("canvas");
    const croppedCtx = croppedCanvas.getContext("2d");

    croppedCanvas.width = width;
    croppedCanvas.height = height;

    croppedCtx.drawImage(
        preview,
        x,
        y,
        width,
        height,
        0,
        0,
        width,
        height
    );

    document.body.appendChild(croppedCanvas);
});
downloadButton.addEventListener("click", function () {
    if (!croppedCanvas) {
        alert("Please crop an image first.");
        return;
    }

    const link = document.createElement("a");
    link.download = "smartcrop-image.png";
    link.href = croppedCanvas.toDataURL("image/png");
    link.click();
});
