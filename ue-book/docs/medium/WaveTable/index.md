# Wave Tables

> Default implementation of WaveTable support within the Unreal Audio Engine.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（曲线编辑器视图、资产工厂） |
| 模块 | `WaveTable` (Runtime), `WaveTableEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WaveTable) | |

## 用途

WaveTable 插件提供了一套完整的波表（WaveTable）数据框架，用于在 UE5 音频引擎中存储、采样、变换和编辑波形数据。

波表是一种经典的音频合成技术：将一个完整周期的波形预计算并存储在数组中，运行时通过查表和插值来生成音频信号或控制曲线，比实时计算三角函数等数学运算要高效得多。

这个插件解决的核心问题是：**为 MetaSound 等音频系统提供标准化的波表数据资产和采样工具**。它支持：

- **多种曲线类型生成波表**：线性、指数、对数、正弦、自定义曲线、音频文件导入
- **多种位深度**：16-bit PCM 和 32-bit IEEE Float，可在存储空间和精度之间权衡
- **灵活的采样模式**：固定分辨率（适合振荡器/包络）和固定采样率（适合采样器/粒子化）
- **运行时采样器**：支持频率调制、相位调制、同步触发、one-shot/循环模式
- **音频代理（Audio Proxy）**：支持音频线程安全的数据传递

## 使用场景

- 你在 MetaSound 中需要自定义振荡器波形 → 创建 WaveTableBank 资产，选择曲线类型（正弦、锯齿、自定义等）
- 你想用音频文件作为波表源（采样器用途）→ 设置曲线类型为 "File"，导入 .wav/.ogg/.flac 等文件
- 你需要精确控制包络曲线 → 在 WaveTableBank 中设置 Unipolar 模式，用曲线编辑器绘制包络
- 你需要在音频线程安全地使用波表数据 → 通过 `FWaveTableBankAssetProxy` 代理访问
- 你想在运行时动态采样波表 → 使用 `FWaveTableSampler` 进行带调制的实时采样

## 蓝图用法

此插件主要面向 C++ 和 MetaSound 节点层，**没有暴露 `BlueprintCallable` 函数**。`FWaveTableTransform` 结构体的 `Curve`、`Scalar`、`CurveShared` 属性标记为 `BlueprintReadWrite`，可以在蓝图中作为结构体属性读写，但实际的波表创建和采样操作在 C++ 层完成。

### 可访问的蓝图属性

| 属性 | 类型 | 所在结构体 | 说明 |
|---|---|---|---|
| `Curve` | `EWaveTableCurve` | `FWaveTableTransform` | 曲线类型 |
| `Scalar` | `float` | `FWaveTableTransform` | 指数/对数曲线的缩放因子 |
| `CurveShared` | `UCurveFloat*` | `FWaveTableTransform` | 共享曲线资产引用 |

### 编辑器用法

在编辑器中，WaveTableBank 资产提供了一个可视化曲线编辑器：

1. 右键 Content Browser → Audio → Wave Table Bank
2. 打开资产，设置采样模式（FixedResolution / FixedSampleRate）
3. 在 Entries 数组中添加条目，每个条目选择曲线类型
4. 曲线编辑器实时显示波形预览

## C++ 用法

### 头文件引入

```cpp
#include "WaveTable.h"               // 核心数据结构
#include "WaveTableBank.h"           // 波表银行资产
#include "WaveTableTransform.h"      // 曲线变换
#include "WaveTableSampler.h"        // 运行时采样器
#include "WaveTableSettings.h"       // 文件导入设置
#include "WaveTableImporter.h"       // 文件导入处理
```

### 基本用法：创建 WaveTableData

```cpp
// 来源: WaveTable.h - FWaveTableData

// 创建 16-bit PCM 格式的波表数据
FWaveTableData TableData(EWaveTableBitDepth::PCM_16);

// 从 float 数组创建
TArray<float> Samples = { 0.0f, 0.5f, 1.0f, 0.5f, 0.0f, -0.5f, -1.0f, -0.5f };
constexpr bool bIsLoop = true;
TableData.SetData(Samples, bIsLoop);
TableData.SetFinalValue(0.0f); // 循环回第一个值

// 获取数据视图
TArrayView<const float> DataView;
if (TableData.GetDataView(DataView))
{
    // 安全访问采样数据
}

// 位深度转换
TableData.SetBitDepth(EWaveTableBitDepth::IEEE_Float);
```

### 基本用法：运行时采样

```cpp
// 来源: WaveTableSampler.h - FWaveTableSampler

// 创建采样器并配置
WaveTable::FWaveTableSampler Sampler;
Sampler.SetFreq(1.0f);   // 1x 速率读取整张表
Sampler.SetPhase(0.0f);  // 起始相位
Sampler.SetInterpolationMode(WaveTable::FWaveTableSampler::EInterpolationMode::Cubic);

// 单样本采样
float Sample = 0.0f;
Sampler.Process(TableData, Sample);

// 批量采样到输出缓冲区
TArray<float> OutputBuffer;
OutputBuffer.SetNum(512);
Sampler.Process(TableData, MakeArrayView(OutputBuffer));
```

### 进阶用法：带调制的采样

```cpp
// 来源: WaveTableSampler.cpp - Process 带调制参数版本

WaveTable::FWaveTableSampler Sampler;
Sampler.SetFreq(2.0f);  // 2 倍频率

// 频率调制缓冲区（每个样本的频率倍率）
TArray<float> FreqMod;
FreqMod.SetNum(512);
for (int32 i = 0; i < 512; ++i)
{
    FreqMod[i] = 1.0f + 0.5f * FMath::Sin(2.0f * PI * i / 512.0f);
}

// 相位调制缓冲区
TArray<float> PhaseMod;
PhaseMod.SetNumZeroed(512);

