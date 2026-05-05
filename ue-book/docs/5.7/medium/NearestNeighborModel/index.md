# ML Deformer Nearest Neighbor Model (DEPRECATED)

> Nearest Neighbor Model for the ML Deformer Framework. This model has been deprecated. Please use the Detail Pose Model instead.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 依赖、着色器） |
| 模块 | `NearestNeighborModel` (Runtime), `NearestNeighborModelEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-16 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/NearestNeighborModel) | |

> **⚠️ 已废弃 (5.4)**：此插件已被标记为 DEPRECATED，请使用 **Detail Pose Model** 替代。

## 用途

NearestNeighborModel 是 ML Deformer 框架的一种专用模型实现，用于通过**最近邻搜索 + 线性基底**的方式实时驱动布料等次级动画变形。其核心思想是：

1. 将网格顶点变形分解为 **PCA 基底线性组合**（低频主成分）+ **最近邻残差偏移**（高频细节）
2. 神经网络预测 PCA 系数，再用这些系数在预计算的 ROM（Range of Motion）数据库中搜索最近邻帧
3. 总顶点偏移公式：`vertex_delta = mean_delta + basis * coeff + nearest_neighbor_delta`
4. 为防止帧间突变，应用时间衰减滤波：`vertex_delta(t) = decay * vertex_delta(t-1) + (1 - decay) * vertex_delta`

这使得布料变形既受骨骼姿态驱动（通过网络预测），又能保持训练数据中的高频褶皱细节（通过最近邻匹配）。

## 使用场景

- 你用 ML Deformer 框架训练了角色布料变形效果 → 用此模型替代默认的 Morph Model，获得更真实的褶皱细节
- 你的角色有多个独立布料区域（如衬衫+裤子），需要分别搜索最近邻 → 将网格划分为多个 Section
- 你需要在运行时实时推断布料变形（游戏、虚拟人等）→ 此模型通过 NNE (Neural Network Engine) 运行优化网络
- 你想用 K-Means 聚类从大量训练帧中选取代表性姿态作为 ROM 数据集

## 架构总览

```
UNearestNeighborModel (UMLDeformerMorphModel)
├── TArray<UNearestNeighborModelSection*> Sections  ← 每个 Section 对应一个布料区域
│   ├── NeighborPoses (UAnimSequence)      ← ROM 姿态动画
│   ├── NeighborMeshes (UGeometryCache)    ← ROM 几何缓存
│   ├── PCA Basis / Vertex Mean             ← 线性基底
│   └── Neighbor Coeffs / Offsets           ← 最近邻系数与残差偏移
└── UNearestNeighborOptimizedNetwork       ← 推断用神经网络 (NNE)

UNearestNeighborModelInstance (UMLDeformerMorphModelInstance)
├── OptimizedNetworkInstance               ← 网络实例
├── PreviousWeights                        ← 上一师权重（用于衰减滤波）
└── DistanceBuffer                         ← 最近邻距离缓冲
```

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumSections` | 获取 Section 数量 | `UNearestNeighborModel` |
| `GetSectionPtr` | 获取指定索引的 Section 指针 | `UNearestNeighborModel` |
| `GetPCACoeffStarts` | 获取每个 Section 的 PCA 系数起始偏移 | `UNearestNeighborModel` |
| `GetTotalNumBasis` | 所有 Section 的基底总数 | `UNearestNeighborModel` |
| `IsReadyForTraining` | 模型是否已准备好训练 | `UNearestNeighborModel` |
| `IsReadyForInference` | 模型是否已准备好推断 | `UNearestNeighborModel` |
| `DoesUsePCA` | 是否使用 PCA 基底模式 | `UNearestNeighborModel` |
| `GetNumBasis` | 获取 Section 的基底数量 | `UNearestNeighborModelSection` |
| `GetVertexMap` | 获取 Section 的顶点映射 | `UNearestNeighborModelSection` |
| `GetVertexWeights` | 获取 Section 的顶点权重 | `UNearestNeighborModelSection` |
| `GetBasis` | 获取 Section 的 PCA 基底数据 | `UNearestNeighborModelSection` |
| `GetVertexMean` | 获取 Section 的顶点均值 | `UNearestNeighborModelSection` |
| `GetAssetNeighborCoeffs` | 获取 Section 的最近邻系数 | `UNearestNeighborModelSection` |
| `Reset` | 重置模型实例状态 | `UNearestNeighborModelInstance` |
| `Eval` | 用指定输入数据运行推断（Python 用） | `UNearestNeighborModelInstance` |

### 使用示例（蓝图描述）

**获取模型的 Section 信息：**
1. 获取 ML Deformer Component → 获取 Model 资产
2. Cast 到 `UNearestNeighborModel`
3. 调用 `GetNumSections` 获取 Section 数量
4. 循环调用 `GetSectionPtr` 获取每个 Section
5. 从 Section 获取 `GetNumBasis`、`GetVertexMap`、`GetVertexWeights` 等信息

**重置运行时实例：**
1. 获取 `UNearestNeighborModelInstance`
2. 调用 `Reset()` → 清除上一帧的衰减权重，防止切换姿态时产生残留

## C++ 用法

### 头文件引入

```cpp
#include "NearestNeighborModel.h"
#include "NearestNeighborModelInstance.h"
#include "NearestNeighborModelInputInfo.h"
#include "NearestNeighborOptimizedNetwork.h"
```

### 基本用法 — 获取模型 Section 信息

来源：`NearestNeighborModel.h` / `NearestNeighborModel.cpp`

```cpp
// 获取 NearestNeighborModel（假设已通过 ML Deformer 框架获取）
UNearestNeighborModel* NNModel = Cast<UNearestNeighborModel>(MLDeformerModel);
if (!NNModel) return;

// 检查模型是否已准备好
if (!NNModel->IsReadyForInference())
{
    UE_LOG(LogTemp, Warning, TEXT("Model not ready for inference"));
    return;
}

// 遍历所有 Section
for (int32 i = 0; i < NNModel->GetNumSections(); ++i)
{
    const UNearestNeighborModelSection& Section = NNModel->GetSection(i);
    
    int32 NumBasis = Section.GetNumBasis();
    int32 NumVertices = Section.GetNumVertices();
    int32 NumNeighbors = Section.GetRuntimeNumNeighbors();
    
    UE_LOG(LogTemp, Log, TEXT("Section %d: Basis=%d, Verts=%d, Neighbors=%d"),
        i, NumBasis, NumVertices, NumNeighbors);
}
```

### 基本用法 — 运行推断实例

来源：`NearestNeighborModelInstance.cpp`

```cpp
// 创建模型实例
UNearestNeighborModelInstance* Instance = NNModel->CreateModelInstance(Component);
Instance->Init(SkeletalMeshComponent);

// 每帧 Tick（由 ML Deformer Component 自动调用）
// Tick 内部流程：
// 1. SetupInputs() — 从骨骼姿态提取输入、裁剪到训练范围
// 2. Execute()     — 运行 NNE 网络推断
// 3. RunNearestNeighborModel() — 最近邻搜索 + 时间衰减

// 手动重置（切换角色或姿态时）
Instance->Reset();
```

### 进阶用法 — 训练模型（Python 交互）

来源：`NearestNeighborTrainingModel.h`

```cpp
// 训练模型通过 Python 蓝图实现事件驱动
// UNearestNeighborTrainingModel 提供了以下 BlueprintImplementableEvent：

// 1. Train() — 训练神经网络
int32 Result = TrainingModel->Train();

// 2. UpdateNearestNeighborData() — 更新最近邻数据
int32 UpdateResult = TrainingModel->UpdateNearestNeighborData();

// 3. KmeansClusterPoses() — K-Means 聚类选取代表性姿态
int32 ClusterResult = TrainingModel->KmeansClusterPoses(KMeansData);

// 4. GetNeighborStats() — 获取最近邻统计信息
bool StatsResult = TrainingModel->GetNeighborStats(StatsData);
```

