# Proxy LOD Plugin (Experimental)

> A plugin to generate Proxy LOD systems.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProxyLODMeshReduction` (Editor), `DirectXMesh` (External), `UVAtlas` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin) | |

## 用途

ProxyLODPlugin 是一个**编辑器工具**，用于为大型静态网格体（Static Mesh）生成简化的**代理（Proxy）模型**，以创建高效的 LOD（Level of Detail）系统。它并非传统的基于边折叠的网格简化，而是通过**体素化（Voxelization）和网格重建**的技术，将复杂的几何体转换为一个更简单、面数更少但形状大致保留的代理网格。这对于优化开放世界场景中大量静态物体的渲染性能至关重要。

## 使用场景

-   你在开发一个**开放世界游戏**，场景中有大量复杂的建筑、岩石或植被模型，需要为它们生成低面数的 LOD 模型以提升远处渲染性能。
-   你需要为复杂的静态网格体快速生成一个**碰撞代理体**，用于物理模拟或遮挡剔除。
-   传统的网格简化工具无法很好地处理模型间的**缝隙和穿插**，而此插件的体素化方法能更好地处理这类情况。

## 蓝图用法

此插件主要作为**编辑器工具**集成，通常通过编辑器菜单或按钮触发，而非在运行时蓝图中调用。其核心功能是作为**网格简化管线（Mesh Reduction Pipeline）** 的一部分，可能被其他编辑器工具或资产处理流程调用。

## C++ 用法

此插件的核心功能通过 `ProxyLODMeshReduction` 模块提供，通常作为编辑器扩展或自定义资产处理工具的一部分被调用。

### 头文件引入

```cpp
#include "ProxyLODMeshReductionModule.h"
```

### 基本用法

该插件通常不直接在游戏代码中使用，而是作为编辑器工具链的一部分。其主要入口点是 `ProxyLODMeshReduction` 模块，它注册了自定义的网格简化器。

## Demo 示例

由于此插件是编辑器工具，没有运行时 Demo。其使用方式是：
1.  在项目设置中启用 `ProxyLODPlugin`。
2.  在内容浏览器中选择一个或多个静态网格体资产。
3.  通过右键菜单或编辑器工具栏找到“生成代理 LOD”或类似选项。
4.  配置体素化分辨率、目标面数等参数。
5.  执行生成，插件将创建一个新的、简化的静态网格体资产。

## 模块依赖

从 `Build.cs` 分析，使用此插件需要以下非标准依赖：

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 用于读取和操作网格的顶点、三角形等几何数据。 |
| `MeshConversion` | 用于在不同网格表示格式（如 MeshDescription 与 RenderData）之间转换。 |
| `MeshUtilitiesCommon` | 提供网格处理相关的通用工具函数。 |
| `ProxyLODMeshReduction` | 本插件的核心模块，提供代理 LOD 生成算法。 |
| `DirectXMesh` | 第三方库，提供 DirectX 相关的网格处理工具（如计算法线、切线）。 |
| `UVAtlas` | 第三方库，提供 UV 图集生成算法，用于为代理网格创建新的 UV 布局。 |

## 维护状态

### 近期更新

由于未提供具体的 git log 信息，无法列出近期更新。基于其创建时间和实验性状态，该插件可能已长期处于维护不活跃状态。

### 维护评价

-   **年龄**: 创建于 2017 年，已有约 7 年历史。
-   **状态**: `.uplugin` 明确标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明它是一个**实验性功能**，从未达到正式发布状态。
-   **平台限制**: 仅支持 `Win64` 平台。
-   **综合评价**: 这是一个**实验性、可能已废弃**的插件。它提供了独特的体素化代理 LOD 生成方法，但长期处于 Beta 状态且默认禁用。**不推荐在新项目中作为核心依赖使用**，除非你明确需要其特定的体素化生成算法，并愿意承担实验性功能的风险。对于生产环境，建议评估官方支持的、更成熟的 LOD 生成方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin)