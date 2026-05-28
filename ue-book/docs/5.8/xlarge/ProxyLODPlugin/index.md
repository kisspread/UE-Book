# Proxy LOD Plugin (Experimental)

> A plugin to generate Proxy LOD systems.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 代理LOD插件 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProxyLODMeshReduction` (Editor), `DirectXMesh` (External), `UVAtlas` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ProxyLODPlugin) | |

## 用途
该插件提供在虚幻编辑器中生成代理级别（Proxy Level of Detail, ProxyLOD）网格的功能。它主要用于简化复杂或高面数静态网格体，通过算法生成一个低面数的代理网格，同时尽可能保持原始网格的视觉特征（如轮廓和主要形状）。这种代理网格常用于远处物体的渲染、碰撞检测优化或作为HLOD（Hierarchical Level of Detail）系统的一部分，以提升游戏运行时的性能。

## 使用场景
- 你拥有一个高面数的静态网格体（如建筑、岩石、环境资产），需要为其生成一个简化的代理网格用于远处渲染。
- 你在搭建开放世界场景，需要为HLOD系统生成代理网格以优化内存和渲染性能。
- 你需要一个自动化的工作流，在编辑器中批量或交互式地为资产生成优化后的LOD网格。

## 蓝图用法
该插件主要通过编辑器工具和命令行使用，本身不提供标准的蓝图节点。其核心功能（代理网格生成算法）封装在 `ProxyLODMeshReduction` 运行时模块中，但预期在编辑器上下文中通过静态网格体编辑器、资产工具或编辑器工具栏按钮调用。

## C++ 用法
该插件主要通过编辑器界面交互使用。其核心算法位于 `ProxyLODMeshReduction` 模块中，但通常不直接从用户代码调用，而是作为编辑器功能的后端。

### 头文件引入
```cpp
// 如果你需要在C++中直接使用其功能（非典型用法），可引用该模块
#include "ProxyLODMeshReduction.h"
```

## 模块列表
| 模块 | 类型 | 说明 |
|---|---|---|
| `ProxyLODMeshReduction` | Editor | 核心模块，包含代理LOD网格生成的算法和主要功能。 |
| `DirectXMesh` | External | 第三方库，提供DirectX网格处理（如网格简化、属性计算）功能。 |
| `UVAtlas` | External | 第三方库，提供UV展开算法，用于生成代理网格的UV。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了32位和64位格式化说明符与参数类型不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF` 宏。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 使用代码修复工具将所有手写的空析构函数改为 `= default`。 |
| 2025-09-15 | `8bdc434e` | Workaround to prevent crash in UVAtlas | 添加了一个变通方案以防止UVAtlas库崩溃。 |

### 维护评价
- **创建时间**：约2年前（2024年1月）。
- **维护状态**：**活跃维护**。最近一次更新在2026年5月，且近期有多次提交，内容包括编译警告修复、第三方库稳定性问题修复和代码现代化。
- **实验性状态**：标记为 `IsBetaVersion: true`，说明功能可能不完整或接口不稳定。
- **推荐度**：适合在Windows平台上进行实验性开发和功能验证。由于是实验性功能，不建议直接用于生产环境。若需使用，建议关注其更新日志并做好备份。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ProxyLODPlugin)