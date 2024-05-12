import os
import json
import scripts.ui as ui
import numpy as np
from PIL import Image, ImageOps


BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class ImgAsciiConvertor:
    def __init__(self, resolution_scale: float, output_to_file: bool, print_output: bool = False) -> None:
        self._resolution_scale = resolution_scale
        self._output_to_file = output_to_file
        self._print_output = print_output

        self._grayscale_chars = ' .\'`^",:;Il!i><~+_-?]}[{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'

        self._input_path = os.path.join(BASE_PATH, 'input\\img_ascii')
        self._output_path = os.path.join(BASE_PATH, 'output\\img_ascii')

    def convert_input_files(self) -> None:
        for file in os.listdir(self._input_path):
            self.convert(file)

    def convert(self, image_path: str, print_message: bool = False) -> list:
        if not os.path.isfile(image_path):
            raise FileNotFoundError

        if print_message:
            print(f'Converting {os.path.basename(image_path)} to ascii...')

        with Image.open(image_path) as base_image:
            image = ImageOps.grayscale(base_image)
            image_array = np.array(image)

        image_size = image_array.shape
        x_step = int(image_size[0] / (image_size[0] * np.clip(self._resolution_scale, 0.0, 1.0)))
        y_step = int(image_size[1] / (image_size[1] * np.clip(self._resolution_scale, 0.0, 1.0)))

        # Lower sampling in the vertical direction to avoid stretching
        y_step = int(y_step * (1.5 + self._resolution_scale))

        output_ascii = []

        for y in range(0, image_size[0] - y_step, y_step):
            # Build row string
            output_row = ''
            for x in range(0, image_size[1] - x_step, x_step):
                pixel_chunk = image_array[y:(y + y_step), x:(x + x_step)]
                average_color_value = np.mean(pixel_chunk)
                ascii_char = self._convert_gray_to_ascii(average_color_value)
                output_row += ascii_char
            
            # Add the row string to output
            output_ascii.append(output_row)
        
        if self._output_to_file:
            result_filename = f'{os.path.basename(image_path).split(".")[0]}'
            result_path = self._save_result(output_ascii, result_filename)

        if print_message:
            outro_lines = ['CONVERSION FINISHED']
            if self._output_to_file:
                outro_lines.append(f' -> Output file: {result_path}')

            ui.print_lines(outro_lines, seperate_chunk=True)

        if self._print_output:
            self.print_result(output_ascii)

        return output_ascii
    
    def set_resolution_scale(self, resolution_scale: float) -> None:
        self._resolution_scale = resolution_scale

    def _convert_gray_to_ascii(self, gray_value: float) -> str:
        index_value = round(((gray_value / 256) * (len(self._grayscale_chars) - 1)))
        return self._grayscale_chars[index_value]

    def _save_result(self, output: list, file_name: str) -> str:
        # Add resolution to file name
        file_name += f'_0{int(self._resolution_scale * 100)}'

        result_path = os.path.join(self._output_path, f'{file_name}.json')
        with open(result_path, 'w') as json_file:
            json.dump(output, json_file)
        
        return result_path

    def print_result(self, result: list) -> None:
        ui.print_lines([
            'RESULT:',
            '',
            *[''.join(row) for row in result]
        ], max_separator_length=100)
        ui.print_separator(length=100)
