# ML Deformer Framework

> Machine Learning Mesh Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 机器学习变形框架 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MLDeformerFramework` (Runtime), `MLDeformerFrameworkEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework) | |

## 用途

ML Deformer Framework 是 Unreal Engine 5 中**基于机器学习的网格变形运行时框架**。它解决的核心问题是：传统线性蒙皮（Linear Blend Skinning）无法精确还原 DCC 软件中复杂肌肉挤压、布料褶皱、关节弯曲等高保真形变效果。

该框架提供了一套完整的运行时管线，将预先训练好的神经网络模型集成到骨骼网格体的渲染流程中。在运行时，框架会从骨骼组件采集骨骼旋转和动画曲线作为神经网络输入，执行推理后输出顶点偏移或形变权重，从而驱动 Mesh Deformer Graph 实现高质量形变。

框架本身不包含具体模型实现（如 MorphModel），而是定义了基类接口（`UMLDeformerModel`、`UMLDeformerModelInstance`），具体模型如 Morph Model 和 GeometryCache Model 继承自这些基类。它还与 Optimus Compute Framework 深度集成，通过自定义 Compute Data Interface 将骨骼数据和调试数据传递给 GPU Deformer Graph。

**为什么存在**：传统形变方案要么质量不够（纯蒙皮），要么性能太差（逐顶点模拟）。ML Deformer 通过离线训练、运行时推理的方式，在保持实时性能的同时大幅提升了形变质量，特别适用于高保真角色动画场景。

## 使用场景

- 你在制作 AAA 级角色，需要关节处的肌肉挤压、褶皱等高保真效果 → 使用 ML Deformer Morph Model
- 你有 DCC 中的高精度布料/软体模拟数据，想在运行时还原 → 使用 GeometryCache 基础的 ML Deformer
- 你需要在运行时通过蓝图混合 ML 形变效果的强度 → 使用 `UMLDeformerComponent` 的 Weight 参数
- 你需要在 GPU Deformer Graph 中使用 ML 形变数据 → 使用框架提供的 Optimus Data Interface

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetWeight` | 设置 ML 变形权重（0=关闭，1=完全激活） | `UMLDeformerComponent` |
| `GetWeight` | 获取当前 ML 变形权重 | `UMLDeformerComponent` |
| `SetupComponent` | 配置变形器资产和目标骨骼网格体组件 | `UMLDeformerComponent` |
| `SetDeformerAsset` | 设置要使用的 ML Deformer 资产 | `UMLDeformerComponent` |
| `GetDeformerAsset` | 获取当前使用的 ML Deformer 资产 | `UMLDeformerComponent` |
| `GetSkeletalMeshComponent` | 获取被变形的目标骨骼网格体组件 | `UMLDeformerComponent` |
| `FindSkeletalMeshComponent` | 在同一 Actor 上查找与资产兼容的骨骼网格体组件 | `UMLDeformerComponent` |
| `UpdateSkeletalMeshComponent` | 自动查找并设置目标骨骼网格体组件 | `UMLDeformerComponent` |
| `GetModelInstance` | 获取当前模型实例对象 | `UMLDeformerComponent` |
| `SetMorphTargetDeltaFloats` | 从 Python 训练脚本设置形变目标的顶点偏移（浮点数组） | `UMLDeformerMorphModel` |
| `SetMorphTargetDeltas` | 设置形变目标的顶点偏移（Vector3f 数组） | `UMLDeformerMorphModel` |
| `SetMorphTargetsErrorOrder` | 设置形变目标的重要性排序（用于 LOD） | `UMLDeformerMorphModel` |
| `SetMorphTargetsMinMaxWeights` | 设置形变目标权重的最小/最大值范围 | `UMLDeformerMorphModel` |
| `CanDynamicallyUpdateMorphTargets` | 检查是否支持动态更新形变目标 | `UMLDeformerMorphModel` |
| `GetTrainingDevice` | 获取训练使用的设备名称 | `UMLDeformerModel` |

### 使用示例（蓝图描述）

**基本设置流程**：

1. 在 Actor 上添加 `UMLDeformerComponent`
2. 调用 `SetupComponent`，传入 ML Deformer 资产和目标 `SkeletalMeshComponent`
3. 使用 `SetWeight` 控制变形强度（0~1 混合）

**蓝图连接方式**：
- `BeginPlay` → `SetupComponent(MLDeformerAsset, SkeletalMeshComponent)`
- 每帧或按需 → `SetWeight(Alpha)` 控制淡入淡出
- `SetWeight(0.0)` 时，框架会跳过神经网络推理以优化性能

**运行时动态切换资产**：
- 调用 `SetDeformerAsset(NewAsset)`，内部会自动重建模型实例

## C++ 用法

### 头文件引入

```cpp
#include "MLDeformerComponent.h"
#include "MLDeformerAsset.h"
#include "MLDeformerModel.h"
#include "MLDeformerModelInstance.h"
#include "MLDeformerMorphModel.h"
#include "MLDeformerInputInfo.h"
```

### 基本用法

以下示例展示如何在 C++ 中设置和使用 ML Deformer Component：

```cpp
// 在 Actor 中创建并配置 ML Deformer Component
// 来源：基于 MLDeformerComponent.h 的 SetupComponent/Activate 流程

