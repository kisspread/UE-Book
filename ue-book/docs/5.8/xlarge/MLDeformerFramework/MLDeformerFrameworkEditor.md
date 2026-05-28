# ML Deformer Framework

> Machine Learning Mesh Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | ML 变形器框架 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资产、编辑器UI组件） |
| 模块 | `MLDeformerFramework` (Runtime), `MLDeformerFrameworkEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework) | |

## 用途

ML Deformer Framework 是一个基于机器学习的网格变形框架，允许通过训练神经网络来复制复杂的网格变形效果（如布料模拟、肌肉变形、皮肤褶皱等），并以极低的运行时开销在游戏中实时播放。

核心思路是：用离线的高质量动画数据（来自模拟或动捕）训练一个 ML 模型，然后在游戏中用骨骼变换和动画曲线作为输入，让模型预测顶点偏移量，从而替代昂贵的实时物理模拟或大量的 Morph Target。

**框架本身不包含具体的 ML 算法实现**，它提供的是：
- 模型注册表（Model Registry）机制，用于管理不同类型的 ML 变形器模型
- 编辑器侧的完整工作流（数据采样 → 训练 → 测试对比）
- 与 Python 训练脚本的集成接口
- 丰富的编辑器 UI（时间轴、骨骼/曲线选择器、蒙版配置等）

实际的 ML 模型（如 Neural Morph Model）作为独立插件构建在此框架之上。

## 使用场景

- 你需要将离线布料/肌肉模拟结果烘焙到游戏中，同时保持运行时性能 → 用 ML Deformer
- 你的角色有复杂的面部变形需求，但不想维护数百个 Morph Target → 用 ML Deformer
- 你需要在保持视觉质量的前提下降低顶点数 → 用 ML Deformer 学习高模到低模的变形映射
- 你想自定义 ML 变形器的训练流程或模型架构 → 继承此框架的基类

## 编辑器用法

ML Deformer 是一个**资产编辑器插件**，通过双击 Content Browser 中的 ML Deformer Asset 打开编辑器。

### 资产编辑器核心功能

| 功能 | 说明 |
|---|---|
| 训练模式（Training Mode） | 配置训练数据（源动画 + 目标网格），启动 Python 训练 |
| 测试模式（Testing Mode） | 对比 Linear Skinned / ML Deformed / Ground Truth 三种结果 |
| 模型切换 | 支持注册多种 ML 模型类型，一键切换 |
| 蒙版（Masking） | 通过骨骼/曲线/顶点属性控制变形器影响区域 |
| 时间轴 | 内置时间轴控件，支持逐帧预览和拖拽 |

### 工具菜单扩展

可通过 `FMLDeformerEditorToolkit::AddToolsMenuExtender()` 向编辑器工具菜单添加自定义扩展。

## C++ 用法

### 头文件引入

```cpp
#include "MLDeformerEditorModel.h"           // 编辑器模型基类
#include "MLDeformerEditorToolkit.h"         // 资产编辑器
#include "MLDeformerModelRegistry.h"         // 模型注册表
#include "MLDeformerSampler.h"               // 数据采样器
#include "MLDeformerTrainingModel.h"         // Python 训练模型
#include "MLDeformerMorphModelEditorModel.h" // Morph 模型编辑器
#include "MLDeformerGeomCacheEditorModel.h"  // GeomCache 模型编辑器
```

### 基本用法：注册自定义模型

在你的 Editor 模块中注册自定义 ML 变形器模型类型，使其出现在编辑器 UI 的模型选择列表中：

```cpp
// MyEditorModule.cpp - StartupModule()
#include "MLDeformerEditorModule.h"
#include "MLDeformerModelRegistry.h"

void FMyEditorModule::StartupModule()
{
    UE::MLDeformer::FMLDeformerEditorModule& EditorModule = 
        FModuleManager::LoadModuleChecked<UE::MLDeformer::FMLDeformerEditorModule>("MLDeformerFrameworkEditor");
    
    EditorModule.GetModelRegistry().RegisterEditorModel(
        UMyCustomModel::StaticClass(),                                                    // 运行时模型类型
        UE::MLDeformer::FOnGetEditorModelInstance::CreateStatic(&FMyCustomEditorModel::MakeInstance),  // 编辑器模型工厂
        100  // 优先级（越高越优先，新建资产时默认选择最高优先级的模型）
    );
}

void FMyEditorModule::ShutdownModule()
{
    UE::MLDeformer::FMLDeformerEditorModule& EditorModule = 
        FModuleManager::LoadModuleChecked<UE::MLDeformer::FMLDeformerEditorModule>("MLDeformerFrameworkEditor");
    
    EditorModule.GetModelRegistry().UnregisterEditorModel(UMyCustomModel::StaticClass());
}
```

### 进阶用法：自定义编辑器模型

继承 `FMLDeformerEditorModel`（或其子类如 `FMLDeformerGeomCacheEditorModel` / `FMLDeformerMorphModelEditorModel`）来实现自定义的编辑器交互逻辑：

```cpp
// MyCustomEditorModel.h
#include "MLDeformerGeomCacheEditorModel.h"

class FMyCustomEditorModel : public UE::MLDeformer::FMLDeformerGeomCacheEditorModel
{
public:
    // 必须实现：编辑器模型工厂方法
    static FMLDeformerEditorModel* MakeInstance();
    
