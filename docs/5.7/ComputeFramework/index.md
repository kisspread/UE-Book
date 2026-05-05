# Compute Framework

> Support for user authored GPU compute graphs

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ComputeFramework` (Runtime), `ComputeFrameworkEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-22 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ComputeFramework) | |

## 用途

Compute Framework 是 UE5 的 **GPU 计算图编排系统**，提供了一种声明式方式将多个 Compute Shader Kernel 和数据接口（Data Interface）组织成有向图，由引擎自动处理 shader 编译、参数绑定、资源管理和调度执行。

与直接使用 `DispatchComputeShader` 或 RDG 不同，Compute Framework 解决的核心问题是：**将 GPU 计算任务的"数据流"与"执行逻辑"解耦**。Kernel 只声明它需要读/写哪些外部函数（如 `ReadValue`、`WriteValue`），Data Interface 负责提供这些函数的具体实现（如 buffer 读写、线程数查询等）。这样同一份 Kernel 代码可以搭配不同的 Data Interface 运行在不同的数据源上，无需修改 shader。

该框架被 UE5 内部系统（如 PCG、Animation Deformer）使用，为"用户编写的 GPU 计算管线"提供完整的生命周期管理：编译、permutation 管理、异步 shader 编译、render thread 调度、GPU readback 等。

**版本说明**：当前 VersionName 为 `0.9`，`IsBetaVersion=true`，`EnabledByDefault=false`。需要在项目设置中手动启用。

## 使用场景

- 你需要在 GPU 上运行自定义计算逻辑，且需要管理多个 kernel 之间的数据流 → 用 Compute Framework 组织计算图
- 你需要让同一份 compute shader 代码适配不同的数据源（不同 buffer 格式、不同 mesh 数据等） → 通过 Data Interface 抽象数据访问
- 你在开发动画变形器、粒子系统或其他需要 GPU 计算管线的功能 → 使用 `UComputeGraphComponent` + `UComputeGraph` 搭建
- 你需要异步编译大量 compute shader permutation，且希望引擎自动管理编译和缓存 → Compute Framework 内置了完整的 shader 编译管理
- 你需要 GPU→CPU readback 功能 → `FComputeDataProviderRenderProxy::GetReadbackData()` 提供异步 readback 支持

## 架构概览

Compute Framework 的核心架构由以下层次组成：

```
┌─────────────────────────────────────────────────────────────┐
│  UComputeGraph (资产)                                        │
│  ├── UComputeKernel[]          ← Kernel 调用列表              │
│  │   └── UComputeKernelSource  ← HLSL 源码或程序化生成        │
│  ├── UComputeDataInterface[]   ← 数据接口声明                 │
│  ├── FComputeGraphEdge[]       ← Kernel ↔ DataInterface 连接 │
│  └── Bindings[]                ← 绑定对象类型                 │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  UComputeGraphComponent (ActorComponent)                     │
│  └── FComputeGraphInstance                                   │
│      ├── DataProviders[]       ← 运行时数据提供者             │
│      └── EnqueueWork()         ← 提交到渲染线程               │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  FComputeGraphTaskWorker (渲染线程)                           │
│  ├── 接收 GraphRenderProxy + DataProviderRenderProxies        │
│  ├── 按 Kernel 顺序排序并提交 dispatch                        │
│  └── 管理 GPU readback 回调                                   │
└─────────────────────────────────────────────────────────────┘
```

### 核心概念