// 假设已有 SkeletalMeshComponent 和 MLDeformerAsset
UMLDeformerComponent* DeformerComp = NewObject<UMLDeformerComponent>(this);
DeformerComp->SetupComponent(MLDeformerAsset, SkeletalMeshComponent);
DeformerComp->RegisterComponent();

// 设置变形权重（0 = 无效果，1 = 完全激活）
DeformerComp->SetWeight(0.8f);

// 获取当前实际使用的权重（包含控制台命令覆盖后的最终值）
float FinalWeight = DeformerComp->GetFinalMLDeformerWeight();
```

### 进阶用法

**兼容性检查**：在应用 ML Deformer 前检查骨骼网格体是否兼容：

```cpp
// 来源：基于 MLDeformerInputInfo.h 的 IsCompatible/GenerateCompatibilityErrorString
UMLDeformerInputInfo* InputInfo = Model->GetInputInfo();
if (!InputInfo->IsCompatible(SkeletalMeshComponent))
{
    FString ErrorText = InputInfo->GenerateCompatibilityErrorString(SkeletalMeshComponent);
    UE_LOG(LogMLDeformer, Warning, TEXT("Compatibility error: %s"), *ErrorText);
}
```

**从 Python 训练脚本设置形变目标数据**：

```cpp
// 来源：MLDeformerMorphModel.h 的 SetMorphTargetDeltaFloats/SetMorphTargetsMinMaxWeights
// 通过反射调用（Python 绑定场景）
UMLDeformerMorphModel* MorphModel = Cast<UMLDeformerMorphModel>(Asset->GetModel());

// 设置形变目标顶点偏移（NumMorphs * NumBaseMeshVerts * 3 个浮点数）
TArray<float> Deltas;
// ... 填充 Deltas 数据 ...
MorphModel->SetMorphTargetDeltaFloats(Deltas);

// 设置每个形变目标权重的训练期间最小/最大值范围
TArray<float> MinValues, MaxValues;
// ... 从训练数据提取 ...
MorphModel->SetMorphTargetsMinMaxWeights(MinValues, MaxValues);

// 设置形变目标重要性排序（用于 LOD 优化）
TArray<int32> MorphTargetOrder;
TArray<float> ErrorValues;
// ... 计算排序 ...
MorphModel->SetMorphTargetsErrorOrder(MorphTargetOrder, ErrorValues);
```

**自定义模型实现**：

```cpp
// 来源：基于 MLDeformerModel.h 和 MLDeformerModelInstance.h 的虚函数接口
// 创建自定义的 ML Deformer 模型
UCLASS()
class UMyCustomMLDeformerModel : public UMLDeformerModel
{
    GENERATED_BODY()
public:
    virtual UMLDeformerModelInstance* CreateModelInstance(UMLDeformerComponent* Component) override
    {
        return NewObject<UMyCustomModelInstance>(Component);
    }
    
    virtual bool IsTrained() const override { return bTrained; }
    virtual FString GetDisplayName() const override { return TEXT("My Custom Model"); }
    virtual int32 GetNumFloatsPerBone() const override { return 6; } // 两个3D向量表示旋转
};

UCLASS()
class UMyCustomModelInstance : public UMLDeformerModelInstance
{
    GENERATED_BODY()
protected:
    // 准备神经网络输入
    virtual bool SetupInputs() override
    {
        // 填充神经网络输入数据
        return true;
    }
    
    // 执行推理
    virtual void Execute(float ModelWeight) override
    {
        // 运行神经网络推理并应用结果
    }
    
