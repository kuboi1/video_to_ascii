import os
import scripts.ui as ui
from scripts.img_ascii_convertor import ImgAsciiConvertor

INPUT_PATH = os.path.abspath('.\\input\\img_ascii')
OUTPUT_PATH = os.path.abspath('.\\output\\img_ascii')


# Define input options
class InputOptions:
    image_path: str
    resolution_scale: float
    print_output: bool


def main() -> None:
    # Print intro
    print_intro()

    # Get input options
    input_options = get_input_options()

    ui.print_separator()

    convertor = ImgAsciiConvertor(
        resolution_scale=input_options.resolution_scale, 
        output_to_file=True, 
        print_output=input_options.print_output
    )
    convertor.convert(image_path=input_options.image_path, print_message=True)


def print_intro() -> None:
    ui.print_lines([
        'IMAGE TO ASCII CONVERTOR',
        ' - Convert an image to ascii'
    ], seperate_chunk=True)


def get_input_options() -> InputOptions:
    input_options = InputOptions()

    input_options.image_path = ui.get_input(
        prompt='Image path',
        custom_validator=ui.file_type_validator,
        custom_validator_args=['jpg', 'jpeg', 'png'],
        custom_validator_error='Path specified is not a supported image type'
    )

    print()

    input_options.resolution_scale = ui.get_range_input(
        prompt='Resolution scale',
        min_val=0.1,
        max_val=1.0
    )

    print()

    input_options.print_output = ui.get_bool_input('Print result')

    return input_options


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Turn off on keyboard interrupt
        print('Turned off by Keyboard Interrupt')