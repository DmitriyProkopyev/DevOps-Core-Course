import os
import time
import requests
import pulumi
import pulumi.dynamic as dynamic
from pulumi import Config
from pulumi import Output, ResourceOptions

config = Config("yandex")

# 1) Read OAuth token from environment (same as Terraform)
OAUTH_TOKEN = os.environ.get("YC_OAUTH_TOKEN")
if not OAUTH_TOKEN:
    raise Exception("YC_OAUTH_TOKEN environment variable is not set")

FOLDER_ID = "b1g6pc9ifc5v88lqj4ij"
CLOUD_ID = "b1gl3bijlmooaqjl2vp6"


def get_iam_token(oauth_token: str) -> str:
    """Exchange OAuth token for IAM token (what Terraform provider does internally)."""
    resp = requests.post(
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        json={"yandexPassportOauthToken": oauth_token},
        headers={"Content-Type": "application/json"},
    )
    if not resp.ok:
        raise Exception(f"IAM token request failed: {resp.status_code} {resp.text}")
    data = resp.json()
    iam_token = data.get("iamToken")
    if not iam_token:
        raise Exception(f"No iamToken in response: {data}")
    return iam_token


# 2) Get IAM token at program start
IAM_TOKEN = get_iam_token(OAUTH_TOKEN)


