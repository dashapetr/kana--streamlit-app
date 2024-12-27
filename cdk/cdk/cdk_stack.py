from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_wafv2 as wafv2,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_elasticloadbalancingv2 as elbv2,
    aws_secretsmanager as secretsmanager,
)
import aws_cdk as core
from config import Config


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
            domain_name="kana.example.com",
            validation=acm.CertificateValidation.from_dns()
        )

        # Create Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "StreamlitKanaWebApp",
            cluster=cluster,  # ECS Cluster
            cpu=Config.CPU,  # CPU for the Fargate service
            desired_count=1,  # Number of tasks
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8501,  # Port for the container
            ),
            memory_limit_mib=Config.MEMORY,  # Memory for the Fargate service
            public_load_balancer=True,  # Expose load balancer to the public
            certificate=certificate,
            redirect_http=True
        )

        # Generate secure headers from Secrets Manager
        custom_header_secret  = secretsmanager.Secret(
            self, "CustomHeaderSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                exclude_punctuation=True,
                include_space=False,
                password_length=32,
                secret_string_template="{}",
                generate_string_key="header_value"
            )
        )

        # Restrict ALB Listener Rule to Requests with Custom Header
        fargate_service.listener.add_action(
            "RestrictToCustomHeader",
            priority=1,
            conditions=[
                elbv2.ListenerCondition.http_header(
                    name="X-Custom-Header",
                    values=[custom_header_secret.secret_value_from_json("header_value").to_string()]
                )
            ],
            action=elbv2.ListenerAction.forward(target_groups=[fargate_service.target_group])
        )

        # Default Action: Return 403 for Other Requests
        fargate_service.listener.add_action(
            "DefaultDenyAction",
            priority=2,
            conditions=[elbv2.ListenerCondition.path_patterns(["/*"])],
            action=elbv2.ListenerAction.fixed_response(
                status_code=403,
                content_type="text/plain",
                message_body="Access Denied"
            )
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
            scope="CLOUDFRONT",
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

        # Create CloudFront distribution
        cloudfront_distribution = cloudfront.Distribution(
            self, "StreamlitKanaCloudFront",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.LoadBalancerV2Origin(
                    fargate_service.load_balancer,
                    protocol_policy=cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
                    custom_headers={"X-Custom-Header":
                                        custom_header_secret.secret_value_from_json("header_value").to_string()}
                ),
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=["kana.example.com"],
            certificate=certificate,
            enable_logging=True,
            web_acl_id=waf.attr_arn
        )

        # Add Route53 A Record
        hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name="example.com")
        route53.ARecord(
            self, "KanaAppAliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(cloudfront_distribution)),
            record_name="kana"  # This will create the record 'kana.example.com'
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
