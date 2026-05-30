# ICVFX

> Conveniently collects plugins for In-Camera VFX

| 属性 | 值 |
|---|---|
| 中文名 | 摄影机内视觉特效聚合插件 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ICVFX) | |

## 用途

ICVFX 插件本身不包含任何运行时或编辑器代码。它是一个 **聚合插件**，用于方便地启用一整套用于“摄影机内视觉特效”（In-Camera VFX）工作流的插件。其主要作用是作为一个开关，当启用时，会自动启用其所依赖的一系列特定插件（如 AjaMedia, MediaCompositing, nDisplay 等），从而快速搭建一个适用于虚拟制片和 LED 墙拍摄的测试或演示环境。

## 使用场景

- 你需要在引擎中快速启用一整套用于虚拟制片（Virtual Production）和 ICVFX 工作流的插件，以测试 nDisplay、媒体输入输出、色彩校正等功能时。
- 你在进行 LED 墙拍摄的原型开发或演示，希望一键配置好相关的插件集合。

## 蓝图用法

**无**。本插件不提供任何蓝图节点或资产。它的功能完全通过插件管理器启用其子插件来实现。

## C++ 用法

**无**。本插件不包含任何代码模块，因此不提供 C++ API。

## Demo 示例

**无**。本插件为纯配置聚合插件，不包含独立的可运行示例。

## 模块依赖

本插件自身没有 `Build.cs` 文件。启用本插件后，它将自动启用其 `.uplugin` 文件中定义的以下子插件（基于提供的 `.uplugin` 元数据片段推断）：
- `AjaMedia`
- （以及元数据中可能列出的其他插件，如 `MediaCompositing`, `nDisplay` 等。完整列表需查看插件目录）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `87384dcd` | ICVFX plugin: Move MultiUserClient before LiveLink to avoid optional-dep ordering bug. | 调整了内部插件加载顺序，修复了一个与 MultiUser 和 LiveLink 相关的可选依赖顺序错误。 |
| 2023-06-09 | `3311e621` | Updating supported platforms, now matching QAVirtualProduction. | 更新了支持的平台列表，使其与 QAVirtualProduction 插件保持一致。 |
| 2023-01-31 | `b58de93b` | Create ICVFXTesting plugin with the intention of porting SaloonPerf to use it | 为了将 SaloonPerf 测试迁移到新框架，创建了相关的 ICVFXTesting 插件。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件内链到供应商网站的链接更新为 HTTPS 等安全协议。 |
| 2022-09-16 | `a5ce4e7c` | Change load order for ICVFX plugin to make sure ConsoleVariablesAsset is available. | 调整了 ICVFX 插件的加载顺序，确保其依赖的 ConsoleVariablesAsset 能正确加载。 |

### 维护评价

- **状态**：维护中。插件标记为 `IsBetaVersion: true`，表明其仍处于实验/测试阶段。从 Git 记录看，2023 年仍有平台支持的更新，2025 年有功能性修复（依赖顺序），表明仍在被关注和维护。
- **特点**：本插件是“元插件”，其价值在于聚合和管理其他插件。因此，其更新通常围绕依赖列表、加载顺序和平台支持展开。
- **建议**：推荐在需要快速搭建 ICVFX/Virtual Production 环境时使用。但需注意其“实验性”标签，并在生产环境中评估其启用的所有子插件是否稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ICVFX)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ICVFXTesting) （根据 Git 记录，相关测试可能在此目录或引擎测试目录中）