### 进阶用法 — 自定义采样

来源：`NearestNeighborGeomCacheSampler.h`

```cpp
// 自定义采样器可以使用自定义的 AnimSequence 和 GeometryCache
FNearestNeighborGeomCacheSampler Sampler;
Sampler.Customize(CustomAnimSequence, CustomGeometryCache);

// 按帧采样
bool bSuccess = Sampler.CustomSample(FrameIndex);

// 获取网格索引缓冲
TArray<uint32> IndexBuffer = Sampler.GetMeshIndexBuffer();
```

### 进阶用法 — 网络推断（Python Eval）

来源：`NearestNeighborModelInstance.cpp`

```cpp
// 通过 Eval 函数进行慢速推断（主要用于 Python 测试）
TArray<float> InputData;
InputData.SetNum(InputDim);
// ... 填充输入数据 ...

TArray<float> OutputData = ModelInstance->Eval(InputData);
// OutputData 包含网络预测的 PCA 系数
```

## 核心算法详解

### 1. 推断流程（每帧）

```
骨骼姿态 → BoneRotations → ComputeNetworkInput → 网络输入
    ↓
NNE 推断 → PCA 系数 (OutputView)
    ↓
对每个 Section:
  ├── 提取该 Section 的系数切片
  ├── 计算与所有最近邻的距离平方
  ├── 选择最近邻（或 RBF 加权多个近邻）
  └── 应用时间衰减滤波
    ↓
Morph Weights → 外部 Morph Set → 网格变形
```

### 2. 时间衰减

```cpp
// DecayCoeff = (e^((DecayFactor-1)*DeltaTime + Delta0) - 1) / (e^Delta0 - 1)
// 当 DecayFactor=1 时无衰减；DecayFactor=0 时完全淡出
// 默认 DecayFactor=0.85，让褶皱"粘附"一段时间
```

### 3. 最近邻选择模式

- **最近邻模式**（默认）：选择距离最近的 1 个邻居，权重为 `NearestNeighborOffsetWeight`
- **RBF 模式**（`bUseRBF=true`）：使用高斯径向基函数混合多个邻居，`exp(-d²/σ²)` 加权，结果更平滑

### 4. Section 权重图创建方式

| 方法 | 说明 |
|---|---|
| `FromText` | 从文本解析顶点索引（如 "2, 3, 5-8, 9"） |
| `SelectedBones` | 使用选中骨骼的蒙皮权重 |
| `VertexAttributes` | 使用网格的 float 顶点属性 |
| `ExternalTxt` | 从外部 .txt 文件加载权重（每行一个 float） |

## Demo 示例

### 最小 C++ 推断示例

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core" });
PrivateDependencyModuleNames.AddRange(new string[]
{
    "NearestNeighborModel",
    "MLDeformerFramework",
    "Engine",
    "CoreUObject"
});
```

**NearestNeighborDemo.h：**
```cpp
#pragma once
#include "CoreMinimal.h"

class FNearestNeighborDemo
{
public:
    void RunInference(class UNearestNeighborModel* Model, 
                      class USkeletalMeshComponent* SkelComp);
};
```

**NearestNeighborDemo.cpp：**
```cpp
#include "NearestNeighborDemo.h"
#include "NearestNeighborModel.h"
#include "NearestNeighborModelInstance.h"
#include "Components/SkeletalMeshComponent.h"

