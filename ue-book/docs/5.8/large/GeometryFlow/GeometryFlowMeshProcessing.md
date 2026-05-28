# GeometryFlow

> Geometry DataFlow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流图 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryFlowCore` (Runtime), `GeometryFlowMeshProcessing` (Runtime), `GeometryFlowMeshProcessingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryFlow) | |

## 用途

GeometryFlow 是一个实验性的**几何数据流图**框架插件。它并非直接提供几何处理工具，而是提供了一套用于构建**可配置、可中断的几何处理管线**的底层架构。

**解决的核心问题**：在游戏开发或数字内容创作中，处理高分辨率网格（如LOD生成、法线计算、碰撞体生成）通常涉及一系列复杂且耗时的操作。这些操作可能需要在工具界面中调整参数、预览结果，并可能被用户中断。传统的命令式调用方式难以管理这些复杂性。

**GeometryFlow 的解决方案**：它将每个几何处理操作抽象为一个“节点”（Node），节点之间通过“数据流”（Data Flow）连接。整个处理过程变成一个可求值的“图”（Graph）。这种设计带来几个关键优势：
1.  **模块化与复用**：每个节点（如`FSimplifyMeshNode`、`FComputeMeshNormalsNode`）封装了独立的处理逻辑，可以像积木一样自由组合。
2.  **惰性求值与缓存**：框架内置了依赖跟踪和缓存机制。只有当输入数据变化或配置改变时，才会重新计算相关节点，避免重复工作。
3.  **支持原地处理**：节点可以标记其输入数据是否可变（`Transformable`），框架能智能选择是否在原始数据上直接修改，以提升效率。
4.  **进度与取消支持**：所有节点的计算过程都集成了进度报告和取消检查，使得构建长时间运行且可交互的几何处理工具成为可能。
5.  **解耦逻辑与界面**：计算逻辑（在节点中）与用户界面（可以是编辑器工具、命令行等）完全分离。

本质上，GeometryFlow 是 Epic Games 用于构建其内部高级几何处理工具（如网格LOD工具链）的**底层引擎**，它封装了处理流程的复杂性，让开发者可以专注于定义“做什么”，而不是“如何调度和协调”。

## 使用场景

-   **你需要开发一个“一键式”资产优化工具**：例如，一个工具需要对导入的高模执行：清理几何体 -> 简化网格 -> 重新计算法线 -> 生成碰撞体 -> 计算UV -> 烘焙法线贴图。使用 GeometryFlow，你可以将这些步骤定义为一个图，用户只需调整少量参数，即可一键执行整个复杂流程，并能随时取消。
-   **你在构建一个需要复杂几何预处理管线的系统**：比如一个程序化生成系统，其输出需要经过多步几何操作才能用于游戏。使用 GeometryFlow 图来管理这个管线，可以使流程清晰、易于调试和修改。
-   **你想创建一个允许用户在UI中自由组合几何处理操作的工具**：类似于节点材质编辑器，但用于网格处理。GeometryFlow 提供了所有节点定义和图求值的基础，你可以在此之上构建UI。

## 蓝图用法

**重要说明**：GeometryFlow 主要是一个 C++ 框架，其核心节点类（如 `FSimplifyMeshNode`）和数据类型（如 `FDynamicMesh3`、`FMeshSimplifySettings`）**并非**设计为直接在蓝图中实例化和连接。蓝图更常作为高层调用者，触发基于此框架构建的编辑器工具或函数。

然而，插件包含的 `USTRUCT` 设置类型（如 `FMeshSimplifySettings`）可以在蓝图中作为配置结构使用。你通常不会在蓝图中直接操作 `FNode` 对象，而是通过封装好的 C++ 接口（例如某个 `UFUNCTION(BlueprintCallable)`）来间接驱动图。

### 核心蓝图相关类型（配置结构）

