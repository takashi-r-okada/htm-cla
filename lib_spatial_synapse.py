#!env python
# -*- coding: utf-8 -*-

import random
import lib_parameters

class Spatial_synapse(object): #これが input sequence の全ての数分，またはその部分集合分の数分だけ作られて一つのカラムに内包される．
	
	#----------------------------------------------------------
	#Methods for Overlap of SP
	#----------------------------------------------------------
	
	def get_input_value(self, input_bit):

		#print memory
		if self.permanence > self.shared_parameters.connected_perm:
			return input_bit
		else:
			return 0

	#----------------------------------------------------------
	#Methods for Inhibition of SP
	#----------------------------------------------------------
	
	#----------------------------------------------------------
	#Methods for Learning of SP
	#----------------------------------------------------------
	
	def sp_learn(self):
		if self.permanence > self.shared_parameters.connected_perm:
			self.permanence = self.permanence + self.shared_parameters.permanence_inc
			self.permanence = min(1.0, self.permanence)
		else:
			self.permanence = self.permanence - self.shared_parameters.permanence_dec
			self.permanence = max(0.0, self.permanence)
	def boost_permanence(self):
		self.permanence = self.permanence + 0.1 * self.shared_parameters.connected_perm 

	#----------------------------------------------------------
	#Methods of Constructor
	#----------------------------------------------------------
	
	def __init__(self):

		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#Variable for SP
		#- - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		lib_parameters.create_parameters(self)
		#self.permanence = (random.random())**2.0
		self.permanence = random.normalvariate(self.sp_parameters.permanence_mean, self.sp_parameters.permanence_sd)
		if self.permanence > 1.0:
			self.permanence = 1.0
		elif self.permanence < 0.0:
			self.permanence = 0.0


if __name__ == '__main__':
	print '?'
