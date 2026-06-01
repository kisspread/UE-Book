# Motion Design Transition Logic

> 转场逻辑模块，用于协调多个场景或关卡之间的平滑过渡与状态管理。

| 属性 | 值 |
|---|---|
| 中文名 | 转场逻辑 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheTransition` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheTransition) | |

## 用途

AvalancheTransition 模块解决了虚拟制作（Virtual Production）中多场景/多关卡动态切换时的协调与过渡管理问题。它提供了一个基于 **State Tree（状态树）** 的框架，用于定义和执行“转场行为”（Transition Behavior）。其核心在于允许开发者为场景的“进入”（In）和“退出”（Out）过程分别设计复杂的逻辑流，这些逻辑流可以响应事件、检查状态、并与其他场景的转场逻辑进行交互，从而实现平滑、可控且同步的场景切换效果。这在广播、现场活动和需要实时切换多个虚拟布景的生产中至关重要。

## 使用场景

-   你在进行一场虚拟直播，需要从“采访场景”切换到“舞台全景”，并且要求当前场景淡出的同时，下一个场景的灯光和摄像机位需要提前就绪。
-   你管理着多个虚拟关卡（Level），希望它们能够按特定顺序、条件或时间触发进行加载、卸载和显示，并在此过程中协调动画、媒体播放等。
-   你需要为不同的场景过渡创建可重用、可组合的逻辑，例如“等待所有其他层动画播放完毕后再切换”或“如果遇到网络错误则回退到备用场景”。

## 蓝图用法

本模块的蓝图 API 主要集中在 `UAvaTransitionLibrary` 函数库中，用于查询和监控当前世界中的转场状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTransitionContext` | 从上下文对象（通常是 Actor 或组件）获取其关联的转场上下文信息。 | `UAvaTransitionLibrary` |
| `IsTransitionActiveInLayers` | 判断指定层（Layer）中是否正在进行转场。可按层类型（相同、不同、特定）和转场类型（进入、退出）过滤。 | `UAvaTransitionLibrary` |
| `AreScenesTransitioning` | 判断除了自身场景外，指定层中是否还有其他场景正在参与转场。 | `UAvaTransitionLibrary` |
| `GetTransitionBehavior` | 获取指定上下文对象关联的转场行为接口。 | `UAvaTransitionLibrary` |
| `GetTransitionTree` | 获取指定上下文对象关联的转场状态树资产。 | `UAvaTransitionLibrary` |

### 使用示例（蓝图描述）

1.  **查询当前场景转场状态**：
    *   在场景中的某个 Actor（例如管理器 Actor）的蓝图中，调用 `Get Transition Context` 节点，将 `Self` 作为上下文对象输入。
    *   将其输出连接到 `Is Transition Active In Layers` 节点。设置 `Layer Comparison Type` 为 `Same`（查询自身所在层）。
    *   该节点会返回一个布尔值，表示当前场景的转场逻辑是否正在运行。

2.  **检查是否有其他场景正在进入**：
    *   同样获取转场上下文。
    *   调用 `Are Scenes Transitioning` 节点。将 `Layers` 参数设置为希望监控的层（可以是特定标签容器）。
    *   在 `Scenes to Ignore` 中，将当前场景的 World 资产引用添加进去（通过其他方式获取）。
    *   如果返回 `true`，则表示有其他场景正在该层进行转场。

## C++ 用法

本模块的核心在于通过实现 `IAvaTransitionBehavior` 接口和创建自定义的 State Tree 任务/条件节点来扩展转场逻辑。

### 头文件引入

```cpp
#include "AvalancheTransition/Public/IAvaTransitionBehavior.h"
#include "AvalancheTransition/Public/AvaTransitionTree.h"
```

### 基本用法

从 `AAvaTransitionBehaviorActor` 的实现可以窥见核心用法：一个 Actor 可以通过拥有一个 `UAvaTransitionTree` 和实现 `IAvaTransitionBehavior` 接口，来定义自身的转场逻辑。

**文件路径：** `Private/Behavior/AvaTransitionBehaviorActor.h`

```cpp
// 一个简化的自定义转场行为 Actor 结构示意
UCLASS()
class AMyTransitionActor : public AActor, public IAvaTransitionBehavior
{
    GENERATED_BODY()
public:
    // IAvaTransitionBehavior 接口实现
    virtual UObject& AsUObject() override { return *this; }
    virtual UAvaTransitionTree* GetTransitionTree() const override;
    virtual FAvaTagHandle GetTransitionLayer() const override { return MyTransitionLayer; }
    virtual bool IsEnabled() const override { return bMyBehaviorEnabled; }
    // ... 其他接口方法实现

private:
    UPROPERTY()
    TObjectPtr<UAvaTransitionTree> MyTransitionTreeAsset;

    UPROPERTY(EditAnywhere)
    FAvaTagHandle MyTransitionLayer;

    UPROPERTY(EditAnywhere)
    bool bMyBehaviorEnabled = true;
};
```

### 进阶用法

