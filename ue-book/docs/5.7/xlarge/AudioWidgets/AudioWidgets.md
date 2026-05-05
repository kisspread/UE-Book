# Audio Widgets

> Collection of widgets tailored to interacting with audio-related data and systems.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、样式资产、蓝图控件） |
| 模块 | `AudioWidgetsCore` (RuntimeAndProgram), `AudioWidgets` (Runtime), `AudioWidgetsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-12-10 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets) | |

## 用途

AudioWidgets 是一套**音频可视化 UI 组件库**，为 Unreal Engine 提供专业的音频分析和交互控件。它解决的核心问题是：在引擎内实时显示和操控音频数据。

该插件包含三大类功能：

1. **音频分析仪面板**：示波器（Oscilloscope）、矢量示波器（Vectorscope）、频谱图（Spectrum Plot）、响度计（Loudness Meter），可作为 Audio Analyzer Rack 的独立单元使用
2. **材质驱动的音频控件**：使用材质（Material）而非纹理渲染的旋钮（Knob）、滑块（Slider）、按钮（Button）、电平表（Meter）、包络线（Envelope），提供比传统 Slate 控件更丰富的视觉效果
3. **采样序列显示组件**：波形查看器（Waveform Viewer）、标尺（Ruler）、网格覆盖层（Grid Overlay）、播放头（Playhead）、触发阈值线（Trigger Threshold Line），用于时间域音频数据的精确可视化

插件默认未启用（`Installed: false`），需要在项目设置中手动开启。它依赖 AudioSynesthesia 插件进行音频分析，并且 AudioWidgetsCore 模块专门支持 UnrealInsights 程序。

## 使用场景

- 你在制作音频编辑工具，需要在编辑器中显示实时波形 → 用 `SFixedSampledSequenceViewer` + `FWaveformAudioSamplesDataProvider`
- 你需要一个矢量示波器来监控立体声相位 → 用 `UAudioVectorscope` UMG 控件
- 你正在构建自定义音频混音器界面，需要材质风格的旋钮和滑块 → 用 `UAudioMaterialKnob` / `UAudioMaterialSlider`
- 你需要在 MetaSounds 编辑器中显示 ADSR 包络曲线 → 用 `UAudioMaterialEnvelope`
- 你要实现一个实时示波器来观察音频信号波形 → 用 `FAudioOscilloscope` Rack Unit
- 你需要一个专业的音频电平表来监控音量 → 用 `UAudioMaterialMeter` 或 `SAudioMeter`

## 蓝图用法

### 音频材质电平表（Audio Material Meter）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Meter Channel Info` | 设置电平表各通道的音量值 | `UAudioMaterialMeter` |
| `Get Meter Channel Info` | 获取当前各通道音量值 | `UAudioMaterialMeter` |
| `Meter Channel Info Delegate` | 绑定委托，自动驱动电平表数值 | `UAudioMaterialMeter` |

### 音频材质按钮（Audio Material Button）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Is Pressed` | 设置按钮按下状态 | `UAudioMaterialButton` |
| `Get Is Pressed` | 获取按钮当前是否按下 | `UAudioMaterialButton` |
| `On Button Pressed Changed Event` | 按钮状态变化时触发的事件 | `UAudioMaterialButton` |

### 矢量示波器（Vectorscope）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Processing` | 开始音频采样和矢量示波器渲染 | `UAudioVectorscope` |
| `Stop Processing` | 停止处理 | `UAudioVectorscope` |

### 使用示例

**创建矢量示波器 UMG 控件：**

1. 在 UMG 设计器中拖入 `AudioVectorscope` 控件
2. 设置 `Audio Bus` 属性指向一个已创建的 AudioBus 资产
3. 调整 `Display Persistence Ms`（显示持续时间，默认 60ms）
4. 调整 `Scale`（缩放比例，默认 1.0）
5. 设置 `Grid Divisions`（网格划分数，默认 2）
6. 在 BeginPlay 中调用 `Start Processing` 开始显示
7. 在 EndPlay 中调用 `Stop Processing` 停止

**创建材质风格电平表：**

1. 在 UMG 设计器中拖入 `AudioMaterialMeter` 控件
2. 在 Style 属性中配置 `FAudioMaterialMeterStyle`（材质、颜色、方向等）
3. 设置 `Orientation`（水平或垂直）
4. 通过 `Set Meter Channel Info` 节点传入 `FMeterChannelInfo` 数组来驱动电平显示
5. 或绑定 `Meter Channel Info Delegate` 委托实现自动更新

## C++ 用法

### 头文件引入

