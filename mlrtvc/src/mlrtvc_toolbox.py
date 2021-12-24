from pathlib import Path
from core.toolbox import Toolbox
from core.utils.argutils import print_args
from core.utils.modelutils import check_model_paths
import argparse
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs the toolbox",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-d",
        "--datasets_root",
        type=Path,
        help="Path to the directory containing your datasets. See toolbox/__init__.py for a list of "
        "supported datasets.",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--saved_models_dir",
        type=Path,
        default="../saved_models",
        help="Directory containing saved models",
    )
    parser.add_argument(
        "-l",
        "--language_code",
        type=str,
        default="en_US",
        help="Language to use for speech generation",
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="If True, processing is done on CPU, even when a GPU is available.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random number seed value to make toolbox deterministic.",
    )
    args = parser.parse_args()
    print_args(args, parser)

    if args.cpu:
        # Hide GPUs from Pytorch to force CPU processing
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    del args.cpu

    # Launch the toolbox
    Toolbox(**vars(args))
