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
import change_filename
import struct

#設定
line_plotsize = 0.5
marker_plotsize =2
fft_plot_x_range = [100, 10000]
min_amplitude = 0.02



argvs = sys.argv

#chunk = 5000 #このフレーム数だけ wave file から読み込む模様

infilename_wav = argvs[1]
fft_span_sec = float(argvs[2])
outfilename_png = change_filename.add_filename(infilename_wav, '_output')
outfilename_png = change_filename.change_extname(outfilename_png, 'png')
outfilename_spc = change_filename.change_extname(infilename_wav ,'spc')

#スペクトルファイルを扱う
outfile_spc = open(outfilename_spc, 'wb')

infile_wav = wave.open(infilename_wav, 'rb')
#print infile_wav
sampling_rate = infile_wav.getframerate()
chunk = int(fft_span_sec * sampling_rate)
full_length = infile_wav.getnframes()
position_shift = math.floor(chunk/2)
#print position_shift, 'position_shift'
#print infile_wav.tell(), 'tell0'
#print infile_wav.getsampwidth()

outfile_spc.seek(256, 0)

for h in range(int(math.floor(full_length/position_shift)) - 1):
	present_position = infile_wav.tell()
	if h != 0:
		infile_wav.setpos(present_position - chunk + position_shift)
		#print infile_wav.tell(),h
	#print chunk
	indata = infile_wav.readframes(chunk)
	array = scipy.fromstring(indata,scipy.int16)

	if infile_wav.getnchannels() > 1:
		array_mono = numpy.zeros(chunk)
		for i in range(len(array)): #モノラル化
			if i % 2 == 0:
				array_mono[i/2] = array[i]
			else:
				pass
		array = numpy.copy(array_mono)

	array = array/float(2 ** 15) #規格化 #16bit サンプルサイズを仮定している
	#print array

	#print type(infile_wav.getframerate())
	time_array = numpy.arange(0.0, 1.0/float(sampling_rate) * float(chunk), 1.0/float(infile_wav.getframerate()))
	#print len(time_array)
	#print len(array)
	outfilename_05d_png = change_filename.add_filename(outfilename_png, '%05d' % h)
	if numpy.amax(abs(array)) > min_amplitude:
		grapher.auto_fast(time_array,array,'Time (s)','y',outfilename_05d_png,'title (t = %0.2f)' % (float(h) * position_shift / sampling_rate),'-')

	array_fft = scipy.fft(array)
	m = math.ceil((len(array) + 1)/2.0)

	array_fft = array_fft[:m]
	array_fft = abs(array_fft) #複素数を絶対値にする時の顔
	for i in range(len(array_fft)):
		array_fft[i] = array_fft[i] ** 2.0

	max_array_fft = numpy.max(array_fft)

	array_fft_db = numpy.zeros(len(array_fft))
	for i in range(len(array_fft)):
		#array_fft_db[i] = general.dbm(array_fft[i])- 58.17
		array_fft_db[i] = general.dbm(array_fft[i]/max_array_fft)

	#array_fft_domain = numpy.arange(sampling_rate)
	#print float(len(array)) / float(sampling_rate)
	array_fft_domain = numpy.arange(float(sampling_rate) / float(len(array)), float(sampling_rate),float(sampling_rate) / float(len(array)))

	#スペクトル表示
	if numpy.amax(abs(array)) > min_amplitude:
		max_frequency = 450 * 3
		array_fft_domain_index = numpy.where(array_fft_domain < max_frequency)
		#print array_fft_domain
		#grapher.auto_fast(array_fft_domain[array_fft_domain_index],array_fft_db[array_fft_domain_index],'Frequency (Hz)','y','output_fft' + '%05d' % h + '.png','title','-')

		fig = pylab.figure()
		ax = fig.add_subplot(111)
		fig.subplots_adjust(bottom = 0.16,top=0.9,left=0.16,right=0.9) 
		#ax.plot(array_fft_domain[array_fft_domain_index],array_fft_db[array_fft_domain_index],'-', linewidth = line_plotsize, markersize = marker_plotsize)
		pylab.bar(array_fft_domain[array_fft_domain_index[0]],array_fft_db[array_fft_domain_index[0]] + 8.0)
		#pylab.ylim(-10.0,0.0)
		pylab.ylim(0.0,8.0)
		pylab.xlim(fft_plot_x_range[0], fft_plot_x_range[1])
		pylab.xscale('log')
		#pylab.xlim(3470.0,3530.0)
		grapher.graph_draw('Frequency(Hz)', 'Amplitude(dB)', 'Spectrum (t = %0.2f)' % (float(h) * position_shift / sampling_rate))
		outfilename_fft_05d_png = change_filename.add_filename(outfilename_png, '_fft' + '%05d' % h)
		pylab.savefig(outfilename_fft_05d_png)
		pylab.close()
		#print array_fft_domain_index
		for j in array_fft_domain_index[0]:
			#print j
			#print array_fft_domain[j]
			bdata = struct.pack('1f', array_fft_domain[j])
			outfile_spc.write(bdata)
			bdata = struct.pack('1f', array_fft_db[j])
			outfile_spc.write(bdata)
			#bdata = struct.pack('1H', 0)
			#outfile_spc.write(bdata)




	if h!=0 and h % 10 == 0:
		print h / math.floor(full_length/position_shift) * 100, '%'

outfile_spc.seek(8, 0)
bdata = struct.pack('1l', len(array_fft_domain_index[0]))
outfile_spc.write(bdata)
outfile_spc.seek(192,0)
print str(len(infilename_wav))
bdata = struct.pack(str(len(infilename_wav)) + 's', infilename_wav)
outfile_spc.write(bdata)
outfile_spc.close()




