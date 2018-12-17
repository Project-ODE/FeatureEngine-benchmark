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
