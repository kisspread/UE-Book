# Compute Framework

> Support for user authored GPU compute graphs

| 属性 | 值 |
|---|---|
| 中文名 | 计算框架 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ComputeFramework` (Runtime), `ComputeFrameworkEditor` (Editor), `ComputeDataInterface` (Runtime), `EditableComputeGraph` (Runtime), `EditableComputeGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework) | |

## 用途
ComputeFramework 是一个允许用户在运行时创建、编译和执行自定义 GPU 计算着色器图的框架。它解决的核心问题是：在不手动管理着色器代码和渲染资源的情况下，以**数据驱动**和**节点化**的方式构建复杂的 GPU 计算管线。

该框架的核心概念包括：
1.  **计算图 (`UComputeGraph`)**：表示一个由内核（Kernels）和数据接口（Data Interfaces）组成的计算流程图。
2.  **计算内核 (`UComputeKernel`)**：代表一个将要在 GPU 上运行的着色器程序，其源代码可以是原始的 HLSL 文本或其他编辑器（如材质图）生成的代码。
3.  **数据接口 (`UComputeDataInterface`)**：定义了内核如何与外部数据（如缓冲区、纹理、参数）进行读写交互。
4.  **数据提供者 (`UComputeDataProvider`)**：数据接口在运行时的具体实现，负责在游戏线程和渲染线程之间准备和传递数据。

通过这个框架，开发者可以专注于描述计算的逻辑（图的结构和内核代码），而框架负责处理着色器的编译、资源的创建/绑定、调度执行和跨线程数据同步等底层细节。

## 使用场景
- **自定义动画/物理变形器**：需要在 GPU 上进行大规模的顶点或骨骼计算，例如布料模拟、程序化动画。
- **GPU 粒子模拟**：实现复杂的粒子系统，其更新逻辑完全在 GPU 上运行。
- **后处理与图像处理**：构建链式的图像处理滤镜，每个滤镜都是一个计算着色器内核。
- **AI 与机器学习推理**：在 GPU 上运行推理模型作为游戏逻辑的一部分。
- **任何需要高性能通用计算 (GPGPU) 的场景**：当计算逻辑可以被表达为一个数据流图时。

## 蓝图用法
该框架主要通过 `UComputeGraphComponent` 组件暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeProvider` | 为图中的一个数据提供者进行自定义初始化。 | `UComputeGraphComponent` |
| `QueueExecute` | 将计算图的执行排入渲染队列，将在下一帧渲染时执行。 | `UComputeGraphComponent` |
| `CreateDataProviders` | 为图实例创建并绑定数据提供者对象。 | `FComputeGraphInstance` |
| `EnqueueWork` | 将计算图实例的工作排入计算系统执行。 | `FComputeGraphInstance` |

### 使用示例（蓝图描述）

1.  在你的 Actor 上添加一个 `ComputeGraphComponent`。
2.  在组件的属性中，指定一个预创建好的 `ComputeGraph` 资产。
3.  通常，你需要重写 `InitializeProvider` 蓝图事件。在此事件中，根据 `InDataInterfaceIndex` 判断是哪个数据接口需要初始化，并对传入的 `InOutDataProvider` 对象进行属性设置（例如，设置一个纹理引用或缓冲区大小）。
4.  在需要触发计算的时刻（如 `BeginPlay` 或某个按键事件），调用 `QueueExecute` 节点。
5.  框架会在后续的渲染帧中自动执行该图，将数据从游戏线程提交到渲染线程，并调度 GPU 计算着色器。

## C++ 用法

### 头文件引入

```cpp
#include "ComputeFramework/ComputeGraph.h"
#include "ComputeFramework/ComputeKernel.h"
#include "ComputeFramework/ComputeDataInterface.h"
#include "ComputeFramework/ComputeDataProvider.h"
#include "ComputeFramework/ComputeGraphInstance.h"
#include "ComputeFramework/ComputeGraphComponent.h"
```

### 基本用法

从源码分析中，典型的使用模式涉及定义一个图及其组件，然后在游戏逻辑中实例化和执行它。

```cpp
// 假设已有 UMyCustomDataInterface 和 UMyCustomKernelSource 类
// 1. 创建并配置计算图 (通常在编辑器中完成或通过代码构建)
UComputeGraph* MyGraph = NewObject<UComputeGraph>();
// ... 使用 FComputeGraphBuilder 或直接设置其 KernelInvocations, DataInterfaces, GraphEdges 属性 ...

