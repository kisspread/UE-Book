# Geometry Script

> Geometry Script provides a library of functions for creating and editing Meshes in Blueprints and Python

| 属性 | 值 |
|---|---|
| 中文名 | 几何脚本 |
| 分类 | Geometry |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryScriptingCore` (Runtime), `GeometryScriptingEditor` (Editor) |
| 实验性 | ⚦ 否 |
| 创建时间 | 2024-02-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting) | |

## 用途

`GeometryScript` 是一个运行时几何脚本系统，它将复杂的几何处理算法（如网格布尔运算、简化、重拓扑、UV生成、属性计算等）封装为可在蓝图（Blueprint）和 Python 脚本中直接调用的函数库。其核心目的是通过程序化方式在 Unreal Engine 内部创建和编辑网格资产（`UStaticMesh`, `UDynamicMesh`），从而实现批量处理、工具开发和运行时动态几何生成，替代了大量重复的手动编辑操作。

## 使用场景

- **程序化内容生成 (PCG)**：在游戏中运行时动态生成或修改地形、建筑、物体等网格资产。
- **工具开发**：为编辑器创建自定义的网格处理工具或批处理脚本。
- **资产预处理**：使用 Python 脚本在导入或构建管线中自动执行网格清理、简化、修复拓扑等操作。
- **原型设计与研究**：快速在蓝图中实现并验证几何处理算法，而无需编写 C++ 代码。

## 模块总览

此插件由两个核心模块构成，分别服务于运行时和编辑器环境。

| 模块 | 类型 | 说明 |
|---|---|---|
| [GeometryScriptingCore](./GeometryScriptingCore.md) | Runtime | 核心运行时库，提供 `UDynamicMesh` 和 `UGeometryScriptLibrary_*` 类，包含所有可在蓝图和 Python 中调用的几何处理函数。 |
| [GeometryScriptingEditor](./GeometryScriptingEditor.md) | Editor | 编辑器扩展模块，提供用于资产处理（如烘焙纹理）的编辑器专用工具和命令。 |

## 蓝图核心概念（概述）

> 详细 API 列表请参阅 [GeometryScriptingCore](./GeometryScriptingCore.md) 文档。

在蓝图中使用 `GeometryScript` 的核心工作流围绕以下类展开：

1.  **`UDynamicMesh`**：可动态编辑的网格对象。通常通过“创建动态网格”节点从 `UStaticMesh` 创建，或在蓝图中新建。
2.  **`UGeometryScriptLibrary_*`**：一系列静态函数库，例如 `MeshBoolean`, `Remesh`, `SimplifyMesh` 等。所有函数都接受并返回 `UDynamicMesh` 对象，支持链式调用。
3.  **`UStaticMesh`**：最终的目标资产。处理完成后，使用“将动态网格转为静态网格”节点将其固化。

**典型蓝图流程**：
“创建动态网格” -> 一系列 `GeometryScript` 函数处理 -> “将动态网格转为静态网格”。

## C++ 核心概念（概述）

> 详细用法请参阅 [GeometryScriptingCore](./GeometryScriptingCore.md) 文档。

在 C++ 中，主要通过 `FDynamicMesh3` 和相关的 `FGeometryScript*` 函数（位于 `GeometryScriptingCore` 模块）进行操作。

```cpp
// 核心头文件
#include "GeometryScript/GeometryScriptTypes.h"
#include "GeometryScript/GeometryScriptMeshAssetFunctions.h"
#include "GeometryScript/GeometryScriptMeshQueryFunctions.h"

// 示例：从StaticMesh创建动态网格并获取信息
UDynamicMesh* DynamicMesh = NewObject<UDynamicMesh>();
FGeometryScriptMeshReadOptions ReadOptions;
UGeometryScriptLibrary_MeshAssetFunctions::CreateDynamicMeshFromStaticMesh(
    SomeStaticMesh, ReadOptions, DynamicMesh, EGeometryScriptOutcomePins::Success);

int32 NumVertices, NumTriangles;
UGeometryScriptLibrary_MeshQueryFunctions::GetMeshInfo(DynamicMesh, NumVertices, NumTriangles);
```

## 模块依赖

要在你的项目或插件中使用 `GeometryScript`，需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 提供底层的 `FDynamicMesh3` 数据结构和基础几何操作。 |
| `GeometryFramework` | 提供 `UDynamicMesh` 资产和相关的 Actor/Component。 |
| `MeshModelingToolset` | 编辑器模块依赖，用于与建模工具交互和纹理烘焙等高级功能。 |
| `UnrealEd` | 编辑器模块依赖，用于资产工厂和编辑器工具集成。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `5925f0e4` | GeometryScript: Add validation for DynamicMesh overlay triangle storage coverage to BakeTexture. | 为纹理烘焙功能添加了对动态网格覆盖层三角形存储覆盖范围的验证。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数会产生警告的代码。 |
| 2026-05-12 | `6a996b5e` | [Geometry] Fixed auto generated poly group sometimes does not generate subd compatible groups | [几何] 修复了自动生成多边形组有时不生成细分曲面兼容组的问题。 |
| 2026-04-23 | `9f503464` | Optional rebalance geometry/attribute weight in simplifier | 在网格简化器中增加了可选的几何与属性权重再平衡选项。 |
| 2026-04-15 | `8b93226f` | Add editor-only dynamic mesh processor class, so dataflow geometry script users can access the edito | 添加了仅编辑器的动态网格处理器类，以便数据流几何脚本用户可以访问编辑器功能。 |

### 维护评价

`GeometryScript` 是一个 **活跃维护** 的插件。它自 2024 年初创建以来，持续有功能更新、Bug 修复和性能优化。从最近的提交历史可以看出，更新非常频繁，涵盖了核心功能增强（如简化器权重平衡）、特定工作流改进（如纹理烘焙验证）以及底层代码的健壮性修复。作为 Epic 官方主推的程序化网格处理解决方案，其长期维护和支持有较高保障。**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/GeometryScripting)