| 概念 | 类 | 说明 |
|---|---|---|
| **Compute Graph** | `UComputeGraph` | 计算图资产，包含 kernel 列表、data interface 列表和连接边 |
| **Kernel** | `UComputeKernel` | 一个 GPU compute shader 调用单元 |
| **Kernel Source** | `UComputeKernelSource` | Kernel 的 HLSL 源码（可以是文本或程序化生成） |
| **Data Interface** | `UComputeDataInterface` | 声明 kernel 需要的外部数据访问函数（编译期） |
| **Data Provider** | `UComputeDataProvider` | Data Interface 的运行时实例，实际提供 GPU 资源 |
| **Data Provider Proxy** | `FComputeDataProviderRenderProxy` | Data Provider 的渲染线程代理 |
| **Graph Component** | `UComputeGraphComponent` | ActorComponent，将 graph 绑定到 Actor 并驱动执行 |
| **Graph Instance** | `FComputeGraphInstance` | 管理 data provider 的创建和工作入队 |
| **Render Proxy** | `FComputeGraphRenderProxy` | Graph 的渲染线程只读副本 |
| **Task Worker** | `FComputeGraphTaskWorker` | 渲染线程的调度器，负责 dispatch 排序和执行 |

### 执行流程

1. **创建阶段**：创建 `UComputeGraph` 资产，添加 kernel 和 data interface，定义边连接
2. **编译阶段**：调用 `UpdateResources()` 触发异步 shader 编译（或在首次使用时延迟编译）
3. **绑定阶段**：通过 `CreateDataProviders()` 创建 data provider 实例，绑定到数据源
4. **入队阶段**：调用 `EnqueueWork()` 将 graph + data provider proxies 提交到渲染线程
5. **执行阶段**：渲染线程的 `FComputeGraphTaskWorker::SubmitWork()` 按 kernel 顺序收集 shader、permutation、dispatch data，通过 RDG 提交 GPU dispatch
6. **Readback 阶段**（可选）：异步 readback 结果回调到游戏线程

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateDataProviders` | 为指定绑定索引创建所有 Data Provider 对象 | `UComputeGraphComponent` |
| `DestroyDataProviders` | 销毁所有关联的 Data Provider 对象 | `UComputeGraphComponent` |
| `QueueExecute` | 将计算图加入下一帧渲染更新的执行队列 | `UComputeGraphComponent` |

### 属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `ComputeGraph` | `UComputeGraph*` | 要执行的计算图资产引用 | `UComputeGraphComponent` |

### 使用示例（蓝图描述）

1. **基础用法**：在 Actor 上添加 `ComputeGraphComponent`，在 Details 面板设置 `ComputeGraph` 属性指向一个计算图资产。组件注册时自动创建 binding index 0 的 Data Provider。在需要执行时（如 Tick 事件）调用 `QueueExecute` 节点。

2. **自定义数据绑定**：先调用 `CreateDataProviders(BindingIndex, BindingObject)` 绑定特定数据源，然后在 Tick 中调用 `QueueExecute`。组件销毁时自动调用 `DestroyDataProviders`。

## C++ 用法

### 头文件引入

```cpp
#include "ComputeFramework/ComputeFramework.h"
#include "ComputeFramework/ComputeGraph.h"
#include "ComputeFramework/ComputeGraphComponent.h"
#include "ComputeFramework/ComputeGraphInstance.h"
#include "ComputeFramework/ComputeKernel.h"
#include "ComputeFramework/ComputeKernelSource.h"
#include "ComputeFramework/ComputeDataInterface.h"
#include "ComputeFramework/ComputeDataProvider.h"
```

### 基本用法 — 使用 ComputeGraphComponent

`UComputeGraphComponent` 是最简单的使用方式，适用于 Actor 场景：

```cpp
// 在 Actor 中添加组件
UPROPERTY(VisibleAnywhere)
TObjectPtr<UComputeGraphComponent> ComputeGraphComp;

// 创建并设置
ComputeGraphComp = CreateDefaultSubobject<UComputeGraphComponent>(TEXT("ComputeGraph"));
ComputeGraphComp->ComputeGraph = MyComputeGraphAsset; // 在蓝图或构造函数中设置

// 运行时：创建自定义数据绑定（binding index 1，绑定到某个 UObject）
ComputeGraphComp->CreateDataProviders(1, MyBindingObject);

