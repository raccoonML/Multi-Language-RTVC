## Preprocessing

### Datasets

For datasets to be detected by the preprocessing scripts, they must be arranged in a specific directory structure. See the [datasets readme](../datasets/README.md) for details.

### Folder structure

Preprocessing creates one or more of these output folders in your datasets directory. Training only requires the SV2TTS folder corresponding to the model being trained (encoder, synthesizer, or vocoder).
```
- datasets
    - SV2TTS
        - encoder
        - synthesizer
            - audio
            - mels
            - embeds
            - train.txt
        - vocoder
            - mels_gta
            - train.txt
```

### Encoder

To preprocess the encoder, point it to your datasets directory. Dataset support is provided for LibriSpeech train-clean-500, VoxCeleb1 and VoxCeleb2. Adapt the code to support other datasets.

```
python encoder_preprocess.py ../datasets
```


### Synthesizer

The synthesizer requires speaker embeddings and mel targets for training. Preprocessing occurs in this order.

1. Mel spectrograms are computed after processing audio to match selected sample rate and remove silence.
2. Speaker embeddings are produced from encoder inference. The encoder takes a mel spectrogram as input; however the synthesizer mels are not compatible which requires a separate audio preprocess and spectrogram calculation.

Supported datasets are LibriSpeech and LibriTTS. Folders other than `train-clean-100` and `train-clean-360` can be used by specifying a `--subfolders` argument. It is possible to preprocess a different dataset without modifying code, if the new dataset is rearranged to resemble the folder structure of LibriTTS.

#### LibriSpeech preprocessing

```
python synthesizer_preprocess.py ../datasets
```

#### LibriTTS preprocessing

```
python synthesizer_preprocess.py ../datasets --datasets_name LibriTTS --no_alignments
```


### Vocoder

Vocoder training requires the audio preprocessing and mel spectrogram generation for the synthesizer, described above. The preprocessing step here is **completely optional** as there is a command-line flag to train on the ground truth mels in `datasets/SV2TTS/synthesizer/mels`.

This step creates "ground-truth-aligned" mel spectrograms (GTA mels) using the synthesizer model. In some cases, training a vocoder on GTA mels results in a higher quality output in the end-to-end SV2TTS, where the synthesizer outputs are passed to the vocoder.

The vocoder preprocess has no dataset dependence as the preprocessed synthesizer data it uses has a standard format. 

```
python vocoder_preprocess.py ../datasets
```
