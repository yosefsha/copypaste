#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.compute_stack import PastesComputeStack
from stacks.data_stack import PastesDataStack
from stacks.edge_stack import PastesEdgeStack
from stacks.network_stack import PastesNetworkStack
from stacks.waf_stack import PastesWafStack

app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

data_stack = PastesDataStack(app, "PastesDataStack", env=env)
network_stack = PastesNetworkStack(app, "PastesNetworkStack", env=env)
compute_stack = PastesComputeStack(
    app,
    "PastesComputeStack",
    vpc=network_stack.vpc,
    alb_security_group=network_stack.alb_security_group,
    table=data_stack.table,
    env=env,
)
waf_stack = PastesWafStack(app, "PastesWafStack", env=env)
edge_stack = PastesEdgeStack(
    app,
    "PastesEdgeStack",
    load_balancer=compute_stack.load_balancer,
    web_acl_arn=waf_stack.web_acl.attr_arn,
    domain_name="paste.yossidemo.click",
    certificate_arn="arn:aws:acm:us-east-1:963352896991:certificate/2fac63ac-2858-4d7e-bd8e-b1b4e1c93d59",
    env=env,
)

app.synth()
