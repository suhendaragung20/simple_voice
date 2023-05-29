from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
source_folder = 'source'

@app.route('/')
def home():
    message = request.args.get('message')
    return render_template('index.html', message=message)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['notulenFile']
    if file:
        filename = file.filename
        file.save(os.path.join(source_folder, filename))
        message = 'File notulen berhasil diunggah dan disimpan: ' + filename
        return redirect(url_for('home', message=message))
    else:
        return 'Tidak ada file yang diunggah.'

@app.route('/queue')
def queue():
    files = os.listdir(source_folder)
    return render_template('queue.html', files=files)

@app.route('/transcribe/<filename>')
def transcribe(filename):
    # Perform transcription on the selected file
    # Add your transcription logic here
    from moviepy.video.io.VideoFileClip import VideoFileClip

    # path file mp4 yang akan diubah ke mp3
    mp4_file_path = source_folder+"/"+filename

    # path file mp3 hasil konversi
    mp3_file_path = "audio.wav"

    from pydub import AudioSegment

    # load the input file using pydub
    audio = AudioSegment.from_file(mp4_file_path)

    # export the audio in WAV format using pydub
    audio.export(mp3_file_path, format="wav")

    import wave
    import math


    # fungsi untuk memecah file WAV
    filename = 'audio.wav'
    chunk_duration = 60.0
    chunk_index = 0
    # membuka file WAV
    with wave.open(filename, 'rb') as wav_file:
        # mendapatkan parameter file WAV
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        total_frames = wav_file.getnframes()

        # menghitung jumlah frame per chunk
        chunk_size = int(math.ceil(chunk_duration * frame_rate))

        # inisialisasi variabel
        current_frame = 0
        chunk_index = 0

        # memproses setiap chunk
        while current_frame < total_frames:
            # membaca data frame dari file WAV
            wav_file.setpos(current_frame)
            frames = wav_file.readframes(chunk_size)

            # menulis data frame ke file WAV baru
            chunk_filename = f'{filename.split(".")[0]}_{chunk_index}.wav'
            with wave.open(chunk_filename, 'wb') as chunk_file:
                chunk_file.setnchannels(num_channels)
                chunk_file.setsampwidth(sample_width)
                chunk_file.setframerate(frame_rate)
                chunk_file.writeframes(frames)

            # update variabel
            current_frame += chunk_size
            chunk_index += 1

    import requests
    import json

    url = 'https://telkom-bac-api.apilogy.id/Speech_To_Text_Service/1.0.0/stt_inference'
    api_key = 'YPLCmjnu7pUpBDToZRcMH5WOrIousL8j'
    result = ""
    start = 0
    end = chunk_index
    resultfinal = ""
    for i in range(start,end):
        file_path = 'audio_'+str(i)+'.wav'
        lang = 'indonesian'

        headers = {'accept': 'application/json', 'x-api-key': api_key}
        files = {'audio': (file_path, open(file_path, 'rb'), 'audio/x-wav')}
        data = {'lang': lang}

        response = requests.post(url, headers=headers, data=data, files=files)
        response_json = response.json()
        #print(response_json)
        result = json.dumps(response_json["data"]["all_text"])
        resultfinal = resultfinal + " " + result
    #message = request.args.get('message')
    return render_template('transcribe.html', message=resultfinal)

if __name__ == '__main__':
    app.run()
