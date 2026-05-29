# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流图 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、运行时组件、场景代理） |
| 模块 | `DataflowEditor` (Editor), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow) | |

## 用途

DataflowGraph 是一个基于节点图的脚本系统，专门用于处理几何数据（如几何体集合、动态网格）。它提供了一个可视化编程环境，用户可以通过连接节点来定义数据流——从输入（如网格）经过一系列变换、破碎、变形等操作，最终输出结果。DataflowEnginePlugin 模块负责在运行时环境下承载和渲染这些数据流的结果，包括：

- 提供 `UDataflowComponent` 和 `ADataflowActor` 用于在场景中显示数据流生成的几何体。
- 支持选择、高亮、碰撞等交互（通过场景代理和命中代理）。
- 提供类型系统（如 `FDataflowDynamicMeshArray`）以便在节点间传递动态网格数组。
- 维护渲染目标集合，用于在编辑器中预览特定节点的输出。

与蓝图类似但面向几何操作，Dataflow 特别适合程序化建模、动态破坏（如 Chaos 破碎）以及实时几何编辑。

## 使用场景

- **程序化建模**：在运行时根据输入参数生成或变形网格，例如根据风场数据动态修改地形。
- **交互式破坏**：使用 Chaos 物理破坏后，将破碎碎片通过 Dataflow 重新组合并渲染。
- **编辑器工具**：在编辑器中用节点图编写几何处理逻辑，并实时预览结果（配合 `DataflowEditor` 模块）。
- **数据转换**：将不同格式的几何数据（如静态网格、动态网格、几何体集合）通过节点图转换并输出。

## 蓝图用法

该模块主要为 C++ 设计，蓝图暴露的接口有限。以下是从头文件中提取的可用于蓝图的类型和属性。

### 核心类型

| 节点 | 说明 | 所在类/结构 |
|---|---|---|
| `FCollectionAttributeKey` | 用于标识几何体集合中的属性（Attribute）和组（Group），可在蓝图中编辑。 | `DataflowConnectionTypes.h` |
| `ADataflowActor` | 在场景中放置的 Actor，自带一个 `UDataflowComponent`。 | `DataflowActor.h` |
| `UDataflowComponent` (部分属性) | 数据流组件，拥有 `RenderTargets` 等只读属性。 | `DataflowComponent.h` |

**注意**：`UDataflowComponent` 的 `AddRenderTarget`、`ResetRenderTargets`、`SetRenderingCollection` 等方法未标记 `BlueprintCallable`，因此仅限 C++ 调用。

### 蓝图使用示例

1. 在关卡中放置一个 `ADataflowActor`（蓝图类可以直接创建或放置）。
2. 获取其 `DataflowComponent`（`GetDataflowComponent` 节点，返回 `UDataflowComponent`）。
3. 通过 C++ 或编辑器工具设置 `Dataflow` 对象和渲染目标，蓝图不直接提供节点。

## C++ 用法

以下用法基于头文件提供的 API 和常规实践。

### 头文件引入

```cpp
#include "Dataflow/DataflowActor.h"
#include "Dataflow/DataflowComponent.h"
#include "Dataflow/DataflowEngineSceneProxy.h"
#include "Dataflow/DataflowConnectionTypes.h"
```

### 基本用法

**创建 Dataflow Actor 并获取组件**

```cpp
// 在 GameMode 或 Actor 中生成一个 DataflowActor
ADataflowActor* DataflowActor = GetWorld()->SpawnActor<ADataflowActor>(ADataflowActor::StaticClass(), SpawnLocation, SpawnRotation);
UDataflowComponent* DfComponent = DataflowActor->GetDataflowComponent();
```

**设置 Dataflow 对象和上下文**

```cpp
// 假设已有一个 UDataflow* 资源
UDataflow* MyDataflow = LoadObject<UDataflow>(nullptr, TEXT("/Game/MyDataflow"));
DfComponent->SetDataflow(MyDataflow);

// 设置上下文（通常由编辑器或运行时管理器提供）
TSharedPtr<UE::Dataflow::FContext> Context = MakeShared<UE::Dataflow::FContext>();
DfComponent->SetContext(Context);
```

**添加渲染目标并触发更新**

```cpp
// 获取数据流图中的某个节点，作为渲染目标
const UDataflowEdNode* NodeToDisplay = ...;
DfComponent->AddRenderTarget(NodeToDisplay);

// 设置渲染集合（从 Dataflow 评估结果中获取）
FManagedArrayCollection RenderCollection = /* ... */;
DfComponent->SetRenderingCollection(MoveTemp(RenderCollection));
DfComponent->Invalidate();  // 标记需要重新生成场景代理
```

**选择状态操作**

```cpp
FDataflowSelectionState SelectionState(FDataflowSelectionState::DSS_Dataflow_Vertex);
SelectionState.Vertices.Add(42);               // 选择顶点索引 42
SelectionState.Nodes.Emplace(TEXT("MeshNode"), 0);
DfComponent->SetSelectionState(SelectionState);
```

