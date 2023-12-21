from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from modules import SST
from modules import TTS
from modules import Translate
from modules import Video
import os
import shutil

app = FastAPI()

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
AUDIO_FOLDER = "audio"
VIDEO_FOLDER = "video"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

sst = SST()
tts = TTS()
translator = Translate()
video_manager = Video()

@app.post("/process_video/")
async def process_video(video_file: UploadFile = File(...)):
    video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
    with open(video_path, "wb") as video:
        video.write(video_file.file.read())

    audio_output_path = os.path.join(AUDIO_FOLDER, f"{os.path.splitext(video_file.filename)[0]}.wav")
    await video_manager.extract_audio(video_path, audio_output_path)

    final_result, vad_timing = await sst.process_audio_with_timing(audio_output_path)

    translated_text = await translator.translate_text(final_result, source_lang="en", target_lang="ru")

    text_speaker_tuples = [(translated_text, 1)]
    await tts.batch_text_to_speech(text_speaker_tuples, output_folder=OUTPUT_FOLDER)

    output_video_path = os.path.join(VIDEO_FOLDER, f"{os.path.splitext(video_file.filename)[0]}_processed.mp4")
    video_clip = await video_manager.load_video_from_path(video_path)
    for start, end in zip(vad_timing[::2], vad_timing[1::2]):
        await video_manager.replace_audio_in_range(video_clip, os.path.join(OUTPUT_FOLDER, "output_1.wav"), start, end)

    await video_manager.save_video(video_clip, output_video_path)

    shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    shutil.rmtree(AUDIO_FOLDER)
    os.makedirs(AUDIO_FOLDER, exist_ok=True)
    shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    return FileResponse(output_video_path, media_type="video/mp4", filename=output_video_path)