// 每帧触发执行
ComputeGraphComp->QueueExecute();
```

> 来源：`Source/ComputeFramework/Private/ComputeGraphComponent.cpp`

### 基本用法 — 直接使用 FComputeGraphInstance

当不需要 ActorComponent 时，可以直接操作 `FComputeGraphInstance`：

```cpp
#include "ComputeFramework/ComputeGraphInstance.h"
#include "ComputeFramework/ComputeGraph.h"

FComputeGraphInstance GraphInstance;

// 创建 Data Providers（binding index 0，绑定对象为 this）
GraphInstance.CreateDataProviders(MyComputeGraph, 0, this);

// 入队执行
GraphInstance.EnqueueWork(
    MyComputeGraph,        // 计算图资产
    GetScene(),            // 场景接口
    ComputeTaskExecutionGroup::EndOfFrameUpdate, // 执行组名
    GetFName(),            // Owner 名称
    FSimpleDelegate(),     // Fallback 委托（无效时调用）
    this                   // Owner 指针
);
```

> 来源：`Source/ComputeFramework/Private/ComputeGraphInstance.cpp`

### 进阶用法 — 自定义 Data Interface 和 Data Provider

创建自定义 Data Interface 需要实现三个类：

```cpp
// 1. Data Interface（编译期，声明 shader 函数签名）
UCLASS()
class UMyDataInterface : public UComputeDataInterface
{
    GENERATED_BODY()
public:
    TCHAR const* GetClassName() const override { return TEXT("MyData"); }
    
    void GetSupportedInputs(TArray<FShaderFunctionDefinition>& OutFunctions) const override
    {
        FShaderFunctionDefinition Func;
        Func.Name = TEXT("ReadMyData");
        Func.ParamTypes.Add(FShaderParamTypeDefinition{/* ... */});
        OutFunctions.Add(Func);
    }
    
    void GetHLSL(FString& OutHLSL, FString const& InDataInterfaceName) const override
    {
        // 提供 HLSL 实现代码
        OutHLSL = TEXT("float ReadMyData_") + FString(InDataInterfaceName) 
                + TEXT("(uint Index) { /* ... */ }");
    }
    
    void GetShaderParameters(TCHAR const* UID, 
        FShaderParametersMetadataBuilder& InOutBuilder,
        FShaderParametersMetadataAllocations& InOutAllocations) const override
    {
        // 声明 shader 参数
    }
    
    UComputeDataProvider* CreateDataProvider() const override;
};

// 2. Data Provider（游戏线程，创建渲染线程代理）
UCLASS()
class UMyDataProvider : public UComputeDataProvider
{
    GENERATED_BODY()
public:
    FComputeDataProviderRenderProxy* GetRenderProxy() override
    {
        return new FMyDataProviderProxy(/* ... */);
    }
};

// 3. Data Provider Proxy（渲染线程，提供 GPU 资源和 dispatch 数据）
class FMyDataProviderProxy : public FComputeDataProviderRenderProxy
{
public:
    void AllocateResources(FRDGBuilder& GraphBuilder, 
                          FAllocationData const& InAllocationData) override
    {
        // 分配 RDG buffer 资源
    }
    
    void GatherDispatchData(FDispatchData const& InDispatchData) override
    {
        // 填充 shader 参数数据
    }
};
```

### 进阶用法 — 查询框架状态

```cpp
// 检查平台是否支持 Compute Framework
bool bSupported = ComputeFramework::IsSupported(GMaxRHIShaderPlatform);

// 检查框架是否已启用
bool bEnabled = ComputeFramework::IsEnabled();

// 检查是否使用延迟编译
bool bDeferred = ComputeFramework::IsDeferredCompilation();

// 强制重建所有计算图（编辑器）
ComputeFramework::RebuildComputeGraphs();

