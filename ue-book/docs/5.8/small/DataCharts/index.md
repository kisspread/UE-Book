# Data Charts

> Generate charts based on data tables（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据图表 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DataCharts` (Runtime), `DataChartsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-01-23 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataCharts) | |

## 用途

根据数据表（DataTable）自动生成图表可视化。面向虚拟制片场景，将游戏引擎中的结构化数据以图表形式呈现，便于数据监控和分析。该插件仍处于 Beta 状态，未默认安装。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`DataCharts`](DataCharts.md) | Runtime | 核心图表生成逻辑，数据绑定与渲染 |
| [`DataChartsEditor`](DataChartsEditor.md) | Editor | 编辑器集成，图表资产的编辑与放置支持 |

## 使用场景

- 你在虚拟制片流程中需要实时可视化数据表中的数值变化 → 用 DataCharts
- 你需要在编辑器中快速预览 DataTable 的统计图表 → 用 DataChartsEditor

## 模块依赖

该插件无特殊依赖，仅使用标准 Core/Engine/Slate 等基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录通用改动 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 添加头文件引用，为后续修改做准备 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件中的外部链接为安全协议 |
| 2021-01-26 | `d52549d8` | Placement Mode: shape category special icon handling and updates to plugins using FPlaceableItem | 适配放置模式 API 变更 |
| 2020-09-03 | `7a7c1c0c` | Updated Data Charts Plugin for new Placement Mode API. Included temporary icon that will be replace | 适配新放置模式 API，添加临时图标 |

### 维护评价

⚠️ **维护不活跃，不建议新项目使用。**

- 该插件自 2023 年 1 月起已超过 2 年无实质性功能更新，最近几次提交均为外部 API 适配或头文件调整。
- 仍标记为 `IsBetaVersion=true` 且 `Installed=false`，从未正式发布。
- Epic 的虚拟制片工具链已向其他方向演进（如 nDisplay、In-Camera VFX 等），该插件前景不明。
- 如果你确实需要在 UE 中渲染图表，可将其作为参考实现，但不建议依赖它构建正式功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataCharts)