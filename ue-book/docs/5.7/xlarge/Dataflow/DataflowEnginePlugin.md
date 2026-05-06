# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据流图 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、网格体数据） |
| 模块 | `DataflowAssetTools` (Runtime), `DataflowEditor` (Runtime), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow) | |

## 用途

Dataflow 插件为 UE 编辑器提供基于节点的可视化数据流图系统，允许用户通过连接节点来定义和处理几何体数据（如网格体、点云、集合等）。其核心机制是通过 `FManagedArrayCollection` 在多节点之间传递结构化数据，支持实时预览和迭代。

`DataflowEnginePlugin` 模块是运行时组件，负责在编辑器或游戏世界中渲染和可视化 Dataflow 图产生的几何体结果。它提供了 `UDataflowComponent`（用于挂载渲染数据）和 `ADataflowActor`（方便在场景中放置），并通过场景代理、命中代理等实现交互式选择。

## 使用场景

- 你正在开发程序化几何体生成工具，希望用可视化节点编排算法流。
- 你需要将 Dataflow 图的计算结果实时显示在 3D 视口中，并支持用户点击选择顶点/面。
- 你需要在运行时（如编辑器预览或 Standalone Game）中播放 Dataflow 生成的动态几何体序列。

## 蓝图用法

本模块不直接提供蓝图可调用的节点（`UFUNCTION(BlueprintCallable)`），但通过 `UPROPERTY(BlueprintReadOnly)` 暴露了组件引用，可在蓝图中获取并用于数据传递。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDataflowComponent (节点)` | 获取 DataflowActor 上的 DataflowComponent | `ADataflowActor`（通过蓝图访问其公开属性） |
| 无（函数未标记为蓝图可调用） | | |

**注**：若要执行 Dataflow 的计算或修改渲染集合，需在 C++ 中实现自定义蓝图节点或使用 DataflowNodes 模块提供的预置节点。

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/DataflowActor.h"
#include "Dataflow/DataflowComponent.h"
```

### 基本用法

```cpp
// 在编辑器或世界中生成一个 DataflowActor
ADataflowActor* DataflowActor = World->SpawnActor<ADataflowActor>(ADataflowActor::StaticClass(), SpawnLocation, SpawnRotation);
UDataflowComponent* DataflowComp = DataflowActor->GetDataflowComponent();

// 设置 Dataflow 资产（假设已有一个 UDataflow* 对象）
DataflowComp->SetDataflow(MyDataflow);

// 设置渲染集合（从某个 Dataflow 上下文获取的 FManagedArrayCollection）
FManagedArrayCollection NewCollection;
// ... 填充集合数据 ...
DataflowComp->SetRenderingCollection(MoveTemp(NewCollection));

// 设置选择状态（用于高亮）
FDataflowSelectionState State(FDataflowSelectionState::EMode::DSS_Dataflow_Vertex);
State.Vertices = { 0, 5, 12 };
DataflowComp->SetSelectionState(State);

// 标记组件更新渲染
DataflowComp->Invalidate();
```

**来源文件**：`Public/Dataflow/DataflowActor.h`, `Public/Dataflow/DataflowComponent.h`

### 进阶用法

```cpp
// 注册渲染目标（仅渲染特定节点输出的几何体）
const UDataflowEdNode* Node = ...; // 从 Dataflow 图获取
DataflowComp->AddRenderTarget(Node);

// 重置渲染目标，回归全部节点输出
DataflowComp->ResetRenderTargets();

// 设置上下文（用于节点求值）
TSharedPtr<UE::Dataflow::FContext> Context = MakeShared<UE::Dataflow::FContext>();
DataflowComp->SetContext(Context);

// 获取并修改渲染集合
FManagedArrayCollection& Col = DataflowComp->ModifyRenderingCollection();
Col.AddAttribute<FVector>("Vertices", "Point");
```

## Demo 示例

以下是一个在游戏世界 Spawn 场景中创建 DataflowActor 并设置简单渲染集合的最小 C++ 示例。此代码应放置于 `YourModule` 的某个 `.cpp` 文件中（需包含对应 include）。

```cpp
// DemoDataflowActorSpawner.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DemoDataflowActorSpawner.generated.h"

UCLASS()
class ADemoDataflowActorSpawner : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SpawnDataflowActor(const UDataflow* DataflowAsset);
};
```

```cpp
// DemoDataflowActorSpawner.cpp
#include "DemoDataflowActorSpawner.h"
#include "Dataflow/DataflowActor.h"
#include "Dataflow/DataflowComponent.h"
#include "GeometryCollection/ManagedArrayCollection.h"

void ADemoDataflowActorSpawner::SpawnDataflowActor(const UDataflow* DataflowAsset)
{
    if (!DataflowAsset || !GetWorld()) return;

    FActorSpawnParameters Params;
    ADataflowActor* Actor = GetWorld()->SpawnActor<ADataflowActor>(
        ADataflowActor::StaticClass(),
        GetActorLocation() + FVector(0, 0, 100),
        FRotator::ZeroRotator,
        Params
    );
    if (Actor)
    {
        UDataflowComponent* Comp = Actor->GetDataflowComponent();
        Comp->SetDataflow(DataflowAsset);

        // 创建一个简单的三角形集合
        FManagedArrayCollection Collection;
        TManagedArray<FVector>& Vertices = Collection.AddAttribute<FVector>("Vertices", "Point");
        TManagedArray<FIntVector>& Triangles = Collection.AddAttribute<FIntVector>("Indices", "Face");
        Vertices.Add(FVector(0,0,0));
        Vertices.Add(FVector(100,0,0));
        Vertices.Add(FVector(50,100,0));
        Triangles.Add(FIntVector(0,1,2));

        Comp->SetRenderingCollection(MoveTemp(Collection));
        Comp->Invalidate();
    }
}
```

## 模块依赖

`DataflowEnginePlugin` 在 `Build.cs` 中可能会依赖以下独特模块（常见模块已省略）：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionEngine` | 提供 `FManagedArrayCollection` 及其序列化/渲染支持 |
| `DataflowCore` | 核心数据流图框架（节点、上下文） |
| `DataflowNodes` | 运行时节点定义，用于连接和计算 |
| `DataflowEditor` （编辑器环境） | 编辑器内的图编辑器与预览场景，但在运行时可能不必要 |

**注意**：实际依赖需以 `Build.cs` 为准，以上为根据头文件 `#include` 推断。

## 维护状态

### 近期更新

- 2025-11-18 `296af658` Dataflow : make sure we mark the dataflow package dirty when the tools are committing their values
- 2025-10-16 `8b858c13` Unshelved from pending changelist '46933319':
- 2025-10-03 `7f04ddbd` Dataflow : fix cancelled close request causing the preview actor to be deleted and subsequent calls
- 2025-10-03 `71e223a6` Dataflow: (可能包含功能增强或重构)
- 2025-10-02 `aba7c452` Disable the dataflow slow task progress notification for now as this is causing UI focus issues

### 维护评价

- **创建时间**：2025-10-02，至今约 1 个月。
- **更新频率**：最近一个月内有多次提交，涉及 Bug 修复（关闭请求导致 Actor 删除）、UI 问题（进度通知）、数据标记等。表明该插件正处于积极开发和迭代阶段。
- **活跃度**：活跃维护中，但版本号仍为 0.1，且标记为实验性，API 可能随时变动。
- **风险**：作为实验性插件，部分功能可能不稳定，尤其是在不同引擎版本间可能存在不兼容。建议仅用于原型开发和测试，生产项目需谨慎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow/Tests)（可能存在，但当前模块未单独提供）