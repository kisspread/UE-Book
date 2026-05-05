# ML Deformer Neural Morph Model

> Neural Morph Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、训练 Python 脚本） |
| 模块 | `NeuralMorphModel` (Runtime), `NeuralMorphModelEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel) | |

## 用途

Neural Morph Model 是 UE5 ML Deformer 框架的一个**模型实现**，通过神经网络生成高度压缩的 morph targets 来近似目标变形。它的核心思路是：用神经网络从骨骼旋转和/或动画曲线输入中预测 morph target 权重，从而在运行时实现高质量的网格变形修正。

与基础的 Morph Model 和 Vertex Delta Model 不同，Neural Morph Model 的神经网络**运行在 CPU** 上（通过 NNE / NNERuntimeBasicCpu），但使用 **GPU 端的压缩 morph targets**（需要 Shader Model 5）。这种架构在性能和质量之间取得了良好的平衡。

该模型提供两种工作模式：

- **Local 模式**：每个骨骼/曲线拥有一个独立的小型神经网络，CPU 性能更高，内存占用更低，morph targets 更具局部性
- **Global 模式**：所有骨骼和曲线输入到一个全连接神经网络，CPU 开销稍高，但可能产生更高质量的变形（功能上类似 Vertex Delta Model，但使用 CPU 推理 + GPU 压缩 morph targets）

训练过程通过 Python（借助 `PythonMLPackages` 插件）在编辑器中完成，训练结果以 `.nmn`（Neural Morph Network）自定义二进制格式序列化到 ML Deformer Asset 中。

## 使用场景

- 你的角色使用骨骼动画，但线性蒙皮无法正确表现肌肉膨胀、关节挤压等复杂变形 → 用 Neural Morph Model 训练并修正
- 你需要比 Vertex Delta Model 更高性能的运行时变形修正 → 使用 Local 模式，每个骨骼独立推理
- 多个骨骼协同产生特定变形（如肩部+上臂同时影响腋下区域）→ 定义 Bone Group
- 你需要将变形限制在特定区域，防止左臂旋转影响右臂 → 启用 Bone Masking
- 你希望训练过程快速迭代 → 先用 1000-3000 次迭代测试，最终资产用 10k-1M 次迭代

## 蓝图用法

本插件主要面向编辑器工作流，运行时通过 `UMLDeformerComponent` 自动驱动，不需要手动蓝图操作。以下是可从蓝图访问的关键接口：

### 训练模型节点（`UNeuralMorphTrainingModel`）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Train()` | 主训练函数（Python 实现），返回训练结果 | `UNeuralMorphTrainingModel` |
| `GetNumBoneGroups()` | 获取骨骼组数量 | `UNeuralMorphTrainingModel` |
| `GetNumCurveGroups()` | 获取曲线组数量 | `UNeuralMorphTrainingModel` |
| `GenerateBoneGroupIndices()` | 生成骨骼组索引数组 | `UNeuralMorphTrainingModel` |
| `GenerateCurveGroupIndices()` | 生成曲线组索引数组 | `UNeuralMorphTrainingModel` |
| `GetMorphTargetMasks()` | 获取 morph target 掩码（Local 模式 + Bone Masking 启用时） | `UNeuralMorphTrainingModel` |

### 运行时模型属性（`UNeuralMorphModel`）

所有 `UPROPERTY(EditAnywhere, BlueprintReadWrite)` 的训练参数均可在蓝图中读写：

| 属性 | 默认值 | 说明 |
|---|---|---|
| `Mode` | `Local` | 运行模式：Local（每骨骼独立网络）或 Global（单个全连接网络） |
| `LocalNumMorphTargetsPerBone` | 6 | 每骨骼/曲线/组的 morph target 数量（Local 模式） |
| `GlobalNumMorphTargets` | 128 | 总 morph target 数量（Global 模式） |
| `NumIterations` | 5000 | 训练迭代次数 |
| `LocalNumHiddenLayers` | 1 | 隐藏层数（Local 模式） |
| `LocalNumNeuronsPerLayer` | 6 | 每层神经元数（Local 模式） |
| `GlobalNumHiddenLayers` | 2 | 隐藏层数（Global 模式） |
| `GlobalNumNeuronsPerLayer` | 128 | 每层神经元数（Global 模式） |
| `BatchSize` | 128 | 训练批次大小 |
| `LearningRate` | 0.001 | 学习率 |
| `RegularizationFactor` | 0.0 | 正则化因子（0 = 禁用，最高质量但更高内存） |
| `SmoothLossBeta` | 0.0 | Smooth L1 Loss 的 beta 参数 |
| `bEnableBoneMasks` | false | 启用 per-bone 掩码（仅 Local 模式） |
| `SkinningMode` | `Linear` | 蒙皮模式（Linear 或 DualQuaternion） |

## C++ 用法

### 头文件引入

```cpp
#include "NeuralMorphModel.h"
#include "NeuralMorphNetwork.h"
#include "NeuralMorphModelInstance.h"
#include "NeuralMorphInputInfo.h"
```

