import sys

sys.path.append("../")
from core.synthesizer.preprocess import preprocess_dataset
from core.synthesizer.preprocess import create_embeddings
from core.synthesizer.hparams import hparams
from core.utils.argutils import print_args
from pathlib import Path
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocesses audio files from datasets, encodes them as mel spectrograms "
        "and writes them to the disk. Audio files are also saved, to be used by the "
        "vocoder for training.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "datasets_root",
        type=Path,
        help="Path to the directory containing your LibriSpeech/TTS datasets.",
    )
    parser.add_argument(
        "-o",
        "--out_dir",
        type=Path,
        default=argparse.SUPPRESS,
        help="Path to the output directory that will contain the mel spectrograms, the audios and the "
        "embeds. Defaults to <datasets_root>/SV2TTS/synthesizer/",
    )
    parser.add_argument(
        "-n",
        "--n_processes",
        type=int,
        default=None,
        help="Number of processes in parallel.",
    )
    parser.add_argument(
        "-s",
        "--skip_existing",
        action="store_true",
        help="Whether to overwrite existing files with the same name. Useful if the preprocessing was "
        "interrupted.",
    )
    parser.add_argument(
        "-e",
        "--encoder_model_fpath",
        type=Path,
        default="../../saved_models/en_US/pretrained/encoder/encoder.pt",
        help="Path to your trained encoder model.",
    )
    parser.add_argument(
        "--max_embed_processes",
        type=int,
        default=4,
        help="Maximum number of parallel processes for embedding. An encoder is created for each, so "
        "you may need to lower this value on GPUs with low memory. Set it to 1 if CUDA is unhappy.",
    )
    parser.add_argument(
        "--hparams",
        type=str,
        default="",
        help="Hyperparameter overrides as a comma-separated list of name-value pairs",
    )
    parser.add_argument(
        "--no_trim",
        action="store_true",
        help="Preprocess audio without trimming silences (not recommended).",
    )
    parser.add_argument(
        "--no_alignments",
        action="store_true",
        help="Use this option when dataset does not include alignments\
        (these are used to split long audio files into sub-utterances.)",
    )
    parser.add_argument(
        "--datasets_name",
        type=str,
        default="LibriSpeech",
        help="Name of the dataset directory to process.",
    )
    parser.add_argument(
        "--subfolders",
        type=str,
        default="train-clean-100, train-clean-360",
        help="Comma-separated list of subfolders to process inside your dataset directory",
    )
    parser.add_argument(
        "--no_mels", action="store_true", help="Use this option to skip mel generation."
    )
    parser.add_argument(
        "--no_embeds",
        action="store_true",
        help="Use this option to skip embed generation.",
    )

    args = parser.parse_args()

    # Process the arguments
    if not hasattr(args, "out_dir"):
        args.out_dir = args.datasets_root.joinpath("SV2TTS", "synthesizer")

    # Create directories
    assert args.datasets_root.exists()
    args.out_dir.mkdir(exist_ok=True, parents=True)

    # Verify webrtcvad is available
    if not args.no_trim:
        try:
            import webrtcvad
        except:
            raise ModuleNotFoundError(
                "Package 'webrtcvad' not found. This package enables "
                "noise removal and is recommended. Please install and try again. If installation fails, "
                "use --no_trim to disable this error message."
            )
    del args.no_trim

    # Get preprocess options
    process_mels = False if args.no_mels else True
    process_embeds = False if args.no_embeds else True
    del args.no_mels
    del args.no_embeds

    # Build args for embedding
    args_embeds = argparse.Namespace(
        encoder_model_fpath=args.encoder_model_fpath,
        n_processes=args.max_embed_processes,
        synthesizer_root=args.out_dir,
        skip_existing=args.skip_existing,
    )

    # Delete args not used for mel preprocessing
    del args.encoder_model_fpath
    del args.max_embed_processes

    # Preprocess the dataset
    print_args(args, parser)
    args.hparams = hparams.parse(args.hparams)

    # Preprocess mels
    if process_mels:
        print("Preprocessing mels...")
        preprocess_dataset(**vars(args))

    # Preprocess embeds
    if process_embeds:
        print("Preprocessing embeds...")
        create_embeddings(**vars(args_embeds))
