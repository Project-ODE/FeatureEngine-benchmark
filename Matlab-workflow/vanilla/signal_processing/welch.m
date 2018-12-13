function welch = welch(signal, fs, windowSize, windowOverlap, windowFunction, nfft)

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
    
    psdNormFactor = 1.0 / (fs * sum(windowFunction .^ 2));
    powerSpectralDensity = powerSpectrum * psdNormFactor;
    
    % take the average of all the periodograms
    welch = mean(powerSpectralDensity, 2);
end

