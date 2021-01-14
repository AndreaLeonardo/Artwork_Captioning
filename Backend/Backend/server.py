import os
from os.path import isfile, join
from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from ImageCaptionLearner import ImageCaptionLearner

UPLOAD_FOLDER = './images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

imgCaptLrn = ImageCaptionLearner()
imgCaptLrn.load("bestmodel")

app = Flask(__name__)
app.secret_key = b'sese'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global imgCaptLrn

    if request.method == 'POST':
        # check if the post request has the file part
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            evaluation = imgCaptLrn.predict(path, 5)
            return jsonify(evaluation)
    return jsonify({"data": "False"})


if __name__ == '__main__':
    port = 8000  # the custom port you want
    app.run(host='0.0.0.0', port=port, debug=True)