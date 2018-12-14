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

%% Taken from MathWorks to reduce run time and PAMGuide from Merchant et al. 2015
function results = spectralComputation(...
    signal, fs, windowSize, windowOverlap, windowFunction, nfft,...
    lowFreq, highFreq)

    tolWindowFunction = hamming(fs, 'periodic');

    vWelch = welch(signal, fs, windowSize, windowOverlap, windowFunction, nfft);
    
    vTol = tol(signal, fs, tolWindowFunction, lowFreq, highFreq);
    
    spl = 10 * log10(sum(vWelch));

    results = struct(...
        'welch', vWelch,...
        'spl', spl,...
        'tol', vTol...
     );
end
