import os


def find_podspec(path_input: str) -> str:
    for file in os.listdir(path_input):
        if '.podspec' in file:
            return os.path.join(path_input, file)
    raise ValueError('Missing podspec value')