    // 可选：自定义采样器
    virtual TSharedPtr<FMLDeformerSampler> CreateSamplerObject() const override;
    
    // 可选：自定义训练流程
    virtual ETrainingResult Train() override;
    
    // 可选：自定义编辑器 Actor
    virtual FMLDeformerEditorActor* CreateEditorActor(
        const FMLDeformerEditorActor::FConstructSettings& Settings) const override;
    
    // 可选：属性变更处理
    virtual void OnPropertyChanged(FPropertyChangedEvent& PropertyChangedEvent) override;
};
```

## Demo 示例

### 自定义 ML Deformer 模型（最小可编译示例）

#### MyMLDeformerModel.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MLDeformer/MLDeformerModel.h"
#include "MyMLDeformerModel.generated.h"

// 运行时模型 - 存储变形器数据和配置
UCLASS(Blueprintable)
class MYPLUGIN_API UMyMLDeformerModel : public UMLDeformerModel
{
    GENERATED_BODY()

public:
    // 自定义模型参数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Training")
    float LearningRate = 0.001f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Training")
    int32 NumEpochs = 100;
};
```

#### MyMLDeformerEditorModel.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MLDeformerGeomCacheEditorModel.h"

class FMyMLDeformerEditorModel : public UE::MLDeformer::FMLDeformerGeomCacheEditorModel
{
public:
    virtual FString GetReferencerName() const override 
    { 
        return TEXT("FMyMLDeformerEditorModel"); 
    }

    static UE::MLDeformer::FMLDeformerEditorModel* MakeInstance()
    {
        return new FMyMLDeformerEditorModel();
    }

    // 自定义训练流程
    virtual ETrainingResult Train() override;
    
    // 自定义属性变更响应
    virtual void OnPropertyChanged(FPropertyChangedEvent& PropertyChangedEvent) override;
};
```

#### MyMLDeformerTrainingModel.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MLDeformerGeomCacheTrainingModel.h"
#include "MyMLDeformerTrainingModel.generated.h"

// Python 训练模型 - 提供 C++ → Python 的训练接口
UCLASS(Blueprintable, MinimalAPI)
class UMyMLDeformerTrainingModel : public UMLDeformerGeomCacheTrainingModel
{
    GENERATED_BODY()

public:
    // 声明 Python 会实现的训练方法
    // 在 Python 中调用时为: train()
    UFUNCTION(BlueprintImplementableEvent, Category = "Training Model")
    int32 Train() const;
};
```

#### MyEditorModule.cpp（注册模型）
```cpp
#include "MLDeformerEditorModule.h"
#include "MLDeformerModelRegistry.h"
#include "MyMLDeformerModel.h"
#include "MyMLDeformerEditorModel.h"

void FMyEditorModule::StartupModule()
{
    auto& Registry = FModuleManager::LoadModuleChecked<UE::MLDeformer::FMLDeformerEditorModule>(
        "MLDeformerFrameworkEditor").GetModelRegistry();
    
    Registry.RegisterEditorModel(
        UMyMLDeformerModel::StaticClass(),
        UE::MLDeformer::FOnGetEditorModelInstance::CreateStatic(
            &FMyMLDeformerEditorModel::MakeInstance),
        10
    );
}

void FMyEditorModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("MLDeformerFrameworkEditor"))
    {
        auto& Registry = FModuleManager::GetModuleChecked<UE::MLDeformer::FMLDeformerEditorModule>(
            "MLDeformerFrameworkEditor").GetModelRegistry();
        Registry.UnregisterEditorModel(UMyMLDeformerModel::StaticClass());
    }
}
```

## 模块依赖

依赖模块需要从 Build.cs 中提取。基于框架的模块结构：

| 模块 | 用途 |
|---|---|
| `MLDeformer` | ML Deformer 运行时核心模块（模型、组件、资产定义） |
| `GeometryCache` | 几何缓存支持，用于地面真值数据的采样和回放 |
| `NeuralNetworkInference` | 神经网络推理模块，用于运行时执行训练好的模型 |
| `ToolWidgets` | 编辑器工具控件（骨骼选择器、曲线选择器等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 清理 MLDeformer 中的废弃动画 API |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | 时间轴工具化初始版本，影响 ML Deformer 编辑器时间轴 |
| 2026-04-06 | `3f81d395` | [ContentBrowser] New Add Menu Animation Menu | Content Browser 动画菜单重构 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | Deformer Graph 运行时修复 |

### 维护评价

**活跃维护**。ML Deformer Framework 自 2022 年从 Experimental 提升以来持续获得更新。最近的改动集中在：
- UE 5.8 的 API 弃用清理（确保前向兼容）
- 与 Sequencer 时间轴工具化的集成
- 编辑器 UI 的持续改进

作为 Epic Games 官方维护的核心动画功能，该框架拥有长期维护保障。框架设计成熟，采用模型注册表 + 编辑器模型分离的架构，具有良好的扩展性。

**注意事项**：
- 该框架需要 Python 环境进行训练，确保安装了 UE 自带的 Python 发行版
- ML Deformer 运行时需要支持 Deformer Graph 的 GPU 后端
- 建议配合 `MLDeformer` 运行时插件一起使用，本框架插件主要提供编辑器和架构支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)