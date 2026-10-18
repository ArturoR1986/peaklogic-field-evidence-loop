"""Read-only AWS identity/inventory check. Never launches or modifies a resource."""
from __future__ import annotations
import argparse
import json
import os
from datetime import datetime, timezone


def inspect(session, *, region: str, expected_account: str | None):
    from botocore.config import Config
    cfg = Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 1})
    report = {"task_id": "F03", "region": region, "checked_at": datetime.now(timezone.utc).isoformat(),
              "writes_attempted": False, "credit_coverage": "NOT_VERIFIED",
              "spending_limit": "NOT_VERIFIED", "deployment_authorized_by_this_script": False}
    if session.get_credentials() is None:
        return {**report, "status": "BLOCKED_NO_AWS_CREDENTIALS"}
    identity = session.client("sts", region_name=region, config=cfg).get_caller_identity()
    report["account"] = identity["Account"]
    report["caller_arn"] = identity["Arn"]
    if not expected_account or identity["Account"] != expected_account:
        return {**report, "status": "BLOCKED_ACCOUNT_CONFIRMATION_REQUIRED"}
    client = session.client("ec2", region_name=region, config=cfg)
    pages = client.get_paginator("describe_instances").paginate(Filters=[
        {"Name": "tag:Project", "Values": ["PeakLogic-F03"]},
        {"Name": "instance-state-name", "Values": ["running", "stopped", "pending"]}])
    report["tagged_instances"] = [
        {"instance_id": instance["InstanceId"], "state": instance["State"]["Name"],
         "instance_type": instance["InstanceType"],
         "root_device_type": instance.get("RootDeviceType"),
         "has_public_ip": bool(instance.get("PublicIpAddress")),
         "security_group_ids": [g["GroupId"] for g in instance.get("SecurityGroups", [])],
         "volume_ids": [m["Ebs"]["VolumeId"] for m in instance.get("BlockDeviceMappings", []) if "Ebs" in m]}
        for page in pages for reservation in page["Reservations"] for instance in reservation["Instances"]]
    return {**report, "status": "IDENTITY_AND_TAGGED_INVENTORY_READ_ONLY",
            "next_gate": "Verify credits, limits, scoped SSM access and persistent volume; no deployment was performed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="eu-north-1")
    parser.add_argument("--expected-account")
    parser.add_argument("--profile")
    parser.add_argument("--use-instance-profile", action="store_true",
                        help="Allow IMDS credential discovery only on the authorized EC2 host")
    args = parser.parse_args()
    if not args.use_instance_profile:
        os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
    import boto3
    try:
        result = inspect(boto3.Session(profile_name=args.profile), region=args.region,
                         expected_account=args.expected_account)
    except Exception as exc:
        # Service errors can contain account IDs; retain output privately. Never
        # print credentials, request signing data, environment dumps or debug logs.
        result = {"task_id": "F03", "status": "BLOCKED_READ_ONLY_PREFLIGHT",
                  "error_type": type(exc).__name__, "writes_attempted": False}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "IDENTITY_AND_TAGGED_INVENTORY_READ_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
