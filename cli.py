from parsing import cli_parser,get_filter_dict,parse_instances,parse_security_groups
from pprint import pprint
from filter import sg_filter


if __name__=='__main__':
    parser = cli_parser()
    args = parser.parse_args()
    instances_file = args.instance_file_path
    sg_file = args.sg_file_path
    sg_file = args.sg_file_path
    filter_dict = get_filter_dict(args)
    pprint(filter_dict)
    instance_sg = parse_instances(instances_file)
    sg_rules_ingress,sg_rules_egress = parse_security_groups(sg_file)
    sg_filtered_ingress = sg_filter(sg_rules_ingress,"ingress",**filter_dict)
    pprint(sg_filtered_ingress)








