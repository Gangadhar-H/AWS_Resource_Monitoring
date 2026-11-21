"""Maps a finding to a human-readable suggestion. The tool never acts on it."""
from __future__ import annotations


def recommend(resource_type: str, status: str) -> str:
    if resource_type == "ebs":
        return ("Snapshot the volume if the data may be needed, then delete it "
                "to stop paying for unused storage.")
    if resource_type == "eip":
        return "Release this Elastic IP, or associate it with a running resource."
    if resource_type == "ec2" and status == "stopped":
        return ("Instance is stopped but its EBS volumes are still billed. "
                "Snapshot and delete the volumes, or terminate the instance if no longer needed.")
    if resource_type == "ec2" and status == "underutilized":
        return ("Downsize to a smaller instance type, or stop it if idle. "
                "Check memory and network usage first: CloudWatch does not report memory by default.")
    return "Review this resource."
