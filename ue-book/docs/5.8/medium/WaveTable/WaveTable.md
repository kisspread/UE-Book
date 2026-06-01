# Wave Tables

> Default implementation of WaveTable support within the Unreal Audio Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 波表引擎 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WaveTable` (Runtime), `WaveTableEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WaveTable) | |

## 用途

WaveTable 插件为 Unreal Audio Engine 提供了一套完整的波表（WaveTable）支持。波表是一种用于音频合成、调制和效果处理的数据结构，它将音频波形或调制曲线存储为离散样本的数组，然后可以以不同速率和插值方式回放。

这个插件的核心目标是：
1.  提供通用的波表数据结构（`FWaveTableData`）和处理工具，支持多种位深（16位PCM和32位浮点）。
2.  实现一个可配置的波表采样器（`FWaveTableSampler`），用于从波表数据中高效地采样音频样本。
3.  支持从音频文件、曲线资产或自定义函数生成波表数据。
4.  提供波表资产（`UWaveTableBank`）的管理，用于批量存储和使用波表。

它最初是从Modulation插件迁移出来的，旨在为MetaSound节点、其他音频工具以及任何需要波表功能的系统提供一个独立且可扩展的基础。

## 使用场景

-   **音频合成**：在 MetaSound 中使用波表作为振荡器，生成丰富的音频波形。
-   **调制控制**：将波表用作LFO（低频振荡器），为参数（如音量、音高、滤波器截止频率）创建动态变化。
-   **包络生成**：利用波表创建自定义的ADSR（Attack, Decay, Sustain, Release）包络形状。
-   **采样器功能**：将音频文件导入为波表，并通过采样器以不同速度和音高播放。
-   **效果器设计**：在自定义音频效果中，使用波表作为查找表来处理信号。

## 蓝图用法

由于插件主要面向运行时和编辑器扩展，其核心数据结构（如 `FWaveTableData`）和设置类（如 `FWaveTableSettings`, `FWaveTableTransform`）多为 `USTRUCT`，可以在蓝图中作为变量使用和配置。但插件本身并未直接暴露大量蓝图可调用节点，其使用通常与 MetaSound 节点或其他音频系统深度集成。

### 核心类（蓝图中可配置的结构体）

| 类/结构体 | 说明 | 所在类 |
|---|---|---|
| `FWaveTableData` | 存储波表原始数据的核心结构体，支持16位和32位格式。 | `UWaveTableBank` 的内部数据 |
| `FWaveTableTransform` | 定义波表如何从曲线或文件生成，包含曲线类型、时长等设置。 | `FWaveTableBankEntry` 的成员 |
| `FWaveTableSettings` | 从音频文件导入波表时的具体设置（如文件路径、通道索引、相位、淡入淡出等）。 | `FWaveTableTransform` 的编辑器数据 |
| `UWaveTableBank` | 波表资产，存储一系列波表条目，是实际使用中创建和管理波表的主要资产。 | `UWaveTableBank` |

### 使用示例（蓝图描述）

1.  **创建波表资产**：在内容浏览器中右键 -> Audio -> Wave Table Bank 创建一个 `UWaveTableBank` 资产。
2.  **配置波表条目**：双击打开资产，设置 `SampleMode`（采样模式）、`Resolution`（分辨率）和 `bBipolar`（双极性）。
3.  **添加波表条目**：在 `Entries` 数组中添加元素。每个元素包含一个 `FWaveTableTransform`。
4.  **设置波表数据源**：在 `FWaveTableTransform` 中，选择 `Curve` 类型。例如：
    -   选择 `Linear` 生成线性斜坡。
    -   选择 `Sin` 生成正弦波。
    -   选择 `File` 并设置 `FilePath` 从音频文件导入。
5.  **在 MetaSound 中使用**：在 MetaSound 图表中，使用 `Wave Table Player` 或 `Wave Table Oscillator` 等节点，并将波表资产作为输入。

## C++ 用法

### 头文件引入

