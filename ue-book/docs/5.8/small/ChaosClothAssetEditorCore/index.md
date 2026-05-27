# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流资产、材质模板等） |
| 模块 | `ChaosClothAssetEditor` (Editor), `ChaosClothAssetEditorTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

该插件是创建和编辑基于 Dataflow（数据流）的布料资产（Cloth Asset）的核心框架。它从早期的 `ChaosClothEditor` 插件中拆分出来，目的是将 USD 相关代码剥离，专注于提供独立的、核心的布料资产编辑功能。它为物理模拟（Chaos）驱动的布料提供了可视化的数据流编辑器、资产预览和基础工具集，是构建高级布料模拟工作流的基础。

## 使用场景

- 你需要为虚拟角色或物体创建和调整基于物理的布料（如服装、旗帜）。
- 你正在使用 Dataflow（数据流图）方式来程序化地定义布料的物理属性、形状和动画行为。
- 你需要一个专门的编辑器来可视化、预览和调试布料资产，而不依赖于 USD 管线。
- 你在开发一个需要物理布料模拟的游戏或应用程序，并希望拥有模块化的核心编辑能力。

## 蓝图用法

作为编辑器核心插件，其主要功能集中在编辑器内的 Dataflow 图表和资产操作，公开给蓝图的节点较少。核心功能通过编辑器 UI 和数据流图提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 资产创建/编辑操作 | 通过编辑器菜单或资产右键菜单触发，非蓝图节点 | N/A (Editor UI) |

## C++ 用法

该插件的 C++ 接口主要用于扩展编辑器功能和构建自定义数据流节点。

### 头文件引入

```cpp
#include "ChaosClothAssetEditorModule.h" // 核心模块
#include "ChaosClothAsset/ClothAsset.h" // 布料资产类
```

### 基本用法

用于在代码中访问布料资产和编辑器功能。
```cpp
// 获取布料资产编辑器模块
IChaosClothAssetEditorModule& ClothEditorModule = FModuleManager::GetModuleChecked<IChaosClothAssetEditorModule>(“ChaosClothAssetEditor”);

// 创建一个新的布料资产 (通常在编辑器工具或自动化流程中使用)
UChaosClothAsset* NewAsset = NewObject<UChaosClothAsset>();
```

### 进阶用法

创建自定义的数据流节点以扩展布料编辑功能。
```cpp
// 自定义数据流节点需要继承自 FDataflowNode 并实现相应接口。
// 该插件提供了基础节点类型和上下文，用于在布料数据流图中进行计算和处理。
// 具体实现请参考模块文档中关于节点开发的部分。
```

## Demo 示例

一个完整的、可编译的最小示例通常涉及创建自定义数据流节点或扩展编辑器面板。由于篇幅限制，此处仅给出框架概念。具体示例请参考模块文档中的 [ChaosClothAssetEditor.md](ChaosClothAssetEditor.md) 和 [ChaosClothAssetEditorTools.md](ChaosClothAssetEditorTools.md)。

## 模块依赖

从 Build.cs 分析，该插件独特的依赖较少，主要用于物理模拟核心。

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心，提供布料模拟底层支持 |
| `ChaosSolverEngine` | Chaos 物理解算器引擎 |
| `DataflowEngine` | 数据流（Dataflow）图执行引擎 |
| `ClothSolverCore` | 布料解算器核心逻辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复浮点精度警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为布料资产添加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Daaflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 在布料和数据流选择工具视口添加 HUD 选择信息 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复编译警告 |

### 维护评价

该插件创建于 **2026年1月**，非常新。从 Git 记录看，维护**极为活跃**，最近一次更新在 **2026年5月20日**。它正处于功能快速迭代和稳定性修复阶段，由 Epic Games 官方团队维护。作为 Chaos 物理布料工具链的核心部分，预计会持续更新。**强烈推荐**用于需要基于数据流编辑布料资产的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- [模块文档：ChaosClothAssetEditor](ChaosClothAssetEditor.md)
- [模块文档：ChaosClothAssetEditorTools](ChaosClothAssetEditorTools.md)