#!/bin/tcsh

#==========================================================
#Initial Settings
#==========================================================

set sps = 8000 #sampling rate of making wav files

#==========================================================
#Main Processes
#==========================================================

set array = (`find ~/Project/gatal_large_files/tidigits_flac/data/adults/train -name "??.flac"` | wc --line)
echo $%array flac files are processing......
foreach i ($array)
	ffmpeg -y -i $i -ac 1 -ar 8000 $i:r:t.wav >& temp.log
	if ($status) then
		echo $i, Error.
	else
		cp $i:r:t.wav output.wav
		matlab -nodisplay -r implement_erb >! matlab.log
		#matlab -r implement_erb >! matlab.log # for debug
		ipython csv2spc.py output.txt $i
		mv output.spc $i:r.spc
		echo $i, Succeeded.
	endif
	rm $i:r:t.wav
end
