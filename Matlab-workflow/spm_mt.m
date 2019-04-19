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


%% SPM script of the benchmark
% to run it in cli use: `matlab -nodisplay -nosplash -nodesktop -r 'spm_mt nNodes nFiles inputBaseDir outputBaseDir nThreads'`


function [] = spm_mt(nNodes, nFiles, inputBaseDir, outputBaseDir, nThreads)
% Four arguments should be passed:
%   - nNodes: The number of datarmor nodes used in this run as a Int.
%   - nFiles: The number of SPM wav files to be processed in this run as a Int.
%   - inputBaseDir: The base directory containing the dataset as a String.
%   - outputBaseDir: The base directory where results are written as a String.
%   - nThreads: The number of threads used for precesing.
% For example, this set of parameters works as of 2018-12-17 on Datarmor:
% Array('1', '200', ''/home/datawork-alloha-ode/Datasets/SPM',
%   '/home/datawork-alloha-ode/benchmark')


tStart = tic;

%% include source files containing program's functions

addpath(genpath(strcat('.', filesep, 'signal_processing', filesep)));

%% init parameters

% sound sampling rate
sampleRate = 32768.0;
% linear scale
calibrationFactor = 0.0;
% long window, in seconds
segmentDuration = 60.0;
% short window, in samples
windowSize = 256;
% short window, in samples
nfft = 256;
% in samples
windowOverlap = 128;

lowFreqTOL = 0.2 * sampleRate;
highFreqTOL = 0.4 * sampleRate;

segmentSize = fix(sampleRate * segmentDuration);

windowFunction = hamming(windowSize, 'periodic'); % window used for windowing

runId = char(strcat(...
    'SPM', string(nFiles), 'files_', string(segmentSize), '_', string(windowSize),...
    '_', string(windowOverlap), '_', string(nfft)));

%% read wavFilesMetadata

fid = fopen(strcat(inputBaseDir, '/PAM/Metadata_SPMAuralA2010.csv'));

wavFilesMetadata = textscan(fid,...
  '%q %q %q %q %q %q %q %q %q %q %q %q %q %q %q %q %q %q %q %q %q',...
  'delimiter',';');

fclose(fid);

%% define data location

resultsLocation = strcat(outputBaseDir, filesep, 'results', filesep, 'matlab_mt', filesep,...
    char(string(nNodes)), filesep, runId);


wavFilesLocation = strcat(inputBaseDir, '/PAM/SPMAuralA2010');

wavFiles = struct(...
    'name', string(wavFilesMetadata{1}),...
    'timestamp', string(strcat(wavFilesMetadata{10}, 'T', wavFilesMetadata{11}, 'Z'))...
);

if (exist(resultsLocation, 'dir') == 0)
    mkdir(resultsLocation);
end

threadPool = parpool(str2num(nThreads));

%% Compute & Write results

parfor iFile = 1 : str2num(nFiles)
  disp(strcat('start computing: ', wavFiles.name(iFile)))
  startDateInMatlabTime = datenum(...
      char(wavFiles.timestamp(iFile)),...
      'yyyy/mm/ddTHH:MM:SSZ');

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


  disp(strcat('Computed over now write: ', wavFiles.name(iFile)))

  fd = fopen(resultFile, 'w');

  for iRes = 1 : length(results)
      fprintf(fd, jsonencode(results(iRes)));
      fprintf(fd, '\n');
  end

  fclose(fd);
  disp(strcat('Finished with: ', wavFiles.name(iFile)))
end

delete(threadPool)

%% Compute elapsed time

tEnd = toc(tStart);

fprintf('Elapsed Time: %d\n', tEnd);
fprintf('End of computations\n')

end
