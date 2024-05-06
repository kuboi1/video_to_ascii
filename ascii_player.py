import os
import scripts.ui as ui
from scripts.ascii_video_player import AsciiVideoPlayer


# Define input options
class InputOptions:
    input_path: str


def main() -> None:
    # Print intro
    print_intro()        

    # Get input options
    input_options = get_input_options()

    # Play ascii video
    player = AsciiVideoPlayer()
    player.play(input_options.input_path, True)


def print_intro() -> None:
    ui.print_lines([
        'ASCII VIDEO PLAYER',
        ' - Plays an ascii video in the console',
        ' - .json and .pkl files made using the Ascii Video Convertor supported'
    ], seperate_chunk=True)


def get_input_options() -> InputOptions:
    input_options = InputOptions()

    input_options.input_path = ui.get_input(
        prompt='Ascii video file path',
        custom_validator=ui.file_type_validator,
        custom_validator_args=['json', 'pkl'],
        custom_validator_error='Invalid file type - only .json and .pkl supported'
    )

    return input_options


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Turn off on keyboard interrupt
        os.system('cls')
        print('Turned off by Keyboard Interrupt')