| 结构体 | 说明 | 所在头文件 |
|---|---|---|
| `FMeshSimplifySettings` | 网格简化操作的所有配置参数 | `MeshSimplifyNode.h` |
| `FMeshNormalsSettings` | 法线计算操作的配置参数 | `MeshNormalsNodes.h` |
| `FGenerateSimpleCollisionSettings` | 简单碰撞几何体生成的配置参数 | `GenerateSimpleCollisionNode.h` |
| `FMeshRecalculateUVsSettings` | UV重新计算的配置参数 | `MeshRecalculateUVsNode.h` |

### 使用示例（概念性描述）

在蓝图中，你通常不会直接看到 `FSimplifyMeshNode`。更可能的用法是：

1.  在 C++ 中，你编写一个自定义的 `UObject` 或编辑器工具类。
2.  该类拥有一个函数（标记为 `UFUNCTION(BlueprintCallable)`），函数内部构造并执行一个 GeometryFlow 图。
3.  函数参数接受 `FMeshSimplifySettings` 等 `USTRUCT`。
4.  在蓝图中，你调用这个封装好的函数，并将一个填充好的 `FMeshSimplifySettings` 变量作为参数传入。

## C++ 用法

### 头文件引入

使用核心模块和网格处理功能：
```cpp
#include "GeometryFlowCore.h"
#include "GeometryFlowMeshProcessing.h"
```

### 基本用法：创建节点并连接

以下示例展示了如何创建一个简单的网格简化节点，并执行它。这假设你已经有一个输入的 `FDynamicMesh3`。

```cpp
// 来自源码分析，基于 Public/MeshProcessingNodes/MeshSimplifyNode.h 等文件推断的典型用法
#include "GeometryFlowCore.h"
#include "GeometryFlowMeshProcessing.h"

void SimplifyMeshExample(UE::Geometry::FDynamicMesh3& MeshInOut)
{
    using namespace UE::GeometryFlow;

    // 1. 创建一个网格数据容器
    auto MeshData = MakeSafeShared<FDataDynamicMesh>();
    MeshData->SetData(MeshInOut); // 设置输入网格，注意：SetData 可能会拷贝或移动，需查看具体实现

    // 2. 创建简化设置并填充
    FMeshSimplifySettings SimplifySettings;
    SimplifySettings.TargetType = EGeomtryFlow_MeshSimplifyTargetType::TrianglePercentage;
    SimplifySettings.TargetFraction = 0.5f; // 简化到50%
    auto SettingsData = MakeSafeShared<FDataMeshSimplifySettings>();
    SettingsData->SetData(SimplifySettings);

    // 3. 创建网格简化节点
    FSimplifyMeshNode SimplifyNode;

    // 4. 创建输入/输出数据映射
    FNamedDataMap DataIn, DataOut;

    // 5. 将数据连接到节点的输入参数名上
    DataIn.SetData(FSimplifyMeshNode::InParamMesh(), MeshData);
    DataIn.SetData(FSimplifyMeshNode::InParamSettings(), SettingsData);

    // 6. 准备求值信息（可用于进度跟踪和取消）
    TUniquePtr<FEvaluationInfo> EvalInfo = MakeUnique<FEvaluationInfo>();

    // 7. 执行节点求值
    SimplifyNode.Evaluate(DataIn, DataOut, EvalInfo);

    // 8. 从输出获取结果
    if (TSafeSharedPtr<IData>* OutMeshPtr = DataOut.Find(FSimplifyMeshNode::OutParamResultMesh()))
    {
        FDynamicMesh3& ResultMesh = (*OutMeshPtr)->GetDataRef<FDynamicMesh3>((int)EMeshProcessingDataTypes::DynamicMesh);
        // 对结果网格进行操作...
        MeshInOut = MoveTemp(ResultMesh); // 移动结果出来
    }
}
```

### 进阶用法：构建一个简单的处理图

构建一个将网格简化和重新计算法线串联起来的处理流程。