模块提供了丰富的内置 State Tree 节点（Tasks 和 Conditions）来构建逻辑。你也可以创建自定义节点。

**创建自定义任务节点：**

**文件路径：** `Public/Tasks/AvaTransitionDelayTask.h` (参考此结构)

```cpp
// 自定义任务：在转场中播放一个音效
USTRUCT(DisplayName = "Play Sound During Transition", Category = "Transition Logic")
struct FMyPlaySoundTransitionTask : public FAvaTransitionTask
{
    GENERATED_BODY()

    // 实例数据，可在编辑器中配置
    USTRUCT()
    struct FInstanceData
    {
        GENERATED_BODY()
        UPROPERTY(EditAnywhere)
        USoundBase* SoundToPlay;
    };
    using FInstanceDataType = FInstanceData;

    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override
    {
        FInstanceData* Data = Context.GetInputData<FInstanceData>();
        if (Data && Data->SoundToPlay)
        {
            UGameplay::PlaySound2D(GetWorld(), Data->SoundToPlay);
        }
        return EStateTreeRunStatus::Running; // 或 Succeeded
    }
    // ... 其他必要实现
};
```

## Demo 示例

一个最小化的自定义转场行为 Actor。

**MyTransitionActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AvalancheTransition/Public/IAvaTransitionBehavior.h"
#include "MyTransitionActor.generated.h"

class UAvaTransitionTree;

UCLASS(Blueprintable)
class AMyTransitionActor : public AActor, public IAvaTransitionBehavior
{
    GENERATED_BODY()
    
public:
    AMyTransitionActor();

    // IAvaTransitionBehavior Interface
    virtual UObject& AsUObject() override { return *this; }
    virtual UAvaTransitionTree* GetTransitionTree() const override;
    virtual FAvaTagHandle GetTransitionLayer() const override;
    virtual void SetTransitionLayer(FAvaTagHandle InLayer) override;
    virtual bool IsEnabled() const override;
    virtual void SetEnabled(bool bInEnabled) override;
    virtual EAvaTransitionInstancingMode GetInstancingMode() const override;
    virtual void SetInstancingMode(EAvaTransitionInstancingMode InMode) override;
    virtual const FStateTreeReference& GetStateTreeReference() const override;

protected:
    UPROPERTY(EditAnywhere, Category = "Transition Logic")
    FAvaTagHandle TransitionLayer;

    UPROPERTY(EditAnywhere, Category = "Transition Logic")
    bool bEnabled = true;

    UPROPERTY(EditAnywhere, Category = "Transition Logic")
    EAvaTransitionInstancingMode InstancingMode = EAvaTransitionInstancingMode::New;

    UPROPERTY(EditAnywhere, Category = "Transition Logic", meta = (Schema = "/Script/AvalancheTransition.AvaTransitionTreeSchema"))
    FStateTreeReference StateTreeReference;
};
```

**MyTransitionActor.cpp**
```cpp
#include "MyTransitionActor.h"
#include "AvalancheTransition/Public/AvaTransitionTree.h"

AMyTransitionActor::AMyTransitionActor()
{
    // 默认启用
    bEnabled = true;
}

UAvaTransitionTree* AMyTransitionActor::GetTransitionTree() const
{
    // 从 StateTreeReference 中获取实际的资产对象
    if (const UStateTree* StateTree = StateTreeReference.GetStateTree())
    {
        return Cast<UAvaTransitionTree>(StateTree);
    }
    return nullptr;
}

// ... 其他接口方法的简单实现，返回成员变量即可。
// 例如:
// FAvaTagHandle AMyTransitionActor::GetTransitionLayer() const { return TransitionLayer; }
// bool AMyTransitionActor::IsEnabled() const { return bEnabled; }
// ... 等等
```

## 模块依赖

从源码结构和类关系推断，使用本模块需要以下独特依赖（已排除 Core、Engine 等常见模块）：

| 模块 | 用途 |
|---|---|
| `StateTree` | 核心的状态树框架，所有转场逻辑基于此构建。 |
| `AvaTag` | 用于定义和识别“转场层”（Transition Layer）的标签系统。 |
| `AvalancheTransition` | （自身模块）提供基础接口、任务、条件和子系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将 Motion Design 的编辑器标签页（场景设置、大纲）归类到独立组。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown 页面设置时增加了 MRQ 分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added... | 在节目控制工具栏添加了页面加载选项（全部、下一个、选定），并新增了... |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，用于强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 视口：通过通知客户端视口关联或脱离状态，减少必需的样板代码。 |

### 维护评价

AvalancheTransition 模块是 **活跃维护中** 的。它作为 Motion Design 工具的核心部分，于 2025 年 5 月从实验性目录迁移到正式的 Virtual Production 插件中。截至 2026 年 5 月，其所属的插件仍有持续的功能性更新和优化。代码结构清晰，基于成熟的 State Tree 系统，设计模式（接口、行为实例、执行器）考虑周全，具备良好的扩展性。**推荐使用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheTransition)
-   官方文档（暂无）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)