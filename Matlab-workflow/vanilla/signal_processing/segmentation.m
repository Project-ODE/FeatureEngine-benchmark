function segmentedSignal = segmentation(signal, windowSize, windowOverlap)
    nPredictedWindows = fix((length(signal) - windowOverlap) / (windowSize - windowOverlap));

    % grid whose rows are each (overlapped) segment for analysis
    segmentedSignalWithPartial = buffer(signal, windowSize, windowOverlap, 'nodelay');

    segmentedSignalWithPartialShape = size(segmentedSignalWithPartial);

    % remove final segment if not full
    if segmentedSignalWithPartialShape(2) ~= nPredictedWindows
        segmentedSignal = segmentedSignalWithPartial(:, 1:nPredictedWindows);
    else
        segmentedSignal = segmentedSignalWithPartial;
    end
end

