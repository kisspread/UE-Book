# Compute Framework

> Support for user authored GPU compute graphs

| 属性 | 值 |
|---|---|
| 中文名 | 计算框架 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ComputeFramework` (Runtime), `ComputeFrameworkEditor` (Runtime), `ComputeDataInterface` (Runtime), `EditableComputeGraph` (Runtime), `EditableComputeGraphEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework) | |

## 用途

Compute Framework 是一个用于创建、管理和执行用户自定义 GPU 计算着色器的运行时框架。它解决了在 UE5 中高效运行复杂 GPU 计算逻辑（如物理模拟、数据生成、图像处理等）的问题，提供了一个图编辑器（Graph Editor）来可视化地构建计算流程，并自动处理着色器编译、资源绑定和执行调度。

该插件的主要目标是让开发者无需手动管理 Compute Shader 的底层细节，而是通过节点图定义计算流程，从而降低 GPU 计算编程的门槛。

## 使用场景

- 你需要在 GPU 上运行自定义的粒子模拟、流体模拟或布料物理。
- 你需要实现复杂的图像后处理算法，且需要逐像素或逐片元的计算逻辑。
- 你需要进行大规模的数据转换或生成，例如纹理生成、地形高度图计算。
- 你希望使用可视化的节点图来构建和调试 GPU 计算流程。

## 蓝图用法

由于 `ComputeFramework` 核心模块主要是 C++ 运行时，且当前分析的 `ComputeFrameworkEditor` 模块是编辑器模块，主要提供编译和同步功能，因此蓝图公开的 API 相对有限。核心的图资产和计算实体在 C++ 中管理。

### 核心节点

该插件主要提供编辑器内的可视化图编辑功能，运行时通过 C++ 接口调用。蓝图层面更多是处理计算结果，而非直接构建图。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TriggerRecompile` | 触发计算图的重新编译（编辑器内） | `UComputeGraph` |

### 使用示例（蓝图描述）

1.  在内容浏览器中创建一个 `ComputeGraph` 资产。
2.  双击打开它，在图形编辑器中从调色板拖拽计算内核（Kernel）、数据接口（Data Interface）等节点，连线构建计算流程。
3.  在游戏逻辑或编辑器工具中，通过 C++ 获取该图资产的实例，将其附加到场景中的 `UComputeComponent` 组件上。
4.  在运行时，`UComputeComponent` 会负责调度该图的执行，将计算结果（例如写入纹理或缓冲区）提供给材质或其他系统使用。

## C++ 用法

### 头文件引入

```cpp
#include "ComputeFramework/ComputeGraph.h"
#include "ComputeFramework/ComputeComponent.h"
```

### 基本用法

创建并执行一个计算图。

```cpp
// 假设你已经有一个 UComputeGraph* 类型的资产（MyComputeGraph）
// 通常在 Actor 或 Component 中持有对它的引用

// 创建一个计算组件并附加到 Actor 上
UComputeComponent* ComputeComp = NewObject<UComputeComponent>(this);
ComputeComp->RegisterComponent();
ComputeComp->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

// 设置要执行的计算图
ComputeComp->SetComputeGraph(MyComputeGraph);

// 触发一次计算（通常在 Tick 或特定事件中调用）
ComputeComp->ExecuteGraph();
```

*来源：引擎中 `UComputeComponent` 的典型用法模式。*

### 进阶用法

与数据接口交互，为计算图提供输入数据并读取输出结果。

```cpp
// 假设图中有一个名为 "InputBuffer" 的数据接口节点
// 我们需要为它提供一个 SSBO (Shader Storage Buffer Object) 作为输入

FShaderResourceViewRHIRef InputSRV = ... // 从渲染资源创建的 SRV

