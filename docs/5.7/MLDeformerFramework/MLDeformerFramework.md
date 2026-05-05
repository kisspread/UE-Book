# ML Deformer Framework

> Machine Learning Mesh Deformer Framework

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、训练数据处理器设置） |
| 模块 | `MLDeformerFramework` (Runtime), `MLDeformerFrameworkEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework) | |

## 用途

ML Deformer Framework 是 UE5 的**机器学习网格变形框架**，用于在运行时通过神经网络推理来修正骨骼网格体的变形效果。它解决的核心问题是：**线性蒙皮（LBS）在复杂形变区域（如肩膀、肘部、膝盖）产生的"糖果纸"效果**。

框架本身不包含具体的神经网络实现，而是提供了一套完整的基础设施：

1. **模型抽象层**：定义了 `UMLDeformerModel` 基类，支持多种后端实现（Morph Model、Neural Morph Model 等）
2. **运行时推理管线**：`UMLDeformerComponent` + `UMLDeformerModelInstance` 负责在游戏运行时执行神经网络推理
3. **训练数据管理**：支持 Geometry Cache 作为训练目标，管理动画序列与几何缓存的映射关系
4. **可视化调试系统**：提供热力图、顶点偏移可视化、Ground Truth 对比等调试工具
5. **Compute Framework 集成**：通过 Optimus 数据接口支持 GPU 计算图调试

该框架是 Epic 官方 ML Deformer 编辑器工具的底层引擎，被 `MLDeformer` 主插件所依赖。

## 使用场景

- 你有一个需要高质量肌肉/布料变形的角色 → 使用 ML Deformer 训练并应用变形修正
- 你的角色在肩膀、肘部等关节处出现蒙皮伪影 → 用 ML Deformer 修正这些区域
- 你需要在运行时动态混合 ML 变形效果（如受伤状态）→ 通过 `SetWeight` 控制变形强度
- 你需要为不同平台提供不同质量等级的变形 → 通过 Morph Model 的质量级别系统
- 你需要调试 ML 变形的输入输出 → 使用 Compute Framework 的 Debug Data Interface

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetWeight` | 获取当前 ML 变形权重（0-1） | `UMLDeformerComponent` |
| `SetWeight` | 设置 ML 变形权重，0 为禁用，1 为完全激活 | `UMLDeformerComponent` |
| `GetDeformerAsset` | 获取当前使用的 ML Deformer 资产 | `UMLDeformerComponent` |
| `GetSkeletalMeshComponent` | 获取关联的骨骼网格体组件 | `UMLDeformerComponent` |
| `SetupComponent` | 设置变形器资产和目标骨骼网格体组件 | `UMLDeformerComponent` |
| `CanDynamicallyUpdateMorphTargets` | 检查是否支持动态更新 Morph Target | `UMLDeformerMorphModel` |

### 使用示例（蓝图描述）

**基本用法**：
1. 在角色蓝图中添加 `ML Deformer Component`
2. 设置 `Deformer Asset` 属性为你的 ML Deformer 资产
3. 组件会自动查找匹配的 SkeletalMeshComponent
4. 在运行时通过 `Set Weight` 节点控制变形强度

**动态权重控制**：
1. 获取 `ML Deformer Component` 引用
2. 使用 `Set Weight` 节点，输入 0.0 到 1.0 的浮点值
3. 权重为 0 时会跳过推理计算，节省性能
4. 权重为 1 时完全应用 ML 变形修正

**多角色对比**：
1. 创建多个角色蓝图，每个使用不同的 ML Deformer 资产
2. 在可视化设置中配置 `Compare Actors` 数组
3. 编辑器中可同时预览多个变形效果进行对比

## C++ 用法

### 头文件引入

```cpp
#include "MLDeformerComponent.h"
#include "MLDeformerAsset.h"
#include "MLDeformerModel.h"
#include "MLDeformerModelInstance.h"
#include "MLDeformerInputInfo.h"
```

### 基本用法

```cpp
// 获取角色上的 ML Deformer 组件
UMLDeformerComponent* DeformerComp = Actor->FindComponentByClass<UMLDeformerComponent>();
if (DeformerComp)
{
    // 设置变形权重（0.0 - 1.0）
    DeformerComp->SetWeight(0.8f);
    
    // 获取当前权重
    float CurrentWeight = DeformerComp->GetWeight();
    
    // 获取关联的资产
    UMLDeformerAsset* Asset = DeformerComp->GetDeformerAsset();
    
    // 获取模型实例
    UMLDeformerModelInstance* Instance = DeformerComp->GetModelInstance();
}
```

### 进阶用法

```cpp
// 手动设置组件（用于动态创建）
UMLDeformerComponent* DeformerComp = NewObject<UMLDeformerComponent>(Actor);
DeformerComp->SetupComponent(MyDeformerAsset, SkelMeshComponent);
DeformerComp->RegisterComponent();

// 检查兼容性
UMLDeformerModelInstance* Instance = DeformerComp->GetModelInstance();
if (Instance)
{
    FString ErrorMsg = Instance->CheckCompatibility(SkelMeshComponent, true);
    if (!ErrorMsg.IsEmpty())
    {
        UE_LOG(LogMLDeformer, Warning, TEXT("Compatibility issues: %s"), *ErrorMsg);
    }
}

// 使用性能计数器监控推理时间
UE::MLDeformer::FMLDeformerPerfCounter PerfCounter;
PerfCounter.SetHistorySize(60); // 保存 60 帧历史
PerfCounter.BeginSample();
// ... 执行推理 ...
PerfCounter.EndSample();

int32 AvgCycles = PerfCounter.GetCyclesAverage();
int32 MaxCycles = PerfCounter.GetCyclesMax();
```

