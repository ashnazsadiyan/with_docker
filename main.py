from fastapi import FastAPI, Response
from mangum import Mangum
import uvicorn
# import ssl
import subprocess
from typing import List  # Import List type for questions
from pydantic import BaseModel
import whisper
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
from pydub import AudioSegment
import os
import m3u8
import requests

# import os


app = FastAPI()
handler = Mangum(app)

# ssl._create_default_https_context = ssl._create_unverified_context
# router = APIRouter()


class Question:
    def __init__(self, answer: str, start_time: float, end_time: float):
        self.answer = answer
        self.start_time = start_time
        self.end_time = end_time
        self.expected = ""
        self.given = ""
        self.result = 0


class QuestionsAnswers(BaseModel):
    answer: str
    start_time: int
    end_time: int
    question: str
    identity: str


class Questions(BaseModel):
    link: str
    questions: List[QuestionsAnswers]
    identification: str

# zs
def get_audio(start_time: float, end_time: float, _id: str, identification: str):
    audio = AudioSegment.from_file(f'{identification}.WAV')
    audio_segment = audio[start_time:end_time]
    extracted_file = f"{_id}.mp3"
    audio_segment.export(extracted_file, format='mp3')


def get_text(file_name: str):
    model = whisper.load_model("base")
    result = model.transcribe(file_name, fp16=False)
    os.remove(file_name)
    return result["text"]


def check_text(expected_answer: str, given_answer: str, question: str):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([expected_answer, given_answer], convert_to_tensor=True)
    cosine_score = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    similarity_score = cosine_score.item()

    print(f"Similarity Score for question {question}: {similarity_score}")
    return similarity_score


def convert_seconds(seconds: int):
    timestamp_sec = seconds / 1000  # Convert milliseconds to seconds
    date = datetime.fromtimestamp(timestamp_sec)
    print(date.strftime("%Y-%m-%d %H:%M:%S"))
    return date.strftime("%Y-%m-%d %H:%M:%S")


def download_audio_from_m3u8(url, output_path):
    # Fetch the HLS playlist
    playlist = m3u8.load(url)

    # Find the audio stream in the playlist
    audio_uri = None
    for playlist_entry in playlist.segments:
        if playlist_entry.uri.endswith('.ts'):  # Adjust this condition based on your playlist structure
            audio_uri = playlist_entry.uri
            break

    if audio_uri:
        # Download the audio segment
        audio_url = f"{url.rsplit('/', 1)[0]}/{audio_uri}"  # Construct absolute URL
        audio_data = requests.get(audio_url).content

        # Save the audio data to a WAV file
        with open(output_path, 'wb') as file:
            file.write(audio_data)

        print(f"Audio downloaded and saved to {output_path}")
    else:
        print("Audio segment not found in the playlist")


@app.get('/')
def index():
    return {"message": "recroots ai-models"}


@app.post("/get-score")
async def get_score(questions: Questions, response: Response):
    try:
        download_audio_from_m3u8(questions.link,f'{questions.identification}.WAV')
        # subprocess.run(['/usr/bin/ffmpeg', '-i', questions.link, '-b:a', '64k', f'{questions.identification}.WAV'])
        new_result = []
        index = 0
        for question in questions.questions:
            if question.answer:
                if index > 0:
                    start_time = question.start_time - questions.questions[0].start_time
                    end_time = start_time + (question.end_time - question.start_time)
                else:
                    start_time = 0
                    end_time = question.end_time - question.start_time

                print(start_time, 'start_time', end_time, 'end_time')
                get_audio(start_time, end_time, question.identity, questions.identification)
                audio_text = get_text(f"{question.identity}.mp3")
                result = check_text(question.answer, audio_text, question.question)
                new_question = Question(question.answer, question.start_time, question.end_time)
                new_question.expected = question.answer
                new_question.given = audio_text
                new_question.result = result
                new_result.append(new_question)
                index = index + 1
            else:
                response.status_code = 400
                return {"message": "no data found"}
            # os.remove(f'{questions.identification}.WAV')
        return {"message": new_result}
    # Return the list of new questions with results

    except Exception as e:
        print(e)
        response.status_code = 500
        return {"message": "something went wrong"}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=9000)
#