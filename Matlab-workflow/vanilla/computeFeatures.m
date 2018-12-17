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

function results = computeFeatures(...
    wavFileLocation, wavFileName, startDateInUnixTimeMs, sampleRate,...
    calibrationFactor, segmentDuration, windowSize,...
    windowOverlap, windowFunction, nfft, lowFreq, highFreq)

    wavInfo = audioinfo(strcat(wavFileLocation, wavFileName));

    % @TODO perform checks against expected infos

    rawSound = audioread(strcat(wavFileLocation, wavFileName), 'double');

    calibratedSignal = rawSound * (10 ^ (calibrationFactor / 20));

    segmentSize = fix(segmentDuration * sampleRate);

    nSegments = fix(wavInfo.TotalSamples / segmentSize);

    results = {};

    % going backwards to have the right struct size allocation of results
    for iSegment = nSegments-1 : -1 : 0
        spectralResults = spectralComputation(...
            calibratedSignal(1 + iSegment*segmentSize : (iSegment+1) * segmentSize),...
            sampleRate, windowSize, windowOverlap, windowFunction, nfft,...
            lowFreq, highFreq);

        segmenTsInUnixMs = startDateInUnixTimeMs + 1000.0 * iSegment * (segmentSize / sampleRate);
        segmentTsInMatlabTime = segmenTsInUnixMs / 86400000 + 719529;
        segmentTimestamp = datestr(segmentTsInMatlabTime, 'yyyy-mm-ddTHH:MM:SS.FFFZ');

        format long

        % Convert results to json string to enforce json structure
        results(1 + iSegment).timestamp = strcat(segmentTimestamp);

        results(1 + iSegment).welch = strcat(...
            '[', jsonencode(spectralResults.welch), ']'...
        );
        results(1 + iSegment).spl = strcat(...
            '[[', jsonencode(spectralResults.spl), ']]'...
        );

        results(1 + iSegment).tol = strcat(...
            '[', jsonencode(spectralResults.tol), ']'...
        );
    end
end
