import argparse
import logging
import sys

from .uiflow_custom_block_generator import UiFlowCustomBlockGenerator

LOG_FORMAT = "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)s | %(funcName)s) %(message)s"


def get_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(level)
    logger.addHandler(sh)
    return logger


parser = argparse.ArgumentParser(
    prog="python -m uiflow_custom_block_generator", description="Generating a custom block file for UiFlow"
)
parser.add_argument(
    "config",
    nargs=1,
    type=argparse.FileType("r", encoding="utf-8"),
    help="Custom Block Definition File(JSON)",
)
parser.add_argument("--target-dir", "-t", help="Target Directory")
parser.add_argument("--debug", "-d", action="store_true", help="Debug Print")
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.INFO
logger = get_logger(__name__, log_level)
generator = UiFlowCustomBlockGenerator(args.config[0], target_dir=args.target_dir, logger=logger)
generator.generate()
