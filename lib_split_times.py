#!env python
# -*- coding: utf-8 -*-
#>>> import lib_split_times

import time

class Split_times_step(object):
	def sp(self, step_index):
		self.st_sp[step_index] = time.time()
	def sp_debug(self, step_index):
		self.st_sp_debug[step_index] = time.time()
	def tp(self, step_index):
		self.st_tp[step_index] = time.time()
	def tp_debug(self, step_index):
		self.st_tp_debug[step_index] = time.time()

	def __init__(self):
		self.st_zero = time.time()
		self.st_sp = [[self.st_zero,] * 4,]
		self.st_sp_debug = [[self.st_zero,] * 2,]
		self.st_tp = [[self.st_zero,] * 5,]
		self.st_tp_debug = [[self.st_zero,] * 2,]

	def __repr__(self):
		result += u'''
## SP
    [0] %f : 時刻 (SP 開始),
    [1] %f : 時刻 (SP.Overlap 終了),
    [2] %f : 時刻 (SP.Inhibition 終了),
    [3] %f : 時刻 (SP.Learning 終了 (= SP 終了)).
'''.encode('utf-8') % (self.st_sp[0] - self.st_zero, self.st_sp[1] - self.st_zero, self.st_sp[2] - self.st_zero, self.st_sp[3] - self.st_zero)
		result += u'''
## SP Debug
    [0] %f : 時刻 (SP デバッグ用出力開始),
    [1] %f : 時刻 (SP デバッグ用出力終了).
'''.encode('utf-8') % (self.st_sp_debug[0] - self.st_zero, self.st_sp_debug[1] - self.st_zero)
		result += u'''
## TP
    [0] %f : 時刻 (TP 開始),
    [1] %f : 時刻 (新時刻ステップ追加終了),
    [2] %f : 時刻 (TP.Phase1 終了),
    [3] %f : 時刻 (TP.Phase2 終了),
    [4] %f : 時刻 (TP.Phase3 終了 (= TP 終了)).
'''.encode('utf-8') % (self.st_tp[0] - self.st_zero, self.st_tp[1] - self.st_zero,self.st_tp[2] - self.st_zero, self.st_tp[3] - self.st_zero, self.st_tp[4] - self.st_zero)
		result += u'''
## TP Debug
    [0] %f : 時刻 (TP デバッグ用出力開始),
    [1] %f : 時刻 (TP デバッグ用出力終了),
'''.encode('utf-8') % (self.st_tp_debug[0] - self.st_zero, self.st_tp_debug[1] - self.st_zero)

		return result

class Split_times(object):
	def opening(self, step_index):
		self.st_opening[step_index] = time.time()
	def closing(self, step_index):
		self.st_closing[step_index] = time.time()
	def __init__(self):
		self.st_zero = time.time()
		self.st_opening = [self.st_zero,] * 4
		self.st_closing = [self.st_zero,] * 4
		self.split_times_steps = []

	def __repr__(self):
		result = u'''# Split Times
'''.encode('utf-8')
		result += u'''
## 実行日時
    実験日         : 
    実験パラメータ :
'''.encode('utf-8')
		result += u'''
## 開始処理
    [0] %f : 時刻 (開始),
    [1] %f : 時刻 (インプットベクトルのサイズ検出・時刻方面サイズ検出終了),
    [2] %f : 時刻 (メモリ読み込みまたはメモリ新規作成終了),
    [3] %f : 時刻 (全時刻ステップの開始).
'''.encode('utf-8') % (self.st_opening[0] - self.st_zero, self.st_opening[1] - self.st_zero, self.st_opening[2] - self.st_zero, self.st_opening[3] - self.st_zero)

#		result += u'''
### SP
#    [0] %f : 時刻 (SP 開始),
#    [1] %f : 時刻 (SP.Overlap 終了),
#    [2] %f : 時刻 (SP.Inhibition 終了),
#    [3] %f : 時刻 (SP.Learning 終了 (= SP 終了)).
#'''.encode('utf-8') % (self.st_sp[0] - self.st_zero, self.st_sp[1] - self.st_zero, self.st_sp[2] - self.st_zero, self.st_sp[3] - self.st_zero)
#		result += u'''
### SP Debug
#    [0] %f : 時刻 (SP デバッグ用出力開始),
#    [1] %f : 時刻 (SP デバッグ用出力終了).
#'''.encode('utf-8') % (self.st_sp_debug[0] - self.st_zero, self.st_sp_debug[1] - self.st_zero)
#		result += u'''
### TP
#    [0] %f : 時刻 (TP 開始),
#    [1] %f : 時刻 (新時刻ステップ追加終了),
#    [2] %f : 時刻 (TP.Phase1 終了),
#    [3] %f : 時刻 (TP.Phase2 終了),
#    [4] %f : 時刻 (TP.Phase3 終了 (= TP 終了)).
#'''.encode('utf-8') % (self.st_tp[0] - self.st_zero, self.st_tp[1] - self.st_zero,self.st_tp[2] - self.st_zero, self.st_tp[3] - self.st_zero, self.st_tp[4] - self.st_zero)
#		result += u'''
### TP Debug
#    [0] %f : 時刻 (TP デバッグ用出力開始),
#    [1] %f : 時刻 (TP デバッグ用出力終了),
#'''.encode('utf-8') % (self.st_tp_debug[0] - self.st_zero, self.st_tp_debug[1] - self.st_zero)
		result += u'''
## 終了処理
    [0] %f : 時刻 (全時刻ステップの終了),
    [1] %f : 時刻 (メモリ書き込み終了),
    [2] %f : 時刻 (終了).'''.encode('utf-8') % (self.st_closing[0] - self.st_zero, self.st_closing[1] - self.st_zero, self.st_closing[2] - self.st_zero)

		return result

if __name__ == '__main__':
	print 'Usage: Import this module from other python script.'

	split_times = Split_times()
	print split_times