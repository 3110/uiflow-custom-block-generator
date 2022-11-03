import argparse
import json
import logging
import os
import sys

from .uiflow_custom_block import *
from .uiflow_custom_block_generator import UiFlowCustomBlockGenerator
from .uiflow_custom_block_parser import UiFlowCustomBlockParser

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
    "target_file",
    nargs=1,
    help="Custom Block Definition File(JSON) or M5B File",
)
parser.add_argument("--target-dir", "-t", help="Target Directory")
parser.add_argument("--debug", "-d", action="store_true", help="Debug Print")
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.INFO
logger = get_logger(__name__, log_level)

if UiFlowCustomBlockParser.isCustomBlockFile(args.target_file[0]):
    m5b_file = args.target_file[0]
    parser = UiFlowCustomBlockParser(logger)
    target_dir, setting, codes = parser.parse(m5b_file, target_dir=args.target_dir)

    setting_name = to_snake(os.path.splitext(os.path.basename(m5b_file))[0]) + "." + EXT_JSON

    os.makedirs(target_dir, exist_ok=True)
    with open(os.path.join(target_dir, setting_name), mode='w', encoding='UTF-8') as f:
        f.write(json.dumps(setting, indent=DEFAULT_JSON_INDENT, ensure_ascii=False))
    for name, code in codes.items():
        code_name = name + "." + EXT_PY
        with open(os.path.join(target_dir, code_name), mode='w', encoding='UTF-8') as f:
            f.write('\n'.join(code))
else:
    generator = UiFlowCustomBlockGenerator(args.target_file[0], target_dir=args.target_dir, logger=logger)
    generator.generate()
