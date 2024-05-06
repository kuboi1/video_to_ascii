import os
import shutil
import json
import pickle
import multiprocessing as mp
import time
import ui
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
    def __init__(self, resolution_scale: float, num_cores: int, output_type: str) -> None:
        self._resolution_scale = resolution_scale
        self.set_num_cores(num_cores)
        self.set_output_type(output_type)

        self._input_path = os.path.abspath('./input/video_ascii')
        self._output_path = os.path.abspath('./output/video_ascii')
        self._temp_path = os.path.abspath('./temp')

        self._frame_extractor = VideoFramesExtractor(self._temp_path)
        self._image_convertor = ImgAsciiConvertor(resolution_scale, False)
        self._video_player = AsciiVideoPlayer()

        self._extract_start = None
        self._conversion_start = None

        # Create shared output dict for multiprocessing
        manager = mp.Manager()
        self._output_frames = manager.dict()

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
        self._extract_start = time.time()
        temp_dir = self._frame_extractor.extract(video_path)
        result_fps = self._frame_extractor.get_vidcap_fps() # Save fps for output before closing vidcap
        self._frame_extractor.close_vidcap()
        print(f'Frames extracted in {(time.time() - self._extract_start):.2f}s')
        print()

    	# Convert frames to ascii
        self._conversion_start = time.time()
        self._convert_frames(temp_dir)
        
        # Save output to file
        print('Saving the result...', end='\r')
        result_filename = f'{os.path.basename(video_path).split(".")[0]}'
        result_path = self._save_result(result_filename, result_fps)

        # Clear temp directory
        print('Cleaning up...      ', end='\r')
        shutil.rmtree(temp_dir)

        print(f'Ascii conversion finished in {(time.time() - self._conversion_start):.2f}s')
        print()
        print()

        ui.print_lines([
            f'VIDEO CONVERSION FINISHED - Total time {(time.time() - self._extract_start):.2f}s',
            f' -> Output file: {result_path}'
        ], seperate_chunk=True)

        if (play_after_finish):
            self._play(result_path)
    
    def set_output_type(self, output_type: str) -> None:
        if output_type not in OUTPUT_TYPES:
            return

        self._output_type = OUTPUT_TYPES[output_type]
    
    def set_resolution_scale(self, resolution_scale: float) -> None:
        self._resolution_scale = resolution_scale
        self._image_convertor.set_resolution_scale(resolution_scale)
    
    def set_num_cores(self, num_cores: int) -> None:
        # Set num cores in range 1 - max cores
        self._num_cores = max(1, min(num_cores, os.cpu_count()))

    def _convert_frames(self, temp_dir: list) -> None:
        print('Preparing ascii conversion...', end='\r')
        # Create processes based on num cores attribute
        frames = os.listdir(temp_dir)
        chunk_size = ceil(len(frames)/self._num_cores)
        split_frames = self._split_frames(frames, chunk_size)
        processes = []

        for frame_chunk in split_frames:
            process = mp.Process(target=self._convert_frame_chunk, args=(frame_chunk,temp_dir,len(frames),))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()
        
        # Clear the progress line
        print('                                                                                    ')

    def _convert_frame_chunk(self, frame_chunk: list, temp_dir: str, frame_count: int) -> None:
        for frame in frame_chunk:
            frame_number = frame.split('.')[0].split('_')[-1]
            self._output_frames[frame_number] = self._image_convertor.convert(os.path.join(temp_dir, frame))

            # Print progress
            self._print_convert_progress(frame_count)

    def _split_frames(self, frames: list, chunk_size: int = 100):
        for i in range(0, len(frames), chunk_size):  
            yield frames[i:i + chunk_size] 

    def _save_result(self, file_name: str, fps: float) -> None:
        output = {
            'fps':          fps,
            'resolution':   self._resolution_scale,
            'frames':       dict(self._output_frames)
        }

        # Add resolution to file name
        file_name += f'_0{int(self._resolution_scale * 100)}'

        if self._output_type == OUTPUT_JSON:
            result_path = os.path.join(self._output_path, f'{file_name}.json')
            with open(result_path, 'w') as json_file:
                json.dump(output, json_file)
        
        if self._output_type == OUTPUT_PICKLE:
            result_path = os.path.join(self._output_path, f'{file_name}.pkl')
            with open(result_path, 'wb') as pkl_file:
                pickle.dump(output, pkl_file)

        return result_path

    def _print_convert_progress(self, frame_count: int) -> None:
        time_passed = time.time() - self._conversion_start
        converted_frames = len(self._output_frames.keys())
        fps = converted_frames / time_passed
        estimate = int((frame_count - converted_frames) / fps)

        print(f'Converting frames to ascii [{converted_frames}/{frame_count}] | est. time left: {estimate}s            ', end='\r')

    def _play(self, path: str) -> None:
        print()
        input('Press enter to play the ascii video!')
        self._video_player.play(path, True)
