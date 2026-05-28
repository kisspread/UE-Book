# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器UI功能） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

该插件是 **TEDS (Editor Data Storage)** 生态系统的功能层。TEDS 是 Unreal Engine 的新一代核心编辑器数据存储系统，而本插件并非 TEDS 本身，而是**基于 TEDS 构建的一系列具体的编辑器UI和功能模块**。它旨在使用 TEDS 的高性能、数据驱动架构来重新实现或增强现有的编辑器功能，例如内容浏览器、大纲视图、属性编辑器等，为编辑器界面提供更统一、高效的数据访问和操作方式。

## 使用场景

-   当你需要**高性能、数据驱动的编辑器UI**来处理大量场景Actor或资产时。
-   当你需要**扩展编辑器数据结构**（如向 Actor 或资产添加自定义元数据）而不修改原有类时。
-   当你需要**统一不同编辑器面板**（如内容浏览器、大纲视图）的数据管理方式时。
-   当你需要在编辑器中**基于复杂查询**来浏览、筛选和操作 Actor、资产等数据时。

## 蓝图用法

本插件主要为编辑器功能扩展提供蓝图可用的接口和节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （基于模块推断，具体API需查阅子模块） | 创建或获取数据视图 | 各模块中的 `UCLASS` |
| （基于模块推断） | 执行数据查询 | `TedsQueryStack` 相关类 |
| （基于模块推断） | 操作资产数据 | `TedsAssetData` 相关类 |
| （基于模块推断） | 管理收藏夹 | `UnifiedFavorites` 相关类 |

### 使用示例（蓝图描述）

由于该插件高度模块化，蓝图用法分散在各子模块中。典型使用流程可能是：
1.  在自定义编辑器工具蓝图中，使用 `TedsContentBrowser` 模块提供的节点来创建自定义的资产浏览器。
2.  使用 `TedsQueryStack` 模块构建查询，以在自定义面板中显示特定条件的 Actor 列表。
3.  通过 `TedsPropertyEditor` 模块集成自定义属性到标准属性编辑器中。

## C++ 用法

该插件的 C++ API 主要面向编辑器工具开发者，用于扩展或替换现有编辑器功能。

### 头文件引入

根据使用的子模块引入对应头文件：
```cpp
#include "TedsOutliner/TedsOutlinerModule.h"
#include "TedsContentBrowser/TedsContentBrowserModule.h"
#include "TedsQueryStack/TedsQueryStackModule.h"
// ... 其他模块头文件
```

### 基本用法

注册自定义数据类型并创建视图（概念性示例）：
```cpp
// 获取 TEDS 查询栈模块
ITedsQueryStackModule& QueryStackModule = FModuleManager::Get().LoadModuleChecked<ITedsQueryStackModule>(TEXT("TedsQueryStack"));

// 创建查询（概念，具体API需查阅模块文档）
FQueryHandle Query = QueryStackModule.CreateQuery(FMyCustomQueryParams());

// 将查询结果绑定到自定义UI（例如，一个Slate列表视图）
TSharedRef<SWidget> MyWidget = SNew(SMyListView).QueryStack(Query);
```

### 进阶用法

通过多个模块组合，构建复杂的编辑器功能：
1.  使用 `TedsTypeInfo` 定义自定义数据结构。
2.  使用 `TedsOperations` 对这些数据执行批量操作。
3.  使用 `TedsTableViewer` 以表格形式展示数据。
4.  使用 `TedsPropertyEditor` 让用户在表格中直接编辑属性。

## 模块依赖

所有子模块都高度依赖 TEDS 核心系统。要使用本插件的任何功能，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 核心模块，提供数据存储、查询等基础架构 |
| `PropertyEditor` | 属性编辑器扩展，被 `TedsPropertyEditor` 等模块依赖 |
| `ContentBrowser` | 内容浏览器扩展，被 `TedsContentBrowser` 模块依赖 |
| `OutlinerModule` | 大纲视图扩展，被 `TedsOutliner` 模块依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限的 UEFN 环境中启用 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 大纲视图中隐藏非编辑关卡实例内的未加载 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复 TEDS 大纲视图中无效的跨关卡拖放操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回滚变更 CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 大纲视图中隐藏非编辑关卡实例内的未加载 Actor 行 |

### 维护评价

该插件是**活跃维护中的实验性项目**。
- **创建时间**：约 2 年前（2024年7月），属于较新的功能。
- **更新频率**：近期（2026年5月）有**密集的功能更新和问题修复**，特别是针对 `TedsOutliner` 模块。
- **维护状态**：处于**活跃开发阶段**，由 Epic 团队持续完善。
- **已知限制**：标记为 `IsExperimentalVersion: true`，表明 API 和功能尚不稳定，未来可能发生变化。
- **推荐使用**：**不建议用于生产环境**。适合有兴趣的开发者研究 TEDS 架构、学习新编辑器功能开发模式，或在自己的实验性项目中尝试。对于需要稳定性的项目，应继续使用传统的编辑器子系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- 官方文档：暂无
- 测试用例：源码目录内可能包含，需查阅各子模块