import click
import os
from ci.external_cmd import ExternalCmd
from pathlib import Path
import shutil


@click.command()
@click.option("--layer-name", help="Layer name")
@click.option("--path", help="Path to the folder with CFN templates to package")
@click.option("--main-template", help="Name of the main template file")
@click.option("--branch", help="Branch name")
@click.option("--artifacts-bucket", help="S3 bucket for artifacts")
@click.option("--cfn-bucket", help="S3 bucket for cfn templates")
def package(layer_name, path, main_template, branch, artifacts_bucket, cfn_bucket):
    out_dir = os.path.join("build", "templates")
    if Path(out_dir).exists():
        shutil.rmtree(out_dir)
    Path(out_dir).mkdir(exist_ok=True, parents=True)

    for template_file in os.listdir(path):
        if template_file.endswith(".cfn"):
            if template_file == main_template:
                continue
            template_file_full_path = os.path.join(path, template_file)
            out_path = os.path.join(out_dir, template_file)
            click.echo(f"Packaging {template_file} to {out_path}")
            ExternalCmd.run(
                f"aws cloudformation package "
                f"--template-file {template_file_full_path} "
                f"--s3-bucket {artifacts_bucket} "
                f"--s3-prefix {layer_name}/{branch} "
                f"--output-template-file {out_path}"
            )

            click.echo(f"Uploading {out_path} to {cfn_bucket}")
            ExternalCmd.run(
                f"aws s3 cp {out_path} s3://{cfn_bucket}/{layer_name}/{branch}/{template_file}"
            )


if __name__ == "__main__":
    package()
