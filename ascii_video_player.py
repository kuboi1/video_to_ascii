import json
import pickle
import os
import time

class AsciiVideoPlayer:
    def __init__(self, default_frame_rate: int = 24) -> None:
        self._default_frame_rate = default_frame_rate

        self._frames = {}
        self._frame_rows = 0

    def play(self, path: str, clear_before: bool = False) -> None:
        print('Loading video...')

        input_data = self._get_input_data(path)

        input_frames = input_data['frames']
        frame_rate = input_data['fps']
        frame_rate += 0.1 # Needs a bit of adjusting to be perfect
        
        # Sort frames
        frame_keys = list(input_frames.keys())
        frame_keys.sort(key=int)
        self._frames = {i: input_frames[i] for i in frame_keys}
        self._frame_rows = len(list(self._frames.values())[0])

        if clear_before:
            self._prep_next_frame()
        
        passed_frames = 0

        for frame_key in self._frames:
            frame_start = time.perf_counter()

            self._display_frame(self._frames[frame_key])

            # Prepare next frame by moving the cursor to the start
            self._prep_next_frame()

            passed_frames += 1

            # Clear console every 5 seconds
            if (passed_frames % (frame_rate * 5)) == 0:
                self._clear_console()

            # Limit frames per second
            time.sleep(max(0, (1.0 / frame_rate) - (time.perf_counter() - frame_start)))
        
        # Clear the last frame
        self._clear_console()

        print('Video finished!')

    def _is_pickle(self, file: str) -> bool:
        return file.endswith('.pkl')

    def _is_json(self, file: str) -> bool:
        return file.endswith('.json')

    def _get_input_data(self, file_path: str) -> dict:
        file_name = os.path.basename(file_path)

        if self._is_json(file_name):
            with open(file_path, 'r') as json_file:
                return json.load(json_file)
        
        if self._is_pickle(file_name):
            with open(file_path, 'rb') as pkl_file:
                return pickle.load(pkl_file)

        return {}

    def _display_frame(self, frame_data: list) -> None:
        print('\n'.join(frame_data))

    def _prep_next_frame(self) -> None:
        # Move cursor up by the number of rows in one frame
        print(f'\033[{self._frame_rows}A\033[2K', end='')
    
    def _clear_console(self) -> None:
        os.system('cls')


if __name__ == '__main__':
    try:
        player = AsciiVideoPlayer()

        input_path = input('Path to input file (.json and .pkl supported): ')

        player.play(input_path, True)
    except KeyboardInterrupt:
        # Turn off on keyboard interrupt
        os.system('cls')

        print('Turned off by Keyboard Interrupt')