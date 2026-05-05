# ML Deformer Framework

> Machine Learning Mesh Deformer Framework

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MLDeformerFramework` (Runtime), `MLDeformerFrameworkEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework) | |

---

## 用途

ML Deformer Framework 是一个**机器学习网格变形框架**，为 UE5 提供基于 ML 的骨骼网格体变形基础设施。它解决的核心问题是：**如何用机器学习模型来驱动骨骼网格体的顶点偏移，从而实现比传统蒙皮更高质量的变形效果**（如肌肉膨胀、布料褶皱、面部微表情等）。

该插件本身是一个**框架层**，不包含具体的 ML 模型实现，而是提供：

1. **运行时基类**（`UMLDeformerModel`、`UMLDeformerComponent`）——定义模型数据格式和运行时变形逻辑
2. **编辑器基础设施**（`FMLDeformerEditorModel`、`FMLDeformerEditorToolkit`）——提供资产编辑器、可视化调试、训练数据采样
3. **训练数据处理工具**（`FTrainingDataProcessor`）——从动画序列中提取最优帧、重混姿态
4. **采样器框架**（`FMLDeformerSampler`、`FMLDeformerGeomCacheSampler`）——采样骨骼旋转、曲线值、顶点偏移
5. **模型注册表**（`FMLDeformerEditorModelRegistry`）——允许第三方插件注册自定义 ML 模型类型

具体的 ML 模型实现（如 Neural Morph Model、Vertex Delta Model 等）在其他插件中，它们继承此框架的基类。

---

## 使用场景

- 你需要用机器学习来驱动高质量的骨骼网格体变形（肌肉、布料、面部） → 使用此框架作为基础，配合具体的 ML 模型插件
- 你要开发自定义的 ML 变形模型 → 继承 `UMLDeformerModel` 和 `FMLDeformerEditorModel`，注册到模型注册表
- 你需要从动画序列中提取最优训练帧 → 使用 Training Data Processor 工具
- 你需要在编辑器中可视化 ML 变形效果、对比 Ground Truth → 使用内置的编辑器视口和可视化设置
- 你要为 ML 变形准备输入数据（骨骼旋转、曲线值、顶点偏移） → 使用 `FMLDeformerSampler` 采样框架

---

## 蓝图用法

该插件主要面向 C++ 扩展，蓝图可调用 API 较少。以下是暴露给蓝图的核心节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateBasicInputsAndOutputBuffers` | 采样所有输入帧并生成训练输入/输出缓冲区文件 | `UMLDeformerGeomCacheTrainingModel` |

### 使用示例（蓝图描述）

该插件的蓝图 API 主要用于训练流程自动化。典型用法是在 Python 训练脚本中通过蓝图调用 `GenerateBasicInputsAndOutputBuffers` 来导出训练数据：

1. 获取 `UMLDeformerGeomCacheTrainingModel` 实例
2. 调用 `GenerateBasicInputsAndOutputBuffers`，传入输入文件路径和输出文件路径
3. 该函数会遍历所有训练动画帧，采样骨骼旋转和顶点偏移，写入文件

---

## C++ 用法

### 头文件引入

```cpp
// 运行时框架
#include "MLDeformerModel.h"
#include "MLDeformerComponent.h"

// 编辑器框架
#include "MLDeformerEditorModel.h"
#include "MLDeformerEditorToolkit.h"
#include "MLDeformerModelRegistry.h"

// 采样器
#include "MLDeformerSampler.h"
#include "MLDeformerGeomCacheSampler.h"

// 训练数据处理
#include "MLDeformerTrainingDataProcessorSettings.h"
```

### 基本用法：注册自定义 ML 模型

这是扩展此框架最核心的操作。你需要创建运行时模型类和编辑器模型类，然后注册到模型注册表。

```cpp
// MyMLModel.h - 自定义运行时模型
#pragma once
#include "MLDeformerModel.h"
#include "MyMLModel.generated.h"

UCLASS(Blueprintable)
class UMyMLModel : public UMLDeformerModel
{
    GENERATED_BODY()
public:
    // 实现你的模型特有属性和逻辑
    UPROPERTY(EditAnywhere, Category = "Settings")
    float MyCustomParam = 1.0f;
};
```

```cpp
// MyMLEditorModel.h - 自定义编辑器模型
#pragma once
#include "MLDeformerEditorModel.h"

class FMyMLEditorModel : public FMLDeformerEditorModel
{
public:
    static FMLDeformerEditorModel* MakeInstance()
    {
        return new FMyMLEditorModel();
    }
    
