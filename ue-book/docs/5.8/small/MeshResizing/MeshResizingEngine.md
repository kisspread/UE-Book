# Mesh Resizing

> Mesh Resizing（网格调整）

| 属性 | 值 |
|---|---|
| 中文名 | 网格调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流节点） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

Mesh Resizing 是一个用于直接编辑和调整静态网格体几何形状的实验性插件。其核心目标是在保持网格体UV布局和拓扑结构基本不变的前提下，实现对网格体大小和形状的快速、非破坏性编辑。

该插件解决了游戏和虚拟制片开发中的一个常见痛点：美术和设计师经常需要快速调整角色、道具或场景资产的尺寸以适应不同需求（例如，为不同体型的角色定制服装），但传统的缩放（Scale）会均匀拉伸UV，导致纹理变形，而重新建模则效率低下。Mesh Resizing 提供了一种更直观、更符合艺术工作流的解决方案，它可能通过数据流节点和编辑器工具集成，允许用户以更精细的方式控制网格体的各个部分。

## 使用场景

*   **角色资产定制**：当你需要为不同体型（如高、矮、胖、瘦）的角色快速调整同一套服装或装备模型，同时要求衣物上的图案或材质细节保持正确的比例和位置时。
*   **建筑和场景资产适配**：需要将一扇门、窗户或家具模型调整到精确的尺寸以适配不同的建筑模块，且不希望窗框、雕花等细节的纹理被拉伸。
*   **原型设计与快速迭代**：在原型阶段，需要快速测试一个物体在场景中不同尺寸下的视觉效果，而不想破坏已有的UV映射，以便后续快速回退或调整。

## 蓝图用法

该插件主要通过 `UMeshResizeSubsystem` 和 `UMeshResizingBlueprintLibrary` 暴露蓝图接口，用于在运行时控制网格调整过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Mesh Resize Subsystem` | 获取当前世界中的网格调整子系统实例，这是使用所有功能的基础。 | `UMeshResizingBlueprintLibrary` |
| `Initialize Resize Data` | 为指定的静态网格组件初始化调整所需的数据，通常在调整操作前调用。 | `UMeshResizeSubsystem` |
| `Resize` | 对已初始化的网格组件执行调整操作，指定目标尺寸或缩放因子。 | `UMeshResizeSubsystem` |
| `Reset Resize Data` | 将网格组件重置为其原始状态（调整前的状态）。 | `UMeshResizeSubsystem` |

### 使用示例（蓝图描述）

1.  **获取子系统**：在你的角色蓝图或任意Actor的事件图表中，使用 `Get Mesh Resize Subsystem` 节点，并连接当前世界上下文，以获取一个对 `UMeshResizeSubsystem` 的引用。
2.  **初始化目标网格**：找到你想要调整的静态网格组件（Static Mesh Component）引用，将其连接到 `Initialize Resize Data` 节点的输入。此步骤会计算并存储网格的基准数据。
3.  **执行调整**：调用 `Resize` 节点，将上一步获取的组件引用作为输入。通过节点的参数（如新的尺寸向量或相对缩放因子）来控制调整的方式和程度。
4.  **重置（可选）**：如果需要撤销调整，对同一个组件调用 `Reset Resize Data` 节点，即可恢复到调整前的状态。

## C++ 用法

该插件的 C++ 接口主要面向需要深度集成或编写自定义编辑器工具的程序员。核心操作与蓝图类似，但通过 C++ 代码直接调用可以更精细地控制流程和进行性能优化。

### 头文件引入

```cpp
// 引入网格调整引擎模块的核心头文件
#include "MeshResizingEngine.h"
// 如果需要使用蓝图库中的辅助函数
#include "MeshResizingBlueprintLibrary.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码对一个静态网格组件执行基本的调整操作。
*（示例灵感来源于 `MeshResizeSubsystemTest.cpp` 中的测试逻辑）*

```cpp
// 假设我们已经有了一个指向目标 UStaticMeshComponent 的指针: MyMeshComponent
// 以及一个有效的 UWorld* WorldContextObject

// 1. 获取网格调整子系统
UMeshResizeSubsystem* ResizeSubsystem = UMeshResizingBlueprintLibrary::GetMeshResizeSubsystem(WorldContextObject);
if (ResizeSubsystem)
{
    // 2. 为目标组件初始化调整数据
    // 该函数可能会在后台计算网格的边、面等拓扑信息以备调整使用。
    ResizeSubsystem->InitializeResizeData(MyMeshComponent);
    
    // 3. 定义新的尺寸 (例如，将物体在X轴方向上放大到1.5倍，Y/Z轴保持不变)
    FVector NewSize = FVector(1.5f, 1.0f, 1.0f);
    
    // 4. 执行调整操作
    // 参数可能包括是否沿特定轴约束、是否平滑过渡等。
    ResizeSubsystem->Resize(MyMeshComponent, NewSize /*, 其他可选参数*/);
    
    // 现在，MyMeshComponent 的几何形状已被调整，但UV和材质可能保持相对不变。
}
```

### 进阶用法

结合事件监听和动态调整。你可能希望在运行时根据游戏逻辑（如玩家输入或物理状态）连续地、平滑地调整网格大小。

