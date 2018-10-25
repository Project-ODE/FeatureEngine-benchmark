# Benchmark resources organization

## Overview

This folder contains the ODE-FeatureEngine signal processing standardization tests reference values.
Sub-folders are as follow:

+ `sounds` contains the wav files
+ `matlab`
  + `values` - contains matlab generated values by benchmark scripts on sounds.
+ `python`
  + `values` - contains python generated values by benchmark scripts on sounds.

## Files conventions

### Sounds

Wav Files in the `sounds` folder should be encoded as `PCM Little-Endian` and named as follow:

```bash
SOUNDID_SYSBITS_WAVBITS_SAMPLENUMBER_SAMPRATE_CHANSNUMBER.wav
```

With:

+ `FILEID` - The sound identifier, unique among sounds
+ `SYSBITS` - The bytes number the file-writing system used (generally `64`, but could be `32`)
+ `WAVBITS` - The number of bits used for sound encoding (`8`, `16` or `24` generally)
+ `SAMPLENUMBER` - The number of samples in the sound file
+ `SAMPRATE` - The sampling rate the sound is using in Hz (usual values are `3900.0` `16000`, `44100`, `96000.0`...)
+ `CHANSNUNMBER` - The number of channels the file contains (`1` for mono, `2` for stereo etc)