```cpp
// 音频材质控件
#include "AudioMaterialSlate/AudioMaterialMeter.h"
#include "AudioMaterialSlate/AudioMaterialButton.h"
#include "AudioMaterialSlate/AudioMaterialEnvelope.h"

// 音频分析仪
#include "AudioOscilloscope.h"
#include "AudioVectorscope.h"

// 波形显示
#include "SFixedSampledSequenceViewer.h"
#include "SFixedSampledSequenceRuler.h"
#include "WaveformAudioSamplesDataProvider.h"

// 传输控制
#include "SparseSampledSequenceTransportCoordinator.h"
#include "FixedSampledSequenceGridData.h"

// 样式
#include "AudioWidgetsStyle.h"
#include "AudioMeterStyle.h"
```

### 基本用法：创建波形查看器

从 `SFixedSampledSequenceViewer` 的构造方式提取：

```cpp
// 创建网格服务
TSharedRef<FFixedSampledSequenceGridData> GridService = 
    MakeShared<FFixedSampledSequenceGridData>(
        TotalFrames,        // 总帧数
        SampleRate,         // 采样率 (Hz)
        TicksTimeFont,      // 刻度字体
        GridSizePixels      // 网格像素大小
    );

// 准备采样数据
TArray<float> SampleData;
// ... 填充音频采样数据 ...

// 创建波形查看器 Slate 控件
SampledSequenceDrawingUtils::FSampledSequenceDrawingParams DrawParams;
// ... 配置绘制参数 ...

TSharedRef<SFixedSampledSequenceViewer> Viewer = 
    SNew(SFixedSampledSequenceViewer)
    .SequenceDrawingParams(DrawParams)
    .HideBackground(false)
    .HideGrid(false)
    .Style(&FAudioWidgetsStyle::Get().GetWidgetStyle<FSampledSequenceViewerStyle>("SampledSequenceViewer.Style"));

// 构造时传入数据和网格服务
Viewer->Construct(
    SFixedSampledSequenceViewer::FArguments(),
    MakeArrayView(SampleData),
    NumChannels,
    GridService
);

// 后续更新波形数据
Viewer->UpdateView(MakeArrayView(NewSampleData), NumChannels);
```

### 基本用法：音频采样数据提供器

从 `FWaveformAudioSamplesDataProvider` 提取：

```cpp
// 创建数据提供器，连接到 AudioBus
TSharedPtr<AudioWidgets::FWaveformAudioSamplesDataProvider> DataProvider =
    MakeShared<AudioWidgets::FWaveformAudioSamplesDataProvider>(
        AudioDeviceId,      // 音频设备 ID
        AudioBus,           // UAudioBus* 音频总线
        NumChannels,        // 要提供的通道数
        TimeWindowMs,       // 时间窗口（毫秒）
        MaxTimeWindowMs,    // 最大时间窗口
        AnalysisPeriodMs    // 分析周期（毫秒）
    );

// 开始处理
DataProvider->StartProcessing();

// 监听数据更新
DataProvider->OnDataViewGenerated.AddLambda(
    [](FFixedSampledSequenceView InView, uint32 FirstSampleIndex)
    {
        // 处理新的音频数据视图
    }
);

// 配置触发模式（用于示波器）
DataProvider->SetTriggerMode(EAudioOscilloscopeTriggerMode::Rising);
DataProvider->SetTriggerThreshold(0.1f);
DataProvider->SetChannelToAnalyze(0);

// 停止处理
DataProvider->StopProcessing();
```

### 进阶用法：创建示波器 Rack Unit

从 `FAudioOscilloscope` 提取：

```cpp
// 创建示波器分析仪 Rack Unit
AudioWidgets::FAudioOscilloscope Oscilloscope(
    AudioDeviceId,                          // 音频设备 ID
    2,                                      // 通道数
    10.0f,                                  // 时间窗口 10ms
    10.0f,                                  // 最大时间窗口 10ms
    10.0f,                                  // 分析周期 10ms
    EAudioPanelLayoutType::Basic,           // 面板布局
    nullptr,                                // 自定义样式（可选）
    nullptr                                 // 外部 AudioBus（可选）
);

// 获取 AudioBus 并连接音频源
UAudioBus* Bus = Oscilloscope.GetAudioBus();

// 开始处理
Oscilloscope.StartProcessing();

// 获取面板 Widget 用于嵌入 UI
TSharedRef<SWidget> PanelWidget = Oscilloscope.GetPanelWidget();

// 停止处理
Oscilloscope.StopProcessing();
```

### 进阶用法：传输控制器（Transport Coordinator）

从 `FSparseSampledSequenceTransportCoordinator` 提取：

