# GeometryFlow

> Geometry DataFlow Graph（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryFlowCore` (Runtime), `GeometryFlowMeshProcessing` (Runtime), `GeometryFlowMeshProcessingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryFlow) | |

## 用途
GeometryFlow 是一个实验性的几何数据处理图插件。它并非解决单一的几何问题，而是为复杂的、多步骤的几何处理操作（如网格简化、UV生成、法线计算等）提供一个基于节点图（Node Graph）的系统化框架。其核心目标是将这些昂贵的计算操作流程化、可视化，使得用户能够通过连接不同的处理节点来构建可复用的几何处理管道，从而将高精度源资产（如高模）高效地转换为游戏可用的资产（如带有LOD和碰撞的静态网格）。

## 使用场景
- 你需要将一个高分辨率、带复杂材质的扫描模型，转换成一个游戏引擎可直接使用的、带有多级LOD和碰撞体的静态网格资产。
- 你需要构建一套标准化的网格处理流程，并希望它能被参数化控制、易于调整和复用，例如用于程序化生成或批量处理工具。
- 你正在开发建模工具（如 Unreal 的 Modeling Mode 工具），并希望在其内部以清晰的流程图方式实现复杂的处理逻辑。

## 蓝图用法
此插件主要提供运行时节点和编辑器支持节点，用于构建几何处理图。蓝图用法主要围绕创建和配置这些节点。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MeshAutoGenerateUVs Node` | 创建一个自动UV生成节点。 | `FMeshAutoGenerateUVsNode` (C++类，蓝图中通过工厂函数创建) |
| `Set MeshAutoGenerateUVs Settings` | 配置自动生成UV的参数，如算法（PatchBuilder， UVAtlas， XAtlas）、迭代次数、打包尺寸等。 | `FMeshAutoGenerateUVsSettings` (USTRUCT) |

### 使用示例（蓝图描述）
1.  **构建处理链**：在蓝图中，你可以实例化不同的处理节点（如“加载网格”节点、“自动UV生成”节点、“网格简化”节点）。将前一个节点的“输出网格”引脚连接到后一个节点的“输入网格”引脚，形成一条处理流水线。
2.  **参数化配置**：为“自动UV生成”节点创建一个 `FMeshAutoGenerateUVsSettings` 结构体变量，设置 `Method` 为 `PatchBuilder`，调整 `NumInitialPatches` 和 `SmoothingSteps` 等参数，然后将这个设置连接到节点的设置输入引脚。
3.  **执行与输出**：触发整个图的执行（例如通过一个“执行”按钮）。最终处理完成的网格可以从终端节点的输出引脚获取，并用于后续的资产生成操作。

## C++ 用法
GeometryFlow 主要是一个 C++ 框架，用于在代码中定义、连接和执行处理节点。

### 头文件引入
```cpp
// 核心数据类型和图系统
#include "GeometryFlowCoreModule.h" 
// 网格处理相关节点
#include "MeshProcessingNodes/MeshAutoGenerateUVsNode.h" 
// 编辑器扩展节点（如UV生成）
#include "MeshProcessingNodes/MeshAutoGenerateUVsNode.h" // 注意：UV生成节点在Editor模块
// 节点注册（编辑器中需要）
#include "MeshProcessingEditorNodeRegistration.h"
```

### 基本用法
以下示例展示如何在 C++ 中创建一个简单的节点图来处理网格。
(来源：基于 `MeshAutoGenerateUVsNode.h` 和插件设计模式推断)
```cpp
// 1. 准备输入数据
using namespace UE::GeometryFlow;
FMeshAutoGenerateUVsSettings UVSettings;
UVSettings.Method = EGeometryFlow_AutoUVMethod::PatchBuilder;
UVSettings.NumInitialPatches = 200;

