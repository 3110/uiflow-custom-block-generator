import argparse
import logging

from .uiflow_custom_block_generator import DEFAULT_ENCODING, UiFlowCustomBlockGenerator, get_logger

parser = argparse.ArgumentParser(
    prog='python -m uiflow_custom_block_generator', description='Generating a custom block file for UiFlow'
)
parser.add_argument(
    "config",
    nargs=1,
    type=argparse.FileType("r", encoding=DEFAULT_ENCODING),
    help="カスタムブロック定義ファイル（JSON）",
)
parser.add_argument("--target-dir", "-t", help="出力先ディレクトリ")
parser.add_argument("--debug", "-d", action="store_true", help="デバッグ表示")
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.INFO
logger = get_logger(__name__, log_level)
generator = UiFlowCustomBlockGenerator(args.config[0], target_dir=args.target_dir, logger=logger)
generator.generate()
