#!env python
# -*- coding: utf-8 -*-

import random
import lib_parameters

from lib_temporal_segment import *

class Cell(object):
	
	#----------------------------------------------------------
	#A Method for Appending a new time step for TP
	#----------------------------------------------------------
	
	def append_time_step(self):
		self.predictive_state.append(0)
		self.active_state.append(0)
		self.learn_state.append(0)

	#----------------------------------------------------------
	#Methods for Phase 1st of TP
	#----------------------------------------------------------

	def determine_an_active_cell(self, columns):
	#bottom_up_predicted == 1 であるならば 1 を返す．
	#それ以外ならば 0 を返す
		#print ',\tself.predictive_state[-2] =',self.predictive_state[-2]
		if self.predictive_state[-2] == 1:
			sg = self.get_active_segment(columns)
			#print 'sg =', sg
			if sg == -1:
				#print 'K', sg
				#self.predictive_state[-2]が
				#逆に間違っていると思われるので訂正しに行く
				self.correct_predictive_state(0)
				return [0,0]
			elif self.temporal_segments[sg].sequence_segment == 1:
				#print 'L', sg
				self.active_state[-1] = 1
				if self.temporal_segments[sg].segment_active(columns, -2, 'learn_state'):
					learn_cell_chosen = 1
					self.learn_state[-1] = 1
				else:
					learn_cell_chosen = 0
				return [1, learn_cell_chosen]
			else:
				return [0,0]
		else:
			return [0,0]
	def get_active_segment(self, columns):
		active_segment = []
		for sg in range(len(self.temporal_segments)):
			if self.temporal_segments[sg].segment_active(columns, -2, 'active_state'):
				active_segment.append(sg)
		#if len(active_segment) == 0:
		#	return -1

		#何故 active_segment が 0 であるのに get_active_segment が実行されてしまうのか (2015/08/12, 18:10)
		# -> この鍵は，columns を下へ下へと引数として渡してくる際に，columns[t = ''''-2''''] を渡していない (t=-1 のを渡してしまってるよね) という所に潜んでいる． (2015/08/12, 18:21)
		# -> どこも間違っていない．恐らくメモリがたりなさすぎて管理できなくなっているのではないか？ (2015/08/12, 20:57)
		# -> 例外が起こっても良いようにしておこう

		sg_returned = 0
		if len(active_segment) > 1:
			for sg in range(len(active_segment)):
				if self.temporal_segments[sg].sequence_segment == 1:
					#print 'A'
					sg_returned = 1
					return int(sg)
		elif len(active_segment) == 1:
			#print 'B'
			sg_returned = 1
			return int(active_segment[0])

		if sg_returned == 0:
			return -1
	def correct_predictive_state(self, new_state):
		self.predictive_state[-2] = new_state
	def make_segment_update(self, columns, sg):
		self.learn_state[-1] = 1
		if sg == -1:
			new_temporal_segment = Temporal_segment(self.index,self.cm,[self.shared_parameters, self.sp_parameters, self.tp_parameters])
			#ここ，ちゃんと最初から最適化されたセグメントオブジェクトを作るようにそのためのメソッド or 関数を書いてくれ．このまま使うな．\
			segment_update = new_temporal_segment.get_segment_active_synapses(sg, columns, -2, 1)
		#	self.temporal_segments.append(new_temporal_segment)
		else:
			segment_update = self.temporal_segments[sg].get_segment_active_synapses(sg, columns, -2, 1)
		segment_update.sequence_segment = 1
		self.segment_update_list.append(segment_update)
	def get_best_matching_segment(self, columns, time):
		best_matching_segment = -1
		max_match = 0
		for sg in range(len(self.temporal_segments)):
			match = self.temporal_segments[sg].calculate_match_without_min_permanence(columns, time)
			if match < self.tp_parameters.min_threshold:
				match = 0
			if max_match < match:
				max_match = match
				best_matching_segment = sg
		return best_matching_segment, max_match

	#----------------------------------------------------------
	#Methods for Phase 2nd of TP
	#----------------------------------------------------------
	
	def calculate_predictive_state(self, columns):
		for sg in range(len(self.temporal_segments)):
			#print '\t\t\t\t',self.temporal_segments[sg].segment_active(columns, -1, 'active_state')
			if self.temporal_segments[sg].segment_active(columns, -1, 'active_state'):
				self.predictive_state[-1] = 1
				#print '\t\t\t\tself.predictive_state[-1] =', self.predictive_state[-1], ', (After calculated)'
				active_update = self.temporal_segments[sg].get_segment_active_synapses(sg, columns, -1, 0)
				pred_segment, match = self.get_best_matching_segment(columns, -1)
				pred_update = self.temporal_segments[sg].get_segment_active_synapses(pred_segment, columns, -2, 1)

				self.segment_update_list = self.segment_update_list + [active_update, pred_update]

	#----------------------------------------------------------
	#Methods for Phase 3rd of TP
	#----------------------------------------------------------
	
	def tp_learn(self):
		if self.learn_state[-1] == 1:
			self.adapt_segments(1)
			self.segment_update_list = []
		elif self.predictive_state[-1] == 0:
			self.adapt_segments(0)
			self.segment_update_list = []
	def adapt_segments(self, positive_reinforcement):

		#----------------------------------------------------------
		#既存 temporal segment の permanence 更新
		#----------------------------------------------------------

		for su in self.segment_update_list:
			if su.segment_index != -1:
				self.temporal_segments[su.segment_index].adapt_existing_segment(su, positive_reinforcement)


		#----------------------------------------------------------
		#新たな temporal segment の追加
		#----------------------------------------------------------
	
		for su in self.segment_update_list:
			if su.segment_index == -1:
				new_segment = Temporal_segment(self.index,self.cm,[self.shared_parameters, self.sp_parameters, self.tp_parameters])
				new_segment.re_initialize(su.starting_cells_for_additional_synapses)

				#----------------------------------------------------------
				#予約された sequence segment 値の反映
				#----------------------------------------------------------
				
				new_segment.sequence_segment = su.sequence_segment

				self.temporal_segments.append(new_segment)

	#----------------------------------------------------------
	#Methods for Other Functions of TP
	#----------------------------------------------------------

	#----------------------------------------------------------
	#Methods of Constructor
	#----------------------------------------------------------
	
	def __init__(self, cl, cm):
		lib_parameters.create_parameters(self)
		self.index = cl
		self.cm = cm
		self.predictive_state = [0,0,] 
		self.active_state = [round(random.random()**2.0),round(random.random()**2.0),] #初期値．
		self.learn_state = [round(random.random()**2.0),round(random.random()**2.0),] #初期値．
		self.temporal_segments = [0,] * self.tp_parameters.number_of_temporal_segments #要素数は処理中に増減する
		for sg in range(self.tp_parameters.number_of_temporal_segments):
			self.temporal_segments[sg] = Temporal_segment(cl,cm,[self.shared_parameters, self.sp_parameters, self.tp_parameters])
		#self.temporal_segment_update = Segment_update()
		self.learning_radius = 0.0
		self.segment_update_list = [] 

if __name__ == '__main__':
	print '?'