```cpp
// 创建传输控制器
FSparseSampledSequenceTransportCoordinator Transport;

// 设置缩放比例
Transport.SetZoomRatio(0.5f);  // 50% 缩放

// 设置播放进度
Transport.SetProgressRatio(0.3f);  // 30% 进度

// 获取当前显示范围
TRange<double> DisplayRange = Transport.GetDisplayRange();

// 拖拽播放头
Transport.ScrubFocusPoint(0.5f, true);  // 移动到 50%，正在拖拽

// 坐标转换
float ZoomedRatio = Transport.ConvertAbsoluteRatioToZoomed(0.5f);
float AbsoluteRatio = Transport.ConvertZoomedRatioToAbsolute(ZoomedRatio);

// 监听事件
Transport.OnFocusPointMoved.AddLambda([](float NewPosition) {
    // 播放头移动
});

Transport.OnDisplayRangeUpdated.AddLambda([](const TRange<double>& NewRange) {
    // 显示范围更新
});
```

## Demo 示例

### 自定义音频电平表 Widget

```cpp
// MyAudioMeterWidget.h
#pragma once

#include "Components/ActorComponent.h"
#include "AudioMaterialSlate/AudioMaterialMeter.h"
#include "MyAudioMeterWidget.generated.h"

UCLASS(BlueprintType, Blueprintable)
class UMyAudioMeterWidget : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
    TObjectPtr<UAudioMaterialMeter> MeterWidget;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
    int32 NumChannels = 2;

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void UpdateMeterLevels(const TArray<float>& ChannelLevels);

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;
};
```

```cpp
// MyAudioMeterWidget.cpp
#include "MyAudioMeterWidget.h"

void UMyAudioMeterWidget::BeginPlay()
{
    Super::BeginPlay();

    if (MeterWidget)
    {
        // 初始化通道信息
        TArray<FMeterChannelInfo> InitialInfo;
        for (int32 i = 0; i < NumChannels; ++i)
        {
            FMeterChannelInfo ChannelInfo;
            ChannelInfo.MeterValue = 0.0f;
            ChannelInfo.PeakValue = 0.0f;
            ChannelInfo.ClippingValue = 1.0f;
            InitialInfo.Add(ChannelInfo);
        }
        MeterWidget->SetMeterChannelInfo(InitialInfo);
    }
}

void UMyAudioMeterWidget::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 从音频分析获取实时电平数据并更新
    // UpdateMeterLevels(CurrentLevels);
}

void UMyAudioMeterWidget::UpdateMeterLevels(const TArray<float>& ChannelLevels)
{
    if (!MeterWidget) return;

    TArray<FMeterChannelInfo> ChannelInfo;
    for (int32 i = 0; i < ChannelLevels.Num(); ++i)
    {
        FMeterChannelInfo Info;
        Info.MeterValue = FMath::Clamp(ChannelLevels[i], 0.0f, 1.0f);
        Info.PeakValue = Info.MeterValue;
        Info.ClippingValue = 1.0f;
        ChannelInfo.Add(Info);
    }
    MeterWidget->SetMeterChannelInfo(ChannelInfo);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 音频分析（插件级依赖） |
| `AudioMixer` | 音频混音器设备访问、AudioBus 支持 |
| `SignalProcessing` | DSP 信号处理（循环缓冲区等） |
| `AudioAnalyzer` | 音频分析器 Rack 框架（IAudioAnalyzerRackUnit） |
| `AudioMaterialWidgets` | 材质驱动的 Slate 控件底层实现 |

## 维护状态

### 近期更新

```
- 412925d26756 Fix non material MetaSound slider value snapping to 0
  → 修复非材质 MetaSound 滑块值吸附到 0 的问题
- a616a8f1e42e Fix undo not working in MetaSounds after undoing a change using an audio material slider
  → 修复使用音频材质滑块后 MetaSounds 撤销功能失效
- ff6917e0db87 Fixing audio slider binding
  → 修复音频滑块绑定问题
```

### 维护评价

**活跃维护中**。AudioWidgets 自 2020 年创建以来持续更新，最近的提交集中在修复 MetaSounds 编辑器中音频材质控件的交互问题（撤销、值吸附、绑定），说明该插件与 MetaSounds 工作流深度集成，是 Epic 当前音频工具链的重要组成部分。

该插件规模较大（222 个源文件），包含完整的运行时、编辑器和 UnrealInsights 支持三个模块。代码结构清晰，Slate 控件和 UMG Widget 分层设计，样式系统完善。作为 Epic 官方维护的音频 UI 组件库，推荐在需要专业音频可视化功能的项目中使用。

**注意事项**：
- 插件默认未启用（`Installed: false`），需在项目设置中手动开启
- 依赖 AudioSynesthesia 插件，需确保其同时启用
- AudioWidgetsCore 模块仅在 UnrealInsights 程序中加载

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets)
- [AudioSynesthesia 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioSynesthesia)