from parsing import cli_parser,get_filter_dict,parse_instances,parse_security_groups
from filter import sg_filter,check_subnet_public
import sys
from multiprocessing import Pool


def process_sgs(args):
    sg_file = args.sg_file_path
    filter_dict = get_filter_dict(args)
    sg_rules_ingress, sg_rules_egress = parse_security_groups(sg_file)
    all_sgs = set(sg_rules_egress.keys()).union(sg_rules_ingress.keys())
    sg_filtered_ingress = sg_filter(sg_rules_ingress, "ingress", **filter_dict)
    sg_filtered_egress = sg_filter(sg_rules_egress, "eggress", **filter_dict)
    sg_filtered = sg_filtered_egress.intersection(sg_filtered_ingress)
    data_dict = {
        "sg_filtered":sg_filtered,
        "all_sgs":all_sgs
    }
    return data_dict


if __name__=='__main__':
    parser = cli_parser()
    args = parser.parse_args()
    instances_file = args.instance_file_path

    pool = Pool(processes=2)
    instance_sg = pool.apply_async(parse_instances,([instances_file]))
    sg_filtered = pool.apply_async(process_sgs,([args]))
    instance_sg = instance_sg.get()
    sg_data = sg_filtered.get()
    sg_filtered = sg_data["sg_filtered"]
    all_sgs = sg_data["all_sgs"]

    instance_ids = instance_sg.keys()
    all_instance_sgs = set()
    for id in instance_ids:
        subnet = instance_sg[id]["subnet"]
        instance_groups = instance_sg[id]["security_groups"]
        all_instance_sgs.update(instance_groups)
        common_groups = sg_filtered.intersection(instance_groups)
        if len(common_groups) > 0 and check_subnet_public(subnet):
            output = "Instance_id:%s, Filtered groups: %s\n" %(id,",".join(common_groups))
            sys.stdout.write(output)

    # Check for missing security groups
    unknown_groups = all_instance_sgs.difference(all_sgs)
    if len(unknown_groups) > 0:
        error = "Unknown security groups: %s" %(",".join(unknown_groups))
        sys.stderr.write(error)