class YandexVMProvider(dynamic.ResourceProvider):
    def create(self, props):
        headers = {
            "Authorization": f"Bearer {IAM_TOKEN}",   # IAM token, not OAuth
            "Content-Type": "application/json",
        }

        pulumi.log.info("Creating security group...")
        sg_resp = requests.post(
            "https://vpc.api.cloud.yandex.net/vpc/v1/securityGroups",
            headers=headers,
            json={
                "folderId": FOLDER_ID,
                "name": props["sg_name"],
                "description": "Allow SSH",
                "networkId": "enpb8u6so7r1apm1p1b6",
                "ruleSpecs": [
                    {
                        "direction": "EGRESS",
                        "protocolName": "ANY",
                        "cidrBlocks": {"v4CidrBlocks": ["0.0.0.0/0"]},
                    },
                    {
                        "direction": "INGRESS",
                        "protocolName": "TCP",
                        "ports": {"fromPort": 22, "toPort": 22},
                        "cidrBlocks": {"v4CidrBlocks": ["0.0.0.0/0"]},
                    },
                ],
            },
        )
        if not sg_resp.ok:
            raise Exception(f"SG creation failed: {sg_resp.status_code} {sg_resp.text}")

        sg_operation_id = sg_resp.json()["id"]
        pulumi.log.info(f"Waiting for SG operation {sg_operation_id}...")
        sg_id = None
        while True:
            op_resp = requests.get(
                f"https://operation.api.cloud.yandex.net/operations/{sg_operation_id}",
                headers=headers,
            )
            if not op_resp.ok:
                raise Exception(f"Failed to poll SG operation: {op_resp.status_code} {op_resp.text}")

            op_data = op_resp.json()
            if op_data.get("done"):
                if op_data.get("error"):
                    raise Exception(f"SG creation failed: {op_data['error']}")
                sg_id = op_data["metadata"]["securityGroupId"]
                pulumi.log.info(f"Security group created: {sg_id}")
                break
            time.sleep(2)

        pulumi.log.info("Fetching Ubuntu 24.04 image...")
        img_resp = requests.get(
            "https://compute.api.cloud.yandex.net/compute/v1/images:latestByFamily"
            "?folderId=standard-images&family=ubuntu-2404-lts",
            headers=headers,
        )
        if not img_resp.ok:
            raise Exception(f"Image fetch failed: {img_resp.status_code} {img_resp.text}")
        image_id = img_resp.json()["id"]
        pulumi.log.info(f"Using image: {image_id}")

        pulumi.log.info("Creating VM instance...")
        vm_resp = requests.post(
            "https://compute.api.cloud.yandex.net/compute/v1/instances",
            headers=headers,
            json={
                "folderId": FOLDER_ID,
                "name": props["name"],
                "zoneId": "ru-central1-b",
                "platformId": "standard-v3",
                "resourcesSpec": {
                    "cores": "2",
                    "memory": str(2 * 1024 * 1024 * 1024),
                    "coreFraction": "20",
                },
                "bootDiskSpec": {
                    "diskSpec": {
                        "size": str(10 * 1024 * 1024 * 1024),
                        "typeId": "network-hdd",
                        "imageId": image_id,
                    }
                },
                "networkInterfaceSpecs": [
                    {
                        "subnetId": "e2lev91h4vsasfe6gd5v",
                        "securityGroupIds": [sg_id],
                        "primaryV4AddressSpec": {
                            "oneToOneNatSpec": {"ipVersion": "IPV4"}
                        },
                    }
                ],
                "metadata": {"user-data": props["user_data"]},
            },
        )
        if not vm_resp.ok:
            raise Exception(f"VM creation failed: {vm_resp.status_code} {vm_resp.text}")

        vm_operation_id = vm_resp.json()["id"]
        pulumi.log.info(f"Waiting for VM operation {vm_operation_id}...")
        vm_id = None
        while True:
            op_resp = requests.get(
                f"https://operation.api.cloud.yandex.net/operations/{vm_operation_id}",
                headers=headers,
            )
            if not op_resp.ok:
                raise Exception(f"Failed to poll VM operation: {op_resp.status_code} {op_resp.text}")

            op_data = op_resp.json()
            if op_data.get("done"):
                if op_data.get("error"):
                    raise Exception(f"VM creation failed: {op_data['error']}")
                vm_id = op_data["response"]["id"]
                pulumi.log.info(f"VM created: {vm_id}")
                break
            time.sleep(2)

        pulumi.log.info("Waiting for NAT IP assignment...")
        nat_ip = None
        while True:
            vm_details = requests.get(
                f"https://compute.api.cloud.yandex.net/compute/v1/instances/{vm_id}",
                headers=headers,
            )
            if vm_details.ok:
                vm_data = vm_details.json()
                if vm_data.get("networkInterfaces"):
                    ni = vm_data["networkInterfaces"][0]
                    nat_data = ni.get("primaryV4Address", {}).get("oneToOneNat")
                    if nat_data and nat_data.get("address"):
                        nat_ip = nat_data["address"]
                        pulumi.log.info(f"NAT IP assigned: {nat_ip}")
                        break
            time.sleep(2)

        return dynamic.CreateResult(
            id_=vm_id,
            outs={"vm_id": vm_id, "sg_id": sg_id, "nat_ip": nat_ip},
        )

    def delete(self, id, props):
        headers = {"Authorization": f"Bearer {IAM_TOKEN}"}

        pulumi.log.info(f"Deleting VM {id}...")
        vm_del = requests.delete(
            f"https://compute.api.cloud.yandex.net/compute/v1/instances/{id}",
            headers=headers,
        )
        if vm_del.ok:
            operation_id = vm_del.json()["id"]
            while True:
                op_resp = requests.get(
                    f"https://operation.api.cloud.yandex.net/operations/{operation_id}",
                    headers=headers,
                )
                if op_resp.ok and op_resp.json().get("done"):
                    pulumi.log.info("VM deleted")
                    break
                time.sleep(2)

        if "sg_id" in props:
            time.sleep(3)
            pulumi.log.info(f"Deleting security group {props['sg_id']}...")
            requests.delete(
                f"https://vpc.api.cloud.yandex.net/vpc/v1/securityGroups/{props['sg_id']}",
                headers=headers,
            )
            pulumi.log.info("Security group deleted")


class YandexVM(dynamic.Resource):
    vm_id: Output[str]
    sg_id: Output[str]
    nat_ip: Output[str]

    def __init__(self, name: str, ssh_key: str, opts: ResourceOptions | None = None):
        user_data = f"""#cloud-config
users:
  - name: ubuntu
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - {ssh_key}"""

        # Declare output keys with placeholder values; provider will fill them via outs.
        props = {
            "name": name,
            "sg_name": f"{name}-sg",
            "user_data": user_data,
            "vm_id": None,
            "sg_id": None,
            "nat_ip": None,
        }

        super().__init__(YandexVMProvider(), name, props, opts)


vm = YandexVM("minimal-vm", config.require("ssh_public_key"))
pulumi.export("vm_external_ip", vm.nat_ip)