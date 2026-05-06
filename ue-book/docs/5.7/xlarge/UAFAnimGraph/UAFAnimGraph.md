# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | 动画图形框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画图形资产） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Runtime), `UAFAnimGraphTestSuite` (Runtime), `UAFAnimGraphUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAF Anim Graph 是 UE5 实验性动画框架 AnimNext 的核心运行时模块。它提供了一套基于“Trait（特性）”的动画图形定义和评估系统，用于替代传统动画蓝图。该插件解决了以下问题：

- **性能瓶颈**：通过预编译的 RigVM 字节码和二进制共享数据进行动画图评估，避免运行时反射和属性查找。
- **扩展性**：使用可组合的“Trait”模式，允许用户通过添加或组合特性（如混合、注入、同步组、事件调用等）来构建动画逻辑，无需创建大量 AnimNode 子类。
- **灵活性**：支持动态注入动画（如播放动画序列、蒙太奇）、运行时变量覆盖、混合栈、布尔条件混合等常见动画模式。
- **与现有系统集成**：提供 `FAnimNode_AnimNextGraph` 节点，可直接在传统动画蓝图中引用 AnimNext 图形，实现渐进式迁移。

## 使用场景

- **性能敏感的游戏**：如开放世界、大型多人在线游戏，需要高效的动画更新和内存布局。
- **复杂动画状态机**：需要混合多种动画源（如动作、跳跃、翻滚），通过“Blend Stack”特性轻松实现堆叠混合。
- **运行时动态注入**：例如播放过场动画或交互动作时，通过“Injection Site”特性向指定插槽注入动画，并控制混合过渡。
- **可扩展的动画管线**：团队需要创建自定义动画逻辑，基于 C++ Trait 模式避免重复实现 AnimNode 基础功能。

## 蓝图用法

以下蓝图节点基于 `UInjectionCallbackProxy` 和 `UPlayAnimCallbackProxy` 类，用于运行时注入和播放动画。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Inject` | 向指定注入站点注入一个对象（如图形、动画序列），并返回一个代理对象用于监听完成、中断或混合事件 | `UInjectionCallbackProxy` |
| `Uninject` | 取消一个之前发起的注入请求，使动画恢复为注入站点的默认源 | `UInjectionCallbackProxy` |
| `Set Variable (Injection Proxy)` | 在注入动画运行期间动态设置一个变量的值（需要事先定义变量覆盖） | `UInjectionCallbackProxy` |
| `Play Anim (AnimNext)` | 播放一个 `UAnimSequence` 到指定站点名称，并控制播放速率、起始位置和混合设置 | `UPlayAnimCallbackProxy` |
| `Get Reference Pose` | 获取指定 `USkeletalMeshComponent` 的参考姿态数据，用于动画图输入 | `UAnimNextSkeletalMeshComponentLibrary` |

### 使用示例（蓝图描述）

#### 播放动画并处理结束事件

1. 调用 `Play Anim (AnimNext)`，连接 `AnimNextComponent`、`SiteName`（如“Slot1”）、`AnimSequence`、`PlayRate` 等参数。
2. 从输出执行引脚（Completed / Blended Out / Interrupted）连接逻辑，例如播放完成后播放下一个动画。
3. 返回的 `UPlayAnimCallbackProxy` 实例会自动绑定事件，无需手动管理。

#### 动态注入图形并设置变量

1. 调用 `Inject` 节点，连接 `AnimNextComponent`、`Site`（一个 `FAnimNextVariableReference` 变量，指定注入站点）、`Object`（一个 `UAnimNextAnimationGraph` 资产）。
2. 从返回的 `InjectionCallbackProxy` 对象上调用 `Set Variable` 节点，选择预先定义的变量名并赋予新值。
3. 调用 `Uninject` 节点以退出注入状态，节点输出 `EUninjectionResult` 指示成功或失败。

## C++ 用法

### 头文件引入

```cpp
#include "Graph/AnimNextAnimationGraph.h"
#include "TraitCore/TraitWriter.h"
#include "TraitCore/TraitReader.h"
#include "TraitCore/NodeTemplateBuilder.h"
#include "Injection/InjectionRequest.h"
```

### 基本用法

#### 构建一个简单的动画图（运行时）

以下示例演示如何使用 `FTraitWriter` 和 `FNodeTemplateBuilder` 在 C++ 中构造一个包含单个 Trait 的图形，并生成共享数据。

```cpp
// 来源: Internal/TraitCore/NodeTemplateBuilder.h + Internal/TraitCore/TraitWriter.h

