# AnimDatabase

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、数据表） |
| 模块 | `AnimDatabase` (Runtime), `AnimDatabaseEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimDatabase) | |

## 用途

AnimDatabase 是一个实验性插件，旨在提供一个用于管理和查询动画数据的数据库系统。它解决的核心问题是：在复杂动画系统（如需要动态混合、变形或基于机器学习生成动画）中，如何高效地组织、索引和检索大量的动画片段或动画数据资产。其存在是为了支持高级动画工作流，特别是与 `AnimationWarping` 和 `LearningCore` 等插件结合使用时，为动画数据提供结构化存储和快速访问能力。

## 使用场景

- 你正在开发一个需要动态动画混合或程序化动画生成的系统，需要一个中央仓库来存储和查询基础动画片段。
- 你正在使用 `AnimationWarping` 插件进行动画变形，需要管理变形的目标动画数据。
- 你正在集成机器学习（通过 `LearningCore`）来生成或驱动动画，需要一个结构化的方式来存储训练数据或生成结果。
- 你的项目包含大量动画资产，需要一种比传统资产浏览器更高效、可编程的查询方式。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `AnimDatabase` | Runtime | 提供动画数据库的核心运行时功能，包括数据存储、查询接口和与动画系统的集成。 |
| `AnimDatabaseEditor` | Editor | 提供在虚幻编辑器中创建、编辑和管理动画数据库资产的工具和界面。 |

### 近期更新

- 2026-04-24 `05f62ee5` AnimGen：新增了在画布上进行调试绘制的支持。
- 2026-04-22 `2fc4ab35` AnimGen：在各编辑器中更改帧范围或帧属性时，不再自动刷新。
- 2026-04-22 `e4a63951` AnimDatabase：新增了若干帧属性函数。
- 2026-04-10 `4f791a26` AnimDatabase：调整了骨骼权重的计算方式，以提升自动编码器在足部关节上的准确性。
- 2026-04-10 `3f7370fe` AnimGen：新增了属性平滑功能，以帮助减少噪声。

### 维护评价

该插件在近期（两周内）提交频率较高，更新内容涵盖功能新增、用户体验优化及核心算法改进，表明其处于**活跃开发与维护**状态。开发团队不仅在添加新特性，也在持续优化现有功能的性能和效果。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimDatabase)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimDatabase/Tests)