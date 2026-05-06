# Hair Card Generator

> Procedurally generate hair cards from hair strands

| 属性 | 值 |
|---|---|
| 中文名 | 发卡生成器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产与数据） |
| 模块 | `HairCardGeneratorDataflow` (Runtime), `HairCardGeneratorEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairCardGenerator) | |

## 用途

本插件提供了一套数据流（Dataflow）节点和编辑器工具，用于**从真实毛发发丝（hair strands）程序化生成毛发卡片（hair cards）**。传统手动制作 hair cards 流程繁琐且难以迭代，该插件通过几何运算将发丝转化为多边形卡片，并支持自动纹理烘焙、LOD 生成、卡片分组等功能，大幅提升实时毛发资产的制作效率。适合需要程序化毛发管线的游戏或影视项目。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [HairCardGeneratorDataflow](HairCardGeneratorDataflow.md) | Runtime | 核心数据流节点，实现发丝→卡片的几何转换、纹理生成、LOD 逻辑 |
| [HairCardGeneratorEditor](HairCardGeneratorEditor.md) | Runtime | 编辑器 UI 及资产工厂，提供卡片生成窗口、预览和资源管理 |

## 使用场景

- 你在开发需要大量角色头发的游戏（如 RPG、MMO），希望用程序化流程替代手动建模
- 你已拥有 Groom 资产（发丝），需要快速导出为 Hair Cards 以用于实时渲染（游戏内或预览）
- 你需要批量生成不同 LOD 级别的毛发卡片，并自动创建材质纹理

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairCardGenerator)
- [HairCardGeneratorDataflow 模块文档](HairCardGeneratorDataflow.md)
- [HairCardGeneratorEditor 模块文档](HairCardGeneratorEditor.md)

> ⚠️ 本插件为实验性功能，API 和行为可能在后续版本中发生变化。启用前请确保项目有备份机制。