```cpp
#include "WaveTable.h"
#include "WaveTableSampler.h"
#include "WaveTableBank.h"
```

### 基本用法

1.  **创建和操作波表数据 (`FWaveTableData`)**

    ```cpp
    #include "WaveTable.h"
    
    void CreateSampleWaveTable()
    {
        // 创建一个基于正弦曲线的波表
        FWaveTableData SineTable;
        const int32 NumSamples = 256;
        SineTable.Reset(NumSamples);
        
        TArrayView<float> DataView;
        if (SineTable.GetDataView(DataView))
        {
            for (int32 i = 0; i < NumSamples; ++i)
            {
                // 生成一个周期的正弦波
                float Phase = static_cast<float>(i) / NumSamples;
                DataView[i] = FMath::Sin(Phase * 2.0f * PI);
            }
        }
        // 设置最终值（用于循环播放时的平滑过渡）
        SineTable.SetFinalValue(DataView[0]);
    }
    ```

2.  **使用采样器 (`FWaveTableSampler`) 从波表中获取样本**

    ```cpp
    #include "WaveTableSampler.h"
    #include "WaveTable.h"
    
    void SampleWaveTable(const FWaveTableData& InTableData)
    {
        // 配置采样器
        FWaveTableSampler::FSettings Settings;
        Settings.Freq = 440.0f / 48000.0f; // 440Hz @ 48kHz 采样率
        Settings.InterpolationMode = FWaveTableSampler::EInterpolationMode::Cubic;
        
        FWaveTableSampler Sampler(MoveTemp(Settings));
        
        // 采样1024个输出样本
        TArray<float> OutputBuffer;
        OutputBuffer.SetNum(1024);
        
        // 处理一整块数据
        Sampler.Process(InTableData, MakeArrayView(OutputBuffer));
        
        // 现在 OutputBuffer 中包含了从波表中采样出的音频信号
    }
    ```

    （来源：`Public/WaveTableSampler.h` 中 `FWaveTableSampler::Process` 的公共接口）

### 进阶用法

1.  **从音频文件导入波表 (`FImporter`)**

    ```cpp
    #include "WaveTableImporter.h"
    #include "WaveTableSettings.h"
    
    void ImportWaveTableFromFile()
    {
        FWaveTableSettings ImportSettings;
        ImportSettings.FilePath.FilePath = TEXT("/Game/Audio/my_sound.wav");
        ImportSettings.ChannelIndex = 0;
        ImportSettings.bNormalize = true;
        
        FWaveTableData ImportedData;
        WaveTable::FImporter Importer(ImportSettings, true /* bBipolar */);
        Importer.Process(ImportedData);
        
        // ImportedData 现在包含了从 my_sound.wav 文件中提取的波表数据
    }
    ```

    （来源：`Public/WaveTableImporter.h` 中 `FImporter` 的构造函数和 `Process` 方法）

2.  **使用波表资产 (`UWaveTableBank`) 和代理 (`FWaveTableBankAssetProxy`)**

    ```cpp
    #include "WaveTableBank.h"
    
    void UseWaveTableBank()
    {
        // 假设我们有一个 UWaveTableBank 资产指针
        UWaveTableBank* Bank = LoadObject<UWaveTableBank>(nullptr, TEXT("/Game/Audio/MyWaveTableBank"));
        if (Bank)
        {
            // 创建音频线程代理（用于安全地在音频线程使用数据）
            Audio::FProxyDataInitParams InitParams;
            TSharedPtr<FWaveTableBankAssetProxy> Proxy = Bank->CreateProxyData(InitParams);
            
            if (Proxy.IsValid())
            {
                EWaveTableSamplingMode SampleMode = Proxy->GetSampleMode();
                int32 SampleRate = Proxy->GetSampleRate();
                bool bBipolar = Proxy->IsBipolar();
                
                // 获取波表数据数组
                const TArray<FWaveTableData>& WaveTables = Proxy->GetWaveTableData();
                // 在音频线程上使用 WaveTables 数据...
            }
        }
    }
    ```

    （来源：`Public/WaveTableBank.h` 中 `FWaveTableBankAssetProxy` 的公共接口）

