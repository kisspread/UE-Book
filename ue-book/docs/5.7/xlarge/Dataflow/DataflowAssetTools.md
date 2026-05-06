# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流图编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、节点配置） |
| 模块 | `DataflowAssetTools` (Runtime), `DataflowEditor` (Runtime), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow) | |

## 用途

DataflowGraph 是一个**数据流节点图**系统，允许用户通过可视化节点连线的方式驱动几何数据处理流程。类似蓝图但专为**几何集合（Geometry Collection）**、**动态网格（DynamicMesh）** 等程序化几何内容设计。它解决了传统手工编辑几何数据低效、难以复用的痛点，提供了可配置的数据处理管线。

- 节点执行**无副作用**的数据转换（输入→输出），支持分支、合并、迭代。
- 内置常见几何操作节点（如网格细分、布尔、重拓扑、UV 生成等），也可通过 C++ 扩展自定义节点。
- 与 **Chaos 物理破坏**、**Procedural Content Generation** 深度集成，可用于编写程序化破坏效果、建筑生成、地形修饰等。

## 使用场景

- 你需要为游戏创建**程序化建筑物**，定义墙体、门窗的生成规则 → 用 Dataflow 节点组合布尔与实例化操作
- 在 **Chaos 破坏**流程中，需要自定义碎片生成或预碎片的网格优化 → 用 Dataflow 替代传统蓝图或 Python 脚本
- 作为**工具开发者**，希望为用户提供可组合的几何处理节点，而非硬编码算法 → 基于 Dataflow 派生自定义节点

## 模块概述

| 模块 | 类型 | 功能 |
|---|---|---|
| `DataflowAssetTools` | Runtime | 核心资产导入/导出工具，提供几何数据格式转换（如 `FRenderingFacade` ↔ `FDynamicMesh3`） |
| `DataflowEditor` | Runtime | 编辑器 UI 与交互逻辑，节点图编辑、资产工厂、Preview Actor 管理等 |
| `DataflowEnginePlugin` | Runtime | 运行时支持模块，允许在游戏中使用 Dataflow 资产执行计算 |
| `DataflowNodes` | Runtime | 预置节点库，包含数学运算、几何操作、集合处理等基础节点 |

## DataflowAssetTools 模块（核心转换工具）

本模块负责将 Dataflow 内部渲染表示（`FRenderingFacade`）与通用几何格式（`FDynamicMesh3`）相互转换，是连接 Dataflow 图与外部几何数据的关键桥梁。

### 蓝图用法

**当前版本**未暴露蓝图可调用函数（所有 API 均为 C++ 内部使用）。如需在蓝图中使用 Dataflow，请通过 Dataflow 节点图直接拖拽或调用 `Run Dataflow` 节点。

### C++ 用法

#### 头文件引入

```cpp
#include "Dataflow/CollectionRenderingPatternUtility.h"
```

#### 基本用法

将几何集合的渲染面转换为动态网格，并取用第一个网格：

```cpp
using namespace UE::Dataflow::Conversion;

// 假设已有 Facade 对象（来自 GeometryCollection 或 Dataflow 资产）
const GeometryCollection::Facades::FRenderingFacade& RenderingFacade = /* ... */;

// 创建动态网格并填充数据
FDynamicMesh3 DynamicMesh;
RenderingFacadeToDynamicMesh(RenderingFacade, 0, DynamicMesh, true);

// 后续可用 DynamicMesh 进行网格操作（如几何处理、可视化）
```

*来源：[DataflowAssetTools/Source/Public/Dataflow/CollectionRenderingPatternUtility.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Dataflow/Source/DataflowAssetTools/Public/Dataflow/CollectionRenderingPatternUtility.h)*

#### 反向转换

将动态网格写回渲染面，用于保存或传递回 Dataflow 管线：

```cpp
FDynamicMesh3 ProcessedMesh = /* ... */;
GeometryCollection::Facades::FRenderingFacade Facade;
DynamicMeshToRenderingFacade(ProcessedMesh, Facade);
```

