# Actor Modifier

> Actual implementation of modifiers for actors based on ActorModifierCore plugin

| 属性 | 值 |
|---|---|
| 中文名 | Actor 修改器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorModifier` (Runtime), `ActorModifierEditor` (Runtime), `ActorModifierLayout` (Runtime), `ActorModifierRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier) | |

## 用途

Actor Modifier 插件是 **基于 ActorModifierCore 框架** 的**具体功能实现集合**。它解决的核心问题是：在虚拟制片（Virtual Production）工作流（特别是 Motion Design 相关场景）中，需要一种高效、可扩展的方式来**动态、批量地修改场景中 Actor 的各种属性**（如变换、可见性、布局等），并响应场景结构的变化。

其存在的意义在于：
1.  **提供开箱即用的修改器（Modifier）**：在 `ActorModifierCore` 提供的基础框架之上，本插件实现了具体的修改器逻辑，例如用于排列子Actor的基类 `UActorModifierArrangeBaseModifier`。
2.  **管理复杂的场景交互**：通过扩展（Extension）系统，自动监听并处理场景树（Scene Tree）结构变化、Actor变换更新、渲染状态变化等，确保修改器能及时响应环境变化并重新计算。
3.  **共享状态管理**：通过 `UActorModifierTransformShared` 和 `UActorModifierVisibilityShared` 等单例对象，安全地协调多个修改器对同一 Actor 状态（如变换、可见性）的修改和保存/恢复，避免冲突。

简单来说，它是让“修改Actor”这个动作变得更智能、更自动化的一套工具包。

## 使用场景

-   你在虚拟制片环境中，需要根据场景中其他Actor的排列（如列表、网格）自动调整一个Actor的位置和方向。
-   你需要批量控制一组Actor的可见性，并希望在某个条件满足时恢复它们的原始状态。
-   你正在开发一个Motion Design（动态设计）工具链，需要一套机制来监听场景变化并触发内容重排或重绘。
-   你需要自定义的Actor层次结构解析逻辑，并将其接入到修改器系统中。

## 蓝图用法

本插件的核心逻辑多为 C++ 扩展（Extension），提供给上层修改器或编辑器工具使用，直接暴露给蓝图的节点较少。其主要交互通过实现特定的 Handler 接口来完成。

### 核心接口与结构体

这些是插件中定义的主要蓝图友好数据结构和枚举，用于配置修改器的行为。

| 名称 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `EActorModifierReferenceContainer` | Enum | 定义如何根据父层级位置查找参考Actor（前一个、后一个、第一个、最后一个等）。 | `ActorModifierSceneTreeUpdateExtension.h` |
| `FActorModifierSceneTreeActor` | Struct | 配置一个被跟踪的Actor，包含其参考方式和是否跳过隐藏Actor。 | `ActorModifierSceneTreeUpdateExtension.h` |
| `EActorModifierAxis` | Enum (Bitflags) | 表示一个或多个坐标轴（X, Y, Z）。 | `ActorModifierTypes.h` |
| `FActorModifierAnchorAlignment` | Struct | 定义水平、垂直、深度三个方向的对齐方式（如左中右、上中下、前中后），用于确定边界框上的锚点。 | `ActorModifierTypes.h` |

### 使用示例（蓝图描述）

1.  **配置一个场景树跟踪对象**：
    在一个修改器的属性面板中，你可能会看到一个类型为 `FActorModifierSceneTreeActor` 的属性。在蓝图中，你可以创建一个该结构体的实例，将其 `ReferenceContainer` 设置为 `EActorModifierReferenceContainer::Previous`，并将其 `bSkipHiddenActors` 设置为 `true`，以此配置修改器“跟踪上一个可见的兄弟Actor”。

2.  **计算对齐偏移**：
    你可以使用 `FActorModifierAnchorAlignment` 结构体来描述你想要的对齐方式（例如：水平居中，垂直底部对齐，深度居中）。然后，调用其 `LocalBounds` 函数，并传入一个 Actor 的本地空间包围盒 (`FBox`)，即可得到从包围盒中心到对齐点的偏移向量 (`FVector`)。这个向量可用于定位或排列物体。

## C++ 用法

本插件的主要使用方式是**创建自定义的修改器或编辑器工具，并利用其提供的扩展（Extension）和共享状态系统**。

### 头文件引入

```cpp
// 核心功能与扩展
#include "Extensions/ActorModifierSceneTreeUpdateExtension.h"
#include "Extensions/ActorModifierRenderStateUpdateExtension.h"
#include "Extensions/ActorModifierTransformUpdateExtension.h"

// 共享状态管理
#include "Shared/ActorModifierTransformShared.h"
#include "Shared/ActorModifierVisibilityShared.h"

// 工具类
#include "Utilities/ActorModifierActorUtils.h"
```

### 基本用法：实现一个自定义修改器扩展

最典型的用法是让你的修改器类继承 `UActorModifierCoreBase`，并实现 `IActorModifierSceneTreeUpdateHandler` 接口来响应场景变化。

```cpp
// MyModifier.h
#pragma once
#include "Modifiers/ActorModifierAttachmentBaseModifier.h"
#include "MyModifier.generated.h"

UCLASS(MinimalAPI, Abstract)
class UMyModifier : public UActorModifierAttachmentBaseModifier // 继承自处理附件的基类
{
    GENERATED_BODY()

protected:
    // 实现接口：当被跟踪的Actor的子项列表发生变化时调用
    virtual void OnSceneTreeTrackedActorDirectChildrenChanged(int32 InIdx, const TArray<TWeakObjectPtr<AActor>>& InPreviousChildrenActors, const TArray<TWeakObjectPtr<AActor>>& InNewChildrenActors) override
    {
        // 例如：子项变了，标记修改器需要重新计算
        MarkModifierDirty();
    }

    // ... 其他必要的虚函数实现，如 OnModifierAdded, ApplyModifier 等
};
```

