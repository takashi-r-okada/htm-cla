##################################################################
##################  空間プーリング前文  #############################
##################################################################
##諸関数の定義
def connected_synapses(spatial_synapse_permanence, column_index): #1 セルに繋がった全 potential_synapse の永続値を受け取って connected な index のみを返す
	connected_synapses = []
	for j in range(len(spatial_synapse_permanence[column_index])):
		if spatial_synapse_permanence[column_index,j] > connected_perm:
			connected_synapses.append(j)
	#print connected_synapses
	return connected_synapses
def input_bit(time, column, connected_synapse):
	#ここで，time = t0, column = c0, connected_synapse = s0 の時の値を定義して返してくれ
	#返す値は 0 または 1
	return 0
def boost_function(active_duty_cycle_c, min_duty_cycle_c):
	if active_duty_cycle_c > min_duty_cycle_c:
		return 1
	else:
		return min_duty_cycle_c / active_duty_cycle_c
def neighbors(column):
	neighbors_columns = []
	for j in range(len(columns_per_region)):
		if j >= column - inhibition_radius and j <= column + inhibition_radius and j >= 0 and j <= columns_per_region - 1:
			neighbors_columns.append(j)
	return neighbors_columns 
def kth_score(columns, overlap, desired_local_activity): #overlap は全 column の overlap 値を持った 1 次元配列．グローバル変数．
	neighbors_overlap = []
	for j in columns:
		neighbors_overlap.append(overlap[j])
	neighbors_overlap = sorted(neighbors_overlap, reverse = True)
	return neighbors_overlap[desired_local_activity - 1]
def max_duty_cycle(columns, active_duty_cycle): #columns には neighbors(c) を入れる．active_duty_cycle は全 column の overlap 値を持った 1 次元配列．グローバル変数．
	neighbors_active_duty_cycle = []
	for j in columns:
		neighbors_active_duty_cycle.append(active_duty_cycle[j])
	neighbors_active_duty_cycle = sorted(neighbors_active_duty_cycle, reverse = True)
	return neighbors_active_duty_cycle[0]
def update_active_duty_cycle(column, active_columns_history, active_columns): #とりあえずこの関数内で active_columns_history を更新して，続いて update_active_duty_cycle を算出し返す
	active_columns_history[column, 1:active_duty_cycle_length - 1] = active_columns_history[column, 0:active_duty_cycle_length - 2]
	if column in active_columns:
		active_columns_history[column, 0] = 1
	else:
		active_columns_history[column, 0] = 0
	updated_active_duty_cycle = numpy.average(active_columns_history[column])
	return [active_columns_history, updated_active_duty_cycle]
def update_overlap_duty_cycle(column, min_overlap_history, overlap, min_overlap):
	min_overlap_history[column, 1:active_duty_cycle_length - 1] = min_overlap_history[column, 0:active_duty_cycle_length - 2]
	if overlap[column] > min_overlap:
		min_overlap_history[column, 0] = 1
	else:
		min_overlap_history[column, 0] = 0
	updated_overlap_duty_cycle = numpy.average(min_overlap_history[column])
	return [min_overlap_history, updated_overlap_duty_cycle]
def average_receptive_field_size(connected_synapses_all):
	connected_synapses_number = 0
	connected_synapses_distance = 0
	for j in range(len(connected_synapses_all)):
		for k in range(len(connected_synapses_all[j][1])):
			connected_synapses_sum_of_distance = connected_synapses_distance + (connected_synapses_all[j][0] - connected_synapses_all[j][1][k]) ** 2.0
			connected_synapses_number = connected_synapses_number + 1
	connected_synapses_distance = (connected_synapses_distance ** 0.5) / connected_synapses_number
	return connected_synapses_distance


##################################################################
##################  空間プーリング本文  #############################
##################################################################
##input ファイルの読み込み
infile = open(filename, 'r')
text = infile.read()
texts = text.split()
first_line_bool = 0
for line in texts:
	inarray_temp = numpy.array(list(line))
	if first_line_bool == 0:
		inarray = inarray_temp
	else:
		inarray = numpy.vstack((inarray, inarray_temp))
infile.close()

connected_synapses_all = []
##Phase 1: オーバーラップ
for c in range(columns_per_region): 
	overlap[c] = 0
	for s in connected_synapses(spatial_synapse_permanence,c):
		overlap[c] = overlap[c] + input_bit(t,c,s)
		connected_synapses_all.append([c,connected_synapses(spatial_synapse_permanence,c)])
	if overlap[c] < min_overlap:
		overlap[c] = 0 #みんな大好き足切り
	else:
		overlap[c] = overlap[c] * boost[c]