#### 进阶用法

结合 Dataflow 图执行批量转换，利用 `bBuildRemapping` 参数保留顶点索引映射，便于后续属性同步：

```cpp
// 假设 SceneCollection 是多个 Geometry 的容器
for (int32 Idx = 0; Idx < SceneCollection.NumGeometries(); ++Idx)
{
    FDynamicMesh3 TempMesh;
    RenderingFacadeToDynamicMesh(SceneCollection.Facade, Idx, TempMesh, true);
    // 此时 TempMesh 的顶点 ID 与 Facade 顶点索引一一映射
    // 修改 TempMesh 后，可通过映射写回
    DynamicMeshToRenderingFacade(TempMesh, SceneCollection.Facade);
}
```

## Demo 示例

以下是一个最小控制台命令，演示在编辑器中使用 DataflowAssetTools 转换数据（需在 `DataflowEditor` 模块启用时运行）：

```cpp
// DataflowAssetToolsDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Dataflow/CollectionRenderingPatternUtility.h"
#include "GeometryCollection/GeometryCollection.h"

class FDataflowAssetToolsDemo
{
public:
    static void Run();
};
```

```cpp
// DataflowAssetToolsDemo.cpp
#include "DataflowAssetToolsDemo.h"
#include "GeometryCollection/GeometryCollectionFacades.h"

void FDataflowAssetToolsDemo::Run()
{
    // 示例：创建一个空的 GeometryCollection，手动添加一个渲染面
    UGeometryCollection* GC = NewObject<UGeometryCollection>();
    const auto& Facade = GC->GetRenderGeometryCollection()->GetFacade();

    // 此处仅为演示 API 调用，实际使用需有有效的 Facade
    UE::Geometry::FDynamicMesh3 Mesh;
    UE::Dataflow::Conversion::RenderingFacadeToDynamicMesh(Facade, INDEX_NONE, Mesh);
    // 此时 Mesh 包含 Facade 中所有几何
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 基础几何数据结构（`FDynamicMesh3`、动态网格操作） |
| `GeometryCollectionEngine` | 几何集合资产的运行时表示与面结构（`FRenderingFacade`） |
| `ChaosCore` | 物理计算核心（Dataflow 常与 Chaos 破坏绑定） |
| `SkeletalReductionLib` | 网格简化相关（可选，用于节点内部） |

其余依赖均为标准 `Core`、`Engine`、`Projects` 等，不逐一列出。

## 维护状态

### 近期更新

- 2025-11-18 `296af658` — Dataflow: make sure we mark the dataflow package dirty when the tools are committing their values
- 2025-10-16 `8b858c13` — Unshelved from pending changelist '46933319'
- 2025-10-03 `7f04ddbd` — Dataflow: fix cancelled close request causing the preview actor to be deleted and subsequent calls
- 2025-10-03 `71e223a6` — Dataflow: (功能更新，具体内容未记录)
- 2025-10-02 `aba7c452` — Disable the dataflow slow task progress notification for now as this is causing UI focus issues

### 维护评价

- **创建时间**：2025-10-02，距今约 0.1 年，属于非常年轻的插件。
- **更新频率**：创建后第一个月有密集提交（2025-10-02 至 2025-10-16），之后进入间歇性维护，最近一次在 2025-11-18。
- **活跃度**：属于**实验性**插件（`IsExperimentalVersion=true`），官方仍在积极开发，但 API 不稳定，版本号 0.1。
- **已知问题**：部分 UI 操作可能导致焦点问题（如 slow task notification被禁用），取消关闭请求时预览 actor 异常删除（已修复）。
- **推荐使用**：适合尝鲜与内部工具开发；**不建议直接用于生产项目**，因 API 可能频繁变更且缺乏完整文档。若需要稳定几何处理管线，可等待正式版或评估其他成熟方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow)
- [官方文档（暂无）]()
- [测试用例]()（此插件尚未公开独立测试用例）