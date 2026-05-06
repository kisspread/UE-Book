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
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow) | |

## 用途

**GeometryFlow** 是 UE5 中一个基于节点图的**几何处理框架**。它允许将网格操作（如简化、法线/切线与 UV 计算、烘焙、体素形态、碰撞几何生成等）以**数据流图（DataFlow Graph）** 的形式组合、连接并顺序执行，以替代传统的逐步骤编程流程。

该插件将每个处理步骤抽象为一个 **Node**，Node 间通过命名端口交换强类型数据（`FDynamicMesh3`、`FImage`、`FCollisionGeometry` 等）。核心模块 `GeometryFlowCore` 提供图执行引擎和节点基类，而本模块 `GeometryFlowMeshProcessing` 则实现了一系列具体的网格处理节点，覆盖了从输入、变换、简化到烘焙的完整管线。

> **设计目标**：解决复杂网格处理流程难以维护、重用和可视化的问题。通过数据流图，可以轻松构建、调试和复用网格处理管道。

---

## 使用场景

- **批量处理静态网格体**（如 LOD 生成）：将多个 Simplification、Normal/UV 计算、Tangent 计算节点串联。
- **纹理烘焙管道**：从高模到低模的 Normal Map、Texture、Multi‑Texture 烘焙，使用 `FMakeMeshBakingCacheNode` → `FBakeMeshNormalMapNode` / `FBakeMeshTextureImageNode` 等。
- **碰撞体自动生成**：使用 `FGenerateSimpleCollisionNode` 输出 `FCollisionGeometry`（盒体、球体、凸包等）。
- **网格修复与清理**：使用 `FMeshMakeCleanGeometryNode` 补洞、清除属性；使用 `FCompactMeshNode` 压缩索引。
- **基于连接组件的网格分解**：使用 `FMakeTriangleSetsFromMeshNode` 或 `FMakeTriangleSetsFromGroupsNode` 将网格分割为子集。

---

## 蓝图用法

本模块 **不直接暴露 BlueprintCallable 函数**。所有节点均为 C++ 类，通过 `GeometryFlowCore` 的图执行引擎工作。但以下 USTRUCT 可以在蓝图编辑器中用于配置节点参数（例如通过 `UProperty` 暴露给细节面板）：

| 结构体 | 说明 | 关联节点 |
|---|---|---|
| `FMeshMakeBakingCacheSettings` | 烘焙缓存（尺寸、UV层、厚度） | `FMakeMeshBakingCacheNode` |
| `FBakeMeshNormalMapSettings` | 法线图烘焙（最大采样距离） | `FBakeMeshNormalMapNode` |
| `FBakeMeshTextureImageSettings` | 纹理烘焙（UV层、最大距离） | `FBakeMeshTextureImageNode` |
| `FBakeMeshMultiTextureSettings` | 多纹理烘焙（继承自单纹理） | `FBakeMeshMultiTextureNode` |
| `FMeshSimplifySettings` | 网格简化（类型、目标、容差等） | `FMeshSimplifyNode` |
| `FMeshNormalsSettings` | 法线计算模式 | `FComputeMeshNormalsNode` |
| `FMeshTangentsSettings` | 切线计算模式 | `FComputeMeshTangentsNode` |
| `FMeshSolidifySettings` | 体素固体化参数 | `FSolidifyMeshNode` |
| `FVoxMorphologyOpSettings` | 体素形态学操作 | `TVoxMorphologyMeshNode` |
| `FMeshRecalculateUVsSettings` | UV 重算（展开类型、层） | `FMeshRecalculateUVsNode` |
| `FMeshRepackUVsSettings` | UV 重新打包（分辨率、间距等） | `FMeshRepackUVsNode` |
| `FGenerateSimpleCollisionSettings` | 简单碰撞体类型与参数 | `FGenerateSimpleCollisionNode` |

这些结构体通过在 `USTRUCT()` 中添加 `UPROPERTY(EditAnywhere, Category=...)` 暴露给编辑器，可在蓝图或 C++ 中构造并传入节点。

---

## C++ 用法

### 头文件引入

```cpp
#include "GeometryFlowMeshProcessingModule.h"          // 模块声明
#include "MeshProcessingNodes/MeshSimplifyNode.h"       // 简化节点
#include "MeshProcessingNodes/MeshNormalsNodes.h"       // 法线节点
#include "DataTypes/DynamicMeshData.h"                  // 网格数据类型
#include "GeometryFlowCoreNodes.h"                      // 核心节点基类
#include "GeometryFlowNodeUtil.h"                       // 节点工具
```

### 基本用法

以下示例演示如何创建一个简化节点、设置输入网格并获取结果（来源：`Engine/Plugins/Experimental/GeometryFlow/Source/GeometryFlowMeshProcessing/Private/` 中的单元测试启发）。

