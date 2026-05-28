# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG (Procedural Content Generation) 是 UE5 提供的官方**可视化脚本框架**，其核心目标是解决**大规模、可控、可复用**的世界内容程序化生成问题。它不仅仅是一个随机放置工具，而是一个完整的图形化数据流系统，允许开发者通过连接不同功能的节点（PCG 节点）来定义复杂的内容生成规则。

这个框架的设计哲学是让美术、设计人员能够直观地“画出”生成逻辑，而无需编写大量 C++ 或蓝图代码。它通过将生成任务拆解为数据源（如点云、样条线）、生成器（如点采样器、表面采样器）、筛选器（如密度筛选、标签筛选）和执行器（如网格体放置器、生成器），来构建灵活且强大的生成管线。

## 使用场景

- **你正在开发一款开放世界游戏** → 用 PCG 来程序化地生成并管理整个地图的植被、岩石、树木和地面装饰物，实现基于生物群落或海拔的智能分布。
- **你需要在城市环境中快速填充大量建筑和物体** → 用 PCG 基于街区布局或样条线，程序化放置路灯、车辆、垃圾桶等街道物件，保持风格一致性并大幅提升关卡制作效率。
- **你需要在室内场景中布置大量家具和道具** → 用 PCG 基于房间边界和家具模板，智能地放置沙发、桌子、装饰品，并确保它们不会相互穿插。
- **你希望创建可重用的、参数化的环境生成规则** → 将 PCG 图打包为子图或蓝图资产，在不同项目或关卡间复用同一套生成逻辑。

## 蓝图用法

PCG 框架提供了丰富的蓝图函数和属性，用于在运行时或编辑器中与 PCG 图交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create PCGGraph` | 创建一个 PCG 图资产实例，是生成任务的起点。 | `UPCGBlueprintHelpers` |
| `Set PCGGraph Input` | 在执行 PCG 图之前，为其设置输入数据（如 Actor 列表、标签等）。 | `UPCGBlueprintHelpers` |
| `Execute PCGGraph` | 在游戏运行时执行指定的 PCG 图，触发整个生成流程。 | `UPCGBlueprintHelpers` |
| `Get PCGGraph Output` | 获取 PCG 图执行完成后产生的输出数据，例如生成的点集或 Actor 列表。 | `UPCGBlueprintHelpers` |
| `Clear PCG Results` | 清除由 PCG 图生成的所有结果（如动态生成的 Actor）。 | `UPCGBlueprintHelpers` |

### 使用示例（蓝图描述）

1.  **创建生成器：** 在蓝图中，首先使用 `Create PCGGraph` 节点创建一个图实例。
2.  **配置输入：** 调用 `Set PCGGraph Input` 节点，将当前关卡中的地面 Actor 列表、需要生成的物体类型标签（如 “Rock”、“Tree”）等数据传递给该图。
3.  **执行生成：** 连接一个 `Execute PCGGraph` 节点，将其 “Graph” 引脚连接到上一步创建的图实例。通常在一个事件（如 `BeginPlay`）后调用此节点。
4.  **处理结果：** 执行后，可通过 `Get PCGGraph Output` 获取生成的数据（例如一个点数组，每个点代表一个待放置物体的位置、旋转和缩放）。后续可以使用 `Spawn Actor From Point` 等节点在这些位置生成实际的游戏物体。
5.  **清理：** 在需要重置场景时（如重新开始关卡），调用 `Clear PCG Results` 节点来销毁所有通过 PCG 动态生成的 Actor。

## C++ 用法

### 头文件引入

使用 PCG 框架的核心类通常需要引入以下头文件：

```cpp
#include "PCGGraph.h"
#include "PCGComponent.h"
#include "PCGBlueprintHelpers.h"
#include "PCGContext.h"
```

### 基本用法

从测试用例和官方用法中，最常见的操作是获取场景中的 PCG 组件并触发其执行。

```cpp
// 示例：在某个 Actor 上触发 PCG 组件重新生成
// (来源：PCG 蓝图节点内部逻辑及常见使用模式)

// 1. 获取 Actor 身上的 PCG 组件
UPCGComponent* PCGComponent = MyActor->FindComponentByClass<UPCGComponent>();
if (PCGComponent)
{
    // 2. 标记组件需要清理（可选，取决于是否要先清除旧结果）
    PCGComponent->CleanupLocalImmediate(true);

    // 3. 标记组件需要生成
    PCGComponent->GenerateLocal(true);
}
```

### 进阶用法

可以通过继承 `UPCGSettings` 并重写 `GetDefaultNodeName` 和 `CreateElement` 来创建自定义的 PCG 节点。

```cpp
// 自定义 PCG 节点的简化示例
// (来源：PCG 框架扩展模式)

