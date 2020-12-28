import click

from ci.external_cmd import ExternalCmd


def _stack_exists(stack_name):
    result = ExternalCmd.run_and_parse_json(
        f"aws cloudformation list-stacks --stack-status-filter "
        "UPDATE_COMPLETE "
        "CREATE_COMPLETE "
        "UPDATE_IN_PROGRESS "
        "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS "
        "ROLLBACK_COMPLETE "
        "UPDATE_ROLLBACK_COMPLETE "
    )
    stacks = result.get("StackSummaries", [])
    for stack in stacks:
        if stack["StackName"] == stack_name:
            return True
    return False


@click.command()
@click.option("--template-file", help="Template file")
@click.option("--layer-name", help="Layer name")
@click.option("--branch", help="Branch name")
def provision(template_file, layer_name, branch):
    stack_name = f"{layer_name}-{branch}"
    click.echo(f"Provisioning {stack_name}")
    if _stack_exists(stack_name):
        click.echo(f"Stack '{stack_name}' already exists. Will update")
        result = ExternalCmd.run_and_parse_json(
            f"aws cloudformation update-stack "
            f"--stack-name {stack_name} "
            f"--template-body file://{template_file} "
            f"--parameters ParameterKey=Branch,ParameterValue={branch} "
            "--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND"
        )
        stack_id = result["StackId"]
        click.echo("Waiting for the stack-update-complete confirmation...")
        ExternalCmd.run(
            f"aws cloudformation wait stack-update-complete --stack-name {stack_id}"
        )
    else:
        click.echo(f"Stack '{stack_name}' does not exist. Will create")
        result = ExternalCmd.run_and_parse_json(
            f"aws cloudformation create-stack "
            f"--stack-name {stack_name} "
            f"--template-body file://{template_file} "
            f"--parameters ParameterKey=Branch,ParameterValue={branch} "
            "--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND"
        )
        stack_id = result["StackId"]
        click.echo("Waiting for the stack-create-complete confirmation...")
        ExternalCmd.run(
            f"aws cloudformation wait stack-create-complete --stack-name {stack_id}"
        )

    click.echo("Confirmed")


if __name__ == "__main__":
    provision()
