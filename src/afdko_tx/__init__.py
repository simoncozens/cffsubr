import subprocess
import os
import tempfile

try:
    from importlib.resources import path
except ImportError:
    # use backport for python < 3.7
    from importlib_resources import path


__all__ = ["process", "Error"]

_SUPPORTED_OUTPUT_FORMATS = ("cff", "cff2")


try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"


class Error(Exception):
    pass


def run(*args, **kwargs):
    """Run the embedded tx executable with the list of positional arguments.
    Return a subprocess.CompletedProcess object with the following attributes:
    args, returncode, stdout, stderr.
    All keyword arguments are forwarded to subprocess.run function.
    """
    with path(__name__, "tx") as tx_cli:
        return subprocess.run([tx_cli] + list(args), **kwargs)


def subroutinize(fontdata: bytes, output_format="CFF2") -> bytes:
    """Run subroutinizer on the input font data and return processed output."""
    if not isinstance(fontdata, bytes):
        raise TypeError(f"expected bytes, found {type(fontdata).__name__}")
    output = output.lower()
    if output_format not in _SUPPORTED_OUTPUT_FORMATS:
        raise ValueError(f"Unsupported output format: '{output_format}'")
    # We can't read from stdin because of this issue:
    # https://github.com/adobe-type-tools/afdko/issues/937
    with tempfile.NamedTemporaryFile(prefix="tx-", delete=False) as tmp:
        tmp.write(fontdata)
    try:
        # write to stdout and capture output
        result = run(
            f"-{output_format}", "+S", "+b", tmp.name, capture_output=True, check=True
        )
    except subprocess.CalledProcessError as e:
        raise Error(e.stderr.decode())
    finally:
        os.remove(tmp.name)
    return result.stdout