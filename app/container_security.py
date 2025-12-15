import sys
import configurations
import requests


def get_headers():
    return {
        "Authorization": f"Bearer {configurations.get('qualys_access_token')}"
    }


def get_qualys_api_gateway_url() -> str:
    return configurations.get("qualys_api_gateway_url")


def get_qualys_access_token() -> str:
    return configurations.get("qualys_access_token")


def validate_if_tag_exists(qualys_tag):
    print(f"Checking if qualys_tag [{qualys_tag}] exists")
    payload = {
        "tagsToValidate": [
            qualys_tag
        ]
    }
    url = f"{get_qualys_api_gateway_url()}/csapi/v1.3/tag/exist"
    response = requests.post(url, json=payload, headers=get_headers())

    if response.status_code == 200:
        if qualys_tag in response.json()["tagDetails"]['existingTags'].keys():
            print(f"qualys_tag [{qualys_tag}] exists")
            return response.json()["tagDetails"]['existingTags'][qualys_tag]
        else:
            print(f"Tag [{qualys_tag}] does not exist. Please provide valid qualys_tag.")
            print(f"<< Script Execution Completed >>")
            sys.exit(0)

    else:
        sys.exit(f"Provided tag {[qualys_tag]} does not exist."
                 f" Status {response.status_code}, Response: {response.text}")


def get_all_images(qql: str) -> dict:
    url = f"{get_qualys_api_gateway_url()}/csapi/v1.3/images?filter={qql}"
    print(url)
    response = requests.get(url, headers=get_headers())

    image_dict = {}
    if response.status_code == 200:
        images = response.json().get("data", [])
        if images:
            for image in images:
                repo = image['repo'][0]
                registry_repo_tag: str = f"{repo['registry']}/{repo['repository']}:{repo['tag']}"
                image_dict = {
                    registry_repo_tag: {
                        'sha': image.get("sha"),
                        'uuid': image.get("uuid")
                    }
                }


    elif response.status_code == 400:
        print(f"Please check if the syntax of qql >> {qql}")
        print(f"<< Script Execution Terminated >>")
        sys.exit(0)

    elif response.status_code == 204:
        print(f"No images found with the provided qql >> {qql}")
        print(f"<< Script Execution Completed >>")
        sys.exit(0)
    else:
        sys.exit(f"Failed to fetch images. Status {response.status_code}, Response: {response.text}")

    return image_dict


def get_vulnerability_details_of_the_image(registry_repo_tag, image_sha: str):
    url = f"{get_qualys_api_gateway_url}/csapi/v1.3/images/{image_sha}"
    response = requests.get(url, headers=get_headers())

    image_vulnerabilities = []

    if response.status_code == 200:
        vulnerabilities = response.json()['vulnerabilities']

        for vulnerability in vulnerabilities:
            try:
                qid_info = {}
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


def assign_tag_to_assets(registry_repo_tag, qualys_tag, tag_uuid, entity_uuid):
    # https://docs.qualys.com/en/cs/api/asset_tagging/assign_tags_to_an_asset.htm
    payload = {"entityType": "IMAGE",
               "tagsToAdd": [{
                   "tagUuid": tag_uuid,
                   "isCascadeToContainer": False}],
               "entityUUID": entity_uuid}

    url = f"{get_qualys_api_gateway_url}/csapi/v1.3/tag/assign"
    response = requests.post(url, json=payload, headers=get_headers())

    if response.status_code == 200:
        print(f"Assigned tag [{qualys_tag}] to asset [{registry_repo_tag}]")
        return True
    else:
        sys.exit(f"Provided tag {[qualys_tag]} does not exist."
                 f" Status {response.status_code}, Response: {response.text}")