// 1. 获取要使用的 Trait 模板（例如，一个简单的“Call Function” Trait）
UE::UAF::FTraitRegistry& Registry = UE::UAF::FTraitRegistry::Get();
const UE::UAF::FTrait* MyTrait = Registry.Find(TEXT("CallFunction")); // 需要正确 FName

// 2. 构建节点模板
UE::UAF::FNodeTemplateBuilder Builder;
Builder.AddTrait(MyTrait->GetTraitUID());
TArray<uint8> TemplateBuffer;
UE::UAF::FNodeTemplate* NodeTemplate = Builder.BuildNodeTemplate(TemplateBuffer);

// 3. 注册节点实例到写入器
UE::UAF::FTraitWriter Writer;
FNodeHandle NodeHandle = Writer.RegisterNode(*NodeTemplate);
Writer.BeginNodeWriting();

// 4. 写入节点数据（假设我们使用默认的 Trait 共享数据）
Writer.WriteNode(NodeHandle,
    [](uint32 TraitIndex, FName PropertyName) -> uint16 { return 0; }, // 潜属性索引
    [](uint32 TraitIndex) -> TConstStructView<FAnimNextTraitSharedData> { return {}; } // 数据
);
Writer.EndNodeWriting();

// 5. 获取最终二进制数据
const TArray<uint8>& GraphData = Writer.GetGraphSharedData();
const TArray<UObject*>& References = Writer.GetGraphReferencedObjects();
```

#### 读取和反序列化图形

```cpp
// 来源: Internal/TraitCore/TraitReader.h

// ... 假设我们有一个包含图形数据的 FArchive& Archive
UE::UAF::FTraitReader Reader(GraphReferencedObjects, GraphReferencedSoftObjects, Archive);
TArray<uint8> OutSharedData;
EErrorState Error = Reader.ReadGraph(OutSharedData);
if (Error == UE::UAF::FTraitReader::EErrorState::None)
{
    // 成功：OutSharedData 包含了可直接使用的布局数据
    // 可以使用 Reader.ResolveNodeHandle() 来解析节点句柄
}
```

### 进阶用法

#### 使用注入系统播放动画

```cpp
// 来源: Internal/PlayAnim/PlayAnimCallbackProxy.h + Internal/Injection/InjectionCallbackProxy.h

UAnimNextComponent* AnimNextComponent = ...;
FName SiteName = "AnimationSlot1";
UAnimSequence* AnimToPlay = ...;

// 创建播放请求回调代理
UPlayAnimCallbackProxy* Proxy = UPlayAnimCallbackProxy::CreateProxyObjectForPlayAnim(
    AnimNextComponent,
    SiteName,
    AnimToPlay,
    1.0f,                   // PlayRate
    0.0f,                   // StartPosition
    FAnimNextInjectionBlendSettings(), // BlendIn
    FAnimNextInjectionBlendSettings()  // BlendOut
);

// 绑定委托
Proxy->OnCompleted.AddDynamic(this, &MyClass::OnAnimFinished);
Proxy->OnInterrupted.AddDynamic(this, &MyClass::OnAnimInterrupted);

// 如果需要提前取消，可以使用 Proxy->PlayingRequest 的 Stop 方法（内部）
```

#### 动态注入一个图形并设置变量覆盖

```cpp
// 来源: Internal/Injection/InjectionCallbackProxy.h

UAnimNextComponent* Component = ...;
FAnimNextVariableReference Site; // 从某处获取
UAnimNextAnimationGraph* GraphAsset = ...;
FAnimNextFactoryParams FactoryParams;

UInjectionCallbackProxy* Proxy = UInjectionCallbackProxy::CreateProxyObjectForInjection(
    Component,
    Site,
    GraphAsset,
    FactoryParams,
    FAnimNextInjectionBlendSettings(),
    FAnimNextInjectionBlendSettings()
);

// 设置一个变量
FAnimNextVariableReference VarRef; // 变量引用（需要提前获取）
Proxy->SetVariable(VarRef, 42);

// 取消注入
EUninjectionResult Result = Proxy->Uninject();
```

## Demo 示例

以下是一个完整的 C++ 类示例，演示如何在一个 Actor 中使用 `UAnimNextComponent` 播放动画序列。

```cpp
// MyActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UAnimNextComponent;
class UAnimSequence;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    UFUNCTION(BlueprintCallable, Category = "AnimNext")
    void PlayAnimationOnSlot(FName SlotName, UAnimSequence* Sequence, float PlayRate = 1.0f);

    UFUNCTION()
    void OnAnimCompleted();

    UFUNCTION()
    void OnAnimInterrupted();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Component")
    USkeletalMeshComponent* SkeletalMeshComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Component")
    UAnimNextComponent* AnimNextComponent;

