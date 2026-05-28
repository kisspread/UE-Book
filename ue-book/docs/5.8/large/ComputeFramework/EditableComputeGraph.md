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
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework) | |

## 用途

Compute Framework 是一个用于在 UE 中可视化创建和执行 GPU Compute Shader 图的运行时框架。它解决的核心问题是：**如何让非 Shader 程序员也能构建自定义的 GPU 计算管线**。

具体来说，这个插件提供了一套数据驱动的系统，用户可以：

1. **定义计算内核（Kernel）**：在图形中描述 HLSL 源码、入口函数、线程组大小
2. **声明数据接口（Data Interface）**：抽象出数据的读写能力，一个接口可以暴露多个 HLSL 函数
3. **绑定游戏对象（Binding Object）**：将数据接口与 ActorComponent 绑定，运行时获取实际数据
4. **通过引脚（Pin）连接**：将内核的 HLSL 参数映射到数据接口的读/写函数

这本质上是一个 **Compute Shader 的节点图（Node Graph）编排系统**。它被 PCG（Procedural Content Generation）框架、Optimus（动画蓝图中的 Deformer Graph）等系统使用。

> ⚠️ 该插件处于实验阶段（IsBetaVersion=true），且默认未启用，需要手动激活。

## 使用场景

- **PCG 框架**：程序化内容生成中的 GPU 加速计算（如点云处理、地形生成）
- **Optimus / Deformer Graph**：角色动画的 GPU 变形器，如肌肉模拟、布料变形
- **自定义 GPU 后处理**：需要在渲染管线中插入自定义计算通道
- **物理模拟**：GPU 加速的粒子系统或流体模拟
- **数据处理管线**：大规模顶点/体素数据的 GPU 批处理

## 蓝图用法

Compute Framework 主要通过资产编辑器使用，运行时 API 较少直接暴露给蓝图。核心工作流在编辑器中完成，生成的 `UComputeGraph` 资产可以在运行时执行。

### 核心类

| 类 | 说明 | 所在模块 |
|---|---|---|
| `UComputeGraph` | 计算图的基类，定义图的拓扑结构 | `ComputeFramework` |
| `UEditableComputeGraph` | 可编辑的计算图实现，支持编辑器中的可视化编排 | `EditableComputeGraph` |
| `UComputeDataInterface` | 数据接口基类，定义数据读写函数 | `ComputeDataInterface` |
| `FComputeGraphDesc` | 图描述结构体，包含所有内核、绑定对象和数据接口 | `EditableComputeGraph` |

### 核心结构体

| 结构体 | 说明 | 所在模块 |
|---|---|---|
| `FComputeGraphKernelDesc` | 描述一个计算内核：HLSL 源码、入口点、线程组大小、输入输出引脚 | `EditableComputeGraph` |
| `FKernelPin` | 描述内核引脚：将 HLSL 参数映射到数据接口函数 | `EditableComputeGraph` |
| `FComputeGraphDataInterfaceDesc` | 描述数据接口：类型、绑定对象、实例设置 | `EditableComputeGraph` |
| `FComputeGraphDataBindingObjectDesc` | 描述绑定对象：名称和 ActorComponent 类型 | `EditableComputeGraph` |

### 典型工作流

1. 在编辑器中创建 `EditableComputeGraph` 资产
2. 添加 Binding Object（绑定到游戏中的 ActorComponent）
3. 添加 Data Interface（选择数据接口类型并配置参数）
4. 添加 Kernel（编写 HLSL 代码，定义输入输出引脚）
5. 将 Kernel 的引脚连接到 Data Interface 的函数
6. 点击 Compile 编译 Shader
7. 在运行时通过 ComputeFramework 的执行系统调度执行

## C++ 用法

### 头文件引入

```cpp
#include "ComputeFramework.h"
#include "ComputeFramework/ComputeGraph.h"
#include "ComputeFramework/ComputeKernel.h"
#include "EditableComputeGraph/EditableComputeGraph.h"
```

### 基本用法：定义数据接口

要创建自定义的数据接口，需要继承 `UComputeDataInterface` 并实现数据读写函数。

```cpp
// MyDataInterface.h
#pragma once

#include "ComputeFramework/ComputeDataInterface.h"
#include "MyDataInterface.generated.h"

UCLASS(BlueprintType, EditInlineNew, Category = "Compute")
class UMyDataInterface : public UComputeDataInterface
{
    GENERATED_BODY()

public:
    // 声明该接口暴露给内核的 HLSL 函数
    // 具体函数签名需参考 ComputeDataInterface 的虚函数实现
};
```

### 基本用法：使用图描述构建计算图

```cpp
// 来源: EditableComputeGraph.h
// FComputeGraphDesc 是图的顶层描述

FComputeGraphDesc GraphDesc;

// 1. 添加绑定对象 - 声明运行时可用的组件
FComputeGraphDataBindingObjectDesc BindingDesc;
BindingDesc.Name = FName("MyBinding");
BindingDesc.Type = UMyComponent::StaticClass();
GraphDesc.BindingObjects.Add(BindingDesc);

// 2. 添加数据接口
FComputeGraphDataInterfaceDesc DataInterfaceDesc;
DataInterfaceDesc.Name = FName("MyData");
DataInterfaceDesc.BindingObjectName = FName("MyBinding");
DataInterfaceDesc.Type = UMyDataInterface::StaticClass();
GraphDesc.DataInterfaces.Add(DataInterfaceDesc);

// 3. 添加计算内核
FComputeGraphKernelDesc KernelDesc;
KernelDesc.Name = FName("MyKernel");
KernelDesc.EntryPoint = TEXT("MainCS");
KernelDesc.GroupSize = FIntVector(64, 1, 1);
KernelDesc.SourceText = TEXT(R"(
    // HLSL compute shader source
    [numthreads(64, 1, 1)]
    void MainCS(uint3 DTid : SV_DispatchThreadID)
    {
        // compute logic here
    }
)");

// 4. 连接引脚
FKernelPin InputPin;
InputPin.KernelFunctionName = TEXT("ReadInput");
InputPin.DataInterfaceName = FName("MyData");
InputPin.DataInterfaceFunctionName = TEXT("GetBuffer");
KernelDesc.Inputs.Add(InputPin);

GraphDesc.Kernels.Add(KernelDesc);
```

