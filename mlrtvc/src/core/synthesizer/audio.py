# raccoonML audio tools.
# MIT License
# Copyright (c) 2021 raccoonML (https://patreon.com/raccoonML)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software") to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR ANY OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import librosa
import numpy as np
import soundfile as sf
import torch
import torchaudio
from scipy import signal

_mel_basis = None

def load_wav(path, hparams):
    # Loads an audio file and returns the waveform data.
    wav, _ = librosa.load(str(path), hparams.sample_rate)
    return wav

def save_wav(wav, path, hparams):
    # Saves waveform data to audio file.
    sf.write(path, wav, hparams.sample_rate)

def melspectrogram(wav, hparams):
    # Converts a waveform to a mel-scale spectrogram.
    # Output shape = (num_mels, frames)

    # Apply preemphasis
    if hparams.preemphasize:
        wav = _preemphasis(wav, hparams)

    # Short-time Fourier Transform (STFT)
    D = librosa.stft(y=wav,
                     n_fft=hparams.n_fft,
                     hop_length=hparams.hop_size,
                     win_length=hparams.win_size)

    # Convert complex-valued output of STFT to absolute value (real)
    S = np.abs(D)

    # Build and cache mel basis
    # This improves speed when calculating thousands of mel spectrograms.
    global _mel_basis
    if _mel_basis is None:
        _mel_basis = _build_mel_basis(hparams)

    # Transform to mel scale
    S = np.dot(_mel_basis, S)

    # Convert amplitude to dB
    min_level = np.exp((hparams.min_level_db + hparams.ref_level_db)/ 20 * np.log(10))
    S = 20 * np.log10(np.maximum(min_level, S)) - hparams.ref_level_db

    # Normalize
    if hparams.signal_normalization:
        S = (S - hparams.min_level_db) / (-hparams.min_level_db)
        if hparams.symmetric_mels:
            S = 2 * hparams.max_abs_value * S - hparams.max_abs_value
            min_value = -hparams.max_abs_value
            max_value = hparams.max_abs_value
        else:
            S = hparams.max_abs_value * S
            min_value = 0
            max_value = hparams.max_abs_value

        if hparams.allow_clipping_in_normalization:
            S = np.clip(S, min_value, max_value)

    return S

def inv_mel_spectrogram(S, hparams):
    # Converts a mel spectrogram to waveform using Griffin-Lim
    # Input shape = (num_mels, frames)
    
    # Denormalize
    if hparams.signal_normalization:
        # Clip spectrogram to limits
        if hparams.allow_clipping_in_normalization:
            if hparams.symmetric_mels:
                S = np.clip(S, -hparams.max_abs_value, hparams.max_abs_value)
            else:
                S = np.clip(S, 0, hparams.max_abs_value)

        # Undo normalization
        if hparams.symmetric_mels:
            S = ((S + hparams.max_abs_value) * -hparams.min_level_db / (2 * hparams.max_abs_value)) + hparams.min_level_db
        else:
            S = (S * -hparams.min_level_db / hparams.max_abs_value) + hparams.min_level_db

    # Convert amplitude from dB to absolute value
    S = S + hparams.ref_level_db
    S = np.power(10.0, 0.05 * S)

    # Build and cache mel basis
    # This improves speed when calculating thousands of mel spectrograms.
    global _mel_basis
    if _mel_basis is None:
        _mel_basis = _build_mel_basis(hparams)

    # Inverse mel basis
    p = np.matmul(_mel_basis, _mel_basis.T)
    d = [1.0 / x if np.abs(x) > 1.0e-8 else x for x in np.sum(p, axis=0)]
    _inv_mel_basis = np.matmul(_mel_basis.T, np.diag(d))

    # Invert mel basis to recover linear spectrogram
    S = np.dot(_inv_mel_basis, S)

    # Use Griffin-Lim to recover waveform
    wav = _griffin_lim(S ** hparams.power, hparams)

    # Invert preemphasis
    if hparams.preemphasize:
        wav = _inv_preemphasis(wav, hparams)

    return wav

def _preemphasis(wav, hparams):
    # Amplifies high frequency content in a waveform.
    wav = signal.lfilter([1, -hparams.preemphasis], [1], wav)
    return wav

def _inv_preemphasis(wav, hparams):
    # Inverts the preemphasis filter.
    wav = signal.lfilter([1], [1, -hparams.preemphasis], wav)
    return wav

def _build_mel_basis(hparams):
    return librosa.filters.mel(hparams.sample_rate, hparams.n_fft, n_mels=hparams.num_mels,
                               fmin=hparams.fmin, fmax=hparams.fmax)

def _griffin_lim(S, hparams):
    if True:
        # Torchaudio result is same, but much faster
        device = torch.device("cpu")
        S_tensor = torch.tensor(S, dtype=torch.float32).to(device)
        window_tensor = torch.tensor(signal.windows.hann(hparams.win_size, sym=True), dtype=torch.float32).to(device)
        wav_tensor = torchaudio.functional.griffinlim(S_tensor, window_tensor, hparams.n_fft, hparams.hop_size,
                                                      hparams.win_size, 1.0, hparams.griffin_lim_iters, 0.0, None, False)
        wav = wav_tensor.cpu().numpy()
    else:
        # Another Griffin-Lim implementation
        angles = np.exp(2j * np.pi * np.random.rand(*S.shape))
        S = np.abs(S).astype(np.complex)
        wav = librosa.istft(S * angles, hop_length=hparams.hop_size, win_length=hparams.win_size)
        for i in range(hparams.griffin_lim_iters):
            angles = np.exp(1j * np.angle(librosa.stft(wav, n_fft=hparams.n_fft, hop_length=hparams.hop_size, win_length=hparams.win_size)))
            wav = librosa.istft(S * angles, hop_length=hparams.hop_size, win_length=hparams.win_size)

    return wav
