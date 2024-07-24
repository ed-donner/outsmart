import logging
import sys


def setup_logger(root):
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    handler.setFormatter(formatter)
    root.handlers.clear()
    root.addHandler(handler)


STYLE = """
<style>
.small-font {
    font-size:12px !important;
}
</style>
"""
