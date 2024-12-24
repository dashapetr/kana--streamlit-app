from aws_cdk import App
import aws_cdk as core
from cdk.cdk_stack import CdkStack

# Specify your AWS account ID and region
env = core.Environment(account="YOUR_ACCOUNT_ID", region="us-east-1")

app = App()
CdkStack(app, "KanaStreamlitApp", env=env)

app.synth()
