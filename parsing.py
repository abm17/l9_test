import ijson,argparse,pprint

def get_filter_dict(args):
    filter_dict = {}
    if args.include_ipv4 is not None:
        filter_dict["include_ipv4"] = set(args.include_ipv4.split(","))
    if args.exclude_ipv4 is not None:
        filter_dict["exclude_ipv4"] = set(args.exclude_ipv4.split(","))
    if args.include_ipv6 is not None:
        filter_dict["include_ipv6"] = set(args.include_ipv6.split(","))
    if args.exclude_ipv6 is not None:
        filter_dict["exclude_ipv6"] = set(args.exclude_ipv6.split(","))
    if args.include_port is not None:
        filter_dict["include_port"] = set([int(port) for port in args.include_port.split(",")])
    if args.exclude_port is not None:
        filter_dict["exclude_port"] = set([int(port) for port in args.exclude_port.split(",")])
    if args.include_protocol is not None:
        filter_dict["include_protocol"] = set([protocol for protocol in args.include_protocol.split(",")])
    if args.exclude_protocol is not None:
        filter_dict["exclude_protocol"] = set([protocol for protocol in args.exclude_protocol.split(",")])
    return filter_dict


def cli_parser():
    parser = argparse.ArgumentParser(description='Prints a list of instance-ids to STDOUT that can be accessed '
                                                 'directly using a specific ip/port/protocol')
    parser.add_argument("instance_file_path", help="Path to file containing instances data")
    parser.add_argument("sg_file_path", help="Path to file containing security group data")
    parser.add_argument("--include_ipv4", help="Comma separated list of permitted IPv4 addresses/CIDR blocks",
                        required=False, default=None)
    parser.add_argument("--exclude_ipv4", help="Comma separated list of restricted IPv4 addresses/CIDR blocks",
                        required=False, default=None)
    parser.add_argument("--include_ipv6", help="Comma separated list of permitted IPv6 addresses/CIDR blocks",
                        required=False, default=None)
    parser.add_argument("--exclude_ipv6", help="Comma separated list of restricted IPv6 addresses/CIDR blocks",
                        required=False, default=None)
    parser.add_argument("--include_port", help="Comma separated list of permitted ports", required=False, default=None)
    parser.add_argument("--exclude_port", help="Comma separated list of restricted ports", required=False, default=None)
    parser.add_argument("--include_protocol", help="Comma separated list of permitted protocols", required=False,
                        default=None)
    parser.add_argument("--exclude_protocol", help="Comma separated list of restricted protocols", required=False,
                        default=None)
    return parser


def parse_instances(filename, structure_prefix="Reservations.item.Instances.item"):
    with open(filename, "r") as f:
        instances = ijson.items(f, structure_prefix)
        instance_sg = {}
        for instance in instances:
            security_groups = set([group["GroupId"] for interface in instance["NetworkInterfaces"]
                                   for group in interface["Groups"]])
            instance_sg[instance["InstanceId"]] = {}
            instance_sg[instance["InstanceId"]]["security_groups"] = security_groups
            instance_sg[instance["InstanceId"]]["subnet"] = instance["SubnetId"]
        return instance_sg


def parse_security_groups(filename, structure_prefix="SecurityGroups.item"):
    with open(filename, "r") as f:
        security_groups = ijson.items(f, structure_prefix)
        sg_rules_ingress = {}
        sg_rules_egress = {}
        for group in security_groups:
            sg_id = group["GroupId"]
            sg_rules_ingress[sg_id] = []
            sg_rules_egress[sg_id] = []
            ip_permissions_ingress = group["IpPermissions"]
            for permission in ip_permissions_ingress:
                policy = {}
                if "FromPort" not in permission:
                    continue
                policy["FromPort"] = int(permission["FromPort"])
                policy["ToPort"] = int(permission["ToPort"])
                policy["Ipv4"] = [ip_range["CidrIp"] for ip_range in permission["IpRanges"]]
                policy["Ipv6"] = [ip_range["CidrIpv6"] for ip_range in permission["Ipv6Ranges"]]
                policy["protocol"] = permission["IpProtocol"]
                sg_rules_ingress[sg_id].append(policy)

            ip_permissions_egress = group["IpPermissionsEgress"]
            for permission in ip_permissions_egress:
                policy = {}
                policy["Ipv4"] = [ip_range["CidrIp"] for ip_range in permission["IpRanges"]]
                policy["Ipv6"] = [ip_range["CidrIpv6"] for ip_range in permission["Ipv6Ranges"]]
                policy["protocol"] = permission["IpProtocol"]
                sg_rules_egress[sg_id].append(policy)
        return sg_rules_ingress, sg_rules_egress
