from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_wafv2 as wafv2
)
import aws_cdk as core
from config import cpu, memory


class CdkStack(core.Stack):
    def __init__(self, scope, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "StreamlitKanaVPC", max_azs=2)

        # Create ECS cluster
        cluster = ecs.Cluster(self, "StreamlitKanaCluster", vpc=vpc)

        # Create IAM Role with least privilege
        role = iam.Role(
            self, "InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role")
            ]
        )

        # Build Dockerfile from local folder and push to ECR
        image = ecs.ContainerImage.from_asset('app')

        # HTTPS Certificate
        certificate = acm.Certificate(
            self, "Certificate",
            domain_name="example.com",
            validation=acm.CertificateValidation.from_dns()
        )

        # Create Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "StreamlitKanaWebApp",
            cluster=cluster,  # ECS Cluster
            cpu=cpu,  # CPU for the Fargate service
            desired_count=1,  # Number of tasks
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8501,  # Port for the container
            ),
            memory_limit_mib=memory,  # Memory for the Fargate service
            public_load_balancer=True,  # Expose load balancer to the public
            certificate=certificate,
            redirect_http=True
        )

        # Setup task auto-scaling
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=5)
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )

        # Add WAF Web ACL with default AWS Managed Rules
        waf = wafv2.CfnWebACL(
            self, "StreamlitKanaWAF",
            scope="REGIONAL",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="StreamlitKanaWAF",
                sampled_requests_enabled=True,
            ),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesCommonRuleSet",
                    priority=1,
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(none={}),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="AWSManagedRulesCommonRuleSet",
                        sampled_requests_enabled=True,
                    ),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name="AWSManagedRulesCommonRuleSet",
                            vendor_name="AWS"
                        )
                    )
                )
            ]
        )

        # Associate WAF with ALB
        waf_association = wafv2.CfnWebACLAssociation(
            self, "WafAssociation",
            resource_arn=fargate_service.load_balancer.load_balancer_arn,
            web_acl_arn=waf.attr_arn
        )

        # Create CloudFront distribution
        cloudfront_distribution = cloudfront.Distribution(
            self, "StreamlitKanaCloudFront",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.LoadBalancerV2Origin(
                    fargate_service.load_balancer,
                    protocol_policy=cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
                    http_port=80,
                    https_port=443,
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=["example.com"],
            certificate=certificate,
            enable_logging=True
        )

        # Add stack outputs
        core.CfnOutput(
            self, "LoadBalancerAddress",
            value=fargate_service.load_balancer.load_balancer_dns_name,
            description="Public address of the ALB (HTTP/HTTPS)",
        )

        core.CfnOutput(
            self, "CloudFrontAddress",
            value=f"https://{cloudfront_distribution.distribution_domain_name}",
            description="Public address of the CloudFront distribution (HTTPS)",
        )