##Phase 2: 抑制
active_columns = []
for c in range(columns_per_region):
	min_local_activity = kth_score(neighbors(c),overlap,desired_local_activity) #c の neighbors のうち desired_local_activity 個目のオーバーラップ値を返す．所謂「min_local_activity；最小の局所アクティブ閾値」
	if overlap[c] > 0 and overlap[c] >= min_local_activity:
		if not (c in active_columns):
			active_columns.append(c)
##Phase 3: 学習
for c in active_columns:
	for s in spatial_synapse_permanence[c]:
		if s in connected_synapses[spatial_synapse_permanence, c]:
			spatial_synapse_permanence[c, s] = spatial_synapse_permanence[c, s] + permanence_inc
			spatial_synapse_permanence[c, s] = min(1.0, spatial_synapse_permanence[c, s])
		else:
			spatial_synapse_permanence[c,s] = spatial_synapse_permanence[c, s] + permanence_dec
			spatial_synapse_permanence[c, s] = max(0.0, spatial_synapse_permanence[c, s])
for c in columns:
	min_duty_cycle[c] = 0.01 * max_duty_cycle(neighbors(c),active_duty_cycle)
	[active_columns_history, active_duty_cycle[c]] = update_active_duty_cycle(c, active_columns_history, active_columns)
	boost[c] = boost_function(active_duty_cycle[c], min_duty_cycle[c])
	###active になった移動平均頻度を計算したが，引き続き min_overlap を越えた移動平均頻度も求める
	###一般には min_overlap を超えたとしてもその後の抑制をくぐり抜けなければ active にはなれない
	[min_overlap_history,overlap_duty_cycle[c]] = update_overlap_duty_cycle(c, min_overlap_history, overlap, min_overlap)
	if overlap_duty_cycle[c] < min_duty_cycle[c]:
		for k in range(len(spatial_synapse_permanence)):
			spatial_synapse_permanence[c,k] = spatial_synapse_permanence[c,k] + 0.1 * connected_perm
inhibition_radius = average_receptive_field_size(connected_synapses_all) #抑制半径の更新




##################################################################
##################  時間プーリング前文  #############################
##################################################################
##各変数の定義
activation_threshold = 20 #整数
##諸オブジェクトの定義
temporary_synapses_permanence = [[[[]] * cells_per_column] * columns_per_region] * active_duty_cycle_length #ここは各シナプスの [接続先, 永続値] を入れる箱
predictive_state_history = numpy.zeros((active_duty_cycle_length, columns_per_region,cells_per_column), dtype=int8)
active_state_history = numpy.zeros((active_duty_cycle_length, columns_per_region, cells_per_column), dtype=int8)
learn_state_history = numpy.zeros((active_duty_cycle_length, columns_per_region, cells_per_column), dtype=int8)
sequence_segment = numpy.zeros((columns_per_region, cells_per_column),dtype=int8)
##諸関数の定義
def segment_active(column, cell, segment, time, state, temporary_synapses_permanence):
	if state == 'active_state':
		if len(temporary_synapses_permanence[time][column][cell][segment]) > activation_threshold:
			pass
	elif state == 'learn_state':
		pass
	else:
		print 'Error.'
		return 1
	else:
		return 0
def get_active_segment(column, cell, time, state, temporary_synapses_permanence):
	active_segment_index = []
	for j in range(len(temporary_synapses_permanence[time][column][cell])):
		if segment_active(columns, cell, j, time, state,temporary_synapses_permanence) == 1:
			active_segment_index.append(j)
	return active_segment_index
def get_best_matching_segment(column, cell, time, activation_threshold, min_threshold, temporary_synapses_permanence):
	for j in range(len(temporary_synapses_permanence[time][column][cell])):
		for k in range(len(temporary_synapses_permanence[time][column][cell][j])):
			temporary_synapses_permanence[time][column][cell][j][k][1]


##################################################################
##################  時間プーリング本文  #############################
##################################################################
##Phase 1: t ステップ目の active_state_history
for c in active_columns:
	feed_forward_predicted = 0
	learn_cell_chosen = 0
	for j in range(len(cells_per_column)):
		if predictive_state_history[1, c, j] == 1:
			s = get_active_segment(c, j, 1, active_state, temporary_synapses_permanence) #値は 1 つのみ返す
			if sequence_segment[c, j, s] == 1:
				feed_forward_predicted = 1
				active_state_history[0, c, j] = 1
				if segment_active(c, j, s, 1, learn_state,temporary_synapses_permanence):
					learn_cell_chosen = 1
					learn_state_history[0, c, j] = 1
	if feed_forward_predicted == 0:
		for k in range(len(cells_per_column)):
			active_state_history[0, c, k] = 1
	if learn_cell_chosen == 0:
		s = get_best_matching_segment() #セグメントを表す添字を返す


##Phase 2: t ステップ目の predictive_state


##Phase 3: Updating Synapses