void FNearestNeighborDemo::RunInference(
    UNearestNeighborModel* Model, USkeletalMeshComponent* SkelComp)
{
    if (!Model || !SkelComp) return;

    // 检查模型状态
    if (!Model->IsReadyForInference())
    {
        UE_LOG(LogTemp, Error, TEXT("Model not ready"));
        return;
    }

    // 创建实例（通常由 ML Deformer Component 自动管理）
    UMLDeformerModelInstance* BaseInstance = Model->CreateModelInstance(nullptr);
    UNearestNeighborModelInstance* NNInstance = 
        Cast<UNearestNeighborModelInstance>(BaseInstance);
    
    NNInstance->Init(SkelComp);

    // 模拟一帧 Tick
    float DeltaTime = 1.0f / 30.0f;
    float ModelWeight = 1.0f;
    NNInstance->Tick(DeltaTime, ModelWeight);

    // 清理
    NNInstance->Reset();
}
```

## 模块依赖

### Runtime 模块 (NearestNeighborModel)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `ComputeFramework` | GPU 计算框架 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `GeometryCache` | 几何缓存资产 |
| `MLDeformerFramework` | ML Deformer 基础框架 |
| `MeshDescription` | 网格描述 |
| `NNE` | Neural Network Engine（运行时神经网络推理） |
| `NNERuntimeBasicCpu` | NNE CPU 运行时后端 |
| `OptimusCore` | Deformer Graph 支持 |
| `Projects` | 插件项目接口 |
| `RHI` | 渲染硬件接口 |
| `RenderCore` | 渲染核心 |
| `SkeletalMeshDescription` | 骨骼网格描述 |

### Editor 模块 (NearestNeighborModelEditor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `EditorFramework` / `UnrealEd` | 编辑器框架 |
| `CoreUObject` / `Engine` | 核心运行时 |
| `Slate` / `SlateCore` / `InputCore` | UI 框架 |
| `MLDeformerFramework` / `MLDeformerFrameworkEditor` | ML Deformer 编辑器支持 |
| `NearestNeighborModel` | 对应的 Runtime 模块 |
| `PropertyEditor` | 属性编辑器自定义 |
| `ToolWidgets` | 工具窗口控件 |
| `SkeletalMeshDescription` | 骨骼网格描述 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `GeometryCache` | 存储 ROM 几何缓存 |
| `ComputeFramework` | GPU 计算 |
| `DeformerGraph` | 运行时变形图 |
| `PythonMLPackages` | Python ML 依赖管理 |
| `MLDeformerFramework` | ML Deformer 基础 |
| `NNERuntimeBasicCpu` | CPU 神经网络推理 |

### Python 依赖

- `scikit-learn==1.2.1` — K-Means 聚类、PCA 等 ML 算法
- `joblib==1.2.0` — 并行计算
- `threadpoolctl==3.1.0` — 线程池控制

## 编辑器工具

### K-Means 聚类工具

`UNearestNeighborKMeansData` — 从大量训练帧中选取代表性姿态：

- **输入**：多组 AnimSequence + 可选 GeometryCache、聚类数量、必须包含的帧
- **输出**：提取后的 AnimSequence（和可选 GeometryCache）
- **用途**：从完整的 Range of Motion 动画中选取 N 个代表性帧作为最近邻数据集

### 统计工具

`UNearestNeighborStatsData` — 分析最近邻搜索质量：

- **输入**：测试 AnimSequence、Section 索引
- **用途**：评估最近邻覆盖度和误差

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-08-28 | `7330b2d` | 重构蒙皮系统支持非 Nanite ISKM，影响此插件的底层渲染路径 |
| 2025-07-10 | `9803c44` | 代码维护：添加 `UE_INLINE_GENERATED_CPP_BY_NAME` |
| 2025-06-26 | `ec90098` | 同上，批量代码修复 |

### 维护评价

- **状态**：⚠️ **已废弃 (DEPRECATED)**
- 插件从 5.4 版本开始被标记为废弃，建议使用 **Detail Pose Model** 替代
- 最近的实质性更新集中在 2025 年中，主要是编译修复和框架重构（非功能更新）
- 大量旧 API（`FClothPartData`、`UNearestNeighborOptimizedNetworkLoader`、网络层级类）已标记为 `UE_DEPRECATED(5.4, ...)`
- 网络推断已从自定义实现迁移到 NNE (Neural Network Engine) 框架
- **不推荐新项目使用**，已有项目应计划迁移到 Detail Pose Model

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/NearestNeighborModel)
- [官方文档 — ML Deformer](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [父插件 — MLDeformerFramework](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
