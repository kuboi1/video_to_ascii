import os
from typing import Any, Callable


# INPUT

def get_input(
        prompt: str, 
        options: list = [], 
        options_prompt: str = '',
        strict_type: type = None, 
        custom_validator: Callable[..., bool] = None,
        custom_validator_args: list = [],
        custom_validator_error: str = None
    ) -> Any:
    
    # Set default options prompt
    if len(options) > 0:
        options_prompt = (f' [{"/".join(options) if options_prompt == "" else options_prompt}]')

    # Get the input
    while True:
        user_input = input(f'> {prompt}{options_prompt}: ')

        # Validate type
        if strict_type is not None:
            try:
                user_input = strict_type(user_input)
            except ValueError:
                print(f'Invalid input type ({type_to_string(strict_type)} needed)')
                print()
                continue

        # Validate options
        if len(options) > 0:
            if user_input not in options:
                print(f'Invalid input -{options_prompt}')
                print()
                continue
        
        # Validate custom validator
        if custom_validator is not None:
            if not custom_validator(user_input, *custom_validator_args):
                print(custom_validator_error if custom_validator_error is not None else 'Invalid value')
                print()
                continue
        
        # Return typed validated input
        return user_input


def get_range_input(prompt: str, min_val: float, max_val: float) -> float:
    return get_input(
        prompt=f'{prompt} ({min_val} - {max_val})',
        strict_type=float,
        custom_validator=range_validator,
        custom_validator_args=[min_val, max_val],
        custom_validator_error=f'Value must be between {min_val} and {max_val}'
    )


def get_bool_input(prompt: str) -> bool:
    user_input = get_input(
        prompt=prompt,
        options=['y', 'n']
    )

    # Default enter (empty string) to y
    return user_input == 'y' or user_input == ''

# VISUAL PRINTS

def print_separator(separator: str = '-', length: int = 50) -> None:
    # Make sure lenght is not negative
    length = max(1, length)

    print()
    print(''.join([separator for _ in range(length)]))
    print()


def print_lines(
        lines: list, 
        separate_lines: bool = False, 
        seperate_chunk: bool = False, 
        separator: str = '-',
        max_separator_length: int = 200
    ) -> None:

    separator_length = min(len(max(lines, key=len)) + 2, max_separator_length)

    if seperate_chunk:
        print_separator(separator, length=separator_length)

    for line in lines:
        print(f' {line}')
        if separate_lines:
            print_separator(separator, length=separator_length)

    if seperate_chunk:
        print_separator(separator, length=separator_length)

# VALIDATORS

def path_input_validator(path_input: str) -> bool:
    return os.path.exists(path_input)


def file_type_validator(path_input: str, *file_ext: str) -> bool:
    return os.path.isfile(os.path.abspath(path_input)) and path_input.split('.')[-1] in file_ext


def range_validator(number_input: float, min_val: float, max_val: float, include_limits: bool = True) -> bool:
    if include_limits:
        return min_val <= number_input <= max_val
    
    return min_val < number_input < max_val

# CONVERTORS

def type_to_string(strict_type: type) -> str:
    if strict_type is str:
        return 'String'
    if strict_type is int or strict_type is float:
        return 'Number'
    
    return 'Any'