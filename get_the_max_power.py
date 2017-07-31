#!env python
# -*- coding: utf-8 -*-
# > ipython cut_and_fft.py wave_ファイル名 FFT_間隔秒数
#注意．パワーを出力する．

#import
import numpy
import wave
import scipy
import matplotlib.pyplot
import math
import sys
import grapher
import general
import pylab


#設定
line_plotsize = 2
marker_plotsize =2
fft_plot_x_range = [440/2, 440 * 3]



argvs = sys.argv

#chunk = 5000 #このフレーム数だけ wave file から読み込む模様

max_power = -1000
infilename_wav = argvs[1]
fft_span_sec = float(argvs[2])

infile_wav = wave.open(infilename_wav, 'rb')
#print infile_wav
sampling_rate = infile_wav.getframerate()
chunk = int(fft_span_sec * sampling_rate)
full_length = infile_wav.getnframes()
position_shift = math.floor(chunk/5)

for h in range(int(math.floor(full_length/position_shift)) - 1):
	present_position = infile_wav.tell()
	if h != 0:
		infile_wav.setpos(present_position - chunk + position_shift)

	#print chunk
	indata = infile_wav.readframes(chunk)
	array = scipy.fromstring(indata,scipy.int16)

	array_mono = numpy.zeros(chunk)

	for i in range(len(array)): #モノラル化
		if i % 2 == 0:
			array_mono[i/2] = array[i]
		else:
			pass
	array = numpy.copy(array_mono)

	array = array/(2 ** 15) #規格化
	#print array

	#print type(infile_wav.getframerate())
	time_array = numpy.arange(0.0, 1.0/float(sampling_rate) * float(chunk), 1.0/float(infile_wav.getframerate()))
	#print len(time_array)
	#print len(array)
	#grapher.auto_fast(time_array,array,'Time (s)','y','output' + '%05d' % h + '.png','title','-')

	array_fft = scipy.fft(array)
	m = math.ceil((len(array) + 1)/2.0)

	array_fft = array_fft[:m]
	array_fft = abs(array_fft) #複素数を絶対値にする時の顔
	for i in range(len(array_fft)):
		array_fft[i] = array_fft[i] ** 2.0
	max_array_fft = numpy.max(array_fft)
	#array_fft = array_fft) / float(numpy.max(array_fft))
	array_fft_db = numpy.zeros(len(array_fft))
	for i in range(len(array_fft)):
		array_fft_db[i] = general.dbm(array_fft[i])
	array_fft_domain = numpy.arange(sampling_rate)
	#print float(len(array)) / float(sampling_rate)
	array_fft_domain = numpy.arange(float(sampling_rate) / float(len(array)), sampling_rate,float(sampling_rate) / float(len(array)))

	max_power_temp = numpy.amax(array_fft_db)
	if max_power_temp > max_power:
		max_power = max_power_temp
	print max_power

	#スペクトル表示
	#max_frequency = 450 * 3
	#array_fft_domain_index = numpy.where(array_fft_domain < max_frequency)
	#print array_fft_domain
	#grapher.auto_fast(array_fft_domain[array_fft_domain_index],array_fft_db[array_fft_domain_index],'Frequency (Hz)','y','output_fft' + '%05d' % h + '.png','title','-')

	#fig = pylab.figure()
	#ax = fig.add_subplot(111)
	#fig.subplots_adjust(bottom = 0.16,top=0.9,left=0.16,right=0.9) 
	#ax.plot(array_fft_domain[array_fft_domain_index],array_fft_db[array_fft_domain_index],'-', linewidth = line_plotsize, markersize = marker_plotsize)
	#pylab.ylim(-15.0,0.0)
	#pylab.xlim(fft_plot_x_range[0], fft_plot_x_range[1])
	#pylab.xscale('log')
	#pylab.xlim(3470.0,3530.0)
	#grapher.graph_draw('Frequency(Hz)', 'Amplitude(dB)', 'Spectrum (t = %0.2f)' % (float(h) * position_shift / sampling_rate))
	#pylab.savefig('output_fft' + '%05d' % h + '.png')
	#pylab.close()


	#if h!=0 and h % 10 == 0:
	#	print h / math.floor(full_length/position_shift) * 100, '%'





