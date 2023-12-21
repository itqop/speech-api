import wave
from vosk import Model, KaldiRecognizer, SetLogLevel
from moviepy.editor import VideoFileClip
import tempfile
import os
import webrtcvad 

class SST:
    def __init__(self, model_path, lang="en-us"):
        SetLogLevel(0)
        self.model = Model(lang=lang, model_path=model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
        self.recognizer.SetPartialWords(True)

    def process_audio_with_timing(self, audio_path):
        with wave.open(audio_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                raise ValueError("Audio file must be WAV format mono PCM.")

            vad_timing = []
            in_speech = False
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break

                is_speech = self.vad.is_speech(data, sample_rate=wf.getframerate())
                if is_speech and not in_speech:
                    vad_timing.append(wf.tell() / wf.getframerate())
                elif not is_speech and in_speech:
                    vad_timing.append(wf.tell() / wf.getframerate())

                in_speech = is_speech

                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    print(result)


                else:
                    partial_result = self.recognizer.PartialResult()
                    print(partial_result)

            final_result = self.recognizer.FinalResult()
            print(final_result)


            return final_result, vad_timing

    def process_video(self, video_path):

        audio_tempfile = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with VideoFileClip(video_path) as video:
            audio = video.audio
            audio.write_audiofile(audio_tempfile.name)

        result = self.process_audio(audio_tempfile.name)

        os.remove(audio_tempfile.name)

        return result
    
    def _extract_audio_from_video(self, video_path):
        audio_tempfile = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with VideoFileClip(video_path) as video:
            audio = video.audio
            audio.write_audiofile(audio_tempfile.name)
        return audio_tempfile.name

    def _cleanup_temp_file(self, file_path):
        os.remove(file_path)

    def set_model_language(self, lang):
        self.model.set_string('lang', lang)

    def set_recognizer_params(self, sample_rate=16000, words=True, partial_words=True):
        self.recognizer.SetSampleRate(sample_rate)
        self.recognizer.SetWords(words)
        self.recognizer.SetPartialWords(partial_words)