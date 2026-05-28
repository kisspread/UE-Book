# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 实验性元声音 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

这个插件是 MetaSound 系统的实验性扩展，用于在正式发布前测试新的音频功能。其核心是引入了**通道无关类型 (Channel Agnostic Types, CAT)** 系统。传统的 MetaSound 节点通常需要明确指定音频通道格式（如 Mono, Stereo），而 CAT 允许节点在运行时动态处理不同通道格式的音频数据，使得构建自适应多通道音频图成为可能。插件包含了用于 CAT 格式转换、混合、声像平移等功能的实验性节点，并提供了示例节点供开发者参考。

## 使用场景

- 你的 MetaSound 图需要处理来自不同源（可能是单声道或立体声）的音频信号，并希望图能自动适配输出通道格式。
- 你正在尝试构建一个更灵活、可重用的音频处理逻辑，不希望为每种可能的通道配置都创建单独的节点或分支。
- 你想提前体验和测试 MetaSound 团队正在开发的新节点功能。

## 蓝图用法

该插件主要通过其提供的实验性 MetaSound 节点在编辑器中使用。这些节点带有可配置的属性，通常通过节点细节面板进行设置。

### 核心配置类与节点

| 配置结构 | 说明 | 关键可配置属性 |
|---|---|---|
| `FMetaSoundCatCastingNodeConfiguration` | **CAT 格式转换节点**的配置。用于将输入的 CAT 信号转换为目标格式。 | `ToType` (目标格式), `TranscodeMethod` (转换方法), `MixMethod` (混音方法) |
| `FMetaSoundCatMixingNodeConfiguration` | **CAT 混音器节点**的配置。用于混合多个 CAT 输入信号。 | `FormatChoosingMethod` (输出格式选择策略), `NumInputs` (输入数量), `CatCastingMethod` |
| `FMetaSoundCatPannerNodeConfiguration` | **CAT 声像平移节点**的配置。用于将 CAT 信号平移到指定的方位角离散通道格式。 | `PanToType` (目标通道格式), `PanningMethod` (平移算法) |
| `FMetaSoundExperimentalExampleNodeConfiguration` | **示例节点**的配置，展示了动态接口和自定义操作器数据的基本用法。 | `String`, `NumInputs`, `NumOutputs` |

### 使用示例（蓝图描述）

1.  **启用插件**：在编辑器中的“插件”面板里找到 “Metasounds Experimental” 并启用它，然后重启编辑器。
2.  **查找实验性节点**：在 MetaSound 编辑器中右键点击搜索节点，你将能找到如 “CAT Casting”、“CAT Mixer”、“CAT Panner” 等实验性节点。
3.  **配置节点**：将节点添加到图表后，在节点细节面板中可以找到其专属的配置属性。例如，对于 “CAT Casting” 节点，你可以设置 `ToType` 为 “Stereo2Dot0” 或 “Mono”。
4.  **连接使用**：将这些节点像标准 MetaSound 节点一样连接到你的音频图中。它们能够接收和输出 `FChannelAgnosticType` 类型的数据，实现通道自适应处理。

## C++ 用法

这些实验性功能主要用于 MetaSound 编辑器和运行时内部，作为其他节点的实现基础。直接的用户 C++ 使用场景较少，主要涉及理解和扩展 CAT 系统。

### 头文件引入

```cpp
// 包含 CAT 类型转换节点的定义，了解 FCatCastingOperator
#include "MetasoundCatCastingNode.h"

// 包含 CAT 类型定义
#include "MetasoundFormatAgnosticType.h"
```

### 基本用法

插件中的节点是作为 MetaSound 运算符 (`IOperator`) 实现的。`FCatCastingOperator` 是 CAT 格式转换节点的核心实现。

```cpp
// 来源: Private/MetasoundCatCastingNode.h
// 这个类实现了 CAT 信号的转换逻辑
class FCatCastingOperator final : public TExecutableOperator<FCatCastingOperator>
{
public:
    // 构造函数，接收构建参数、输入CAT数据、操作器数据和具体名称
    FCatCastingOperator(const FBuildOperatorParams& InParams, FChannelAgnosticTypeReadRef&& InInputCat, const CatCastingPrivate::FCatCastingOperatorData& InData, const FName InConcreteName);
    
    // ... 其他成员 ...
    
    // 核心执行函数，在此执行实际的通道转换
    void Execute();
};
```

### 进阶用法

