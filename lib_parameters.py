#!env python
# -*- coding: utf-8 -*-

import sys

#==========================================================
#Fast Configurations
#==========================================================

#----------------------------------------------------------
#リージョン自体のプロパティ
#----------------------------------------------------------

columns_per_region = 64
initial_inhibition_radius = 10
cells_per_column = 1

#sparse_ratio = 0.02 #general
sparse_ratio = 0.2
#for 64 columns operation
#2 % とかいう疎度はもっと豊富にメモリが使える '''''''ラグジュアリー''''''' な環境でやんなさい．

[permanence_mean, permanence_sd] = [0.2, 0.03]
initial_perm = permanence_mean + permanence_sd * 2.0 #for TP Synapse

permanence_inc = 0.3
permanence_dec = 0.3

#----------------------------------------------------------
#インプットデータのプロパティ
#----------------------------------------------------------

input_sequence_length = 8320

#==========================================================
#Private Constants
#==========================================================

norm_horizon_of_whole_region = float(initial_inhibition_radius)/float(columns_per_region)
##一つのカラムが見る地平線の大きさの半分．

desired_local_activity = 2 * int(round(float(initial_inhibition_radius) * sparse_ratio))
##抑制範囲内における勝者リストに加えるカラムの数
##半径を直径にするために 2 倍してある．

#==========================================================
#Classes (to generate parameters-objects)
#==========================================================

class Parameters(object):

	#----------------------------------------------------------
	#Methods of Constructor
	#----------------------------------------------------------
	
	def __init__(self, pooling_type):
		if pooling_type == 'shared':
			self.columns_per_region = columns_per_region #64 #1 リージョンあたり幾つのカラムを置くか

			self.connected_perm = permanence_mean
			##シナプスの接続を決める永続値の閾値

			self.permanence_inc = permanence_inc
			##1 ステップの学習における永続値の上昇幅

			self.permanence_dec = permanence_dec
			##1 ステップの学習における永続値の下降幅

		elif pooling_type == 'sp':
			self.min_overlap = int(input_sequence_length * sparse_ratio * norm_horizon_of_whole_region * 0.5)
			##抑制において，抑制対象とならない最小オーバーラップ値
			##この 0.5 が妥当がどうか，要調整 (2015.08.25 11:58)

			self.desired_local_activity = desired_local_activity
			##抑制範囲内における勝者リストに加えるカラムの数

			self.initial_inhibition_radius = initial_inhibition_radius
			##1 次元距離，これは毎ステップ変わる．

			self.length_history_kept = 100
			##過去 n 回の平均値を取って学習を調整する場合の遡る history ステップ数

			#----------------------------------------------------------
			#Initial Permanence of Spatial Synapses
			#----------------------------------------------------------

			self.permanence_mean = permanence_mean
			self.permanence_sd = permanence_sd

		elif pooling_type == 'tp':
			self.cells_per_column = cells_per_column
			##1 カラムあたり幾つのセルを置くか

			#self.activation_threshold = 15 #p.62, WhitePaper.
			self.activation_threshold = desired_local_activity
			##要調整 (2015.08.25 11:58)

			self.min_threshold = round(float(desired_local_activity) * 0.5)
			if self.min_threshold < 1:
				print 'min_threshold = 0. Error.'
				sys.exit(1)
			##0.5 という factor が適切かどうか．要調整 (2015.08.25 11:58)

			#self.number_of_temporal_segments = 10
			##超適当．要調整 (2015.08.25 11:58)
			self.number_of_temporal_segments = 2
			##最初は少なくして sequence segment = 1 のセグメントを学習によって追加してもらおうという魂胆．

			self.number_of_temporal_synapses = int(round(initial_inhibition_radius * cells_per_column * 0.5))
			##超適当．要調整 (2015.08.25 11:58)

			self.initial_perm = initial_perm
			##新しく追加するシナプスの初期永続値
			##0.2 は white paper における典型値

			self.new_synapses_count = self.number_of_temporal_synapses * 4
			##学習時に 1 セグメントに追加されるシナプスの最大数
			##最後の 2 が適切かどうか．要調整 (2015.08.25 11:58)

		else:
			print 'Error. pooling_type is undefined.'
			sys.exit(1)

#==========================================================
#Functions
#==========================================================

def read(pooling_type):
	parameters = Parameters(pooling_type)
	return parameters
def create_parameters(outer_object):
	outer_object.shared_parameters = read('shared')
	outer_object.sp_parameters = read('sp')
	outer_object.tp_parameters = read('tp') 
