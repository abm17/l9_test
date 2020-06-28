# ReadMe

This is a generic script to filter AWS EC2 instances based on the security groups associated with them. It can be used to check if an instance can be reached **directly** from a specified IPv4/IPv6 IP, on a specific port using a specific protocol.
The script checks connectivity only at the instance-level and the output might not be correct if route tables, NACL or WAF are configured at the subnet level.

# Usage
The data structure reference for the data files is:
 - [Security Group](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_SecurityGroup.html)
 - [EC2 instances data](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html)

The prefix structure for the JSON file can be modified to support similar nested structures.The CLI supports the following arguments:

 - **<instance_file_path>** - absolute/relative path to file containing instances data
  - **<sg_file_path>** - absolute/relative path to file containing security groups data
 -  --**include_port** - comma separated list of ports to be permitted in the filter. A value of -1 will skip the check for port. This check is skipped by default.
 - --**exclude_port**  - comma separated list of ports to be restricted in the filter.
 - --**include_ipv4** - comma separated list of IPv4 addresses/CIDR blocks to be permitted in the filter. A value of -1 will skip the check for permission/restriction of IPv4 addresses. By default, it checks for all public addresses.
 - --**exclude_ipv4** - comma separated list of IPv4 addresses/CIDR blocks to be restricted in the filter. 
 - --**include_ipv6** - comma separated list of IPv6 addresses/CIDR blocks to be permitted in the filter. A value of -1 will skip the check for permission/restriction of IPv6 addresses. By default, it checks for all public addresses.
 - --**exclude_ipv6** - comma separated list of IPv6 addresses/CIDR blocks to be restricted in the filter. 
 - --**include_protocol** - comma separated list of permitted protocols. A value of -1 will skip this check.  This check is skipped by default.
- --**exclude_protocol** - comma separated list of permitted protocols.

## Example Usage

To find all instances that can be reached publicly (excluding SSH) via a IPv4 network:

    python3 main.py ../instances.json ../security_groups.json --include_protocol -1 --exclude_port 22 --include_ipv4 0.0.0.0/0 --include_ipv6 -1

To find all instances that can serve website traffic to a IPv4 and IPv6 network:

    python3 main.py ../instances.json ../security_groups.json --include_protocol tcp --include_port 80,443 --include_ipv4 0.0.0.0/0 --include_ipv6 ::/0

 

# Key Decisions

## Scalability

The script uses an iterative json parser to load one entry at a time to support infras having a large number of EC2 instances/security groups

Parsing and processing of instance data and security data is run in parallel to reduce runtime.

## Decoupling

The filter functionality is implemented sepearately from the parser in a separate file and can be modified to accomodate more filtering criteria. As of now, it supports filters to include/exclude IPs, ports and protocols.


```
