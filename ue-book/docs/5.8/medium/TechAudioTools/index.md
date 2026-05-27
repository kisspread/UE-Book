# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 技术音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaSound 相关资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

Tech Audio Tools 是一个专门为 MetaSound 系统构建的**高级工具和实用程序集合**。它并非简单的音频播放器，而是为音频程序员和设计师提供了一套用于**自动化、扩展和自定义 MetaSound 工作流**的底层 API 和工具。其核心价值在于：

1.  **MetaSound 图的程序化生成与操作**：允许在 C++ 或蓝图中动态创建、修改 MetaSound 图，实现运行时音频逻辑的构建。
2.  **扩展 MetaSound 编辑器**：提供编辑器端工具，增强 MetaSound 的创作体验，如自定义节点、视图模型等。
3.  **提供核心音频数据操作原语**：包含对 MetaSound 核心数据类型（如 Literal、Wave）的工具函数。

简而言之，它的存在是为了填补 MetaSound 系统在“高级工具链”层面的空白，让复杂的音频系统构建变得可编程、可定制。

## 使用场景

-   **音频系统程序员**：当你需要在运行时根据游戏状态（如角色能力、环境事件）动态生成或切换 MetaSound 效果图时。
-   **音频技术美术 (Technical Audio Designer)**：当你需要为 MetaSound 编辑器创建自定义的节点、输入处理器或视图模型来优化工作流时。
-   **复杂音频逻辑实现**：当标准的 MetaSound 节点无法满足需求，需要通过代码创建自定义的音频处理逻辑时。

## 蓝图用法

蓝图功能主要分布在 `TechAudioTools` 和 `TechAudioToolsMetaSound` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get MetaSound Document` | 从 MetaSound 源资产获取其内部文档对象，用于程序化访问和修改。 | `UMetaSoundUtils` |
| `Create MetaSound Node` | 在指定的 MetaSound 文档中动态创建一个新的节点（如音源、振荡器、调制器）。 | `UMetaSoundUtils` |
| `Create MetaSound Connection` | 在文档中已有的两个节点引脚之间建立连接。 | `UMetaSoundUtils` |
| `Set MetaSound Literal Value` | 设置 MetaSound 图中“文字”节点的值（如浮点数、整数、布尔值）。 | `UMetaSoundUtils` |
| `Get/Set MetaSound Wave Asset` | 获取或设置与 MetaSound Wave 引脚关联的声波资产。 | `UMetaSoundUtils` |

### 使用示例（蓝图描述）

1.  **动态生成一个简单的正弦波发生器**：
    - 使用 `Get MetaSound Document` 从一个空的 MetaSound 资产获取文档。
    - 用 `Create MetaSound Node` 创建一个 “Sine” 节点。
    - 再创建一个 “Audio Output” 节点。
    - 用 `Create MetaSound Connection` 将 Sine 节点的 “Out” 引脚连接到 Audio Output 的 “In” 引脚。
    - 最后编译该 MetaSound 文档，即可得到一个可播放的资产。

2.  **运行时修改音效参数**：
    - 在事件图表中，获取一个已存在的 MetaSound 实例。
    - 使用 `Set MetaSound Literal Value` 节点，根据游戏变量（如速度）实时更新一个控制音高的 Literal 节点的值。

## C++ 用法

重点从测试用例中提取，贴近官方用法。

### 头文件引入

```cpp
#include "TechAudioToolsModule.h" // 核心模块
#include "MetaSoundUtils.h" // MetaSound 操作工具类
#include "MetaSoundDocument.h" // MetaSound 文档类
#include "MetaSoundNode.h" // MetaSound 节点类
```

### 基本用法

```cpp
// 来源：Engine/Plugins/Experimental/TechAudioTools/Source/TechAudioTools/Tests/MetaSoundUtilsTest.cpp
// 测试动态创建 MetaSound 节点

// 1. 创建一个 MetaSound 文档
TSharedRef<UE::Metasound::FMetaSoundDocument> Document = MakeShared<UE::Metasound::FMetaSoundDocument>();

// 2. 使用工具类在文档中创建节点
UE::Metasound::FMetaSoundNode* SineNode = UE::Audio::MetaSoundUtils::CreateNode(
    Document,
    TEXT("Sine"), // 节点类型名
    FGuid::NewGuid(),
    FVector2D(0.f, 0.f) // 节点在图中的位置
);

UE::Metasound::FMetaSoundNode* OutputNode = UE::Audio::MetaSoundUtils::CreateNode(
    Document,
    TEXT("Audio Output"),
    FGuid::NewGuid(),
    FVector2D(100.f, 0.f)
);

// 3. 建立连接
bool bConnected = UE::Audio::MetaSoundUtils::ConnectNodes(
    Document,
    SineNode->GetID(),
    TEXT("Out"), // 输出引脚名
    OutputNode->GetID(),
    TEXT("In") // 输入引脚名
);

// 4. 文档现在可以用于创建 MetaSound 源资产
```

### 进阶用法

结合 `MetaSoundView` (编辑器端) 和 `MetaSoundLiteral` 进行更复杂的操作。

```cpp
// 假设有一个已存在的 MetaSound 资产
UMetaSoundSource* MetaSoundSource = ...;
// 获取其文档进行修改
TSharedRef<UE::Metasound::FMetaSoundDocument> Doc = MetaSoundSource->GetDocument();

