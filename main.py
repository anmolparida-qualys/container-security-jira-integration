from container_security import *
from jira import *
from config_loader import config

if __name__ == '__main__':
    # update values from config.json
    jira_domain = config["jira_domain"]
    jira_email = config["jira_email"]
    jira_api_token = config["jira_api_token"]
    qualys_qql = config["qualys_qql"]
    qualys_tag = config["qualys_tag"]

    # validate if the tag exists - exit if not
    # post https://gateway.qg1.apps.qualys.ca/csapi/v1.3/tag/exist

    qql = f"{qualys_qql} and not tags.name:{qualys_tag}"  # excluding the already tagged images

    # get all images with qql excluding the images already tagged
    # dict_registry_repo_tag_sha = get_all_images(qql="repo.repository:amazon/aws-network-policy-agent")
    dict_registry_repo_tag_sha = get_all_images(qql)
    print(dict_registry_repo_tag_sha)

    # get vulnerability QDS details to be populated in the JIRA issue
    for registry_repo_tag, sha in dict_registry_repo_tag_sha.items():
        print(f"Processing registry_repo_tag: {registry_repo_tag}")

        # get image level vulnerabilities - QIDs
        image_vulnerabilities = get_vulnerability_details_of_the_image(registry_repo_tag, sha)
        for qid_info in image_vulnerabilities:
            print(json.dumps(qid_info, indent=4))

            # create JIRA ticket for each QID
            summary = f"QID {qid_info['qid']} | {registry_repo_tag}"
            create_jira_issue(summary, description_json=qid_info)

        #  tag the image with the qualys_tag