private:
    UPlayAnimCallbackProxy* CurrentAnimProxy = nullptr;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "PlayAnim/PlayAnimCallbackProxy.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "UAFAnimGraph/Private/PlayAnim/PlayAnimCallbackProxy.h" // 需要正确路径

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
    SkeletalMeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>("Mesh");
    RootComponent = SkeletalMeshComponent;
    AnimNextComponent = CreateDefaultSubobject<UAnimNextComponent>("AnimNextComponent");
}

void AMyActor::PlayAnimationOnSlot(FName SlotName, UAnimSequence* Sequence, float PlayRate)
{
    if (!AnimNextComponent || !Sequence) return;

    // 取消之前的播放
    if (CurrentAnimProxy)
    {
        CurrentAnimProxy->Cancel();
        CurrentAnimProxy = nullptr;
    }

    // 创建播放代理
    CurrentAnimProxy = UPlayAnimCallbackProxy::CreateProxyObjectForPlayAnim(
        AnimNextComponent,
        SlotName,
        Sequence,
        PlayRate,
        0.0f,
        FAnimNextInjectionBlendSettings(),
        FAnimNextInjectionBlendSettings()
    );

    if (CurrentAnimProxy)
    {
        CurrentAnimProxy->OnCompleted.AddDynamic(this, &AMyActor::OnAnimCompleted);
        CurrentAnimProxy->OnInterrupted.AddDynamic(this, &AMyActor::OnAnimInterrupted);
    }
}

void AMyActor::OnAnimCompleted()
{
    UE_LOG(LogTemp, Log, TEXT("Animation finished."));
    CurrentAnimProxy = nullptr;
}

void AMyActor::OnAnimInterrupted()
{
    UE_LOG(LogTemp, Warning, TEXT("Animation interrupted."));
    CurrentAnimProxy = nullptr;
}
```

## 模块依赖

由于 `UAFAnimGraph` 是 AnimNext 框架的一部分，它依赖核心的 `UAF` 插件（提供基础类型如 `FTrait`, `FNodeTemplate` 等）。此外，它还依赖以下不常见的模块：

| 模块 | 用途 |
|---|---|
| `UAF` | 基础动画框架，提供 Trait 系统、执行上下文、模块管理等核心机制 |
| `RigVM` | 用于生成和运行预编译的动画图字节码 |
| `StructUtils` | 提供 `FInstancedStruct`、`TStructView` 等工具，用于处理动态结构化数据 |
| `AnimationCore` | 动画核心算法与数据结构（可能被 Trait 实现使用） |
| `AnimGraphRuntime` | 与现有动画蓝图节点（如 `FAnimNode_AnimNextGraph`）交互所需的运行时基类 |

**注意**：若在您的项目模块中使用 `UAFAnimGraph`，需在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "UAF",
    "RigVM",
    "StructUtils",
    "AnimationCore",
    "AnimGraphRuntime"
});
```

（常见依赖如 Core, Engine, Slate 等已省略。）

## 维护状态

### 近期更新

| 日期 | 提交 Hash | 说明 |
|---|---|---|
| 2025-10-01 | `6f23619b` | 将拖放操作的 UEdGraphSchema 资产引用过滤移到各自实现中 |
| 2025-09-03 | `bb48edd8` | 避免编辑器退出时无效内存访问 |
| 2025-09-03 | `bc59af4e` | 避免在旧版 UAF 内容上打开上下文菜单时崩溃 |
| 2025-09-02 | `78089693` | 为 UAF 姿势评估添加作用域命名事件 |
| 2025-08-29 | `3663a91d` | 修复 UAF RigVM 覆盖变量资产持久性 |

### 维护评价

该插件创建于 2025 年 8 月底，至今约 1 个月，属于全新实验性功能。从近期提交看，开发团队正在积极修复崩溃和稳定性问题，并持续进行功能迭代（如添加评估事件、修复资源持久性）。由于 `IsExperimentalVersion=true`，且处于早期开发阶段，**可能存在较多 bug 和 API 不稳定性**。推荐在实验性项目中使用，但需关注未来版本升级时的迁移成本。对于正式项目，建议等待版本稳定或与 Epic 官方沟通规划。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [官方文档](https://docs.unrealengine.com/unreal-engine-animnext/)（请参阅 AnimNext 文档，此插件为 AnimNext 组成部分）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph/Source/UAFAnimGraphTestSuite)