import click
from ci.external_cmd import ExternalCmd


@click.command()
@click.option("--template-file", help="Template file")
@click.option("--layer-name", help="Layer name")
@click.option("--branch", help="Branch name")
def provision(template_file, layer_name, branch):
    stack_name = f"{layer_name}-{branch}"
    click.echo(f"Provisioning {stack_name}...")
    ExternalCmd.run(
        f"aws cloudformation create-stack "
        f"--stack-name {stack_name} "
        f"--template-body file://{template_file} "
        f"--parameters ParameterKey=Branch,ParameterValue={branch}"
    )


if __name__ == "__main__":
    provision()
