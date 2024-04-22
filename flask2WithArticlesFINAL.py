from flask import Flask, render_template, request, redirect
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.models import load_model
from io import BytesIO
import numpy as np

app = Flask(__name__, template_folder='templates', static_url_path='/static')

# Define constants
IMAGE_SIZE = 128
NUM_CLASSES = 5
CLASS_NAMES = ['Melanoma', 'Ringworm', 'Vitiligo', 'Warts', 'Normal']

# Load your trained model
model = load_model('trained_vgg_model_afterChangingDataset.keras')

# # Dictionary mapping disease names to article website URLs
# disease_articles = {
#     # 'Actinic keratosis': 'https://example.com/actinic-keratosis-article',
#     'Melanoma': 'https://www.healthline.com/health/skin-cancer/melanoma',
#     'Ringworm': 'https://www.healthline.com/health/ringworm',
#     'Vitiligo': 'https://www.healthline.com/health/skin-disorders/vitiligo-pictures',
#     'Warts': 'https://www.healthline.com/health/skin/warts',
#     'Normal': 'https://www.healthline.com/health/beauty-skin-care/skin-types-care'
# }

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    # Load the image from the POST request
    img_file = request.files['image']

    # Read the file data as bytes
    img_bytes = img_file.read()

    # Create a file-like object from the bytes
    img_stream = BytesIO(img_bytes)

    # Load the image from the file-like object
    img = image.load_img(img_stream, target_size=(IMAGE_SIZE, IMAGE_SIZE))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    # Preprocess the image
    img_array = preprocess_input(img_array)

    # Make prediction using your trained model
    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions, axis=1)

    # Calculate the probability of the predicted disease
    probability = predictions[0][predicted_class_index[0]] * 100  # Convert to percentage

    # Get the predicted disease name
    predicted_disease = CLASS_NAMES[predicted_class_index[0]-1]

    # Render the template with the predicted disease name and probability
    return render_template('index.html', predicted_disease=predicted_disease, probability=probability)


@app.route('/get_preliminary_treatment')
def get_preliminary_treatment():
    predicted_disease = request.args.get('predicted_disease')
    if predicted_disease:
        # Use a mapping dictionary to map predicted disease names to template file names
        treatment_files = {
            # 'Actinic keratosis': 'preliminary_treatment/actinic_keratosis.html',
            'Melanoma': 'preliminary_treatment/melanoma.html',
            'Ringworm': 'preliminary_treatment/ringworm.html',
            'Vitiligo': 'preliminary_treatment/vitiligo.html',
            'Warts': 'preliminary_treatment/warts.html',
            'Normal': 'https://www.healthline.com/health/beauty-skin-care/skin-types-care'
        }

        # Get the file name for the predicted disease
        template_file = treatment_files.get(predicted_disease)

        # If the template file exists, render it
        if template_file:
            return render_template(template_file)

    # If no file found or predicted disease not provided, redirect to the homepage
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)