要创建一个新的、可配置的 CAT 节点，你需要：
1.  定义一个继承自 `FMetaSoundFrontendNodeConfiguration` 的 USTRUCT，添加所需的 UPROPERTY 配置属性。
2.  实现 `OverrideDefaultInterface` 方法来根据配置动态生成节点的接口。
3.  实现 `GetOperatorData` 方法，将配置数据打包传递给实际的运算符。
4.  创建对应的运算符类，继承自 `TExecutableOperator`，并在其中实现具体的音频处理逻辑。
可参考 `FMetaSoundCatCastingNodeConfiguration` 和 `FCatCastingOperator` 的实现模式。

## Demo 示例

以下是一个极简的示例，展示如何通过配置实例化并执行一个 CAT 格式转换操作。请注意，这通常在 MetaSound 图编译的内部流程中发生，以下代码用于演示原理。

```cpp
// MyCatDemoOperator.h
#pragma once

#include "CoreMinimal.h"
#include "MetasoundCatCastingNode.h"

class FMyCatDemoOperator
{
public:
    static void RunDemo();
};
```

```cpp
// MyCatDemoOperator.cpp
#include "MyCatDemoOperator.h"
#include "MetasoundParamDriver.h" // 用于创建参数

void FMyCatDemoOperator::RunDemo()
{
    using namespace Metasound;

    // 1. 创建模拟的节点构建参数 (实际中由 MetaSound 图编译器提供)
    FBuildOperatorParams Params;
    // ... 初始化 Params，包括 Settings, Inputs, Outputs 等 ...

    // 2. 创建一个模拟的输入 CAT 数据 (例如，一个单声道信号)
    // FChannelAgnosticType 输入数据通常由上游节点提供
    FChannelAgnosticType MonoSignalData;
    // ... 填充 MonoSignalData ...

    // 3. 准备转换节点的配置 (对应节点细节面板中的设置)
    CatCastingPrivate::FCatCastingOperatorData OperatorData;
    OperatorData.ToFormatName = TEXT("Stereo2Dot0"); // 目标：立体声
    OperatorData.TranscodeMethod = Audio::EChannelTranscodeMethod::MixUpOrDown;
    OperatorData.MixMethod = Audio::EChannelMapMonoUpmixMethod::EqualPower;

    // 4. 创建转换运算符实例
    // 注意：实际使用中，FCatCastingOperator 的创建由工厂函数 CreateOperator 管理
    auto Operator = MakeUnique<FCatCastingOperator>(
        Params,
        MakeDataReadReference<FChannelAgnosticType>(MonoSignalData), // 模拟输入引用
        OperatorData,
        TEXT("DemoCastingNode") // 节点名称
    );

    // 5. 绑定输入输出 (在完整图中由图编译器完成)
    FInputVertexInterfaceData InputData;
    InputData.AddOrGetWriteReference<FChannelAgnosticType>(FName("From"), MonoSignalData);
    Operator->BindInputs(InputData);

    FOutputVertexInterfaceData OutputData;
    Operator->BindOutputs(OutputData);

    // 6. 执行转换
    Operator->Execute();

    // 7. 获取输出 (输出应为立体声信号)
    // auto OutputRef = OutputData.GetWriteReference<FChannelAgnosticType>(FName("To"));
    // ... 处理 OutputRef 中的立体声数据 ...
}
```

## 模块依赖

要使用此插件提供的功能，你的项目需要依赖 `Metasound` 插件。

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心插件，提供了音频图表运行时和编辑器基础，是本实验插件的必需前提。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 添加了实验性的 MetaSound 通道无关类型 (CAT) 波形资产支持。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 弃用修复相关的合并冲突。 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 添加了 CAT 乘法节点。 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 添加了 CAT 梯形滤波器节点。 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待定更改列表中恢复。 |

### 维护评价

该插件由 Epic Games 的 MetaSound 团队维护，正处于 **非常活跃的开发期**。从近期提交记录可以看出，团队正在密集地为通道无关类型 (CAT) 系统添加新功能节点（如 Wave, Multiply, Ladder Filter）。

**需要注意**：
1.  **实验性**：插件明确标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明其 API 和功能未来可能发生重大变更，不建议在生产项目中依赖。
2.  **依赖性**：它依赖于核心的 `Metasound` 插件。
3.  **功能定位**：主要服务于 MetaSound 图表编辑器，提供新的节点类型，而非提供大量可供外部代码直接调用的运行时 API。

**结论**：这是一个前沿的、积极开发的实验性插件，适合希望提前了解 MetaSound 未来发展（特别是通道无关类型系统）的开发者或在安全的测试环境中试用。不建议将其用于稳定发布的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- 官方文档：暂无
- 测试用例：在当前提供的路径中未发现专用测试用例目录。