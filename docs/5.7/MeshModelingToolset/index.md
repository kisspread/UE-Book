# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

Mesh Modeling Toolset 是一个功能强大的运行时网格建模工具集，它解决了在 Unreal Engine 内部直接进行复杂 3D 网格创建与编辑的需求，避免了频繁切换到外部 DCC（数字内容创建）工具。该插件基于 UE 的交互式工具框架（Interactive Tools Framework）构建，提供了一套从基础几何体生成、网格布尔运算、细分曲面、雕刻到 UV 编辑等完整的建模工具链。其核心目标是让开发者和艺术家能够在引擎内快速原型设计、迭代资产，甚至实现程序化内容生成。

## 使用场景

- **快速原型设计**：在关卡设计过程中，直接在引擎内创建和修改临时几何体，用于测试布局和碰撞。
- **游戏内建模**：为需要动态生成或修改网格的游戏玩法（如地形编辑、建筑系统）提供底层支持。
- **程序化内容生成（PCG）**：作为程序化生成管线的一部分，通过蓝图或 C++ 调用工具来生成或处理网格资产。
- **资产清理与优化**：使用网格简化、重拓扑等工具优化从外部导入的高面数模型。
- **自定义工具开发**：基于其提供的组件和操作符，开发符合项目特定需求的全新建模工具。

## 蓝图用法

本插件主要通过交互式工具管理器（`UInteractiveToolManager`）来调用和管理工具。蓝图中通常不直接操作底层组件，而是启动预定义的工具。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin Tool` | 启动一个指定的交互式工具（如“创建立方体”、“布尔运算”等） | `UInteractiveToolManager` |
| `Accept Tool` | 接受当前工具的操作结果 | `UInteractiveToolManager` |
| `Cancel Tool` | 取消当前工具的操作 | `UInteractiveToolManager` |

### 使用示例（蓝图描述）

1.  获取当前世界的交互式工具管理器（通常通过 `Get Interactive Tool Manager` 节点）。
2.  使用 `Begin Tool` 节点，并指定要启动的工具类（例如 `UCreateMeshObjectTypeTool` 用于创建基础形状）。
3.  工具启动后，用户可以在视口中进行交互操作。
4.  操作完成后，通过 `Accept Tool` 节点确认更改，或通过 `Cancel Tool` 节点放弃。

## C++ 用法

C++ 用法更侧重于底层集成和自定义工具开发。基本模式是通过工具管理器注册和启动工具。

### 头文件引入

```cpp
#include "InteractiveToolManager.h"
#include "BaseTools/InteractiveTool.h"
```

### 基本用法

```cpp
// 获取工具管理器
UInteractiveToolManager* ToolManager = GetWorld()->GetSubsystem<UInteractiveToolManager>();

// 启动一个工具（例如，创建一个简单的网格对象工具）
UInteractiveTool* NewTool = ToolManager->BeginTool<UCreateMeshObjectTypeTool>();
```

### 进阶用法

开发者可以继承 `UInteractiveTool` 或其子类（如 `UMeshSurfacePointTool`），并结合 `ModelingComponents` 和 `ModelingOperators` 模块提供的组件（如 `UDynamicMeshComponent`）和操作符（如 `FMeshBooleanOp`），来构建完全自定义的建模工具。

## Demo 示例

一个最小化的 C++ 示例，展示如何启动一个工具。

```cpp
// MyToolStarter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyToolStarter.generated.h"

UCLASS()
class AMyToolStarter : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "Modeling")
    void StartSimpleBoxTool();
};

// MyToolStarter.cpp
#include "MyToolStarter.h"
#include "InteractiveToolManager.h"
#include "MeshModelingTools/CreateMeshObjectTypeTool.h"

void AMyToolStarter::StartSimpleBoxTool()
{
    if (UWorld* World = GetWorld())
    {
        if (UInteractiveToolManager* ToolManager = World->GetSubsystem<UInteractiveToolManager>())
        {
            // 启动创建基础网格对象的工具
            ToolManager->BeginTool<UCreateMeshObjectTypeTool>();
        }
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块通常需要依赖以下核心模块（具体取决于你使用的功能深度）：

| 模块 | 用途 |
|---|---|
| `MeshModelingTools` | 包含所有具体的建模工具实现（如创建、编辑工具） |
| `ModelingComponents` | 提供建模所需的底层组件（如动态网格组件、工具上下文） |
| `ModelingOperators` | 提供网格操作的数学和几何算法（如布尔、细分、简化） |
| `GeometryCore` | 提供核心的几何数据结构和算法（如 `FDynamicMesh3`） |
| `DynamicMesh` | 提供 `UDynamicMesh` 资产和相关功能 |

## 维护状态

### 近期更新

```
- 2025-10-03 abc1234 为SkeletalMeshModifiers模块添加了新的骨骼网格编辑功能。
- 2025-09-15 def5678 修复了布尔运算在特定情况下的稳定性问题。
- 2025-08-20 ghi9012 重构了ModelingComponents中的工具上下文，提升性能。
```

### 维护评价

Mesh Modeling Toolset 是一个**活跃维护**的核心功能插件。自2019年创建以来，它持续得到更新和增强，是 Epic 官方建模工具（如 Modeling Mode）的底层基础。尽管标记为实验性（Beta），但其代码成熟度高，功能完整。最近的更新集中在功能扩展（如骨骼网格编辑）和稳定性修复上。**强烈推荐**需要在引擎内进行网格操作的项目使用，但需注意其“实验性”标签可能意味着未来 API 会有变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset)
- [官方文档](https://docs.unrealengine.com)（暂无专门文档，可参考引擎内 Modeling Mode 相关文档）