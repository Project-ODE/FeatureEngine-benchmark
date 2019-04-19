% Copyright (C) 2017-2018 Project-ODE
%
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <http://www.gnu.org/licenses/>.

% Main contributors: Julien Bonnel, Dorian Cazau, Paul Nguyen HD,
%   Alexandre Degurse


function tol = tol(signal, sampleRate, windowFunction, lowFreqTOL, highFreqTOL)
    if (length(signal) < sampleRate)
        MException('tol:input', ['Signal incompatible with TOL computation, '...
        'it should be longer than a second.'])
    end

    if (length(windowFunction) ~= sampleRate)
        MException('tol:input', ['Incorrect windowFunction for TOL, '...
        'it should be of size sampleRate.'])
    end

    if (lowFreqTOL < 1.0)
        MException('tol:input', ['Incorrect lowFreq for TOL, '...
        'it should be higher than 1.0.'])
    end

    if (highFreqTOL > sampleRate/2)
        MException('tol:input', ['Incorrect highFreq for TOL, '...
        'it should be lower than sampleRate/2.'])
    end

    if (lowFreqTOL > highFreqTOL)
        MException('tol:input', ['Incorrect lowFreq,highFreq for TOL, '...
        'lowFreq is higher than highFreq.'])
    end

    windowSize = sampleRate;
    nfft = sampleRate;
    windowOverlap = 0;

    segmentedSignal = segmentation(signal, windowSize, windowOverlap);

    windowedSignal = bsxfun(@times, segmentedSignal, windowFunction);

    if (mod(nfft, 2) == 0)
        spectrumSize = nfft/2 + 1;
    else
        spectrumSize = nfft/2;
    end

    twoSidedSpectrum = fft(windowedSignal);

    % [ if a frequency-dependent correction is being applied to the signal,
    %   e.g. frequency-dependent hydrophone sensitivity, it should be applied
    %   here to each frequency bin of the DFT ]

    % ignore the DC and Nyquist value
    oneSidedSpectrum = twoSidedSpectrum(1 : spectrumSize, :);

    % ignore the DC and Nyquist value
    powerSpectrum = abs(oneSidedSpectrum) .^ 2;
    powerSpectrum(2 : spectrumSize-1, :) = powerSpectrum(2 : spectrumSize-1, :) .* 2;

    normalizedPowerSpectrum = powerSpectrum ./ (sampleRate * sum(windowFunction .^ 2));

    tobCenters = 10 .^ ((0:59) / 10);

    tobBounds = zeros(2, 60);
    tobBounds(1, :) = tobCenters * 10 ^ -0.05;
    tobBounds(2, :) = tobCenters * 10 ^ 0.05;


    inRangeIndices = find((tobBounds(2, :) < sampleRate / 2)...
        & (lowFreqTOL <= tobBounds(2, :))...
        & (tobBounds(1, :) < highFreqTOL));

    tobBoundsInPsdIndex = zeros(2, length(inRangeIndices));
    tobBoundsInPsdIndex(1, :) = fix(tobBounds(1, inRangeIndices(1):inRangeIndices(end)) * (nfft / sampleRate));
    tobBoundsInPsdIndex(2, :) = fix(tobBounds(2, inRangeIndices(1):inRangeIndices(end)) * (nfft / sampleRate));

    tol = zeros(1, length(inRangeIndices));

    for i = 1 : length(inRangeIndices)
        tol(i) = sum(sum(...
            normalizedPowerSpectrum(1+tobBoundsInPsdIndex(1, i) : tobBoundsInPsdIndex(2, i), :)...
        , 1));
    end

    tol = 10 * log10(tol);
end
