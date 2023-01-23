from typing import List, Dict, Any, Optional
from cocoapods.search import get_pod_details


class Dependency:

    def __init__(self, dependency: List[str], is_target: bool = False):
        self.is_target = is_target
        self.version = None
        self.min_version = None
        self.max_version = None
        self.pod_details = None

        if len(dependency) > 0:
            if self.is_target:
                self.name = dependency[0].replace("/", "_")
            else:
                self.name = dependency[0]
                self.pod_details = get_pod_details(self.name)

        if len(dependency) > 1:
            if ">" in dependency[1]:
                self.min_version = self.version_from_str(dependency[1])
            elif "<" in dependency[1]:
                self.max_version = self.version_from_str(dependency[1])
            else:
                self.version = f'"{self.version_from_str(dependency[1])}"'
        if len(dependency) > 2:
            if ">" in dependency[2]:
                self.min_version = self.version_from_str(dependency[2])
            elif "<" in dependency[2]:
                self.max_version = self.version_from_str(dependency[2])

        if self.version is not None:
            self.version_parameter = "exact: "
        elif self.min_version is not None and self.max_version is not None:
            self.version = f'"{self.min_version}"..<"{self.max_version}"'
            self.version_parameter = ""
        elif self.min_version is not None and self.max_version is None:
            self.version = f'"{self.min_version}"'
            self.version_parameter = "from: "
        else:
            self.version_parameter = "branch: "
            if self.pod_details and self.pod_details.branch:
                self.version = self.pod_details.branch
            else:
                self.version = '"main"'

    @staticmethod
    def is_target(pod_dict: dict, dependency: List[str]) -> bool:
        if len(dependency) == 0:
            return False

        dependency_name_split = dependency[0].split("/")
        if pod_dict.get("name") not in dependency_name_split:
            return False

        for subspec in pod_dict.get("subspecs", []):
            subspec_name = subspec.get('name')
            if subspec_name in dependency_name_split:
                return True
        return False

    @staticmethod
    def version_from_str(value):
        value = value.replace("<", "").replace("=", "").replace(" ", "").replace(">", "").split(".")
        if len(value) == 1:
            return f'{value[0]}.0.0'
        elif len(value) == 2:
            return f'{value[0]}.{value[1]}.0'
        elif len(value) == 3:
            return f'{value[0]}.{value[1]}.{value[2]}'

    def to_swift_package_manifest(self):
        if self.pod_details and self.pod_details.github_url:
            if self.pod_details.has_spm:
                return f'.package(url:"{self.pod_details.github_url}", {self.version_parameter}{self.version})'
            else:
                return f'// .package(url:"{self.pod_details.github_url}", {self.version_parameter}{self.version}) /* This is missing SPM support. TODO: manually create SPM support and retry generation.*/'
        elif self.is_target:
            return ''
        else:
            print("private pod detected please manually handle this for now")
            return f'// .package(name:"{self.name}", url:"paste here the url of your git repo", from:"select a correct verion")  TODO: private pod detected please manually create SPM support and add description in the pods_private_index.json file'

    def target_dependency(self):
        if self.pod_details and self.pod_details.github_url:
            return f'.product(name:"{self.pod_details.module_name}", package:"{self.pod_details.github_url.split("/")[-1]}")'
        elif self.is_target:
            return f'.target(name:"{self.name}")'
        else:
            return f'.product(name:"{self.name}") /* This is missing SPM support*/'


dependency_cache: Dict[str, Any] = {}


def get_cached_dependency(dependency_list: List[str]) -> Optional[Dependency]:
    return dependency_cache.get("".join(dependency_list))


def cache_dependency(dependency_list: List[str], dependency: Dependency):
    dependency_cache["".join(dependency_list)] = dependency


def get_dependencies(pod_dict: dict, sub_spec_name: str = None) -> List[Dependency]:
    dependencies_json = pod_dict.get('dependencies', [])
    subspecs = pod_dict.get('subspecs', [])
    dependencies = []
    for sub_spec in subspecs:
        if sub_spec_name is not None:
            if sub_spec.get('name') == sub_spec_name:
                dependencies_json = dependencies_json + sub_spec.get('dependencies', [])
        else:
            dependencies_json = dependencies_json + sub_spec.get('dependencies', [])

    for dependency_json in dependencies_json:
        dependency = get_cached_dependency(dependency_json)
        if dependency is None:
            is_target = Dependency.is_target(pod_dict, dependency_json)
            dependency = Dependency(dependency_json, is_target)
            print("Dependency cache miss", dependency.name)
            cache_dependency(dependency_json, dependency)
        else:
            print("Dependency cache hit", dependency.name)
        dependencies.append(dependency)

    return list(dependencies)