# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

本插件是 Chaos 布料资产编辑器的核心模块，提供基于 Dataflow（数据流）架构创建和编辑布料资产所需的基础编辑器功能。它是从原来的 `ChaosClothEditor` 插件拆分而来的三个插件之一，目的是将 USD 相关代码从编辑器模块中分离出来，同时不损失任何功能。

核心能力包括：
- **布料资产的创建与编辑**：通过 Dataflow 节点图定义布料模拟参数、约束和碰撞设置
- **交互式预览与调优**：在编辑器视口中实时预览布料模拟效果
- **资产转换**：将布料资产转换为运行时可用的格式

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`ChaosClothAssetEditor`](ChaosClothAssetEditor.md) | Runtime | 布料资产编辑器核心：资产编辑器 UI、资产类型定义、编辑器动作 |
| [`ChaosClothAssetEditorTools`](ChaosClothAssetEditorTools.md) | Runtime | 布料资产编辑器工具集：交互式视口工具、选择工具、HUD 信息显示 |

## 使用场景

- 你在制作角色服装/旗帜/窗帘等布料效果 → 用本插件在编辑器中可视化创建和调优布料资产
- 你需要通过数据流节点图定义复杂布料模拟逻辑 → 用本插件的 Dataflow 编辑器
- 你需要在编辑器中实时预览布料模拟并调整参数 → 用本插件的交互式视口工具

## 模块依赖

本插件为编辑器侧工具，使用时需要以下特殊依赖（其他常见依赖已省略）：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 布料资产运行时核心（Dataflow 图定义、布料模拟数据） |
| `ChaosClothAssetEditorCore` | 编辑器核心基础设施 |
| `Dataflow` | 数据流框架（节点图引擎） |
| `DataflowEditor` | 数据流编辑器 UI 框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | Interchange 布料资产增加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Dataflow: add HUD selection information to both Cloth and dataflow selection tool viewports | Dataflow 视口中增加 HUD 选择信息显示 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复编译警告问题 |

### 维护评价

- **活跃维护**：插件创建仅约 5 个月，最近一个月内有多次实质性功能更新和修复
- 开发由 Epic Games 主团队（cedric.caillaud、kriss gossart 等）直接推进
- 持续的功能完善：新增 reimport 支持、Dataflow HUD 信息、代码清理
- 作为 Chaos 布料系统编辑器的核心组件，与 UE5 物理模拟管线深度绑定，属于长期维护项目
- **推荐使用**：如果你的项目需要基于 Dataflow 的布料资产编辑工作流，这是必选插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- [父插件原始代码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothEditor)（拆分前）
- [ChaosClothAsset 运行时插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)（运行时核心）