// 同步触发缓冲区（1.0 = 重置相位）
TArray<float> SyncTriggers;
SyncTriggers.SetNumZeroed(512);

// 输出缓冲区
TArray<float> Output;
Output.SetNum(512);

// 带调制的批量采样
Sampler.Process(
    TableData,
    MakeArrayView(FreqMod),
    MakeArrayView(PhaseMod),
    MakeArrayView(SyncTriggers),
    MakeArrayView(Output)
);
```

### 进阶用法：音频文件导入为波表

```cpp
// 来源: WaveTableImporter.h, WaveTableSettings.h

// 配置导入设置
FWaveTableSettings Settings;
Settings.FilePath.FilePath = TEXT("/path/to/audio.wav");
Settings.ChannelIndex = 0;
Settings.Phase = 0.0f;
Settings.bNormalize = true;
Settings.FadeIn = 0.01f;   // 1% fade in
Settings.FadeOut = 0.01f;  // 1% fade out

// 需要先导入文件数据到 Settings.SourceData（编辑器自动处理）

// 创建导入器并处理
WaveTable::FImporter Importer(Settings, true); // true = bipolar
FWaveTableData OutputData(EWaveTableBitDepth::IEEE_Float);
OutputData.SetNum(256); // 设置输出分辨率
Importer.Process(OutputData);
```

## Demo 示例

### 完整的波表振荡器示例

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "WaveTable",
    "Core",
    "CoreUObject",
    "Engine"
});
```

**WaveTableOscillator.h**：
```cpp
#pragma once

#include "WaveTable.h"
#include "WaveTableSampler.h"

// 一个简单的波表振荡器，从 WaveTableBank 资产中读取数据
class FSimpleWaveTableOscillator
{
public:
    void Init(const FWaveTableData& InTableData, float InFrequency, float InSampleRate);
    void Process(TArrayView<float> OutBuffer);

private:
    WaveTable::FWaveTableSampler Sampler;
    float SampleRate = 48000.0f;
};
```

**WaveTableOscillator.cpp**：
```cpp
#include "WaveTableOscillator.h"

void FSimpleWaveTableOscillator::Init(
    const FWaveTableData& InTableData,
    float InFrequency,
    float InSampleRate)
{
    SampleRate = InSampleRate;

    WaveTable::FWaveTableSampler::FSettings Settings;
    Settings.Freq = InFrequency / SampleRate; // 归一化频率
    Settings.InterpolationMode = WaveTable::FWaveTableSampler::EInterpolationMode::Cubic;
    Settings.bOneShot = false; // 循环播放

    Sampler = WaveTable::FWaveTableSampler(MoveTemp(Settings));
}

void FSimpleWaveTableOscillator::Process(TArrayView<float> OutBuffer)
{
    // 从波表数据采样到输出缓冲区
    Sampler.Process(
        CachedTableData,
        OutBuffer
    );
}
```

## 模块依赖

### WaveTable (Runtime)

| 模块 | 用途 |
|---|---|
| `AudioExtensions` | 音频代理数据工厂接口（IAudioProxyDataFactory） |
| `Core` | 基础类型、数学运算 |
| `CoreUObject` | UObject 序列化、USTRUCT 支持 |
| `Engine` | 资产基础框架 |
| `SignalProcessing` | 浮点数组数学运算（私有依赖） |

### WaveTableEditor (Editor)

| 模块 | 用途 |
|---|---|
| `AssetTools` | 资产创建和管理 |
| `SlateCore` | 编辑器 UI 框架 |
| `CurveEditor` | 曲线编辑器集成（私有依赖） |
| `AudioEditor` | 音频资产编辑器基础（私有依赖） |
| `UnrealEd` | 编辑器框架（私有依赖） |
| `WaveTable` | Runtime 模块本体（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-12 | `b8bdcd83a4fa` | Run UnrealCodeFixup to fix dll storage | 构建工具自动化修复 DLL 导出标记，无功能变化 |
| 2025-07-10 | `9803c443cfab` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 代码生成优化，无功能变化 |
| 2025-06-11 | `e0d87df85d89` | Replace some usages of FORCEINLINE with inline in Audio modules | 代码规范统一，无功能变化 |

最后的功能性更新：

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-11-14 | `269a01d279f9` | Modulation Swins | 修复调制相关的多个 bug（UE-198391 等） |
| 2023-11-09 | `4e1660dcdaa6` | Fix for calculation of final WaveTable value | 修复浮点精度损失导致的 FinalValue 计算错误 |
| 2023-10-25 | `5a79dc98ee3c` | WaveTable Bank Evaluate Node | 新增 MetaSound 中的 WaveTable Bank 评估节点 |

### 维护评价

- **创建时间**：2022 年 6 月，约 4 年历史
- **最近功能性更新**：2023 年 11 月（约 2.5 年前）
- **近期更新**：2025 年更新均为构建工具自动化修复，无实质性功能变更
- **Beta 状态**：`IsBetaVersion=true`，`EnabledByDefault=false`，仍标记为实验性
- **API 变化**：5.3 版本经历了较大的 API 重构（引入多 bit depth 支持、FWaveTableData 替代旧的 TArray<float>），多个旧 API 标记为 Deprecated
- **活跃度**：维护不活跃，2 年以上没有实质性功能更新
- **推荐**：作为 MetaSound 生态的底层基础设施，功能稳定可用，但需注意 API 可能在未来版本继续变化。适合在 MetaSound 节点层面使用，直接在 C++ 层使用时注意关注 deprecation 警告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WaveTable)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 关联 DSP 模块：[SignalProcessing/WaveTableOsc](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/SignalProcessing/Public/DSP/WaveTableOsc.h)（基于波表的振荡器实现）
