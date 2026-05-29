# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

该插件提供了一套基于 Unreal Engine 交互工具框架（Interactive Tools Framework）的**运行时3D网格创建与编辑工具集**。它旨在编辑器和可能的运行时环境中，为用户提供直接操作和修改静态网格体（Static Mesh）或骨骼网格体（Skeletal Mesh）几何形状的能力。其核心功能包括多边形建模、网格体雕刻、UV展开/编辑、网格体布尔运算以及骨骼网格体的权重与拓扑修改，是进行程序化资产生成或精细手动编辑的关键工具套件。

## 使用场景

- **原型快速搭建**：在编辑器中快速创建基础几何体（如立方体、球体、圆柱）并立即进行切割、挤出、倒角等操作，用于关卡设计或资产原型。
- **资产后处理**：在导入外部模型后，直接在UE编辑器中修复拓扑、调整UV、或通过网格体简化/平滑等操作优化其性能。
- **程序化内容生成**：在运行时或编辑器脚本中，通过C++ API动态创建和修改网格体几何形状，实现地形生成、破坏效果等。
- **角色资产编辑**：使用 `SkeletalMeshModifiers` 模块，在编辑器内修改骨骼网格体的顶点、面或UV，或进行蒙皮权重绘制。

## 蓝图用法

*（注：此插件主要为编辑器扩展工具，蓝图可调用函数多为工具管理或底层操作）*

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnBox`, `SpawnSphere` 等 | 在场景中生成基础几何体 | `UMeshModelingSubsystem` |
| `Remesh`, `Smooth`, `ProjectToTarget` | 对目标网格体执行高级操作（重拓扑、平滑、投射） | `UMeshModelingSubsystem` |
| `AcceptActiveTool`, `CancelActiveTool` | 接受或取消当前活动的交互式建模工具 | `UInteractiveToolsSubsystem` |

### 使用示例（蓝图描述）
1.  **生成几何体**：调用 `UMeshModelingSubsystem` 的 `SpawnBox` 节点，在指定位置生成一个立方体 `AStaticMeshActor`。
2.  **启动工具**：使用 `UInteractiveToolsSubsystem` 的 `RegisterTool` 和 `StartTool` 方法，启动如“网格体布尔”等交互工具，并传入操作目标和参数。
3.  **执行程序化操作**：直接调用 `UMeshModelingSubsystem` 的 `Remesh` 或 `Smooth` 函数，并传入 `UStaticMesh` 引用及操作参数，对网格体进行非交互式修改。

## C++ 用法

### 头文件引入

```cpp
#include "ModelingSubsystem.h" // 核心建模子系统
#include "ModelingToolsSubsystem.h" // 工具管理子系统
#include "DynamicMesh/MeshTransforms.h" // 动态网格体操作
```

### 基本用法（工具管理与操作符执行）

*来源：模块文档 ModelingTools.md， ModelingOperators.md*

```cpp
// 获取建模工具子系统
UModelingToolsSubsystem* ModelingSubsystem = GEditor->GetEditorSubsystem<UModelingToolsSubsystem>();

// 创建并配置一个工具操作上下文（用于非交互式操作）
FMeshTransforms::ApplyTransform(DynamicMesh, FTransform(FRotator(0, 45, 0)));

// 通过操作符（Operators）执行具体的几何操作（如布尔运算）
// 注：具体操作符的使用需要查阅对应模块文档，如 FSelfUnionOp, FMeshBooleanOp
```

### 进阶用法（自定义工具与组件）

*来源：模块文档 ModelingComponents.md， MeshModelingTools.md*

```cpp
// 使用交互工具框架创建自定义工具
UMyCustomModelingTool* NewTool = NewObject<UMyCustomModelingTool>(GetTransientPackage(), NAME_None);
if (NewTool)
{
    NewTool->SetWorld(MyWorld);
    // 配置工具属性...
    // 将工具注册并启动
    UInteractiveToolManager* ToolManager = GEditor->GetToolManager();
    ToolManager->RegisterTool(NewTool);
    ToolManager->StartTool(NewTool->GetIdentifier());
}
```

## Demo 示例

*（此插件为大型工具集，完整示例通常在引擎编辑器测试中，此处展示一个基本的程序化网格体操作概念）*

```cpp
// MyMeshGenerator.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyMeshGenerator.generated.h"

