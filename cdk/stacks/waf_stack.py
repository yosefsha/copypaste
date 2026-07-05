from aws_cdk import Stack
from aws_cdk import aws_wafv2 as wafv2
from constructs import Construct


class PastesWafStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.web_acl = wafv2.CfnWebACL(
            self,
            "PastesWebAcl",
            scope="CLOUDFRONT",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name="PastesWebAcl",
            ),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name="RateLimitCreateRoute",
                    priority=1,
                    action=wafv2.CfnWebACL.RuleActionProperty(block={}),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        rate_based_statement=wafv2.CfnWebACL.RateBasedStatementProperty(
                            limit=200,
                            aggregate_key_type="IP",
                            scope_down_statement=wafv2.CfnWebACL.StatementProperty(
                                byte_match_statement=wafv2.CfnWebACL.ByteMatchStatementProperty(
                                    search_string="/",
                                    field_to_match=wafv2.CfnWebACL.FieldToMatchProperty(
                                        uri_path={}
                                    ),
                                    text_transformations=[
                                        wafv2.CfnWebACL.TextTransformationProperty(
                                            priority=0, type="NONE"
                                        )
                                    ],
                                    positional_constraint="EXACTLY",
                                )
                            ),
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="RateLimitCreateRoute",
                    ),
                )
            ],
        )
