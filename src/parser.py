import subprocess


def run_command(path: str) -> str:
    result = subprocess.run(
        ["mediainfo", path, "--Output=JSON"],
        capture_output=True,
        text=True,
    )
    return result.stdout