#!env python
# -*- coding: utf-8 -*-

import spc
import numpy
import struct
import sys
import change_filename

def main(spc_filename):
	##Parameters
	sparse_factor = 0.02

	##Initial Reading
	spc_o = spc.readfile(spc_filename)

	##### n-w+1 = quantizing_number && w/n \simeq sparse_factor を満たすように n, w を決める
	##### 以下は n, w について解いたもの．
	n_per_value = int(round(float(spc_o.quantizing_number - 1) / (1.0 - sparse_factor)))
	w_per_value = int(round(float(spc_o.quantizing_number - 1) / (1.0 - sparse_factor) * sparse_factor))
	#print w_per_value
	n_per_region = n_per_value * spc_o.c_length()
	w_per_region = w_per_value * spc_o.c_length()

	##箱の定義

	#print spc_o.t_length
	sdr = numpy.zeros((spc_o.t_length(), n_per_region), dtype=numpy.uint8)

	for t in range(spc_o.t_length()):
		for c in range(spc_o.c_length()):
			sdr[t, c * n_per_value + int(spc_o.data[c,t]) : c * n_per_value + int(spc_o.data[c,t]) + w_per_value] = [1,] * w_per_value

	##完成!
	#sdr = sdr.T #for_debug

	##出力
	#outfile = open('temp_sdr.txt','w')
	outfile = open(change_filename.change_extname(spc_filename,'sdr'), 'w')
	for i in range(len(sdr)): #t
		#outfile.write('#t\t' + str(i) + '\r\n')
		for j in range(len(sdr[0])): #channel
			#if j % n_per_value == 0:
			#	outfile.write('#t\t' + str(i) + '\t#c\t' + str(j/n_per_value) + '\r\n')
			outfile.write(str(sdr[i,j]))
			if j != len(sdr[0]) - 1:
			#if j + 1 % n_per_value != 0:
				#outfile.write('\t')
			#	outfile.write('')
				pass
			else:
				outfile.write('\r\n')
	outfile.close()

if __name__ == '__main__':
	main(sys.argv[1])
