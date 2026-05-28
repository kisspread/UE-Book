# AudioWidgets

> Collection of widgets tailored to interacting with audio-related data and systems.

| 属性 | 值 |
|---|---|
| 中文名 | 音频控件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产） |
| 模块 | `AudioWidgetsCore` (Runtime), `AudioWidgets` (Runtime), `AudioWidgetsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-12-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets) | |

## 用途

AudioWidgets 插件提供了一套专为音频工作流设计的 Slate/UMG 控件集合。它解决的核心问题是：在 Unreal Engine 中没有开箱即用的专业音频电平表、响度表等控件，开发者需要从零构建。

插件主要提供以下功能：

1. **音频电平表（Audio Meter）**：实时显示多通道音频电平，包含当前值、峰值保持、削波指示器，支持水平/垂直方向
2. **响度表（Loudness Meter）**：遵循广播级响度标准的监视器，支持瞬时响度（Momentary）、短时响度（Short-Term）、长期响度（Long-Term）、响度范围（Loudness Range）和真峰值（True Peak）等指标
3. **可拖拽重排的 TileView**：支持通过拖拽操作重排音频指标的显示顺序
4. **完全可定制的样式系统**：所有控件均支持通过 Style 结构体自定义颜色、尺寸、字体等外观

该插件的 `AudioWidgetsCore` 模块被设计为同时在 Runtime 和 Program（UnrealInsights）中可用，主要用于 Insights 的音频分析视图。

## 使用场景

- 你在制作音频混音界面，需要专业的音量电平表 → 使用 `SAudioMeterWidget`
- 你在开发广播/影视工具，需要 EBU R128 标准的响度监视 → 使用 `FLoudnessMeterWidgetView`
- 你在 Unreal Insights 中添加音频分析面板 → 使用 `AudioWidgetsCore` 模块
- 你需要用户可自定义排序的音频指标列表 → 使用 `SDragReorderableTileView`
- 你在编辑器中构建音频编辑工具面板 → 使用 `AudioWidgetsEditor` 模块

## 蓝图用法

AudioWidgets 的核心控件是 Slate 级别的（`SAudioMeterWidget`、`FLoudnessMeterWidgetView`），但提供了 `BlueprintType` 的数据结构供蓝图使用。

### 核心数据结构

| 结构体 | 说明 | 所在模块 |
|---|---|---|
| `FAudioMeterChannelInfo` | 单通道音频电平数据（值、峰值、削波值） | `AudioWidgetsCore` |
| `FAudioMeterWidgetStyle` | 电平表完整外观样式（图片、尺寸、刻度、字体等） | `AudioWidgetsCore` |
| `FAudioMeterDefaultColorWidgetStyle` | 电平表默认颜色方案 | `AudioWidgetsCore` |
| `FLoudnessMeterSettings` | 响度表配置（刻度范围、目标值、显示选项等） | `AudioWidgetsCore` |
| `FLoudnessMeterDisplayOptions` | 单个响度指标的显示控制（显示数值/显示表/保持最大值） | `AudioWidgetsCore` |

### FAudioMeterChannelInfo 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `MeterValue` | `float` | 当前电平值 |
| `PeakValue` | `float` | 峰值 |
| `ClippingValue` | `float` | 削波值 |
| `MeterValueBarStart` | `TOptional<float>` | 电平条起始值（默认从最小值开始） |

### 使用示例（蓝图描述）

1. **获取音频数据**：通过 `AudioSynesthesia` 插件或其他音频分析源获取通道电平数据
2. **构建 FAudioMeterChannelInfo 数组**：为每个音频通道创建一个 `FAudioMeterChannelInfo`，设置 `MeterValue`、`PeakValue`、`ClippingValue`
3. **传入电平表控件**：将数组绑定到电平表控件的 `MeterChannelInfo` 属性
4. **响应式更新**：通过 ActiveTimer 机制，控件会自动请求刷新最新的通道数据

## C++ 用法

### 头文件引入

```cpp
// 电平表控件
#include "SAudioMeterWidget.h"
#include "AudioMeterChannelInfo.h"
#include "AudioMeterWidgetStyle.h"