    // 覆盖编辑器模型的虚函数以提供自定义行为
    virtual void Init(const InitSettings& Settings) override
    {
        FMLDeformerEditorModel::Init(Settings);
        // 自定义初始化
    }
};
```

```cpp
// 在编辑器模块的 StartupModule 中注册
void FMyMLEditorModule::StartupModule()
{
    FMLDeformerEditorModule& Module = FModuleManager::GetModuleChecked<FMLDeformerEditorModule>("MLDeformerFrameworkEditor");
    Module.GetModelRegistry().RegisterEditorModel(
        UMyMLModel::StaticClass(),
        FOnGetEditorModelInstance::CreateStatic(&FMyMLEditorModel::MakeInstance),
        0  // 优先级，最高优先级的模型在创建新资产时默认选中
    );
}

void FMyMLEditorModule::ShutdownModule()
{
    FMLDeformerEditorModule& Module = FModuleManager::GetModuleChecked<FMLDeformerEditorModule>("MLDeformerFrameworkEditor");
    Module.GetModelRegistry().UnregisterEditorModel(UMyMLModel::StaticClass());
}
```

### 基本用法：使用采样器获取训练数据

```cpp
#include "MLDeformerSampler.h"
#include "MLDeformerEditorModel.h"

// 创建采样器并初始化
TSharedPtr<UE::MLDeformer::FMLDeformerSampler> Sampler = EditorModel->CreateSamplerObject();
Sampler->Init(EditorModel, /*AnimIndex=*/ 0);

// 设置采样空间（预蒙皮空间用于训练，后蒙皮空间用于可视化）
Sampler->SetVertexDeltaSpace(UE::MLDeformer::EVertexDeltaSpace::PreSkinning);

// 采样某一帧
const int32 FrameIndex = 10;
Sampler->Sample(FrameIndex);

// 获取采样结果
const TArray<float>& BoneRotations = Sampler->GetBoneRotations();    // NumBones * 6 floats
const TArray<float>& CurveValues = Sampler->GetCurveValues();         // NumCurves floats
const TArray<float>& VertexDeltas = Sampler->GetVertexDeltas();       // NumVerts * 3 floats
const TArray<FVector3f>& SkinnedPositions = Sampler->GetSkinnedVertexPositions();
```

### 进阶用法：使用 Geometry Cache 采样器

```cpp
#include "MLDeformerGeomCacheSampler.h"
#include "MLDeformerGeomCacheEditorModel.h"

// 获取几何缓存编辑器模型
FMLDeformerGeomCacheEditorModel* GeomCacheEditorModel = 
    static_cast<FMLDeformerGeomCacheEditorModel*>(EditorModel);

// 创建几何缓存采样器
TSharedPtr<FMLDeformerGeomCacheSampler> GeomCacheSampler = 
    StaticCastSharedPtr<FMLDeformerGeomCacheSampler>(GeomCacheEditorModel->CreateSamplerObject());

GeomCacheSampler->Init(EditorModel, /*AnimIndex=*/ 0);
GeomCacheSampler->Sample(/*FrameIndex=*/ 0);

// 检查哪些几何缓存轨道无法映射到骨骼网格体
const TArray<FString>& FailedMeshes = GeomCacheSampler->GetFailedImportedMeshNames();
if (FailedMeshes.Num() > 0)
{
    UE_LOG(LogTemp, Warning, TEXT("Failed to map %d geometry cache tracks"), FailedMeshes.Num());
}

// 获取网格映射关系
const TArray<FMLDeformerGeomCacheMeshMapping>& Mappings = GeomCacheSampler->GetMeshMappings();
```

### 进阶用法：训练数据处理器

```cpp
#include "MLDeformerTrainingDataProcessorSettings.h"
#include "Tools/TrainingDataProcessor/TrainingDataProcessor.h"

using namespace UE::MLDeformer::TrainingDataProcessor;

// 获取模型的训练数据处理器设置
UMLDeformerTrainingDataProcessorSettings* Settings = Model->GetTrainingDataProcessorSettings();

// 执行处理：从输入动画中提取最优帧并重混姿态
FTrainingDataProcessor Processor;
bool bSuccess = Processor.Execute(*Settings, Skeleton);
if (bSuccess)
{
    // 输出动画序列已保存到 Settings 中指定的 AnimSequence
}
```

---

## Demo 示例

### 自定义 ML 变形模型最小示例

```cpp
// MyVertexDeltaModel.h
#pragma once
#include "MLDeformerModel.h"
#include "MyVertexDeltaModel.generated.h"

UCLASS(Blueprintable, MinimalAPI)
class UMyVertexDeltaModel : public UMLDeformerModel
{
    GENERATED_BODY()

public:
    UMyVertexDeltaModel();

    // 模型特有属性
    UPROPERTY(EditAnywhere, Category = "Training")
    int32 NumHiddenLayers = 3;

    UPROPERTY(EditAnywhere, Category = "Training")
    int32 HiddenLayerSize = 128;

