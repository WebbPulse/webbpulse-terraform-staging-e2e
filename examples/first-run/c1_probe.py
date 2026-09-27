"""Throwaway C1 isolation probe: reports only caller ARNs and error codes, never keys."""

import json
import re
import urllib.request
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

ACCOUNT = "870550636948"
BUCKET = "webbpulse-terraform-staging-state"


def own_workspace():
    """The run's workspace id, read from the backend override the runner writes."""
    for path in Path(".").glob("*.tf"):
        match = re.search(r'workspace_key_prefix = "workspaces/([^/"]+)/env"', path.read_text())
        if match:
            return match.group(1)
    return "unknown"


WORKSPACE = own_workspace()
OTHER_PREFIX = "workspaces/ws-01ZZZZZZZZZZZZZZZZZZZZZZZZ/"
ROLES = {
    "workspace_e2e": f"arn:aws:iam::{ACCOUNT}:role/webbpulse-terraform-staging-workspace-e2e",
    "run_role": f"arn:aws:iam::{ACCOUNT}:role/webbpulse-terraform-staging-run-role",
}


def outcome(call):
    """`allowed` or the AWS error code, nothing else."""
    try:
        call()
        return "allowed"
    except ClientError as error:
        return str(error.response.get("Error", {}).get("Code", "ClientError"))
    except Exception as error:
        return type(error).__name__


def arn(session):
    """The caller ARN of a session, or its error code."""
    try:
        return session.client("sts").get_caller_identity()["Arn"]
    except ClientError as error:
        return str(error.response.get("Error", {}).get("Code", "ClientError"))
    except Exception as error:
        return type(error).__name__


def probe(prefix, session, results):
    """Try the cross workspace moves from one session."""
    sts = session.client("sts")
    s3 = session.client("s3")
    results[f"{prefix}_caller"] = arn(session)
    for name, role in ROLES.items():
        results[f"{prefix}_assume_{name}"] = outcome(
            lambda role=role: sts.assume_role(RoleArn=role, RoleSessionName="c1-probe", ExternalId=WORKSPACE)
        )
    results[f"{prefix}_ls_other_prefix"] = outcome(
        lambda: s3.list_objects_v2(Bucket=BUCKET, Prefix=OTHER_PREFIX, MaxKeys=1)
    )
    results[f"{prefix}_ls_bucket_root"] = outcome(lambda: s3.list_objects_v2(Bucket=BUCKET, Prefix="", MaxKeys=1))
    results[f"{prefix}_ls_own_prefix"] = outcome(
        lambda: s3.list_objects_v2(Bucket=BUCKET, Prefix=f"workspaces/{WORKSPACE}/", MaxKeys=1)
    )


def task_role_session(results):
    """The task role session, if plan code can still find its credential endpoint."""
    try:
        with open("/proc/1/environ", "rb") as handle:
            entries = dict(
                item.split("=", 1) for item in handle.read().decode().split("\0") if "=" in item
            )
    except Exception as error:
        results["task_role_environ"] = type(error).__name__
        return None
    uri = entries.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI", "")
    results["task_role_environ"] = "relative_uri_found" if uri else "no_relative_uri"
    if not uri:
        return None
    try:
        with urllib.request.urlopen(f"http://169.254.170.2{uri}", timeout=5) as response:
            creds = json.load(response)
    except Exception as error:
        results["task_role_endpoint"] = type(error).__name__
        return None
    results["task_role_endpoint"] = "credentials_returned"
    return boto3.session.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["Token"],
        region_name="us-west-2",
    )


def main():
    """Emit one flat JSON object of strings for the external data source."""
    results = {"own_workspace": WORKSPACE}
    probe("run_role", boto3.session.Session(region_name="us-west-2"), results)
    probe("state", boto3.session.Session(profile_name="webbpulse-state", region_name="us-west-2"), results)
    task = task_role_session(results)
    if task is not None:
        probe("task_role", task, results)
    print(json.dumps(results))


main()
