from fastapi import FastAPI, Response
from mangum import Mangum
# import uvicorn
import ssl
import subprocess
from typing import List  # Import List type for questions
# from pydantic import BaseModel
# import whisper
# from sentence_transformers import SentenceTransformer, util
from datetime import datetime
from pydub import AudioSegment
import os
import boto3

# import os


app = FastAPI()
handler = Mangum(app)

ssl._create_default_https_context = ssl._create_unverified_context


# router = APIRouter()


# class Question:
#     def __init__(self, answer: str, start_time: float, end_time: float):
#         self.answer = answer
#         self.start_time = start_time
#         self.end_time = end_time
#         self.expected = ""
#         self.given = ""
#         self.result = 0
#
#
# class QuestionsAnswers(BaseModel):
#     answer: str
#     start_time: int
#     end_time: int
#     question: str
#     identity: str
#
#
# class Questions(BaseModel):
#     link: str
#     questions: List[QuestionsAnswers]
#     identification: str

# zs
# def get_audio(start_time: float, end_time: float, _id: str, identification: str):
#     audio = AudioSegment.from_file(f'/tmp/{identification}.WAV')
#     audio_segment = audio[start_time:end_time]
#     extracted_file = f"/tmp/{_id}.mp3"
#     audio_segment.export(extracted_file, format='mp3')


# def get_text(file_name: str):
#     model = whisper.load_model("base")
#     result = model.transcribe(file_name, fp16=False)
#     # os.remove(file_name)
#     return result["text"]


# def check_text(expected_answer: str, given_answer: str, question: str):
#     model = SentenceTransformer('all-MiniLM-L6-v2')
#     embeddings = model.encode([expected_answer, given_answer], convert_to_tensor=True)
#     cosine_score = util.pytorch_cos_sim(embeddings[0], embeddings[1])
#     similarity_score = cosine_score.item()
#
#     print(f"Similarity Score for question {question}: {similarity_score}")
#     return similarity_score


def convert_seconds(seconds: int):
    timestamp_sec = seconds / 1000  # Convert milliseconds to seconds
    date = datetime.fromtimestamp(timestamp_sec)
    print(date.strftime("%Y-%m-%d %H:%M:%S"))
    return date.strftime("%Y-%m-%d %H:%M:%S")


def save_to_s3(bucket_name, object_key, content):
    # AWS credentials setup (make sure you handle credentials securely)
    aws_access_key = 'AKIAZC3RQOWY2DXBO72Q'
    aws_secret_key = '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'

    # Initialize S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

    # Upload content to S3
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=content)


AudioSegment.converter = '/usr/share/ffmpeg'


@app.get("/")
def get_score(response: Response):
    try:
        command = [
            '/usr/share/ffmpeg',
            '-i',
            'https://d8cele0fjkppb.cloudfront.net/ivs/v1/624618927537/y16bDr6BzuhG/2023/12/14/11/3/0lm3JnI0dvgo/media/hls/master.m3u8',
            '-b:a', '64k',
            '-f', 'wav',  # Force output format to WAV
            'pipe:1'  # Send output to stdout
        ]

        # Run FFmpeg command and capture the output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            # Specify your S3 bucket name and object key
            bucket_name = 'reckognitionnew'
            object_key = '657ae0c1ec9a6e346d80318f.WAV'  # Replace with desired object key

            # Save the output to S3
            save_to_s3(bucket_name, object_key, stdout)
            print(f"File uploaded to S3 bucket: {bucket_name}/{object_key}")
        else:
            print(f"FFmpeg command failed with error: {stderr.decode('utf-8')}")

    except Exception as e:
        print(f"An error occurred: {e}")

# @app.get("/")
# def get_score(response: Response):
#     try:
#         print(os.path.exists('/usr/share/ffmpeg'),'file exist')
#         # download_audio_from_m3u8(questions.link,f'{questions.identification}.WAV')
#         subprocess.run(['/usr/share/ffmpeg', '-i', 'https://d8cele0fjkppb.cloudfront.net/ivs/v1/624618927537/y16bDr6BzuhG/2023/12/14/11/3/0lm3JnI0dvgo/media/hls/master.m3u8','-b:a','64k','/usr/share/657ae0c1ec9a6e346d80318f.WAV'])
#         new_result = []
#         index = 0
#         # for question in questions.questions:
#         #     if question.answer:
#         #         if index > 0:
#         #             start_time = question.start_time - questions.questions[0].start_time
#         #             end_time = start_time + (question.end_time - question.start_time)
#         #         else:
#         #             start_time = 0
#         #             end_time = question.end_time - question.start_time
#         #
#         #         print(start_time, 'start_time', end_time, 'end_time')
#         # get_audio(1702551805057, 168136, '657ae0c1ec9a6e346d803190', '657ae0c1ec9a6e346d80318f')
#         # audio_text = get_text("/tmp/657ae0c1ec9a6e346d803190.mp3")
#         #         result = check_text(question.answer, audio_text, question.question)
#         #         new_question = Question(question.answer, question.start_time, question.end_time)
#         #         new_question.expected = question.answer
#         #         new_question.given = audio_text
#         #         new_question.result = result
#         #         new_result.append(new_question)
#         #         index = index + 1
#         #     else:
#         #         response.status_code = 400
#         #         return {"message": "no data found"}
#         #     # os.remove(f'{questions.identification}.WAV')
#         # print(os.path.exists('/tmp/657ae0c1ec9a6e346d80318f.WAV'),'file exist')
#         return {"message": 'audio_text'}
#     # Return the list of new questions with results
#
#     except Exception as e:
#         print(e)
#         response.status_code = 500
#         return {"message": e}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=9000)
#