```cpp
// 基于多个节点头文件推断的串联用法
void OptimizeMesh(UE::Geometry::FDynamicMesh3& Mesh)
{
    using namespace UE::GeometryFlow;

    // 创建共享数据容器
    auto SourceMeshData = MakeSafeShared<FDataDynamicMesh>();
    SourceMeshData->SetData(Mesh);
    
    // 设置参数数据（简化设置和法线设置）
    FMeshSimplifySettings SimplifySettings;
    SimplifySettings.SimplifyType = EGeometryFlow_MeshSimplifyType::AttributeAware;
    SimplifySettings.TargetType = EGeomtryFlow_MeshSimplifyTargetType::TriangleCount;
    SimplifySettings.TargetCount = 1000;
    auto SimplifySettingsData = MakeSafeShared<FDataMeshSimplifySettings>();
    SimplifySettingsData->SetData(SimplifySettings);

    FMeshNormalsSettings NormalsSettings;
    NormalsSettings.NormalsType = EGeometryFlow_ComputeNormalsType::FromFaceAngleThreshold;
    NormalsSettings.AngleThresholdDeg = 30.0;
    auto NormalsSettingsData = MakeSafeShared<FDataMeshNormalsSettings>();
    NormalsSettingsData->SetData(NormalsSettings);

    // 创建节点
    FSimplifyMeshNode SimplifyNode;
    FComputeMeshNormalsNode NormalsNode;

    // 连接第一个节点：简化
    FNamedDataMap SimplifyIn, SimplifyOut;
    SimplifyIn.SetData(FSimplifyMeshNode::InParamMesh(), SourceMeshData);
    SimplifyIn.SetData(FSimplifyMeshNode::InParamSettings(), SimplifySettingsData);
    
    TUniquePtr<FEvaluationInfo> EvalInfo1 = MakeUnique<FEvaluationInfo>();
    SimplifyNode.Evaluate(SimplifyIn, SimplifyOut, EvalInfo1);

    // 获取简化后的网格
    TSafeSharedPtr<IData> SimplifiedMeshData = SimplifyOut.GetData(FSimplifyMeshNode::OutParamResultMesh());

    // 连接第二个节点：计算法线，将简化节点的输出作为输入
    FNamedDataMap NormalsIn, NormalsOut;
    NormalsIn.SetData(FComputeMeshNormalsNode::InParamMesh(), SimplifiedMeshData);
    NormalsIn.SetData(FComputeMeshNormalsNode::InParamSettings(), NormalsSettingsData);

    TUniquePtr<FEvaluationInfo> EvalInfo2 = MakeUnique<FEvaluationInfo>();
    NormalsNode.Evaluate(NormalsIn, NormalsOut, EvalInfo2);

    // 最终输出
    if (TSafeSharedPtr<IData>* FinalMeshPtr = NormalsOut.Find(FComputeMeshNormalsNode::OutParamResultMesh()))
    {
        Mesh = MoveTemp((*FinalMeshPtr)->GetDataRef<FDynamicMesh3>((int)EMeshProcessingDataTypes::DynamicMesh));
    }
}
```

## Demo 示例

一个可编译的最小示例，演示如何使用 `FSimpleInPlaceProcessMeshBaseNode` 派生一个自定义的“计算顶点法线”节点。

```cpp
// MySimpleNormalsNode.h
#pragma once

#include "GeometryFlowCore.h"
#include "GeometryFlowMeshProcessing.h" // 包含基类 FSimpleInPlaceProcessMeshBaseNode

namespace MyGeometryFlow
{
    using namespace UE::GeometryFlow;
    using namespace UE::Geometry;

    /**
     * 一个简单的原地计算网格顶点法线的节点。
     */
    class FMySimplePerVertexNormalsNode : public FSimpleInPlaceProcessMeshBaseNode
    {
        static constexpr int Version = 1;
        GEOMETRYFLOW_NODE_INTERNAL(FMySimplePerVertexNormalsNode, Version, FSimpleInPlaceProcessMeshBaseNode)

    public:
        // 只需要实现这一个函数
        virtual void ApplyNodeToMesh(FDynamicMesh3& MeshInOut, TUniquePtr<FEvaluationInfo>& EvaluationInfo) override
        {
            // 使用 GeometryProcessing 模块中的工具函数快速计算顶点法线
            FMeshNormals::QuickComputeVertexNormals(MeshInOut, false);
        }
    };
}
```

