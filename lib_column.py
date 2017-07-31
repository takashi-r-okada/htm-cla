#!env python
# -*- coding: utf-8 -*-

import lib_parameters

from lib_spatial_synapse import * #for Operating SP 
from lib_cell import * #for Operating TP

class Column(object):

	#----------------------------------------------------------
	#Methods for Whole of SP
	#----------------------------------------------------------

	def get_stance(self, c, s):
		return ((float(c) - float(s) * float(self.shared_parameters.columns_per_region) / float(len(self.spatial_synapses))) ** 2.0 ) ** 0.5

	#----------------------------------------------------------
	#Methods for Overlap of SP
	#----------------------------------------------------------
	
	def update_overlap(self, c, input_sequence, inhibition_radius):
		self.overlap = 0
		for s in range(len(input_sequence)):
			#if self.spatial_synapses[s].permanence > shared_parameters.connected_perm:
			#	self.overlap = self.overlap + self.spatial_synapses[s].get_input_value()

			if self.get_stance(c, s) <= 2 * inhibition_radius:
				self.overlap = self.overlap + self.spatial_synapses[s].get_input_value(input_sequence[s])
		if self.overlap < self.sp_parameters.min_overlap:
			self.overlap = 0.0
		else:
			self.overlap = float(self.overlap) * self.boost

	#----------------------------------------------------------
	#Methods for Inhibition of SP
	#----------------------------------------------------------
	
	#----------------------------------------------------------
	#Methods for Learning of SP
	#----------------------------------------------------------
	
	def sp_learn(self):
		for s in range(len(self.spatial_synapses)):
			self.spatial_synapses[s].sp_learn()
	def update_active_duty_cycle(self, c, active_columns_with_history):
		self.active_duty_cycle = 0.0
		for active_columns in active_columns_with_history:
			if c in active_columns:
				self.active_duty_cycle = self.active_duty_cycle + 1.0
		self.active_duty_cycle = self.active_duty_cycle / float(len(active_columns_with_history))
	def update_boost(self):
		if self.active_duty_cycle == 0:
			self.active_duty_cycle = 1.0/self.sp_parameters.length_history_kept
		if self.active_duty_cycle > self.min_duty_cycle:
			self.boost = 1.0
		else:
			self.boost = self.min_duty_cycle / self.active_duty_cycle
	def update_overlap_duty_cycle(self, c, overlap_with_history):
		self.overlap_duty_cycle = 0.0
		for overlap in overlap_with_history:
			if c in overlap:
				self.overlap_duty_cycle = self.overlap_duty_cycle + 1.0
		self.overlap_duty_cycle = self.overlap_duty_cycle / float(len(overlap_with_history))
	def boost_permanence(self):
		if self.overlap_duty_cycle < self.min_duty_cycle:
			for s in range(len(self.spatial_synapses)): #全てのシナプス候補について行ってよろしい．
				self.spatial_synapses[s].boost_permanence()
	def average_receptive_field_size(self, c): #connected_synapses_number == 0 であるようなカラムの平均半径は 0 と返す．(0 という記号なので，出力先でうまく扱ってくれ)
		average_receptive_field_size = 0.0
		connected_synapses_number = 0
		for s in range(len(self.spatial_synapses)):
			if self.spatial_synapses[s].permanence > self.shared_parameters.connected_perm:
				average_receptive_field_size = average_receptive_field_size + self.get_stance(c, s)
				connected_synapses_number = connected_synapses_number + 1
		if connected_synapses_number == 0:
			return 0
		else:
			return average_receptive_field_size / float(connected_synapses_number)

	#----------------------------------------------------------
	#A Method for Appending a new time step for TP
	#----------------------------------------------------------

	def append_time_step(self):
		for cl in range(self.tp_parameters.cells_per_column):
			self.cells[cl].append_time_step()

	#----------------------------------------------------------
	#Methods for Phase 1st of TP
	#----------------------------------------------------------
	
	def calculate_active_state(self, columns):
		self.bottom_up_predicted = 0
		self.learn_cell_chosen = 0
		for cl in range(self.tp_parameters.cells_per_column):
			#print '\t\t\tCell =', cl,
			self.bottom_up_predicted, self.learn_cell_chosen = self.cells[cl].determine_an_active_cell(columns)
		if self.bottom_up_predicted == 0:
			for cl in range(self.tp_parameters.cells_per_column):
				self.cells[cl].active_state[-1] = 1
		if self.learn_cell_chosen == 0:
			self.add_temporal_segment(columns)
	def add_temporal_segment(self, columns):
		cl, sg = self.get_best_matching_cell(columns, -2)
		self.cells[cl].make_segment_update(columns, sg)
	def get_best_matching_cell(self, columns, time): 
		best_matching_segment = -1
		best_match = 0

		for cl in range(self.tp_parameters.cells_per_column):
			sg, match = self.cells[cl].get_best_matching_segment(columns, time)
			if best_match < match:
				best_match = match
				best_matching_segment = sg
				best_matching_cell = cl
		if best_match < self.tp_parameters.min_threshold:
			best_match = 0
			best_matching_segment = -1
			min_number_of_segments = 0
			cell_with_min_number_of_segments = -1
			for cl in range(self.tp_parameters.cells_per_column):
				number_of_segments = len(self.cells[cl].temporal_segments)
				if min_number_of_segments >= number_of_segments:
					min_number_of_segments = number_of_segments
					cell_with_min_number_of_segments = cl
			best_matching_cell = cell_with_min_number_of_segments
		return best_matching_cell, best_matching_segment

	#----------------------------------------------------------
	#Methods for Phase 2nd of TP
	#----------------------------------------------------------

	def calculate_predictive_state(self, columns):
		for cl in range(self.tp_parameters.cells_per_column):
			#print '\t\t\tCell =', cl
			self.cells[cl].calculate_predictive_state(columns)

	#----------------------------------------------------------
	#Methods for Phase 3rd of TP
	#----------------------------------------------------------
	
	def tp_learn(self):
		for cl in range(self.tp_parameters.cells_per_column):
			self.cells[cl].tp_learn()

	#----------------------------------------------------------
	#Methods for Other Functions of TP
	#----------------------------------------------------------

	def acquire_learn_cells(self, time):
		learn_cells = []
		for cl in range(self.tp_parameters.cells_per_column):
			if self.cells[cl].learn_state[time] == 1:
				learn_cells.append(cl)
		return learn_cells

	#----------------------------------------------------------
	#Methods of Constructor
	#----------------------------------------------------------
	
	def __init__(self, index, input_sequence_length):

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Variable for SP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		lib_parameters.create_parameters(self)
		self.index = index
		self.overlap = 0 # 初期値は 0 で良い (実際に使う時も毎時間ごとに 0 に初期化される)
		self.min_duty_cycle = 0.0 
		self.active_duty_cycle = 0.0
		self.boost = 2.0 # 初期値．1 ステップ毎に更新される．
		#print input_sequence_length, 'input_sequence_length'
		self.spatial_synapses = [0,] * input_sequence_length
		for s in range(input_sequence_length):
			self.spatial_synapses[s] = Spatial_synapse()
		self.neighbors = [] # index を入れるリスト
		self.min_local_activity = 0
		self.kth_score = 0
		self.overlap_duty_cycle = 0.0
		self.learn_cell_chosen = 0

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Variable for TP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		self.bottom_up_predicted = 0
		self.cells = [0,] * self.tp_parameters.cells_per_column
		for cl in range(self.tp_parameters.cells_per_column):
			self.cells[cl] = Cell(cl,index)

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Variable for Debug
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		self.predictive_columns = 0

if __name__ == '__main__':
	print '?'