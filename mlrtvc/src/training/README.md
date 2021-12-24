## Training

### Preprocessing
Before training can be started, [preprocessing](../pre_processing/README.md) for the corresponding model (encoder, synthesizer, vocoder) must be completed.

### Folder structure

Training creates this output folder structure to hold the saved models and other training outputs. The language code (default="en_US") and run_id "MODEL_NAME" are taken from the command-line arguments passed to the training script.
```
- saved_models
    - en_US
        - MODEL_NAME
            - encoder
            - synthesizer
            - vocoder
```

### General considerations
The amount of VRAM consumed depends on the number of model parameters, the filesize of the audio/mel inputs, and batch size used for training. If out-of-memory errors are experienced, they can usually be resolved by changing settings in hparams.

### Training commands

To train a model, you will need to your model a name, and supply the path to the preprocessed data. Specify the language code with the `-l` or `--language_code` argument.

#### Encoder

```
python encoder_train.py --language_code en_US MODEL_NAME ../datasets/SV2TTS/encoder
```

#### Synthesizer

```
python synthesizer_train.py --language_code en_US MODEL_NAME ../datasets/SV2TTS/synthesizer
```

#### Vocoder (trains on ground truth mels in SV2TTS/synthesizer/mels)

It is recommended to train on ground truth mels as a starting point, and explore training with GTA mels if quality does not meet expectations.
```
python vocoder_train.py -g --language_code en_US MODEL_NAME ../datasets
```

#### Vocoder (trains on [GTA mels](../pre_processing/README.md#vocoder) in SV2TTS/vocoder/mels_GTA)

```
python vocoder_train.py --language_code en_US MODEL_NAME ../datasets
```
