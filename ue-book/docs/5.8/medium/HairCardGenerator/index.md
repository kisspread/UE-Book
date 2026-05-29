# Hair Card Generator

> Procedurally generate hair cards from hair strands

| 属性 | 值 |
|---|---|
| 中文名 | 发卡生成器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（发卡生成数据流和编辑器工具） |
| 模块 | `HairCardGeneratorDataflow` (Runtime), `HairCardGeneratorEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairCardGenerator) | |

## 用途
这个插件用于解决虚拟发丝（Hair Strands）渲染性能开销大的问题。它通过程序化方法将高密度的头发发束数据转换为低多边形的发卡（Hair Cards）几何体。发卡是一种游戏开发中常用的头发渲染技术，用少量几何体配合Alpha通道来模拟复杂发型，比实时模拟每根发丝更节省性能。该插件提供了从Groom资产生成优化发卡网格的工作流，适合需要将影视级头发资产适配到实时渲染场景的情况。

## 使用场景
- 你需要将高精度的Groom资产（如MetaHuman头发）转化为可在移动平台或VR中高效渲染的发卡模型。
- 你在制作一个需要大量NPC且每个NPC都有复杂发型的开放世界游戏，需要优化头发渲染性能。
- 你希望在不损失太多视觉保真度的前提下，大幅减少头发相关的DrawCall和几何复杂度。

## 模块概述
本插件包含两个主要模块：

| 模块 | 类型 | 说明 |
|---|---|---|
| `HairCardGeneratorDataflow` | Runtime | **数据流核心模块**。负责定义生成发卡的数据流图（Dataflow Graph），处理从源发束数据到目标发卡网格的算法和逻辑。 |
| `HairCardGeneratorEditor` | Runtime | **编辑器集成模块**。提供在虚幻编辑器中使用的用户界面、资产处理和操作工具，如导入Groom并生成发卡资产的交互式工具。 |

> **注意**：虽然模块类型标记为`Runtime`，但其主要功能面向内容创作流程。`HairCardGeneratorEditor`模块通常仅在编辑器环境下使用。

## 使用流程
1.  **准备Groom资产**：确保你有一个包含头发发束数据的Groom资产（通常由其他DCC工具创建并导入虚幻）。
2.  **使用编辑器工具**：通过插件提供的编辑器界面，选择目标Groom资产。
3.  **配置与生成**：调整发卡生成的参数（如密度、卡片区分、UV布局等），然后执行生成操作。
4.  **获得发卡资产**：插件会输出一个或多个静态网格体（Static Mesh）资产，即生成的发卡几何体，以及相关的材质和纹理。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairCardGenerator)
- [数据流模块文档](HairCardGeneratorDataflow.md)
- [编辑器模块文档](HairCardGeneratorEditor.md)