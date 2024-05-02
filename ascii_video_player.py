import json
import pickle
import os
import time

class AsciiVideoPlayer:
    def __init__(self, frame_rate: int = 24) -> None:
        self._frame_rate = frame_rate

    def play(self, path: str, clear_before: bool = False) -> None:
        print('Loading...')

        input_frames = self._get_input_frames(path)
        
        # Sort frames
        frame_keys = list(input_frames.keys())
        frame_keys.sort(key=int)
        ascii_frames = {i: input_frames[i] for i in frame_keys}

        if clear_before:
            self._clear_console()
        
        for i, frame_key in enumerate(ascii_frames):
            frame_start = time.time()

            self._display_frame(ascii_frames[frame_key])

            frame_end = time.time()

            # Limit frames per second
            time.sleep(max(1.0/self._frame_rate - (frame_end - frame_start), 0))

            self._clear_console()
    
    def _is_pickle(self, file: str) -> bool:
        return file.endswith('.pkl')

    def _is_json(self, file: str) -> bool:
        return file.endswith('.json')

    def _get_input_frames(self, file_path: str) -> dict:
        file_name = os.path.basename(file_path)

        if self._is_json(file_name):
            with open(file_path, 'r') as json_file:
                return json.load(json_file)
        
        if self._is_pickle(file_name):
            with open(file_path, 'rb') as pkl_file:
                return pickle.load(pkl_file)

        return {}

    def _display_frame(self, frame_data: list) -> None:
        for row in frame_data:
            print(''.join(row))

    def _clear_console(self) -> None:
        os.system('cls')


if __name__ == '__main__':
    player = AsciiVideoPlayer()

    input_path = input('Path to input file (.json and .pkl supported): ')

    player.play(input_path, True)