    // 权重为零时的优化路径
    virtual void HandleZeroModelWeight() override
    {
        // 将形变目标权重设为零
    }
};
```

**性能监控**：

```cpp
// 来源：MLDeformerPerfCounter.h 和 MLDeformerComponent.h 的 TickPerfCounter
#if WITH_EDITOR
const UE::MLDeformer::FMLDeformerPerfCounter& PerfCounter = DeformerComp->GetTickPerfCounter();
int32 AvgCycles = PerfCounter.GetCyclesAverage();
int32 MaxCycles = PerfCounter.GetCyclesMax();
#endif
```

## Demo 示例

### 基础 ML Deformer 组件使用

```cpp
// MyMLDeformerActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyMLDeformerActor.generated.h"

class UMLDeformerComponent;
class UMLDeformerAsset;
class USkeletalMeshComponent;

UCLASS()
class AMyMLDeformerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMLDeformerActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* MeshComponent;

    UPROPERTY(VisibleAnywhere)
    UMLDeformerComponent* MLDeformerComponent;

    UPROPERTY(EditAnywhere, Category = "ML Deformer")
    TObjectPtr<UMLDeformerAsset> DeformerAsset;

    /** 混合权重的呼吸动画效果 */
    UPROPERTY(EditAnywhere, Category = "ML Deformer")
    float WeightBlendSpeed = 1.0f;
};
```

```cpp
// MyMLDeformerActor.cpp
#include "MyMLDeformerActor.h"
#include "MLDeformerComponent.h"
#include "MLDeformerAsset.h"
#include "Components/SkeletalMeshComponent.h"

AMyMLDeformerActor::AMyMLDeformerActor()
{
    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    MLDeformerComponent = CreateDefaultSubobject<UMLDeformerComponent>(TEXT("MLDeformer"));
}

void AMyMLDeformerActor::BeginPlay()
{
    Super::BeginPlay();

    if (DeformerAsset)
    {
        // 设置 ML Deformer 组件
        MLDeformerComponent->SetupComponent(DeformerAsset, MeshComponent);
        
        // 检查兼容性
        UMLDeformerModelInstance* Instance = MLDeformerComponent->GetModelInstance();
        if (Instance && !Instance->IsCompatible())
        {
            UE_LOG(LogTemp, Warning, TEXT("ML Deformer not compatible: %s"), 
                *Instance->GetCompatibilityErrorText());
        }
    }
}

void AMyMLDeformerActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 使用正弦波混合形变权重，产生呼吸效果
    float Alpha = (FMath::Sin(GetWorld()->GetTimeSeconds() * WeightBlendSpeed) + 1.0f) * 0.5f;
    MLDeformerComponent->SetWeight(Alpha);
}
```

## 模块依赖

从源码推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | Optimus Compute Data Interface 集成，用于 GPU Deformer Graph |
| `OptimusCore` | Compute Data Interface 基类和组件源 |
| `GeometryCache` | GeometryCache 基础模型的目标网格数据 |
| `NeuralNetwork` | CPU 神经网络推理运行时 |
| `RenderCore` | GPU 缓冲区（FVertexBufferWithSRV 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 5.8 版本动画废弃清理，移除过时 API |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 工具化时间线更新，间接影响编辑器集成 |
| 2026-04-06 | `3f81d395` | [ContentBrowser] New Add Menu Animation Menu | 内容浏览器动画菜单重构 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | Deformer Graph 运行时多个修复，直接影响框架 |

### 维护评价

- **创建时间**：2022-09-06，从 Experimental 迁移并标记为 beta
- **近期活跃度**：非常活跃，2026 年 4 月有多次功能性更新和废弃清理
- **维护状态**：**活跃维护中**，持续跟进引擎版本演进
- **已知限制**：
  - `SetQualityLevel` / `GetQualityLevel` 已在 5.4 中废弃
  - `SetMorphTargetsMaxWeights` 已废弃，应使用 `SetMorphTargetsMinMaxWeights`
  - `GenerateCompatibilityErrorString(USkeletalMesh*)` 已在 5.7 中废弃
  - Morph Model 的神经网络默认在 CPU 上运行（`IsNeuralNetworkOnGPU` 返回 false）
- **推荐程度**：✅ **强烈推荐**。这是 Epic 官方维护的 ML 形变核心框架，持续活跃更新，是高质量角色动画的首选方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework/Tests)