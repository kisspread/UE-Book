# ML Deformer Vertex Delta Model

> Vertex Delta Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | 否（Installed: false） |
| 包含内容 | 是 |
| 模块 | VertexDeltaModel (Runtime), VertexDeltaModelEditor (Editor) |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕 |
| Beta | 是（IsBetaVersion: true） |
| 平台 | Win64, Linux, Mac |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel) | |

## 用途

VertexDeltaModel 是 ML Deformer 框架的一个**模型实现**，使用**基于 GPU 的神经网络**直接输出每个顶点的位移增量（vertex deltas）。与同框架中的 Neural Morph Model（基于 CPU、生成 morph targets）不同，这个模型：

- 神经网络完全运行在 GPU 上（通过 NNE RDG 接口）
- 不生成 morph targets，而是直接输出顶点 delta 缓冲区
- 输出缓冲区留在 GPU 上，由 Deformer Graph（Optimus）直接消费

本质上它是 ML Deformer 框架的一个**参考实现**，展示如何构建一个纯 GPU 推理的变形模型。在效率上不如 Neural Morph Model（后者虽然跑 CPU 但更高效）。

## 使用场景

- 你需要一个基于深度学习的网格变形方案，且希望推理全在 GPU 上完成以避免 CPU-GPU 数据传输
- 你在研究 ML Deformer 框架的扩展方式，想参考一个完整的 GPU 模型实现
- 你的角色需要高精度的肌肉/布料变形效果，且已有 Geometry Cache 作为 ground truth 训练数据

## 工作原理

1. **训练阶段**（编辑器内）：使用 Skeletal Mesh + Geometry Cache 对训练神经网络，网络学习从骨骼变换/曲线值到顶点位移的映射。训练完成后导出 ONNX 模型。
2. **推理阶段**（运行时）：将骨骼矩阵/曲线浮点数作为输入张量上传 GPU，通过 NNE Runtime（ONNX Runtime DirectML）执行推理，输出的 vertex delta 缓冲区直接被 Deformer Graph 读取并应用到网格上。

### 训练参数（编辑器属性）

| 属性 | 默认值 | 说明 |
|---|---|---|
| `NumHiddenLayers` | 3 | 隐藏层数量（1-10），越大越能处理复杂变形，但性能越差 |
| `NumNeuronsPerLayer` | 256 | 每层神经元数量，越大越灵活但越慢 |
| `NumIterations` | 10000 | 训练迭代次数 |
| `BatchSize` | 128 | 每批训练帧数 |
| `LearningRate` | 0.001 | 学习率（0.000001 - 1.0） |

## C++ 用法

### 头文件引入

```cpp
#include "VertexDeltaModel.h"
#include "VertexDeltaModelInstance.h"
#include "VertexDeltaModelVizSettings.h"
```

### 获取模型和创建实例

```cpp
// 从 ML Deformer Asset 获取 VertexDeltaModel
UMLDeformerAsset* DeformerAsset = LoadObject<UMLDeformerAsset>(nullptr, TEXT("MLDeformerAsset'/Path/To/Asset'"));
UVertexDeltaModel* VertexDeltaModel = Cast<UVertexDeltaModel>(DeformerAsset->GetModel());

// 检查是否已训练
bool bTrained = VertexDeltaModel->IsTrained(); // 检查 NNEModel 是否存在

// 通过 MLDeformerComponent 自动创建 ModelInstance
UMLDeformerComponent* Component = ...; // 已有的组件
UMLDeformerModelInstance* ModelInstance = Component->GetModelInstance();
// 实际类型为 UVertexDeltaModelInstance
```

### 访问 GPU 资源

```cpp
UVertexDeltaModelInstance* Instance = Cast<UVertexDeltaModelInstance>(ModelInstance);

// 获取 NNE RDG 模型实例（用于 Deformer Graph 集成）
UE::NNE::IModelInstanceRDG* NNEInstance = Instance->GetNNEModelInstanceRDG();

// 获取输出的 vertex delta RDG 缓冲区
TRefCountPtr<FRDGPooledBuffer> OutputBuffer = Instance->GetOutputRDGBuffer();
```

### 手动设置 NNE 模型数据

```cpp
UVertexDeltaModel* Model = ...;
TObjectPtr<UNNEModelData> OnnxModelData = ...; // 从 ONNX 文件加载
Model->SetNNEModelData(OnnxModelData);
// 会自动广播 ReinitModelInstance 委托
```

### 编辑器模型（训练）

