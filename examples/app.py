#!/usr/bin/env python3
import aws_cdk as cdk

from examples.examples_stack import ExamplesStack


app = cdk.App()
ExamplesStack(app, "ExamplesStack", environment="nonprod")

app.synth()
