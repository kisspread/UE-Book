# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | PCG框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时模块、编辑器模块、测试） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG 是一个程序化内容生成框架，它提供了一个基于蓝图的可视化脚本系统，用于在编辑器和运行时动态生成和填充世界内容。这个插件解决了大型开放世界游戏或程序化生成场景中的内容创建问题，允许开发者通过节点图定义生成规则，高效、可控地填充大量物体（如地形、植被、建筑、物品等），而无需手动放置每一个资产。它支持在编辑器中预览和烘焙生成结果，也支持在运行时动态生成，为游戏世界带来无限的变化和重玩价值。

## 使用场景

- 你需要在开放世界中自动放置数百万棵树木、岩石和草地，且希望它们根据地形坡度、高度和生物群落规则分布。
- 你正在制作一个 Roguelike 游戏，希望每一关的地图布局、敌人和道具都是随机生成的，但又要保证平衡性和可玩性。
- 你有一个大型场景，需要根据玩家的进度或游戏状态，在运行时动态加载或生成特定的区域内容。
- 你希望美术师或设计师能够通过一个易用的可视化节点图来定义生成规则，而无需编写代码。

## 蓝图用法

PCG 框架的核心是基于蓝图的图表系统。以下是主要的蓝图交互方式：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute PCG Graph` | 执行指定的 PCG 图表，进行内容生成。 | `UPCGSubsystem` |
| `Create PCG Graph Instance` | 在指定的执行器上创建一个 PCG 图表实例。 | `UPCGSubsystem` |
| `Get PCG Data` | 获取 PCG 图表执行后生成的数据（如点、属性等）。 | `APCGGraphExecutor` |
| `Cleanup PCG Graph` | 清理指定的 PCG 图表实例及其生成的内容。 | `UPCGSubsystem` |
| `Invalidate PCG Results` | 使 PCG 图表的执行结果失效，触发重新生成。 | `APCGPartitionActor` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `PCG Partition Actor` 或 `PCG Volume`。
2.  为其指定一个 `PCG Graph` 资产（一个由各种 PCG 节点组成的图表）。
3.  在图表中，使用 `Surface Sampler` 节点在地形上采样点，用 `Density Filter` 按距离过滤点，最后用 `Static Mesh Spawner` 节点在采样点上生成网格体。
4.  可以通过 `Blueprint Interface` 节点，将游戏运行时的参数（如玩家位置、游戏时间）传入图表，实现动态生成。

## C++ 用法

PCG 框架提供了强大的 C++ API，用于创建自定义的 PCG 节点、数据类型或与游戏逻辑深度集成。

### 头文件引入

```cpp
#include "PCGComponent.h"
#include "PCGSubsystem.h"
#include "PCGGraph.h"
```

### 基本用法

创建一个自定义的 PCG 节点（用于在图表中处理数据）。

*来源: Engine/Plugins/PCG/Source/PCG/Public/Elements/PCGPointProcessingElementBase.h*

```cpp
UCLASS(MinimalAPI)
class UPCGMyCustomNode : public UPCGSettings
{
    GENERATED_BODY()

public:
    UPCGMyCustomNode();

    // 定义节点的输入输出端口
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;

protected:
    // 执行节点的核心逻辑
    virtual FPCGElementPtr CreateElement() const override;
};

// 对应的执行元素
class FPCGMyCustomNodeElement : public IPCGElement
{
    virtual bool ExecuteInternal(FPCGContext* Context) const override;
};
```

### 进阶用法

从 C++ 代码中驱动 PCG 图表执行，并接收执行结果。

*来源: Engine/Plugins/PCG/Tests/PCGTests.cpp*

```cpp
// 获取场景中的 PCG 子系统
UPCGSubsystem* PCGSubsystem = UWorld::GetSubsystem<UPCGSubsystem>(World);

// 加载一个 PCG 图表资产
UPCGGraph* Graph = LoadObject<UPCGGraph>(nullptr, TEXT("/Game/PCGGraphs/MyPCGGraph"));

// 创建一个执行器并运行图表
FPCGGraphParams GraphParams;
GraphParams.InputData = ...; // 设置输入数据
FPCGGraphExecutor* Executor = PCGSubsystem->CreateGraphExecutor();
Executor->ExecuteGraph(Graph, GraphParams);

// 订阅执行完成的委托
Executor->OnGraphExecutionFinished().AddLambda([this](const FPCGGraphExecutor* InExecutor, const UPCGGraph* InGraph, bool bSuccess)
{
    if (bSuccess)
    {
        // 获取并处理生成的结果
        const FPCGDataCollection& OutputData = InExecutor->GetOutputData();
    }
});
```

## Demo 示例

一个最小的自定义 PCG 节点，用于将所有输入点的 Z 坐标向上移动一个固定值。

**PCGMoveZNode.h**
```cpp
#pragma once

#include "PCGSettings.h"
#include "PCGMoveZNode.generated.h"

UCLASS(MinimalAPI, BlueprintType)
class UPCGMoveZSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UPCGMoveZSettings();

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings)
    float ZOffset = 100.0f;

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
    virtual FPCGElementPtr CreateElement() const override;
};

// 执行元素类（通常在 .cpp 中定义，此处为简洁放入同一文件）
class FPCGMoveZElement : public IPCGElement
{
public:
    virtual bool ExecuteInternal(FPCGContext* Context) const override;
};
```

**PCGMoveZNode.cpp**
```cpp
#include "PCGMoveZNode.h"
#include "PCGContext.h"
#include "PCGPoint.h"
#include "Data/PCGPointData.h"

UPCGMoveZSettings::UPCGMoveZSettings()
{
    // 设置节点在编辑器中的类别
    Category = TEXT("My Custom Nodes");
}

TArray<FPCGPinProperties> UPCGMoveZSettings::InputPinProperties() const
{
    TArray<FPCGPinProperties> Pins;
    Pins.Emplace(PCGPinConstants::DefaultInputLabel, EPCGDataType::Point);
    return Pins;
}

TArray<FPCGPinProperties> UPCGMoveZSettings::OutputPinProperties() const
{
    TArray<FPCGPinProperties> Pins;
    Pins.Emplace(PCGPinConstants::DefaultOutputLabel, EPCGDataType::Point);
    return Pins;
}

FPCGElementPtr UPCGMoveZSettings::CreateElement() const
{
    return MakeShared<FPCGMoveZElement>();
}

bool FPCGMoveZElement::ExecuteInternal(FPCGContext* Context) const
{
    const UPCGMoveZSettings* Settings = Context->GetInputSettings<UPCGMoveZSettings>();
    check(Settings);

    const TArray<FPCGTaggedData> Inputs = Context->InputData.GetInputsByPin(PCGPinConstants::DefaultInputLabel);
    TArray<FPCGTaggedData>& Outputs = Context->OutputData.TaggedData;

    for (const FPCGTaggedData& Input : Inputs)
    {
        const UPCGPointData* PointData = Cast<const UPCGPointData>(Input.Data);
        if (!PointData)
        {
            continue;
        }

        UPCGPointData* OutputPointData = NewObject<UPCGPointData>();
        OutputPointData->InitializeFromData(PointData);
        OutputPointData->GetMutablePoints() = PointData->GetPoints();

        // 修改所有点的 Z 坐标
        for (FPCGPoint& Point : OutputPointData->GetMutablePoints())
        {
            Point.Transform.AddToTranslation(FVector(0, 0, Settings->ZOffset));
        }

        FPCGTaggedData& Output = Outputs.Emplace_GetRef();
        Output.Data = OutputPointData;
        Output.Pin = PCGPinConstants::DefaultOutputLabel;
        Output.Tags = Input.Tags;
    }

    return true;
}
```

## 模块依赖

要使用 PCG 框架的完整功能，你的模块可能需要依赖以下 PCG 特有的模块（已省略常见的 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `PCG` | 核心运行时框架，包含基础节点、数据类型和子系统。 |
| `PCGCompute` | 提供计算相关的支持，用于节点的数据处理。 |
| `PCGEditor` | 编辑器集成，包括 PCG 图表编辑器、自定义节点工厂和可视化。 |

对于简单的运行时 PCG 使用（如执行已有图表），通常只需依赖 `PCG` 模块。如果要开发自定义编辑器节点或工具，则需要额外依赖 `PCGEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复了在构建地形缓存时，某些条目无法解析可能导致的崩溃。 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化了PCG组件的可视化器性能。 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复了访问器为空对象时导致的崩溃。 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存了元数据大小的计算，并通过一个带TLS支持的标志进行控制。 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspectio | 修复了与手动编辑和检查相关的编辑器更新性能问题（及双重更新）。 |

### 维护评价

PCG 框架是一个相对较新的插件，于 2024 年初从实验状态移出。尽管创建时间不长，但其在 2026 年 5 月仍有**非常活跃的更新**，近期提交集中在性能优化和关键崩溃修复上。这表明该框架仍在由 Epic Games 积极维护和改进，是 UE5 程序化内容生成的核心官方解决方案。没有发现废弃迹象，推荐在所有需要程序化生成世界内容的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [模块文档（PCG核心）](docs/large/PCG/PCG.md)
- [模块文档（PCGCompute）](docs/large/PCG/PCGCompute.md)
- [模块文档（PCGEditor）](docs/large/PCG/PCGEditor.md)
- [模块文档（PCGTests）](docs/large/PCG/PCGTests.md)