```cpp
#include "VertexDeltaEditorModel.h"

// 通过工厂方法创建编辑器模型
UE::VertexDeltaModel::FVertexDeltaEditorModel* EditorModel = 
    UE::VertexDeltaModel::FVertexDeltaEditorModel::MakeInstance();

// 训练
ETrainingResult Result = EditorModel->Train();

// 从 ONNX 文件加载已训练的网络
TObjectPtr<UNNEModelData> ModelData = EditorModel->LoadNeuralNetworkFromOnnx(TEXT("path/to/model.onnx"));
```

## Demo 示例

### 最小运行时集成

```cpp
// MyVertexDeltaActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyVertexDeltaActor.generated.h"

class UMLDeformerComponent;
class USkeletalMeshComponent;

UCLASS()
class AMyVertexDeltaActor : public AActor
{
    GENERATED_BODY()
public:
    AMyVertexDeltaActor();

    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* SkeletalMeshComp;

    UPROPERTY(VisibleAnywhere)
    UMLDeformerComponent* MLDeformerComp;
};
```

```cpp
// MyVertexDeltaActor.cpp
#include "MyVertexDeltaActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "MLDeformerComponent.h"

AMyVertexDeltaActor::AMyVertexDeltaActor()
{
    SkeletalMeshComp = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkelMesh"));
    RootComponent = SkeletalMeshComp;

    MLDeformerComp = CreateDefaultSubobject<UMLDeformerComponent>(TEXT("MLDeformer"));
    // 在编辑器中设置 DeformerAsset 指向已训练的 VertexDeltaModel asset
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "MLDeformerFramework"  // 运行时使用
});
```

如果需要在编辑器中训练：
```csharp
PrivateDependencyModuleNames.AddRange(new string[]
{
    "VertexDeltaModel",
    "MLDeformerFrameworkEditor",
    "NNE",
    "NNERuntimeORT"
});
```

## 模块依赖

### Runtime 模块（VertexDeltaModel）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `ComputeFramework` | GPU 计算框架（Deformer Graph） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `GeometryCache` | Geometry Cache 资产支持 |
| `NNE` | 神经网络引擎接口 |
| `NNERuntimeORT` | ONNX Runtime 推理后端 |
| `OptimusCore` | Deformer Graph（Optimus）集成 |
| `Projects` | 插件路径查询 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `MLDeformerFramework` | ML Deformer 基础框架 |

### Editor 模块（VertexDeltaModelEditor）

| 模块 | 用途 |
|---|---|
| `MLDeformerFrameworkEditor` | ML Deformer 编辑器框架 |
| `VertexDeltaModel` | Runtime 模块 |
| `NNE` / `NNERuntimeORT` | 模型训练和加载 |
| `PropertyEditor` | 属性面板自定义 |
| `Slate` / `SlateCore` | UI 框架 |
| `ToolWidgets` | 编辑器工具控件 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `GeometryCache` | 几何缓存资产支持 |
| `NNERuntimeORT` | ONNX Runtime 推理引擎 |
| `DeformerGraph` | Optimus 变形图系统 |
| `PythonMLPackages` | Python ML 包（训练用） |
| `MLDeformerFramework` | ML Deformer 框架 |

运行时需要 Python 包：`onnx==1.14.1`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-25 | `a9573a8` | ComputeFramework: Remove old deprecated functions from compute data providers | Compute Framework 接口清理，跟随框架 API 演进 |
| 2025-06-20 | `35f8ecb` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | Python 依赖管理重构，torch 相关包移至独立插件 |
| 2025-05-09 | `2e8b3a9` | [MLDeformer] Fixed a crash on undo on morph based models. Also changed the icon of the Train button | Bug 修复 + UI 改进 |

### 维护评价

- **创建时间**: 2022 年 9 月，约 3.6 年历史
- **Beta 状态**: `IsBetaVersion=true`，Epic 将其标记为测试阶段
- **维护活跃**: 2025 年仍有实质性更新（bug 修复、框架适配），但更新主要来自 ML Deformer 框架层面的改动
- **定位**: 源码注释明确指出这是"a more as an example of how to implement a model that only uses the GPU"，是参考实现而非生产首选
- **建议**: 适合学习 ML Deformer 框架的 GPU 模型扩展方式。生产环境推荐考虑 Neural Morph Model（更高效）。由于是 Beta 状态，API 可能在未来版本中变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel/Source/VertexDeltaModel/Private/Tests/VertexDeltaModelTest.cpp)（已注释）
