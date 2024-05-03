import os
import shutil
import json
import pickle
import threading
from math import ceil
from video_to_frames import VideoFramesExtractor
from img_ascii_convertor import ImgAsciiConvertor
from ascii_video_player import AsciiVideoPlayer

OUTPUT_JSON = 'JSON'
OUTPUT_PICKLE = 'PICKLE'

OUTPUT_TYPES = {
    'j': OUTPUT_JSON,
    'p': OUTPUT_PICKLE
}

class VideoAsciiConvertor:
    def __init__(self, resolution: tuple) -> None:
        self._input_path = os.path.abspath('./input/video_ascii')
        self._output_path = os.path.abspath('./output/video_ascii')
        self._temp_path = os.path.abspath('./temp')

        self._frame_extractor = VideoFramesExtractor(self._temp_path)
        self._image_convertor = ImgAsciiConvertor(resolution, False)
        self._video_player = AsciiVideoPlayer()

        self._output_type = OUTPUT_JSON
        self._output_frames = {}

    def convert_input_files(self) -> None:
        for file in os.listdir(self._input_path):
            print(f'Converting {file} to ascii...')
            self.convert(os.path.join(self._input_path, file))

    def convert(self, video_path: str, play_after_finish: bool = False) -> str:
        if video_path == '':
            for file in os.listdir(self._input_path):
                if not file.startswith('.'):
                    video_path = os.path.join(self._input_path, file)

        # Extract frames from video into temp folder
        temp_dir = self._frame_extractor.extract(video_path)
        print('Frames extracted.')
        print()

    	# Convert frames to ascii
        self._convert_frames(temp_dir)
        
        # Save output to json
        result_filename = f'{os.path.basename(video_path).split(".")[0]}'
        result_fps = self._frame_extractor.get_vidcap_fps()
        result_path = self._save_result(result_filename, result_fps)

        # Clear temp directory
        print('Cleaning up...')
        shutil.rmtree(temp_dir)
        print()

        print('CONVERSION FINISHED')

        if (play_after_finish):
            self._play(result_path)
    
    def set_output_type(self, output_type: str) -> None:
        if output_type not in OUTPUT_TYPES:
            return

        self._output_type = OUTPUT_TYPES[output_type]

    def _convert_frames(self, temp_dir: list) -> None:
        print('Preparing ascii convert...', end='\r')
        # Create threads for max each 1/100 of the frames
        frames = os.listdir(temp_dir)
        chunk_size = ceil(len(frames)/100)
        split_frames = self._split_frames(frames, chunk_size)
        threads = []

        for frame_chunk in split_frames:
            thread = threading.Thread(target=self._convert_frame_chunk, args=(frame_chunk,temp_dir,))
            threads.append(thread)
            thread.start()
        
        # Add a print progress thread
        pp_thread = threading.Thread(target=self._print_convert_progress, args=(len(frames),))
        threads.append(pp_thread)
        pp_thread.start()

        for thread in threads:
            thread.join()

    def _convert_frame_chunk(self, frame_chunk: list, temp_dir: str) -> None:
        for frame in frame_chunk:
            frame_number = frame.split('.')[0].split('_')[-1]
            self._output_frames[frame_number] = self._image_convertor.convert(os.path.join(temp_dir, frame))

    def _split_frames(self, frames: list, chunk_size: int = 100):
        for i in range(0, len(frames), chunk_size):  
            yield frames[i:i + chunk_size] 

    def _save_result(self, file_name: str, fps: float) -> None:
        print('Saving the result...')
        output = {
            'fps':      fps,
            'frames':   self._output_frames
        }

        if self._output_type == OUTPUT_JSON:
            result_path = os.path.join(self._output_path, f'{file_name}.json')
            with open(result_path, 'w') as json_file:
                json.dump(output, json_file)
        
        if self._output_type == OUTPUT_PICKLE:
            result_path = os.path.join(self._output_path, f'{file_name}.pkl')
            with open(result_path, 'wb') as pkl_file:
                pickle.dump(output, pkl_file)
        
        print()

        return result_path

    def _print_convert_progress(self, frame_count: int) -> None:
        print('Preparing ascii convert...', end='\r')
        while len(self._output_frames.keys()) < frame_count:
            print(f'Converting frames to ascii [{len(self._output_frames.keys())}/{frame_count}]', end='\r')
        print('                                                                                    ')

    def _play(self, path: str) -> None:
        print()
        input('Press enter to play the ascii video!')
        self._video_player.play(path, True)

if __name__ == '__main__':
    convertor = VideoAsciiConvertor((150, 150))
    
    input_path = input('Input path (Leave blank for the first video in the input/video_ascii dir): ')
    output_type = input('Input type [j for JSON, p for PICKLE]: ')
    play_after = input('Play after conversion finished [y/n]: ')

    convertor.set_output_type(output_type)
    convertor.convert(input_path, play_after == 'y')
