# Wave Table

> Default implementation of WaveTable support within the Unreal Audio Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 波表 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产与工具） |
| 模块 | `WaveTable` (Runtime), `WaveTableEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2022-06-15 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WaveTable) | |

## 用途

该插件为 Unreal 音频引擎提供**波表 (WaveTable)** 的核心功能实现。它解决的核心问题是：在音频合成、效果处理（如调制、滤波器自动化）以及更广泛的信号处理场景中，需要一种高效、统一的方式来定义、存储、采样和编辑基于时间或输入值变化的参数曲线（波表）。

插件从早期的 **Modulation** 插件中迁移和分离而来，旨在将波表功能模块化，使其不仅服务于调制系统，还能被其他音频资产（如 MetaSound 节点）和工具（如波表编辑器）所复用。

**核心功能包括：**
*   **波表数据结构 (`FWaveTableData`)**：提供存储和操作波表数据（浮点数组）的底层结构。
*   **波表银行资产 (`UWaveTableBank`)**：一种资产类型，用于管理和存储多个波表变换 (`FWaveTableTransform`) 配置。
*   **波表导入与采样 (`WaveTableImporter`， 从提交信息推断)**：提供从文件加载音频数据并将其作为波表源进行采样的能力。
*   **曲线编辑器集成**：提供自定义的曲线模型 (`FWaveTableCurveModel`) 和堆叠视图 (`SViewStacked`)，用于在编辑器中直观地绘制和预览波表形状。

## 使用场景

-   **音频调制与自动化**：你需要为声音的音高、音量、滤波器截止频率等参数创建复杂的随时间变化的曲线。
-   **自定义音频效果**：在 MetaSound 或自定义音频处理链中，你需要一个可由曲线驱动的 LFO (低频振荡器) 或包络生成器。
-   **视觉特效同步**：需要将音频事件（如鼓点）与视觉参数（如粒子发射强度）通过波表曲线进行精确同步。
-   **游戏逻辑驱动**：使用波表来平滑地控制游戏对象的移动、缩放或其他属性，实现类似缓动函数的效果。

## 蓝图用法

由于插件主要为底层音频引擎和编辑器提供支持，其大部分核心功能以 C++ API 形式暴露。在蓝图中，你主要通过操作 **波表银行 (`UWaveTableBank`)** 资产来使用该插件。运行时模块中可能提供蓝图可调用的节点，用于在运行时评估波表数据（具体函数需查阅运行时模块头文件）。

### 核心概念

| 概念 | 说明 |
|---|---|
| `UWaveTableBank` | 资产，包含一组波表变换配置，每个配置定义了一个波表的形状和参数。 |
| `FWaveTableTransform` | 结构体，定义单个波表的变换规则，包括源曲线、采样模式、淡入淡出等。 |

## C++ 用法

### 头文件引入

```cpp
// 使用运行时波表数据功能
#include "WaveTable.h"

// 使用波表银行资产
#include "WaveTableBank.h"
```

### 基本用法：操作波表数据

`FWaveTableData` 是操作波表的核心类。以下示例展示如何创建、填充并读取一个简单的波表。

**来源：基于 `Public/WaveTableData.h` 推断的核心API用法**

```cpp
#include "WaveTable.h"

void Example_SimpleWaveTable()
{
    using namespace WaveTable;

    // 1. 创建一个波表数据实例 (示例：8个采样点)
    FWaveTableData MyTable(EWaveTableResolution::Eight);

    // 2. 获取可修改的数据数组引用
    TArray<float>& TableValues = MyTable.GetMutableValues();

    // 3. 填充数据 (创建一个简单的线性递增波表)
    const int32 NumSamples = TableValues.Num();
    for (int32 i = 0; i < NumSamples; ++i)
    {
        TableValues[i] = static_cast<float>(i) / static_cast<float>(NumSamples - 1);
    }

    // 4. 读取并评估波表数据
    // 假设我们要在参数 `ParamValue` = 0.5f 处进行采样
    float SampleInput = 0.5f;
    float EvaluatedValue = MyTable.Eval(SampleInput);
    // EvaluatedValue 应该约为 0.5f (取决于具体插值模式)
}

void Example_UseBankAsset()
{
    // 假设已经加载或创建了一个 UWaveTableBank 资产指针 `WaveTableBank`
    UWaveTableBank* WaveTableBank = ...; // 获取资产

    // 遍历资产中的每个波表变换配置并进行处理
    for (const FWaveTableTransform& Transform : WaveTableBank->Transforms)
    {
        // 可以根据 Transform 的设置（如曲线类型、采样率等）来处理或生成波表
        // 具体操作取决于你的音频处理需求
    }
}
```

### 进阶用法：结合插值与采样模式

波表支持不同的采样模式和插值方式，以实现平滑或阶梯状的波形。

```cpp
#include "WaveTable.h"