// 获取图实例，找到对应的数据接口并设置资源
UComputeGraphInstance* GraphInstance = ComputeComp->GetGraphInstance();
if (GraphInstance)
{
    // 通过数据接口的名称或注册标识符找到它
    UComputeDataInterface* DataInterface = GraphInstance->FindDataInterface(TEXT("InputBuffer"));
    if (DataInterface)
    {
        // 设置输入资源（具体方法取决于数据接口的实现）
        DataInterface->SetResource(InputSRV);
    }
}

// 同样，可以读取输出数据接口的结果
UComputeDataInterface* OutputInterface = GraphInstance->FindDataInterface(TEXT("OutputTexture"));
if (OutputInterface)
{
    FShaderResourceViewRHIRef OutputSRV = OutputInterface->GetResource();
    // 使用输出 SRV ...
}
```

*来源：自定义 `UComputeDataInterface` 子类与图交互的典型模式。*

## Demo 示例

一个最小的 Actor 示例，展示如何加载并执行一个计算图。

### MyComputeActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyComputeActor.generated.h"

class UComputeGraph;
class UComputeComponent;

UCLASS()
class AMyComputeActor : public AActor
{
    GENERATED_BODY()

public:
    AMyComputeActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(VisibleAnywhere)
    UComputeComponent* ComputeComponent;

    UPROPERTY(EditAnywhere, Category = "Compute")
    UComputeGraph* MyComputeGraph;

    bool bFirstFrame = true;
};
```

### MyComputeActor.cpp

```cpp
#include "MyComputeActor.h"
#include "ComputeFramework/ComputeComponent.h"
#include "ComputeFramework/ComputeGraph.h"

AMyComputeActor::AMyComputeActor()
{
    PrimaryActorTick.bCanEverTick = true;

    ComputeComponent = CreateDefaultSubobject<UComputeComponent>(TEXT("ComputeComponent"));
    RootComponent = ComputeComponent;
}

void AMyComputeActor::BeginPlay()
{
    Super::BeginPlay();

    if (MyComputeGraph)
    {
        ComputeComponent->SetComputeGraph(MyComputeGraph);
    }
}

void AMyComputeActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 通常在初始化后或需要更新时执行一次计算
    if (bFirstFrame && MyComputeGraph)
    {
        ComputeComponent->ExecuteGraph();
        bFirstFrame = false;
        UE_LOG(LogTemp, Log, TEXT("Compute Graph Executed."));
    }
}
```

## 模块依赖

从各模块的 Build.cs 推断，该插件依赖于 UE 的渲染和着色器编译核心模块。

| 模块 | 用途 |
|---|---|
| `RenderCore` | 渲染核心功能，如 RHI 资源和着色器管理 |
| `ShaderCore` | 着色器编译和反射基础设施 |
| `RHI` | 渲染硬件接口，提供跨平台的 GPU 资源创建和管理 |
| `Projects` | 模块项目信息（常见依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `057cf5d7` | ComputeFramework: Fix data races on FComputeKernelShaderMap registries. | 修复着色器映射注册表中的数据竞争问题 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases (S | 为数据接口添加了每个内核的输出掩码功能，用于与 Optimus 系统集成 |
| 2026-04-21 | `f1e2ebe5` | [PCG][GPUPROFILER] Add support for user-provided stat objects to retrieve timing data from GPU execu | 为 GPU 分析器添加了用户自定义统计对象的支持，便于性能分析 |

### 维护评价

- **状态**：**活跃维护中**。该插件于 2022 年创建，虽然标记为实验性（IsBetaVersion=true），但近期（2026年）仍有实质性功能更新和 bug 修复，特别是与优化（Optimus）、PCG 和 GPU 分析器的集成。
- **推荐度**：**推荐用于实验性项目或需要自定义 GPU 计算的场景**。鉴于其活跃的维护状态和明确的用途，它是 UE5 中构建复杂 GPU 计算管线的有力工具。但由于其 **实验性** 标签和 **默认未启用** 的状态，不建议在需要高度稳定性的生产环境中作为核心依赖。
- **注意**：使用前需在项目设置中手动启用该插件，并关注其版本更新可能带来的 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework/Tests)