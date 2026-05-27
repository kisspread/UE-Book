# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | MetaSound 实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaSound 节点定义、配置资产） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

MetasoundExperimental 插件提供了一套 **Channel Agnostic Types (CAT，通道无关类型)** 系统，这是 MetaSound 音频图的全新功能扩展。传统 MetaSound 节点在设计时就绑定了特定的音频通道格式（如 Mono、Stereo、5.1 等），而 CAT 系统允许节点在运行时动态适配任意通道布局。

**核心解决的问题**：在传统 MetaSound 工作流中，如果你的 MetaSound Source 输出设置为 5.1，但某个节点只能处理 Stereo，就需要手动添加格式转换节点。CAT 系统使节点能够"通道无关"地处理音频数据，自动处理不同通道格式之间的转换（混音、升降通道等），大大简化了多格式音频资产的制作流程。

此外，该插件还包含实验性的 Cat Panner（声像定位）节点，支持在任意方位角通道格式之间进行声像处理。

## 使用场景

- 你需要创建一个 MetaSound，它需要在 Mono、Stereo、5.1 等多种输出格式下都能正确工作 → 使用 CAT 节点自动适配
- 你需要在 MetaSound 图中将单声道音频上混为多声道输出 → 使用 CAT Casting 节点，选择 MixUpOrDown 方法
- 你需要将多声道音频合并为单声道或立体声 → 使用 CAT Casting 节点，选择 ChannelDrop 方法
- 你需要在一个 MetaSound 中混合多个不同通道格式的音频源 → 使用 CAT Mixer 节点
- 你需要对音频进行声像定位（panning）并输出到特定的方位角通道格式 → 使用 CAT Panner 节点

## 蓝图用法

此插件主要通过 MetaSound 编辑器中的节点配置面板使用，不直接暴露蓝图节点。配置通过 MetaSound 图中的节点属性面板完成。

### 核心节点类型

| 节点类型 | 说明 | 配置结构体 |
|---|---|---|
| `Cat Casting` | 通道格式转换节点，在任意 CAT 格式之间转码 | `FMetaSoundCatCastingNodeConfiguration` |
| `Cat Mixer` | 通道无关混音器，自动处理不同通道格式的混合 | `FMetaSoundCatMixingNodeConfiguration` |
| `Cat Panner` | 通道无关声像定位器，支持方位角通道格式 | `FMetaSoundCatPannerNodeConfiguration` |
| `Cat Break` | 将 CAT 类型分解为指定格式的通道数据 | `FMetaSoundCatBreakNodeConfiguration` |
| `Cat Make` | 将通道数据组合为 CAT 类型 | `FMetaSoundCatMakeNodeConfiguration` |
| `Example Node` | 实验性示例节点，展示自定义节点配置 | `FMetaSoundExperimentalExampleNodeConfiguration` |

### Cat Casting 节点配置

在 MetaSound 编辑器中选中 Cat Casting 节点后，属性面板显示：

| 属性 | 类型 | 说明 |
|---|---|---|
| ToType | FName | 目标通道格式（如 Mono、Stereo2Dot0、5Dot1 等） |
| TranscodeMethod | Enum | 转码方法：ChannelDrop（丢弃多余通道）或 MixUpOrDown（智能升降混） |
| MixMethod | Enum | 仅在 MixUpOrDown 模式下生效：Linear、EqualPower、FullVolume |

### Cat Mixer 节点配置

| 属性 | 类型 | 说明 |
|---|---|---|
| FormatChoosingMethod | Enum | 混音格式策略：HighestInput / LowestInput / MetasoundOutput / Custom |
| NumInputs | int32 | 输入数量（1-100） |
| CustomMixFormat | FName | 仅在 Custom 模式下生效，自定义混音格式 |
| CatCastingMethod | Enum | 混音时的转码方法 |
| ChannelMapMonoUpmixMethod | Enum | 单声道上混方法 |

### Cat Panner 节点配置

| 属性 | 类型 | 说明 |
|---|---|---|
| PanToType | FName | 目标方位角通道格式（如 Cat:Stereo2Dot0） |
| PanningMethod | Enum | 声像算法：EqualPower（等功率）或 Linear（线性） |

## C++ 用法

### 头文件引入

```cpp
#include "MetasoundFormatAgnosticType.h"
#include "MetasoundExampleNodeConfiguration.h"
```

### 基本用法 — 创建自定义节点配置

以下示例展示了如何定义一个自定义 MetaSound 节点配置结构体，这是 CAT 系统中所有节点的基础模式：

```cpp
// 来源: Public/MetasoundExampleNodeConfiguration.h

// 定义一个自定义节点配置
USTRUCT()
struct FMyCustomNodeConfiguration : public FMetaSoundFrontendNodeConfiguration
{
    GENERATED_BODY()

    // 节点属性
    UPROPERTY(EditAnywhere, Category = General)
    FString MyString;

    UPROPERTY(EditAnywhere, Category = General, meta = (ClampMin = "1", ClampMax = "1000"))
    uint32 NumInputs;

    UPROPERTY(EditAnywhere, Category = General, meta = (ClampMin = "1", ClampMax = "1000"))
    uint32 NumOutputs;

    // 覆写默认接口，根据配置动态生成输入输出端口
    virtual TInstancedStruct<FMetasoundFrontendClassInterface> OverrideDefaultInterface(
        const FMetasoundFrontendClass& InNodeClass) const override;

    // 传递配置数据到算子
    virtual TSharedPtr<const Metasound::IOperatorData> GetOperatorData() const override;
};
```

