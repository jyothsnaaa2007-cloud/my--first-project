from flask import Flask, request, jsonify
from PIL import Image
import torch
from torchvision import models, transforms

app = Flask(__name__)

# Load AI model
model = models.mobilenet_v2(weights=None)

model.classifier[1] = torch.nn.Sequential(
    torch.nn.Dropout(0.2),
    torch.nn.Linear(model.classifier[1].in_features, 38)
)

model.load_state_dict(
    torch.load("mobilenetv2_plant.pth", map_location="cpu")
)

model.eval()

# Plant disease classes
class_names = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry___Powdery_mildew",
    "Cherry___healthy",
    "Corn___Cercospora_leaf_spot",
    "Corn___Common_rust",
    "Corn___healthy",
    "Corn___Northern_Leaf_Blight",
    "Grape___Black_rot",
    "Grape___Esca",
    "Grape___Leaf_blight",
    "Grape___healthy",
    "Orange___Haunglongbing",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper___Bacterial_spot",
    "Pepper___healthy",
    "Potato___Early_blight",
    "Potato___healthy",
    "Potato___Late_blight",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___healthy",
    "Strawberry___Leaf_scorch",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

# Simple recommendations
recommendations = {
    "Tomato___Early_blight":
        "Remove affected leaves and monitor the plant.",

    "Tomato___Late_blight":
        "Remove affected leaves and avoid excess moisture.",

    "Tomato___healthy":
        "The plant appears healthy. Continue regular monitoring.",

    "Potato___Early_blight":
        "Remove affected leaves and monitor the crop.",

    "Potato___Late_blight":
        "Remove affected plant material and monitor the crop.",

    "Apple___Apple_scab":
        "Remove affected leaves and monitor the plant."
}


@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>SmartCrop</title>

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: #f2f7f2;
            padding: 30px;
        }

        h1 {
            color: #2e7d32;
        }

        button {
            padding: 12px 20px;
            margin: 15px;
            cursor: pointer;
            background: #2e7d32;
            color: white;
            border: none;
            border-radius: 8px;
        }

        #preview {
            max-width: 350px;
            width: 100%;
            margin-top: 20px;
            display: none;
            border-radius: 10px;
        }

        #result {
            margin-top: 25px;
        }
    </style>
</head>

<body>

    <h1>SmartCrop 🌱</h1>

    <p>Smart Crop Image Analysis for Agriculture</p>

    <input type="file" id="imageInput" accept="image/*">

    <br>

    <img id="preview">

    <br>

    <button onclick="analyze()">Analyze Crop</button>

    <div id="result"></div>


    <script>

        const imageInput = document.getElementById("imageInput");
        const preview = document.getElementById("preview");

        imageInput.addEventListener("change", function() {

            const file = imageInput.files[0];

            if (!file) {
                return;
            }

            preview.src = URL.createObjectURL(file);
            preview.style.display = "block";
        });


        async function analyze() {

            const file = imageInput.files[0];

            if (!file) {

                alert("Please select an image first.");

                return;
            }

            document.getElementById("result").innerHTML =
                "<p>🔍 Analyzing image...</p>";


            const formData = new FormData();

            formData.append("image", file);


            try {

                const response = await fetch("/predict", {

                    method: "POST",

                    body: formData

                });


                const result = await response.json();


                if (!response.ok) {

                    throw new Error(
                        result.error || "Prediction failed"
                    );
                }


                document.getElementById("result").innerHTML =

                    "<h2>🌱 Analysis Result</h2>" +

                    "<p><strong>Possible condition:</strong> " +
                    result.disease +
                    "</p>" +

                    "<p><strong>Model confidence:</strong> " +
                    result.confidence +
                    "%</p>" +

                    "<p><strong>Recommendation:</strong> " +
                    result.recommendation +
                    "</p>";

            }

            catch (error) {

                document.getElementById("result").innerHTML =
                    "<p>❌ AI analysis failed.</p>";

                console.error(error);
            }
        }

    </script>

</body>
</html>
"""


@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:

        return jsonify({
            "error": "No image uploaded"
        }), 400


    file = request.files["image"]

    image = Image.open(file).convert("RGB")

    input_tensor = transform(image).unsqueeze(0)


    with torch.no_grad():

        output = model(input_tensor)


    probabilities = torch.softmax(output, dim=1)

    predicted_class = torch.argmax(
        output,
        dim=1
    ).item()

    confidence = (
        probabilities[0][predicted_class].item()
        * 100
    )

    disease = class_names[predicted_class]


    recommendation = recommendations.get(

        disease,

        "Monitor the plant regularly and consult a local agriculture expert if symptoms continue."

    )


    return jsonify({

        "disease": disease,

        "confidence": round(
            confidence,
            2
        ),

        "recommendation": recommendation

    })


if __name__ == "__main__":

    app.run(
        debug=True
    )