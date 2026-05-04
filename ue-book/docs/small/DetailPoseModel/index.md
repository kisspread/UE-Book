# ML Deformer Detail Pose Model

> Detail Pose Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | DetailPoseModel (Runtime), DetailPoseModelEditor (Editor) |
| 创建时间 | 2025-01-10 |
| 年龄标签 | 🆕(≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel) | |

## 用途

Detail Pose Model 是 ML Deformer 框架中的一个高级变形模型，继承自 Neural Morph Model。

它解决的核心问题是：**基础 ML Deformer（Neural Morph Model）在某些特定姿态下无法精确重建细节**——比如衣物褶皱、肌肉挤压等。Detail Pose Model 允许你为这些关键姿态提供"参考帧"，模型会在运行时检测当前姿态是否接近某个参考姿态，如果是，则叠加额外的 morph target 来修正误差。

工作原理：
1. Neural Morph Model 先用神经网络预测基础的 morph target 权重
2. Detail Pose Model 计算神经网络预测与训练数据（ground truth）之间的残差
3. 将残差存储为额外的 morph target（每个 detail pose 一个）
4. 运行时通过最近邻搜索（带 ISPC 加速）找到匹配的 detail pose，用 RBF 或线性插值混合

如果不添加任何 detail pose，模型行为与 Neural Morph Model（Global 模式）完全一致。

## 使用场景

- 你的角色穿着复杂的布料，ML Deformer 在某些姿态下布料变形不够精确 → 用 Detail Pose Model 为这些姿态提供参考帧
- 你需要在特定动作（如蹲下、举手）时保留精细的肌肉/布料变形细节
- 你已经用 Neural Morph Model 获得了不错的整体效果，但某些关键帧仍然有可见误差

**注意**: 此 plugin 是实验性的（`IsExperimentalVersion: true`），需要手动启用。

## 蓝图用法

Detail Pose Model 主要通过 ML Deformer 资产编辑器使用，不直接暴露 BlueprintCallable 函数。以下属性可在编辑器中配置：

### 核心属性（Detail Pose Model 资产）

| 属性 | 说明 | 类型 |
|---|---|---|
| `DetailPosesAnimSequence` | Detail pose 的动画序列（每个关键帧代表一个参考姿态） | `UAnimSequence` |
| `DetailPosesGeomCache` | 对应的 Geometry Cache（与 AnimSequence 帧率和帧数必须一致） | `UGeometryCache` |
| `BlendSpeed` | detail pose 混合速度，0=禁用，1=瞬间切换，默认 0.3 | `float` [0, 1] |
| `bUseRBF` | 是否使用 RBF 插值（更高质量但更耗 CPU），默认 true | `bool` |
| `RBFRange` | RBF 混合范围，越大混合越多 detail pose，GPU 开销越高，默认 1.0 | `float` ≥ 0 |

### 可视化设置（编辑器预览）

| 属性 | 说明 | 类型 |
|---|---|---|
| `DetailPoseWeight` | detail pose 可视化权重，0=不显示，1=完全显示 | `float` [0, 1] |
| `bDrawDetailPose` | 是否绘制最匹配的 detail pose | `bool` |

### 运行时查询

| 方法 | 说明 | 所在类 |
|---|---|---|
| `GetBestDetailPoseIndex()` | 获取当前最匹配的 detail pose 索引（对应 Geometry Cache 的帧号） | `UDetailPoseModelInstance` |

## C++ 用法

### 头文件引入

```cpp
#include "DetailPoseModel.h"
#include "DetailPoseModelInstance.h"
#include "DetailPoseModelInputInfo.h"
```

### 基本用法

```cpp
// 获取 ML Deformer 组件上的 Detail Pose Model Instance
UDetailPoseModelInstance* DetailPoseInstance = Cast<UDetailPoseModelInstance>(MLDeformerComponent->GetModelInstance());
if (DetailPoseInstance)
{
    // 查询当前最匹配的 detail pose 索引
    int32 BestPoseIndex = DetailPoseInstance->GetBestDetailPoseIndex();
}
```

### 配置模型参数

```cpp
UDetailPoseModel* DetailPoseModel = /* 从 MLDeformerAsset 获取 */;

// 设置混合速度
DetailPoseModel->SetBlendSpeed(0.5f);

// 启用 RBF 混合
DetailPoseModel->SetUseRBFBlending(true);
DetailPoseModel->SetRBFRange(1.5f);

// 读取当前配置
float Speed = DetailPoseModel->GetBlendSpeed();
bool bRBF = DetailPoseModel->GetUseRBFBlending();
float Range = DetailPoseModel->GetRBFRange();

// 获取 detail pose 列表
const TArray<FDetailPoseModelDetailPose>& DetailPoses = DetailPoseModel->GetDetailPoses();
for (const FDetailPoseModelDetailPose& Pose : DetailPoses)
{
    // Pose.PoseValues 包含该姿态的神经网络输入值
}
```