```cpp
// 在某个更新循环或事件响应中 (例如 Tick 函数)
void AMyActor::AdjustMeshOverTime(float DeltaTime)
{
    if (UMeshResizeSubsystem* ResizeSubsystem = UMeshResizingBlueprintLibrary::GetMeshResizeSubsystem(GetWorld()))
    {
        // 假设已经初始化过数据
        // 计算一个随时间变化的目标尺寸
        FVector DesiredSize = FVector(FMath::Sin(GetGameTimeSinceCreation()) * 0.5f + 1.0f);
        
        // 执行调整，这可能会在每帧平滑地改变网格形状
        ResizeSubsystem->Resize(MyMeshComponent, DesiredSize);
    }
}

// 记得在不再需要时重置网格，以释放相关资源或恢复原始资产
void AMyActor::ResetMesh()
{
    if (UMeshResizeSubsystem* ResizeSubsystem = UMeshResizingBlueprintLibrary::GetMeshResizeSubsystem(GetWorld()))
    {
        ResizeSubsystem->ResetResizeData(MyMeshComponent);
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在 Actor 中集成网格调整功能。
```cpp
// MyAdjustableActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAdjustableActor.generated.h"

class UStaticMeshComponent;

UCLASS()
class AMyAdjustableActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyAdjustableActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = "Mesh Resizing")
    void AdjustMesh(const FVector& TargetSize);

    UFUNCTION(BlueprintCallable, Category = "Mesh Resizing")
    void ResetMesh();

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* MeshComponent;

    bool bIsInitialized = false;
};
```

```cpp
// MyAdjustableActor.cpp
#include "MyAdjustableActor.h"
#include "Components/StaticMeshComponent.h"
#include "MeshResizingEngine.h"
#include "MeshResizingBlueprintLibrary.h"

AMyAdjustableActor::AMyAdjustableActor()
{
    PrimaryActorTick.bCanEverTick = false; // 按需开启

    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;
}

void AMyAdjustableActor::BeginPlay()
{
    Super::BeginPlay();

    // 在BeginPlay中初始化，确保子系统已就绪
    if (UMeshResizeSubsystem* ResizeSubsystem = UMeshResizingBlueprintLibrary::GetMeshResizeSubsystem(GetWorld()))
    {
        if (MeshComponent && MeshComponent->GetStaticMesh())
        {
            ResizeSubsystem->InitializeResizeData(MeshComponent);
            bIsInitialized = true;
        }
    }
}

void AMyAdjustableActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 可在此添加动态调整逻辑
}

void AMyAdjustableActor::AdjustMesh(const FVector& TargetSize)
{
    if (!bIsInitialized) return;

    if (UMeshResizeSubsystem* ResizeSubsystem = UMeshResizingBlueprintLibrary::GetMeshResizeSubsystem(GetWorld()))
    {
        ResizeSubsystem->Resize(MeshComponent, TargetSize);
    }
}

void AMyAdjustableActor::ResetMesh()
{
    if (!bIsInitialized) return;

    if (UMeshResizeSubsystem* ResizeSubsystem = UMeshResizingBlueprintLibrary::GetMeshResizeSubsystem(GetWorld()))
    {
        ResizeSubsystem->ResetResizeData(MeshComponent);
        bIsInitialized = false; // 重置后需要重新初始化才能再次调整
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 用于实现基于节点图（Node Graph）的网格调整逻辑。 |
| `GeometryCore` | 提供底层的几何计算和处理工具，是进行网格拓扑分析和变形的基础。 |
| `Chaos` | 可能用于在调整后的网格上处理或关联物理模拟数据。 |
| `ModelingToolsEditorMode` | 与编辑器建模工具模式集成，可能为用户提供可视化的调整工具界面。 |
| `MeshResizingCore` | 本插件的核心类型和基础结构定义。 |
| `MeshResizingEngine` | 本插件的核心引擎和子系统逻辑。 |
| `MeshResizingEditorTools` | 提供编辑器内的专用工具和UI。 |
| `MeshResizingDataflowNodes` | 提供在数据流图表中使用的具体调整操作节点。 |

*注：省略了常见的 Core, CoreUObject, Engine, Slate, SlateCore 等依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量被截断为单精度的编译警告。 |
| 2026-05-12 | `a7802337` | Dataflow: | 数据流模块相关的更新（具体信息不足，可能为节点更新或API调整）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理前，添加了必要的头文件包含，为后续维护做准备。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 数据流：为绘画工具添加了套索选择支持，利用了网格模块中的新功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 数据流：更新了许多节点以使用新的渲染系统，属于功能演进。 |

### 维护评价

*   **活跃维护**：该插件创建于2024年底，属于较新的实验性项目。从提交记录看，2025年和2026年均有持续的实质性更新，包括功能添加（如套索工具）、节点渲染系统升级和代码质量改进（修复警告），表明其处于积极开发阶段。
*   **实验性**：`.uplugin` 文件明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着该插件处于早期开发阶段，API和功能可能会发生重大变化，不建议用于正式生产环境。
*   **推荐度**：对于想要探索前沿网格编辑技术或在原型阶段寻找高效资产调整方案的开发者，值得一试。但由于其实验性质，使用时需做好功能可能不完善、存在未知问题或未来需要适配API变更的心理准备。建议密切关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing/Tests) (基于提交记录 `MeshResizeSubsystemTest.cpp` 推断存在)