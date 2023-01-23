from typing import Optional, List

from spm_models.spm_dependency import Dependency
from spm_models.spm_product import Product
from spm_models.spm_suported_platforms import SupportedPlatforms
from spm_models.spm_target import Target


class Package:
    def __init__(self, name: str):
        self.name: str = name
        self.defaultLocalization: Optional[str] = None
        self.platforms: Optional[List[SupportedPlatforms]] = None
        self.pkgConfig: Optional[str] = None
        self.providers: Optional[List[str]] = None
        self.products: List[Product] = []
        self.dependencies: List[Dependency] = []
        self.targets: List[Target] = []
        self.swift_language_versions: Optional[List[str]] = None
        self.cLanguageStandard: Optional[str] = None
        self.cxxLanguageStandard: Optional[str] = None

    def to_swift_package_manifest(self):
        alist = filter(None, ['name: "{}"'.format(self.name),
                              '' if self.defaultLocalization is None else 'defaultLocalization: {},'.format(
                                  self.defaultLocalization),
                              self.platforms_list(),
                              '' if self.pkgConfig is None else 'pkgConfig: {},'.format(self.pkgConfig),
                              self.providers_list(),
                              self.products_list(),
                              self.dependencies_list(),
                              self.targets_list(),
                              self.swift_language_versions_list(),
                              '' if self.cLanguageStandard is None else 'cLanguageStandard: {},'.format(
                                  self.cLanguageStandard),
                              '' if self.cxxLanguageStandard is None else 'cxxLanguageStandard: {}'.format(
                                  self.cxxLanguageStandard)
                              ])
        output = '''let package = Package({})
        '''.format(", \n".join(list(alist))
                   )
        return output

    def platforms_list(self) -> str:
        if self.platforms is None:
            return ''
        else:
            return 'platforms: [{}]'.format(
                ", \n".join([platform.to_swift_package_manifest() for platform in self.platforms]))

    def providers_list(self) -> str:
        if self.providers is None:
            return ''
        else:
            return 'providers: [{}]'.format(", \n".join(self.providers))

    def products_list(self) -> str:
        if len(self.products) == 0:
            return ''
        else:
            return 'products: [{}]'.format(
                ", \n".join([product.to_swift_package_manifest() for product in self.products]))

    def dependencies_list(self) -> str:
        if len(self.dependencies) == 0:
            return ''
        else:
            unique_git_url = {}
            for dep in self.dependencies:
                cached_dep = unique_git_url.get(dep.pod_details.github_url)
                if cached_dep is None or cached_dep.version_parameter == "exact":
                    unique_git_url[dep.pod_details.github_url] = dep
            unique_str_dendepencies = [dep.to_swift_package_manifest() for dep in list(unique_git_url.values())]
            return 'dependencies: [{}\n]'.format(
                ", \n".join(list(set(filter(None, unique_str_dendepencies)))))

    def targets_list(self) -> str:
        if len(self.targets) == 0:
            return ''
        else:
            return 'targets: [{}\n]'.format(
                ", \n".join([target.to_swift_package_manifest() for target in self.targets]))

    def swift_language_versions_list(self) -> str:
        if self.swift_language_versions is None:
            return ''
        else:
            return 'swiftLanguageVersions: [{}]'.format(", \n".join(self.swift_language_versions))