// 2. 在游戏对象中 (如自定义 Actor 或 Component)
class AMyComputeActor : public AActor
{
    // ... 其他成员 ...
    UPROPERTY()
    UComputeGraph* GraphAsset;

    UPROPERTY()
    FComputeGraphInstance GraphInstance;

    UPROPERTY()
    TObjectPtr<UComputeGraphComponent> ComputeComp;

    void InitializeCompute()
    {
        if (GraphAsset)
        {
            // 为图的首个绑定索引（通常是0）创建数据提供者
            // 需要提供一个绑定对象（通常是你自己的 Actor 或 Component）
            GraphInstance.CreateDataProviders(GraphAsset, 0, this);
            // 可选：对提供者进行自定义初始化
            // GraphInstance.InitializeDataProviders(GraphAsset, 0, this);
        }
    }

    void ExecuteCompute()
    {
        if (GraphAsset)
        {
            // 将工作排入计算系统
            GraphInstance.EnqueueWork(GraphAsset, GetWorld()->Scene, TEXT("MyExecutionGroup"), GetFName(), FSimpleDelegate());
        }
    }
};
```

### 进阶用法

**使用 `FComputeGraphBuilder` 程序化构建计算图**

```cpp
#include "ComputeFramework/ComputeGraphBuilder.h"

void BuildGraphProgrammatically(UComputeGraph* OutGraph, UObject* Outer)
{
    FComputeGraphBuilder Builder;

    // 1. 添加内核源
    UComputeKernelSourceWithText* KernelSource = NewObject<UComputeKernelSourceWithText>(Outer);
    KernelSource->SourceText = TEXT("RWBuffer<float> OutputBuffer; [numthreads(64,1,1)] void MainCS() { ... }");
    FKernelHandle Kernel = Builder.AddKernel(KernelSource, TEXT("MyKernel"));

    // 2. 添加数据接口 (需要自定义的 UComputeDataInterface 子类)
    UMyBufferInterface* BufferInterface = NewObject<UMyBufferInterface>(Outer);
    UClass* BufferProviderClass = UMyBufferProvider::StaticClass(); // 对应的数据提供者类
    FInterfaceHandle Interface = Builder.AddDataInterface(BufferInterface, BufferProviderClass, TEXT("OutputBuffer"));

    // 3. 连接内核的输出到数据接口
    Builder.ConnectOutput(Kernel, TEXT("OutputBuffer"), Interface, TEXT("WriteBuffer"));

    // 4. 构建图
    Builder.Build(*OutGraph, *Outer);
}
```

**自定义数据接口和数据提供者**

要扩展框架，通常需要创建 `UComputeDataInterface` 和 `UComputeDataProvider` 的子类。

```cpp
// MyBufferInterface.h
UCLASS()
class UMyBufferInterface : public UComputeDataInterface
{
    GENERATED_BODY()
public:
    virtual TCHAR const* GetClassName() const override { return TEXT("MyBuffer"); }
    virtual void GetSupportedOutputs(TArray<FShaderFunctionDefinition>& OutFunctions) const override;
    virtual void GetHLSL(FString& OutHLSL, FString const& InDataInterfaceName) const override;
    virtual UClass* GetBindingType() const override;
    virtual UComputeDataProvider* CreateDataProvider() const override;
    // ... 其他必要的接口实现 ...
};

// MyBufferProvider.h
UCLASS()
class UMyBufferProvider : public UComputeDataProvider
{
    GENERATED_BODY()
public:
    virtual void Initialize(UComputeDataInterface const* InDataInterface, UObject* InBinding, uint64 InInputMask, uint64 InOutputMask) override;
    virtual FComputeDataProviderRenderProxy* GetRenderProxy() override;
    // ... 其他必要的接口实现 ...
private:
    // 存储实际的资源引用，如 FBufferRHIRef
};

