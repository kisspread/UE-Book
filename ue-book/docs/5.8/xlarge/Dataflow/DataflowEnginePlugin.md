# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质资产、场景代理） |
| 模块 | `DataflowEditor` (Runtime), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow) | |

## 用途

该插件提供了一套完整的**数据流（Dataflow）图系统**，主要用于在**编辑器**环境中可视化地构建、编辑和预览数据处理流程。其核心目标是让用户通过连接节点（Node）的方式处理数据，特别是针对几何体（Geometry）数据，如集合（Collection）、动态网格（DynamicMesh）等。

它解决了以下问题：
1.  **可视化数据流编程**：为复杂的数据处理逻辑（如几何体变形、破碎、网格操作）提供基于节点的图编辑界面。
2.  **编辑器内实时预览**：通过专用的组件和场景代理（SceneProxy），允许用户在3D视口中直接查看数据流节点的输出结果（如几何体、选择状态）。
3.  **与物理/破碎系统集成**：作为 Chaos Destruction 系统的一部分，支持对几何集合（GeometryCollection）等资产进行程序化编辑和效果预览。

## 使用场景

- 你正在使用 **Chaos Destruction** 系统制作破坏效果，需要以可视化节点图的方式程序化地修改或生成几何集合（GeometryCollection）数据。
- 你需要处理几何体集合（`FManagedArrayCollection`），并希望在编辑器中实时看到每个节点操作后的网格、顶点或面的渲染效果。
- 你开发了一个自定义的几何处理工具，希望为其提供一个用户友好的节点式编辑界面。
- 你想在编辑器中调试数据流，查看节点中间输出，例如哪些顶点或面被选中。

## 蓝图用法

`DataflowEnginePlugin` 模块中的 `UDataflowComponent` 是蓝图交互的核心。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRenderingCollection` | 设置组件用于渲染的几何集合数据。 | `UDataflowComponent` |
| `GetRenderingCollection` | 获取当前用于渲染的几何集合数据。 | `UDataflowComponent` |
| `ModifyRenderingCollection` | 获取可修改的几何集合数据的引用（用于就地修改）。 | `UDataflowComponent` |
| `SetDataflow` | 设置该组件关联的数据流资产。 | `UDataflowComponent` |
| `SetSelectionState` | 设置组件的选择状态（选择对象、面或顶点）。 | `UDataflowComponent` |
| `GetSelectionState` | 获取当前的选择状态。 | `UDataflowComponent` |
| `Invalidate` | 标记组件为无效，触发重新计算和渲染更新。 | `UDataflowComponent` |

### 使用示例（蓝图描述）

1.  **设置数据流**：
    在一个 `ADataflowActor` 的蓝图中，获取其 `DataflowComponent` 引用。
    使用 `SetDataflow` 节点，将一个 `UDataflow` 资产（代表一个数据流图）赋值给它。
2.  **提供输入数据**：
    从其他源（如一个几何集合资产）获取 `FManagedArrayCollection` 数据。
    调用 `SetRenderingCollection` 节点，将这个集合设置给 `DataflowComponent`。
3.  **触发更新与预览**：
    当输入数据改变或数据流图修改后，调用 `Invalidate` 节点。
    `DataflowComponent` 会重新执行关联的数据流图，并根据输出更新3D视口中的渲染内容。
4.  **交互选择**：
    用户可以在视口中点击网格。组件会通过 `HDataflowNode`、`HDataflowVertex` 等命中代理（HitProxy）捕获点击。
    组件内部会更新 `FDataflowSelectionState`。你可以通过 `GetSelectionState` 获取当前选择，并根据 `EMode`（对象、面、顶点）进行后续逻辑处理。

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/DataflowComponent.h"
#include "Dataflow/DataflowActor.h"
#include "Dataflow/DataflowConnectionTypes.h"
```

### 基本用法

