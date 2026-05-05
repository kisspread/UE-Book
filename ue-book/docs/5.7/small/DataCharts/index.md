# Data Charts

> Generate charts based on data tables

| 属性 | 值 |
|---|---|
| 分类 | VirtualProduction |
| 默认启用 | 是 |
| 包含内容 | 是（Blueprint、材质、Mesh） |
| 模块 | DataCharts (Runtime), DataChartsEditor (Editor) |
| 创建时间 | 2020-01-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| Beta 状态 | ⚠️ IsBetaVersion = true |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataCharts) | |

## 用途

DataCharts 是一个基于 **蓝图** 实现的数据可视化插件，允许你在 UE5 场景中直接放置柱状图（Bar Chart）、饼图（Pie Chart）和折线图（Line Chart）。它通过 DataTable 作为数据源，将结构化数据渲染为 3D 图表 Actor，适用于虚拟制片（Virtual Production）场景中的实时数据展示。

C++ 层本身几乎没有逻辑——Runtime 模块是空壳，Editor 模块仅负责在编辑器的 Placement 面板中注册图表类别。所有的图表生成、数据绑定和动画逻辑都在 **蓝图（Blueprint）** 中实现。

## 使用场景

- **虚拟制片 LED Volume 现场**：在 VP Stage 上实时展示拍摄进度、预算分配等数据
- **编辑器内数据预览**：需要在关卡中直观查看 DataTable 数据分布时
- **演示与审片**：在 Sequencer 或实时预览中嵌入动态图表辅助决策

## 蓝图用法

### 可用的图表类型

插件通过编辑器的 **Place Actors** 面板提供三种图表 Blueprint：

| 图表类型 | Blueprint 路径 | 说明 |
|---|---|---|
| 柱状图 | `/DataCharts/Blueprints/BP_BarChart` | 竖向柱状图，适合对比数值大小 |
| 饼图 | `/DataCharts/Blueprints/BP_PieChart` | 圆形饼图，适合展示比例分布 |
| 折线图 | `/DataCharts/Blueprints/BP_LineChart` | 折线趋势图，适合展示变化趋势 |

### 放置图表

1. 在编辑器中打开 **Place Actors** 面板（窗口 → 放置 Actor）
2. 找到 **Data Charts** 分类（带有 Virtual Production 图标）
3. 拖拽 BarChart、PieChart 或 LineChart 到场景中

### 数据绑定

图表使用 UE5 的 **DataTable** 作为数据源。插件附带了一个示例 DataTable：

- `Content/Blueprints/DT_Sample` — 示例数据表

你需要创建或准备一个 DataTable 资产，然后在图表 Actor 的 Details 面板中指定数据源。

### 图表组件

插件包含以下蓝图组件/资产：

| 资产 | 路径 | 说明 |
|---|---|---|
| `BP_ChartBase` | `/DataCharts/Blueprints/BP_ChartBase` | 图表基类，所有图表的父类 |
| `CC_Chart` | `/DataCharts/Blueprints/CC_Chart` | 图表自定义组件 |
| `CF_AnimGrow` | `/DataCharts/Blueprints/CF_AnimGrow` | 生长动画（数值从 0 增长到目标值） |
| `CF_AnimFade` | `/DataCharts/Blueprints/CF_AnimFade` | 淡入动画效果 |
| `FChart_Sample` | `/DataCharts/Blueprints/FChart_Sample` | 示例图表函数/格式 |

### 资源资产

| 资产 | 路径 | 说明 |
|---|---|---|
| `SM_Bar` | `/DataCharts/Content/Meshes/SM_Bar` | 柱状图 Mesh |
| `SM_Line` | `/DataCharts/Content/Meshes/SM_Line` | 折线图 Mesh |
| `M_Chart` | `/DataCharts/Content/Materials/M_Chart` | 图表基础材质 |
| `M_ChartLine` | `/DataCharts/Content/Materials/M_ChartLine` | 折线图专用材质 |

## C++ 用法

本插件的 C++ 层非常轻量，几乎没有公开的 C++ API。Runtime 模块的 `StartupModule()` 和 `ShutdownModule()` 均为空实现。所有功能通过蓝图提供。

如果你需要在 C++ 中引用此插件的模块（通常不需要）：

### 头文件引入

```cpp
// 仅当你需要显式引用模块时
#include "DataCharts.h"        // Runtime 模块（空）
// Editor 模块不对外暴露头文件
```

### Build.cs 依赖

在你的 `.Build.cs` 中添加（如有必要）：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "DataCharts"  // Runtime 模块
});
```

> **注意**：由于 Runtime 模块不暴露任何公共 API 或类，添加此依赖实际上没有意义。本插件的主要价值完全在蓝图层面。

## 模块依赖

### DataCharts (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Projects` | 插件/模块管理 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |

> 均为 PrivateDependency，不对外暴露。

### DataChartsEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `EditorFramework` | 编辑器框架 |
| `Engine` | 引擎核心 |
| `Projects` | 插件/模块管理 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `UnrealEd` | 编辑器功能 |
| `PlacementMode` | Actor 放置面板注册 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da71ab9` | IWYU updates to reduce includes | 纯编译维护，清理 include 依赖 |
| 2022-11-07 | `0a10c21ff628` | Update Release-Engine-Staging | 引擎 staging 合并，非针对性更新 |
| 2022-11-03 | `049a3a702172` | Added includes for future change | 预备性 include 添加，空占位文件 |

### 维护评价

**⚠️ 维护不活跃，可能已废弃**

- 创建于 2020 年 1 月（约 6 年前），最初就是 Beta 版本
- 最后一次实质性更新在 **2023 年 1 月**（IWYU 清理），距今超过 3 年
- 最后的功能性提交可追溯到 **2022 年 11 月**之前
- `.uplugin` 中 `IsBetaVersion: true` 始终未摘除，说明从未达到正式发布状态
- 所有核心逻辑在蓝图中，C++ 层几乎没有代码，说明这是一个轻量原型
- `DocsURL` 为空，Epic 从未为此插件编写官方文档

**建议**：如果你需要在 UE5 中展示 DataTable 数据图表，可以参考此插件的蓝图实现思路，但不建议作为生产级解决方案依赖。考虑使用 UMG + 条形图 Widget 或第三方可视化库作为替代。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataCharts)
- 官方文档：无（`DocsURL` 为空）
- 测试用例：无（未发现自动化测试）
