import os
from container_security import *
from jira import *


def load_config():
    config = configurations.variables.copy()

    # override config with environment variables if provided through cli or while running container
    overrides = {
        "jira_domain": os.getenv("JIRA_DOMAIN"),
        "jira_email": os.getenv("JIRA_EMAIL"),
        "jira_api_token": os.getenv("JIRA_API_TOKEN"),
        "qualys_api_gateway_url": os.getenv("QUALYS_API_GATEWAY_URL"),
        "qualys_access_token": os.getenv("QUALYS_ACCESS_TOKEN"),
        "qualys_qql": os.getenv("QUALYS_QQL"),
        "qualys_tag": os.getenv("QUALYS_TAG"),
    }

    # only override if provided
    for key, value in overrides.items():
        if value:
            config[key] = value

    return config


if __name__ == '__main__':
    print(f"<< Script Execution Started >>")

    configurations.variables = load_config()

    # validate if JIRA credentials provided are correct
    if not check_jira_credentials():
        sys.exit()

    # validate if the tag exists - exit if not
    qualys_qql = configurations.variables["qualys_qql"]
    qualys_tag = configurations.variables["qualys_tag"]

    tag_uuid = validate_if_tag_exists(qualys_tag)

    qql = f"{qualys_qql} and not tags.name:{qualys_tag}"  # excluding the already tagged images

    # get all images with qql excluding the images already tagged
    image_dict = get_all_images(qql)
    print(image_dict)

    # get vulnerability QDS details to be populated in the JIRA issue
    for registry_repo_tag, sha_uuid in image_dict.items():
        image_sha = sha_uuid['sha']
        image_uuid = sha_uuid['uuid']
        print(f"Getting vulnerability details for registry_repo_tag: {registry_repo_tag}")

        # get image level vulnerabilities - QIDs
        jira_created = False
        image_vulnerabilities = get_vulnerability_details_of_the_image(registry_repo_tag, image_sha)
        print(f"Creating JIRA tickets for all QIDs present in registry_repo_tag: {registry_repo_tag}")

        # todo - working code - push this part once the container is up and running
        jira_qids = []
        for qid_info in image_vulnerabilities:
            # create JIRA ticket for each QID
            summary = f"QID {qid_info['qid']} | {registry_repo_tag}"
            create_jira_issue(summary, description_json=qid_info)
            jira_qids.append(True)

        #  tag the assets with qualys tag only if all QIDs are now created in Jira
        if all(jira_qids):
            assign_tag_to_assets(registry_repo_tag, qualys_tag, tag_uuid, image_uuid)

    print(f"<< Script Execution Completed >>")
