import os
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip, AudioArrayClip
from moviepy.editor import concatenate_videoclips
import numpy as np

class Video:
    def __init__(self):
        pass

    async def download_video_from_url(self, video_url, output_path):
        # Download a video from a given URL and save it to the specified output path
        # Note: You may use a library like youtube_dl for more advanced video downloading
        command = ["ffmpeg", "-i", video_url, "-c", "copy", output_path]
        subprocess.run(command)

    async def load_video_from_path(self, video_path):
        # Load a video from the specified file path using moviepy
        return VideoFileClip(video_path)

    async def replace_audio_in_range(self, video_clip, audio_path, start_time, end_time):

        original_audio = video_clip.audio

        new_audio_clip = AudioFileClip(audio_path)

        new_audio_clip = new_audio_clip.subclip(start_time, end_time)

        original_duration = original_audio.duration

        if end_time > original_duration:
            silence_duration = end_time - original_duration
            silence = AudioArrayClip(np.zeros(int(silence_duration * original_audio.fps)),
                                     fps=original_audio.fps)
            new_audio_clip = self.concatenate_audioclips([new_audio_clip, silence])

        final_audio_clip = self.concatenate_audioclips([
            original_audio.subclip(0, start_time),
            new_audio_clip,
            original_audio.subclip(end_time, original_duration)
        ])

        video_clip = video_clip.set_audio(final_audio_clip)

        return video_clip

    @staticmethod
    async def save_video(video_clip, output_path):
        video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    @staticmethod
    async def get_video_duration(video_clip):
        return video_clip.duration


    @staticmethod
    async def create_output_folder(folder_name):
        os.makedirs(folder_name, exist_ok=True)
    
    async def concatenate_video_clips(self, video_clips):
        # Concatenate a list of video clips into a single clip

        # Make sure the list is not empty
        if not video_clips:
            raise ValueError("Empty list of video clips")

        # Check if all clips have the same resolution and fps
        first_clip = video_clips[0]
        for clip in video_clips[1:]:
            if clip.size != first_clip.size or clip.fps != first_clip.fps:
                raise ValueError("All video clips must have the same resolution and fps for concatenation")

        # Concatenate the clips
        concatenated_clip = concatenate_videoclips(video_clips)

        return concatenated_clip