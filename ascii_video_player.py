import json
import os
import time

class AsciiVideoPlayer:
    def __init__(self, frame_rate: int = 24) -> None:
        self._frame_rate = frame_rate

    def play(self, path: str, clear_before: bool = False) -> None:
        print('Loading...')
        
        with open(path, 'r') as json_file:
            input_frames: dict = json.load(json_file)
        
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
    
    def _display_frame(self, frame_data: list) -> None:
        for row in frame_data:
            print(''.join(row))

    def _clear_console(self) -> None:
        os.system('cls')


if __name__ == '__main__':
    player = AsciiVideoPlayer()

    input_path = input('Path to input json: ')

    player.play(input_path, True)