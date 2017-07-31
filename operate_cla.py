#!env python
# -*- coding: utf-8 -*-

import sys
import lib_memory
import lib_input_sequence
#import lib_split_times
import time as time_module

#==========================================================
#Main Operation
#==========================================================

def main(spc_filename, memory_filename):
	#split_times = lib_split_times.Split_times()
	#split_times.opening(0)
	print u'[0-0] --------.-------- : 時刻 (開始),'.encode('utf-8')
	time_zero = time_module.time()

	input_sequence_length, t_length = lib_input_sequence.get_lengths(spc_filename)
	print u'[0-1] %f : 時刻 (インプットベクトルのサイズ検出・時刻方面サイズ検出終了),'.encode('utf-8') % (time_module.time() - time_zero)
	time_zero = time_module.time()
	#split_times.opening(1)

	memory = lib_memory.read(memory_filename, input_sequence_length)
	print u'[0-2] %f : 時刻 (メモリ読み込みまたはメモリ新規作成終了),'.encode('utf-8') % (time_module.time() - time_zero)
	time_zero = time_module.time()
	#split_times.opening(2)

	#----------------------------------------------------------
	#Configuration for debug
	#----------------------------------------------------------

	memory.configuration_for_debug(spc_filename)

	#----------------------------------------------------------
	#Operating CLA
	#----------------------------------------------------------

	#split_times.opening(3)
	print u'[0-3] %f : 時刻 (全時刻ステップの開始),'.encode('utf-8') % (time_module.time() - time_zero)
	#print split_times
	for time in range(t_length):
		print 'Time =', time
		#split_times_step = lib_split_times.Split_times_step()
		input_sequence = lib_input_sequence.input_spc(spc_filename, time)

		#----------------------------------------------------------
		#SP
		#----------------------------------------------------------

		time_zero = time_module.time()
		memory.operate_sp(input_sequence)
		print u'    [0-*] %f : 時刻 (SP 全体),'.encode('utf-8') % (time_module.time() - time_zero)

		#----------------------------------------------------------
		#SP debug
		#----------------------------------------------------------

		memory.show_triumphant_imshow_sp(time)

		#----------------------------------------------------------
		#TP
		#----------------------------------------------------------

		time_zero = time_module.time()
		memory.operate_tp()
		print u'    [2-*] %f : 時刻 (TP 全体),'.encode('utf-8') % (time_module.time() - time_zero)

		#----------------------------------------------------------
		#TP debug
		#----------------------------------------------------------

		memory.show_triumphant_imshow_tp(time, 'active_state')
		memory.show_triumphant_imshow_tp(time, 'predictive_state')
		memory.show_triumphant_imshow_tp(time, 'learn_state')

		#del split_times_step
		#print split_times_step
	print u'[1-0] --------.-------- : 時刻 (全時刻ステップの終了),'.encode('utf-8')
	time_zero = time_module.time()
	lib_memory.save(memory)
	print u'[1-1] %f : 時刻 (メモリ書き込み終了),'.encode('utf-8') % (time_module.time() - time_zero)
	time_zero = time_module.time()
	print u'[1-2] %f : 時刻 (終了),'.encode('utf-8') % (time_module.time() - time_zero)
	return memory
def read(memory_filename):
	##Usage: memory = operate_cla.read('foo.cla')
	return lib_memory.read_an_exist_file(memory_filename)
if __name__ == '__main__':
	argvs = sys.argv
	main(argvs[1], argvs[2])