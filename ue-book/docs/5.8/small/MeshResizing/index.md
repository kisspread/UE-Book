# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

这是一个用于编辑器中进行网格资产缩放变换的工具插件。它旨在为用户提供一种交互式、可控的方式，在运行时或编辑器上下文中调整网格体（Static Mesh）的大小，同时可能保持或智能处理网格的拓扑结构、UV 映射和材质属性。这解决了传统等比/非等比缩放变换可能破坏网格细节或引入视觉瑕疵的问题，适用于需要对模型进行非破坏性尺寸调整的工作流。

## 使用场景

- 你在进行关卡设计时，需要快速、非破坏性地调整一个或多个预制道具（如家具、装饰物）的比例，以适应不同的场景布局。
- 你需要批量处理一批角色装备或环境资产，使其尺寸在不同装备组合或关卡中保持一致。
- 你正在使用 Dataflow（数据流）节点式工作流进行程序化内容生成（PCG）或网格操作，并希望将网格缩放作为其中一个可调节的环节。

## 蓝图用法

此插件的编辑器工具和数据流节点主要在编辑器和 Dataflow 图表中使用。具体的蓝图节点需参考 `MeshResizingEditorTools` 和 `MeshResizingDataflowNodes` 模块的文档。核心功能预计包括应用缩放变换、预览结果、以及配置缩放约束的节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| (待从模块文档补充) | | |

### 使用示例（蓝图描述）

由于此插件的交互主要在编辑器视口和 Dataflow 图表中，典型的使用方式是：在 Content Browser 中选择网格资产，通过右键菜单或编辑器工具栏激活“网格缩放”工具；或者在 Dataflow 图表中拖入缩放相关节点，将其连接到网格输入节点，并通过属性面板调整缩放参数。

## C++ 用法

### 头文件引入

```cpp
#include “MeshResizingCore.h”
// 或其他具体模块头文件，如
// #include “MeshResizingEngine.h”
```

### 基本用法

此插件的核心逻辑封装在运行时模块中，但用户接口主要面向编辑器。在 C++ 中，通常通过访问 `MeshResizingEngine` 或 `MeshResizingCore` 提供的服务或子系统来执行缩放操作。以下为概念性示例：

```cpp
// 获取网格缩放子系统（假设存在）
// UM* MeshResizingSubsystem = GEngine->GetEngineSubsystem<UMeshResizingSubsystem>();
// if (MeshResizingSubsystem)
// {
//     // 配置缩放参数
//     FMeshResizeParams Params;
//     Params.ScaleFactor = FVector(1.5f, 1.0f, 1.5f); // 非均匀缩放
//     Params.bPreserveUVs = true;
//
//     // 对目标网格资产应用缩放
//     UStaticMesh* TargetMesh = /*...*/;
//     MeshResizingSubsystem->ResizeMesh(TargetMesh, Params);
// }
```

### 进阶用法

结合 `MeshResizingDataflowNodes` 模块，可以在自定义的 Dataflow 节点或工具中实现复杂的、可定制的网格缩放逻辑。

## Demo 示例

由于此插件处于早期实验阶段且提供编辑器工具，一个最小可运行示例是启用插件后，在编辑器中通过其提供的 UI 进行操作。在 C++ 中调用其核心功能的最小示例需要依赖于具体的模块 API 设计，当前文档不足以提供完整编译代码。建议通过 `Content Examples` 项目或插件自身的测试用例来学习用法。

## 模块依赖

此插件自身包含多个模块。要使用此插件，你的项目或模块**必须启用此插件本身**。其内部模块之间的依赖关系如下（从模块名推断）：
- `MeshResizingCore` 提供核心数据结构和基础功能。
- `MeshResizingEngine` 可能依赖 `MeshResizingCore`，提供核心的缩放算法或引擎集成。
- `MeshResizingEditorTools` 和 `MeshResizingDataflowNodes` 是面向用户接口的模块，依赖前面的引擎和核心模块。

**使用者需在 .uproject 或 .Build.cs 中显式启用 `MeshResizing` 插件。** 如果你的模块代码需要直接调用插件内部的功能，你需要根据目标功能，在你的模块依赖（PrivateDependencyModuleNames）中添加相应的子模块名，例如 `MeshResizingCore` 或 `MeshResizingEngine`。具体依赖请参考各子模块的文档。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量转单精度的编译警告。 |
| 2026-05-12 | `a7802337` | Dataflow: | （与数据流功能相关的提交，具体信息未提供）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在头文件重构前补充了必要的包含声明。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 为数据流中的绘画工具添加了套索支持，利用了网格编辑的新特性。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 更新了大量数据流节点以使用新的渲染系统。 |

### 维护评价

- **状态**：**活跃维护中**。
- **分析**：插件创建于 2024 年底，属于非常新的项目。从提交历史看，直至 2026 年 5 月仍有持续的功能开发（如新增套索工具）和优化（如更新渲染系统、修复警告）。这表明 Epic 的团队正在积极开发和迭代此插件。
- **推荐度**：作为官方实验性插件，适合**提前体验和技术预览**。由于标记为 `IsExperimentalVersion`，且 `EnabledByDefault=false`，其 API 和功能可能在未来版本中发生重大变化或不稳定，不建议用于需要高度稳定性的正式生产项目。但非常适合关注前沿工作流和技术原型验证的开发团队。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]() (暂无)
- [测试用例]() (路径待确认，通常位于 `Engine/Plugins/Experimental/MeshResizing/Tests/` 或 `Engine/Tests/` 下)

**子模块文档**：
- [MeshResizingCore.md](MeshResizingCore.md)
- [MeshResizingEditorTools.md](MeshResizingEditorTools.md)
- [MeshResizingEngine.md](MeshResizingEngine.md)
- [MeshResizingDataflowNodes.md](MeshResizingDataflowNodes.md)