// 刷新指定 execution group 的所有待执行工作
ComputeFramework::FlushWork(GetScene(), ComputeTaskExecutionGroup::EndOfFrameUpdate);

// 中止指定 owner 的所有待执行工作
ComputeFramework::AbortWork(GetScene(), this);
```

> 来源：`Source/ComputeFramework/Private/ComputeFramework.cpp`

## Demo 示例

以下示例展示如何以编程方式构建一个简单的 buffer copy 计算图：

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ComputeFramework",
    "RenderCore",
    "RHI"
});
```

### MyComputeExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ComputeFramework/ComputeGraphInstance.h"
#include "MyComputeExample.generated.h"

class UComputeGraph;

UCLASS(ClassGroup=(Compute), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyComputeExample : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyComputeExample();

    virtual void OnRegister() override;
    virtual void OnUnregister() override;

    /** 要执行的计算图资产 */
    UPROPERTY(EditAnywhere, Category = "Compute")
    TObjectPtr<UComputeGraph> ComputeGraph;

    /** 触发执行 */
    UFUNCTION(BlueprintCallable, Category = "Compute")
    void ExecuteGraph();

protected:
    virtual void SendRenderDynamicData_Concurrent() override;
    virtual void DestroyRenderState_Concurrent() override;
    virtual bool ShouldCreateRenderState() const override { return true; }

private:
    FComputeGraphInstance GraphInstance;
};
```

### MyComputeExample.cpp

```cpp
#include "MyComputeExample.h"

#include "ComputeFramework/ComputeFramework.h"
#include "ComputeFramework/ComputeGraph.h"
#include "ComputeWorkerInterface.h"

UMyComputeExample::UMyComputeExample()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyComputeExample::OnRegister()
{
    Super::OnRegister();
    // 注册时自动创建 binding index 0 的 Data Provider
    if (ComputeGraph)
    {
        GraphInstance.CreateDataProviders(ComputeGraph, 0, this);
    }
}

void UMyComputeExample::OnUnregister()
{
    GraphInstance.DestroyDataProviders();
    Super::OnUnregister();
}

void UMyComputeExample::ExecuteGraph()
{
    if (ComputeGraph)
    {
        MarkRenderDynamicDataDirty();
    }
}

void UMyComputeExample::SendRenderDynamicData_Concurrent()
{
    Super::SendRenderDynamicData_Concurrent();
    
    GraphInstance.EnqueueWork(
        ComputeGraph,
        GetScene(),
        ComputeTaskExecutionGroup::EndOfFrameUpdate,
        GetOwner()->GetFName(),
        FSimpleDelegate(),
        this
    );
}

void UMyComputeExample::DestroyRenderState_Concurrent()
{
    Super::DestroyRenderState_Concurrent();
    ComputeFramework::AbortWork(GetScene(), this);
}
```

## 内置 Data Interface

Compute Framework 提供了两个内置的 Data Interface 实现：

### UComputeDataInterfaceBuffer

通用 GPU buffer 数据接口，支持读写操作。

| 属性 | 类型 | 说明 |
|---|---|---|
| `ValueType` | `FShaderValueTypeHandle` | Buffer 元素的类型（float, int, float3 等） |
| `ElementCount` | `int32` | Buffer 元素数量 |
| `bAllowReadWrite` | `bool` | 是否允许读写（否则只读） |
| `bClearBeforeUse` | `bool` | 使用前是否清零 |

Shader 端提供的函数：
- `ReadNumValues()` — 返回元素数量
- `ReadValue(uint Index)` — 读取元素
- `ReadValueUAV(uint Index)` — 从 UAV 读取（用于读写场景）
- `WriteValue(uint Index, VALUE_TYPE Value)` — 写入元素
- `WriteAtomicAdd/Min/Max(uint Index, VALUE_TYPE Value)` — 原子操作

> 来源：`Shaders/Private/ComputeDataInterfaceBuffer.ush`

### UComputeDataInterfaceDispatch

控制 dispatch 线程数的执行接口。每个 kernel 必须恰好绑定一个 `IsExecutionInterface()` 返回 true 的 Data Interface。

| 属性 | 类型 | 说明 |
|---|---|---|
| `ThreadCount` | `FUintVector` | 每个维度的线程数 |

Shader 端提供的函数：
- `ReadNumThreads()` — 返回 `uint3` 线程数

> 来源：`Shaders/Private/ComputeDataInterfaceDispatch.ush`

## Shader 编写约定

Compute Framework 使用特定的 HLSL 宏来编写 kernel 和 data interface 代码：

### Kernel 入口点

```hlsl
#include "/Plugin/ComputeFramework/Private/ComputeKernelCommon.ush"