以下示例展示如何在 C++ 中创建一个 `ADataflowActor` 并配置其组件。
(基于 `DataflowActor.h` 和 `DataflowComponent.h` 中的声明)

```cpp
// 在某个初始化函数中（例如 PostInitializeComponents）
void AMyActor::SetupDataflowActor()
{
    // 1. 生成一个DataflowActor
    FActorSpawnParameters SpawnParams;
    ADataflowActor* DataflowActor = GetWorld()->SpawnActor<ADataflowActor>(SpawnParams);

    // 2. 获取其核心组件
    UDataflowComponent* DFComponent = DataflowActor->GetDataflowComponent();
    if (DFComponent)
    {
        // 3. 加载一个数据流资产（假设路径已知）
        UDataflow* MyDataflowAsset = LoadObject<UDataflow>(nullptr, TEXT("/Game/Dataflows/DF_MyEffect"));
        
        // 4. 将资产赋给组件，建立关联
        DFComponent->SetDataflow(MyDataflowAsset);

        // 5. （可选）设置初始的几何集合数据
        FManagedArrayCollection MyCollection;
        // ... 填充MyCollection数据 ...
        DFComponent->SetRenderingCollection(MoveTemp(MyCollection));

        // 6. 使组件失效，以触发首次图计算和渲染
        DFComponent->Invalidate();
    }
}
```

### 进阶用法

**自定义视图模式**：
`UDataflowComponent` 通过 `SetViewMode` 接受一个 `IDataflowConstructionViewMode` 接口，允许你控制数据流图的视觉表现方式（例如，如何着色顶点、如何高亮选择）。
```cpp
// 假设你定义了一个自定义视图模式类
class FMyCustomViewMode : public UE::Dataflow::IDataflowConstructionViewMode
{
    // 实现接口方法，定义颜色方案等
};

// 在需要的时候设置
if (DFComponent)
{
    static FMyCustomViewMode MyViewMode;
    DFComponent->SetViewMode(&MyViewMode);
    DFComponent->Invalidate(); // 应用更改
}
```

**处理选择状态**：
当用户在视口中进行交互时，组件会更新其内部的 `FDataflowSelectionState`。你可以轮询或在事件中获取它。
```cpp
void AMyActor::ProcessDataflowSelection()
{
    if (UDataflowComponent* DFComp = FindComponentByClass<UDataflowComponent>())
    {
        const FDataflowSelectionState& SelState = DFComp->GetSelectionState();
        
        switch (SelState.Mode)
        {
        case FDataflowSelectionState::EMode::DSS_Dataflow_Object:
            UE_LOG(LogTemp, Log, TEXT("Selected %d dataflow nodes."), SelState.Nodes.Num());
            // 遍历 SelState.Nodes (TArray<ObjectID>) 获取名称和ID
            break;
        case FDataflowSelectionState::EMode::DSS_Dataflow_Vertex:
            UE_LOG(LogTemp, Log, TEXT("Selected %d vertices."), SelState.Vertices.Num());
            break;
        // ... 处理其他模式
        }
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个可渲染数据流输出的 Actor。

**MyDataflowActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDataflowActor.generated.h"

class UDataflowComponent;
class UDataflow;

UCLASS()
class MYPROJECT_API AMyDataflowActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDataflowActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 触发数据流重新计算 */
    UFUNCTION(BlueprintCallable)
    void ReevaluateDataflow();

private:
    /** 数据流组件 */
    UPROPERTY(VisibleAnywhere, Category = "Dataflow")
    TObjectPtr<UDataflowComponent> DataflowComponent;

    /** 要执行的数据流资产 */
    UPROPERTY(EditAnywhere, Category = "Dataflow")
    TObjectPtr<UDataflow> DataflowAsset;

    /** 用于测试的静态几何集合 */
    FManagedArrayCollection TestCollection;
};
```

