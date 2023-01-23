from typing import List

from spm_models.spm_target import Target


class Product:
    def __init__(self, pod_dict: dict, targets: List[Target]):
        if 'vendored_frameworks' in pod_dict:
            self.type = '.library'
            self.name = pod_dict['vendored_frameworks'].split('.')[0]
            self.targets: List[Target] = targets
        else:
            self.type = '.library'
            self.name = pod_dict['name']
            self.targets = targets

    def to_swift_package_manifest(self):
        # ignore resources
        targets_str = ', '.join(['"{}"'.format(target.name) for target in self.targets])
        return '{}(name: "{}", targets: [{}])'.format(self.type, self.name, targets_str)
