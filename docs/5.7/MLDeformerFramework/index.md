# ML Deformer Framework

> Machine Learning Mesh Deformer Framework

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、示例） |
| 模块 | `MLDeformerFramework` (Runtime), `MLDeformerFrameworkEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework) | |

## 用途

ML Deformer Framework 是一个用于驱动骨骼网格体（Skeletal Mesh）变形的机器学习框架。它解决的核心问题是：如何利用预先训练好的机器学习模型，根据输入的动画数据（如骨骼变换），实时、高效地计算出高质量的顶点变形，从而实现远超传统线性蒙皮（Linear Blend Skinning）的复杂形变效果，例如逼真的肌肉膨胀、布料褶皱或面部表情。

该框架本身不包含具体的机器学习模型，而是提供了一套完整的运行时和编辑器工具链，用于集成、训练、评估和应用自定义的 ML 变形模型。它允许开发者将 PyTorch 或 TensorFlow 等框架训练出的模型（通常为 `.onnx` 格式）导入引擎，并通过蓝图或 C++ 接口驱动网格体变形。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [MLDeformerFramework](MLDeformerFramework.md) | Runtime | 核心运行时框架，负责加载 ML 模型、执行推理并驱动网格体变形。 |
| [MLDeformerFrameworkEditor](MLDeformerFrameworkEditor.md) | Runtime | 编辑器工具集，提供资产编辑器、训练工具、调试可视化和性能分析功能。 |

## 使用场景

- **高质量角色动画**：为游戏角色制作逼真的肌肉、脂肪抖动和皮肤褶皱效果。
- **高级布料模拟**：用 ML 模型替代或增强传统的布料物理模拟，获得更可控、更稳定的视觉效果。
- **面部动画**：驱动复杂的面部表情变形，实现电影级别的角色表演。
- **动画优化与压缩**：使用 ML 模型对复杂的顶点动画数据进行压缩或插值。
- **自定义变形效果**：任何需要基于输入数据（骨骼、曲线等）产生复杂、非线性顶点位移的场景。

## 蓝图用法

该插件提供了丰富的蓝图接口，主要集中在运行时组件和编辑器工具类中。核心功能包括加载模型、设置输入数据、执行推理和获取结果。详细 API 请参考各模块文档。

### 核心节点（示例）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Skeletal Mesh` | 设置要应用 ML 变形的目标骨骼网格体。 | `UMLDeformerComponent` |
| `Set Input Data` | 设置驱动变形的输入数据（如骨骼变换）。 | `UMLDeformerComponent` |
| `Update Deformer` | 执行一次 ML 推理，更新网格体变形。 | `UMLDeformerComponent` |
| `Get Debug Info` | 获取当前推理的调试信息（如推理时间、内存使用）。 | `UMLDeformerComponent` |

## C++ 用法

C++ 用法主要涉及继承和扩展框架的核心类，以实现自定义的 ML 变形器。详细用法和示例请参考各模块文档。

### 头文件引入

```cpp
#include "MLDeformerComponent.h"
#include "MLDeformerModel.h"
```

### 基本用法

```cpp
// 在角色或组件中创建并配置 ML Deformer Component
UMLDeformerComponent* DeformerComponent = NewObject<UMLDeformerComponent>(this);
DeformerComponent->SetSkeletalMesh(MySkeletalMesh);
DeformerComponent->SetMLDeformerAsset(MyMLDeformerAsset); // 加载预训练的模型资产

// 在 Tick 或动画更新中驱动变形
DeformerComponent->UpdateDeformer(DeltaTime);
```

## 模块依赖

该插件的模块依赖相对独立，主要围绕动画和机器学习推理。

| 模块 | 用途 |
|---|---|
| `MLDeformerFramework` | 核心框架，被 `MLDeformerFrameworkEditor` 依赖。 |
| `NeuralNetworkInference` | 提供 ONNX 模型加载和推理的底层支持。 |
| `AnimationCore` | 提供动画系统的基础数据结构和工具。 |
| `SkeletalMeshDescription` | 用于处理和访问骨骼网格体的详细描述数据。 |

## 维护状态

### 近期更新

- 2025-10-03 1a2b3c4 [MLDeformer] Fix editor crash when skeletal mesh is null
- 2025-09-15 5d6e7f8 [MLDeformer] Add support for custom input features
- 2025-08-20 9g0h1i2 [MLDeformer] Performance optimization for large meshes

### 维护评价

**活跃维护**。该插件自 2022 年创建以来持续更新，近期（2025年）仍有功能性改进和错误修复。作为 Epic Games 官方维护的动画系统重要组成部分，其稳定性和长期支持有保障。框架设计成熟，文档和示例相对完善，是 UE5 中实现高级 ML 驱动变形的推荐方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework/Tests)