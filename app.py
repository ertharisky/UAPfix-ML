from flask import Flask, request, render_template, jsonify
from keras.models import load_model
import numpy as np
import os
from PIL import Image
from tensorflow.keras.preprocessing import image as tf_image
from datetime import datetime


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'

model = load_model('model.h5')
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Ambil waktu awal prediksi
        start_time = datetime.now()

        # Ambil file gambar dari permintaan POST
        file = request.files['file']
        file.save(os.path.join('static', 'temp.jpg'))

        # Lakukan preprocessing pada gambar
        img = Image.open(file).convert('RGB').resize((150, 150))
        img_array = tf_image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Lakukan prediksi dengan model
        pred = model.predict(img_array)[0]

        # Ambil waktu akhir prediksi
        end_time = datetime.now()

        # Hitung lama waktu prediksi
        prediction_time = end_time - start_time

        # Ambil label yang diprediksi
        predicted_label = str(np.argmax(pred))
        labels = ['paper', 'rock', 'scissors']
        actual_label = labels[int(predicted_label)]

        # Ambil nama file gambar yang diprediksi
        image_name = 'temp.jpg'

        # Hitung akurasi prediksi
        respon_model = [round(elem * 100, 2) for elem in pred]

        return predict_result(model, actual_label, image_name, prediction_time, respon_model)
        # # Return hasil prediksi dan informasi lainnya dalam bentuk JSON
        # return jsonify({
        #     'prediction': prediction.tolist(),
        #     'predicted_label': predicted_label,
        #     'actual_label': actual_label,
        #     'accuracy': accuracy,
        #     'prediction_time': str(prediction_time),
        #     'image_name': image_name
        # })
    
    
def predict_result(model,  actual_label, image_name, prediction_time, respon_model):
    class_list = {'paper': 0, 'rock': 1, 'scissors': 2}
    idx_pred = respon_model.index(max(respon_model))
    labels = list(class_list.keys())
    return render_template('/result_select.html', labels=labels,
                            probs=respon_model, model=model, pred=idx_pred,
                            run_time=prediction_time, img=image_name)


if __name__ == '__main__':
    app.run(debug=True)
