#!env python
# -*- coding: utf-8 -*-

import sys
import lib_parameters
import numpy
import cPickle as pickle
import grapher
import math
import os
import time as time_module
#import lib_animation

from lib_column import *

#共通文法として，現在 = -1，1 ステップ前 = -2 という添字で表す．(悪く思わないでくれ，0 - origin なんだ)

#==========================================================
#Classes (Synapse, Cell, Column, Region, Memory)
#==========================================================

class Memory(object):

	#----------------------------------------------------------
	#Methods for Overlap of SP
	#----------------------------------------------------------

	#----------------------------------------------------------
	#Methods for Inhibition of SP
	#----------------------------------------------------------
	
	def calculate_neighbors(self, c0): # 中心のカラムの index を受け取る
		self.columns[c0].neighbors = []
		for c in range(self.shared_parameters.columns_per_region):
			if c >= c0 - self.inhibition_radius and c <= c0 + self.inhibition_radius and c >= 0 and c <= self.shared_parameters.columns_per_region - 1:
				self.columns[c0].neighbors.append(c)
	def update_kth_score(self, c0):
		neighbors_overlapped = []
		for c in self.columns[c0].neighbors:
			if self.columns[c].overlap > self.sp_parameters.min_overlap:
				neighbors_overlapped.append(self.columns[c].overlap)
		neighbors_overlapped = sorted(neighbors_overlapped, reverse = True)
		#print neighbors_overlapped
		if len(neighbors_overlapped) == 0:
			self.columns[c0].kth_score = self.shared_parameters.columns_per_region
			#print 'no neighbors_overlapped'
		elif len(neighbors_overlapped) < self.sp_parameters.desired_local_activity:
			self.columns[c0].kth_score = neighbors_overlapped[-1]
		else:
			self.columns[c0].kth_score = neighbors_overlapped[self.sp_parameters.desired_local_activity - 1]

	#----------------------------------------------------------
	#Methods for Learning of SP
	#----------------------------------------------------------
	
	def update_min_duty_cycle(self, c0):
		max_active_duty_cycle = 0.0
		for c in self.columns[c0].neighbors:
			if self.columns[c].active_duty_cycle > max_active_duty_cycle:
				max_active_duty_cycle = self.columns[c].active_duty_cycle
		self.columns[c0].min_duty_cycle = 0.01 * max_active_duty_cycle
	def update_overlap_duty_cycle(self, c):
		if self.columns[c].overlap > self.sp_parameters.min_overlap:
			self.overlap_with_history[-1].append(c)
		self.columns[c].update_overlap_duty_cycle(c, self.overlap_with_history)
	def average_receptive_field_size(self):
		average_receptive_field_size = 0.0
		columns_number_with_connected_synapses = 0
		for c in range(self.shared_parameters.columns_per_region):
			average_receptive_field_size = average_receptive_field_size + self.columns[c].average_receptive_field_size(c)
			if self.columns[c].average_receptive_field_size(c) != 0:
				columns_number_with_connected_synapses = columns_number_with_connected_synapses + 1
		return average_receptive_field_size / float(columns_number_with_connected_synapses)

	#----------------------------------------------------------
	#Methods to Operate whole CLA
	#----------------------------------------------------------
	
	def operate_sp(self, input_sequence):

		#split_times_step(0)
		print u'    [0-0] --------.--------- : 時刻 (SP 開始),'
		time_zero = time_module.time()

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Overlap of SP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		for c in range(self.shared_parameters.columns_per_region):
			self.columns[c].update_overlap(c, input_sequence, self.inhibition_radius) #その time_step の input_sequence 全体を渡すようにしている．
		#split_times_step(1)
		print u'    [0-1] %f : 時刻 (SP.Overlap 終了),' % (time_module.time() - time_zero)
		time_zero = time_module.time()

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Inhibition of SP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		self.active_columns_with_history.append([])
		if len(self.active_columns_with_history) > self.sp_parameters.length_history_kept:
			self.active_columns_with_history = self.active_columns_with_history[-self.sp_parameters.length_history_kept:]
		#print self.inhibition_radius, u'抑制半径'
		for c in range(self.shared_parameters.columns_per_region):
			self.calculate_neighbors(c)
			self.update_kth_score(c)
			self.columns[c].min_local_activity = self.columns[c].kth_score # わざわざ min_local_activity に代入しなくても直接 kth_score 使っていいかも．
			#print min_local_activity
			if self.columns[c].overlap > 0 and self.columns[c].overlap >= self.columns[c].min_local_activity:
				self.active_columns_with_history[-1].append(c)
		#split_times_step(2)
		print u'    [0-2] %f : 時刻 (SP.Inhibition 終了),' % (time_module.time() - time_zero)
		time_zero = time_module.time()

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Learning of SP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		for c in self.active_columns_with_history[-1]:
			self.columns[c].sp_learn()
		self.overlap_with_history.append([])
		if len(self.overlap_with_history) > self.sp_parameters.length_history_kept:
			self.overlap_with_history = self.overlap_with_history[-self.sp_parameters.length_history_kept:]
		for c in range(self.shared_parameters.columns_per_region):
			self.update_min_duty_cycle(c)
			self.columns[c].update_active_duty_cycle(c, self.active_columns_with_history)
			self.columns[c].update_boost()
			self.update_overlap_duty_cycle(c)
			self.columns[c].boost_permanence()
		self.inhibition_radius = self.average_receptive_field_size()
		#split_times_step(3)
		print u'    [0-3] %f : 時刻 (SP.Learning 終了 (= SP 終了)),' % (time_module.time() - time_zero)

	def operate_tp(self):

		print u'    [2-0] --------.-------- : 時刻 (TP 開始),'
		time_zero = time_module.time()

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Appending a new time step for TP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		#print '\tTP.Ph 1'
		for c in range(len(self.columns)):
			self.columns[c].append_time_step()
		print u'    [2-1] %f : 時刻 (新時刻ステップ追加終了),' % (time_module.time() - time_zero)
		time_zero = time_module.time()

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Phase 1st of TP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		for c in self.active_columns_with_history[-1]:
			#print '\t\tColumn =', c
			self.columns[c].calculate_active_state(self.columns)
		print u'    [2-2] %f : 時刻 (TP.Phase1 終了),' % (time_module.time() - time_zero)
		time_zero = time_module.time()
		
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Phase 2nd of TP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		#print '\tTP.Ph 2'
		for c in range(len(self.columns)):
			#print '\t\tColumn =', c
			self.columns[c].calculate_predictive_state(self.columns)
		print u'    [2-3] %f : 時刻 (TP.Phase2 終了),' % (time_module.time() - time_zero)
		time_zero = time_module.time()

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Phase 3rd of TP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		#print '\tTP.Ph 3'
		for c in range(len(self.columns)):
			self.columns[c].tp_learn()
		print u'    [2-4] %f : 時刻 (TP.Phase3 終了 (= TP 終了)),' % (time_module.time() - time_zero)
		time_zero = time_module.time()

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Other Functions of TP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

	#----------------------------------------------------------
	#Methods of Constructor
	#----------------------------------------------------------
	
	def __init__(self, filename, input_sequence_length): #メモリの新規作成
		print 'New memory has been created.'
		self.filename = filename
		#self.create_global_parameters()
		lib_parameters.create_parameters(self)

		self.columns = [0,] * self.shared_parameters.columns_per_region
		for c in range(self.shared_parameters.columns_per_region):
			self.columns[c] = Column(c, input_sequence_length)
		self.inhibition_radius = self.sp_parameters.initial_inhibition_radius
		self.active_columns_with_history = [[]]
		self.overlap_with_history = [[]] #その時間ステップにおいて min_overlap 値を越えたカラムのインデックスのリスト．それを多時間ステップ分記憶したもの
		self.learning_files_count = 0

	#----------------------------------------------------------
	#Methods for debug
	#----------------------------------------------------------

	def configuration_for_debug(self, input_filename):
		self.baserootname = os.path.splitext(os.path.basename(self.filename))[0]
		self.input_filename = os.path.splitext(input_filename)[0].replace('/', '-')

		print ' '
		print '###############################################################'
		print '##  '
		print '##  Properties for Debug'
		print '##  '
		print '##  The CLA Memory Name is "%s".' % self.baserootname
		print '##  This Memory has learned %d input data by far.' % self.learning_files_count
		print '##  Present Learning Operation is for %s.' % self.input_filename
		print '##  '
		print '###############################################################'
		print ' '

		self.dir_for_debug = os.environ['CLA_REPO'] + '/debug/' + self.baserootname + '/' + str(self.learning_files_count) + '_' + self.input_filename + '/'
		os.makedirs(self.dir_for_debug)
		os.makedirs(self.dir_for_debug + 'imshow')

	def show_overlapped(self):
		for c in range(self.shared_parameters.columns_per_region):
			if self.columns[c].overlap > 1:
				print u'■',
			else:
				print u' ',
			if c % 32 == 0:
				print '\r\n'
		print '\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n'
	def show_triumphant(self):
		print self.active_columns_with_history[-1]

	#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	#Methods for SP debug
	#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

	##メソッド作成候補:
	##	- 「input_sequence 列を表示するメソッド」
	##	- 「各 column の overlap 値を表示するメソッド」
	##	- 「各 column の connected synapses の数を表示するメソッド」
	##	- 


	def output_activity_of_columns_sp(self, time):
		l = int(float(self.shared_parameters.columns_per_region)**0.5)
		array_output = numpy.zeros((l,l))

	def show_triumphant_imshow_sp(self, time):
		l = int(float(self.shared_parameters.columns_per_region)**0.5) #columns_per_region の二乗根
		array_output = numpy.zeros((l,l))
		for c in range(self.shared_parameters.columns_per_region):
			if c in self.active_columns_with_history[-1]:
				array_output[math.floor(c / l), c - int(l * math.floor(c/ l))] = 1.0
		grapher.auto_imshow_customized(array_output, l, l, 'x','y', self.dir_for_debug + 'imshow/imshow_sp_' + str(time) + '.png','title','gray',0,1)

	#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	#Methods for TP debug
	#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

	##メソッド作成候補:
	##	- 「各 cell の active / unactive を表示するメソッド」
	##	- 「各 cell の predictive / unpredictive を表示するメソッド」
	##	- 「各 cell の learn / unlearn を表示するメソッド」


	def show_triumphant_imshow_tp(self, time, state):
		l = int(float(self.shared_parameters.columns_per_region)**0.5) #columns_per_region の二乗根
		array_output = numpy.zeros((l,l))
		for c in range(self.shared_parameters.columns_per_region):
			if state == 'active_state':
				column_is_active = 0
				for cl in range(len(self.columns[c].cells)):
					column_is_active = column_is_active + self.columns[c].cells[cl].active_state[-1]
				#if column_is_active > 0:
				array_output[math.floor(c / l), c - int(l * math.floor(c/ l))] = float(column_is_active) / float(self.tp_parameters.cells_per_column)
				if self.columns[c].bottom_up_predicted == 1:
					array_output[math.floor(c / l), c - int(l * math.floor(c/ l))] = array_output[math.floor(c / l), c - int(l * math.floor(c/ l))] * 0.8
			if state == 'predictive_state':
				column_is_predictive = 0
				for cl in range(len(self.columns[c].cells)):
					column_is_predictive = column_is_predictive + self.columns[c].cells[cl].predictive_state[-2]
					array_output[math.floor(c / l), c - int(l * math.floor(c/ l))] = float(column_is_predictive) / float(self.tp_parameters.cells_per_column)

			if state == 'learn_state':
				column_is_learning = 0
				for cl in range(len(self.columns[c].cells)):
					column_is_learning = column_is_learning + self.columns[c].cells[cl].learn_state[-1]
				array_output[math.floor(c / l), c - int(l * math.floor(c/ l))] =float(column_is_learning) / float(self.tp_parameters.cells_per_column)
		grapher.auto_imshow_customized(array_output, l, l, 'x','y', self.dir_for_debug + 'imshow/imshow_tp_' + state + '_' + str(time) + '.png','title','jet',0,1)

#==========================================================
#Functions
#==========================================================

def read_an_exist_file(filename):
	memory_file = open(filename, 'rb')
	memory = pickle.load(memory_file)
	memory_file.close()
	return memory
	
def read(filename, input_sequence_length):
	try:
	#if 1:
		memory_file = open(filename, 'rb')
		memory = pickle.load(memory_file)
		memory_file.close()
		if hasattr(memory, 'learning_files_count'):
			memory.learning_files_count = memory.learning_files_count + 1
		else:
			memory.learning_files_count = 0
	#	memory.read_global_parameters()
		print 'Memory File has been read.'
	except:
		memory = Memory(filename, input_sequence_length)
	return memory

def save(memory):
	memory_file = open(memory.filename,'wb')
	pickle.dump(memory, memory_file)
	memory_file.close()
	return 0

if __name__ == '__main__':
	print '?'
