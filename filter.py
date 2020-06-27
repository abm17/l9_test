import ipaddress


def check_subnet_public(subnet_id):
    """
    Stub for public subnet check
    Description: https://www.cloudconformity.com/knowledge-base/aws/EC2/instance-not-in-public-subnet.html
    """
    return True

def check_ip_ranges(ip_ranges, include_ip, exclude_ip, mode):
    if mode == "Ipv4":
        convert_to_network = ipaddress.IPv4Network
    elif mode == "Ipv6":
        convert_to_network = ipaddress.IPv6Network
    ip_ranges = [convert_to_network(ip_range) for ip_range in ip_ranges]
    include_ip = [convert_to_network(ip_range) for ip_range in include_ip]
    exclude_ip = [convert_to_network(ip_range) for ip_range in exclude_ip]
    all_inclusion_checks = []
    all_exclusion_checks = []
    for ip_range in ip_ranges:
        check = [ip.subnet_of(ip_range) for ip in include_ip]
        all_inclusion_checks.append(any(check))
        check = [not ip.subnet_of(ip_range) for ip in exclude_ip]
        all_exclusion_checks.append(all(check))
    return any(all_inclusion_checks) and all(all_exclusion_checks)


def sg_filter(sg_dict,mode,**filter_args):
    include_port = filter_args.get("include_port",set())
    exclude_port = filter_args.get("exclude_port", set())
    include_ipv4 = filter_args.get("include_ipv4", set())
    exclude_ipv4 = filter_args.get("exclude_ipv4", set())
    include_ipv6 = filter_args.get("include_ipv6", set())
    exclude_ipv6 = filter_args.get("exclude_ipv6", set())
    exclude_protocol = filter_args.get("exclude_protocol", set())
    include_protocol = filter_args.get("include_protocol", {})
    sg_all = sg_dict.keys()
    filtered_sgs = set()

    for sg in sg_all:
        rules = sg_dict[sg]
        if mode == "ingress":
            if "-1" not in include_port:
                rules = [rule for rule in rules if include_port.issubset(set(range(rule["FromPort"],rule["ToPort"]+1))) and exclude_port.isdisjoint(set(range(rule["FromPort"],rule["ToPort"]+1)))]
            if "-1" not in include_protocol:
                rules = [rule for rule in rules if rule["protocol"] in include_protocol]
            if "-1" not in exclude_protocol:
                rules = [rule for rule in rules if rule["protocol"] not in exclude_protocol]
        if "-1" not in include_ipv4:
            rules = [rule for rule in rules if check_ip_ranges(rule["Ipv4"], include_ipv4, exclude_ipv4,"Ipv4")]
        if "-1" not in include_ipv6:
            rules = [rule for rule in rules if check_ip_ranges(rule["Ipv6"], include_ipv6, exclude_ipv6, "Ipv6")]
        if rules:
            filtered_sgs.add(sg)
    return filtered_sgs