// 使用 KERNEL_ENTRY_POINT 宏定义入口
// 自动提供：SV_GroupIndex, SV_GroupID, SV_GroupThreadID, SV_DispatchThreadID
KERNEL_ENTRY_POINT(MyKernelEntry)
{
    uint ThreadIndex = DTid.x;
    if (ThreadIndex >= ReadNumValues())
    {
        return;
    }
    WriteValue(ThreadIndex, ReadValue(ThreadIndex) * 2.0);
}
```

### Data Interface 代码

```hlsl
// 使用 DI_IMPL_READ / DI_IMPL_WRITE 定义接口函数
// DI_UID 宏确保同一 Data Interface 的多个实例不冲突

DI_IMPL_READ(ReadValue, VALUE_TYPE, uint Index)
{
    return MyBuffer[Index];
}

DI_IMPL_WRITE(WriteValue, uint Index, VALUE_TYPE Value)
{
    MyBuffer[Index] = Value;
}

// 使用 DI_UNIFORM_LOCAL 引用 uniform 变量
uint DI_UNIFORM_LOCAL(BufferElementCount);
```

### KERNEL_ENTRY_POINT 宏展开

```hlsl
// KERNEL_ENTRY_POINT(MyFunc) 展开为：
void MyFunc(
    uint Gidx : SV_GroupIndex,    // Group 内线程索引
    uint3 Gid : SV_GroupID,       // Group ID
    uint3 GTid: SV_GroupThreadID, // Group 内线程 ID（3D）
    uint3 DTid : SV_DispatchThreadID) // 全局 Dispatch 线程 ID（3D）
```

> 来源：`Shaders/Private/ComputeKernelCommon.ush`

## Permutation 系统

Compute Framework 支持 shader permutation，允许在编译期根据配置生成不同变体：

```cpp
// 在 KernelSource 中声明 permutation
FComputeKernelPermutationBool Perm;
Perm.Name = TEXT("ENABLE_FEATURE_A");
Perm.Value = false; // 默认值
KernelSource->PermutationSet.BooleanOptions.Add(Perm);

