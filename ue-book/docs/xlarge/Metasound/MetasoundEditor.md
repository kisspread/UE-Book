# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、节点库） |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-22 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是一个基于节点的高性能音频处理系统，旨在将音频 DSP（数字信号处理）图的创建和控制权完全交给声音设计师。它解决了传统音频系统中声音设计师需要依赖程序员来实现复杂音频逻辑的痛点。

**核心功能**：
- **可视化节点图编辑器**：提供类似蓝图的节点图界面，用于构建音频处理流程。
- **样本精确控制**：支持在音频样本级别进行精确的控制和调制。
- **数据驱动**：音频参数和事件可以来自游戏数据（如角色状态、环境变量）和蓝图，实现动态、交互式的音频体验。
- **资产化**：音频逻辑被封装为可复用的 `MetaSound` 资产（`MetaSoundSource` 用于可播放的音源，`MetaSoundPatch` 用于可复用的音频处理片段）。
- **高性能**：专为实时音频处理设计，优化了图的编译和执行效率。

## 使用场景

- **动态音乐系统**：根据游戏状态（如战斗、探索）实时混合、切换音乐层。
- **环境音效**：创建复杂的、对玩家位置和动作做出反应的环境声景。
- **交互式音频反馈**：为 UI 交互、技能释放、武器射击等提供丰富、可变的音效。
- **程序化音频生成**：使用数学节点和噪声生成器创造独特的音效。
- **音频原型设计**：声音设计师可以快速迭代音频设计，无需等待程序员实现。

## 蓝图用法

