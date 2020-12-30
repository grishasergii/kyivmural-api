import click
import json

from ci.external_cmd import ExternalCmd


def _get_output_from_stack_description(stack_description, output_key):
    for output in stack_description["Outputs"]:
        if output["OutputKey"] == output_key:
            return output["OutputValue"]
    raise KeyError(f"{output_key} not found")


@click.command()
@click.option("--stack-name", help="Name of the stack")
@click.option("--stage-name", help="Name of the api stage")
def deploy(stack_name, stage_name):
    click.echo(f"Fetching REST API id from {stack_name} stack...")
    stack_descriptions = ExternalCmd.run_and_parse_json(
        f"aws cloudformation describe-stacks --stack-name {stack_name}"
    )

    stack_description = stack_descriptions["Stacks"][0]
    api_id = _get_output_from_stack_description(stack_description, "RestApiId")
    log_group_arn = _get_output_from_stack_description(stack_description, "ApiGatewayAccessLogGroupArn")

    click.echo(f"API id is {api_id}")
    click.echo(f"Deploying {stage_name} stage...")
    ExternalCmd.run(
        f"aws apigateway create-deployment --rest-api-id {api_id} --stage-name {stage_name}"
    )
    operations = [
        {
            "op": "add",
            "path": "/accessLogSettings/destinationArn",
            "value": log_group_arn
        },
        {
            "op": "add",
            "path": "/accessLogSettings/format",
            "value": '{ "requestId":"$context.requestId", "ip": "$context.identity.sourceIp", "caller":"$context.identity.caller", "user":"$context.identity.user","requestTime":"$context.requestTime", "httpMethod":"$context.httpMethod","resourcePath":"$context.resourcePath", "status":"$context.status","protocol":"$context.protocol", "responseLength":"$context.responseLength" }'
        },
    ]
    ExternalCmd.run(
        f"aws apigateway update-stage --rest-api-id {api_id} --stage-name {stage_name} --patch-operations {json.dumps(operations)}"
    )
    click.echo("Done")


if __name__ == "__main__":
    deploy()
