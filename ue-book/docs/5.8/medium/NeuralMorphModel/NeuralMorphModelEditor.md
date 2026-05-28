# ML Deformer Neural Morph Model

> Neural Morph Model for the ML Deformer Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 神经形态变形模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置） |
| 模块 | `NeuralMorphModel` (Runtime), `NeuralMorphModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel) | |

## 用途

该插件是 **ML Deformer（机器学习变形器）** 框架中的一个具体实现，提供了一种基于神经网络的“形态（Morph）”模型。它解决的核心问题是：如何高效地学习并重现高精度的角色网格变形（如肌肉、布料、复杂的面部动画）。

传统方法可能需要为每一个骨骼或动作组合制作大量的 Blend Shape（混合形状），这在高精度动画中会导致资产臃肿、内存占用高和性能开销大。**Neural Morph Model** 通过训练一个神经网络来学习这些变形关系，能够使用更少的输入（骨骼变换、动画曲线）预测出复杂的顶点位置偏移，从而实现高质量的局部变形效果，同时保持较好的性能。

## 使用场景

- 你需要为你的AAA级角色创建电影级别的精细动画，特别是涉及复杂肌肉扭曲和布料褶皱的部位。
- 你的角色动画师已经创建了高质量的几何体缓存（Geometry Cache）动画，你希望引擎能自动学习并优化这些变形。
- 你希望利用机器学习技术，减少传统 Blend Shape 方案的内存开销，同时保持动画质量。

## 蓝图用法

该插件主要提供**编辑器端**的工具和**运行时训练**蓝图接口。在运行时，其核心功能由 ML Deformer 组件调用，开发者较少直接使用其蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Train` | 调用 Python 训练脚本进行模型训练。需要在蓝图中实现。 | `UNeuralMorphTrainingModel` |
| `GetNumBoneGroups` | 获取当前配置的骨骼组数量。 | `UNeuralMorphTrainingModel` |
| `GetNumCurveGroups` | 获取当前配置的曲线组数量。 | `UNeuralMorphTrainingModel` |
| `GenerateBoneGroupIndices` | 生成骨骼组的索引数组，用于训练。 | `UNeuralMorphTrainingModel` |
| `GenerateCurveGroupIndices` | 生成曲线组的索引数组，用于训练。 | `UNeuralMorphTrainingModel` |
| `GetMorphTargetMasks` | 获取混合形状目标的遮罩数据。 | `UNeuralMorphTrainingModel` |

### 使用示例（蓝图描述）

1.  **训练流程**：在 ML Deformer 编辑器面板中配置好模型后，点击“Train”按钮。这会调用 `UNeuralMorphTrainingModel::Train()` 蓝图事件，你需要在这里实现连接 Python 训练服务的逻辑。
2.  **读取训练结果**：训练完成后，模型会自动加载训练好的神经网络。运行时的 `UMLDeformerComponent` 会使用该网络进行实时变形。

## C++ 用法

该插件的 C++ 使用主要集中在扩展或自定义编辑器模型。

### 头文件引入

```cpp
#include "NeuralMorphModel/NeuralMorphModel.h"
#include "NeuralMorphModelEditor/NeuralMorphEditorModel.h"
```

### 基本用法

以下示例展示了如何获取并初始化 Neural Morph 的编辑器模型。

```cpp
// 来源: NeuralMorphEditorModel.h, NeuralMorphModel.h
#include "NeuralMorphModel/NeuralMorphModel.h"
#include "NeuralMorphModelEditor/NeuralMorphEditorModel.h"

// 假设我们有一个 UNeuralMorphModel* RuntimeModel 指针
UNeuralMorphModel* RuntimeModel = ...; // 通常来自资产

// 获取或创建对应的编辑器模型实例
UE::MLDeformer::FMLDeformerEditorModel* EditorModel = UE::NeuralMorphModel::FNeuralMorphEditorModel::MakeInstance();
if (EditorModel)
{
    // 初始化编辑器模型，传入运行时模型等信息
    FMLDeformerEditorModel::InitSettings Settings;
    Settings.Model = RuntimeModel;
    // ... 设置其他参数
    EditorModel->Init(Settings);

    // 现在可以使用 EditorModel 进行调试绘制、遮罩构建等操作
    // EditorModel->Render(...);
}
```

### 进阶用法

自定义编辑器模型以扩展神经形态模型的行为，例如添加新的输入遮罩生成逻辑。

