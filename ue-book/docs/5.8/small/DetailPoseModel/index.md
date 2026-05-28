# ML Deformer Detail Pose Model

> Detail Pose Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 细节姿势模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `DetailPoseModel` (Runtime), `DetailPoseModelEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel) | |

## 用途

本插件是 UE5 机器学习变形器（ML Deformer）框架中的一个高级变形模型。它旨在解决标准机器学习重建过程中可能丢失的高频率细节问题，例如衣物褶皱、肌肉细微形变等。其核心机制是允许用户定义一组“关键姿势”，在这些姿势下，模型会将机器学习重建结果与额外提供的细节进行混合，从而生成更逼真、细节更丰富的最终变形效果。

本插件是 **Nearest Neighbor Model 的替代与重写**，基于 **Neural Morph Model** 架构构建。这意味着它共享了神经形态模型的所有用户界面和交互逻辑，同时在其基础上增加了“关键姿势细节混合”的专属功能，为用户提供了统一且强大的体验。

## 使用场景

- **电影级角色动画**：在需要极高保真度的角色动画中，用于补充传统蒙太奇或基础ML变形器无法捕捉的服装褶皱和微表情。
- **游戏CG过场动画**：制作高品质的过场动画时，使用此模型确保角色在复杂运动中的细节表现。
- **高精度数字人**：驱动超写实数字人时，作为提升皮肤和衣物变形真实感的最终优化步骤。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `DetailPoseModel` | Runtime | 运行时核心模块，包含模型的数据结构、计算逻辑和资产类型定义。 |
| `DetailPoseModelEditor` | Editor | 编辑器扩展模块，提供模型的属性自定义界面、细节姿势编辑工具和训练流程集成。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel)
- [官方文档 (ML Deformer)](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel/Tests)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-09 | `2e8b3a9b` | [MLDeformer] Fixed a crash on undo on morph based models. Also changed the icon of the Train button. | 修复了基于形态模型撤销操作时的崩溃问题，并更新了训练按钮的图标。 |
| 2025-04-08 | `4bb2bc8d` | [MLDeformer] Added in-engine tools to help with the creation of training data for ML Deformers. Also... | 添加了引擎内工具，用于帮助创建ML变形器的训练数据。 |
| 2025-02-11 | `887aa3d9` | [MLDeformer] Fixed a bug where the Neural Morph Model would actually launch the Detail Pose Model. T... | 修复了一个导致神经形态模型错误启动细节姿势模型的bug。 |
| 2025-01-10 | `a5f27226` | [MLDeformer] Added a new Detail Pose Model. This is a complete rewrite and replacement for the Nearest Neighbor Model... | 初始提交。新增细节姿势模型，作为最近邻模型的完全重写和替代方案，并为其父模型添加了双四元数支持。 |

### 维护评价

本插件**创建于2025年初，非常新**，且自创建以来保持着**活跃的维护状态**。从提交历史看，它不仅是功能新增，也包含了重要的bug修复和依赖该框架的其他模型（如Neural Morph Model）的改进。作为 `IsExperimentalVersion = true` 的插件，它处于快速迭代和完善阶段，API和功能可能随版本变化。对于需要在ML Deformer框架下追求极致变形细节的用户，这是一个**值得关注并推荐试用**的实验性功能。建议在测试项目中验证其稳定性后再用于生产。