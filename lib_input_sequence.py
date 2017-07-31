#!env python
# -*- coding: utf-8 -*-

import encode_to_sdr
import change_filename
import numpy

#==========================================================
#Functions
#==========================================================

#----------------------------------------------------------
#Functions for reading SDR or SPC file.
#----------------------------------------------------------

def decode_sdrfile_to_sdr(sdrfile, time):
	time_index = 0
	for line in sdrfile:
		if time_index == time:
			return numpy.array(map(int,list(line[:-2])))
		time_index = time_index + 1
	return 1
def input_spc(spc_filename, time):
	try:
		f = open(change_filename.change_extname(spc_filename,'sdr'), 'r')
	except:
		encode_to_sdr.main(spc_filename)
		f = open(change_filename.change_extname(spc_filename,'sdr'), 'r')
	return decode_sdrfile_to_sdr(f, time)

#----------------------------------------------------------
#Functions for get the lengths (Time, Channels) of input.
#----------------------------------------------------------

def get_lengths_from_sdrfile(sdrfile):
	time_index = 0
	for line in sdrfile:
		if time_index == 0:
			input_sequence_length = len(line[:-2])
		time_index = time_index + 1
	return input_sequence_length, time_index
def get_lengths(spc_filename):
	try:
		f = open(change_filename.change_extname(spc_filename,'sdr'), 'r')
	except:
		encode_to_sdr.main(spc_filename)
		f = open(change_filename.change_extname(spc_filename,'sdr'), 'r')
	return get_lengths_from_sdrfile(f)

#==========================================================
#
#==========================================================

if __name__ == '__main__':
	print '?'
