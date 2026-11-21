"""Hardcoded pricing ASSUMPTIONS (USD, approximate on-demand Linux, us-east-1).

These are NOT live prices. Prices vary by region and change over time, so verify
them on the AWS pricing page / AWS Pricing Calculator and state this assumption
in your report. Replace this module with the AWS Price List API later.
"""

HOURS_PER_MONTH = 730

# EC2 on-demand, USD per hour
EC2_HOURLY = {
    "t2.micro": 0.0116,
    "t2.small": 0.0230,
    "t2.medium": 0.0464,
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "t3.large": 0.0832,
    "t3a.micro": 0.0094,
    "m5.large": 0.0960,
    "m5.xlarge": 0.1920,
    "c5.large": 0.0850,
    "r5.large": 0.1260,
}
EC2_DEFAULT_HOURLY = 0.05  # used when instance type is not in the table

# EBS, USD per GB-month
EBS_GB_MONTH = {
    "gp3": 0.08,
    "gp2": 0.10,
    "io1": 0.125,
    "io2": 0.125,
    "st1": 0.045,
    "sc1": 0.015,
    "standard": 0.05,
}
EBS_DEFAULT_GB_MONTH = 0.10

# Public IPv4 address not in use, USD per hour (AWS charges for all public IPv4)
EIP_HOURLY = 0.005
