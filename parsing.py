import ijson


def parse_instances(filename, structure_prefix="Reservations.item.Instances.item"):
    with open(filename, "r") as f:
        instances = ijson.items(f, structure_prefix)
        instance_sg = {}
        for instance in instances:
            security_groups = set([group["GroupId"] for group in instance["NetworkInterfaces"]["Groups"]])
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
                policy["fromPort"] = int(permission["FromPort"])
                policy["toPort"] = int(permission["ToPort"])
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
