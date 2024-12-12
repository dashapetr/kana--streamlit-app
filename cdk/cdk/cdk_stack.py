from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam
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
        )

        # Setup task auto-scaling
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=5)
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )
