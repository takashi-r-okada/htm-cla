#!/bin/tcsh

#==========================================================
#Main Processes
#==========================================================

set array = (`find ~/{input the directory_for_data here}/106_htm/cla_branch_for_tidigits_cognition/corpus/tidigits_flac/data/adults/train/woman/ -name "2?.spc"` | wc --line)
echo $array

echo CLA machine is learning $%array spc files ......
foreach i ($array)
	ipython operate_cla.py $i ../memory/20150825_12.cla
end
