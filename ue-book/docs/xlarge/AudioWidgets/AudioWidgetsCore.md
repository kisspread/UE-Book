# AudioWidgets

> Collection of widgets tailored to interacting with audio-related data and systems.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AudioWidgetsCore` (RuntimeAndProgram), `AudioWidgets` (Runtime), `AudioWidgetsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-12-10 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets) | |

## 用途

AudioWidgets 插件提供了一套专门用于音频数据可视化和交互的 Slate 控件集合。其核心功能是提供高性能、可定制的音频电平表（Audio Meter）控件，用于实时显示音频信号的幅度、峰值和削波状态。该插件解决了在编辑器工具、音频分析界面（如 Unreal Insights）以及运行时音频监控 UI 中，需要专业、美观且高效的音频数据可视化需求。它将音频数据的显示逻辑与具体的音频引擎（如 Engine 模块）解耦，使得核心控件可以在不依赖完整引擎的场景（如独立程序）中使用。

## 使用场景

- **音频编辑器工具**：在自定义的音频编辑器或资产检查器中，需要实时显示音频波形或电平。
- **音频分析与监控**：在开发用于分析音频频谱、响度或诊断音频问题的工具时，需要专业的仪表盘控件。
- **Unreal Insights 集成**：为 Unreal Insights 性能分析工具提供独立的音频监控面板，用于分析游戏运行时的音频性能。
- **运行时音频设置 UI**：在游戏内的音频设置菜单中，提供可视化的音量或电平反馈。

## 蓝图用法

AudioWidgets 主要提供底层的 Slate 控件，其蓝图集成主要通过 `UAudioMeter` 等 UMG 包装器（位于 `AudioWidgets` 模块）实现。核心数据结构 `FAudioMeterChannelInfo` 是蓝图类型，可用于在蓝图中传递音频通道信息。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Meter Channel Info` | 设置音频电平表要显示的通道信息数组 | `UAudioMeter` (UMG 包装器) |
| `Get Meter Channel Info` | 获取当前音频电平表显示的通道信息 | `UAudioMeter` (UMG 包装器) |
| `Set Orientation` | 设置电平表的绘制方向（水平/垂直） | `UAudioMeter` (UMG 包装器) |
| `Set Background Color` | 设置电平表背景颜色 | `UAudioMeter` (UMG 包装器) |
| `Set Meter Value Color` | 设置电平表当前值的颜色 | `UAudioMeter` (UMG 包装器) |
| `Set Meter Peak Color` | 设置电平表峰值指示器的颜色 | `UAudioMeter` (UMG 包装器) |

### 使用示例（蓝图描述）

1.  在 UMG 设计器中，从调色板拖入一个 `AudioMeter` 控件。
2.  在事件图表中，创建一个 `FAudioMeterChannelInfo` 结构体数组，为每个音频通道（如左、右声道）设置 `MeterValue`（当前值）、`PeakValue`（峰值）和 `ClippingValue`（削波值）。
3.  将包含通道信息的数组连接到 `AudioMeter` 控件的 `Set Meter Channel Info` 节点，即可实时更新电平表显示。
4.  可通过 `Set Orientation`、`Set Background Color` 等节点在运行时动态调整控件外观。

## C++ 用法

### 头文件引入

```cpp
#include "SAudioMeterWidget.h"
#include "AudioMeterChannelInfo.h"
#include "AudioMeterWidgetStyle.h"
```

### 基本用法

创建并配置一个基础的音频电平表 Slate 控件。

```cpp
// 来源: 基于 SAudioMeterWidget.h 的接口设计
// 创建一个音频电平表控件
TSharedRef<SAudioMeterWidget> AudioMeter = SNew(SAudioMeterWidget)
    .Orientation(Orient_Vertical) // 设置为垂直方向
    .BackgroundColor(FLinearColor::Black)
    .MeterValueColor(FLinearColor::Green)
    .MeterPeakColor(FLinearColor::Red);

// 准备通道数据
TArray<FAudioMeterChannelInfo> ChannelInfo;
FAudioMeterChannelInfo LeftChannel;
LeftChannel.MeterValue = 0.7f; // 当前电平值 (0.0 - 1.0)
LeftChannel.PeakValue = 0.9f;  // 峰值
ChannelInfo.Add(LeftChannel);

FAudioMeterChannelInfo RightChannel;
RightChannel.MeterValue = 0.65f;
RightChannel.PeakValue = 0.85f;
ChannelInfo.Add(RightChannel);

// 更新控件显示
AudioMeter->SetMeterChannelInfo(ChannelInfo);
```

### 进阶用法

使用样式资产（`FSlateWidgetStyleAsset`）来统一管理控件外观，并实现动态更新。

```cpp
// 来源: 基于 AudioMeterWidgetStyle.h 的样式系统
// 1. 加载或创建一个样式资产
const FAudioMeterWidgetStyle& MeterStyle = FAudioMeterWidgetStyle::GetDefault(); // 或从资产加载

