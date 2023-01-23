from argparse import ArgumentParser, RawTextHelpFormatter
import shutil
import os
import subprocess


def has_error(result) -> bool:
    return len(result.stderr.decode('utf-8')) > 0


def create_xcframework(simulator_framework_path: str, device_framework_path: str, output_path: str):
    result = subprocess.run(['xcodebuild',
                             '-create-xcframework',
                             "-framework", simulator_framework_path,
                             "-framework", device_framework_path,
                             "-output", output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(output_path)
    print(result)
    if has_error(result):
        raise ValueError("Unknown error")


class BinaryLibrary:
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path
        result = subprocess.run(['lipo', '-i', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if has_error(result):
            raise ValueError("This is not a fat file")
        self._result = result.stdout.decode('utf-8')
        self.simulator_x86 = True if "x86_64" in self._result else False
        self.simulator_i386 = True if "i386" in self._result else False
        self.device_arm64 = True if "arm64" in self._result else False
        self.device_armv7 = True if "armv7" in self._result else False

    def remove_arch(self, simulator_x86=False, simulator_i386=False, device_arm64=False, device_armv7=False):

        if True not in [simulator_x86 is False and self.simulator_x86,
                        simulator_i386 is False and self.simulator_i386,
                        device_arm64 is False and self.device_arm64,
                        device_armv7 is False and self.device_armv7]:
            raise ValueError("Remove's specified would result in an empty fat file")
        cmd = ['lipo']
        cmd += ['-remove', 'i386'] if simulator_i386 and self.simulator_i386 else []
        cmd += ['-remove', 'x86_64'] if simulator_x86 and self.simulator_x86 else []
        cmd += ['-remove', 'arm64'] if device_arm64 and self.device_arm64 else []
        cmd += ['-remove', 'armv7'] if device_armv7 and self.device_armv7 else []
        cmd += [self.path, '-o', self.path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if has_error(result):
            raise Exception("Unknown reason")
        self.simulator_i386 = simulator_i386
        self.simulator_x86 = simulator_x86
        self.device_arm64 = device_arm64
        self.device_armv7 = device_armv7


def spm_from_framework(path):
    # 1. duplicate framework for device and one for simulator
    parent_dir = os.path.dirname(path)
    framework_name = os.path.basename(path)
    # 1.1 find binary from framework
    binary: BinaryLibrary
    for file in os.listdir(path):
        try:
            binary = BinaryLibrary(os.path.join(path, file))
        except ValueError:
            continue
    # 1.2 duplicate device framework
    device_framework_path = os.path.join(parent_dir, "output", "Device", framework_name)
    shutil.copytree(path, device_framework_path)
    # 1.3 duplicate simulator framework
    simulator_framework_path = os.path.join(parent_dir, "output", "Simulator", framework_name)
    shutil.copytree(path, simulator_framework_path)
    # 2. Remove unnecessary architectures. For device keep only armv7 & arm64 and for simulator keep only x86_64 & i386
    device_binary_path = os.path.join(device_framework_path, binary.name)
    device_binary = BinaryLibrary(device_binary_path)
    try:
        device_binary.remove_arch(simulator_x86=True, simulator_i386=True)
        print("Removed simulator architectures from", device_binary_path)
    except ValueError:
        print("Remove simulator architectures not executed")

    simulator_binary_path = os.path.join(simulator_framework_path, binary.name)
    simulator_binary = BinaryLibrary(simulator_binary_path)
    try:
        simulator_binary.remove_arch(device_arm64=True, device_armv7=True)
        print("Removed device architectures from", simulator_binary_path)
    except ValueError:
        print("Remove device architectures not executed")
    # 3. combine the two frameworks together into one xcframework
    create_xcframework(simulator_framework_path,
                       device_framework_path,
                       os.path.join(parent_dir, "output", os.path.splitext(framework_name)[0] + ".xcframework"))


def spm_from_framework_main():
    parser: ArgumentParser = ArgumentParser(prog='python migrate.py',
                                            formatter_class=RawTextHelpFormatter,
                                            description="example:\n"
                                                        "   # python spm_from_framework -p 'path to a framework'")
    parser.add_argument('-p',
                        '--path',
                        required=True,
                        help='path to a framework')
    parser.set_defaults(func=spm_from_framework)
    args = parser.parse_args()
    args.func(args.path)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    spm_from_framework_main()
