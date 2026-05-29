# Data Charts

> Generate charts based on data tables

| 属性 | 值 |
|---|---|
| 中文名 | 数据图表 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、放置模式配置） |
| 模块 | `DataCharts` (Runtime), `DataChartsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-01-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataCharts) | |

## 用途

DataCharts 插件用于基于 DataTable（数据表）自动生成可视化图表。它属于虚拟制作（VirtualProduction）工具链的一部分，旨在帮助用户在编辑器中直观地查看和分析表格数据，例如资产统计数据、性能指标或其他结构化信息。

该插件的核心功能是将 Unreal Engine 中的 DataTable 资产转化为可交互的图表形式，方便在虚拟制片工作流中进行数据驱动的决策。插件提供了编辑器集成（DataChartsEditor 模块），支持在编辑器中直接预览和放置图表。

> **注意**：此插件标记为 Beta 版本（`IsBetaVersion=true`），且未默认启用（`Installed=false`），属于实验性质的工具。

## 使用场景

- 你在虚拟制片场景中需要可视化分析 DataTable 中的资产统计、预算分配或日程数据
- 你需要将游戏运行时产生的数据表以图表形式展示给团队成员
- 你希望在编辑器中快速预览 DataTable 的数据分布趋势

## 蓝图用法

该插件的公共 API 极为有限，模块头文件仅包含标准的 `IModuleInterface` 实现，未暴露额外的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。图表生成功能可能通过编辑器工具或资产类型实现，而非蓝图节点。

### 核心节点

暂无公开的蓝图节点（插件主要通过编辑器集成工作）。

## C++ 用法

### 头文件引入

```cpp
#include "DataCharts.h"
```

### 基本用法

该插件的 Runtime 模块极为精简，仅提供标准的模块接口：

```cpp
// DataCharts 模块自动随引擎加载，无需手动操作
// 核心功能由编辑器模块 DataChartsEditor 提供
```

> 插件的源码中未包含公开的 C++ API 类或接口，使用方式主要通过编辑器 UI 交互完成。

## Demo 示例

由于该插件未暴露可编程的 C++/蓝图 API，以下为编辑器中的使用方式：

1. 在 `Edit > Plugins` 中启用 **Data Charts** 插件，重启编辑器
2. 创建或打开一个 DataTable 资产
3. 通过插件提供的编辑器界面生成对应的图表视图

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

> 注：Build.cs 中未列出额外的非标准依赖模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录批量更新 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 添加头文件引用，为后续改动做准备 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件中的外部链接更新为 HTTPS |
| 2021-01-26 | `d52549d8` | Placement Mode: shape category special icon handling and updates to plugins using FPlaceableItem | 更新放置模式 API 适配 |
| 2020-09-03 | `7a7c1c0c` | Updated Data Charts Plugin for new Placement Mode API. Included temporary icon that will be replace | 适配新版放置模式 API，添加临时图标 |

### 维护评价

**⚠️ 维护不活跃，谨慎使用**

- 该插件已超过 **2 年**没有功能性更新（最后一次有意义的改动在 2023 年 1 月，仅为引擎级批量变更）
- 标记为 **Beta 版本**，从未达到正式发布状态
- `Installed=false`，说明 Epic 未将其作为默认推荐插件
- 最近几次提交均为被动维护（API 适配、链接更新），无新功能开发
- 源码规模极小（8 个文件），功能完整度存疑
- **不建议在生产项目中依赖此插件**，仅适合原型验证或学习参考

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataCharts)