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


function welch = welch(signal, sampleRate, windowSize, windowOverlap, windowFunction, nfft)

    segmentedSignal = segmentation(signal, windowSize, windowOverlap);

    % multiply segments by window function
    windowedSignal = bsxfun(@times, segmentedSignal, windowFunction);

    if (mod(nfft, 2) == 0)
        spectrumSize = nfft/2 + 1;
    else
        spectrumSize = nfft/2;
    end

    twoSidedSpectrum = fft(windowedSignal, nfft);

    % [ if a frequency-dependent correction is being applied to the signal,
    %   e.g. frequency-dependent hydrophone sensitivity, it should be applied
    %   here to each frequency bin of the DFT ]

    % ignore the DC and Nyquist value
    oneSidedSpectrum = twoSidedSpectrum(1 : spectrumSize, :);

    % ignore the DC and Nyquist value
    powerSpectrum = abs(oneSidedSpectrum) .^ 2;
    powerSpectrum(2 : spectrumSize-1, :) = powerSpectrum(2 : spectrumSize-1, :) .* 2;

    psdNormFactor = 1.0 / (sampleRate * sum(windowFunction .^ 2));
    powerSpectralDensity = powerSpectrum * psdNormFactor;

    % take the average of all the periodograms
    welch = mean(powerSpectralDensity, 2);
end
