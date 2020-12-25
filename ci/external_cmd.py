import json
import subprocess

import click


class ExternalCmd:
    @staticmethod
    def _base_run(cmd, **kwargs):
        check_value = True
        if "check" in kwargs:
            check_value = kwargs.pop("check")

        try:
            output = subprocess.run(
                cmd, shell=True, encoding="UTF-8", check=check_value, **kwargs
            )
        except subprocess.CalledProcessError as err:
            raise click.ClickException(f"External Command has failed: {cmd}") from err

        return output

    @staticmethod
    def run(cmd):
        ExternalCmd._base_run(cmd)

    @staticmethod
    def run_silent(cmd):
        return ExternalCmd._base_run(cmd, **{"stdout": subprocess.PIPE})

    @staticmethod
    def run_and_parse_json(cmd):
        process = ExternalCmd.run_silent(cmd)
        return json.loads(process.stdout)