```cpp
// MySimpleNormalsNode.cpp
#include "MySimpleNormalsNode.h"

// 如果需要在图中注册此节点，可能需要在此文件或模块的 Startup 中进行注册。
// 具体注册方式需参考 GeometryFlowCore 中的节点注册机制。
```

**使用示例**：
```cpp
// 在另一个文件中使用
#include "MySimpleNormalsNode.h"

void RecalculateMyNormals(UE::Geometry::FDynamicMesh3& Mesh)
{
    using namespace MyGeometryFlow;

    auto MeshData = MakeSafeShared<FDataDynamicMesh>();
    MeshData->SetData(Mesh);

    FMySimplePerVertexNormalsNode MyNode;

    FNamedDataMap DataIn, DataOut;
    DataIn.SetData(FMySimplePerVertexNormalsNode::InParamMesh(), MeshData);

    TUniquePtr<FEvaluationInfo> EvalInfo = MakeUnique<FEvaluationInfo>();
    MyNode.Evaluate(DataIn, DataOut, EvalInfo);

    if (TSafeSharedPtr<IData>* OutData = DataOut.Find(FMySimplePerVertexNormalsNode::OutParamResultMesh()))
    {
        Mesh = MoveTemp((*OutData)->GetDataRef<FDynamicMesh3>((int)EMeshProcessingDataTypes::DynamicMesh));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供底层的几何算法（简化、法线计算、UV展开、凸包生成等），是所有节点功能的核心。 |
| `MeshModelingToolsetExp` | 可能提供了一些实验性的建模工具，GeometryFlow 中的某些节点可能依赖其提供的特定算法或数据类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新版 UE_LOGF 宏，属于代码现代化维护。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码规范修复，将默认析构函数从显式定义改回 `= default`。 |
| 2025-10-23 | `3acea6cd` | add geometric tolerance to mesh->convex hull simplification path, to allow simplification below the | 为网格到凸包的简化路径添加几何容差，允许更激进的简化。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 代码生成优化，内联生成的CPP文件以提升编译性能。 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 代码规范修复，确保API导出宏（DLL storage）正确应用于方法和静态变量。 |

### 维护评价

**综合评价：活跃维护中的实验性框架。**

-   **创建时间**：2020 年 11 月，至今约 5 年，属于“老古董”级别。
-   **近期活动**：最近一次提交在 2026 年 4 月，且 2025 年内有多次针对代码规范、性能优化和功能增强的提交。这表明该插件**仍在被 Epic 的工程师维护和使用**，并非已废弃。
-   **维护内容**：更新主要是**底层维护和优化**（日志迁移、代码修复、编译优化），而非大规模的功能增加。这符合其作为“框架/基础设施”的定位。
-   **实验状态**：`.uplugin` 中明确标记 `IsExperimentalVersion: true`，且默认未启用。这意味着 API 可能不稳定，不建议在正式项目中直接深度依赖，除非你有能力跟进可能的改动。
-   **已知限制**：作为底层框架，它没有自己的编辑器UI，使用门槛较高，需要深厚的 C++ 和几何处理知识。文档几乎缺失（`DocsURL` 为空）。
-   **推荐使用**：如果你在开发一个**需要高度定制化几何处理流程的编辑器工具或插件**，并且愿意研究和使用实验性 API，GeometryFlow 是一个强大且设计良好的基础框架。对于仅需要使用现成几何处理功能的普通开发者，建议直接使用 `GeometryProcessing` 模块或引擎内置的建模工具。

**警告**：此插件标记为实验性，API 随时可能发生破坏性更改。在生产环境中使用需谨慎，并做好维护的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryFlow)
- [官方文档]() (无，`.uplugin` 中 `DocsURL` 为空)
- [测试用例]() (未在提供的信息中明确指明路径，可能位于 `Engine/Tests/` 下或插件内部的测试模块中)