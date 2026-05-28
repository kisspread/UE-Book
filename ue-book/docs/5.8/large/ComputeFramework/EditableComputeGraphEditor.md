# Compute Framework

> Support for user authored GPU compute graphs

| 属性 | 值 |
|---|---|
| 中文名 | 计算框架 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ComputeFramework` (Runtime), `ComputeFrameworkEditor` (Editor), `ComputeDataInterface` (Runtime), `EditableComputeGraph` (Runtime), `EditableComputeGraphEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework) | |

## 用途

ComputeFramework 是一个实验性的 GPU 计算图框架。它不仅仅是渲染工具，更是一个让开发者能够通过图形化界面（类似蓝图节点图）来编写、连接和调度 GPU 计算任务（Compute Shaders）的系统。

核心解决的问题是：将复杂的 GPU 计算逻辑（如物理模拟、粒子系统、后处理、AI 推理等）从硬编码的 C++/HLSL 中解放出来，使其可以通过资产（`UEditableComputeGraph`）进行可视化编辑和动态编排，从而提高迭代效率和复用性。

## 使用场景

- 你需要快速原型化一个新的 GPU 算法（例如，自定义的粒子动力学、地形生成、流体模拟），并希望直观地看到数据流和连接关系。
- 你的项目中有多个需要协同工作的 GPU 计算内核，希望通过图形化工具管理它们之间的数据传递和执行顺序。
- 你正在开发一个程序化内容生成（PCG）或其他需要大规模 GPU 并行计算的系统，希望有一个通用的图编辑器来组织计算单元。
- 你作为技术美术（Technical Artist），需要在不深入编写底层代码的情况下，配置和调试 GPU 计算逻辑。

## 蓝图用法

该插件的核心功能是编辑器工具包和运行时计算图管理，其公开的 `BlueprintCallable` 函数非常有限，主要面向 C++ 或编辑器脚本。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileGraph` | 触发对当前 `UEditableComputeGraph` 资产的编译，将其描述转化为可执行的着色器。 | `FEditableComputeGraphEditorToolkit` |
| `GetCompileState` | 查询计算图的编译状态（最新、需要重新编译、有错误）。 | `FEditableComputeGraphEditorToolkit` |

### 使用示例（蓝图描述）

由于该插件主要提供编辑器工具和运行时管理类，蓝图中直接使用通常涉及通过 `Editor Scripting Utilities` 插件或 C++ 接口来加载和操作 `UEditableComputeGraph` 资产。直接在游戏逻辑中“使用”计算图，通常需要调用 `ComputeFramework` 运行时模块提供的更低级 API 来调度执行。

## C++ 用法

### 头文件引入

```cpp
// 访问可编辑计算图资产
#include "EditableComputeGraph/EditableComputeGraph.h"

// 使用运行时计算框架核心
#include "ComputeFramework/ComputeFramework.h"

// 如果需要在自己的编辑器中集成或扩展图表编辑
#include "EditableComputeGraphEditor/EditableComputeGraphEditorToolkit.h"
```

### 基本用法（编辑器扩展）

创建和打开一个 `UEditableComputeGraph` 资产的编辑器实例。

```cpp
// 来源：基于 UAssetDefinition_EditableComputeGraph::OpenAssets 的逻辑推断
#include "AssetEditorToolkit.h"
#include "EditableComputeGraph/EditableComputeGraph.h"
#include "EditableComputeGraphEditor/EditableComputeGraphEditorToolkit.h"

void OpenComputeGraphEditor(UEditableComputeGraph* ComputeGraphAsset)
{
    if (ComputeGraphAsset)
    {
        // 通过工厂方法创建编辑器工具包实例
        TSharedRef<FEditableComputeGraphEditorToolkit> EditorToolkit =
            FEditableComputeGraphEditorToolkit::Create(
                ComputeGraphAsset,
                EToolkitMode::Standalone,
                TSharedPtr<IToolkitHost>()
            );
        // 编辑器会自动注册并显示在虚幻编辑器中
    }
}
```

### 进阶用法（编译和状态检查）

```cpp
// 假设你已经持有一个指向 FEditableComputeGraphEditorToolkit 的指针 EditorToolkit
void RecompileIfDirty(FEditableComputeGraphEditorToolkit* EditorToolkit)
{
    if (EditorToolkit)
    {
        // 检查编译状态
        FEditableComputeGraphEditorToolkit::ECompileState State = EditorToolkit->GetCompileState();
        if (State == FEditableComputeGraphEditorToolkit::ECompileState::NeedsCompile)
        {
            // 如果图表已修改但未编译，则触发编译
            EditorToolkit->CompileGraph();
            UE_LOG(LogTemp, Log, TEXT("Compute Graph compilation triggered."));
        }
        else if (State == FEditableComputeGraphEditorToolkit::ECompileState::Broken)
        {
            UE_LOG(LogTemp, Warning, TEXT("Compute Graph has compilation errors. Check the Output log."));
        }
    }
}
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何程序化地创建一个简单的 `UEditableComputeGraph` 资产，并为其添加一个内核（Kernel）。**请注意**：该资产的“编辑”和“运行”主要依赖于其专属的编辑器工具包和 `ComputeFramework` 的运行时调度。