// Data Interface 也可以添加 permutation
void GetPermutations(FComputeKernelPermutationVector& OutVector) const override
{
    OutVector.AddPermutation(TEXT("BUFFER_FORMAT"), 3); // 0=Float, 1=Int, 2=Uint
}
```

运行时通过 `FComputeDataProviderRenderProxy::GatherPermutations()` 设置每个 invocation 的 permutation ID。

## 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `r.ComputeFramework.Enable` | 1 | 启用/禁用 Compute Framework |
| `r.ComputeFramework.DeferredCompilation` | 1 | 延迟编译（首次使用时编译而非 PostLoad） |
| `r.ComputeFramework.SortSubmit` | 1 | 按最优顺序排序 GPU dispatch 提交 |
| `r.ComputeFramework.TriggerGPUCaptureDispatches` | 0 | 触发 N 次后续 dispatch 的 GPU capture |
| `r.ComputeFramework.RebuildComputeGraphs` | — | 控制台命令，强制重建所有已加载的计算图 |

> 来源：`Source/ComputeFramework/Private/ComputeFramework.cpp`, `Source/ComputeFramework/Private/ComputeGraphWorker.cpp`

## 模块依赖

### ComputeFramework (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 系统 |
| `Engine` | Actor/Component 系统 |
| `Projects` | 插件管理 |
| `RenderCore` | 渲染核心（shader、RDG） |
| `Renderer` | 渲染器（compute system interface） |
| `RHI` | RHI 抽象层 |

私有包含路径模块：`DerivedDataCache`

### ComputeFrameworkEditor (Editor)

| 模块 | 用途 |
|---|---|
| `AssetTools` | 编辑器资产操作注册 |
| `ComputeFramework` | 核心运行时模块 |
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器框架 |

## 模块清单

| 模块 | 类型 | LoadingPhase | 说明 |
|---|---|---|---|
| `ComputeFramework` | Runtime | PostConfigInit | 核心计算图编译、调度、执行系统 |
| `ComputeFrameworkEditor` | Editor | Default | 编辑器资产类型注册、shader 编译 tick |

## 文件结构

```
ComputeFramework/
├── ComputeFramework.uplugin
├── Source/
│   ├── ComputeFramework/                    # Runtime 模块
│   │   ├── ComputeFramework.Build.cs
│   │   ├── Public/ComputeFramework/
│   │   │   ├── ComputeFramework.h           # 命名空间工具函数
│   │   │   ├── ComputeGraph.h               # 计算图资产类
│   │   │   ├── ComputeGraphComponent.h      # ActorComponent
│   │   │   ├── ComputeGraphFromText.h       # 文本驱动的计算图
│   │   │   ├── ComputeGraphInstance.h       # Graph 实例管理
│   │   │   ├── ComputeKernel.h              # Kernel 定义
│   │   │   ├── ComputeKernelSource.h        # Kernel 源码基类
│   │   │   ├── ComputeDataInterface.h       # Data Interface 基类
│   │   │   ├── ComputeDataProvider.h        # Data Provider 基类
│   │   │   ├── ComputeSource.h              # 通用源码基类
│   │   │   ├── ComputeKernelPermutationSet.h
│   │   │   ├── ComputeKernelPermutationVector.h
│   │   │   ├── ComputeKernelCompileResult.h
│   │   │   ├── ComputeMetadataBuilder.h
│   │   │   ├── ShaderParamTypeDefinition.h  # Shader 类型系统
│   │   │   ├── ShaderParameterMetadataAllocation.h
│   │   │   └── IComputeFrameworkModule.h
│   │   └── Private/
│   │       ├── ComputeFramework.cpp         # 命名空间实现 + CVar
│   │       ├── ComputeFrameworkModule.cpp   # 模块启动/关闭
│   │       ├── ComputeGraph.cpp             # Graph 编译管线（~1200 行）
│   │       ├── ComputeGraphComponent.cpp
│   │       ├── ComputeGraphFromText.cpp     # 文本 Graph 示例实现
│   │       ├── ComputeGraphInstance.cpp
│   │       ├── ComputeGraphWorker.cpp       # 渲染线程调度（~400 行）
│   │       ├── ComputeKernel.cpp
│   │       ├── ComputeKernelShader.cpp
│   │       ├── ComputeKernelShaderMap.cpp   # Shader Map 管理
│   │       ├── ComputeKernelShaderCompilationManager.cpp
│   │       ├── ComputeKernelShared.cpp
│   │       ├── ComputeSystem.cpp
│   │       ├── ComputeDataInterfaceBuffer.cpp
│   │       ├── ComputeDataInterfaceDispatch.cpp
│   │       ├── ComputeDataProvider.cpp
│   │       ├── ComputeMetadataBuilder.cpp
│   │       ├── ShaderParamTypeDefinition.cpp
│   │       ├── ShaderParameterMetadataAllocation.cpp
│   │       └── ComputeFramework/
│   │           ├── ComputeViewExtension.cpp/h      # 场景视图扩展
│   │           ├── ComputeSystem.h                  # 系统实现
│   │           ├── ComputeGraphWorker.h
│   │           ├── ComputeGraphRenderProxy.h
│   │           ├── ComputeKernelShader.h
│   │           ├── ComputeKernelShaderType.h
│   │           ├── ComputeKernelShaderCompilationManager.h
│   │           ├── ComputeKernelDerivedDataVersion.h
│   │           ├── ComputeKernelShared.h            # FComputeKernelResource
│   │           ├── ComputeFrameworkModule.h
│   │           ├── ComputeDataInterfaceBuffer.h
│   │           ├── ComputeDataInterfaceDispatch.h
│   │           └── ComputeViewExtension.h
│   └── ComputeFrameworkEditor/              # Editor 模块
│       ├── ComputeFrameworkEditor.Build.cs
│       ├── Public/ComputeFramework/
│       │   └── IComputeFrameworkEditorModule.h
│       └── Private/
│           ├── ComputeFrameworkEditorModule.cpp
│           ├── ComputeFrameworkCompilationTick.cpp
│           ├── ComputeGraphFromTextFactory.cpp
│           ├── ComputeGraphFromTextAssetActions.cpp
│           └── ComputeFramework/
│               ├── ComputeFrameworkEditorModule.h
│               ├── ComputeFrameworkCompilationTick.h
│               ├── ComputeGraphFromTextFactory.h
│               └── ComputeGraphFromTextAssetActions.h
└── Shaders/Private/
    ├── ComputeKernel.usf                    # Kernel 入口 shader
    ├── ComputeKernelCommon.ush              # Kernel 宏定义
    ├── ComputeDataInterfaceBuffer.ush       # Buffer DI shader 模板
    ├── ComputeDataInterfaceDispatch.ush     # Dispatch DI shader 模板
    └── BufferAlias.ush                      # float3/int3 对齐辅助
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-04 | `0a9c04c82b7a` | Fix issue where CF system view extension gets overwritten every time a new scene is created | 修复多场景场景下 ViewExtension 被覆盖的 bug |
| 2025-08-22 | `dd473bc34ead` | Fix Builder stalls by calling UpdateResources with deferred compilation check | 修复 PCG 使用时 Builder 卡顿问题 |
| 2025-08-18 | `59532358a330` | Add execution group for view-dependent work | 新增 `PostTLASBuild` execution group，支持 TLAS 构建后执行计算 |

