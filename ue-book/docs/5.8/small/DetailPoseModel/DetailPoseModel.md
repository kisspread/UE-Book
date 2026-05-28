# ML Deformer Detail Pose Model

> Detail Pose Model for the ML Deformer Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 细节姿态模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器设置） |
| 模块 | `DetailPoseModel` (Runtime), `DetailPoseModelEditor` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-01-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel) | |

## 用途

该插件是**机器学习（ML）变形器框架**的一个扩展模型。它解决的问题是：基础的机器学习变形器在重建角色动画时，可能会丢失一些关键细节，例如衣服的精细褶皱、皮肤的拉伸细节等。

它的核心思想是：允许用户手动提供一系列“关键细节姿态”（Detail Poses）。在运行时，当检测到角色的当前姿态接近某个预设的关键姿态时，模型会将预先计算好的、用于恢复该姿态下细节的“形态目标”（Morph Target）混合进来，从而在ML重建的基础上“填补”丢失的细节，显著提升变形质量。

本质上，它是 **Neural Morph Model（神经形态模型）** 的高级版本，继承了其所有UI、UX和功能，并在此基础上增加了“细节姿态”这一关键特性。

## 使用场景

- 你正在为角色制作高品质的实时过场动画，发现机器学习变形器生成的服装褶皱不够精细，尤其是在某些特定摆姿（如手臂弯曲、身体扭转）时。 → 用 **Detail Pose Model** 为这些关键姿态补充细节。
- 你的游戏角色在进行高速运动或战斗动作时，模型基于物理模拟或ML重建的皮肤变形出现了不自然的“尖峰”或失真。 → 使用该模型，并利用其内置的**双四元数蒙皮（Dual Quaternion Skinning）**支持来获得更平滑、更真实的变形效果。
- 你已经在使用 Neural Morph Model，但希望在其基础上进一步提升特定关键帧的变形精度。 → 升级到 Detail Pose Model，它提供了与 Neural Morph Model 统一的体验和额外的细节控制能力。

## 蓝图用法

该插件的蓝图节点主要集中在模型配置和运行时实例查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Detail Poses` | 获取当前模型配置的所有细节姿态数据。 | `UDetailPoseModel` |
| `Get Blend Speed` | 获取细节姿态混合的速度。 | `UDetailPoseModel` |
| `Set Blend Speed` | 设置细节姿态混合的速度（0-1）。 | `UDetailPoseModel` |
| `Get Use RBF Blending` | 查询是否使用RBF（径向基函数）进行混合。 | `UDetailPoseModel` |
| `Set Use RBF Blending` | 设置是否使用RBF混合。 | `UDetailPoseModel` |
| `Get RBF Range` | 获取RBF混合的影响范围。 | `UDetailPoseModel` |
| `Set RBF Range` | 设置RBF混合的影响范围。 | `UDetailPoseModel` |
| `Get Best Detail Pose Index` | （运行时）获取当前与角色姿态最匹配的细节姿态在几何缓存中的帧索引。 | `UDetailPoseModelInstance` |

### 使用示例（蓝图描述）

1.  **创建模型资产**：在内容浏览器中右键，创建 `ML Deformer Model`，并选择 `Detail Pose Model` 作为类型。
2.  **配置细节姿态**：在模型资产的编辑器中，在“Detail Poses”类别下，分别指定一个 `AnimSequence` 和一个 `GeometryCache`。这两个资源需要拥有相同的帧率和帧数，每一帧都对应一个你想要保留细节的“关键姿态”。
3.  **调整参数**：
    -   **Blend Speed**：控制细节姿态淡入的速度。设为0则禁用细节姿态，设为1则瞬间切换。
    -   **Use RBF Blending**：勾选以获得更平滑、质量更高的细节姿态间混合，但会增加CPU开销。
    -   **RBF Range**：当启用RBF混合时，此值越大，会同时影响更多相邻的细节姿态，但也会降低GPU性能。
4.  **在运行时查询**：可以通过 `ML Deformer Component` 获取对应的 `Model Instance`，然后调用 `Get Best Detail Pose Index` 来了解当前激活的是哪个细节姿态。

## C++ 用法

### 头文件引入

```cpp
#include "DetailPoseModel.h"
#include "DetailPoseModelInstance.h"
#include "DetailPoseModelInputInfo.h"
```

### 基本用法

该插件主要通过继承和配置来使用。下面的代码展示了如何通过C++获取并设置一个`UDetailPoseModel`的属性。

```cpp
// 假设你已经有一个UDetailPoseModel的指针 DetailPoseModel
UDetailPoseModel* DetailPoseModel = ...; // 从资产或组件获取

// 获取运行时模型实例的混合速度
float CurrentBlendSpeed = DetailPoseModel->GetBlendSpeed();

// 设置混合速度（必须在 0.0 到 1.0 之间）
DetailPoseModel->SetBlendSpeed(0.5f);

