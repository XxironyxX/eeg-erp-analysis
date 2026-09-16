"""
MNE 示例数据 ERP 分析：滤波去底噪 + 分段 + P1 峰值对齐 + 提取 P1
说明：示例数据无 oddball 范式，没有经典 P300，分析 P1 更合适。
"""

import mne
import numpy as np
from scipy.ndimage import shift as ndshift
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
#更改字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False   # 修复负号显示为方块

# ---------- 1. 读数据 ----------
data_path = mne.datasets.sample.data_path()
raw = mne.io.read_raw_fif(
    data_path / 'MEG' / 'sample' / 'sample_audvis_raw.fif',
    preload=True, verbose=False
)

# ---------- 2. 事件 ----------
events = mne.find_events(raw, stim_channel='STI 014', verbose=False) #找到事件发生的时间
print(f'找到 {len(events)} 个事件')

# ---------- 3. 滤波去底噪 ----------
raw_eeg = raw.copy().pick('eeg')
raw_eeg.filter(l_freq=0.1, h_freq=40.0,
               fir_design='firwin', verbose=False)
raw_eeg.notch_filter(freqs=50.0, verbose=False)
raw_eeg.set_eeg_reference('average', projection=False, verbose=False)
print(f'滤波完成，保留 {len(raw_eeg.ch_names)} 个 EEG 通道')

# ---------- 4. 分段 ----------
# 分析 P1：用视觉刺激（P1 在枕区最强），或听觉也可
event_id = {'auditory/left': 1, 'auditory/right': 2, 'visual': 3}
tmin, tmax = -0.2, 0.5          # P1 早，tmax 不用拉到 0.8

epochs = mne.Epochs(
    raw_eeg, events, event_id, tmin=tmin, tmax=tmax,
    baseline=(None, 0), preload=True,
    reject=dict(eeg=150e-6), verbose=False
)   #分段时指定时间窗
print(f'提取了 {len(epochs)} 个 epochs')

<<<<<<< Updated upstream
# 5. P1 峰值对齐
=======
# ============================================================
# 5. P1 峰值对齐
# ============================================================
>>>>>>> Stashed changes
p1_win    = (0.07, 0.15)       # P1 搜索窗（约 70–150 ms）
max_shift = 0.05               # P1 抖动小，限 ±50 ms
smooth_ms = 10                 # P1 尖，平滑短一点

data  = epochs.get_data()
times = epochs.times
sfreq = 1.0 / (times[1] - times[0])
mask  = (times >= p1_win[0]) & (times <= p1_win[1])
win_times = times[mask]

# 自动选 P1 最强通道（枕区会胜出）
mean_seg = data[:, :, mask].mean(axis=0)
ch_idx = int(np.argmax(mean_seg.mean(axis=1)))
align_channel = epochs.ch_names[ch_idx]
print(f'自动选中的对齐通道: {align_channel}')

# 平滑后逐试次找 P1 峰
sigma = max(1, int(smooth_ms / 1000 * sfreq))
lats = np.array([
    win_times[np.argmax(gaussian_filter1d(ep[ch_idx, mask], sigma))]
    for ep in data
])
print(f'对齐前 P1 潜伏期: {lats.mean()*1000:.1f} ± {lats.std()*1000:.1f} ms')

target_lat = lats.mean()
shifts_ms  = (target_lat - lats) * 1000
print(f'平移量: std {shifts_ms.std():.1f} ms, '
      f'最大 {np.abs(shifts_ms).max():.1f} ms, '
      f'|shift|>20ms 占比 {(np.abs(shifts_ms)>20).mean()*100:.1f}%')

# 平移（基线区保持不动）
dt = times[1] - times[0]
zero_idx = int(np.argmin(np.abs(times)))
aligned = np.empty_like(data)
for i, ep in enumerate(data):
    shift_samp = (target_lat - lats[i]) / dt
    shift_samp = np.clip(shift_samp, -max_shift/dt, max_shift/dt)
    for c in range(ep.shape[0]):
        pre  = ep[c, :zero_idx]
        post = ndshift(ep[c, zero_idx:], shift_samp,
                       mode='nearest', cval=0.0)
        aligned[i, c] = np.concatenate([pre, post])

epochs_aligned = mne.EpochsArray(
    aligned, epochs.info, events=epochs.events,
    tmin=tmin, event_id=epochs.event_id, baseline=None, verbose=False
)

<<<<<<< Updated upstream
#  6. 平均 
erp_raw     = epochs.average()
erp_aligned = epochs_aligned.average()

# 7. 量化 P1 幅值提升
=======
# ---------- 6. 平均 ----------
erp_raw     = epochs.average()
erp_aligned = epochs_aligned.average()

# ---------- 7. 量化 P1 幅值提升 ----------
>>>>>>> Stashed changes
def peak(evoked, ch, win):
    seg = evoked.copy().crop(tmin=win[0], tmax=win[1])
    idx = seg.ch_names.index(ch)
    arr = seg.data[idx]
    i = int(np.argmax(arr))
    return seg.times[i]*1000, arr[i]*1e6

lat_r, amp_r = peak(erp_raw,     align_channel, p1_win)
lat_a, amp_a = peak(erp_aligned, align_channel, p1_win)

print('\n===== P1 分析结果 =====')
print(f'通道: {align_channel}')
print(f'未对齐: 潜伏期 {lat_r:.1f} ms, 幅值 {amp_r:.2f} µV')
print(f'对齐后: 潜伏期 {lat_a:.1f} ms, 幅值 {amp_a:.2f} µV')
<<<<<<< Updated upstream
print(f'P1 幅值提升: {amp_a - amp_r:+.2f} µV  ({(amp_a/amp_r-1)*100:+.1f}%)')

# 8. 可视化 
=======
print(f'★ P1 幅值提升: {amp_a - amp_r:+.2f} µV  ({(amp_a/amp_r-1)*100:+.1f}%)')

# ---------- 8. 可视化 ----------
>>>>>>> Stashed changes
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(erp_raw.times,     erp_raw.copy().pick(align_channel).data[0]*1e6,
        label='未对齐', lw=1.5)
ax.plot(erp_aligned.times, erp_aligned.copy().pick(align_channel).data[0]*1e6,
        label='P1 峰值对齐', lw=1.5)
ax.axvline(target_lat, color='gray', ls='--', alpha=0.6,
           label=f'目标潜伏期 {target_lat*1000:.0f} ms')
ax.axvspan(p1_win[0], p1_win[1], color='orange', alpha=0.1, label='P1 窗')
ax.set_xlabel('Time (s)'); ax.set_ylabel('Amplitude (µV)')
ax.set_title(f'{align_channel}: P1 对齐前后对比')
ax.legend(); fig.tight_layout()
fig.savefig('p1_align_compare.png', dpi=150)

<<<<<<< Updated upstream
# joint 图（查看 P1 地形）
erp_aligned.plot_joint(times=[0.08, 0.10, 0.12, 0.15],
                       title='ERP (P1 对齐)')

plt.show()
=======
# joint 图（看 P1 地形）
erp_aligned.plot_joint(times=[0.08, 0.10, 0.12, 0.15],
                       title='ERP (P1 对齐)')

plt.show()
>>>>>>> Stashed changes
