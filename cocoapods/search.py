import json
import os
import subprocess
from typing import Optional
import requests


class PodDetails:
    def __init__(self):
        self.has_spm = False
        self.github_url = None
        self.name = None
        self.branch = None
        self.module_name = None

    def __str__(self):
        return '{' + f'has_spm:{self.has_spm},' \
                     f' github:{self.github_url},' \
                     f' name:{self.name},' \
                     f' branch:{self.branch} ' \
                     f' module_name:{self.module_name}' \
                     '}'


def has_spm_support(git_repo):
    if git_repo is None:
        return False
    # Make the API call
    git_repo = git_repo + '/blob/master/Package.swift'
    response = requests.get(git_repo)
    has_spm = response.status_code == 200
    return has_spm


def generate_indexed_pods(path_to_local_git_repo):
    # in future maybe use this repository directly somehow https://github.com/CocoaPods/Specs
    with open("pods_index.json", "w") as index:
        dict_index = {}
        for subdir, dirs, files in os.walk(path_to_local_git_repo):
            for file in files:
                if "podspec" in file:
                    dict_index[file.replace(".podspec.json", "")] = os.path.join(subdir, file)
        json_string = json.dumps(dict_index)
        index.write(json_string)


def public_pod(name):
    if not os.path.exists("pods_index.json"):
        raise NotImplemented("Manually generate the pods_index.json file by following the instructions")

    # pods_index.json is the json generated from the git repo containing all the pod specs
    with open("pods_index.json") as index:
        dict_json = json.loads(index.read())
        pod_json_path = dict_json.get(name)
        if pod_json_path is None:
            return None

    print("pod json local path", pod_json_path)
    with open(pod_json_path) as pod_json_file:
        pod_json = json.loads(pod_json_file.read())
        pod_details = PodDetails()
        pod_details.name = pod_json.get('name')
        if pod_details.name is None:
            return None

        pod_details.github_url = pod_json.get('source', {}).get('git')
        if pod_details.github_url is None:
            pod_details.github_url = pod_json.get('source', {}).get('http')
            if pod_details.github_url is None:
                return None

        pod_details.module_name = pod_json.get('module_name', pod_details.name)
        pod_details.github_url = pod_details.github_url.replace(".git", "")
        pod_details.has_spm = has_spm_support(pod_details.github_url)
        pod_details.branch = get_default_git_branch(pod_details)

    return pod_details


def private_pod(name):
    # pods_index.json is the json generated from the git repo containing all the pod specs
    with open("pods_private_index.json") as pod_json_file:
        pod_json_list = json.loads(pod_json_file.read())
        for pod_json in pod_json_list:
            pod_details = PodDetails()
            pod_details.name = pod_json.get('name')
            if pod_details.name is None:
                continue
            if pod_details.name != name:
                continue

            pod_details.github_url = pod_json.get('source', {}).get('git')
            if pod_details.github_url is None:
                continue

            pod_details.github_url = pod_details.github_url.replace(".git", "")
            branch = pod_json.get('source', {}).get('branch')
            pod_details.branch = None if branch is None else f'"{branch}"'
            pod_details.has_spm = pod_json.get('has_spm')
            pod_details.module_name = pod_details.name

            return pod_details

    return None


def get_default_git_branch(pod_details: PodDetails) -> str:
    branches = subprocess.run(["git", "ls-remote", "--heads", pod_details.github_url],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    branches = branches.stdout.decode('utf-8')
    branches = "".join(branches.strip().split("\n"))
    if "master" in branches:
        return '"master"'
    if "main" in branches:
        return '"main"'


def get_pod_details(pod_name) -> Optional[PodDetails]:
    if "/" in pod_name:
        pod_name = pod_name.split("/")[0]
    pod = private_pod(pod_name)
    if pod:
        print("Private Pod \n", pod)
        return pod

    pod = public_pod(pod_name)
    if pod:
        print("Public Pod \n", pod)
        return pod

    print("Pod not found \n", pod_name)
    return pod


# Example
if __name__ == '__main__':
    pod_name_query = "AFNetworking"
    pod_out = get_pod_details(pod_name_query)
    # one needs to generate an intermediary file used for searching for public pod details
    # generate_indexed_pods(path_to_git_repo)