## Demo 示例

一个简单的示例：创建一个波表资产，生成一个自定义的“Attack-Decay”包络，并在控制台打印其采样值。

**WaveTableDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "WaveTableDemo.generated.h"

UCLASS()
class UWaveTableDemo : public UObject
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "WaveTable Demo")
	void GenerateAndSampleEnvelope();
};
```

**WaveTableDemo.cpp**
```cpp
#include "WaveTableDemo.h"
#include "WaveTableData.h"
#include "WaveTableSampler.h"

void UWaveTableDemo::GenerateAndSampleEnvelope()
{
	// 1. 创建一个波表数据容器
	FWaveTableData EnvelopeTable;
	const int32 NumSamples = 128;
	EnvelopeTable.Reset(NumSamples);

	// 2. 填充一个简单的Attack-Decay包络
	TArrayView<float> Samples;
	if (EnvelopeTable.GetDataView(Samples))
	{
		for (int32 i = 0; i < NumSamples; ++i)
		{
			float Progress = static_cast<float>(i) / (NumSamples - 1);
			if (Progress < 0.1f) // 10% Attack
			{
				Samples[i] = Progress / 0.1f;
			}
			else // 90% Decay
			{
				Samples[i] = 1.0f - ((Progress - 0.1f) / 0.9f);
			}
		}
	}

	// 3. 使用采样器以一次播放模式采样它
	FWaveTableSampler::FSettings SamplerSettings;
	SamplerSettings.bOneShot = true; // 一次播放，不循环
	SamplerSettings.Freq = 1.0f;     // 频率不影响，因为我们只采样一次整个表

	FWaveTableSampler Sampler(MoveTemp(SamplerSettings));

	// 4. 采样20个点（模拟播放进度）
	TArray<float> OutputSamples;
	OutputSamples.SetNum(20);
	for (int32 i = 0; i < 20; ++i)
	{
		float SampleValue;
		float NormalizedIndex = static_cast<float>(i) / 19.0f; // [0, 1] 范围内的索引
		Sampler.Process(EnvelopeTable, SampleValue, FWaveTableSampler::ESingleSampleMode::Hold);
		OutputSamples[i] = SampleValue;
	}

	// 5. 打印结果
	UE_LOG(LogTemp, Log, TEXT("Generated Envelope Samples:"));
	for (int32 i = 0; i < OutputSamples.Num(); ++i)
	{
		UE_LOG(LogTemp, Log, TEXT("[%02d]: %.3f"), i, OutputSamples[i]);
	}
}
```

## 模块依赖

从模块类型和插件功能推断，使用此插件需要以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 插件与音频引擎的核心混音器交互。 |
| `SignalProcessing` | 采样器内部可能使用信号处理工具。 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单项，可能影响波表资产的创建入口。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，提升日志性能。 |
| 2026-02-02 | `9dc10c15` | Unclamp Modulation Patches | 调整调制补丁的参数范围限制。 |
| 2025-07-12 | `b8bdcd83` | Run UnrealCodeFixup to fix dll storage | 修复 DLL 存储相关的编译问题。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME ... | 优化生成代码，提升编译和运行时性能。 |

### 维护评价

WaveTable 插件自 2022 年创建以来，保持持续更新，最近一次更新在 2026 年 4 月，表明它仍在**活跃维护**中。更新内容涉及代码优化、编译修复和功能微调，这与 Epic Games 对音频引擎的持续改进一致。

尽管 `.uplugin` 文件标记为 `IsBetaVersion: true` 且默认不启用，但从其代码成熟度和与 MetaSound 的深度集成来看，它已经是一个相当稳定的组件。它主要作为 MetaSound 等高级音频系统的底层支持存在，对于需要波表功能的开发者来说是**推荐使用**的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WaveTable)
- 官方文档（无）