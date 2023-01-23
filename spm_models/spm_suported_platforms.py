from typing import List


class SupportedPlatforms:
    def __init__(self, platform: str, version: str):
        platforms = {'ios': 'iOS',
                     # TODO: add the rest of the platforms here macOS, system ...
                     # check the documentation
                     # https://developer.apple.com/documentation/packagedescription/supportedplatform
                     }
        self.platform = platforms[platform]
        self.version = 'v' + version.split('.')[0]

    def to_swift_package_manifest(self):
        return '.{}(.{})'.format(self.platform, self.version)


def get_platform(pod_dict: dict) -> List[SupportedPlatforms]:
    platform: dict = pod_dict.get('platform')

    if platform is not None:
        return [SupportedPlatforms(list(platform.keys())[0], list(platform.values())[0])]
    else:
        return [SupportedPlatforms('ios', '11')]