### 进阶用法：监听编译结果

```cpp
// 来源: EditableComputeGraph.h - OnCompileOutputChanged delegate

// 在编辑器中，可以监听每个内核的编译完成事件
if (UEditableComputeGraph* EditableGraph = Cast<UEditableComputeGraph>(GraphAsset))
{
    EditableGraph->OnCompileOutputChanged.AddLambda(
        [](int32 KernelIndex, const FComputeKernelCompileResults& Results)
        {
            if (Results.bSucceeded)
            {
                UE_LOG(LogTemp, Log, TEXT("Kernel %d compiled successfully"), KernelIndex);
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Kernel %d compilation failed"), KernelIndex);
            }
        }
    );

    // 触发图重建和 Shader 编译
    EditableGraph->RebuildGraph();
}
```

## Demo 示例

### 自定义 ComputeDataInterface

```cpp
// MyPointDataInterface.h
#pragma once

#include "ComputeFramework/ComputeDataInterface.h"
#include "MyPointDataInterface.generated.h"

UCLASS(EditInlineNew, BlueprintType, Category = "Compute")
class MYMODULE_API UMyPointDataInterface : public UComputeDataInterface
{
    GENERATED_BODY()

public:
    /** 每个点的位置 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Data")
    TArray<FVector> Positions;

    /** 获取 HLSL 源码片段，定义数据接口的声明 */
    virtual FString GetShaderSource(const FString& EntryPoint) const override;
    
    /** 声明数据接口暴露给内核的参数列表 */
    virtual void GetShaderParameters(
        TArray<FComputeKernelShaderParameterInfo>& OutParameters
    ) const override;
};
```

```cpp
// MyPointDataInterface.cpp
#include "MyPointDataInterface.h"

FString UMyPointDataInterface::GetShaderSource(const FString& EntryPoint) const
{
    // 返回 HLSL 头文件或函数声明
    return TEXT(R"(
        StructuredBuffer<float3> PointPositions;
        
        float3 ReadPointPosition(uint Index)
        {
            return PointPositions[Index];
        }
    )");
}

void UMyPointDataInterface::GetShaderParameters(
    TArray<FComputeKernelShaderParameterInfo>& OutParameters) const
{
    // 绑定 SRV 参数
    OutParameters.Add({TEXT("PointPositions"), 
        EComputeKernelShaderParameterType::SRV});
}
```

## 模块依赖

该插件由 5 个模块组成，各模块职责：

| 模块 | 类型 | 职责 |
|---|---|---|
| `ComputeFramework` | Runtime | 核心运行时：图调度、Kernel 编译、GPU 资源管理 |
| `ComputeDataInterface` | Runtime | 数据接口基类和内置实现 |
| `EditableComputeGraph` | Runtime | 可编辑图的数据结构（FComputeGraphDesc 等） |
| `ComputeFrameworkEditor` | Editor | 图编译器、Shader 管理工具 |
| `EditableComputeGraphEditor` | Editor | 可视化图编辑器 UI |

使用该插件时，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | 运行时图执行和调度 |
| `ComputeDataInterface` | 自定义数据接口基类 |
| `EditableComputeGraph` | 创建和编辑计算图资产 |
| `RenderCore` | Shader 编译和渲染管线集成 |
| `RHI` | 底层 GPU 资源抽象 |

> 注：模块依赖基于插件的通用需求推断，实际依赖请参考各模块的 Build.cs 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `057cf5d7` | ComputeFramework: Fix data races on FComputeKernelShaderMap registries. | 修复 ShaderMap 注册表的多线程数据竞争 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases... | 为数据接口添加逐内核输出掩码（与 Optimus 联动） |
| 2026-04-21 | `f1e2ebe5` | [PCG][GPUPROFILER] Add support for user-provided stat objects to retrieve timing data from GPU execution | 添加用户自定义 GPU 性能统计对象支持 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored... | 重构 Shader 编译作业的状态管理 |

### 维护评价

**活跃维护** 🟢

- **年龄**：约 4 年，2022 年从 Experimental 目录移至正式 Runtime 目录
- **更新频率**：最近 2 个月内有 5 次提交，更新非常频繁
- **维护内容**：涵盖 Bug 修复（数据竞争）、新功能（Per-kernel output mask）、性能优化（GPU profiler 支持）和代码现代化
- **实验性状态**：仍标记为 IsBetaVersion=true，API 可能发生变化
- **核心用户**：PCG 框架和 Optimus/DeformerGraph 是主要消费者，Epic 持续投入维护

> ⚠️ 虽然维护活跃，但该插件仍处于 Beta 状态。在生产环境中使用需谨慎，API 可能在版本间发生破坏性变更。建议将其作为底层基础设施使用，通过 PCG 或 Optimus 等更稳定的上层系统间接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework)
- 官方文档：暂无
- [PCG 框架文档](https://docs.unrealengine.com/5.8/en-US/procedural-content-generation-framework-in-unreal-engine/)（Compute Framework 的主要使用者之一）
- [Optimus / Deformer Graph](https://docs.unrealengine.com/5.8/en-US/deformer-graph-in-unreal-engine/)（另一个主要使用者）