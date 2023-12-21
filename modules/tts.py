from vosk_tts import Model, Synth
import os
from moviepy.editor import AudioFileClip

class TTS:
    def __init__(self, model_name="vosk-model-tts-ru-0.4-multi"):
        self.model = Model(model_name=model_name)
        self.synth = Synth(self.model)

    def text_to_speech(self, text, output_path, speaker_id=1):
        self.synth.synth(text, output_path, speaker_id)

    def batch_text_to_speech(self, text_list, output_folder):
        for text, speaker_id in text_list:
            output_path = f"{output_folder}/output_{speaker_id}.wav"
            self.text_to_speech(text, output_path, speaker_id)

    @staticmethod
    def create_text_speaker_tuples(final_result, vad_timing):
        text_speaker_tuples = []
        current_speaker_id = 1

        for start, end in zip(vad_timing[::2], vad_timing[1::2]):
            text_speaker_tuples.append((final_result, current_speaker_id))
            current_speaker_id = 4 if current_speaker_id == 1 else 1

        return text_speaker_tuples

    @staticmethod
    def create_output_folder(folder_name):
        os.makedirs(folder_name, exist_ok=True)

    def set_model(self, model_name):
        self.model.set_string('model_name', model_name)
        self.synth = Synth(self.model)

    def change_speaker_id(self, text_speaker_tuples, new_speaker_id):
        return [(text, new_speaker_id) for text, _ in text_speaker_tuples]

    def combine_audio_files(self, audio_paths, output_path):
        clips = [AudioFileClip(audio_path) for audio_path in audio_paths]
        combined_clip = concatenate_audioclips(clips)
        combined_clip.write_audiofile(output_path)