import json
import os
import sys

from container_security import *
from jira import *


def load_config():
    """
    Load configuration with priority:
    1. Environment variables
    2. Default values from configurations.variables
    """
    # Start with defaults
    config = dict(configurations.variables)

    # override config with environment variables if provided through cli or while running container
    env_overrides = {
        "jira_domain": os.getenv("JIRA_DOMAIN"),
        "jira_email": os.getenv("JIRA_EMAIL"),
        "jira_api_token": os.getenv("JIRA_API_TOKEN"),
        "qualys_api_gateway_url": os.getenv("QUALYS_API_GATEWAY_URL"),
        "qualys_access_token": os.getenv("QUALYS_ACCESS_TOKEN"),
        "qualys_qql": os.getenv("QUALYS_QQL"),
        "qualys_tag": os.getenv("QUALYS_TAG"),
    }

    # Override only if ENV var is set
    for key, value in env_overrides.items():
        if value is not None:
            config[key] = value

    return config


if __name__ == "__main__":
    print("\n================================== Script Execution Started ==================================\n")

    # Load final merged config
    configurations.variables.update(load_config())

    # Validate JIRA credentials
    if not check_jira_credentials():
        sys.exit(1)

    qualys_qql = configurations.variables["qualys_qql"]
    qualys_tag = configurations.variables["qualys_tag"]

    # Validate tag
    tag_uuid = validate_if_tag_exists(qualys_tag)

    # Exclude already tagged images
    qql = f"{qualys_qql} and not tags.name:{qualys_tag}"
    print(f"Fetching results for QQL {qql}")

    # Get images
    image_dict = get_all_images(qql)

    for registry_repo_tag, sha_uuid in image_dict.items():
        image_sha = sha_uuid["sha"]
        image_uuid = sha_uuid["uuid"]

        print(f"\nGetting vulnerability details for registry_repo_tag: {registry_repo_tag}")

        image_vulnerabilities = get_vulnerability_details_of_the_image(registry_repo_tag, image_sha)

        print(f"Creating JIRA tickets for all QIDs present in registry_repo_tag: {registry_repo_tag}")

        jira_qids = []

        for qid_info in image_vulnerabilities:
            summary = f"QID {qid_info['qid']} | {registry_repo_tag}"
            create_jira_issue(summary, description_json=qid_info)
            jira_qids.append(True)

        # Tag image only if all JIRA issues were created
        if all(jira_qids):
            assign_tag_to_assets(registry_repo_tag, qualys_tag, tag_uuid, image_uuid)

    print("\n================================== Script Execution Ended ==================================\n")
