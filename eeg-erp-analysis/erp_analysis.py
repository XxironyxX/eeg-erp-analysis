import mne

# 数据保存在 ~/mne_data 目录下
data_path = mne.datasets.sample.data_path()

# 读取fif格式的原始数据，preload=True表示一次性全部加载到内存中
raw = mne.io.read_raw_fif(data_path / 'MEG' / 'sample' / 'sample_audvis_raw.fif', preload=True)


# 在完整的原始数据中，从名为'STI 014'的通道里找到所有事件
events = mne.find_events(raw, stim_channel='STI 014')
print(f'找到 {len(events)} 个事件')
print('前5个事件:', events[:5])

# 去掉MEG通道、保留EEG通道，也不要刺激通道（因为我们已经提取了事件）
raw_eeg = raw.copy().pick_types(meg=False, eeg=True, stim=False)
print(f'保留了 {len(raw_eeg.ch_names)} 个EEG通道')

# 示例数据中：1=左耳听觉刺激，2=右耳听觉刺激，3=视觉刺激
event_id = {'auditory/left': 1, 'auditory/right': 2, 'visual': 3}

# 提取刺激前0.2秒到刺激后0.5秒的数据
tmin, tmax = -0.2, 0.5

# baseline指定基线校正的时间窗口（这里取刺激前200ms）
epochs = mne.Epochs(raw_eeg, events, event_id, tmin=tmin, tmax=tmax,
                    baseline=(tmin, 0), preload=True)

print(f'提取了 {len(epochs)} 个epochs')


# 对所有epochs进行叠加平均
erp = epochs.average()


# plot_joint会同时显示波形图和地形图
erp.plot_joint()

# 保存波形图
fig = erp.plot_joint()
fig.savefig('erp_waveforms.png')