from typing import Optional, List

from spm_models.spm_dependency import get_dependencies


class Target:
    def __init__(self, pod_dict: dict, sub_spec_name: Optional[str] = None):
        self.type = None
        self.name = None
        self.path = None
        self.exclude = None
        self.plugins = None
        self.linkerSettings = None
        self.swiftSettings = None
        self.cxxSettings = None
        self.cSettings = None
        self.publicHeadersPath = None
        if 'vendored_frameworks' in pod_dict:
            self.type = '.binaryTarget'
            self.name = pod_dict['vendored_frameworks'].split('.')[0]
            self.path = pod_dict['vendored_frameworks']
        else:
            self.sources = None
            self.type = '.target'
            self.name = pod_dict['name'] + (("_" + sub_spec_name) if sub_spec_name else "")
            self.resources: Optional[List[str]] = None
            self.dependencies = None
            self.handle_path(pod_dict)
            self.handle_resource(pod_dict.get("resource"))
            self.handle_xcconfig(pod_dict)

            if sub_spec_name is not None:
                self.handle_subspec(pod_dict, sub_spec_name)

    def handle_resource(self, resource):
        # TODO: in case there are code data models, XIB, nib files skip them cause SPM handles them automatically
        if resource is None or ".xcassets" in resource or ".strings" in resource or ".lproj" in resource:
            return

        resource = resource.replace("/**", "").replace("/*", "").replace(".*", "")

        if self.resources is None:
            self.resources = []

        resource_components: List[str] = resource.split("/")
        for component in self.path.split("/"):
            if component == resource_components[0]:
                resource_components.pop(0)
            else:
                resource_components.insert(0, '..')
        self.resources.append('.copy("{}")'.format("/".join(resource_components)))

    def handle_path(self, json: dict):
        sources = json.get('source_files', None)
        if sources is not None:
            # self.sources = [f'"{sources}"']
            self.path = f'{sources.replace("/**", "").replace("/*", "")}'

    def handle_subspec(self, pod_dict: dict, sub_spec_name: str) -> dict:
        sub_specs = pod_dict['subspecs']
        sub_spec: Optional[dict] = None
        for sub_spec_dict in sub_specs:
            if sub_spec_dict['name'] == sub_spec_name:
                sub_spec = sub_spec_dict
        if sub_spec is None:
            raise ValueError("missing expected sub spec")

        self.handle_path(sub_spec)
        self.handle_xcconfig(sub_spec)

        resources_dict = sub_spec.get('resource_bundles', None)
        self.resources = []
        if resources_dict is not None:
            for key in list(resources_dict.keys()):
                resources = resources_dict[key]
                for resource in resources:
                    self.handle_resource(resource)
        if len(self.resources) == 0:
            self.resources = None

        self.dependencies = [dependency.target_dependency() for dependency in get_dependencies(pod_dict, sub_spec_name)]

        return sub_spec

    def handle_xcconfig(self, pod_dict: dict):
        defines = pod_dict.get('xcconfig', {}).get("SWIFT_ACTIVE_COMPILATION_CONDITIONS", "").split(" ")
        if "$(inherited)" in defines:
            defines.remove("$(inherited)")
        if len(list(filter(None, defines))) == 0:
            return
        if self.swiftSettings is None:
            self.swiftSettings = []
        self.swiftSettings = self.swiftSettings + [f'.define("{define}")' for define in defines]

    def to_swift_package_manifest(self):
        parameters = [f'name: "{self.name}"']
        if self.type == '.binaryTarget':
            parameters.append(f'path: "{self.path}"')
            return '{}({})'.format(self.type, ", \n".join(parameters))

        dependencies_str = ", \n".join(self.dependencies) if self.dependencies else None
        sources_str = ", \n".join(self.sources) if self.sources else None
        resources_str = ', '.join(self.resources) if self.resources else None
        swift_settins_str = ', \n'.join(self.swiftSettings) if self.resources else None
        parameters = parameters + ['' if self.dependencies is None else f'dependencies: [{dependencies_str} \n]',
                                   '' if self.path is None else f'path: "{self.path}"',
                                   '' if self.exclude is None else f'exclude: []',
                                   # TODO fix the exclude definition for a target
                                   '' if self.sources is None else f'sources: [{sources_str}]',
                                   '' if self.resources is None else f'resources: [{resources_str}]',
                                   # TODO fix the resources definition for a target
                                   '' if self.publicHeadersPath is None else f'publicHeadersPath: nil',
                                   # TODO fix the publicHeadersPath string definition
                                   '' if self.cSettings is None else f'cSettings: []',  # TODO fix
                                   '' if self.cxxSettings is None else f'cxxSettings: []',  # TODO fix
                                   '' if self.swiftSettings is None else f'swiftSettings: [{swift_settins_str}]',
                                   '' if self.linkerSettings is None else f'linkerSettings: []',  # TODO fix
                                   '' if self.plugins is None else f'plugins: []',  # TODO fix
                                   ]

        parameters = list(filter(None, parameters))
        return '{}({})'.format(self.type, ", \n".join(parameters))

    def __eq__(self, other):
        if isinstance(other, Target):
            return self.path == other.path
        return False

    def __hash__(self):
        return hash(self.path)
