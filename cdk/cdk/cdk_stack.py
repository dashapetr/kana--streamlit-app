from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam
)
import aws_cdk as core


class CdkStack(core.Stack):
    def __init__(self, scope, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "StreamlitKanaVPC", max_azs=2)

        # Create ECS cluster
        cluster = ecs.Cluster(self, "StreamlitKanaCluster", vpc=vpc)

        # ECS optimized AMI
        ecs_optimized_image = ecs.EcsOptimizedImage.amazon_linux2()

        role = iam.Role(
            self, "InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess")
            ]
        )

        # Define a launch template for the Auto Scaling Group
        launch_template = ec2.LaunchTemplate(
            self,
            "LaunchTemplate",
            instance_type=ec2.InstanceType("t3.medium"),
            machine_image=ecs_optimized_image,
            role=role,
            user_data=ec2.UserData.custom(
                f"#!/bin/bash\n"
                f"echo ECS_CLUSTER={cluster.cluster_name} >> /etc/ecs/ecs.config\n"
            ),
        )

        # Create an AutoScalingGroup using the launch template
        asg = autoscaling.AutoScalingGroup(
            self,
            "AsgSpot",
            vpc=vpc,
            desired_capacity=2,
            min_capacity=1,
            max_capacity=5,
            launch_template=launch_template,
        )

        # Attach IAM policy for ECS
        asg.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess")
        )

        # Build Dockerfile from local folder and push to ECR
        image = ecs.ContainerImage.from_asset('app')

        # Create Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "StreamlitKanaService",
            cluster=cluster,  # ECS Cluster
            cpu=2048,  # CPU for the Fargate service
            desired_count=1,  # Number of tasks
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8501,  # Port for the container
            ),
            memory_limit_mib=4096,  # Memory for the Fargate service
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