// 响度表控件
#include "LoudnessMeterWidgetView.h"
#include "LoudnessMeterSettings.h"

// 可拖拽重排 TileView
#include "SDragReorderableTileView.h"
```

### 基本用法 —— 创建电平表

创建一个基本的音频电平表控件，显示立体声通道的实时电平：

```cpp
// 来源: Public/SAudioMeterWidget.h
// 创建电平表数据
TArray<FAudioMeterChannelInfo> ChannelInfo;
ChannelInfo.Add({ /*MeterValue=*/0.5f, /*PeakValue=*/0.7f, /*ClippingValue=*/1.0f });
ChannelInfo.Add({ /*MeterValue=*/0.3f, /*PeakValue=*/0.6f, /*ClippingValue=*/1.0f });

// 创建电平表控件
TSharedRef<SAudioMeterWidget> MeterWidget =
    SNew(SAudioMeterWidget)
    .Orientation(EOrient_Horizontal)
    .BackgroundColor(FLinearColor::Black)
    .MeterValueColor(FLinearColor::Green)
    .MeterPeakColor(FLinearColor::Yellow)
    .MeterClippingColor(FLinearColor::Red)
    .MeterChannelInfo_Lambda([ChannelInfo]() { return ChannelInfo; });
```

### 基本用法 —— 创建响度表

```cpp
// 来源: Public/LoudnessMeterWidgetView.h
// 创建响度表视图
FLoudnessMeterWidgetView LoudnessMeterView;

// 配置刻度参数
FLoudnessMeterWidgetView::FLoudnessScaleParams ScaleParams;
ScaleParams.Range = 60;
ScaleParams.Offset = 0;
ScaleParams.Target = -23;          // EBU R128 标准目标
ScaleParams.TruePeakLimit = -1.0f; // 真峰值限制 (dBTP)
LoudnessMeterView.InitLoudnessScale(ScaleParams);

// 添加响度指标
FLoudnessMeterWidgetView::FLoudnessMetric MomentaryMetric;
MomentaryMetric.Name = FName("Momentary");
MomentaryMetric.DisplayName = LOCTEXT("Momentary", "M");
MomentaryMetric.MeterMetric = EAudioMeterMetric::Loudness;
MomentaryMetric.Value = /* 绑定到瞬时响度数据源 */;
MomentaryMetric.bShowMeter = true;
MomentaryMetric.Color = FLinearColor::Green;
LoudnessMeterView.AddLoudnessMetric(MomentaryMetric);

// 生成控件
TSharedRef<SWidget> Widget = LoudnessMeterView.MakeWidget();
```

### 进阶用法 —— 自定义样式

```cpp
// 来源: Public/AudioMeterWidgetStyle.h
// 完全自定义电平表外观
FAudioMeterWidgetStyle CustomStyle;
CustomStyle.MeterSize = FVector2D(400.0f, 30.0f);
CustomStyle.MeterPadding = FVector2D(15.0f, 8.0f);
CustomStyle.ValueRangeDb = FVector2D(-60.0f, 0.0f);
CustomStyle.bShowScale = true;
CustomStyle.bScaleSide = true;
CustomStyle.DecibelsPerHash = 6;
CustomStyle.PeakValueWidth = 3.0f;
CustomStyle.ClippingValueWidth = 3.0f;
CustomStyle.SetFont(FSlateFontInfo(
    FPaths::EngineContentDir() / TEXT("Slate/Fonts/Roboto-Bold.ttf"), 10));

// 使用自定义样式创建控件
TSharedRef<SAudioMeterWidget> StyledMeter =
    SNew(SAudioMeterWidget)
    .Style(&CustomStyle)
    .MeterChannelInfo(MyChannelInfoAttribute);
```

### 进阶用法 —— 可拖拽重排的 TileView

```cpp
// 来源: Private/SDragReorderableTileView.h
// 继承 SDragReorderableTileView 并实现拖拽操作创建
// 需要实现纯虚函数 CreateDragDropOperation()
// 需要提供 FOnSetShowItem 和 FOnReorderItems 委托

