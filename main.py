from container_security import *
from jira import *
from config_loader import config

if __name__ == '__main__':
    print(f"<< Script Execution Started >>")

    # update values from config.json
    jira_domain = config["jira_domain"]
    jira_email = config["jira_email"]
    jira_api_token = config["jira_api_token"]
    qualys_qql = config["qualys_qql"]
    qualys_tag = config["qualys_tag"]

    # validate if the tag exists - exit if not
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
        image_vulnerabilities = get_vulnerability_details_of_the_image(registry_repo_tag, image_sha)
        print(f"Creating JIRA tickets for all QIDs present in registry_repo_tag: {registry_repo_tag}")
        for qid_info in image_vulnerabilities:
            # print(json.dumps(qid_info, indent=4))

            # create JIRA ticket for each QID
            summary = f"QID {qid_info['qid']} | {registry_repo_tag}"
            create_jira_issue(summary, description_json=qid_info)

        #  tag the image with the qualys_tag
        assign_tag_to_assets(registry_repo_tag, qualys_tag, tag_uuid, image_uuid)

    print(f"<< Script Execution Completed >>")
