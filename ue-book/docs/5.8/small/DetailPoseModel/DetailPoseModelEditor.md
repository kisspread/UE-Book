# ML Deformer Detail Pose Model

> Detail Pose Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 细节姿态模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DetailPoseModel` (Runtime), `DetailPoseModelEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel) | |

## 用途

DetailPoseModel 是 UE5 ML Deformer (机器学习变形器) 框架的一个高级模型。它主要用于解决 ML 重建动画中可能丢失的精细细节（例如衣物褶皱、皮肤褶皱、复杂布料动态）的问题。

该模型的核心思路是：在 ML 变形器基础变形的基础上，允许用户手动提供一些关键细节姿态。在运行时，模型会根据当前骨骼状态找到最接近的关键姿态，并将该姿态对应的细节“混合”回基础变形结果中，从而极大地提升变形的精细度和真实感。

它是 NeuralMorphModel 的一个特化扩展，继承了后者的架构和大部分 UI/UX，因此对于熟悉 Neural Morph Model 的用户来说，学习成本较低。同时，它也引入了对双四元数蒙皮（Dual Quaternion Skinning）的直接支持，这可以改善训练出的变形效果，减少尖刺状的伪影。

## 使用场景

- 你正在使用 ML Deformer 制作高质量的角色动画，但对服装褶皱、肌肉抖动等细节的还原效果不满意。
- 你需要一种方法来手动补充和增强机器学习自动学习到的变形细节。
- 你希望获得比 Nearest Neighbor Model 更统一的用户体验和更强大的基础功能（继承自 Neural Morph Model）。
- 你的角色蒙皮方案适合使用双四元数蒙皮以获得更平滑的变形结果。

## 蓝图用法

本插件的功能主要通过 ML Deformer 资产编辑器进行配置和使用，直接暴露的蓝图节点较少。核心工作流程在编辑器模型和细节面板中完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDetailPoseModel` | 获取与当前编辑器模型关联的运行时 DetailPoseModel 资产。 | `FDetailPoseEditorModel` (C++ 编辑器内部) |
| `Train` | 触发模型训练过程。 | `FDetailPoseEditorModel` (C++ 编辑器内部) |

### 使用示例（蓝图描述）

1.  **在 ML Deformer 资产编辑器中**：创建或编辑一个 ML Deformer 资产，选择 “Detail Pose Model” 作为其变形模型。
2.  **配置细节姿态动画**：在模型设置中，指定一个包含所需关键细节姿态的动画序列和对应的几何缓存。编辑器会提供错误检查（如帧数匹配）。
3.  **训练模型**：点击编辑器内的 “Train” 按钮。训练过程会基于基础骨架和提供的关键细节姿态数据，学习如何将细节混合回基础变形。
4.  **预览**：在编辑器视口中，模型会显示一个独立的 “细节姿态 Actor”（颜色不同于主模型），该 Actor 会实时显示与当前骨骼姿态最匹配的关键细节姿态，以便进行可视化对比和调试。

## C++ 用法

### 头文件引入

```cpp
// 获取运行时模型
#include "DetailPoseModel.h"
// (主要操作在编辑器模型中完成，通常无需直接包含运行时模块头文件)

// 编辑器相关（仅在编辑器模块中可用）
#include "DetailPoseEditorModel.h"
```

### 基本用法

主要通过 `FDetailPoseEditorModel` 类与模型进行交互，它管理着训练、预览和 Actor 创建等核心流程。

```cpp
// 在编辑器上下文中获取 Detail Pose 模型的编辑器实例（通常由 ML Deformer 编辑器管理）
UE::DetailPoseModel::FDetailPoseEditorModel* EditorModel = ...; // 通过工厂方法或已有上下文获取

// 触发训练
ETrainingResult Result = EditorModel->Train();

// 获取关联的运行时模型资产
UDetailPoseModel* RuntimeModel = EditorModel->GetDetailPoseModel();
if (RuntimeModel)
{
    // 可以对运行时模型进行一些查询或设置
}
```
*（来源：基于 `FDetailPoseEditorModel.h` 中的公共接口）*

### 进阶用法

该模型的内部实现涉及关键细节姿态的差值计算和编辑器 Actor 的管理。

```cpp
// 以下为编辑器模型内部逻辑，用于理解其工作原理，通常不作为用户直接调用的 API

// 1. 计算细节姿态差值
TArray<FVector3f> DetailDeltas;
TArray<FDetailPoseModelDetailPose> DetailPoses;
EditorModel->CalculateDetailPoseDeltas(DetailDeltas, DetailPoses);
// DetailDeltas 存储了每个细节姿态的顶点偏移数据
// DetailPoses 存储了每个细节姿态的元信息（如对应的几何缓存帧）