### 维护评价

- **创建时间**：2021-11-22（在 Experimental 中），2022-08-30 迁移到 Runtime
- **活跃度**：**活跃维护** — 最近更新在 2025 年 9 月，有功能性更新和 bug 修复
- **版本状态**：仍标记为 Beta（`IsBetaVersion=true`，VersionName `0.9`），但已被 PCG、Animation Deformer 等内部系统广泛依赖
- **重要更新**：5.6 版本中 `CreateDataProvider` API 有 breaking change（deprecated 带 binding 参数的版本），5.7 中 `PreSubmit`/`PostSubmit` 从 `FRDGBuilder` 参数改为 `FComputeContext` 参数
- **已知限制**：
  - 默认不启用（`EnabledByDefault=false`），需要手动在插件设置中启用
  - 平台支持取决于 `FDataDrivenShaderPlatformInfo::GetSupportsComputeFramework()`
  - `ComputeFramework.Build.cs` 中所有依赖都是 `PrivateDependencyModuleNames`，使用时只需依赖 `ComputeFramework` 模块名即可
- **推荐**：如果你需要在 UE5 中构建自定义 GPU 计算管线，且希望引擎管理编译、调度和生命周期，推荐使用。但需要注意 API 可能随版本变化（仍为 Beta 状态）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ComputeFramework)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ComputeFramework)：插件内未发现独立测试文件