// MyBufferProviderProxy.h (渲染线程代理)
class FMyBufferProviderProxy : public FComputeDataProviderRenderProxy
{
public:
    // 实现 GetDispatchThreadCount, GatherPermutations, AllocateResources, GatherDispatchData 等
    // 在 GatherDispatchData 中，将 RDG 缓冲区句柄或参数写入 FDispatchData 结构。
};
```

## Demo 示例

以下是一个最小的自包含示例，展示了如何创建一个简单的计算图并将其绑定到组件上执行。

**MyComputeDemoComponent.h**
```cpp
#pragma once
#include "ComputeFramework/ComputeGraphComponent.h"
#include "MyComputeDemoComponent.generated.h"

UCLASS(ClassGroup=(Compute), meta=(BlueprintSpawnableComponent))
class UMyComputeDemoComponent : public UComputeGraphComponent
{
    GENERATED_BODY()
public:
    UMyComputeDemoComponent();

protected:
    // 重写初始化，为特定数据接口设置默认值（如缓冲区大小）
    virtual void InitializeProvider_Implementation(int32 InDataInterfaceIndex, UObject* InOutDataProvider) override;
};
```

**MyComputeDemoComponent.cpp**
```cpp
#include "MyComputeDemoComponent.h"
#include "MyCustomDataInterface.h" // 假设的自定义数据接口
#include "MyCustomDataProvider.h"   // 假设的自定义数据提供者

UMyComputeDemoComponent::UMyComputeDemoComponent()
{
    // 在构造函数中指定要使用的计算图资产（通常在编辑器中设置）
    // ComputeGraph = LoadObject<UComputeGraph>(...);
}

void UMyComputeDemoComponent::InitializeProvider_Implementation(int32 InDataInterfaceIndex, UObject* InOutDataProvider)
{
    Super::InitializeProvider_Implementation(InDataInterfaceIndex, InOutDataProvider);

    // 根据索引判断是哪个数据接口，进行定制化初始化
    if (UMyBufferDataProvider* BufferProvider = Cast<UMyBufferDataProvider>(InOutDataProvider))
    {
        BufferProvider->SetBufferSize(1024); // 例如，设置一个默认的缓冲区大小
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 提供渲染线程基础设施（RDG, FRHICommandList 等）。 |
| `RHI` | 渲染硬件接口，用于创建 GPU 资源。 |
| `ShaderCore` | 着色器编译、反射和元数据管理。 |
| `ComputeDataInterface` | 提供内置的数据接口实现（如缓冲区、纹理）。 |
| `OptimusCore` | **可能依赖**：Optimus 框架（用于动画节点图）是 ComputeFramework 的主要用户之一，提供了 `UComputeKernelSource` 的图形化实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `057cf5d7` | ComputeFramework: Fix data races on FComputeKernelShaderMap registries. | 修复了计算核着色器映射注册表上的数据竞争问题。 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases (S... | 为数据接口添加了按内核的输出掩码功能，以优化特定情况下的资源绑定。 |
| 2026-04-21 | `f1e2ebe5` | [PCG][GPUPROFILER] Add support for user-provided stat objects to retrieve timing data from GPU execu... | 为 GPU 执行添加了对用户提供的统计对象支持，以收集性能计时数据。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored ... | 重构了着色器编译作业结构，移除了显式的标志位。 |

### 维护评价
ComputeFramework 是一个**活跃维护中**的**实验性**（Beta）插件。
- **创建时间**：约3年前（2022年）。
- **维护频率**：近期（2026年4-5月）有多次功能增强和bug修复提交，表明它仍在积极开发中。
- **状态**：`EnabledByDefault=false` 和 `IsBetaVersion=true` 明确标示其为实验性功能。
- **已知限制**：作为 Beta 版本，API 可能发生变化，功能和稳定性可能未达到正式发布标准。
- **推荐**：**适合早期采用者和需要前沿 GPU 计算能力的项目**。如果你需要在 UE5 中构建高性能、数据驱动的计算管线，并愿意承担 API 变化的风险，这个框架是一个强大的工具。不建议在要求高度稳定的生产环境中直接使用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework/Tests) (如果存在)