// 查找图中的特定节点并修改其 Literal 参数
if (UE::Metasound::FMetaSoundNode* FrequencyNode = UE::Audio::MetaSoundUtils::FindNodeByName(Doc, TEXT("Frequency")))
{
    // 设置该节点（假设是一个 Literal 节点）的值为 440.0f
    UE::Metasound::FMetaSoundLiteral Literal;
    Literal.Type = UE::Metasound::EMetaSoundLiteralType::Float;
    Literal.AsFloat = 440.0f;
    UE::Audio::MetaSoundUtils::SetNodeLiteralValue(Doc, FrequencyNode->GetID(), Literal);

    // 更新资产
    MetaSoundSource->SetDocument(Doc);
}
```

## Demo 示例

一个最小化的示例，展示如何在运行时创建一个 MetaSound 并播放一个正弦波。

**MyDynamicSound.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyDynamicSound.generated.h"

class UMetaSoundSource;
class UAudioComponent;

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyDynamicSound : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="DynamicSound")
    void PlayDynamicSineWave(float Frequency = 440.0f);

private:
    UPROPERTY()
    TObjectPtr<UMetaSoundSource> DynamicMetaSoundSource;

    UPROPERTY()
    TObjectPtr<UAudioComponent> AudioComponent;
};
```

**MyDynamicSound.cpp**
```cpp
#include "MyDynamicSound.h"
#include "MetaSoundSource.h"
#include "Components/AudioComponent.h"
#include "MetaSoundDocument.h"
#include "MetaSoundNode.h"
#include "TechAudioToolsModule.h" // 引入模块
#include "MetaSoundUtils.h"

void UMyDynamicSound::BeginPlay()
{
    Super::BeginPlay();
    // 创建空的 MetaSound 资产 (通常在编辑器完成，这里仅为演示)
    DynamicMetaSoundSource = NewObject<UMetaSoundSource>(GetTransientPackage(), TEXT("DynamicSine"));
}

void UMyDynamicSound::PlayDynamicSineWave(float Frequency)
{
    if (!DynamicMetaSoundSource) return;

    // 1. 获取文档
    TSharedRef<UE::Metasound::FMetaSoundDocument> Document = DynamicMetaSoundSource->GetDocument();
    // 清空现有节点（可选）
    Document->GetGraph().Nodes.Reset();

    // 2. 创建节点
    UE::Metasound::FMetaSoundNode* SineNode = UE::Audio::MetaSoundUtils::CreateNode(
        Document, TEXT("Sine"), FGuid::NewGuid(), FVector2D::ZeroVector);

    // 设置频率参数（创建一个 Literal 节点并连接）
    UE::Metasound::FMetaSoundNode* FreqLiteral = UE::Audio::MetaSoundUtils::CreateNode(
        Document, TEXT("Literal Float"), FGuid::NewGuid(), FVector2D(-100.f, 0.f));
    UE::Metasound::FMetaSoundLiteral Literal;
    Literal.Type = UE::Metasound::EMetaSoundLiteralType::Float;
    Literal.AsFloat = Frequency;
    UE::Audio::MetaSoundUtils::SetNodeLiteralValue(Document, FreqLiteral->GetID(), Literal);
    UE::Audio::MetaSoundUtils::ConnectNodes(Document, FreqLiteral->GetID(), TEXT("Value"), SineNode->GetID(), TEXT("Frequency"));

    UE::Metasound::FMetaSoundNode* OutputNode = UE::Audio::MetaSoundUtils::CreateNode(
        Document, TEXT("Audio Output"), FGuid::NewGuid(), FVector2D(100.f, 0.f));

    // 3. 连接 Sine 到 Output
    UE::Audio::MetaSoundUtils::ConnectNodes(Document, SineNode->GetID(), TEXT("Out"), OutputNode->GetID(), TEXT("In"));

    // 4. 应用文档到资产
    DynamicMetaSoundSource->SetDocument(Document);

    // 5. 播放
    if (!AudioComponent)
    {
        AudioComponent = NewObject<UAudioComponent>(GetOwner());
        AudioComponent->RegisterComponent();
    }
    AudioComponent->SetSound(DynamicMetaSoundSource);
    AudioComponent->Play();
}
```

## 模块依赖

从 .uplugin 的 `Plugins` 字段和常见实践推断，使用此插件需要以下**独特**依赖：

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心运行时和编辑器框架，是此插件的基础。 |
| `ModelViewViewModel` | 提供 MVVM 框架，用于构建插件中 `TechAudioToolsMetaSoundEditor` 模块的编辑器 UI（如自定义视图模型）。 |

*注意：使用者自己的模块 Build.cs 还需添加对 `TechAudioTools`, `TechAudioToolsMetaSound` 等模块的依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合了 MetaSound 引脚类型注册及相关的编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退了一个导致持续集成编译错误的改动。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册（前一版本的更新）。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound Literal 的视图模型添加了撤销/重做事务支持。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 `DocumentConfiguration` 重命名为更准确的 `MetaSoundTemplate`。 |

### 维护评价

-   **状态**：**活跃开发中**。
-   **创建时间**：2025年4月，是一个非常年轻的插件（约1年）。
-   **更新频率**：最近一个月内有多次实质性功能提交和整合，显示开发正在积极进行。
-   **实验性**：明确标记为实验性和测试版，意味着 API 和功能集未来可能发生重大变化。
-   **推荐**：**对于前沿音频项目或需要深度定制 MetaSound 工作流的团队强烈推荐尝试**。但不建议用于对稳定性要求极高的生产环境，需接受其 API 变动的风险。作为 Epic 官方出品的实验性工具，代表了 MetaSound 生态系统的未来发展方向。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/TechAudioTools/Source/TechAudioTools/Tests/) （位于 `TechAudioTools` 模块内）