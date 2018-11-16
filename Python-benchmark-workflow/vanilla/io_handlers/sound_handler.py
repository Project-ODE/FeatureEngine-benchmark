#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2018 Project-ODE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Authors: Dorian Cazau, Alexandre Degurse

"""
Module providing SoundHandler class for sound file reading
"""

import os
import soundfile


class SoundHandler:
    """
    Class handling the reading of sound files
    """
    def __init__(
            self,
            file_name,
            wav_file_location,
            wav_bits,
            n_samples,
            sample_rate,
            n_channels
    ):

        self.wav_file_location = wav_file_location
        self.file_name = file_name
        self.wav_bits = wav_bits
        self.n_samples = n_samples
        self.sample_rate = sample_rate
        self.n_channels = n_channels

    def read(self):
        """
        Method reading the sound file specified by the class arguments.
        :return: A tuple containing the content of the soundfile as a
            numpy.array and the sounds' sample rate.
        """
        sound_file = soundfile.SoundFile(os.path.join(
            self.wav_file_location, self.file_name
        ))

        assert sound_file.samplerate == self.sample_rate
        assert sound_file.channels == self.n_channels
        assert sound_file.format == "WAV"
        assert sound_file.frames == self.n_samples
        assert sound_file.subtype == "PCM_{}".format(self.wav_bits)

        sig = sound_file.read()
        sample_rate = sound_file.samplerate

        return sig, sample_rate
