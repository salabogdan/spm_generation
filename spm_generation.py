from argparse import Namespace, ArgumentParser, RawTextHelpFormatter

from cocoapods.search import generate_indexed_pods
from podspec_analyser.podspec_yacc import parse_podspec
from podspec_analyser.search import find_podspec
from spm_from_podspec import swift_package_manifest_from, swift_package_init


def generate_function(args):
    generate_indexed_pods(args.path_to_git_spec_repo)


def _add_generate_cocoa_index_command(subparsers):
    generate_parser = subparsers.add_parser('generate_cocoa_index', formatter_class=RawTextHelpFormatter)
    generate_parser.set_defaults(func=generate_function)
    generate_parser.add_argument('-p',
                                 '--path_to_git_spec_repo',
                                 help='Path to git spec repo. '
                                      'You should checkout this repo https://github.com/CocoaPods/Specs '
                                      'and send the local path to the repo',
                                 required=True)


def generate_spm_for_project(input_path: str):
    swift_package_init(input_path)
    podspec_file = find_podspec(input_path)
    print('Transpiling Podspec file', podspec_file)
    json_podspec = parse_podspec(podspec_file)
    print(f"\nIntermediary output\n -------->\njson_podspec = {json_podspec}\n <-------\n\n", )
    swift_package_manifest_from(json_podspec,
                                input_path)


def spm_function(args):
    generate_spm_for_project(args.for_project)


def _add_spm_command(subparsers):
    generate_parser = subparsers.add_parser('spm', formatter_class=RawTextHelpFormatter)
    generate_parser.set_defaults(func=spm_function)
    generate_parser.add_argument('-p',
                                 '--for_project',
                                 help="Path to project for which you want to generate spm support",
                                 required=True)


def _create_parsers(subparsers):
    """Add all available commands"""
    _add_spm_command(subparsers)
    _add_generate_cocoa_index_command(subparsers)


def _get_args() -> Namespace:
    """Method to create and configure a argument parser"""
    parser: ArgumentParser = ArgumentParser(prog='python spm_generation.py',
                                            formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(title='These are the available commands',
                                       description='spm                    Generates a Swift Package Manifest from a '
                                                   'podspec file \n'
                                                   'generate_cocoa_index   Generates cocoapods index files used for '
                                                   'getting podspec detials \n',
                                       dest='sub command')
    subparsers.required = True
    _create_parsers(subparsers)

    return parser.parse_args()


def main():
    args = _get_args()
    args.func(args)


if __name__ == '__main__':
    main()
    # debug
    # generate_spm_for_project("path_to_project_to_debug")