// MyCustomPCGSettings.h
UCLASS(BlueprintType, EditInlineNew, Category = "PCG")
class MYGAME_API UMyCustomPCGSettings : public UPCGSettings
{
    GENERATED_BODY()
public:
    // 节点输入输出定义
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;

    // 返回节点在编辑器中的名称
    virtual FName GetDefaultNodeName() const override { return FName(TEXT("MyCustomNode")); }

    // 返回创建执行元素的工厂
    virtual UPCGElement* CreateElement() const override;

    // 自定义属性
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Settings")
    float MyCustomValue = 1.0f;
};

// MyCustomPCGElement.h
UCLASS()
class UMyCustomPCGElement : public IPCGElement
{
    GENERATED_BODY()
public:
    // 核心执行逻辑
    virtual bool ExecuteInternal(FPCGContext* Context) const override;
};
```

## Demo 示例

一个简单的 PCG 图生成任务，通过 C++ 代码创建并执行。

```cpp
// MyPCGDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PCGGraph.h"
#include "PCGComponent.h"
#include "MyPCGDemo.generated.h"

UCLASS()
class AMyPCGDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyPCGDemo();

    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "PCG", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<UPCGComponent> PCGComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "PCG", meta = (AllowPrivateAccess = "true"))
    TSoftObjectPtr<UPCGGraph> MyPCGGraphAsset;
};
```

```cpp
// MyPCGDemo.cpp
#include "MyPCGDemo.h"
#include "PCGBlueprintHelpers.h"

AMyPCGDemo::AMyPCGDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建一个 PCG 组件作为默认子对象
    PCGComponent = CreateDefaultSubobject<UPCGComponent>(TEXT("PCGComponent"));
    RootComponent = PCGComponent;
}

void AMyPCGDemo::BeginPlay()
{
    Super::BeginPlay();

    // 检查资产是否有效
    if (MyPCGGraphAsset.IsValid())
    {
        UPCGGraph* Graph = MyPCGGraphAsset.LoadSynchronous();
        if (Graph)
        {
            // 将资产设置给组件
            PCGComponent->SetGraph(Graph);

            // 触发生成
            // 注意：直接调用 GenerateLocal(true) 会立即同步执行，可能卡顿。
            // 在实际项目中，通常由组件在适当时机自动或异步调用。
            PCGComponent->GenerateLocal(true);
        }
    }
}
```

## 模块依赖

要使用 PCG 框架，你的模块（如游戏模块）通常需要依赖以下不常见的模块：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架的核心运行时模块，包含所有基础类和执行逻辑。 |
| `PCGCompute` | 提供用于在 GPU 或异步计算任务上执行 PCG 节点的功能（用于性能密集型操作）。 |
| `Landscape` | PCG 与地形系统的集成，用于在地形上采样高度、材质等信息。 |
| `Foliage` | PCG 与植被系统的集成，用于程序化生成植被实例。 |
| `GeometryFramework` | 与几何体编辑工具的集成，可能用于动态网格体操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复在构建地形缓存时，某些条目无法解析可能导致的崩溃。 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化了 PCG 组件的可视化器性能。 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复了与访问器交互时空对象导致的崩溃。 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存了元数据大小计算，并通过一个带 TLS 支持的标志来控制，以确保常规路径不受影响。 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspectio | 修复了与手动编辑（及双重更新）和检查器相关的编辑器更新性能问题。 |

### 维护评价

PCG 框架自 2024 年初从实验性状态正式移出后，已成为 UE5 官方内容管线的核心组件。从近期的 git 记录看，**Epic Games 对其维护非常活跃**，最近的提交集中于**性能优化、稳定性修复和崩溃解决**，表明该框架正处于快速成熟和完善阶段。

**优点：**
- 官方支持，集成度高，与引擎其他系统（Landscape, Foliage）无缝对接。
- 持续的性能优化和 Bug 修复，稳定性不断提升。
- 文档和社区资源正在快速积累。

**建议：**
- 对于 5.4 及以后版本的新项目，强烈推荐使用 PCG 进行大规模程序化内容生成。
- 注意关注官方更新日志，因为框架API在快速发展中可能发生变化。
- 对于复杂的性能瓶颈，可考虑结合 `PCGCompute` 模块进行异步或GPU加速处理。

**总体评价：活跃维护，功能强大且不断进化，是 UE5 中进行程序化生成的最佳官方解决方案。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Tests/PCGTests)