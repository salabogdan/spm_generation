import re
import os.path
import subprocess

from spm_models.spm_dependency import get_dependencies
from spm_models.spm_package import Package
from spm_models.spm_product import Product
from spm_models.spm_suported_platforms import get_platform
from spm_models.spm_target import Target
from xcframework_from_framework import has_error

swift_package_file_name = 'Package.swift'


def swift_package_init(output_path):
    if os.path.isfile(os.path.join(output_path, swift_package_file_name)):
        print('Has already a swift package manifest file no need to generate one')
        return
    result = subprocess.run(['swift',
                             'package',
                             'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=output_path)
    if has_error(result):
        raise ValueError("Unknown error")


def swift_package_manifest_from(podspec: dict, output_dir: str):
    output: str = os.path.join(output_dir, swift_package_file_name)
    pod_dict = podspec.get('new pod', {})
    handle_readme(pod_dict)
    if 'vendored_frameworks' in pod_dict:
        targets = [Target(pod_dict, None)]
        product = Product(pod_dict, targets)
    else:
        subspecs = pod_dict.get('subspecs', [])
        targets = []
        if len(subspecs) > 0:
            for subspec in subspecs:
                print('subspec -> target', subspec['name'])
                targets.append(Target(pod_dict, subspec['name']))
            targets = list(set(targets))
        else:
            targets.append(Target(pod_dict, None))
        product = Product(pod_dict, targets)

    package = Package(pod_dict.get('name'))
    package.defaultLocalization = pod_dict.get('defaultLocalization', None)
    package.platforms = get_platform(pod_dict)
    # ----
    # package.pkgConfig = pod_dict.get('', None)
    # package.providers = pod_dict.get('', None)
    package.products = [product]
    package.dependencies = get_dependencies(pod_dict)
    package.targets = targets
    # package.swiftLanguageVersions = pod_dict.get('', None)
    # package.cLanguageStandard = pod_dict.get('', None)
    # package.cxxLanguageStandard = pod_dict.get('', None)
    # ----
    package_string = package.to_swift_package_manifest()
    write_to_spm(package_string, output)
    publish_spm(pod_dict)


def publish_spm(pod_dict: dict):
    tag_version = pod_dict.get('version')
    # TODO: commit the current version to git and create a tag with the name equal to tag_version


def handle_readme(pod_dict: dict):
    # create or update the README doc with the summary at the beginning and description variable following it
    # print('Generating README.md file')
    summary = pod_dict.get('summary')
    description = pod_dict.get('description')
    homepage = pod_dict.get('homepage')
    author = pod_dict.get('author')
    readme = summary + \
             "\n\n Description: {}".format(description) + \
             '\n\n Homepage:{}'.format(homepage) + \
             '\n\n Contributors: {}'.format(author)
    # TODO: write the readme file to disk


def handle_license(pod_dict: dict):
    # if there is a license file then no need to do anything otherwise
    # we need to get a default licence file from github
    # based on the license[type]
    license_file = pod_dict.get('license', {}).get('file', None)
    if license_file is None:
        license_file = 'LICENSE'
        # TODO: download the file form github base on the type of license set


def write_to_spm(package_string: str, output_file):
    if not os.path.isfile(output_file):
        raise ValueError('missing spm file')

    # read the file and replace the package string with the generated one
    with open(output_file) as reader:
        regex = r"([\s\w\W]*import PackageDescription)"
        match = re.compile(regex).match(reader.read())
        swift_header = match.group()

    output_content = swift_header + '\n\n' + package_string
    print(f"Output code \n -------> \n{output_content}\n <-------")
    with open(output_file, 'w') as f:
        f.write(output_content)
