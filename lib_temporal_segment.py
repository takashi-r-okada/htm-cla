#!env python
# -*- coding: utf-8 -*-

#import lib_parameters

from lib_temporal_segment_update import *
from lib_temporal_synapse import * 

class Temporal_segment(object):

	#----------------------------------------------------------
	#A Method for Appending a new time step for TP
	#----------------------------------------------------------

	#----------------------------------------------------------
	#Methods for Phase 1st of TP
	#----------------------------------------------------------
	
	def segment_active(self, columns, time, state_type):
		number_of_active_synapses = 0
		for sn in range(len(self.temporal_synapses)):
			number_of_active_synapses = number_of_active_synapses + self.temporal_synapses[sn].synapse_active(columns, time, state_type)
		#print 'number_of_active_synapses', number_of_active_synapses
		if number_of_active_synapses > self.tp_parameters.activation_threshold:
			return 1
		else:
			return 0
	def get_segment_active_synapses(self, segment_index, columns, time, new_synapses):
		active_synapses = []
		if segment_index != -1:
			for sn in range(len(self.temporal_synapses)):
				if self.temporal_synapses[sn].synapse_active(columns, time, 'active_state'):
					active_synapses.append(sn)
		segment_update = Segment_update([self.shared_parameters, self.sp_parameters, self.tp_parameters], segment_index, active_synapses, new_synapses)
		segment_update.make_additional_synapses_list(columns, time, self.cm)
		return segment_update
	def calculate_match_without_min_permanence(self, columns, time):
		match = 0
		for sn in self.temporal_synapses:
			if sn.synapse_active_without_min_permanence(columns, time):
				match = match + 1
		return match

	#----------------------------------------------------------
	#Methods for Phase 2nd of TP
	#----------------------------------------------------------
	
	#----------------------------------------------------------
	#Methods for Phase 3rd of TP
	#----------------------------------------------------------
	
	def adapt_existing_segment(self, segment_update, positive_reinforcement):
		if positive_reinforcement == 1:
			for sn in range(len(self.temporal_synapses)):
				if sn in segment_update.active_synapses:
					self.temporal_synapses[sn].increase_permanence()
				else:
					self.temporal_synapses[sn].decrease_permanence()
		else:
			for sn in range(len(self.temporal_synapses)):
				if sn in segment_update.active_synapses:
					self.temporal_synapses[sn].decrease_permanence()
	def re_initialize(self, starting_cells_for_additional_synapses):
		self.temporal_synapses = [0,] * len(starting_cells_for_additional_synapses) #一旦全てのシナプスを消して欲しい配列だけ作る
		for sn in range(len(self.temporal_synapses)):
			self.temporal_synapses[sn] = Temporal_synapse([self.shared_parameters, self.sp_parameters, self.tp_parameters])
			self.temporal_synapses[sn].re_initialize(starting_cells_for_additional_synapses[sn])

	#----------------------------------------------------------
	#Methods for Other Functions of TP
	#----------------------------------------------------------

	#----------------------------------------------------------
	#Methods of Constructor
	#----------------------------------------------------------
	
	def create_parameters(self, parameters):
		self.shared_parameters = parameters[0]
		self.sp_parameters = parameters[1]
		self.tp_parameters = parameters[2]
	def __init__(self, cl, cm, parameters):
		self.create_parameters(parameters)
		self.cl = cl
		self.cm = cm
		self.temporal_synapses = [0,] * self.tp_parameters.number_of_temporal_synapses
		for sn in range(self.tp_parameters.number_of_temporal_synapses):
			self.temporal_synapses[sn] = Temporal_synapse([self.shared_parameters, self.sp_parameters, self.tp_parameters])
		self.sequence_segment = int(round(random.random()))

if __name__ == '__main__':
	print '?'