UCLASS()
class UMyMeshGenerator : public UEditorSubsystem
{
    GENERATED_BODY()
public:
    // 在编辑器中生成一个简单的程序化网格体
    UFUNCTION(BlueprintCallable, Category = "Demo")
    AStaticMeshActor* GenerateSimpleProceduralMesh(UWorld* World, FVector Location);
};

// MyMeshGenerator.cpp
#include "MyMeshGenerator.h"
#include "ModelingSubsystem.h"
#include "Engine/StaticMeshActor.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/MeshNormals.h"

AStaticMeshActor* UMyMeshGenerator::GenerateSimpleProceduralMesh(UWorld* World, FVector Location)
{
    if (!World) return nullptr;

    // 1. 使用建模子系统生成一个基础的动态网格体（例如一个圆柱体的骨架）
    UModelingSubsystem* Subsystem = GEditor->GetEditorSubsystem<UModelingSubsystem>();
    UE::Geometry::FDynamicMesh3 DynamicMesh;
    // ... 填充DynamicMesh的顶点和三角形数据（此处省略几何构建代码） ...

    // 2. 计算法线
    UE::Geometry::FMeshNormals::QuickComputeNormals(DynamicMesh);

    // 3. 将动态网格体转换为静态网格体资产并生成Actor
    // （此步骤涉及资产创建，通常通过子系统或引擎API完成，此处为概念示意）
    // return Subsystem->CreateStaticMeshFromDynamicMesh(DynamicMesh, World, Location);
    return nullptr; // 示例占位
}
```

## 模块依赖

从构建脚本分析，要使用此插件的功能，你的模块通常需要依赖以下**特有模块**：

| 模块 | 用途 |
|---|---|
| `ModelingTools` | 提供具体的建模工具实现（如网格体编辑工具） |
| `ModelingComponents` | 提供建模过程中所需的UI组件和交互逻辑 |
| `ModelingOperators` | 实现底层的几何操作算法（如布尔、简化、平滑） |
| `GeometryCore` | 提供核心几何数据结构（如 `FDynamicMesh3`） |
| `DynamicMesh` | 动态网格体的运行时表示与操作 |
| `MeshModel` | 网格体模型的特定数据结构和操作 |
| `ToolCore` | 交互工具框架的核心接口和基类 |
| `InteractiveToolsFramework` | 构建交互式工具（如移动、旋转小部件）的底层框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `2cd4fab7` | SReferenceSkeletonTree: preserve selection across RefreshTreeView so unrelated | 骨骼树UI：刷新时保持选择状态 |
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 顶点属性和蒙皮权重绘制工具：新增同步笔刷半径选项 |
| 2026-05-26 | `1b791587` | [SkeletalMeshModelingTools] Edit Skeleton tool: route deleted-bone weights to root instead of droppi | 编辑骨骼工具：删除骨骼权重转移到根而非丢弃 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 顶点属性绘制工具：重构笔画累加器支持松弛笔刷 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 几何选择：仅编辑顶点时跳过组拓扑重建 |

### 维护评价

- **创建时间**：约 4 年（2021年7月）。
- **近期更新**：非常活跃，最近一次更新在**2026年5月27日**，集中在工具增强、骨骼权重处理、UI选择和顶点绘制功能的优化。
- **维护状态**：**活跃维护**。作为引擎核心编辑器和潜在运行时工具的一部分，由 Epic Games 持续开发和改进。
- **已知限制**：插件标记为 `IsBetaVersion: true` 且 `Hidden: true`，意味着 API 可能不稳定，且默认不启用。需要手动在插件列表中启用。
- **推荐使用**：**推荐**。对于需要在编辑器或运行时进行程序化网格体生成和编辑的项目，这是一个功能强大且持续维护的工具集。但请注意其实验性状态，建议在稳定版本引擎中进行充分测试，并关注未来API可能的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Editor/MeshModelingToolset)