### 进阶用法

**自定义渲染代理（覆盖默认代理）**

```cpp
// 继承 FDataflowEngineSceneProxy 可以自定义渲染行为
class FMyDataflowSceneProxy : public FDataflowEngineSceneProxy
{
    // 重写 GetDynamicMeshElements 等
};
```

**使用类型策略（FDataflowDynamicMeshArray）**

```cpp
FDataflowDynamicMeshArray DynMeshArray;
// 赋值单个动态网格
UDynamicMesh* Mesh = NewObject<UDynamicMesh>();
DynMeshArray.Value = { Mesh };

// 使用 FDataflowConverter 在 TObjectPtr<UDynamicMesh> 和 TArray<TObjectPtr<UDynamicMesh>> 之间转换
TArray<TObjectPtr<UDynamicMesh>> Array;
FDataflowConverter<TArray<TObjectPtr<UDynamicMesh>>>::From<TObjectPtr<UDynamicMesh>>(Mesh, Array);
```

## Demo 示例

以下是一个完整的 C++ 示例，展示如何在运行时创建一个 DataflowActor 并关联一个简单的渲染集合。假设你已经有一个 `UDataflow` 资源和一个预计算的 `FManagedArrayCollection`。

### MyDataflowDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Dataflow/DataflowActor.h"
#include "MyDataflowDemo.generated.h"

UCLASS()
class AMyDataflowDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyDataflowDemo();

    virtual void BeginPlay() override;

protected:
    UPROPERTY(EditAnywhere, Category = "Dataflow")
    UDataflow* DataflowAsset = nullptr;

    UPROPERTY()
    ADataflowActor* DataflowActor = nullptr;
};
```

### MyDataflowDemo.cpp

```cpp
#include "MyDataflowDemo.h"
#include "Dataflow/DataflowComponent.h"
#include "GeometryCollection/ManagedArrayCollection.h"
#include "Engine/World.h"

AMyDataflowDemo::AMyDataflowDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDataflowDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!DataflowAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("DataflowAsset not set!"));
        return;
    }

    // 1. 创建 DataflowActor
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    DataflowActor = GetWorld()->SpawnActor<ADataflowActor>(ADataflowActor::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

    // 2. 获取 DataflowComponent
    UDataflowComponent* DfComp = DataflowActor->GetDataflowComponent();
    DfComp->SetDataflow(DataflowAsset);

    // 3. 构建一个简单的渲染集合（例如一个三角形）
    FManagedArrayCollection Collection;
    // 通常这里会从 Dataflow 评估获得，此处手动创建示例
    // 添加顶点组、面组、顶点位置等……
    // 简化：直接设置空集合
    DfComp->SetRenderingCollection(MoveTemp(Collection));

    // 4. 设置上下文并触发更新
    TSharedPtr<UE::Dataflow::FContext> Context = MakeShared<UE::Dataflow::FContext>();
    DfComp->SetContext(Context);
    DfComp->Invalidate();
}
```

## 模块依赖

从 `DataflowEnginePlugin.Build.cs` 提取（根据代码中 #include 推断）：

| 模块 | 用途 |
|---|---|
| `GeometryCollections` | 提供 `FManagedArrayCollection` 用于几何体集合数据 |
| `DataflowNodes` | 提供 `UDataflow`、`UDataflowEdNode` 等数据流基础类型 |
| `DynamicMesh` | 提供 `UDynamicMesh` 类型 |
| `RenderCore` | 渲染资源管理 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, Projects, DeveloperSettings。

**注意**：实际依赖以对应 `Build.cs` 为准，上述仅基于头文件引用推测。建议使用前检查 `Source/DataflowEnginePlugin/DataflowEnginePlugin.Build.cs`。

## 维护状态

### 近期更新

- 2026-04-25 `8450647a` Dataflow : make proximity renderable type use the exploded settings
- 2026-04-24 `ddbdf42c` Dataflow : add exploded view and hierarchical component to geometry collection rendering type
- 2026-04-24 `ca3cc903` Dataflow : fix time line issues
- 2026-04-23 `3bbaa3bc` Dataflow Editor : fix issue with reloading assets with embedded dataflow graph
- 2026-04-23 `23602a95` Dataflow: (此条被截断，推测为功能更新)

### 维护评价

- **创建时间**：2026-04-23，距今不到半年，属于非常新的插件。
- **更新频率**：连续多日有提交，活跃度高，修复问题并增加新功能（爆炸视图、层级组件等）。
- **稳定性**：版本号 0.1，仍处于早期阶段，API 可能变化。
- **推荐使用**：适合需要新式几何数据流处理的工程项目，但需注意版本升级时可能的 API 变更。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow)
- [官方文档](待官方补充)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow/DataflowEnginePlugin-Tests)（假设路径）