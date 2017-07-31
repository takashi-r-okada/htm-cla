#!env python
# -*- coding: utf-8 -*-
#lib_temporal_segment_update.py

import random
import math

class Segment_update(object):

	#----------------------------------------------------------
	#A Method for Appending a new time step for TP
	#----------------------------------------------------------

	#----------------------------------------------------------
	#Methods for Phase 1st of TP
	#----------------------------------------------------------
	
	def make_additional_synapses_list(self, columns, time, cm_index):
		if self.new_synapses == 1:
			addition_count = self.tp_parameters.new_synapses_count - len(self.starting_cells_for_additional_synapses)
			if addition_count > 0:
				learn_cells = []
				for cm in range(len(columns)):
					if cm != cm_index:
						learn_cells_cm = columns[cm].acquire_learn_cells(time)
						for cl in learn_cells_cm:
							learn_cells.append([cm, cl])
				#print len(learn_cells), 'len_learn_cells'
				
				##注意:
				##	ここで learn_cells の要素数が 0 ならば無限ループが発生
				##	やるべきことは:
				##		1. learn_cells の要素が 1 つ以上になるように learn_state のでき方を調整する
				##		2. learn_cells の要素が 0 であった時にはどのような処理を行うかを記述する．
				if len(learn_cells) == 0:
					pass
					## learn_state が 1 のセルが 0 個の時は self.starting_cells_for_additional_synapses は [] で返す．
				else:
					learn_cells_mono = learn_cells[:]
					while len(learn_cells) < addition_count:
						learn_cells = learn_cells + learn_cells_mono
					for cl in range(addition_count):
						cell_index = random.randint(0, len(learn_cells)-1)
						self.starting_cells_for_additional_synapses.append(learn_cells[cell_index])
						del learn_cells[cell_index]
		else:
			pass

	#----------------------------------------------------------
	#Methods for Phase 2nd of TP
	#----------------------------------------------------------
	
	#----------------------------------------------------------
	#Methods for Phase 3rd of TP
	#----------------------------------------------------------

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
	def __init__(self, parameters, segment_index, active_synapses, new_synapses):
		self.create_parameters(parameters)
		self.new_synapses = new_synapses
		self.segment_index = segment_index
		self.sequence_segment = 0

		self.active_synapses = []
		self.starting_cells_for_additional_synapses = []
		if len(active_synapses) >= self.tp_parameters.new_synapses_count:
			#重複を許さない
			for sn in range(self.tp_parameters.new_synapses_count):
				synapse_index = int(round(random.random() * float(len(active_synapses) - 1)))
				#print 'synapse_index =', synapse_index, 'and len(active_synapses) =', len(active_synapses)
				self.active_synapses.append(active_synapses[synapse_index])
				del active_synapses[synapse_index]
		else:
			self.active_synapses = active_synapses

if __name__ == '__main__':
	print '?'