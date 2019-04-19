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

% Main contributors: Julien Bonnel, Dorian Cazau, Paul Nguyen HD
%   Alexandre Degurse


%% Example script of the benchmark
% It run on the test data located at FeatureEngine-benchmark/test/resources
% to run it in cli use: `matlab -nodisplay -nosplash -nodesktop -r "example_mt"`
function [] = example_mt()

% clear everything, for test only.
% it also deletes any arguments passed to the script !
clc
close all
clear


tStart = tic;

%% include source files containing program's functions

addpath(genpath(strcat('.', filesep, 'signal_processing', filesep)));

%% init parameters

% sound sampling rate
sampleRate = 1500.0;
% linear scale
calibrationFactor = 0.0;
% long window, in seconds
segmentDuration = 1.0;
% short window, in samples
windowSize = 256;
% short window, in samples
nfft = 256;
% in samples
windowOverlap = 128;

lowFreqTOL = 0.2 * 1500;
highFreqTOL = 0.4 * 1500;

segmentSize = fix(sampleRate * segmentDuration);

windowFunction = hamming(windowSize, 'periodic'); % window used for windowing

runId = char(strcat(...
    'Example_', string(segmentSize), '_', string(windowSize),...
    '_', string(windowOverlap), '_', string(nfft)));

%% read wavFilesMetadata

fid = fopen('../test/resources/metadata/Example_metadata.csv');

% wavFilesMetadata are not used but this line is needed to disregard it
wavFilesMetadataHeader = textscan(fid,'%q %q', 1, 'delimiter', ',');
wavFilesMetadata = textscan(fid,'%q %q','delimiter',',');

fclose(fid);

%% define data location

resultsLocation = strcat('..', filesep, 'test', filesep,...
    'resources', filesep, 'results', filesep, 'matlab_mt', filesep,...
    '1', filesep, runId);

wavFilesLocation = strcat('..', filesep, 'test', filesep,...
    'resources', filesep, 'sounds');

wavFiles = struct(...
    'name', string(wavFilesMetadata{1}),...
    'timestamp', string(wavFilesMetadata{2})...
);

if (exist(resultsLocation, 'dir') == 0)
    mkdir(resultsLocation);
end

threadPool = parpool(2);

%% Compute & Write results

parfor iFile = 1 : length(wavFiles.name)
    startDateInMatlabTime = datenum(...
        char(wavFiles.timestamp(iFile)),...
        'yyyy-mm-ddTHH:MM:SSZ');

    startDateInUnixTimeMs = (startDateInMatlabTime - 719529) * 86400000;

    results = computeFeatures(...
        wavFilesLocation, char(wavFiles.name(iFile)), startDateInUnixTimeMs,...
        sampleRate, calibrationFactor,...
        segmentDuration, windowSize, windowOverlap, windowFunction,...
        nfft, lowFreqTOL, highFreqTOL);

    soundNameSplitted = split(string(wavFiles.name(iFile)), '_');
    soundId = char(strcat(soundNameSplitted(1), '_', string(1500),...
        '_', string(windowSize), '_', string(windowOverlap), '_',...
        string(nfft)));

    resultFile = strcat(resultsLocation, filesep,...
        soundId, '.json');

    fd = fopen(resultFile, 'w');

    for iRes = 1 : length(results)
        resultsAsString = strrep(strrep(...
            jsonencode(results(iRes)), '"[[', '[['), ']]"', ']]');
        fprintf(fd, resultsAsString);
        fprintf(fd, '\n');
    end

    fclose(fd);

end

delete(threadPool)

%% Compute elapsed time

tEnd = toc(tStart);

fprintf('Elapsed Time: %d\n', tEnd);
fprintf('End of computations\n')

end
