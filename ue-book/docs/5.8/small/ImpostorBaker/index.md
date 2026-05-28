# ImpostorBaker

> Generates a variety of Impostors for use as distant mesh LODs.

| 属性 | 值 |
|---|---|
| 中文名 | 伪装物烘焙器 |
| 分类 | Mesh |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2021-05-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImpostorBaker) | |

## 用途

ImpostorBaker 是一个工具插件，旨在解决大型开放世界或场景中远距离静态网格物体（Static Mesh）的渲染性能问题。它通过生成高质量的“伪装物”（Impostor），替代原始的高面数网格作为低级LOD使用。这些伪装物通常是一系列预渲染的图像或简化的几何体，从不同角度观察时能模拟原始网格的外观，从而在几乎不损失视觉质量的前提下，大幅减少渲染开销和内存占用。

## 使用场景

- **大型开放世界游戏**：当场景中有大量树木、岩石、建筑等静态物体时，需要为远距离物体生成Impostor LOD。
- **性能敏感的项目**：需要极致优化渲染管线，尤其是在移动平台或低端PC上。
- **自定义LOD工作流**：项目有特殊的LOD生成需求，或希望自动化生成Impostor资产。

## 蓝图用法

该插件的核心功能是提供一套蓝图节点，用于从现有静态网格资产生成不同类型的Impostor。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Generate Impostor` | 主要的生成节点，输入一个静态网格，输出Impostor资产及其材质。 | （插件蓝图资产） |
| `Create MIC Editor Only` | 创建仅编辑器使用的材质实例，常用于烘焙过程中的材质设置。 | （插件蓝图资产） |

### 使用示例（蓝图描述）

1.  在资产浏览器中，右键点击一个静态网格资产（如一棵树）。
2.  在“Scripted Asset Actions”上下文菜单中，选择“ImpostorBaker”相关操作（具体菜单项名称取决于插件集成方式）。
3.  弹出的设置窗口中，选择Impostor类型（如Billboard、Octahedral等）、分辨率、生成参数。
4.  执行生成后，插件会创建一个新的静态网格资产（Impostor网格）和对应的材质/材质实例。

## C++ 用法

由于此插件主要为纯内容插件（无C++代码模块），其功能完全通过蓝图资产和编辑器扩展实现。**在C++中直接调用其功能并非标准用法**。如需在C++工具中集成类似功能，通常需要直接实现Impostor烘焙算法。

## Demo 示例

**重要提示**：此插件默认未启用（`Installed: false`）且位于 `Experimental` 目录下。使用前需手动启用。

1.  在项目设置的插件（Plugins）窗口中，搜索并启用“ImpostorBaker”插件。
2.  启用后，编辑器重启可能提示需要其依赖插件（`BlueprintMaterialTextureNodes` 和 `GeometryScripting`），请一并启用。
3.  在内容浏览器中找到一个静态网格资产。
4.  按照“蓝图用法”章节中的描述，使用上下文菜单或工具栏中的ImpostorBaker功能生成一个伪装物。

## 模块依赖

此插件本身没有C++代码模块，但其蓝图资产和功能依赖以下插件：

| 模块 | 用途 |
|---|---|
| `BlueprintMaterialTextureNodes` | 提供蓝图中操作材质和纹理的节点，用于烘焙过程中的材质创建与设置。 |
| `GeometryScripting` | 提供几何脚本功能，可能用于Impostor网格的生成和编辑操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-23 | `2e8618c3` | ImpostorBaker: Make geometryscripting reference editor only since it is only used in editor only con | 限制几何脚本模块引用仅在编辑器上下文中，优化依赖关系。 |
| 2025-01-30 | `5e6326e8` | ImpostorBaker: Replaced node that was innaccesible with "CreateMICEditorOnly" and also made it clean | 替换了无法访问的节点为 `CreateMICEditorOnly`，并清理了相关代码。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的厂商链接为安全协议（HTTPS）。 |
| 2021-05-27 | `43fa62fc` | Merge from Release-Engine-Test @ 16487383 to UE5/Main | 从引擎测试分支合并至UE5主线，初始版本。 |

### 维护评价

- **状态**：**维护中，但不活跃**。
- **分析**：
    - 插件创建于2021年，已有约4年历史。
    - 有持续的更新记录，最近一次是2025年4月的修复，表明仍被关注。
    - 但绝大多数更新（特别是2025年之前的）主要是针对UE版本升级的编译修复和链接更新，**实质性功能增强非常少**。
    - 插件标记为实验性（`Installed: false`）且位于`Experimental`目录，表明其稳定性和API可能发生变化。
- **建议**：可以试用或作为实现类似功能的参考，但不建议作为项目中长期依赖的核心解决方案。使用时需要接受其可能存在的限制和潜在的维护中断风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImpostorBaker)