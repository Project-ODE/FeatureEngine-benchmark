function tol = tol(signal, fs, windowFunction, lowFreqTOL, highFreqTOL)
    if (length(signal) < fs)
        MException('tol:input', ['Signal incompatible with TOL computation, '...
        'it should be longer than a second.'])
    end

    if (length(windowFunction) ~= fs)
        MException('tol:input', ['Incorrect windowFunction for TOL, '...
        'it should be of size fs.'])
    end
    
    if (lowFreqTOL < 1.0)
        MException('tol:input', ['Incorrect lowFreq for TOL, '...
        'it should be higher than 1.0.'])
    end

    if (highFreqTOL > fs/2)
        MException('tol:input', ['Incorrect highFreq for TOL, '...
        'it should be lower than fs/2.'])
    end
    
    if (lowFreqTOL > highFreqTOL)
        MException('tol:input', ['Incorrect lowFreq,highFreq for TOL, '...
        'lowFreq is higher than highFreq.'])
    end
    
    windowSize = fs;
    nfft = fs;
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
    
    normalizedPowerSpectrum = powerSpectrum ./ (fs * sum(windowFunction .^ 2));
    
    tobCenters = 10 .^ ((0:59) / 10);
    
    tobBounds = zeros(2, 60);
    tobBounds(1, :) = tobCenters * 10 ^ -0.05;
    tobBounds(2, :) = tobCenters * 10 ^ 0.05;
    
    
    inRangeIndices = find((tobBounds(2, :) < fs / 2)...
        & (lowFreqTOL <= tobBounds(2, :))...
        & (tobBounds(1, :) < highFreqTOL));
    
    tobBoundsInPsdIndex = zeros(2, length(inRangeIndices));
    tobBoundsInPsdIndex(1, :) = fix(tobBounds(1, inRangeIndices(1):inRangeIndices(end)) * (nfft / fs));
    tobBoundsInPsdIndex(2, :) = fix(tobBounds(2, inRangeIndices(1):inRangeIndices(end)) * (nfft / fs));
        
    tol = zeros(1, length(inRangeIndices));
    
    for i = 1 : length(inRangeIndices)
        tol(i) = sum(sum(...
            normalizedPowerSpectrum(1+tobBoundsInPsdIndex(1, i) : tobBoundsInPsdIndex(2, i), :)...
        , 1));
    end
    
    tol = 10 * log10(tol);
end

