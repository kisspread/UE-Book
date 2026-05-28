# ML Deformer Vertex Delta Model

> Vertex Delta Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 顶点Delta模型 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `VertexDeltaModel` (Runtime), `VertexDeltaModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel) | |

## 用途

VertexDeltaModel 是 **ML Deformer** 框架中的一个具体模型实现。它通过使用**顶点位置差值（Delta）**作为训练目标，来训练一个神经网络模型，该模型能够根据骨骼姿势预测出网格顶点的位移修正量。

简而言之，它解决了一个核心问题：**如何让角色或物体的变形（如肌肉膨胀、布料褶皱）在复杂动画中表现得更加真实和物理正确**。传统骨骼动画仅依靠骨骼权重蒙皮，对于非骨骼关节的形变（如次级动画）往往力不从心。VertexDeltaModel通过机器学习“学习”这些复杂变形，从而在运行时（Runtime）生成高保真度的动画效果。

## 使用场景

*   **你是一名动画师或技术美术（TA）**，需要为角色制作带有复杂肌肉、脂肪或布料次级动画的高质量动画资产，且希望其在不同骨骼姿势下自动、平滑地变形。
*   **你的项目对角色动画的保真度要求极高**（如数字人、高品质写实游戏），标准的骨骼蒙皮无法满足视觉要求。
*   **你已经使用或计划使用 ML Deformer** 作为你的机器学习动画解决方案，并需要一个开箱即用的、基于顶点差值的模型来快速开始。

## 蓝图用法

此插件主要在编辑器中配置资产，在运行时由 ML Deformer 组件自动驱动。核心的蓝图交互通常涉及资产管理和动画蓝图设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMLDeformerAsset` | 获取当前关联的 ML Deformer 资产引用。 | `UMLDeformerComponent` |
| `SetMLDeformerAsset` | 动态设置 ML Deformer 组件要使用的资产（可能包含此模型的训练结果）。 | `UMLDeformerComponent` |

### 使用示例（蓝图描述）

1.  **资产创建与训练**：在内容浏览器中右键，选择“Animation -> ML Deformer Asset”。打开资产后，在细节面板中选择“Model”为 `VertexDeltaModel`。配置训练数据（参考姿势和校正姿势）后，执行训练。
2.  **运行时应用**：将训练好的 ML Deformer 资产拖拽到角色蓝图中的 `ML Deformer` 组件上。在运行时，组件将根据当前骨骼姿势自动调用 VertexDeltaModel 进行推理，修正网格体顶点。

## C++ 用法

### 头文件引入

```cpp
// 核心模型模块
#include "VertexDeltaModel.h"

// 编辑器集成（用于资产自定义等）
#include "VertexDeltaModelEditor.h"
```

### 基本用法

（来源：基于 `VertexDeltaModel` 和 `MLDeformer` 的典型用法逻辑）

```cpp
#include "VertexDeltaModel.h"
#include "MLDeformerModel.h"

// 假设我们有一个 UMLDeformerAsset
UMLDeformerAsset* MyAsset = ...; 

// 获取资产中实际的模型实例（可能是 UVertexDeltaModel）
UMLDeformerModel* Model = MyAsset->GetModel();

// 检查模型是否为我们的 VertexDeltaModel
if (UVertexDeltaModel* VertexDeltaModel = Cast<UVertexDeltaModel>(Model))
{
    // 在此处可以访问 VertexDeltaModel 特有的属性或方法
    // 例如，检查其训练状态或获取其输入/输出数据规格
    // 注意：实际的推理过程通常由 UMLDeformerComponent 在运行时自动管理
}
```

### 进阶用法

进阶用法涉及在编辑器扩展中与模型交互，例如为其添加自定义编辑器 UI 或数据预处理。

```cpp
#include "VertexDeltaModel.h"
#include "MLDeformerEditorModel.h"

// 编辑器模型类，用于扩展资产编辑器
class FVertexDeltaModelEditorModel : public IMLDeformerEditorModel
{
public:
    // 可能重写此方法来为 VertexDeltaModel 提供特定的编辑器详情面板
    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override;
    
    // 可能重写此方法来执行特定的数据验证
    virtual bool IsReadyForTraining() const override;
};
```

## Demo 示例

一个最小化的示例，展示如何通过 C++ 访问一个已存在的 VertexDeltaModel 资产并获取其基础信息。

```cpp
// MyAnimInstance.h
#pragma once
#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

class UMLDeformerAsset;
class UVertexDeltaModel;

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    // 通过蓝图或编辑器设置的资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ML Deformer")
    UMLDeformerAsset* DeformerAsset;

    // 运行时函数，用于调试或信息展示
    UFUNCTION(BlueprintCallable, Category="ML Deformer")
    FString GetVertexDeltaModelInfo() const;
};

// MyAnimInstance.cpp
#include "MyAnimInstance.h"
#include "MLDeformerAsset.h"
#include "MLDeformerModel.h"
#include "VertexDeltaModel.h"

FString UMyAnimInstance::GetVertexDeltaModelInfo() const
{
    if (!DeformerAsset)
    {
        return TEXT("No Deformer Asset assigned.");
    }

    UMLDeformerModel* Model = DeformerAsset->GetModel();
    if (UVertexDeltaModel* VertexDeltaModel = Cast<UVertexDeltaModel>(Model))
    {
        // 假设 UVertexDeltaModel 有一个函数获取其描述
        // return VertexDeltaModel->GetModelDescription();
        return TEXT("This is a Vertex Delta Model.");
    }

    return TEXT("The model in the asset is not a Vertex Delta Model.");
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MLDeformer` | ML Deformer 框架的核心，提供基础模型接口和组件。 |
| `NeuralNetworkInference` | 提供运行时神经网络推理能力。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 清理动画模块废弃代码，涉及 ML Deformer 框架。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | 修复了 Deformer Graph (Optimus) 运行时的多个问题，可能间接受益。 |

### 维护评价

- **状态**：**活跃维护**。
- **依据**：插件创建于2022年，最近一次实质性更新（涉及框架清理和日志迁移）在2026年4月，距今（2026年）不足一年。它作为 ML Deformer 生态的重要组成部分，随着 UE5 主版本更新而同步维护。
- **建议**：**推荐使用**。作为 Epic 官方维护的机器学习动画解决方案的一部分，VertexDeltaModel 具有良好的长期支持和稳定性。尽管标记为 Beta (实验性)，但其基础框架和近期的维护活动表明它是一个成熟且持续改进中的功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel/Tests) (如果存在)