## Demo 示例

### Build.cs 依赖配置

```csharp
// 如果你只需要运行时访问（读取模型数据）
PublicDependencyModuleNames.AddRange(new string[]
{
    "DetailPoseModel"
});

// 如果你需要在编辑器中扩展/自定义训练流程
PublicDependencyModuleNames.AddRange(new string[]
{
    "DetailPoseModel",
    "DetailPoseModelEditor"
});
```

### 最小使用示例

```cpp
// MyMLDeformerComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "MyMLDeformerComponent.generated.h"

class UMLDeformerComponent;
class UDetailPoseModelInstance;

UCLASS()
class UMyMLDeformerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditAnywhere)
    UMLDeformerComponent* MLDeformerComponent;

private:
    UPROPERTY()
    UDetailPoseModelInstance* CachedInstance = nullptr;
};
```

```cpp
// MyMLDeformerComponent.cpp
#include "MyMLDeformerComponent.h"
#include "DetailPoseModelInstance.h"
#include "MLDeformerComponent.h"

void UMyMLDeformerComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!CachedInstance && MLDeformerComponent)
    {
        CachedInstance = Cast<UDetailPoseModelInstance>(MLDeformerComponent->GetModelInstance());
    }

    if (CachedInstance)
    {
        int32 BestPose = CachedInstance->GetBestDetailPoseIndex();
        if (BestPose >= 0)
        {
            // 当前正在使用 detail pose，可以做额外的游戏逻辑
            UE_LOG(LogTemp, Log, TEXT("Active detail pose: %d"), BestPose);
        }
    }
}
```

## 模块依赖

### DetailPoseModel（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `NeuralMorphModel` | 父模型，提供基础神经变形功能 |
| `MLDeformerFramework` | ML Deformer 框架核心 |
| `NNE` | Neural Network Engine，神经网络推理 |
| `NNERuntimeBasicCpu` | CPU 端神经网络运行时 |
| `GeometryCache` | Geometry Cache 支持 |
| `OptimusCore` | GPU 计算框架 |
| `ComputeFramework` | 计算框架 |
| `RenderCore` / `RHI` | 渲染基础设施 |

### DetailPoseModelEditor（Editor）

| 模块 | 用途 |
|---|---|
| `DetailPoseModel` | Runtime 模块 |
| `NeuralMorphModel` | Neural Morph Model 运行时 |
| `NeuralMorphModelEditor` | Neural Morph Model 编辑器 |
| `MLDeformerFramework` / `MLDeformerFrameworkEditor` | ML Deformer 框架 |
| `UnrealEd` | 编辑器核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `PropertyEditor` | 属性面板自定义 |
| `ToolWidgets` | 工具控件 |
| `DeveloperSettings` | 开发者设置 |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `NeuralMorphModel` | Detail Pose Model 继承自 Neural Morph Model，必须先启用此 plugin |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-09 | `04ea12a` | Fixed a crash on undo on morph based models. Also changed the icon of the Train button. | Bug 修复：修复撤销操作导致的崩溃，UI 小改动 |
| 2025-04-08 | `4bb2bc8` | Added in-engine tools to help with the creation of training data for ML Deformers. Also added support for Undo/Redo to the ML Deformer asset editor. | 重要功能更新：新增引擎内训练数据创建工具，撤销/重做支持 |
| 2025-02-11 | `887aa3d` | Fixed a bug where the Neural Morph Model would actually launch the Detail Pose Model. Also improved Python imports. | Bug 修复：修复模型类型混淆问题，改进 Python 训练脚本 |

### 维护评价

- **年龄**: 创建于 2025-01-10，至今约 1 年，属于较新的 plugin
- **活跃度**: 活跃维护中，最近一次更新在 2025-05-09，最近 3 个月内有实质性功能更新
- **状态**: 实验性（`IsExperimentalVersion: true`，`Installed: false`），默认不启用
- **稳定性**: 仍有活跃的 bug 修复，说明在实际使用中持续发现问题
- **推荐**: 适合对动画变形质量有高要求的项目使用，但需注意实验性标签意味着 API 可能变化

⚠️ 此 plugin 标记为实验性，API 可能在未来版本中发生变化。建议在使用时做好版本兼容性准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/MLDeformer/DetailPoseModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [父模型 NeuralMorphModel 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/MLDeformer/NeuralMorphModel)