### 基本用法 — 查询模型状态

```cpp
// 假设已有一个 UNeuralMorphModel* Model
// 检查模型是否已训练
if (Model->IsTrained())
{
    // 获取运行模式
    ENeuralMorphMode Mode = Model->GetModelMode();
    
    // 获取训练参数
    int32 NumIterations = Model->GetNumIterations();
    float LearningRate = Model->GetLearningRate();
    
    // 获取神经网络
    UNeuralMorphNetwork* Network = Model->GetNeuralMorphNetwork();
    int32 NumBones = Network->GetNumBones();
    int32 NumCurves = Network->GetNumCurves();
    int32 NumOutputs = Network->GetNumOutputs();
}
```

来源：`NeuralMorphModel/Public/NeuralMorphModel.h`

### 运行时推理

```cpp
// 创建模型实例（通常由 UMLDeformerComponent 自动完成）
UNeuralMorphModelInstance* Instance = Cast<UNeuralMorphModelInstance>(
    Model->CreateModelInstance(Component));

// 初始化（绑定骨骼网格体组件）
Instance->Init(SkeletalMeshComponent);

// 设置输入（骨骼变换 + 曲线值 + 归一化）
bool bInputsReady = Instance->SetupInputs();

// 执行推理，更新 morph target 权重
if (bInputsReady)
{
    Instance->Execute(ModelWeight);  // ModelWeight: 0.0 ~ 1.0
}
```

来源：`NeuralMorphModel/Private/NeuralMorphModelInstance.cpp`

### 直接使用神经网络

```cpp
// 获取网络实例
UNeuralMorphNetwork* Network = Model->GetNeuralMorphNetwork();
UNeuralMorphNetworkInstance* NetInstance = Network->CreateInstance();

// 填充输入
TArrayView<float> Inputs = NetInstance->GetInputs();
// ... 填充骨骼旋转和曲线值 ...

// 执行推理
NetInstance->Run();

// 读取输出（morph target 权重）
TArrayView<const float> Outputs = NetInstance->GetOutputs();
```

来源：`NeuralMorphModel/Private/NeuralMorphNetwork.cpp`

### 进阶用法 — 骨骼组与掩码

```cpp
// 获取骨骼组信息
const TArray<FNeuralMorphBoneGroup>& BoneGroups = Model->GetBoneGroups();
for (const FNeuralMorphBoneGroup& Group : BoneGroups)
{
    FName GroupName = Group.GroupName;
    const TArray<FBoneReference>& Bones = Group.BoneNames;
    // ...
}

// 检查骨掩码是否启用
if (Model->IsBoneMaskingEnabled() && 
    Model->GetModelMode() == ENeuralMorphMode::Local)
{
    // 掩码信息存储在 BoneMaskInfoMap 和 BoneGroupMaskInfoMap 中
    const TMap<FName, FMLDeformerMaskInfo>& MaskMap = Model->BoneMaskInfoMap;
}
```

来源：`NeuralMorphModel/Public/NeuralMorphModel.h`, `NeuralMorphTypes.h`

## Demo 示例

### 最小可运行示例 — 读取已训练模型信息

```cpp
// MyNeuralMorphReader.h
#pragma once
#include "CoreMinimal.h"
#include "NeuralMorphModel.h"
#include "NeuralMorphNetwork.h"

class FMyNeuralMorphReader
{
public:
    void ReadModelInfo(UNeuralMorphModel* Model)
    {
        if (!Model || !Model->IsTrained())
        {
            UE_LOG(LogTemp, Warning, TEXT("Model not trained yet."));
            return;
        }

        UNeuralMorphNetwork* Network = Model->GetNeuralMorphNetwork();
        
        UE_LOG(LogTemp, Display, TEXT("Mode: %s"), 
            Model->GetModelMode() == ENeuralMorphMode::Local ? TEXT("Local") : TEXT("Global"));
        UE_LOG(LogTemp, Display, TEXT("Bones: %d, Curves: %d"), 
            Network->GetNumBones(), Network->GetNumCurves());
        UE_LOG(LogTemp, Display, TEXT("Main Inputs: %d, Outputs: %d"), 
            Network->GetNumMainInputs(), Network->GetNumMainOutputs());
        UE_LOG(LogTemp, Display, TEXT("Groups: %d, ItemsPerGroup: %d"), 
            Network->GetNumGroups(), Network->GetNumItemsPerGroup());
        
        if (Network->GetGroupModel())
        {
            UE_LOG(LogTemp, Display, TEXT("Group Inputs: %d, Group Outputs: %d"),
                Network->GetNumGroupInputs(), Network->GetNumGroupOutputs());
        }
    }
};
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "NeuralMorphModel",
    "MLDeformerFramework"
});
```

## 模块依赖

### Runtime 模块 `NeuralMorphModel`

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `MLDeformerFramework` | ML Deformer 框架基类（UMLDeformerMorphModel 等） |
| `NNE` | Neural Network Engine — 神经网络推理框架 |
| `NNERuntimeBasicCpu` | NNE CPU 推理运行时 |
| `GeometryCache` | 几何缓存支持 |
| `ComputeFramework` | 计算框架 |
| `OptimusCore` | Deformer Graph 支持 |
| `RenderCore` / `RHI` | 渲染核心 |