### 进阶用法：管理Actor的变换状态

当你需要临时修改一个Actor的变换（如移动、旋转），之后还想恢复原状时，应该使用 `UActorModifierTransformShared` 单例。

```cpp
// 在你的修改器逻辑中
void UMyTransformModifier::ApplyModifier()
{
    AActor* TargetActor = GetModifiedActor();
    // 获取共享状态管理器
    UActorModifierTransformShared* TransformShared = GetSharedObject<UActorModifierTransformShared>();
    
    // 在修改前，保存当前状态（只需保存一次，多次调用会更新跟踪列表）
    TransformShared->SaveActorState(this, TargetActor, EActorModifierTransformSharedState::LocationRotation);
    
    // ... 执行你的变换逻辑 ...
    TargetActor->SetActorLocation(NewLocation);
}

void UMyTransformModifier::UnapplyModifier()
{
    AActor* TargetActor = GetModifiedActor();
    UActorModifierTransformShared* TransformShared = GetSharedObject<UActorModifierTransformShared>();
    
    // 恢复之前保存的状态
    TransformShared->RestoreActorState(this, TargetActor, EActorModifierTransformSharedState::LocationRotation);
}
```

## Demo 示例

以下是一个最小的自定义修改器头文件和实现，它订阅场景树更新，并在子Actor列表变化时输出日志。

```cpp
// MySceneTreeListenerModifier.h
#pragma once
#include "Modifiers/ActorModifierAttachmentBaseModifier.h"
#include "MySceneTreeListenerModifier.generated.h"

UCLASS()
class UMySceneTreeListenerModifier : public UActorModifierAttachmentBaseModifier
{
    GENERATED_BODY()

public:
    // 设置修改器的元数据
    virtual void OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata) override;

protected:
    // 当添加到Actor时，开始跟踪自身的场景树状态（继承自父类）
    // 父类 OnModifierAdded 已包含使用 ReferenceActor 进行跟踪的逻辑

    // 实现接口函数
    virtual void OnSceneTreeTrackedActorDirectChildrenChanged(
        int32 InIdx,
        const TArray<TWeakObjectPtr<AActor>>& InPreviousChildrenActors,
        const TArray<TWeakObjectPtr<AActor>>& InNewChildrenActors) override
    {
        UE_LOG(LogTemp, Log, TEXT("Modifier [%s]: Tracked actor's direct children changed! Count: %d -> %d"),
            *GetModifierName().ToString(),
            InPreviousChildrenActors.Num(),
            InNewChildrenActors.Num());
    }
};

// MySceneTreeListenerModifier.cpp
#include "MySceneTreeListenerModifier.h"

void UMySceneTreeListenerModifier::OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata)
{
    // 调用父类设置（重要，会设置场景树跟踪）
    Super::OnModifierCDOSetup(InMetadata);
    
    // 设置修改器的显示名称和描述
    InMetadata.SetName(TEXT("MySceneTreeListener"));
    InMetadata.SetDescription(TEXT("Listens for children changes on its reference actor."));
}

// (需要添加相应的 .cpp 文件和 Build.cs 模块依赖)
```

## 模块依赖

要使用本插件的功能，你的项目模块通常需要依赖以下 **ActorModifier** 体系中的模块。其他依赖（如 `Core`, `Engine`）是标准依赖，已省略。

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 基础修改器框架、扩展接口、元数据系统。必须依赖。 |
| `ActorModifier` | 提供场景树、渲染状态、变换更新等核心扩展的具体实现。 |
| `ActorModifierLayout` | （如需）提供具体的布局排列相关修改器。 |
| `ActorModifierRendering` | （如需）提供具体的渲染相关修改器。 |

**典型 Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "ActorModifierCore", // 必需
    "ActorModifier"      // 使用核心扩展功能时需要
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update causing | 优化渲染状态脏标记机制，并修复了引发文本3D更新的问题。 |
| 2026-04-08 | `5c28c1d0` | Motion Design: added render state dirty reason scope for the modifier system to have a better idea o | 为修改器系统添加了渲染状态脏标记的原因作用域，以更好地判断更新来源。 |
| 2026-03-13 | `ab2df2c3` | Motion Design: moved usage of core ticker to custom ts ticker instance to better control timing. | 将核心计时器使用移至自定义的时间刻度实例，以更好地控制更新时序。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件重命名规范调整（内部维护）。 |
| 2025-09-23 | `cabb6e4f` | MotionDesign : ActorModifier | 插件从实验性路径迁移至正式的虚拟制片路径下的初始提交。 |

### 维护评价

-   **创建时间**：插件于 2025 年 5 月创建，非常年轻（约 1 年）。
-   **活跃度**：近期（2026年4月）仍有功能性更新和优化，表明该插件正在被积极开发和集成到 Motion Design 工作流中。
-   **状态**：**活跃维护中**。作为虚拟制片（Motion Design）工具链的一部分，是 Epic 重点开发的方向。
-   **已知限制**：插件的 `.uplugin` 明确标记为 `EnabledByDefault: false`，意味着这是一个**实验性功能**，默认不启用。用户需要手动启用，并且API可能会发生变化。
-   **推荐**：如果你在开发高级的虚拟制片或动态设计工具，并且需要强大的、响应式的Actor修改能力，**推荐研究和试用**此插件。但对于稳定性要求极高的核心游戏逻辑，鉴于其“实验性”标签，需谨慎评估并做好跟进更新的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的文件中发现)