MetaSound 提供了丰富的蓝图 API，主要通过 `UMetaSoundEditorSubsystem` 和 `UMetaSoundBuilderSubsystem` 进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Or Begin Building MetaSound Asset` | 查找或开始编辑一个 MetaSound 资产，返回其构建器。 | `UMetaSoundEditorSubsystem` |
| `Build To Asset` | 将一个 MetaSound 构建器（Builder）编译成一个可播放的 MetaSound 资产。 | `UMetaSoundEditorSubsystem` |
| `Set Node Location` | 设置 MetaSound 图中某个节点的视觉位置（用于编辑器布局）。 | `UMetaSoundEditorSubsystem` |
| `Add Builder Delegate Listener` | 为构建器添加一个监听器对象，用于响应构建器文档的各种变化（如输入添加、重命名等）。 | `UMetaSoundEditorSubsystem` |
| `Find Or Create Graph Input Metadata` | 查找或创建图输入的元数据（如浮点数的范围信息）。 | `UMetaSoundEditorSubsystem` |
| `Add Graph Input` | 向 MetaSound 图添加一个新的输入端口。 | `UMetaSoundBuilderBase` |
| `Add Graph Output` | 向 MetaSound 图添加一个新的输出端口。 | `UMetaSoundBuilderBase` |
| `Add Node` | 向图中添加一个指定类的节点。 | `UMetaSoundBuilderBase` |
| `Connect Nodes` | 连接两个节点的引脚。 | `UMetaSoundBuilderBase` |
| `Set Literal` | 设置节点输入引脚的默认值（字面量）。 | `UMetaSoundBuilderBase` |

### 使用示例（蓝图描述）

1.  **创建一个简单的 MetaSound**：
    - 使用 `Find Or Begin Building MetaSound Asset` 节点，传入一个已存在的 `MetaSoundSource` 资产或留空以创建新的。
    - 从返回的 `Builder` 对象，调用 `Add Graph Input` 添加一个 `Float` 类型的输入，命名为 `Volume`。
    - 调用 `Add Node` 添加一个 `Multiply` 节点。
    - 调用 `Add Node` 添加一个 `Sine Wave` 节点。
    - 调用 `Connect Nodes` 将 `Sine Wave` 的 `Audio` 输出连接到 `Multiply` 的第一个输入。
    - 调用 `Connect Nodes` 将 `Volume` 输入节点连接到 `Multiply` 的第二个输入。
    - 调用 `Add Graph Output` 添加一个 `Audio` 输出。
    - 调用 `Connect Nodes` 将 `Multiply` 的输出连接到最终的 `Audio` 输出。
    - 最后，调用 `Build To Asset` 将构建器编译成资产。

2.  **监听构建器变化**：
    - 调用 `Add Builder Delegate Listener` 获取一个 `UMetaSoundEditorBuilderListener` 对象。
    - 在蓝图中，将该对象的 `On Graph Input Added`、`On Graph Input Name Changed` 等委托绑定到自定义事件，以响应编辑器中的操作。

## C++ 用法

### 头文件引入

```cpp
#include "MetasoundEditorSubsystem.h"
#include "MetasoundBuilderSubsystem.h"
#include "MetasoundFrontendDocument.h"
```

### 基本用法

以下示例展示如何在 C++ 中创建一个 MetaSound 并添加节点。代码逻辑参考自 `MetasoundEditorSubsystem` 和 `MetasoundBuilderBase` 的蓝图实现。

```cpp
// 假设在某个编辑器工具或自定义资产编辑器中
void CreateSimpleMetaSound()
{
    // 1. 获取编辑器子系统
    UMetaSoundEditorSubsystem* EditorSubsystem = GEditor->GetEditorSubsystem<UMetaSoundEditorSubsystem>();
    if (!EditorSubsystem) return;

    // 2. 创建一个新的 MetaSoundSource 构建器 (Transient)
    EMetaSoundBuilderResult Result;
    UMetaSoundBuilderBase* Builder = EditorSubsystem->FindOrBeginBuilding(nullptr, Result); // nullptr 表示创建新的
    if (Result != EMetaSoundBuilderResult::Succeeded || !Builder) return;

    // 3. 添加一个浮点输入
    const FName InputName = TEXT("Frequency");
    Builder->AddGraphInput(InputName, GetMetasoundDataTypeName<float>(), EMetaSoundFrontendVertexAccessType::Value);

    // 4. 添加一个 Sine Wave 节点
    const FMetasoundFrontendClassName SineWaveClassName = GetMetasoundFrontendClassName<FSineWaveNode>();
    FMetaSoundNodeHandle SineNodeHandle = Builder->AddNode(SineWaveClassName);

    // 5. 添加一个 Audio Output 节点
    const FMetasoundFrontendClassName AudioOutputClassName = GetMetasoundFrontendClassName<FAudioOutputNode>();
    FMetaSoundNodeHandle OutputNodeHandle = Builder->AddNode(AudioOutputClassName);

    // 6. 连接节点：Sine Wave 的 Audio 输出 -> Audio Output 的 Audio 输入
    Builder->ConnectNodes(SineNodeHandle, TEXT("Audio"), OutputNodeHandle, TEXT("Audio"));

    // 7. 设置 Sine Wave 节点的 Frequency 输入为我们的图输入
    Builder->ConnectNodes(Builder->GetGraphInputNodeHandle(InputName), TEXT("Value"), SineNodeHandle, TEXT("Frequency"));

    // 8. 构建资产
    FString AssetName = TEXT("MySimpleSine");
    FString PackagePath = TEXT("/Game/Audio/");
    TScriptInterface<IMetaSoundDocumentInterface> MetaSoundAsset = EditorSubsystem->BuildToAsset(
        Builder, TEXT("MyAuthor"), AssetName, PackagePath, Result);

    if (Result == EMetaSoundBuilderResult::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT("MetaSound asset created: %s"), *MetaSoundAsset.GetObject()->GetName());
    }
}
```

### 进阶用法

更复杂的用法涉及使用 `FMetaSoundFrontendDocumentBuilder` 直接操作底层文档结构，或创建自定义节点。这通常用于开发新的 MetaSound 节点类型或进行批量资产处理。

```cpp
// 示例：直接使用 Frontend Document Builder 修改 MetaSound 文档
void ModifyMetaSoundDocument(UMetaSoundSource* MetaSoundSource)
{
    if (!MetaSoundSource) return;

    // 获取文档构建器
    FMetaSoundFrontendDocumentBuilder DocumentBuilder(MetaSoundSource->GetDocument());

    // 添加一个自定义输入，并设置其默认值
    const FName CustomInput = TEXT("CustomParam");
    DocumentBuilder.AddGraphInput(CustomInput, GetMetasoundDataTypeName<float>(), EMetaSoundFrontendVertexAccessType::Value);

    // 设置该输入在默认页面的默认值为 1.0f
    FMetasoundFrontendLiteral Literal;
    Literal.Set(1.0f);
    DocumentBuilder.SetGraphInputDefault(CustomInput, Literal);

    // 应用修改（这会标记资产为脏）
    DocumentBuilder.ApplyChanges();
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何用 C++ 创建一个包含基本节点连接的 MetaSound。

**MetaSoundDemo.h**
```cpp
// MetaSoundDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MetaSoundDemo.generated.h"

UCLASS()
class UMetaSoundDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MetaSoundDemo")
    void CreateDemoMetaSound();
};
```

**MetaSoundDemo.cpp**
```cpp
// MetaSoundDemo.cpp
#include "MetaSoundDemo.h"
#include "MetasoundEditorSubsystem.h"
#include "MetasoundBuilderSubsystem.h"
#include "MetasoundFrontend.h"
#include "MetasoundPrimitives.h" // For GetMetasoundDataTypeName

void UMetaSoundDemoSubsystem::CreateDemoMetaSound()
{
    UMetaSoundEditorSubsystem* EditorSS = GEditor->GetEditorSubsystem<UMetaSoundEditorSubsystem>();
    if (!EditorSS) return;

    EMetaSoundBuilderResult Result;
    UMetaSoundBuilderBase* Builder = EditorSS->FindOrBeginBuilding(nullptr, Result);
    if (Result != EMetaSoundBuilderResult::Succeeded) return;

    // 添加输入
    Builder->AddGraphInput(TEXT("Amplitude"), GetMetasoundDataTypeName<float>(), EMetaSoundFrontendVertexAccessType::Value);

    // 添加节点
    auto SineNode = Builder->AddNode(GetMetasoundFrontendClassName<FSineWaveNode>());
    auto MultiplyNode = Builder->AddNode(GetMetasoundFrontendClassName<FMultiplyNode<float>>());
    auto OutputNode = Builder->AddNode(GetMetasoundFrontendClassName<FAudioOutputNode>());

    // 连接
    Builder->ConnectNodes(SineNode, TEXT("Audio"), MultiplyNode, TEXT("Input1"));
    Builder->ConnectNodes(Builder->GetGraphInputNodeHandle(TEXT("Amplitude")), TEXT("Value"), MultiplyNode, TEXT("Input2"));
    Builder->ConnectNodes(MultiplyNode, TEXT("Output"), OutputNode, TEXT("Audio"));

    // 构建
    EditorSS->BuildToAsset(Builder, TEXT("Demo"), TEXT("DemoSineWave"), TEXT("/Game/MetaSounds/"), Result);
}
```

## 模块依赖

MetaSound 插件内部模块依赖关系复杂，但对于**使用**该插件的开发者，主要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | MetaSound 的前端文档系统、数据类型注册、节点类注册。是定义 MetaSound 数据结构和接口的核心。 |
| `MetasoundEngine` | MetaSound 的运行时引擎，负责图的编译、实例化和音频处理。 |
| `MetasoundStandardNodes` | 提供了一套标准的音频处理节点（如振荡器、滤波器、数学运算等）。 |
| `MetasoundGraphCore` | 图处理的核心数据结构和算法。 |

**注意**：`MetasoundEditor` 模块仅用于编辑器环境，不应在运行时游戏模块中依赖。

## 维护状态

### 近期更新

- 2025-10-03 `41ab63f8f1f0` 移除了 MetaSound 编辑器中本应由调用代码/脚本事务管理的资产标记为脏的操作。
- 2025-09-15 `e307f58ca290` 修复了 MetaSound 预设自动保存时的编辑器崩溃问题。
- 2025-08-20 `48ec3f5adcac` 修复了撤销 MetaSound 预设输入覆盖时的崩溃问题。

### 维护评价

MetaSound 是 UE5 音频系统的核心组件，自 2020 年引入以来持续得到 Epic Games 的积极维护和功能增强。从近期提交记录看，团队仍在专注于修复编辑器稳定性问题和提升用户体验，表明该插件处于**活跃维护**状态。

- **优势**：功能强大，与引擎深度集成，是官方推荐的下一代音频解决方案。
- **注意**：由于系统复杂，学习曲线较陡。部分高级功能（如自定义节点开发）需要深入理解其架构。
- **推荐**：对于任何需要复杂、动态音频交互的 UE5 项目，强烈推荐使用 MetaSound。它代表了 UE 音频技术的未来方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/overview-of-metasounds-in-unreal-engine/) (UE5 官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)