// 2. 使用样式创建控件
TSharedRef<SAudioMeterWidget> StyledMeter = SNew(SAudioMeterWidget)
    .Style(&MeterStyle)
    .MeterChannelInfo(TAttribute<TArray<FAudioMeterChannelInfo>>::Create(
        [this]() { return this->GetCurrentAudioLevels(); } // 绑定一个动态获取数据的函数
    ));

// 3. 在样式中自定义外观
FAudioMeterWidgetStyle CustomStyle;
CustomStyle.SetMeterSize(FVector2D(300.0f, 30.0f))
           .SetShowScale(true)
           .SetScaleSide(false) // 刻度显示在右侧
           .SetValueRangeDb(FVector2D(-60.0f, 0.0f)); // 显示范围 -60dB 到 0dB
```

## Demo 示例

一个在 Slate 应用程序中创建并更新音频电平表的最小示例。

**MyAudioMeterWidget.h**
```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "AudioMeterChannelInfo.h"

class SMyAudioMeterWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyAudioMeterWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    // 定时更新音频数据的函数
    void UpdateAudioLevels();

    TSharedPtr<class SAudioMeterWidget> MeterWidget;
    FTimerHandle UpdateTimerHandle;
};
```

**MyAudioMeterWidget.cpp**
```cpp
#include "MyAudioMeterWidget.h"
#include "SAudioMeterWidget.h"
#include "TimerManager.h"

void SMyAudioMeterWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SAssignNew(MeterWidget, SAudioMeterWidget)
            .Orientation(Orient_Horizontal)
            .MeterValueColor(FLinearColor::Yellow)
            .MeterPeakColor(FLinearColor::Red)
    ];

    // 启动一个定时器，每 50 毫秒更新一次数据（模拟实时音频）
    if (GEngine && GEngine->GetWorldContexts().Num() > 0)
    {
        UWorld* World = GEngine->GetWorldContexts()[0].World();
        if (World)
        {
            World->GetTimerManager().SetTimer(
                UpdateTimerHandle,
                this,
                &SMyAudioMeterWidget::UpdateAudioLevels,
                0.05f, // 50ms
                true
            );
        }
    }
}

void SMyAudioMeterWidget::UpdateAudioLevels()
{
    // 模拟生成随机的音频电平数据
    TArray<FAudioMeterChannelInfo> Levels;
    for (int32 i = 0; i < 2; ++i) // 模拟立体声
    {
        FAudioMeterChannelInfo Info;
        Info.MeterValue = FMath::FRandRange(0.0f, 1.0f);
        Info.PeakValue = FMath::Max(Info.MeterValue, Info.PeakValue * 0.95f); // 峰值缓降
        Info.ClippingValue = (Info.MeterValue > 0.98f) ? 1.0f : 0.0f;
        Levels.Add(Info);
    }

    if (MeterWidget.IsValid())
    {
        MeterWidget->SetMeterChannelInfo(Levels);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 插件声明依赖此插件，用于音频分析功能集成。 |

## 维护状态

### 近期更新

- 4d797bcdc6b4 Ran UnrealCodeFixup to move dllstorage to correct places in code
  - *代码维护性修复，调整了 DLL 导出符号的位置。*
- 56316db30d6d [AudioWidgets] Migration of FAudioMeterStyle, FAudioMeterDefaultColorStyle, FMeterChannelInfo and SAudioMeter logic to AudioWidgetsCore module in order to be able to use an audio meter widget without having to depend on Engine (so it can be used in Audio Insights standalone)
  - *重要架构更新：将核心样式、数据结构和控件逻辑迁移到 `AudioWidgetsCore` 模块，实现了与 Engine 的解耦，使其能在 Unreal Insights 等独立程序中使用。*
- fdb7f9b03d2c [AudioWidgets] Created AudioWidgetCore module, this module will contain widgets/logic that doesn't depend on Engine
  - *创建了 `AudioWidgetsCore` 模块，为上述解耦架构奠定基础。*

### 维护评价

**活跃维护**。该插件创建于 2020 年底，属于较新的插件。从近期的 Git 提交记录看，它在 2023 年经历了重要的架构重构（引入 `AudioWidgetsCore` 模块），旨在提升模块化和适用范围（支持独立程序）。这表明 Epic 仍在积极维护和改进此插件，以适应更广泛的使用场景（如 Unreal Insights）。目前没有发现已知的重大问题或废弃标记。**推荐使用**，特别是对于需要专业音频数据可视化且希望代码保持良好模块化的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供的信息中定位到具体测试文件路径)