// 2. 创建输入数据映射
FNamedDataMap DatasIn;
DatasIn.AddData(TEXT("Mesh"), /* 一个 FDynamicMesh3 的智能指针 */);
DatasIn.AddData(TEXT("Settings"), MakeShared<FMeshAutoGenerateUVsSettings>(UVSettings));

// 3. 实例化处理节点
FMeshAutoGenerateUVsNode UVNode;

// 4. 评估节点
TUniquePtr<FEvaluationInfo> EvalInfo;
UVNode.Evaluate(DatasIn, EvalInfo);

// 5. 获取输出
TSharedPtr<FDynamicMesh3> ResultMesh;
UVNode.GetOutput(TEXT("Mesh"), ResultMesh); // 假设的输出获取接口
```

### 进阶用法
自定义节点，继承 `TProcessMeshWithSettingsBaseNode`。
```cpp
// MyCustomNode.h
USTRUCT()
struct FMyCustomSettings
{
    GENERATED_USTRUCT_BODY()
    // 定义你的参数
    UPROPERTY(EditAnywhere, Category = "My Custom")
    float SomeParameter = 1.0f;
};

class FMyCustomProcessNode : public TProcessMeshWithSettingsBaseNode<FMyCustomSettings>
{
    GEOMETRYFLOW_NODE_INTERNAL(FMyCustomProcessNode, 1, FNode)

    virtual void ProcessMesh(
        const FNamedDataMap& DatasIn,
        const FMyCustomSettings& Settings,
        const FDynamicMesh3& MeshIn,
        FDynamicMesh3& MeshOut,
        TUniquePtr<FEvaluationInfo>& EvaluationInfo) override
    {
        // 在这里实现你自定义的网格处理逻辑
        // 使用 Settings.SomeParameter 和 MeshIn， 输出到 MeshOut
    }
};
```

## Demo 示例
一个最小的、可编译的示例，演示如何构建并运行一个包含单个节点的图。
（注意：此示例侧重于框架使用，并非完整的工具链。）

**CustomGeometryFlowNode.h**
```cpp
#pragma once
#include "GeometryFlowCore/Node.h"
#include "GeometryFlowCore/DataTypes.h"
#include "GeometryFlowCore/NamedDataMap.h"
#include "DynamicMesh/DynamicMesh3.h"

namespace UE { namespace GeometryFlow {

// 定义一个简单的设置结构体
USTRUCT()
struct FSimpleMeshScaleSettings
{
    GENERATED_USTRUCT_BODY()
    UPROPERTY(EditAnywhere)
    double ScaleFactor = 1.0;
};

// 定义一个缩放网格的节点
class FSimpleMeshScaleNode : public FNode
{
public:
    // 输入输出类型声明（简化）
    using FInputMesh = TDataDefinition<TSharedPtr<FDynamicMesh3>>;
    using FInputSettings = TDataDefinition<FSimpleMeshScaleSettings>;
    using FOutputMesh = TDataDefinition<TSharedPtr<FDynamicMesh3>>;

    GEOMETRYFLOW_NODE_INTERNAL(FSimpleMeshScaleNode, 1, FNode)

    FSimpleMeshScaleNode()
    {
        // 设置输入输出端口
        AddInput(FInputMesh::MakeIdentifier(), FInputMesh::DefaultValue());
        AddInput(FInputSettings::MakeIdentifier(), FInputSettings::DefaultValue());
        AddOutput(FOutputMesh::MakeIdentifier(), FOutputMesh::DefaultValue());
    }

