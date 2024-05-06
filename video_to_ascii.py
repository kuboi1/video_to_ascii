import scripts.ui as ui
import os
from scripts.video_ascii_convertor import VideoAsciiConvertor

# Define input options
class InputOptions:
    resolution_scale: float
    num_cores: int
    output_type: str
    input_path: str
    play_after: bool


def main() -> None:
    # Print intro
    print_intro()

    # Get input options
    input_options = get_input_options()

    ui.print_separator()

    # Setup convertor
    convertor = VideoAsciiConvertor(
        input_options.resolution_scale,
        input_options.num_cores,
        input_options.output_type
    )

    # Convert
    convertor.convert(input_options.input_path, input_options.play_after)


def print_intro() -> None:
    ui.print_lines([
        'VIDEO TO ASCII CONVERTOR',
        ' - Input options below to convert video to ascii art',
        ' - You can play the output in the custom video player included in this project'
    ], seperate_chunk=True)


def get_input_options() -> InputOptions:
    input_options = InputOptions()

    input_options.input_path = ui.get_input(
        prompt='Video input path',
        custom_validator=ui.file_type_validator,
        custom_validator_args=['mp4'],
        custom_validator_error='The path specified is not a video'
    )

    print()

    input_options.resolution_scale = ui.get_range_input(
        prompt='Resolution scale',
        min_val=0.1,
        max_val=1.0
    )

    print()

    input_options.num_cores = ui.get_range_input(
        prompt=f'Number of cores to use for conversion',
        min_val=1,
        max_val=os.cpu_count()
    )

    print()

    input_options.output_type = ui.get_input(
        prompt='Output type',
        options=['j', 'p'],
        options_prompt='j for JSON, p for PICKLE'
    )

    print()

    input_options.play_after = ui.get_bool_input(prompt='Play after conversion finished')

    return input_options


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Turn off on keyboard interrupt
        print('Turned off by Keyboard Interrupt')