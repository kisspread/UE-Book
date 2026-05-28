# ML Deformer Neural Morph Model

> Neural Morph Model for the ML Deformer Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 神经形变模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `NeuralMorphModel` (Runtime), `NeuralMorphModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel) | |

## 用途

`NeuralMorphModel` 是 ML Deformer 框架的一个具体模型实现。它不是通用的动画工具，而是专用于利用机器学习（具体为神经网络）来学习和预测角色网格体（Skeletal Mesh）在骨骼驱动下的复杂形变。

这个插件解决的核心问题是：如何通过数据驱动的方式，自动生成比传统线性蒙皮（LBS）更精确的网格体变形效果。它通过训练一个神经网络模型来学习从骨骼姿态到顶点偏移量的映射关系，从而实现对肌肉膨胀、皮肤滑动等复杂形变的高精度模拟。其存在是为了提升角色动画的视觉保真度，尤其是在特写镜头或高要求项目中。

## 使用场景

- 你在制作一个对角色变形细节要求极高的3A游戏或数字人项目。
- 你需要模拟真实的肌肉运动、脂肪抖动或衣物下的皮肤变形，而标准骨骼动画无法满足要求。
- 你已经使用或计划使用 ML Deformer 框架，并需要一个基于神经网络的可选模型来获得高质量的形变预测。

## 蓝图用法

此插件主要通过 ML Deformer 框架集成使用。在蓝图中，您通常不会直接操作 `NeuralMorphModel` 的内部节点，而是通过 ML Deformer 组件的设置界面来配置和选择该模型。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `设置MLDeformer资产` | 在 ML Deformer 组件上设置包含 NeuralMorphModel 的资产 | `UMLDeformerComponent` |
| `设置MLDeformer输入` | 设置模型的输入数据（如骨骼变换、曲线值） | `UMLDeformerComponent` |

### 使用示例（蓝图描述）

在你的角色蓝图中：
1.  添加一个 `MLDeformerComponent` 到角色的网格体组件下。
2.  在组件详情面板的 “MLDeformer” 分类下，将 “Deformer Asset” 设置为一个预先创建好的 `MLDeformerAsset`。
3.  在资产编辑器中打开该 `MLDeformerAsset`，在 “Model” 下拉菜单中选择 “Neural Morph Model”。
4.  配置模型的训练数据（动画、曲线）和输出目标（待修正的网格体）。
5.  运行训练（在编辑器或通过蓝图/代码）。
6.  游戏运行时，`MLDeformerComponent` 会自动使用训练好的 `NeuralMorphModel` 来修正网格体的变形。

## C++ 用法

在 C++ 层面，主要涉及继承和集成。开发者通常不会直接实例化 `UNeuralMorphModel`，而是通过 ML Deformer 框架的工厂机制或资产类型来使用。

### 头文件引入

```cpp
#include "MLDeformerModel.h"
#include "NeuralMorphModel.h"
```

### 基本用法

以下代码片段展示了如何在一个自定义的 ML Deformer 模型类中继承并可能扩展神经形变模型的功能。这通常用于创建自定义的、基于神经网络的形变逻辑。

```cpp
// 假设你正在创建一个自定义的 ML Deformer 模型，内部使用神经形变逻辑。
// MyCustomDeformerModel.h
#pragma once

#include "CoreMinimal.h"
#include "MLDeformerModel.h"
#include "MyCustomDeformerModel.generated.h"

UCLASS(BlueprintType)
class UMyCustomDeformerModel : public UMLDeformerModel
{
    GENERATED_BODY()

public:
    // 重写框架要求的方法，用于初始化模型
    virtual void InitModel() override;

    // 重写推理函数，这里可以调用神经网络进行预测
    virtual void Predict(const FMLDeformerInputData& InputData, FMLDeformerOutputData& OutputData) override;

private:
    // 内部可以持有 UNeuralMorphModel 的实例或相关推理对象
    // 例如: UNeuralMorphModel* NeuralMorphInstance;
};
```

### 进阶用法

结合 `NeuralMorphModelEditor` 模块，可以在编辑器工具中扩展模型的训练和预览功能。

```cpp
// MyNeuralMorphEditorCustomization.cpp (位于 Editor 模块)
#include "NeuralMorphModelDetails.h"

// 扩展 Neural Morph Model 在细节面板中的显示
class FMyNeuralMorphModelDetails : public FNeuralMorphModelDetails
{
public:
    // 自定义属性展示
    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override
    {
        // 调用父类实现
        FNeuralMorphModelDetails::CustomizeDetails(DetailBuilder);
        
        // 添加自定义的编辑器 UI 或逻辑
        // ...
    }
};
```

## Demo 示例

一个演示如何在自己的模块中引用和初始化神经形变模型基础概念的最小示例。

```cpp
// NeuralMorphDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NeuralMorphDemo.generated.h"

class UNeuralMorphModel;

UCLASS()
class UNeuralMorphDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // 演示函数：检查神经形变模型插件是否可用
    UFUNCTION(BlueprintCallable)
    bool IsNeuralMorphModelAvailable() const;

private:
    // 可以持有模型的引用或工厂信息
};
```

```cpp
// NeuralMorphDemo.cpp
#include "NeuralMorphDemo.h"
#include "NeuralMorphModel.h" // 引入模块头文件
#include "Modules/ModuleManager.h"

void UNeuralMorphDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 确保 NeuralMorphModel 模块已加载
    FModuleManager::Get().LoadModule(TEXT("NeuralMorphModel"));
}

void UNeuralMorphDemoSubsystem::Deinitialize()
{
    Super::Deinitialize();
}

bool UNeuralMorphDemoSubsystem::IsNeuralMorphModelAvailable() const
{
    // 检查核心模块类是否存在，这是判断插件功能是否可用的简单方法
    return UNeuralMorphModel::StaticClass() != nullptr;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MLDeformer` | 神经形变模型所基于的核心 ML Deformer 框架 |
| `AnimGraphRuntime` | 提供动画图运行时支持，用于将模型集成到动画蓝图 |
| `NeuralNetworkInference` | 提供底层的神经网络推理能力（可能被框架隐含依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | UE 5.8 动画废弃代码清理，涉及 MLDeformer 部分，表明插件已适配 5.8。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF，是代码现代化的常见维护操作。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... (Applied to MLDeformer) | 为生成的 .cpp 文件添加内联宏，优化编译，属于性能维护。 |
| 2025-06-27 | `6a731b96` | [MLDeformer] Crash fix when pasting a list of bones in the Neural Morph Model when there is no skele... | 修复了在 Neural Morph Model 中粘贴骨骼列表时，因无骨架导致的崩溃 bug。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... (Applied) | 同 `9803c443`，是批量代码维护的一部分。 |

### 维护评价

该插件自 2022 年创建，至今仍在持续维护。从近期提交记录看（2025年，2026年），维护**活跃**，不仅包括编译器适配（UE 5.8）、代码现代化（日志宏），还有实质性的**bug 修复**（如骨骼列表崩溃问题）。

然而，其创建之初即被标记为 **Beta**，且在后续更新中未发现明确移除 Beta 标记的提交。这意味着该插件功能可能已基本稳定，但仍被 Epic 官方视为“实验性”或“非最终”产品，可能存在未完全暴露的限制或未来接口变动的风险。

**总体推荐**：对于追求前沿、高保真角色动画，且项目处于研发阶段或接受实验性功能的团队，该插件**值得尝试和评估**。对于需要极高稳定性的生产项目，建议密切关注其 Beta 状态变化，并在集成前进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel/Source/NeuralMorphModel/Tests)