    // 实现基类要求的接口
    virtual int32 GetNumBones() const override;
    virtual int32 GetNumCurves() const override;
    virtual int32 GetNumMorphTargets() const override { return 0; }
    virtual bool IsValidForTraining() const override;
};
```

```cpp
// MyVertexDeltaModel.cpp
#include "MyVertexDeltaModel.h"

UMyVertexDeltaModel::UMyVertexDeltaModel()
{
    // 设置默认值
    NumHiddenLayers = 3;
    HiddenLayerSize = 128;
}

int32 UMyVertexDeltaModel::GetNumBones() const
{
    // 返回输入骨骼数量
    return InputBones.Num();
}

int32 UMyVertexDeltaModel::GetNumCurves() const
{
    // 返回输入曲线数量
    return InputCurves.Num();
}

bool UMyVertexDeltaModel::IsValidForTraining() const
{
    return UMLDeformerModel::IsValidForTraining() 
        && NumHiddenLayers > 0 
        && HiddenLayerSize > 0;
}
```

```cpp
// MyVertexDeltaEditorModel.h
#pragma once
#include "MLDeformerEditorModel.h"

class FMyVertexDeltaEditorModel : public FMLDeformerEditorModel
{
public:
    static FMLDeformerEditorModel* MakeInstance()
    {
        return new FMyVertexDeltaEditorModel();
    }

    virtual ETrainingResult Train() override
    {
        // 调用 Python 训练脚本
        // ...
        return ETrainingResult::Success;
    }
};
```

```cpp
// MyVertexDeltaEditorModule.cpp - 注册模型
#include "MLDeformerEditorModule.h"
#include "MLDeformerModelRegistry.h"
#include "MyVertexDeltaModel.h"
#include "MyVertexDeltaEditorModel.h"

void FMyVertexDeltaEditorModule::StartupModule()
{
    FMLDeformerEditorModule& MLModule = 
        FModuleManager::GetModuleChecked<FMLDeformerEditorModule>("MLDeformerFrameworkEditor");
    
    MLModule.GetModelRegistry().RegisterEditorModel(
        UMyVertexDeltaModel::StaticClass(),
        FOnGetEditorModelInstance::CreateStatic(&FMyVertexDeltaEditorModel::MakeInstance),
        10  // 较高优先级，创建新资产时默认使用此模型
    );
}

void FMyVertexDeltaEditorModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("MLDeformerFrameworkEditor"))
    {
        FMLDeformerEditorModule& MLModule = 
            FModuleManager::GetModuleChecked<FMLDeformerEditorModule>("MLDeformerFrameworkEditor");
        MLModule.GetModelRegistry().UnregisterEditorModel(UMyVertexDeltaModel::StaticClass());
    }
}
```

---

## 模块依赖

### MLDeformerFramework (Runtime)

无特殊依赖（仅标准 Core/Engine/Slate 等）

### MLDeformerFrameworkEditor (Runtime)

| 模块 | 用途 |
|---|---|
| `MLDeformerFramework` | 运行时框架基类 |
| `GeometryCache` | 几何缓存支持（用于 Ground Truth 采样） |
| `Persona` | 骨骼编辑器基础设施 |
| `AnimationEditor` | 动画编辑器集成 |
| `MeshDescription` | 网格描述操作（顶点属性创建） |
| `ToolMenus` | 编辑器工具菜单注册 |
| `EditorInteractiveToolsFramework` | 交互式工具框架（Paint Mode） |

---

## 维护状态

### 近期更新

```
- ef974f9e0ffe MLDeformer: Some fixes where it would not detect curves.
- 8f822e233652 MLDeformer: Integrate new deferred python initialization and deferred pip installer interfaces
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
```

- `ef974f9e0ffe` 修复了曲线检测问题，属于功能性 bug 修复
- `8f822e233652` 集成了延迟 Python 初始化和延迟 pip 安装器接口，属于架构改进
- `9803c443cfab` 批量添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏，属于编译优化

### 维护评价

**活跃维护**。该插件创建于 2022 年，至今约 3 年，仍在持续更新。近期提交包含功能性修复和架构改进，表明 Epic 仍在积极维护此框架。作为 UE5 ML Deformer 生态系统的核心框架层，它被多个具体 ML 模型插件（如 Neural Morph Model、Vertex Delta Model）所依赖，具有较高的稳定性保障。

**注意事项**：
- 该插件依赖 Python 环境进行 ML 模型训练，需要正确配置 Python 和 pip
- 部分 API 在 5.4 版本中被标记为 `UE_DEPRECATED`，表明框架仍在演进中
- `MLDeformerFrameworkEditor` 模块类型标记为 Runtime 而非 Editor，这可能是有意为之以支持运行时编辑器功能

**推荐使用**：✅ 推荐。如果你需要开发基于 ML 的网格变形功能，这是官方推荐的框架基础。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework/Tests)