// 2. 创建和更新用于预览的编辑器 Actor
// 在 CreateActors 中会调用 CreateDetailPoseActor
FDetailPoseModelEditorActor* PreviewActor = EditorModel->CreateDetailPoseActor(World);
// 每个 Tick 中会调用 UpdateDetailPoseActor 来更新其显示
EditorModel->UpdateDetailPoseActor(*PreviewActor);
// Actor 会通过 SetTrackedComponent 跟踪 MLDeformerComponent，以同步显示最接近的细节姿态帧。
```
*（来源：`FDetailPoseEditorModel.h` 中的私有方法和 `DetailPoseModelEditorActor.h`）*

## Demo 示例

一个最小化的 C++ 示例，展示如何在编辑器工具或自动化测试中实例化并操作该模型。

```cpp
// DetailPoseModelDemo.h
#pragma once

#include "CoreMinimal.h"

class FDetailPoseModelDemo
{
public:
    void RunDemo();

private:
    // 模拟的编辑器模型实例
    TUniquePtr<UE::DetailPoseModel::FDetailPoseEditorModel> EditorModel;
};

// DetailPoseModelDemo.cpp
#include "DetailPoseModelDemo.h"
#include "DetailPoseEditorModel.h" // 来自 DetailPoseModelEditor 模块
#include "DetailPoseModel.h"       // 来自 DetailPoseModel 模块（运行时模型类）

void FDetailPoseModelDemo::RunDemo()
{
    // 注意：此示例仅用于说明API结构，实际运行需要完整的编辑器上下文和资产。
    // 通常，编辑器模型由 ML Deformer 编辑器框架自动管理。

    // 1. 创建编辑器模型实例 (实际中应通过 FMLDeformerEditorModel::MakeInstance 的注册工厂)
    // EditorModel = MakeUnique<UE::DetailPoseModel::FDetailPoseEditorModel>();
    // EditorModel->Init(/* 需要的参数，如 UMLDeformerModel* */);

    // 2. 检查关联的运行时模型
    if (EditorModel.IsValid())
    {
        UDetailPoseModel* RuntimeModel = EditorModel->GetDetailPoseModel();
        if (RuntimeModel)
        {
            UE_LOG(LogTemp, Log, TEXT("Found DetailPoseModel: %s"), *RuntimeModel->GetName());
        }

        // 3. （概念性）启动训练
        // ETrainingResult TrainResult = EditorModel->Train();
        // if (TrainResult == ETrainingResult::Success)
        // {
        //     UE_LOG(LogTemp, Log, TEXT("Training completed successfully."));
        // }
    }
}
```
*（说明：这是一个概念性示例，实际使用必须在 UE 编辑器模块环境中，并通过正确的资产和工作流进行。）*

## 模块依赖

从插件的 `Plugins` 字段和模块间的继承关系可知，核心依赖如下：

| 模块 | 用途 |
|---|---|
| `MLDeformer` | 基础 ML Deformer 框架，提供核心模型、编辑器和运行时架构。 |
| `NeuralMorphModel` | DetailPoseModel 的直接父模型，提供神经形态变形的基础功能、训练模型和编辑器逻辑。 |
| `GeometryCache` | 用于存储和播放细节姿态的几何缓存动画数据。 |

（注：`Core`, `CoreUObject`, `Engine`, `Slate`, `UMG`, `UnrealEd` 等常见依赖已省略。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-09 | `2e8b3a9b` | [MLDeformer] Fixed a crash on undo on morph based models. Also changed the icon of the Train button. | 修复了基于变形模型的撤销崩溃问题，并更换了训练按钮的图标。 |
| 2025-04-08 | `4bb2bc8d` | [MLDeformer] Added in-engine tools to help with the creation of training data for ML Deformers. Also | 添加了引擎内工具以辅助 ML 变形器训练数据的创建。 |
| 2025-02-11 | `887aa3d9` | [MLDeformer] Fixed a bug where the Neural Morph Model would actually launch the Detail Pose Model. T | 修复了神经形态模型错误启动细节姿态模型的 Bug。 |
| 2025-01-10 | `a86d3905` | [MLDeformer] Small PVS static analyzer check fix. | 修复了 PVS 静态分析检查的小问题。 |
| 2025-01-10 | `a5f27226` | [MLDeformer] Added a new Detail Pose Model. This is a complete rewrite and replacement for the Nearest Neighbor Model... | 初始提交：添加了新的细节姿态模型，作为最近邻模型的完整重写和替代。 |

### 维护评价

- **活跃维护**：该插件于 2025 年 1 月创建，最近一次实质性更新在 2025 年 5 月，距离现在不足一年。
- **功能状态**：作为实验性插件，它已经具备了核心功能（模型定义、编辑器支持、训练），并且正在经历 bug 修复和功能增强（如添加训练辅助工具）。
- **稳定性**：从近期 commit 看，主要集中在修复崩溃和逻辑错误，说明插件在走向稳定的过程中。
- **推荐度**：**推荐在实验性项目中使用**。它代表了 ML Deformer 框架的一个重要进化方向，特别适合追求极高变形精度的用户。但由于其 `Installed` 为 `false` 且处于 `Experimental` 文件夹下，使用前需要在项目设置中手动启用。不建议在核心生产项目中立即采用，除非团队愿意承担实验性功能可能带来的 API 变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel/Tests) *(路径需确认，通常位于插件下的Tests目录)*