    virtual void Evaluate(const FNamedDataMap& DatasIn, TUniquePtr<FEvaluationInfo>& EvaluationInfo) override
    {
        // 获取输入
        TSharedPtr<FDynamicMesh3> InputMesh;
        FSimpleMeshScaleSettings Settings;
        GetInputData(DatasIn, FInputMesh::MakeIdentifier(), InputMesh);
        GetInputData(DatasIn, FInputSettings::MakeIdentifier(), Settings);

        if (InputMesh.IsValid())
        {
            // 执行处理：缩放顶点
            FDynamicMesh3* OutMesh = new FDynamicMesh3(*InputMesh); // 复制
            for (int VertexID : OutMesh->VertexIndicesItr())
            {
                FVector3d Pos = OutMesh->GetVertex(VertexID);
                OutMesh->SetVertex(VertexID, Pos * Settings.ScaleFactor);
            }

            // 设置输出
            SetOutputData(FOutputMesh::MakeIdentifier(), MakeShareable(OutMesh));
        }
    }
};

}} // namespace UE::GeometryFlow
```

**MyGeometryFlowTest.cpp**
```cpp
#include "CustomGeometryFlowNode.h"
#include "GeometryFlowCore/NamedDataMap.h"

void TestSimpleGeometryFlow()
{
    using namespace UE::GeometryFlow;

    // 1. 创建一个简单的立方体网格
    FDynamicMesh3 Mesh;
    // ... (此处省略创建立方体的代码，假设已创建一个简单网格)

    // 2. 创建设置
    FSimpleMeshScaleSettings ScaleSettings;
    ScaleSettings.ScaleFactor = 2.0;

    // 3. 构建输入数据映射
    FNamedDataMap DatasIn;
    DatasIn.AddData(FSimpleMeshScaleNode::FInputMesh::MakeIdentifier(), MakeShareable(&Mesh));
    DatasIn.AddData(FSimpleMeshScaleNode::FInputSettings::MakeIdentifier(), ScaleSettings);

    // 4. 创建节点并执行
    FSimpleMeshScaleNode ScaleNode;
    TUniquePtr<FEvaluationInfo> EvalInfo;
    ScaleNode.Evaluate(DatasIn, EvalInfo);

    // 5. 获取结果
    TSharedPtr<FDynamicMesh3> ScaledMesh;
    ScaleNode.GetOutputData(FSimpleMeshScaleNode::FOutputMesh::MakeIdentifier(), ScaledMesh);

    if (ScaledMesh.IsValid())
    {
        // ScaledMesh 中的网格现在是原始网格的两倍大小
    }
}
```

## 模块依赖
要使用此插件，你的项目或模块需要依赖以下插件和模块（从 .uplugin 和 Build.cs 推断）：
| 模块/插件 | 用途 |
|---|---|
| `GeometryProcessing` | 提供核心的几何处理算法和数据结构（如 `FDynamicMesh3`） |
| `MeshModelingToolsetExp` | 提供实验性的网格建模工具集，可能与此插件协作 |
| `GeometryScript` | 提供蓝图友好的几何脚本扩展 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，属于全局日志系统升级。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全局代码风格统一，将空析构函数改为 `= default`。 |
| 2025-10-23 | `3acea6cd` | add geometric tolerance to mesh->convex hull simplification path, to allow simplification below the | 在网格到凸包的简化路径中添加几何容差，允许更激进的简化。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为源码文件添加内联生成代码宏，优化编译。 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修正头文件，确保DLL导出/导入标记作用在方法和静态变量上，而非类型。 |

### 维护评价
GeometryFlow 是一个创建于 2020 年底的实验性原型插件。**最近的提交（2025-2026年）均为引擎范围内的代码风格统一、宏迁移或编译优化，并非针对此插件的功能性更新或 Bug 修复。** 这表明该插件的核心功能早已停止开发，可能仅作为某些内部工具或概念验证的底层代码存在。
- **状态**：维护不活跃，实验性，且默认不启用、不安装。
- **问题**：官方文档缺失，API 稳定性未知，未发现活跃的社区使用或维护迹象。
- **推荐**：**不推荐用于生产项目**。它适合作为学习 Epic 如何设计几何处理管道的参考，或作为开发类似系统时的灵感来源。若需要在项目中实现类似功能，建议基于 `GeometryProcessing` 和 `MeshModelingToolset` 等更稳定、文档更完善的模块自行构建。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryFlow)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/GeometryFlow) (可能存在)