import json
import pickle
import os
import time
import keyboard

class AsciiVideoPlayer:
    def __init__(self, default_frame_rate: int = 24) -> None:
        self._default_frame_rate = default_frame_rate

        self._frames = {}
        self._frame_rows = 0
        self._frame_cols = 0
        self._first_frame = 0
        self._current_frame = 0

        self._paused = False

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

        # Set frame dimensions
        self._frame_rows = len(list(self._frames.values())[0])
        self._frame_cols = len(list(self._frames.values())[0][0])

        # Set first frame key
        self._first_frame = self._current_frame = int(list(self._frames.keys())[0])

        if clear_before:
            self._clear_console()
        
        while self._has_next_frame():
            frame_start = time.perf_counter()

            # Display the ascii frame
            self._display_frame(self._frames[str(self._current_frame)])

            # Print a seperator
            self._print_seperator()

            # Print player controls
            self._print_controls()

            # Check for input and handle it
            self._handle_user_input()

            # Prepare next frame by moving the cursor to the start
            self._prep_next_frame()

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

    def _handle_user_input(self) -> None:
        if self._paused:
            # UNPAUSE
            if keyboard.is_pressed('w'):
                if self._paused:
                    self._paused = False
        else:
            # PAUSE
            if keyboard.is_pressed('q'):
                self._paused = True
                # Clear the controls line
                print(f'\033[1A\033[2K', end='')
                print(''.join([' ' for _ in range(self._frame_cols)]))
                print(f'\033[1A\033[2K', end='')
                print('| PAUSED: Press f3 to unpause |')
            
            # REWIND
            if keyboard.is_pressed('e'):
                if self._current_frame - 5 >= self._first_frame:
                    self._current_frame -= 5
            
            # FAST FORWARD
            if keyboard.is_pressed('r'):
                self._current_frame += 4

        # CLEAR ARTIFACTS
        if keyboard.is_pressed('t'):
            self._clear_console()
        
        # STOP AND TURN OFF
        if keyboard.is_pressed('z') or keyboard.is_pressed('y'):
            self._clear_console()
            self._playing = False
            print('Video stopped by controls')
            exit(0)
    
    def _print_seperator(self) -> None:
        if self._paused:
            return
        
        print(''.join(['-' for _ in range(self._frame_cols)]))

    def _print_controls(self) -> None:
        if self._paused:
            return
        
        print('CONTROLS: | q - Pause | e - Rewind | r - Fast forward | t - Clear artifacts | y - Stop |')

    def _display_frame(self, frame_data: list) -> None:
        if self._paused:
            return
        
        print('\n'.join(frame_data))

    def _prep_next_frame(self) -> None:
        if self._paused:
            return
        
        self._current_frame += 1
        
        # Move cursor up by the number of rows in one frame + 2 rows for controls
        move_lines = self._frame_rows + 2
        print(f'\033[{move_lines}A\033[2K', end='')
    
    def _has_next_frame(self) -> bool:
        return str(self._current_frame + 1) in self._frames
    
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