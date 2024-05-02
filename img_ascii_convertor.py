import os
import numpy as np
from math import floor
from PIL import Image, ImageOps

class ImgAsciiConvertor:
    def __init__(self, output_resolution: tuple, output_to_file: bool, print_output: bool = False) -> None:
        self._output_resolution = output_resolution
        self._output_to_file = output_to_file
        self._print_output = print_output

        self._grayscale_chars = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{[}]?-_+~<>i!lI;:,"^`\'. '

        self._input_path = os.path.abspath('./input/img_ascii')
        self._output_path = os.path.abspath('./output/img_ascii')

    def convert_input_files(self) -> None:
        for file in os.listdir(self._input_path):
            self.convert(file)

    def convert(self, file: str, print_message: bool = False) -> list:
        if print_message:
            print(f'Converting {os.path.basename(file)} to ascii...')

        with Image.open(os.path.join(self._input_path, file)) as base_image:
            image = ImageOps.grayscale(base_image)
            image_array = np.array(image)

        image_size = image_array.shape
        x_step = floor(image_size[0] / self._output_resolution[0]) if self._output_resolution[0] < image_size[0] else 1
        y_step = floor(image_size[1] / self._output_resolution[1]) if self._output_resolution[1] < image_size[1] else 1

        # Lower sampling in the vertical direction to avoid stretching
        # y_step = floor(y_step * 2)

        output_ascii = []

        for y in range(0, image_size[0] - y_step, y_step):
            output_row = []
            for x in range(0, image_size[1] - x_step, x_step):
                pixel_chunk = image_array[y:(y + y_step), x:(x + x_step)]
                average_color_value = np.mean(pixel_chunk)
                ascii_char = self._convert_gray_to_ascii(average_color_value)
                output_row.append(ascii_char)
            
            output_ascii.append(output_row)

        if self._print_output:
            self.print_result(output_ascii)

        return output_ascii
    
    def _convert_gray_to_ascii(self, gray_value: float) -> str:
        index_value = round(((gray_value / 256) * (len(self._grayscale_chars) - 1)))
        return self._grayscale_chars[index_value]

    def print_result(self, result: list) -> None:
        os.system('cls')
        for row in result:
            print(''.join(row))


def main() -> None:
    convertor = ImgAsciiConvertor((100, 50), True, True)
    convertor.convert_input_files()


if __name__ == '__main__':
    main()