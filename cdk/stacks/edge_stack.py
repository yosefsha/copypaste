from pathlib import Path

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment
from constructs import Construct

STATIC_DIR = Path(__file__).resolve().parents[2] / "src" / "copypaste" / "static"


class PastesEdgeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        load_balancer,
        web_acl_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        static_bucket = s3.Bucket(
            self,
            "PastesStaticBucket",
            removal_policy=RemovalPolicy.RETAIN,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        self.distribution = cloudfront.Distribution(
            self,
            "PastesDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.LoadBalancerV2Origin(
                    load_balancer,
                    protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            ),
            additional_behaviors={
                "/static/*": cloudfront.BehaviorOptions(
                    origin=origins.S3BucketOrigin.with_origin_access_control(static_bucket),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                ),
            },
            web_acl_id=web_acl_arn,
        )

        self.static_bucket = static_bucket

        s3_deployment.BucketDeployment(
            self,
            "DeployStaticAssets",
            sources=[s3_deployment.Source.asset(str(STATIC_DIR))],
            destination_bucket=static_bucket,
            destination_key_prefix="static",
            distribution=self.distribution,
            distribution_paths=["/static/*"],
        )

        CfnOutput(self, "DistributionDomainName", value=self.distribution.distribution_domain_name)
