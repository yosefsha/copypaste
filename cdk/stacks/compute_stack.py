from pathlib import Path

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from constructs import Construct

REPO_ROOT = Path(__file__).resolve().parents[2]


class PastesComputeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.Vpc,
        alb_security_group: ec2.SecurityGroup,
        table,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster = ecs.Cluster(self, "PastesCluster", vpc=vpc)

        image_asset = ecr_assets.DockerImageAsset(
            self,
            "PastesImage",
            directory=str(REPO_ROOT),
            file="Dockerfile",
            exclude=["cdk", ".git", ".venv", ".pytest_cache", ".playwright-mcp"],
            platform=ecr_assets.Platform.LINUX_AMD64,
        )

        task_definition = ecs.FargateTaskDefinition(
            self,
            "PastesTaskDef",
            cpu=256,
            memory_limit_mib=512,
        )
        container = task_definition.add_container(
            "PastesContainer",
            image=ecs.ContainerImage.from_docker_image_asset(image_asset),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="pastes"),
            environment={
                "AWS_REGION": self.region,
                "PASTE_TABLE_NAME": table.table_name,
            },
        )
        container.add_port_mappings(ecs.PortMapping(container_port=5000))

        table.grant_read_write_data(task_definition.task_role)
        # grant_read_write_data doesn't cover these: ListTables isn't resource-scoped
        # (db.create_table's resource.tables.all() call), and TTL actions are a
        # separate action namespace (db._ensure_ttl_enabled runs on every worker boot).
        task_definition.task_role.add_to_policy(
            iam.PolicyStatement(actions=["dynamodb:ListTables"], resources=["*"])
        )
        task_definition.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=["dynamodb:UpdateTimeToLive", "dynamodb:DescribeTimeToLive"],
                resources=[table.table_arn],
            )
        )

        service_security_group = ec2.SecurityGroup(
            self,
            "ServiceSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
        )

        service = ecs.FargateService(
            self,
            "PastesService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            assign_public_ip=True,
            security_groups=[service_security_group],
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
        )

        alb = elbv2.ApplicationLoadBalancer(
            self,
            "PastesAlb",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_security_group,
        )
        listener = alb.add_listener("PastesListener", port=80, open=False)
        listener.add_targets(
            "PastesTargets",
            port=5000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[service],
            health_check=elbv2.HealthCheck(path="/healthz"),
        )
        service_security_group.add_ingress_rule(
            peer=alb_security_group,
            connection=ec2.Port.tcp(5000),
            description="Allow traffic from the ALB only",
        )

        self.load_balancer = alb

        CfnOutput(self, "LoadBalancerDNS", value=alb.load_balancer_dns_name)
