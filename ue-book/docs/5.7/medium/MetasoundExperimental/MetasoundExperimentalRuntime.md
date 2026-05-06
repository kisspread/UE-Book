# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 元声音实验性扩展 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Metasound 示例资产、节点配置） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

该插件是 MetaSound 的**实验性扩展集合**，专为尚未稳定、不适合正式发布的功能提供试验场。当前主要包含：

- **通道无关类型（Channel Agnostic Type, CAT）系统** – 允许 MetaSound 节点处理任意通道数的音频流（如 1.0 声道 → 5.1 声道），并支持灵活的格式转换（ChannelDrop、MixUpOrDown）。
- **动态节点配置** – 通过 `FMetaSoundFrontendNodeConfiguration` 子类，使节点能根据参数自动生成可变数量的输入/输出引脚（如 "CatMixer" 动态混音器）。
- **Fade 节点** – 音频淡入淡出功能（由近期提交引入）。
- **节点配置扩展机制** – 允许自定义节点覆盖默认接口、传递运算符数据，为高级用户提供扩展点。

**为什么存在？**  
MetaSound 的核心框架是稳定的，但许多高级特性（如多声道动态处理、通道格式转换、可变引脚节点）需要大量实验才能确定 API 和用户体验。此插件为这些功能的快速迭代提供了隔离环境，避免影响核心 MetaSound 的稳定性。

## 使用场景

- 你正在制作一个需要**自动适配不同声道数音频源**的游戏（如将立体声音效重新映射到 7.1 声道），可使用 CatCasting 节点。
- 你需要创建一个 **可变输入数量的混音器**（例如音频源数量不固定），可使用 CatMixer 节点并动态设置输入数量。
- 你希望**测试 MetaSound 尚未稳定的新节点**（如 Fade 节点），并参与反馈。
- 你是 MetaSound 节点开发者，想要利用 `OverrideDefaultInterface` 和 `OperatorData` 机制扩展节点能力。

## 蓝图用法

该插件主要面向 MetaSound 图编辑器（而非直接暴露蓝图调用）。以下为通过 `UMetasoundCatCastingOptionsHelper` 暴露的辅助函数：

### 核心函数（蓝图可调用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCastingOptions` | 返回所有可用的 CAT 格式名称（如 "Mono", "Stereo", "5.1" 等） | `UMetasoundCatCastingOptionsHelper` (静态) |

**使用说明**：此函数通常在节点配置的 `GetOptions` 元数据中间接使用，以在细节面板中填充下拉选项。也可在蓝图节点中调用以动态查询可用格式。

## C++ 用法

### 头文件引入

```cpp
#include "MetasoundChannelAgnosticType.h"
#include "MetasoundCatCastingNode.h"
#include "MetasoundCatMixerNode.h"
```

### 基本用法（CAT 数据类型）

```cpp
// 创建一个 Channel Agnostic Type，指定格式为 "Stereo"
Metasound::FChannelAgnosticType CatStereo(InSettings, FName("Stereo"));

// 使用默认格式（GetDefaultCatFormat() 返回 "Mono" 等）
Metasound::FChannelAgnosticType CatDefault(InSettings);
```

来源：`Engine/Plugins/Experimental/MetasoundExperimental/Source/MetasoundExperimentalRuntime/Public/MetasoundChannelAgnosticType.h`

### 进阶用法（自定义节点配置）

以下示例展示如何继承 `FMetaSoundFrontendNodeConfiguration` 并覆盖接口创建动态引脚节点（参考 CatMixer）：

```cpp
// MyCatMixerNodeConfiguration.h
#include "MetasoundCatMixerNode.h"

USTRUCT()
struct FMyCustomMixerConfig : public FMetaSoundCatMixingNodeConfiguration
{
    GENERATED_BODY()

    virtual TInstancedStruct<FMetasoundFrontendClassInterface> OverrideDefaultInterface(
        const FMetasoundFrontendClass& InNodeClass) const override
    {
        // 根据 NumInputs 动态生成输入引脚
        TArray<FMetasoundFrontendClassInput> Inputs;
        for (int32 i = 0; i < NumInputs; i++)
        {
            FMetasoundFrontendClassInput Input;
            Input.Name = *FString::Printf(TEXT("Audio In %d"), i);
            Input.TypeName = GetMetasoundDataTypeName<FChannelAgnosticType>();
            Inputs.Add(Input);
        }

        // 使用基类 CatMixing 的接口（输出格式由 FormatChoosingMethod 决定）
        // 此处简化，实际见基类实现
        return FMetaSoundFrontendClassInterface(Inputs, {Output});
    }

    virtual TSharedPtr<const Metasound::IOperatorData> GetOperatorData() const override
    {
        // 传递自定义数据给运算符
        return nullptr; // 或返回自定义 IOperatorData
    }
};
```

来源：`Engine/Plugins/Experimental/MetasoundExperimental/Source/MetasoundExperimentalRuntime/Private/MetasoundCatMixerNode.h`

## Demo 示例

以下是一个最小 C++ 节点，使用 `FMetaSoundCatCastingNodeConfiguration` 创建通道格式转换节点（仅展示 USTRUCT 部分，注册节点需参考 MetaSound 文档）：

```cpp
// MyCatCastingNode.h
#pragma once

#include "MetasoundCatCastingNode.h"
#include "MetasoundOperatorData.h"

USTRUCT()
struct FMyCatCastConfig : public FMetaSoundCatCastingNodeConfiguration
{
    GENERATED_BODY()

    virtual TInstancedStruct<FMetasoundFrontendClassInterface> OverrideDefaultInterface(
        const FMetasoundFrontendClass& InNodeClass) const override
    {
        // 基于 ToType 和 TranscodeMethod 生成输入/输出接口
        // 此处省略具体实现，参考基类
        return Super::OverrideDefaultInterface(InNodeClass);
    }

    virtual TSharedPtr<const Metasound::IOperatorData> GetOperatorData() const override
    {
        // 传递 TranscodeMethod 等参数给运算符
        return MakeShared<Metasound::Experimental::FWidgetExampleOperatorData>(
            static_cast<float>(TranscodeMethod)
        );
    }
};
```

**编译要求**：将 `MetasoundExperimentalRuntime` 添加到你的模块的 `PublicDependencyModuleNames` 中。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | 核心 MetaSound 框架，提供图执行、数据类型、节点注册等 |

**其他依赖**：无特殊依赖（仅标准 Core/CoreUObject/Engine 等）。

## 维护状态

### 近期更新

- 2025-09-30 `3a283b32` — [MetaSound Experimental] Fade Node unit test fix
- 2025-08-21 `51079168` — Improve metasound node registration association with modules
- 2025-08-15 `38229d1b` — Metasound LOCTEXT fixups
- 2025-08-05 `da28318e` — [Metasound Experimental] Addressed minor optimization feedback
- 2025-08-05 `4c1309f1` — [Metasound Experimental] - Added Fade Node

### 维护评价

- **创建时间**：2025-08-05
- **更新频率**：活跃，最近三个月内有多次功能性更新（Fade 节点、节点注册优化）
- **状态**：实验性插件（`IsExperimentalVersion=true`），标志着还在快速原型阶段，API 可能随时变化
- **推荐度**：适合开发者试用并提供反馈，**不建议直接用于生产项目**；若需要稳定 MetaSound 扩展，请等待其进入正式模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental)
- [核心 MetaSound 文档（官方）](https://docs.unrealengine.com/5.3/en-US/metasound-in-unreal-engine/)
- [测试用例（可能位于 Engine/Tests 下，暂无直接链接）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Metasound)