## Demo 示例

### 自定义 ML Deformer 模型实例

```cpp
// MyCustomModelInstance.h
#pragma once

#include "MLDeformerModelInstance.h"
#include "MyCustomModelInstance.generated.h"

UCLASS()
class UMyCustomModelInstance : public UMLDeformerModelInstance
{
    GENERATED_BODY()

public:
    // 初始化模型实例
    virtual void Init(USkeletalMeshComponent* SkelMeshComponent) override;
    
    // 每帧更新
    virtual void Tick(float DeltaTime, float ModelWeight) override;
    
    // 检查是否可用于数据提供者
    virtual bool IsValidForDataProvider() const override;

protected:
    // 自定义推理逻辑
    void RunCustomInference(float DeltaTime);
    
    // 存储推理结果
    TArray<FVector3f> DeformedPositions;
};
```

```cpp
// MyCustomModelInstance.cpp
#include "MyCustomModelInstance.h"
#include "MLDeformerModel.h"
#include "SkeletalRenderPublic.h"

void UMyCustomModelInstance::Init(USkeletalMeshComponent* SkelMeshComponent)
{
    Super::Init(SkelMeshComponent);
    
    // 初始化自定义数据
    if (Model)
    {
        int32 NumVertices = Model->GetNumBaseMeshVerts();
        DeformedPositions.SetNum(NumVertices);
    }
}

void UMyCustomModelInstance::Tick(float DeltaTime, float ModelWeight)
{
    Super::Tick(DeltaTime, ModelWeight);
    
    if (ModelWeight > 0.0f)
    {
        RunCustomInference(DeltaTime);
    }
}

bool UMyCustomModelInstance::IsValidForDataProvider() const
{
    return Super::IsValidForDataProvider() && DeformedPositions.Num() > 0;
}

void UMyCustomModelInstance::RunCustomInference(float DeltaTime)
{
    // 获取输入数据
    UMLDeformerInputInfo* InputInfo = Model->GetInputInfo();
    if (!InputInfo) return;
    
    // 收集骨骼变换
    TArray<FTransform> BoneTransforms;
    // ... 从 SkeletalMeshComponent 获取骨骼数据 ...
    
    // 执行自定义推理
    // ... 你的神经网络推理代码 ...
    
    // 应用结果到网格体
    // ... 更新顶点位置 ...
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 几何缓存资产支持，用于存储训练目标网格数据 |
| `ComputeFramework` | GPU 计算框架集成，支持 Optimus 计算图 |
| `OptimusCore` | Optimus 计算数据接口，用于调试数据可视化 |
| `RenderCore` | 渲染资源管理，GPU 缓冲区创建 |
| `RHI` | 渲染硬件接口，用于 GPU 资源操作 |
| `MeshDescription` | 网格描述，用于顶点数据处理 |

## 维护状态

### 近期更新

```
- ef974f9e0ffe MLDeformer: Some fixes where it would not detect curves.
- 7330b2d66672 Refactor of skinning systems to support basic non-Nanite ISKM and AnimBanks for a single LOD. - USE_SKINNING_SCENE_EXTENSION_FOR_NON_NANITE controls whether the feature is enabled. It is DISABLED by default until feature complete. - Bone transforms from the skinning scene extension are plumbed through to the GPU skin vertex factory and replace the existing bone transforms. Currently the old transform buffers are still allocated. - The worst case LOD is allocated for transforms. Non-instanced skinned meshes sub-allocate for the current LOD. ISKM's only use LOD0. - Non-Nanite ISKM's do not support ray tracing yet. - HLSL-2021 is enabled only when the feature define is enabled. A small hack is in place to fix pipeline mismatches between vertex / pixel shaders. - Renamed FSkeletalMeshSceneProxyBase to FSkinningSceneExtensionProxy and used composition instead. This cleans up the inheritance chain and allows for an FInstancedSkinningSceneExtensionProxy variant. - Moved ISKM proxies and mesh objects out of the component cpp. - Non-Nanite bone transforms require a bone map indirection for each section. The single-instance anim provider performs the indirection on the CPU when uploading transforms. The anim bank does it on the GPU using the scatter. Currently only the GPU mode is implemented.
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
```

**解读**：
- `ef974f9e0ffe`：修复了曲线检测的 bug，这是功能性修复
- `7330b2d66672`：大规模重构蒙皮系统，支持非 Nanite 的 ISKM 和 AnimBanks，这是底层架构改进
- `ec9009980d52`：代码生成优化，添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏

### 维护评价

**活跃维护中** ✅

- **创建时间**：2022 年 4 月，约 3 年历史
- **更新频率**：持续有功能性更新和 bug 修复
- **代码质量**：有完善的序列化版本控制、向后兼容性支持、废弃 API 标记
- **文档支持**：有官方文档链接，代码注释详尽
- **测试覆盖**：框架设计支持单元测试（通过 `CheckCompatibility` 等方法）

**推荐使用**：✅ 强烈推荐

这是 Epic 官方维护的核心动画系统组件，用于提升角色变形质量。框架设计成熟，API 稳定，有完善的编辑器工具链支持。适合需要高质量角色变形的项目，特别是 AAA 级游戏角色开发。

**注意事项**：
- 需要配合 ML Deformer 编辑器插件使用（训练、可视化）
- 运行时推理有一定性能开销，需根据目标平台评估
- 部分 API 标记为 `WITH_EDITORONLY_DATA`，仅在编辑器中可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework/Tests)