```cpp
// 1. 创建节点实例
TUniquePtr<UE::GeometryFlow::FMeshSimplifyNode> SimplifyNode = MakeUnique<UE::GeometryFlow::FMeshSimplifyNode>();

// 2. 生成输入网格数据（例如一个球体）
FDynamicMesh3 SourceMesh;
// ... 填充 SourceMesh 顶部 ...

// 3. 包装为节点输入
TSafeSharedPtr<UE::GeometryFlow::FDataDynamicMesh> MeshInput = MakeSafeShared<UE::GeometryFlow::FDataDynamicMesh>();
MeshInput->SetData(SourceMesh);

// 4. 创建设置数据（例如简化到 50% 三角形）
UE::GeometryFlow::FMeshSimplifySettings Settings;
Settings.SimplifyType = UE::GeometryFlow::EGeometryFlow_MeshSimplifyType::AttributeAware;
Settings.TargetType = UE::GeometryFlow::EGeomtryFlow_MeshSimplifyTargetType::TrianglePercentage;
Settings.TargetFraction = 0.5f;

TSafeSharedPtr<UE::GeometryFlow::FDataSimplifySettings> SettingsData = MakeSafeShared<UE::GeometryFlow::FDataSimplifySettings>();
SettingsData->SetData(Settings);

// 5. 组装输入 Map
UE::GeometryFlow::FNamedDataMap Inputs;
Inputs.SetData(FMeshSimplifyNode::InParamMesh(), MeshInput);
Inputs.SetData(FMeshSimplifyNode::InParamSettings(), SettingsData);

// 6. 执行 Evaluate
UE::GeometryFlow::FNamedDataMap Outputs;
TUniquePtr<UE::GeometryFlow::FEvaluationInfo> EvalInfo = MakeUnique<UE::GeometryFlow::FEvaluationInfo>();
SimplifyNode->Evaluate(Inputs, Outputs, EvalInfo);

// 7. 获取结果
TSafeSharedPtr<UE::GeometryFlow::FDataDynamicMesh> ResultMesh = Outputs.FindDataChecked(FMeshSimplifyNode::OutParamResultMesh()).AsShared();
const FDynamicMesh3& SimplifiedMesh = ResultMesh->GetDataConstRef<FDynamicMesh3>((int)UE::GeometryFlow::EMeshProcessingDataTypes::DynamicMesh);
```

### 进阶用法：构建烘焙管线

将多个节点串联为一个图：

```cpp
using namespace UE::GeometryFlow;

// 1. 创建节点
TUniquePtr<FMakeMeshBakingCacheNode> CacheNode = MakeUnique<FMakeMeshBakingCacheNode>();
TUniquePtr<FBakeMeshNormalMapNode> NormalNode = MakeUnique<FBakeMeshNormalMapNode>();

// 2. 准备数据（略）
// ...

// 3. 连接节点（手动传递输出到输入的输入 Map）
// 先执行 CacheNode
CacheNode->Evaluate(CacheInputs, CacheOutputs, EvalInfo);
TSafeSharedPtr<FMeshBakingCacheData> BakeCache = CacheOutputs.FindDataChecked(FMakeMeshBakingCacheNode::OutParamCache()).AsShared();

// 再执行 NormalNode
FNamedDataMap NormalInputs;
NormalInputs.SetData(FBakeMeshNormalMapNode::InParamBakeCache(), BakeCache);
NormalInputs.SetData(FBakeMeshNormalMapNode::InParamTangents(), TangentsInput);
NormalInputs.SetData(FBakeMeshNormalMapNode::InParamSettings(), NormalSettings);
NormalNode->Evaluate(NormalInputs, NormalOutputs, EvalInfo);
TSafeSharedPtr<FDataNormalMapImage> NormalMap = NormalOutputs.FindDataChecked(FBakeMeshNormalMapNode::OutParamNormalMap()).AsShared();
```

---

## Demo 示例

以下完整示例展示如何创建一个 `FMeshSimplifyNode` 并获取简化结果（仅核心逻辑，需依赖 `GeometryFlowCore` 和网格数据源）。

### Source/MyGeomFlowDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GeometryFlowCoreNodes.h"
#include "MeshProcessingNodes/MeshSimplifyNode.h"
#include "MeshProcessingNodes/MeshProcessingBaseNodes.h"
#include "DataTypes/DynamicMeshData.h"

class FMyGeomFlowDemo
{
public:
    static bool RunSimplificationExample();
};
```

### Source/MyGeomFlowDemo.cpp

```cpp
#include "MyGeomFlowDemo.h"
#include "GeometryCore/Public/DynamicMesh/DynamicMesh3.h"
#include "GeometryCore/Public/Generators/GridBoxMeshGenerator.h"

bool FMyGeomFlowDemo::RunSimplificationExample()
{
    using namespace UE::GeometryFlow;

    // 1. 创建一个简单网格（单位立方体）
    UE::Geometry::FGridBoxMeshGenerator BoxGen;
    BoxGen.Box = UE::Geometry::FOrientedBox3d(UE::Geometry::FVector3d::Zero(), 100.0f);
    UE::Geometry::FDynamicMesh3 BoxMesh(&BoxGen.Generate());

    TSafeSharedPtr<FDataDynamicMesh> MeshInput = MakeSafeShared<FDataDynamicMesh>();
    MeshInput->SetData(BoxMesh);

    // 2. 设置简化参数（保留 10% 三角形）
    FMeshSimplifySettings Settings;
    Settings.TargetType = EGeomtryFlow_MeshSimplifyTargetType::TrianglePercentage;
    Settings.TargetFraction = 0.1f;

    TSafeSharedPtr<FDataSimplifySettings> SettingsData = MakeSafeShared<FDataSimplifySettings>();
    SettingsData->SetData(Settings);

    // 3. 创建节点并配置
    FMeshSimplifyNode Node;
    FNamedDataMap Inputs, Outputs;
    Inputs.SetData(FMeshSimplifyNode::InParamMesh(), MeshInput);
    Inputs.SetData(FMeshSimplifyNode::InParamSettings(), SettingsData);

    // 4. 执行
    TUniquePtr<FEvaluationInfo> EvalInfo = MakeUnique<FEvaluationInfo>();
    Node.Evaluate(Inputs, Outputs, EvalInfo);

    // 5. 检查输出
    if (Outputs.Contains(FMeshSimplifyNode::OutParamResultMesh()))
    {
        const FDynamicMesh3& Result = Outputs.FindDataChecked(FMeshSimplifyNode::OutParamResultMesh())
            ->GetDataConstRef<FDynamicMesh3>((int)EMeshProcessingDataTypes::DynamicMesh);

        UE_LOG(LogTemp, Display, TEXT("Simplify finished: %d triangles -> %d triangles"), BoxMesh.TriangleCount(), Result.TriangleCount());
        return true;
    }
    UE_LOG(LogTemp, Error, TEXT("Simplify failed!"));
    return false;
}
```

---

## 模块依赖

### 本模块（GeometryFlowMeshProcessing）依赖

| 模块 | 用途 |
|---|---|
| `GeometryFlowCore` | 数据流图核心：节点基类、数据类型、图执行引擎 |
| `GeometryProcessing` | 几何处理算法（简化、法线、UV 展开等），由 UE 官方 GeometryProcessing 插件提供 |
| `MeshModelingToolsetExp` | 实验性网格建模工具集，提供碰撞体生成、烘焙等算法 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, EditorStyle, PropertyEditor, Projects, DeveloperSettings（均为标准或常见依赖，无需列出）。

### 使用本模块时，你的模块需在 `Build.cs` 中添加

```csharp
PublicDependencyModuleNames.Add("GeometryFlowMeshProcessing");
// 如需使用编辑器节点注册，还需 GeometryFlowMeshProcessingEditor
// 通常需同时添加以下运行时依赖
PublicDependencyModuleNames.Add("GeometryProcessing");
PublicDependencyModuleNames.Add("GeometryFlowCore");
```

---

## 维护状态

### 近期更新

| 日期 | Commit Hash | 说明 |
|---|---|---|
| 2025-07-10 | `9803c443` | 为包含 .gen.cpp 文件的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME |
| 2025-05-31 | `52e3dac1` | 使用 UnrealCodeFixup 更新头文件以将 DLL 存储放在方法/静态变量而非类型上 |
| 2024-12-16 | `dbb51bc5` | GeometryFlow: 清理节点注册 |
| 2024-12-13 | `1d69cf7b` | 几何处理单元测试：消除警告，为启用测试做准备 |
| 2024-11-10 | `66e9bb39` | 移除所有 #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 作用域 |

### 维护评价

- **创建时间**：2024‑11‑10（约 8 个月前），属于较新的插件。
- **最近更新**：2025‑07‑10 尚有编译修复提交，2025‑05‑31 有头文件清理更新。总体活跃度中等，但近期无功能性新增。
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion=true`，表示 API 和功能可能不稳定，未来可能大改。
- **推荐使用**：适合需要构建自定义几何处理管线的开发者。由于处于实验阶段，建议在非核心生产项目中使用，并配合良好的单元测试覆盖。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow)
- [官方文档](https://docs.unrealengine.com)（未提供独立文档页，可参考 UE5 几何处理相关文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/GeometryFlow/Source/GeometryFlowMeshProcessing/Private/)（位于 `Private/` 目录下的单元测试文件）