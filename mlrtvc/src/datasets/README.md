## Datasets

### Sample structure

Here is an example directory structure for placing datasets so they can be detected by the preprocessing scripts.
```
- datasets
    - LibriSpeech
        - train-clean-100
        - train-clean-360
        - train-other-500
    - LibriTTS
        - train-clean-100
        - train-clean-360
    - VoxCeleb1
        - wav
    - VoxCeleb2
        - dev
            - wav
```

### Output

Preprocessing creates one or more of these output folders. Training uses the SV2TTS folder corresponding to the model being trained (encoder, synthesizer, or vocoder).
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
