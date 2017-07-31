#!env python
# -*- coding: utf-8 -*-
# > ipython csv2spc.py output.txt /Users/okada/Project/gatal_large_files/tidigits_flac/data/adults/test/man/ar/3268a.flac

##import
import sys
import change_filename
import struct
import numpy
import spc

argvs = sys.argv

##読み込み
infile = open(argvs[1], 'r')
first_line_bool = 1
for line in infile:
	items = line.split()
	for j in range(len(items)):
		items[j] = float(items[j])
	data_temp = numpy.array(items)
	#print data_temp
	if first_line_bool == 1:
		data = numpy.copy(data_temp)
		first_line_bool = 0
	else:
		data = numpy.vstack((data, data_temp))
	#print data
infile.close()
#data = data.T

##書き込み
#outfile = open(change_filename.change_extname(argvs[1], 'spc'),'wb')
#
#for i in range(len(data)):
#	for j in range(len(data[0])):
#		bdata = struct.pack('1f', 0.0)
#		outfile_spc.write(bdata)
#		bdata = struct.pack('1f', data[i,j])
#		outfile_spc.write(bdata)

spc.savefile(change_filename.change_extname(argvs[1], 'spc'), 0, 1, 1, numpy.zeros(len(data)), data, change_filename.change_extname(argvs[1], 'wav'), 4, 256, argvs[2], '')
#(spcfilename, logarithm, power, inner_hair_cell, channels, data, wavfilename, byte_width, quantizing_number, original_wavefile_path, comment)



