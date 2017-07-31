% initial reading
addpath(genpath('/Users/okada/Documents/MATLAB'))
filename = 'output.wav'
[x, fs] = audioread(filename)

% config
n_divide = 50

% main
numel_x = numel(x) % ファイル全体のサンプル数

fcoefs = MakeERBFilters(fs,32,100); % 32 チャンネル, fs [sps] の Gammatone Auditory フィルタの係数行列を生成

y = ERBFilterBank(x, fcoefs) % サンプルベクタ x と ERB filter bank のそれぞれとを掛ける
debug_0 = y
y_meddied = MeddisHairCell(y, fs)
y_meddied = y_meddied - mean(mean(y_meddied))
debug01 = y_meddied
%y_meddied = 10 * log10(abs(y_meddied));
y_meddied = power(abs(y_meddied),2);

% First 7 Time Point Reject
y_meddied = y_meddied(:,8:end)

% Decimation 処理
decimation_ratio = (numel_x - 7)/100
decimation_index = decimation_ratio:decimation_ratio:numel_x
rounded_decimation_index = round(decimation_index)
y_meddied = y_meddied(:,rounded_decimation_index)
debug02 = y_meddied

% ここからビンまとめ
bin_set_number = round(numel(y_meddied(1,:)) / (n_divide))
for c = 1 : n_divide
	if c == 1
		y_meddied_subset = y_meddied(:,1 : bin_set_number)
		y_meddied_subset_t = y_meddied_subset' %'
		y_meddied_binned_t = mean(y_meddied_subset_t)
	else
		y_meddied_subset = y_meddied(:,bin_set_number * (c-1) + 1 :bin_set_number * (c-1) + bin_set_number)
		y_meddied_subset_t = y_meddied_subset' %'
		y_meddied_binned_temp_t = mean(y_meddied_subset_t)
		y_meddied_binned_t = vertcat(y_meddied_binned_t, y_meddied_binned_temp_t)
	end
end
y_meddied = y_meddied_binned_t' %'
debug_1 = y_meddied

%ここまでビンまとめ

y_meddied_normalized = uint8((y_meddied - min(min(y_meddied)))/(max(max(y_meddied)) - min(min(y_meddied))) * 255)
% resp_linear = power(abs(fft(y_meddied')), 2) % '
% resp = (10 * log10(resp_linear)); %もともと Amplitude であった物をパワー且つ対数に直す
%freqScale = ((0: fft_npoint - 1)/(fft_npoint) * fs); % プロット用の横軸配列を用意する
%semilogx(freqScale(1: (fft_npoint/2 - 1)), resp(1:(fft_npoint/2 - 1),:)); % 
%axis([10 10000 -100 0]);
%xlabel('Frequency (Hz)');
%ylabel('Filter Response (dB)');


imwrite(y_meddied_normalized(:,1:end), jet,'output.png'); %
dlmwrite('output.txt',y_meddied_normalized(:,1:end),'\t')


quit


