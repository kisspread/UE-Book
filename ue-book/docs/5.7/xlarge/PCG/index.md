# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-13 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG) | |

## 用途

PCG 是一个用于在编辑器和运行时程序化填充世界内容的**可视化脚本框架**。它解决了手动放置大量重复或基于规则的内容（如植被、岩石、建筑布局、任务物品等）效率低下的问题。开发者通过连接节点图来定义生成规则、数据筛选、变换和放置逻辑，从而快速、可控地创建复杂的程序化内容。

## 使用场景

- **大型开放世界**：程序化生成地形上的植被、岩石、废墟等自然或人工装饰物。
- **关卡设计**：快速原型化并填充室内场景（家具、杂物）或城市街区（建筑、街道道具）。
- **动态内容**：在运行时根据游戏状态（如玩家位置、任务进度）动态生成或更新场景内容。
- **规则化布局**：创建遵循特定规则（如网格、随机散布、沿样条线）的物体布局。

## 蓝图用法

PCG 主要是一个编辑器工具，其运行时蓝图 API 相对有限，核心在于通过编辑器中的 PCG 图资产进行设计。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create PCG Component` | 在 Actor 上创建一个 PCG 组件，用于执行 PCG 图。 | `UPCGBlueprintHelpers` |
| `Execute` | 触发 PCG 组件执行其关联的 PCG 图。 | `UPCGComponent` |
| `Get Generated Data` | 获取 PCG 图执行后生成的输出数据（如点集、属性集）。 | `UPCGComponent` |
| `Get All PCG Components` | 获取 Actor 上所有的 PCG 组件。 | `UPCGBlueprintHelpers` |

### 使用示例（蓝图描述）

1.  在目标 Actor（如一个空的 Actor 或场景管理器）上，使用 `Create PCG Component` 节点添加一个 PCG 组件。
2.  将该组件的 `Graph` 属性设置为你在编辑器中创建的 PCG 图资产。
3.  在需要触发生成时（如 `BeginPlay` 或自定义事件），调用该组件的 `Execute` 节点。
4.  可以使用 `Get Generated Data` 节点来获取生成的数据，并用于后续逻辑（如统计生成物体数量）。

## C++ 用法

PCG 的 C++ 用法主要集中在扩展框架（创建自定义节点）和程序化控制执行流程。

### 头文件引入

```cpp
#include "PCGComponent.h"
#include "PCGGraph.h"
#include "PCGSubsystem.h"
```

### 基本用法

```cpp
// 在某个 Actor 的 BeginPlay 中触发 PCG 图执行
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 查找或创建 PCG 组件
    UPCGComponent* PCGComponent = FindComponentByClass<UPCGComponent>();
    if (!PCGComponent)
    {
        PCGComponent = NewObject<UPCGComponent>(this);
        PCGComponent->RegisterComponent();
    }

    // 设置要执行的 PCG 图（假设 GraphAsset 已在编辑器中设置或通过代码加载）
    PCGComponent->SetGraph(GraphAsset);

    // 触发执行
    PCGComponent->Generate();
}
```
*(来源：基于 `UPCGComponent` API 的通用用法)*

### 进阶用法

更复杂的用法涉及监听生成完成事件、清理生成数据，或创建自定义的 PCG 节点（`UPCGSettings` 子类）来扩展框架功能。详细 API 请参考各模块文档。

## Demo 示例

一个最小的 C++ 示例，展示如何在 Actor 中集成 PCG 组件并执行图。

**MyPCGActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyPCGActor.generated.h"

class UPCGComponent;
class UPCGGraph;

UCLASS()
class AMyPCGActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPCGActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "PCG")
    TObjectPtr<UPCGComponent> PCGComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "PCG")
    TObjectPtr<UPCGGraph> PCGGraph;
};
```

**MyPCGActor.cpp**
```cpp
#include "MyPCGActor.h"
#include "PCGComponent.h"
#include "PCGGraph.h"

AMyPCGActor::AMyPCGActor()
{
    PCGComponent = CreateDefaultSubobject<UPCGComponent>(TEXT("PCGComponent"));
    RootComponent = PCGComponent;
}

void AMyPCGActor::BeginPlay()
{
    Super::BeginPlay();

    if (PCGGraph)
    {
        PCGComponent->SetGraph(PCGGraph);
        PCGComponent->Generate();
    }
}
```

**YourModule.Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "PCG" // 主要依赖 PCG 运行时模块
});
```

## 模块依赖

要使用 PCG 框架，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 核心运行时库，包含组件、图、数据等基础类型。 |
| `PCGCompute` | PCG 的计算后端，负责在 CPU 或 GPU 上执行节点逻辑。 |
| `PCGEditor` | PCG 的编辑器集成，包含图编辑器、节点自定义界面等。仅编辑器模块。 |

## 维护状态

### 近期更新

PCG 作为 UE5 的核心功能之一，由 Epic Games 持续积极维护和更新。其更新通常与引擎版本同步，包含性能优化、新节点、Bug 修复和功能增强。具体更新记录请查看各子模块文档。

### 维护评价

- **活跃维护**：PCG 是 UE5 程序化内容生成的战略性框架，自 2022 年引入以来持续获得大量投入和更新。
- **推荐使用**：对于需要程序化生成大量场景内容的项目，PCG 是官方推荐且功能强大的解决方案。它处于快速迭代期，新功能不断加入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG/Tests)