// 启用RBF混合以提高质量
DetailPoseModel->SetUseRBFBlending(true);
// 设置RBF混合的影响范围
DetailPoseModel->SetRBFRange(2.0f);

// 访问模型的所有细节姿态数据
const TArray<FDetailPoseModelDetailPose>& DetailPoses = DetailPoseModel->GetDetailPoses();
```

### 进阶用法

在运行时，你可能需要与模型实例交互，获取动画状态。以下代码演示了如何从`UMLDeformerComponent`获取实例并查询当前细节姿态。

```cpp
// 假设你有一个指向角色身上的UMLDeformerComponent的指针
UMLDeformerComponent* DeformerComponent = ...;

// 获取模型实例
UMLDeformerModelInstance* ModelInstance = DeformerComponent->GetModelInstance();
if (UDetailPoseModelInstance* DetailPoseInstance = Cast<UDetailPoseModelInstance>(ModelInstance))
{
    // 查询当前最匹配的细节姿态索引（对应几何缓存的帧号）
    int32 BestFrameIndex = DetailPoseInstance->GetBestDetailPoseIndex();
    UE_LOG(LogTemp, Log, TEXT("Current best matching detail pose frame: %d"), BestFrameIndex);
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建并配置一个 `UDetailPoseModel`。

```cpp
// MyDetailPoseModelActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DetailPoseModel.h"
#include "MyDetailPoseModelActor.generated.h"

UCLASS()
class MYPROJECT_API AMyDetailPoseModelActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDetailPoseModelActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UDetailPoseModel> MyDetailPoseModel;
};

// MyDetailPoseModelActor.cpp
#include "MyDetailPoseModelActor.h"
#include "UObject/UObjectGlobals.h"

AMyDetailPoseModelActor::AMyDetailPoseModelActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDetailPoseModelActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时动态创建一个Detail Pose Model实例（通常用于演示或测试）
    MyDetailPoseModel = NewObject<UDetailPoseModel>(this, TEXT("RuntimeDetailPoseModel"));
    
    if (MyDetailPoseModel)
    {
        // 配置模型参数
        MyDetailPoseModel->SetBlendSpeed(0.7f);
        MyDetailPoseModel->SetUseRBFBlending(true);
        MyDetailPoseModel->SetRBFRange(1.5f);
        
        // 在实际使用中，你需要通过编辑器资产来设置 DetailPosesAnimSequence 和 DetailPosesGeomCache。
        // 这里仅演示API调用。
        UE_LOG(LogTemp, Warning, TEXT("Detail Pose Model created with BlendSpeed: %f, RBF: %s"),
            MyDetailPoseModel->GetBlendSpeed(),
            MyDetailPoseModel->GetUseRBFBlending() ? TEXT("True") : TEXT("False"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MLDeformer` | ML Deformer 框架的核心运行时和接口。 |
| `NeuralMorphModel` | 该模型的父类 Neural Morph Model 所在的模块。 |
| `GeometryCache` | 用于存储和播放几何缓存（Detail Pose 的动画数据）。 |
| `AnimationCore` | 提供动画相关的基础工具，如双四元数支持。 |
| `SkeletalMeshDescription` | 处理骨骼网格体数据，用于输入信息处理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-09 | `2e8b3a9b` | [MLDeformer] Fixed a crash on undo on morph based models. Also changed the icon of the Train button. | 修复了基于形态模型的撤销操作崩溃问题，并更换了训练按钮图标。 |
| 2025-04-08 | `4bb2bc8d` | [MLDeformer] Added in-engine tools to help with the creation of training data for ML Deformers. | 新增了引擎内工具，帮助创建ML变形器的训练数据。 |
| 2025-02-11 | `887aa3d9` | [MLDeformer] Fixed a bug where the Neural Morph Model would actually launch the Detail Pose Model. | 修复了神经形态模型会错误启动细节姿态模型的Bug。 |
| 2025-01-10 | `a86d3905` | [MLDeformer] Small PVS static analyzer check fix. | 针对PVS静态分析器的小型修复。 |
| 2025-01-10 | `a5f27226` | [MLDeformer] Added a new Detail Pose Model... | 初始提交，添加了全新的细节姿态模型，替换了最近邻模型。 |

### 维护评价

-   **创建时间**：2025年初创建，是一个较新的插件。
-   **最近更新**：在创建后的4个月内有3次提交，包括初始功能、bug修复和工具改进。最新一次更新在2025年5月。
-   **活跃度**：**活跃维护中**。作为Experimental插件，仍在持续迭代和修复问题。
-   **已知限制**：标记为实验性 (`IsExperimentalVersion: true`)，且默认未安装 (`Installed: false`)，意味着它可能尚未稳定，API和功能在未来版本中可能会发生变化。
-   **推荐**：如果你正在使用ML Deformer框架，并且对动画质量有极高要求，需要修复特定的变形细节缺陷，**推荐尝试使用**此模型。但鉴于其实验性状态，建议在非核心项目或原型开发中使用，并关注后续版本更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel)
-   [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/) (ML Deformer 基础文档)