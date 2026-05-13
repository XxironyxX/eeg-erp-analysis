# EEG ERP Analysis with MNE

## 项目描述
使用 MNE 库对公开 EEG 数据进行事件相关电位（ERP）分析，提取刺激锁时脑电响应。

## 数据来源
MNE 官方示例数据集（sample_audvis_raw.fif），包含听觉和视觉刺激的 EEG/MEG 数据。

## 分析步骤
1. 加载数据
2. 提取事件（刺激标记）
3. 保留 EEG 通道
4. 提取 epochs（刺激前后片段）
5. 计算 ERP（叠加平均）
6. 绘制波形图和地形图

## 运行方法
```bash
python erp_analysis.py
```

## 结果示例

## 依赖库
- mne >= 1.6.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
