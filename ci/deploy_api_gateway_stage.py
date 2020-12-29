import click

from ci.external_cmd import ExternalCmd


@click.command()
@click.option("--stack-name", help="Name of the stack")
@click.option("--stage-name", help="Name of the api stage")
def deploy(stack_name, stage_name):
    click.echo(f"Fetching REST API id from {stack_name} stack...")
    stack_descriptions = ExternalCmd.run_and_parse_json(
        f"aws cloudformation describe-stacks --stack-name {stack_name}"
    )
    api_id = None
    stack_description = stack_descriptions["Stacks"][0]
    for output in stack_description["Outputs"]:
        if output["OutputKey"] == "RestApiId":
            api_id = output["OutputValue"]
            break

    if not api_id:
        raise click.ClickException("RestApiId not found in stack outputs")

    click.echo(f"API id is {api_id}")
    click.echo(f"Deploying {stage_name} stage...")
    ExternalCmd.run(
        f"aws apigateway create-deployment --rest-api-id {api_id} --stage-name {stage_name}"
    )
    click.echo("Done")


if __name__ == "__main__":
    deploy()
