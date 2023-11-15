from googleapiclient.discovery import build
from pytube import YouTube
import os
import subprocess
import shutil
import re
from typing import Union


class ytDL:

    def __init__(self) -> None:
        """
        Parameters:
        self.video_url (str): the URL of video going to be downloaded

        """

        #self.video_url_domain= 'https://www.youtube.com/watch?v='
        #self.video_url_id = 'ym4c711LseE'
        #self.video_url = ''.join([self.video_url_domain, self.video_url_id])
        
        self.video_url = 'https://www.youtube.com/watch?v=ym4c711LseE'
        self.yt = YouTube(self.video_url)
        self.video_title = self.yt.title
        self.uploader = self.yt.author
        self.video_id = self.yt.video_id
        self.download_folder = 'download'
        self.ffmpeg = r"C:\Users\Fredd\AppData\Local\Programs\ffmpeg\bin\ffmpeg"
        if not os.path.exists(self.download_folder):
            os.mkdir(self.download_folder)

    def valid_numeric_input(self, message, selection_list) -> int:
        """
        Summary of the Function:
        Check whether the input format is numeric

        Parameters:
        message (str)
        selection_list (list)

        Returns:
        user_input_index (int)

        """
        user_input = input(message)

        while True:
            try:
                user_input_index = int(user_input) - 1
                if user_input_index in range(len(selection_list)):
                        return user_input_index
                else:
                    print('\nPlease enter a valid option\n')
                    return self.valid_numeric_input(message, selection_list)

            except ValueError:
                print('\nPlease enter a valid option\n')
                return self.valid_numeric_input(message, selection_list)
            
            
    def replace_special_characters(self, input_string) -> str:
        """
        Summary of the Function:
        Check whether the string includes invalid symbols ([\/:*?"<>|]) and replace it

        Parameters:
        input_string (str)

        Returns:
        replaced_string (str)

        """
        pattern = re.compile(r'[\/:*?"<>|]')
        replaced_string = re.sub(pattern, '', input_string)
        return replaced_string

    def combine_video_audio(self) -> None:
        """
        Summary of the Function:
        Combine the original video and audio file into one single file and delete the original video and audio files

        """
        for file in os.listdir(self.video_download_dir):
                if file.endswith('mp4') == True:
                    video = file
                    
                audio_dir = os.path.join(self.video_download_dir, 'audio')
                for file in os.listdir(audio_dir):
                    audio = file

        cmd_list = [self.ffmpeg, "-i", os.path.join(self.video_download_dir, f'{video}'), "-i", os.path.join(audio_dir, f'{audio}'), "-c:v", "copy", "-strict", "experimental", "-y", os.path.join(self.video_download_dir, f"New {video}.{self.video_format}")]

        if subprocess.run(cmd_list).returncode == 0:
            print ("Script ran successfully")
        else:
            print ("There was an error running your script")

        shutil.rmtree(audio_dir)
        os.remove(os.path.join(self.video_download_dir, f'{video}'))
        os.rename(os.path.join(self.video_download_dir, f'New {video}.{self.video_format}'), os.path.join(self.video_download_dir, f'{video}.{self.video_format}'))

    def yt_download_selector(self) -> None:

        """
        Summary of the Function:
        Step1: Select whether downing the video as a video file or a audio only file
        Step2: If downloading as a video file, select the resolution; If downloading as an audio file, selecy the kbps

        """

        video_streams = self.yt.streams.filter(type='video', file_extension='mp4')
        resolution_list = [(stream.resolution, str(stream.is_progressive), stream.type) for stream in video_streams]
        audio_streams = self.yt.streams.filter(type='audio', file_extension='mp4')
        kbps_list = [(stream.abr, str(stream.is_progressive), stream.type) for stream in audio_streams]

        selector_dict = {}
        selector_dict['video'] = {}
        selector_dict['audio'] = {}

        for index, element in enumerate(resolution_list):
            if element[1] == 'True':
                selector_dict['video'][element[0]] = video_streams[index]
            else:
                if element[0] not in selector_dict:
                    selector_dict['video'][element[0]] = video_streams[index]

        for index, element in enumerate(kbps_list):
            selector_dict['audio'][element[0]] = audio_streams[index]

        video_or_audio = ['video', 'audio']
            
        message = '''----------------------------
Would you like to download it as a video or audio?

1. Video
2. Audio

----------------------------\n''' 

        user_input = self.valid_numeric_input(message, video_or_audio)

        resolution_list = [str(res) + 'p' for res in sorted([int(k[:-1]) for k in selector_dict['video']], reverse=True)]
        kbps_list = [str(kbps) + 'kbps' for kbps in sorted([int(k[:-4]) for k in selector_dict['audio']], reverse=True)]

        if user_input == 0:
            message_list = []
            message_start = f'''----------------------------
Please choose a desired video resolution\n\n'''
            message_list.append(message_start)
            for index, res in enumerate(resolution_list):
                message_list.append(f'{index + 1}: {res}\n')

            message_end = '''\n----------------------------\n''' 
            message_list.append(message_end)
            res_message = ''.join(message_list)
           

            user_input = int(self.valid_numeric_input(res_message, resolution_list))
            
            selected_video = selector_dict['video'][resolution_list[user_input]]
            
            self.video_format = selected_video.mime_type.split('/')[1]
            self.video_resolution = selected_video.resolution 
            file_fullname = ' '.join([self.video_resolution, self.video_title, self.video_format])
            self.file_fullname = self.replace_special_characters(file_fullname )
            self.video_download_dir = os.path.join(self.download_folder, self.file_fullname)

            if not os.path.exists(self.video_download_dir):
                txt_file = 'description.txt'
                txt_path = os.path.join(self.video_download_dir,  txt_file)
                selected_video.download(output_path=self.video_download_dir)
                with open(txt_path, 'w') as file:
                    file.write(f'Title: {self.video_title}\n')
                    file.write(f'YT Channel: {self.uploader}\n')
                    file.write(f'Res: {self.video_resolution}\n')
                    file.write(f'Type: Video')

                if selected_video.is_progressive == False:
                    audio_for_video = self.yt.streams.filter(file_extension='mp4').get_audio_only()
                    audio_download_dir = os.path.join(self.download_folder , self.file_fullname, "audio")
                    audio_for_video.download(output_path=audio_download_dir)

                self.combine_video_audio()

                print(f'''------------------------------\n
Title: {self.video_title}
YT Channel: {self.uploader}
Res: {self.video_resolution}
Type: Video

Downloaded Successfully
------------------------------''')

            else:
                print('\n************ file has already existed ************')
                exit()

        elif user_input == 1:
            message_list = []
            message_start = f'''----------------------------
Please choose a desired audio kbps\n\n'''
            message_list.append(message_start)
            for index, kbps in enumerate(kbps_list):
                message_list.append(f'{index + 1}: {kbps}\n')

            message_end = '''\n----------------------------\n''' 
            message_list.append(message_end)
            kbps_message = ''.join(message_list)

            user_input = int(self.valid_numeric_input(kbps_message, kbps_list))
            
            selected_audio = selector_dict['audio'][kbps_list[user_input]]
            self.audio_format = selected_audio.mime_type.split('/')[1]
            self.video_kpps = selected_audio.abr
            file_fullname = ' '.join([self.video_kpps, self.video_title, self.audio_format])
            self.file_fullname = self.replace_special_characters(file_fullname )
            self.audio_download_dir = os.path.join(self.download_folder, self.file_fullname)

            if not os.path.exists(self.audio_download_dir):
                txt_file = 'description.txt'
                txt_path = os.path.join(self.audio_download_dir,  txt_file)
                selected_audio.download(output_path=self.audio_download_dir)
                with open(txt_path, 'w') as file:
                    file.write(f'Title: {self.video_title}\n')
                    file.write(f'YT Channel: {self.uploader}\n')
                    file.write(f'Kbps: {self.video_kpps}\n')
                    file.write(f'Type: Audio')

                print(f'''------------------------------\n
Title: {self.video_title}
YT Channel: {self.uploader}
Kbps: {self.video_kpps}
Type: Audio

Downloaded Successfully
------------------------------''')

            else:
                print('\n************ file has already existed ************')
                exit()

def main():

    ytdl = ytDL()

    def run():
        ytdl.yt_download_selector()

    run()

if __name__=='__main__':
    main()