void Example_AdvancedSampling()
{
    using namespace WaveTable;

    // 创建一个固定分辨率的波表
    FWaveTableData MyTable(EWaveTableResolution::ThirtyTwo);

    // ... 填充数据 ...

    // 设置采样模式和插值模式（通常通过 FWaveTableTransform 或波表资产配置）
    // FWaveTableTransform Transform;
    // Transform.SamplingMode = EWaveTableSamplingMode::FixedResolution;
    // Transform.InterpolationMode = EWaveTableInterpolation::Linear;

    // 在评估时，不同的设置会影响结果
    float Input = 0.123f;
    float Value = MyTable.Eval(Input); // 根据预设的插值模式计算
}
```

## Demo 示例

一个最小化的 C++ 示例，演示如何创建一个 `WaveTableData` 对象并执行基本操作。

**WaveTableDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "WaveTable.h" // 包含波表核心头文件

UCLASS(Blueprintable)
class UWaveTableDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "WaveTable Demo")
    void CreateAndSampleWaveTable();

private:
    TUniquePtr<WaveTable::FWaveTableData> DemoTable;
};
```

**WaveTableDemo.cpp**
```cpp
#include "WaveTableDemo.h"

void UWaveTableDemo::CreateAndSampleWaveTable()
{
    using namespace WaveTable;

    // 创建一个包含16个采样点的波表
    DemoTable = MakeUnique<FWaveTableData>(EWaveTableResolution::Sixteen);
    TArray<float>& Values = DemoTable->GetMutableValues();

    // 生成一个正弦波形状 (简化)
    for (int32 i = 0; i < Values.Num(); ++i)
    {
        float NormalizedIndex = static_cast<float>(i) / static_cast<float>(Values.Num() - 1);
        Values[i] = FMath::Sin(NormalizedIndex * 2.0f * PI); // [-1, 1] 范围的正弦波
    }

    // 评估几个点
    if (DemoTable.IsValid())
    {
        float EvalPoint = 0.25f;
        float Result = DemoTable->Eval(EvalPoint);
        UE_LOG(LogTemp, Log, TEXT("WaveTable evaluated at %.2f: %.4f"), EvalPoint, Result);

        EvalPoint = 0.75f;
        Result = DemoTable->Eval(EvalPoint);
        UE_LOG(LogTemp, Log, TEXT("WaveTable evaluated at %.2f: %.4f"), EvalPoint, Result);
    }
}
```

## 模块依赖

从模块结构和常见音频插件模式推断，依赖如下：

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 提供底层音频信号处理工具和算法。 |
| `SlateCore`, `Slate`, `EditorWidgets` | (Editor 模块) 用于构建自定义的曲线编辑器 UI。 |
| `AssetTools`, `ContentBrowser` | (Editor 模块) 用于集成资产创建、操作和内容浏览器显示。 |
| `GraphEditor` | (Editor 模块) 可能用于未来与蓝图或 MetaSound 图表的集成。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 调整了内容浏览器中“添加”菜单的音频相关菜单项布局。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件中的日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-02-02 | `9dc10c15` | Unclamp Modulation Patches | 与调制补丁相关的改动，可能影响波表在调制系统中的使用。 |
| 2025-07-12 | `b8bdcd83` | Run UnrealCodeFixup to fix dll storage | 进行代码修复以修正 DLL 导出相关问题。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 为源文件添加内联生成宏，属于代码构建优化。 |

### 维护评价

**评价：实验性功能，维护不活跃**

*   **创建时间**：该插件于 2022 年中创建，作为功能从 Modulation 插件分离的“检查点”。
*   **近期更新**：最近的提交（2025-2026 年）主要是**编译修复、代码规范化和菜单 UI 微调**，没有任何实质性功能增强或重大重构。这表明该插件处于“仅维护”状态，以保证其能随引擎编译。
*   **实验性状态**：`.uplugin` 中 `IsBetaVersion: true` 且 `EnabledByDefault: false`，明确表明这是一个未完成、可能发生变化的实验性功能。它的 API 和资产格式在正式版中可能会有破坏性改动。
*   **活跃度**：自首次提交后，没有持续的功能开发记录。它更像是一个为特定项目（或内部系统如 MetaSound）提取的基础模块，而非一个活跃发展中的独立插件。
*   **推荐使用**：**仅推荐给对 Unreal 音频引擎内部结构有深入了解，并且需要底层波表支持作为自定义工具或插件基石的开发者。** 对于普通游戏开发者，应优先使用 Unreal 现成的音频系统（如 MetaSound），并关注其官方文档，而非直接依赖此实验性插件。使用前请务必在版本控制下进行，并做好应对 API 变更的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WaveTable)
-   [官方文档]() (无)
-   [测试用例]() (未在提供的信息中发现)