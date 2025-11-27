import sys
from logging import raiseExceptions

from config_loader import config

# config.json >> config loader
qualys_api_gateway_url = config["qualys_api_gateway_url"]
qualys_access_token = config["qualys_access_token"]
headers = {"Authorization": f"Bearer {config['qualys_access_token']}"}

import requests
import json


def get_all_images(qql: str) -> dict:
    url = f"{qualys_api_gateway_url}/csapi/v1.3/images?filter={qql}"
    print(f"GET {url}")
    response = requests.get(url, headers=headers)

    registry_repo_tag_sha = {}
    if response.status_code == 200:
        images = response.json().get("data", [])
        if images:
            for image in images:
                repo = image['repo'][0]
                registry_repo_tag: str = f"{repo['registry']}/{repo['repository']}:{repo['tag']}"
                registry_repo_tag_sha = {registry_repo_tag: image.get("sha")}

    elif response.status_code == 204:
        print(f"No images found with the provided qql >> {qql}")
    else:
        sys.exit(f"Failed to fetch images. Status {response.status_code}, Response: {response.text}")

    return registry_repo_tag_sha


def get_vulnerability_details_of_the_image(registry_repo_tag, image_sha: str):
    url = f"{qualys_api_gateway_url}/csapi/v1.3/images/{image_sha}"
    response = requests.get(url, headers=headers)

    image_vulnerabilities = []
    qid_info = {}
    if response.status_code == 200:
        vulnerabilities = response.json()['vulnerabilities']

        for vulnerability in vulnerabilities:

            try:
                qid_info.update({
                    'sha': image_sha,
                    'registry_repo_tag': registry_repo_tag,
                    'qid': vulnerability.get('qid'),
                    'title': vulnerability.get('title'),
                    'qdsScore': vulnerability.get('qdsScore'),
                    'cveids': vulnerability.get('cveids'),
                    'cvssInfo': vulnerability.get('cvssInfo'),
                })

                if vulnerability.get('software'):
                    softwares = []
                    for software in vulnerability.get('software'):
                        sw = {
                            'name': software.get('name'),
                            'version': software.get('version'),
                            'fixVersion': software.get('fixVersion'),
                            'packagePath': software.get('packagePath'),
                            'scanType': software.get('scanType')
                        }
                        softwares.append(sw)
                    qid_info['software'] = softwares

                # print(json.dumps(qid_info, indent=4))
            except Exception as e:
                print(f"Exception occurred: {type(e).__name__} for registry_repo_tag >> {registry_repo_tag}")
                print(f"QID: {vulnerability.get('qid')} for registry_repo_tag >> {registry_repo_tag}")
                raise
            image_vulnerabilities.append(qid_info)
    elif response.status_code == 204:
        print(f"No image found with sha >> {image_sha}")
    else:
        raise RuntimeError(f"Failed to fetch image details. Status {response.status_code}, Response: {response.text}")

    return image_vulnerabilities