```cpp
// MyComputeGraphDemo.h
#pragma once

#include "CoreMinimal.h"
#include "EditableComputeGraph/EditableComputeGraph.h"
#include "MyComputeGraphDemo.generated.h"

UCLASS()
class UMyComputeGraphDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 创建一个示例计算图资产 */
    UFUNCTION(BlueprintCallable, Category = "ComputeFrameworkDemo")
    static UEditableComputeGraph* CreateDemoGraph(UObject* Outer);

    /** 向图表中添加一个示例内核 */
    static void AddSampleKernel(UEditableComputeGraph* Graph);
};
```

```cpp
// MyComputeGraphDemo.cpp
#include "MyComputeGraphDemo.h"
#include "EditableComputeGraph/ComputeGraphKernelDesc.h" // 包含 FComputeGraphKernelDesc 定义

UEditableComputeGraph* UMyComputeGraphDemo::CreateDemoGraph(UObject* Outer)
{
    // 创建一个临时资产（实际使用通常保存到磁盘）
    UEditableComputeGraph* NewGraph = NewObject<UEditableComputeGraph>(Outer, UEditableComputeGraph::StaticClass(), FName("DemoComputeGraph"), RF_Transient);

    if (NewGraph)
    {
        AddSampleKernel(NewGraph);
        UE_LOG(LogTemp, Log, TEXT("Demo Compute Graph created with one kernel."));
    }
    return NewGraph;
}

void UMyComputeGraphDemo::AddSampleKernel(UEditableComputeGraph* Graph)
{
    if (!Graph) return;

    // 1. 创建内核描述结构体
    FComputeGraphKernelDesc KernelDesc;
    KernelDesc.KernelName = TEXT("SimpleAdditionKernel");
    KernelDesc.EntryPoint = TEXT("MainCS"); // HLSL 入口函数名

    // 2. 定义一个简单的 HLSL 计算内核源码
    // 注意：这是示意代码，实际的HLSL需要符合Compute Framework的约定（如使用DI_前缀函数）
    KernelDesc.SourceText = TEXT(R"(
        // 简单的计算内核，将两个输入相加
        RWBuffer<float> ResultBuffer;
        Buffer<float> InputA;
        Buffer<float> InputB;

        [numthreads(64,1,1)]
        void MainCS(uint3 DTid : SV_DispatchThreadID)
        {
            // 实际项目中，这里应调用通过DI_前缀函数声明的接口
            // 例如: ResultBuffer[DTid.x] = DI_ReadValue_InputA(DTid.x) + DI_ReadValue_InputB(DTid.x);
            ResultBuffer[DTid.x] = InputA[DTid.x] + InputB[DTid.x];
        }
    )");

    // 3. 将内核描述添加到图表的内核数组中
    Graph->Kernels.Add(KernelDesc);
    // 4. 标记图表已修改（脏状态）
    Graph->MarkPackageDirty();
}
```

## 模块依赖

从插件的模块构成和核心功能（GPU计算、着色器编译、图形化编辑）推断，使用者需要依赖以下非标准模块。**以下为常见模块已省略**。

| 模块 | 用途 |
|---|---|
| `RenderCore` | GPU 渲染核心基础设施，包括着色器编译管线、渲染命令等。 |
| `Renderer` | 虚幻引擎的渲染器，可能用于集成计算任务到渲染流水线。 |
| `ShaderCore` | 着色器核心库，提供 HLSL 相关的工具和类型。 |
| `Slate` | 用于构建资产编辑器自定义 UI（如 `SComputeGraphView`, `SComputeGraphHlslEditor`）。 |
| `EditorFramework` | 提供 `FAssetEditorToolkit` 基类，用于构建资产编辑器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `057cf5d7` | ComputeFramework: Fix data races on FComputeKernelShaderMap registries. | 修复了计算内核着色器映射注册表中的数据竞争问题，提升了多线程安全性。 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases (S | 为数据接口添加了按内核的输出掩码功能，与Optimus动画系统协同，允许更精细的控制。 |
| 2026-04-21 | `f1e2ebe5` | [PCG][GPUPROFILER] Add support for user-provided stat objects to retrieve timing data from GPU execu | 与PCG和GPU Profiler集成，支持使用用户自定义的统计对象来获取GPU执行时间数据。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，可能是为了结构化日志或格式优化。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构了着色器作业结构，移除了显式的完成/释放标志，代之以更扩展的机制。 |

### 维护评价

- **活跃维护**：尽管插件被标记为实验性 (`IsBetaVersion: true`) 且默认禁用，但从 git 历史看，**最近（2026年4-5月）仍有密集的功能更新和核心修复**。
- **集成活跃**：近期的更新显示该框架正在与 **Optimus（动画）** 和 **PCG（程序化生成）** 等其他重要系统集成，表明其仍在积极开发和应用中。
- **版本状态**：版本号为 0.9，仍处于 Beta 阶段，API 和功能可能发生变化。
- **推荐程度**：**推荐有需求的团队在开发环境或原型项目中评估和使用**。它提供了一种强大的 GPU 计算图化编辑方案，但需注意其实验性状态，不建议直接用于稳定的生产版本，除非团队有能力跟踪和适配其 API 变更。长期未更新的警告不适用，因为它目前是活跃的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework)
- [官方文档]() （无）
- [测试用例]() （无提供信息）