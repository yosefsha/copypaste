from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class PastesNetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(
            self,
            "PastesVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
            ],
        )

        cloudfront_prefix_list = ec2.PrefixList.from_lookup(
            self,
            "CloudFrontPrefixList",
            prefix_list_name="com.amazonaws.global.cloudfront.origin-facing",
        )

        self.alb_security_group = ec2.SecurityGroup(
            self,
            "AlbSecurityGroup",
            vpc=self.vpc,
            description="Allow inbound HTTP only from CloudFront's origin-facing IPs",
            allow_all_outbound=True,
        )
        self.alb_security_group.add_ingress_rule(
            peer=ec2.Peer.prefix_list(cloudfront_prefix_list.prefix_list_id),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP from CloudFront",
        )