**MyDataflowActor.cpp**
```cpp
#include "MyDataflowActor.h"
#include "Dataflow/DataflowComponent.h"

AMyDataflowActor::AMyDataflowActor()
{
    PrimaryActorTick.bCanEverTick = false;

    DataflowComponent = CreateDefaultSubobject<UDataflowComponent>(TEXT("DataflowComp"));
    RootComponent = DataflowComponent;
}

void AMyDataflowActor::BeginPlay()
{
    Super::BeginPlay();

    // 初始设置数据流资产
    if (DataflowAsset)
    {
        DataflowComponent->SetDataflow(DataflowAsset);
    }

    // 初始化一个简单的测试集合 (例如，一个平面)
    // 注意：实际构建FManagedArrayCollection需要更多步骤，此处仅为示意
    TestCollection.AddElements<FVector3f>(1, TEXT("Vertex"));
    TestCollection.AddElements<FIntVector>(1, TEXT("Face"));
    // ... 填充数据 ...

    // 将集合传递给组件
    DataflowComponent->SetRenderingCollection(MoveTemp(TestCollection));
    DataflowComponent->Invalidate(); // 首次计算和渲染
}

void AMyDataflowActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AMyDataflowActor::ReevaluateDataflow()
{
    if (DataflowComponent)
    {
        // 如果输入数据改变了，可能需要重新设置集合
        // DataflowComponent->SetRenderingCollection(新的集合);
        DataflowComponent->Invalidate();
    }
}
```

## 模块依赖

`DataflowEnginePlugin` 模块的依赖（从其推断）：

| 模块 | 用途 |
|---|---|
| `DataflowCore` | 数据流图系统的核心运行时库，包含节点、边、上下文等基础定义。 |
| `DataflowNodes` | 提供一组内置的数据流节点（如集合操作、网格操作节点）。 |
| `GeometryCollectionEngine` | 几何集合（GeometryCollection）的运行时支持，常用于破坏系统。 |
| `PhysicsCore` | 物理系统核心，可能用于与碰撞或动力学数据交互。 |
| `Chaos` | Chaos 物理和破坏框架。 |
| `RenderCore` | 渲染核心，场景代理（SceneProxy）需要它来提交渲染数据。 |
| `DynamicMesh` | 提供 `UDynamicMesh` 资产，用于操作动态网格。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee85ff45` | Dataflow : remove sections from rendering settings since they are half broken | 移除了渲染设置中部分损坏的区段功能 |
| 2026-05-25 | `25af8e6f` | Dataflow : add extra checks on the edit skin weight tool to inform user about why the node may not work | 为编辑蒙皮权重工具增加了额外检查，以告知用户节点可能不工作的原因 |
| 2026-05-22 | `9a062c29` | [Dataflow Editor] Fixed container mutation during tick evaluation. | 修复了在 Tick 评估期间容器发生变更的 Bug |
| 2026-05-22 | `8dc486bc` | Dataflow Editor : Fix crash happening when using a tool with another Dataflow editor opened | 修复了当使用一个工具且另一个数据流编辑器打开时发生的崩溃 |
| 2026-05-22 | `8cfadbd3` | Dataflow Editor : fix Undo / redo issues with comment nodes | 修复了注释节点撤销/重做的问题 |

### 维护评价

- **创建时间**：2026年4月，是一个非常新的插件。
- **最近更新频率**：非常活跃，在2026年5月有多次连续提交，专注于修复 Bug 和优化编辑器体验。
- **维护状态**：**积极维护中**。作为从 Experimental 转正的模块，当前处于快速迭代和问题修复阶段。
- **已知问题/限制**：从提交历史看，渲染设置、工具提示、容器线程安全、编辑器稳定性等方面仍存在 Bug 需要修复。
- **推荐使用**：**适合在开发中尝试和集成**，但需注意它仍处于早期成熟阶段（v0.1），API 和功能可能随更新而变化。建议在项目的非核心或可插拔部分使用，并保持关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow)
- 官方文档：暂无
- 测试用例：暂无公开路径