#!env python
# -*- coding: utf-8 -*-

import random

class Temporal_synapse(object):

	#----------------------------------------------------------
	#A Method for Appending a new time step for TP
	#----------------------------------------------------------

	#----------------------------------------------------------
	#Methods for Phase 1st of TP
	#----------------------------------------------------------
	
	def synapse_active(self, columns, time, state_type):
		if state_type == 'active_state':
			#print self.starting_cell[1]
			#print columns[self.starting_cell[0]].cells[self.starting_cell[1]]
			if self.permanence > self.shared_parameters.connected_perm and columns[self.starting_cell[0]].cells[self.starting_cell[1]].active_state[time] == 1:
				return 1
			else:
				return 0
		if state_type == 'learn_state':
			if self.permanence > self.shared_parameters.connected_perm and columns[self.starting_cell[0]].cells[self.starting_cell[1]].learn_state[time] == 1:
				return 1
			else:
				return 0
	def synapse_active_without_min_permanence(self, columns, time):
		#本メソッドは state_type == 'active_state' 限定．
		if columns[self.starting_cell[0]].cells[self.starting_cell[1]].active_state[time] == 1:
			return 1
		else:
			return 0

	#----------------------------------------------------------
	#Methods for Phase 2nd of TP
	#----------------------------------------------------------
	
	#----------------------------------------------------------
	#Methods for Phase 3rd of TP
	#----------------------------------------------------------
	
	def increase_permanence(self):
		self.permanence = self.permanence + self.shared_parameters.permanence_inc
		if self.permanence > 1:
			self.permanence = 1.0
		elif self.permanence < 0:
			self.permanence = 0.0
	def decrease_permanence(self):
		self.permanence = self.permanence - self.shared_parameters.permanence_dec
		if self.permanence > 1:
			self.permanence = 1.0
		elif self.permanence < 0:
			self.permanence = 0.0
	def re_initialize(self,starting_cell):
		self.permanence = self.tp_parameters.initial_perm
		self.starting_cell = starting_cell

	#----------------------------------------------------------
	#Methods for Other Functions of TP
	#----------------------------------------------------------

	#----------------------------------------------------------
	#Methods for Constructor
	#----------------------------------------------------------
	
	def create_parameters(self, parameters):
		self.shared_parameters = parameters[0]
		self.sp_parameters = parameters[1]
		self.tp_parameters = parameters[2]
	def __init__(self, parameters):
		self.create_parameters(parameters)
		self.starting_cell = [random.randint(0, self.shared_parameters.columns_per_region - 1), random.randint(0, self.tp_parameters.cells_per_column - 1)] #index
		#self.permanence = 0.25 + 0.4 * (random.random())**2.0
		self.permanence = random.normalvariate(self.sp_parameters.permanence_mean,self.sp_parameters.permanence_mean)
		if self.permanence > 1:
			self.permanence = 1.0
		elif self.permanence < 0:
			self.permanence = 0.0

#def create_global_parameters(self, outer_shared_parameters, outer_sp_parameters, outer_tp_parameters): #メモリの新規作成時のみ実行
#	global shared_parameters
#	shared_parameters = outer_shared_parameters
#	global sp_parameters
#	sp_parameters = outer_sp_parameters
#	global tp_parameters
#	tp_parameters = outer_tp_parameters

if __name__ == '__main__':
	print '?'