### Editor 模块 `NeuralMorphModelEditor`

| 模块 | 用途 |
|---|---|
| `MLDeformerFrameworkEditor` | ML Deformer 编辑器框架 |
| `NeuralMorphModel` | 对应的 Runtime 模块 |
| `UnrealEd` | 编辑器核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `PropertyEditor` | 属性面板自定义 |
| `DeveloperSettings` | 项目设置基类 |
| `Json` | JSON 序列化 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `GeometryCache` | 几何缓存（训练数据源） |
| `DeformerGraph` | GPU Deformer Graph |
| `PythonMLPackages` | Python 训练环境 |
| `MLDeformerFramework` | ML Deformer 框架 |
| `NNERuntimeBasicCpu` | NNE CPU 推理运行时 |

## 架构详解

### 类层次结构

```
UMLDeformerMorphModel (框架基类)
  └── UNeuralMorphModel              ← 运行时模型，存储训练参数和网络

UMLDeformerMorphModelInstance (框架基类)
  └── UNeuralMorphModelInstance      ← 运行时实例，驱动推理

UMLDeformerMorphModelInputInfo (框架基类)
  └── UNeuralMorphInputInfo          ← 输入信息（骨骼/曲线/组）

UMLDeformerMorphModelVizSettings (框架基类)
  └── UNeuralMorphModelVizSettings   ← 可视化设置（掩码显示模式）

UObject
  └── UNeuralMorphNetwork            ← 神经网络（NNE 模型数据）
      └── UNeuralMorphNetworkInstance ← 网络实例（独立输入/输出缓冲区）

UMLDeformerGeomCacheTrainingModel (框架基类)
  └── UNeuralMorphTrainingModel      ← Python 训练桥接

FMLDeformerMorphModelEditorModel (框架基类)
  └── FNeuralMorphEditorModel        ← 编辑器模型（掩码构建、训练、UI）
```

### 网络架构

在 **Local 模式**下，系统包含两个网络：
- **Main Network**：一个"多模型"（Multi-Model），内含每个骨骼/曲线独立的小型 MLP。输入维度 = `NumBones × 6 + NumCurves × 6`，输出维度 = `NumMorphsPerBone × (NumBones + NumCurves)`
- **Group Network**（可选）：处理骨骼组和曲线组，输入维度 = `NumGroups × 6 × NumItemsPerGroup`

在 **Global 模式**下，只有一个网络：
- 输入维度 = `NumBones × 6 + NumCurves`，输出维度 = `NumMorphTargets`

每个骨骼使用 6 个浮点数表示旋转信息（Local 模式下曲线也用 6 个浮点值，Global 模式下曲线用 1 个）。

### 推理流水线

```
骨骼网格体组件 → 读取骨骼变换 + 动画曲线
    ↓
FillNetworkInputs(): 填充主网络输入缓冲区
    ↓
输入归一化: (input - mean) / std
    ↓
填充 Group Network 输入（如有骨骼组/曲线组）
    ↓
NetworkInstance->Run(): NNE CPU 推理
    ↓
输出 → morph target 权重（含 means morph target）
    ↓
可选: 权重钳制（防止训练外输入导致"爆炸"）
    ↓
应用到 ExternalMorphSet → GPU 压缩 morph targets 渲染
```

### 文件格式

训练输出文件扩展名为 `.nmn`（Neural Morph Network），自定义二进制格式：
- Magic Number: `0x234A1304`
- Version: `1`
- 包含：模式、morph 数量、骨骼/曲线数量、组信息、输入归一化参数（mean/std）、NNE 运行时名称、主网络数据、组网络数据

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-10 | `9803c443cfab` | 为所有含 .gen.cpp 的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME`（代码修复工具批量应用） |
| 2025-06-27 | `6a731b965fd4` | **Bug 修复**：修复在没有选择骨架或找不到骨骼时粘贴骨骼列表导致的崩溃 |
| 2025-06-26 | `ec9009980d52` | 为源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME`（同上批量应用） |

### 维护评价

- **活跃维护** ✅：2025 年 6-7 月仍有实质性更新（包括 crash 修复和代码质量改进）
- **成熟稳定**：自 2022 年 9 月创建以来持续维护，约 4 年历史
- **非实验性**：`IsBetaVersion=false`，`IsExperimentalVersion=false`，`Installed=false`（需手动启用）
- **架构升级**：5.4 版本将推理后端从自定义 MLP 迁移到 NNE（Neural Network Engine），旧格式通过 PostLoad 自动转换
- **5.5 版本变更**：`FNeuralMorphMaskInfo` 已废弃，迁移至框架层的 `FMLDeformerMaskInfo`
- **推荐使用**：作为 Epic 官方的 ML Deformer 模型实现，是角色变形修正的首选方案之一

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [MLDeformerFramework 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