// FOnSetShowItem: 控制项目的显示/隐藏
// FOnReorderItems: 处理项目重排逻辑
// 支持跨 TileView 拖拽（从一个 TileView 拖到另一个）
// 空 TileView 可接收拖拽项
```

## Demo 示例

### 最小电平表控件示例

```cpp
// MyAudioMeterWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "SAudioMeterWidget.h"
#include "AudioMeterChannelInfo.h"

class SMyAudioMeterWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyAudioMeterWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs)
    {
        // 创建一个水平方向的立体声电平表
        ChildSlot
        [
            SNew(SAudioMeterWidget)
            .Orientation(Orient_Horizontal)
            .BackgroundColor(FLinearColor(0.02f, 0.02f, 0.02f))
            .MeterValueColor(FLinearColor(0.1f, 0.8f, 0.1f))
            .MeterPeakColor(FLinearColor(1.0f, 0.9f, 0.0f))
            .MeterClippingColor(FLinearColor::Red)
            .MeterChannelInfo(this, &SMyAudioMeterWidget::GetChannelInfo)
        ];

        // 注册活跃定时器以每帧刷新
        RegisterActiveTimer(0.0f,
            FWidgetActiveTimerDelegate::CreateSP(
                this, &SMyAudioMeterWidget::OnActiveTimer));
    }

private:
    TArray<FAudioMeterChannelInfo> GetChannelInfo() const
    {
        // 这里替换为实际的音频数据源
        return CachedChannelInfo;
    }

    EActiveTimerReturnType OnActiveTimer(double InCurrentTime, float InDeltaTime)
    {
        // 从音频系统获取最新数据并缓存
        // CachedChannelInfo = AudioSubsystem->GetMeterData();
        return EActiveTimerReturnType::Continue;
    }

    TArray<FAudioMeterChannelInfo> CachedChannelInfo;
};
```

## 模块依赖

从插件源码分析，`AudioWidgetsCore` 模块的 `SupportedPrograms` 为 `UnrealInsights`，表示核心模块专门针对 Insights 程序优化。

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 音频分析数据源（插件级依赖，提供响度/频谱等分析能力） |
| `Slate` | Slate 控件框架（电平表、TileView 等基础 UI） |

其他标准依赖（Core, CoreUObject, Engine, SlateCore 等）已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-05-12 | `fcaaf385` | [AudioWidgets] Loudness Meters: context menu polish. Reorganize settings into Loudness Scale, Reference... | 响度表上下文菜单优化，重新组织设置分类 |
| 2026-05-12 | `d2e95dfd` | [AudioWidgets] Loudness Meter: add max value indicator line on meters that support max value. | 响度表支持最大值的指标添加最大值指示线 |
| 2026-05-12 | `ba019a16` | [AudioWidgets] Audio Meter: implemented ClippingValue draw in SAudioMeterWidget. | 音频电平表实现削波值绘制功能 |
| 2026-05-12 | `bd1d2d5c` | [AudioWidgets] [Audio Insights] Loudness Meters: set different default colors for Range and True Pea... | 响度表为范围和真峰值指标设置不同的默认颜色 |

### 维护评价

**活跃维护中** ✅

- 创建于 2020 年 12 月，至今约 6 年历史
- **最近更新非常活跃**：2026 年 5 月 12-13 日有多次密集提交，包含功能增强（削波值绘制、最大值指示线）、UI 优化（上下文菜单重组）和编译修复
- 持续为 Unreal Insights 的音频分析功能提供 UI 支持
- 插件从最初的实验性状态（首个 commit 描述为 "Checkpoint: Experimental Audio Widget Plugin"）已成长为成熟稳定的音频控件库
- 有明确的模块化设计（Core/Runtime/Editor 三层分离）
- **推荐使用**：如果你的项目需要专业的音频电平表或响度监视功能，这是一个成熟且活跃维护的选择

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets)
- [AudioWidgetsCore 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets/Source/AudioWidgetsCore)
- [AudioWidgets 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets/Source/AudioWidgets)
- [AudioWidgetsEditor 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets/Source/AudioWidgetsEditor)
- [AudioSynesthesia 插件（依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia)