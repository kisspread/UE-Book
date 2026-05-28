# Dataprep Geometry Operations

> Experimental geometry processing operations usable in the Dataprep Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Dataprep 几何操作 |
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataprepGeometryOperations` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Enterprise/DataprepGeometryOperations) | |

## 用途

`DataprepGeometryOperations` 插件为 Unreal Engine 的 **Dataprep 编辑器** 提供了一套实验性的几何网格处理操作（Operations）。它的核心目的是在数据准备（Data Preparation）流水线中，自动化执行对导入的 3D 网格资产（如 CAD 模型、扫描数据）进行优化和清理的几何操作。

它解决的主要问题包括：
1.  **网格优化**：通过重网格化（Remesh）和简化（Simplify）减少模型的三角形数量，以提升运行时性能。
2.  **数据清理**：焊接（Weld）共边、烘焙（Bake）变换，以修复模型导入过程中产生的旋转、缩放和轴心点问题。
3.  **几何分割**：使用平面切割（Plane Cut）功能，可以按几何条件分割模型。

该插件使得这些复杂的几何处理过程能够作为节点集成到可视化的 Dataprep 图表中，无需编写代码即可对成批资产进行处理。

## 使用场景

-   你正在为数字孪生或建筑可视化项目导入高精度的 CAD/BIM 模型，这些模型三角形面数过高，需要批量优化。→ 使用 **Remesh** 或 **Simplify** 操作。
-   你从其他 DCC 软件（如 Maya, Blender）导入的模型带有旋转、非均匀缩放，或者轴心点不在正确位置。→ 使用 **Bake Transform** 操作。
-   模型中存在未合并的共边顶点，导致出现视觉接缝或影响光照。→ 使用 **Weld Edges** 操作。
-   你需要将一个整体模型按特定平面拆分成多个独立部件。→ 使用 **Plane Cut** 操作。
-   你需要筛选出场景中被其他物体完全遮挡、不可见的静态网格体演员（Actor）。→ 使用 **Jacketing Filter**。

## 蓝图用法

此插件主要通过 **Dataprep 编辑器** 使用，其核心操作（Operation）作为节点添加到 Dataprep 图表中。在蓝图中，主要接触的是这些操作的**属性配置**。

### 核心操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remesh` | 对输入网格进行重网格化，可指定目标三角形数、平滑强度等。 | `UDataprepRemeshOperation` |
| `Bake Transform` | 将物体的旋转和/或缩放烘焙到网格数据中，并可选重置轴心点。 | `UDataprepBakeTransformOperation` |
| `Weld Edges` | 根据容差值合并（焊接）网格中距离过近的边。 | `UDataprepWeldEdgesOperation` |
| `Simplify Mesh` | 根据百分比减少网格的三角形数量。 | `UDataprepSimplifyMeshOperation` |
| `Plane Cut` | 使用一个平面切割网格，可选择保留正侧、负侧或两侧。 | `UDataprepPlaneCutOperation` |
| `Jacketing` (Filter) | 一个过滤器，用于筛选出被其他网格体遮挡的物体。 | `UDataprepJacketingFilter` |
| `Select In Volume` (Selection Transform) | 一个选择转换器，选择与当前选中物体相交或在其内部的所有物体。 | `UDataprepOverlappingActorsSelectionTransform` |

### 使用示例（蓝图描述）

在 **Dataprep 编辑器** 中，你可以这样构建一个处理流程：

1.  **输入**：从内容浏览器拖入一个或多个包含静态网格体资产的 Actor 蓝图。
2.  **添加操作**：在图表的 `Main Graph` 节点上右键，选择 `Add Operation` -> `Mesh Operation` -> `Remesh`。
3.  **配置参数**：在右侧细节面板中，设置 `TargetTriangleCount` 为 1000，`SmoothingStrength` 为 0.5。
4.  **连接**：将 `Main Graph` 节点的输出执行引脚连接到 `Remesh` 节点的输入执行引脚。
5.  **输出**：运行图表，经过重网格化处理后的模型将输出到指定位置。
6.  **进阶**：你可以串联多个操作，例如先 `Bake Transform`，再 `Remesh`，最后 `Weld Edges`，形成一个完整的模型优化流水线。

## C++ 用法

此插件主要服务于 Dataprep 编辑器，其操作类通常在编辑器上下文中被实例化和调用。如果你需要编写与几何处理相关的 C++ 代码，可以借鉴其内部使用的工具类，如 `FJacketingProcess`。

### 头文件引入

```cpp
// 如果使用 Jacketing 功能
#include “JacketingProcess.h”
```

### 基本用法

以下是使用 `FJacketingProcess` 来查找被遮挡 Actor 的示例，借鉴自其静态方法接口。

```cpp
#include “JacketingProcess.h”

// 假设你有一组待检测的Actor和一组构成遮挡物的Actor
TArray<AActor*> ActorsToTest; // 待检测是否可见的Actor
TArray<AActor*> OccluderActors; // 可能造成遮挡的Actor

// 配置 Jacketing 选项
FJacketingOptions Options;
Options.Accuracy = 3.0f; // 体素精度，单位：厘米
Options.MergeDistance = 4.0f; // 用于填补缝隙的距离
Options.Target = EJacketingTarget::Level; // 应用于关卡中的Actor

// 存放被判定为遮挡（不可见）的Actor
TArray<AActor*> OccludedActors;

// 执行遮挡剔除计算（bSilent设为true以禁用进度对话框）
FJacketingProcess::ApplyJacketingOnMeshActors(ActorsToTest, &Options, OccludedActors, true);

// OccludedActors 现在包含了被完全遮挡的Actor引用
// 你可以选择隐藏、标记或删除它们
```

### 进阶用法

此插件定义的操作类（如 `UDataprepRemeshOperation`）继承自 `UDataprepEditingOperation`。理论上，你可以继承它们来创建自定义的几何操作，但这需要深入理解 Dataprep 框架的执行流程。

```cpp
#include “DataprepCore/Public/DataprepEditingOperation.h”

UCLASS()
class UMyCustomGeometryOperation : public UDataprepEditingOperation
{
    GENERATED_BODY()

public:
    // 定义你的操作参数
    UPROPERTY(EditAnywhere, Category = “MyOptions”)
    float SomeParameter = 1.0f;

protected:
    // 实现核心操作逻辑
    virtual void OnExecution_Implementation(const FDataprepContext& InContext) override
    {
        // 获取输入的物体（通常是 UStaticMeshComponent 或其所有者Actor）
        TArray<UObject*> Objects = InContext.GetObjects();

        // 在这里编写你的几何处理代码
        // 通常需要使用 UE::Geometry 或 MeshDescription 库
        // ...
    }
};
```

## Demo 示例

由于此插件的核心功能集成于 Dataprep 编辑器 UI 中，没有独立的 C++ Demo。一个最小的自定义操作示例如上所示。

一个可行的“Demo”是创建一个 **Dataprep 预设**：

1.  在编辑器中打开 `Dataprep Editor`。
2.  创建一个新资产，命名为 `SM_OptimizationPreset`。
3.  在图表中按顺序添加以下操作节点：
    -   `Bake Transform`：勾选 `bBakeRotation` 和 `bRecenterPivot`。
    -   `Simplify Mesh`：设置 `TargetPercentage` 为 50。
    -   `Weld Edges`：设置 `Tolerance` 为 0.001。
4.  保存该预设。
5.  在内容浏览器中，右键任意一个静态网格体资产，选择 `Dataprep` -> `Apply Preset` -> `SM_OptimizationPreset`，即可一键执行该优化流程。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 提供核心几何数据结构，如 `FDynamicMesh3`。 |
| `GeometryProcessing` | 提供高级的几何处理算法，如重网格化、简化、布尔运算等。 |
| `DataprepCore` | Dataprep 框架的核心模块，定义了操作（Operation）、过滤器（Filter）等基类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到更现代的 UE_LOGF。 |
| 2026-02-06 | `a18acbc2` | update another usage of FDynamicMeshEditor::SplitMesh to use the TUniquePtr version; MeshPartitionRe | 更新 `SplitMesh` 用法至新版本；涉及网格分区相关改动。 |
| 2024-12-20 | `d0cf4301` | ModelingTools: Promote experimental modeling tools to beta. | 建模工具：将实验性建模工具提升至 Beta 阶段。 |
| 2024-12-19 | `0b7db795` | [Backout] - CL38936187 | [回退] - 回退了提交 CL38936187。 |
| 2024-12-19 | `4581f566` | ModelingTools: Promote experimental modeling tools to beta. | 建模工具：将实验性建模工具提升至 Beta 阶段（可能为之前回退的重新提交）。 |

### 维护评价

-   **创建时间**：插件创建于 2020 年，已有约 6 年历史。
-   **维护状态**：**活跃维护**。最近的提交（2026年）表明 Epic 仍在更新其依赖的底层库（如 `FDynamicMeshEditor`）和进行代码现代化（UE_LOGF）。2024年底有将其依赖的建模工具标记为 Beta 的提交。
-   **实验性与风险**：该插件在 `.uplugin` 中明确标记为 **Experimental** 且 `IsBetaVersion=true`，且默认不启用。这意味着其 API、功能和用法可能在未来的引擎版本中发生变化，不建议用于需要长期稳定性的生产核心项目。
-   **推荐**：对于探索性项目、内部工具或对模型优化有明确需求的数字孪生/建筑可视化项目，在了解其风险的前提下可以使用。使用前建议备份资产。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Enterprise/DataprepGeometryOperations)
-   官方文档：无
-   测试用例：无（在提供的文件列表中未发现测试代码）