### 基本用法 — 使用 CAT Casting 操作符

```cpp
// 来源: Private/MetasoundCatCastingNode.h

namespace Metasound
{
    // 创建 Cat Casting 算子工厂
    static TUniquePtr<IOperator> CreateCastingOperator(
        const FBuildOperatorParams& InParams,
        FBuildResults& OutResults)
    {
        return FCatCastingOperator::CreateOperator(InParams, OutResults);
    }

    // 获取节点元数据
    FNodeClassMetadata Metadata = FCatCastingOperator::GetNodeInfo();
}
```

### 进阶用法 — 自定义算子数据传递

```cpp
// 来源: Public/MetasoundExampleNodeConfiguration.h

namespace Metasound::Experimental
{
    // 定义自定义算子数据类型，用于在配置和运行时算子之间传递数据
    class FWidgetExampleOperatorData : public TOperatorData<FWidgetExampleOperatorData>
    {
    public:
        static const FLazyName OperatorDataTypeName;

        FWidgetExampleOperatorData(const float& InFloat)
            : MyFloat(InFloat)
        {
        }

        float MyFloat;
    };
}

// 在配置结构体中使用
USTRUCT()
struct FMetaSoundWidgetExampleNodeConfiguration : public FMetaSoundFrontendNodeConfiguration
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = General)
    float MyFloat;

    // 将配置数据打包为算子数据
    TSharedPtr<const Metasound::IOperatorData> GetOperatorData() const override
    {
        if (!OperatorData.IsValid())
        {
            OperatorData = MakeShared<Metasound::Experimental::FWidgetExampleOperatorData>(MyFloat);
        }
        return OperatorData;
    }

private:
    mutable TSharedPtr<Metasound::Experimental::FWidgetExampleOperatorData> OperatorData;
};
```

### 进阶用法 — 方位角转换工具函数

```cpp
// 来源: Public/MetasoundCatPannerNode.h

// 将归一化的方位角值（0.0-1.0）转换为角度（0.0-360.0）
float Degrees = Metasound::NormalizedAzimuthToDegrees(0.5f); // 返回 180.0f
```

## Demo 示例

以下示例展示如何注册一个自定义的 CAT 转换节点：

```cpp
// MyCatNode.h
#pragma once

#include "MetasoundFrontendNodeConfiguration.h"
#include "MetasoundNode.h"

USTRUCT()
struct FMyCatConversionConfiguration : public FMetaSoundFrontendNodeConfiguration
{
    GENERATED_BODY()

    FMyCatConversionConfiguration() = default;

    UPROPERTY(EditAnywhere, Category = General)
    FName TargetFormat = TEXT("Cat:Stereo2Dot0");

    virtual TInstancedStruct<FMetasoundFrontendClassInterface> OverrideDefaultInterface(
        const FMetasoundFrontendClass& InNodeClass) const override;
    virtual TSharedPtr<const Metasound::IOperatorData> GetOperatorData() const override;
};
```

```cpp
// MyCatNode.cpp
#include "MyCatNode.h"
#include "MetasoundCatConversionNode.h"

void RegisterMyCatNode()
{
    // 使用插件提供的 CAT 节点注册机制
    Metasound::RegisterCatConvertNode();
}

TInstancedStruct<FMetasoundFrontendClassInterface> 
FMyCatConversionConfiguration::OverrideDefaultInterface(
    const FMetasoundFrontendClass& InNodeClass) const
{
    // 根据配置的 TargetFormat 动态生成接口
    TInstancedStruct<FMetasoundFrontendClassInterface> Interface;
    // ... 配置输入输出端口 ...
    return Interface;
}

TSharedPtr<const Metasound::IOperatorData> 
FMyCatConversionConfiguration::GetOperatorData() const
{
    // 将格式配置传递给运行时算子
    return nullptr; // 根据实际需求实现
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心引擎，提供节点系统、算子框架、前端文档结构 |
| `AudioMixer` | 音频混音器，提供通道转码（ChannelAgnosticTranscoder）底层实现 |
| `AudioPlatformConfiguration` | 音频平台配置，定义通道格式枚举和映射方法 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 新增 CAT 波形相关功能 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup | 修复 FSoundWaveData API 废弃导致的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 新增 CAT 乘法运算节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 新增 CAT 梯形滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261' | 从待提交更改列表中恢复 |

### 维护评价

- **活跃维护** ✅：该插件在最近一个月内持续有功能性更新，CAT 节点类型不断增加（Wave、Multiply、Ladder Filter 等）
- **实验性状态** ⚠️：标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能随时变化
- **创建时间短**：仅创建约 3 个月，处于早期开发阶段
- **功能快速迭代**：从 Git 历史看，正在密集添加各种 CAT 节点类型
- **推荐程度**：适合想要提前体验 MetaSound CAT 系统的开发者用于学习和实验，**不建议用于正式项目**

> ⚠️ **警告**：此插件为实验性功能，API 随时可能变更，依赖此插件的项目可能在后续引擎版本中需要大量修改。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [Metasound 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)（前置依赖）