```cpp
// 创建一个自定义的编辑器模型，继承自 FNeuralMorphEditorModel
class FMyCustomNeuralMorphEditorModel : public UE::NeuralMorphModel::FNeuralMorphEditorModel
{
public:
    // 覆盖初始化函数，添加自定义逻辑
    virtual void Init(const InitSettings& Settings) override
    {
        UE::NeuralMorphModel::FNeuralMorphEditorModel::Init(Settings);
        // 在此处添加自定义初始化代码，例如注册额外的可视化选项
    }

    // 覆盖遮罩生成逻辑
    virtual void GenerateBoneMaskInfos(int32 HierarchyDepth) override
    {
        // 调用父类默认实现
        UE::NeuralMorphModel::FNeuralMorphEditorModel::GenerateBoneMaskInfos(HierarchyDepth);

        // 对生成的遮罩进行后处理...
        // 例如，可以获取模型并修改其遮罩缓冲区
        UNeuralMorphModel* NeuralModel = GetNeuralMorphModel();
        if (NeuralModel)
        {
            TArray<float>& MaskBuffer = NeuralModel->GetInputItemMaskBuffer();
            // ... 自定义处理 MaskBuffer
        }
    }
};

// 注册自定义编辑器模型（通常在模块 Startup 时）
// 在模块的 StartupModule() 中：
// FMLDeformerEditorModule::Get().RegisterEditorModelForModelClass(UNeuralMorphModel::StaticClass(), &FMyCustomNeuralMorphEditorModel::MakeInstance);
```

## Demo 示例

以下是一个最小的自定义神经形态模型编辑器扩展示例。

**MyCustomNeuralMorphEditorModel.h**
```cpp
#pragma once
#include "NeuralMorphModelEditor/NeuralMorphEditorModel.h"

class FMyCustomNeuralMorphEditorModel : public UE::NeuralMorphModel::FNeuralMorphEditorModel
{
public:
    static UE::MLDeformer::FMLDeformerEditorModel* MakeInstance();
    virtual void Init(const InitSettings& Settings) override;
};
```

**MyCustomNeuralMorphEditorModel.cpp**
```cpp
#include "MyCustomNeuralMorphEditorModel.h"

UE::MLDeformer::FMLDeformerEditorModel* FMyCustomNeuralMorphEditorModel::MakeInstance()
{
    return new FMyCustomNeuralMorphEditorModel();
}

void FMyCustomNeuralMorphEditorModel::Init(const InitSettings& Settings)
{
    // 调用基类初始化
    UE::NeuralMorphModel::FNeuralMorphEditorModel::Init(Settings);

    // 添加自定义逻辑，例如在编辑器中显示额外提示
    UE_LOG(LogTemp, Log, TEXT("Custom Neural Morph Editor Model Initialized."));
}
```

## 模块依赖

要使用 `NeuralMorphModel` 插件，你的模块需要依赖以下模块。

| 模块 | 用途 |
|---|---|
| `MLDeformer` | 提供 ML Deformer 框架的核心类和接口（`UMLDeformerModel`, `FMLDeformerEditorModel` 等）。 |
| `NeuralMorphModel` | （运行时模块）提供 `UNeuralMorphModel` 运行时资产类。 |
| `NeuralMorphModelEditor` | （编辑器模块）提供编辑器模型 `FNeuralMorphEditorModel`、细节面板定制和 UI 控件。 |
| `GeometryCache` | （可选）如果使用几何体缓存作为训练目标，可能需要依赖此模块。 |
| `MeshDescription` | 用于处理网格数据，是 ML Deformer 框架的常见依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 针对 UE 5.8 版本进行了废弃 API 的清理工作。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏 UE_LOG 迁移为新的 UE_LOGF 宏。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加了内联生成的 C++ 代码宏，以优化编译。 |
| 2025-06-27 | `6a731b96` | [MLDeformer] Crash fix when pasting a list of bones in the Neural Morph Model when there is no skeleton. | 修复了在神经形态模型中粘贴骨骼列表但未指定骨骼网格体时导致的崩溃。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 与之前类似，添加内联生成宏以优化编译。 |

### 维护评价

该插件创建于 2022 年，属于 **ML Deformer** 框架的一部分，是 Epic Games 的官方功能模块。从 git 记录看，**仍在积极维护中**。最近的提交（截至 2026 年 4 月）主要是针对新引擎版本的兼容性修复（API 清理、宏迁移）和重要的 bug 修复（如崩溃修复）。

- **优点**：官方支持，与引擎深度集成，持续更新以适配新版本。
- **注意点**：插件在 .uplugin 中标记为 `IsBetaVersion` 或 `IsExperimentalVersion`，表明其 API 和功能可能在未来版本中发生变化，使用时需关注版本更新日志。
- **推荐**：对于需要实现高质量、高性能机器学习驱动的角色动画的项目，**强烈推荐使用**。它是 UE5 ML Deformer 生态中的核心组件之一。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/MLDeformer)