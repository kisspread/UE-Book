# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑核心 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

此插件是 Chaos 布料系统资产编辑流程的核心框架。它解决了使用数据流（Dataflow）图来创建和编辑布料资产的基础需求。该插件并非包含所有编辑功能，而是提供基础编辑器框架、核心工具类和数据流节点接口，为构建完整的布料资产编辑器（如集成 USD 支持的插件）奠定基础。

## 使用场景

- 你需要为游戏中的角色创建和编辑复杂的服装布料物理模拟资产。
- 你希望使用可视化的数据流节点图（而非纯代码）来定义和调整布料行为。
- 你是技术美术或物理工程师，需要在编辑器内直接对布料资产进行迭代和预览。

## 模块列表

本插件为**大型**插件，按功能拆分为以下子模块：

- [**ChaosClothAssetEditor**](ChaosClothAssetEditor.md): 布料资产编辑器核心模块，提供资产工厂、编辑器窗口、细节面板等基础编辑器框架。
- [**ChaosClothAssetEditorTools**](ChaosClothAssetEditorTools.md): 布料资产编辑工具集，包含基于数据流的工具节点、网格转换工具等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下产生截断警告的代码。 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为Interchange布料资产添加重新导入支持。 |
| 2026-05-12 | `f1d5a018` | Daaflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 为布料和数据流选择工具视口添加HUD选择信息。 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复特定模块文件中的编译警告。 |

### 维护评价

该插件创建时间较近（约1年），近期（2026年4-5月）仍有频繁的功能性更新和问题修复，表明其处于**活跃维护**状态。作为 Chaos 布料资产工作流的核心部分，它仍在持续迭代。目前没有发现已知的重大问题或废弃标记。**推荐使用**，它是构建高级布料编辑功能的基础。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- [官方文档]()（暂无）