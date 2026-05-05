# Deformer Graph

> Editor for creating GPU mesh deformation graphs

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、计算着色器资源） |
| 模块 | `OptimusSettings` (Runtime), `OptimusCore` (Runtime), `OptimusDeveloper` (UncookedOnly), `OptimusEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph) | |

---

## 用途

DeformerGraph（内部代号 Optimus）是一个 **基于 GPU 计算着色器的网格变形图编辑系统**。它允许用户通过可视化节点图的方式，编写和组合 GPU Compute Shader 来实时变形骨骼网格体（Skeletal Mesh）。

**核心解决的问题**：传统的 CPU 端网格变形（如 Morph Target、骨骼蒙皮）在处理大量顶点或复杂变形逻辑时性能受限。DeformerGraph 将变形计算完全放到 GPU 上执行，通过 Compute Shader 实现高性能的自定义变形管线。

**为什么存在**：
- 为动画/角色技术美术提供一个 **无需编写 C++ 代码** 即可创建 GPU 变形逻辑的工具
- 与 ControlRig 深度集成，可在动画蓝图管线中无缝插入 GPU 变形步骤
- 基于 ComputeFramework 插件的通用计算框架，支持数据驱动的 GPU 计算调度
- 前身是 Experimental 阶段的 Optimus 插件，2022 年迁出并重命名为 DeformerGraph（参见 UE-162367）

**典型应用场景**：
- 肌肉模拟变形（Muscle Deformation）
- 布料二次变形（Secondary Cloth Motion）
- 程序化身体比例调整
- 任何需要高性能 GPU 端顶点位移的效果

---

## 使用场景

- 你在做一个写实角色，需要基于骨骼驱动的 **肌肉膨胀/收缩效果** → 用 DeformerGraph 创建肌肉变形图
- 你需要在运行时根据游戏逻辑 **动态修改网格顶点**（如受伤凹陷、风吹变形） → 用 DeformerGraph 的变量系统暴露参数给蓝图
- 你的项目使用 ControlRig 做动画，想在骨骼求值后 **插入 GPU 变形步骤** → DeformerGraph 与 ControlRig 管线原生集成
- 你是技术美术，想 **可视化地编写 GPU 变形逻辑** 而不是手写 HLSL → 用 DeformerGraph 的节点编辑器

---

## 模块架构

本插件由 4 个模块组成，职责分明：

| 模块 | 类型 | 职责 |
|---|---|---|
| **OptimusSettings** | Runtime | 运行时设置和配置（PostConfigInit 最早加载） |
| **OptimusCore** | Runtime | 核心运行时逻辑：图定义、节点系统、数据绑定、GPU 调度 |
| **OptimusDeveloper** | UncookedOnly | 开发者工具：仅在编辑器/开发构建中可用，提供调试和开发辅助功能 |
| **OptimusEditor** | Editor | 编辑器 UI：可视化节点图编辑器、属性面板、预览窗口 |

**插件依赖**：
- **ComputeFramework** — 提供通用 GPU 计算调度框架
- **ControlRig** — 提供动画管线集成点

---

## 蓝图用法

DeformerGraph 主要通过 **资产配置 + 动画蓝图集成** 的方式使用，运行时蓝图交互相对有限。

### 核心概念

| 概念 | 说明 |
|---|---|
| **Deformer Graph 资产** | 在内容浏览器中创建的 `.udg` 资产，包含完整的变形图定义 |
| **Data Interface** | 定义 GPU 着色器如何访问引擎数据（骨骼变换、顶点缓冲等） |
| **Kernel Node** | 图中的计算着色器节点，包含实际的 HLSL 变形逻辑 |
| **Variable** | 暴露给蓝图的参数，可在运行时动态修改 |
| **Resource** | 图内部的中间数据（如顶点位移缓冲区） |

### 运行时蓝图交互

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Vector Variable` | 设置图中的向量变量值 | `UOptimusDeformerInstance` |
| `Set Scalar Variable` | 设置图中的标量变量值 | `UOptimusDeformerInstance` |
| `Set Bool Variable` | 设置图中的布尔变量值 | `UOptimusDeformerInstance` |

### 使用示例（蓝图描述）

**在动画蓝图中启用 DeformerGraph**：

1. 打开你的 **Skeletal Mesh** 资产
2. 在 `Deformer Graph` 属性槽中指定你创建的 DeformerGraph 资产
3. 在动画蓝图的事件图表中，通过 `Get Deformer Instance` 获取实例引用
4. 使用 `Set Scalar Variable` / `Set Vector Variable` 节点在运行时修改变形参数

**典型蓝图流程**：
```
Event Tick → Get Deformer Instance → Set Scalar Variable (Name="MuscleFlex", Value=0.7)
```

---

## C++ 用法

### 头文件引入

```cpp
// 核心运行时 API
#include "OptimusDeformer.h"
#include "OptimusDeformerInstance.h"
#include "OptimusComponentSource.h"
#include "OptimusVariableDescription.h"
#include "OptimusResourceDescription.h"

// 数据接口
#include "OptimusDataInterface.h"

// 计算框架集成
#include "ComputeFramework/ComputeGraph.h"
```

### 基本用法 — 获取和操作 Deformer 实例

```cpp
// 在拥有 SkeletalMeshComponent 的 Actor 中
// 来源: OptimusCore 模块运行时绑定逻辑

#include "OptimusDeformer.h"
#include "OptimusDeformerInstance.h"

// 获取骨骼网格体组件上绑定的 DeformerGraph 实例
USkeletalMeshComponent* SkelMeshComp = GetSkeletalMeshComponent();
if (UOptimusDeformerInstance* DeformerInstance = SkelMeshComp->GetDeformerInstance())
{
    // 设置运行时变量
    DeformerInstance->SetScalarVariable(FName("FlexAmount"), 0.5f);
    DeformerInstance->SetVectorVariable(FName("WindDirection"), FVector(1.0f, 0.0f, 0.0f));
}
```

### 进阶用法 — 自定义 Data Interface

```cpp
// 创建自定义 Data Interface 以向 GPU 着色器暴露自定义数据
// 来源: OptimusCore 模块 DataInterface 架构

#include "OptimusComputeDataInterface.h"

// 自定义 Data Interface 需要实现以下接口:
// 1. GetShaderParameters() - 提供着色器参数绑定
// 2. GetSimulatedDataInterfaces() - 提供模拟数据
// 3. 继承 UOptimusComputeDataInterface

UCLASS()
class UMyCustomDataInterface : public UOptimusComputeDataInterface
{
    GENERATED_BODY()

public:
    // 定义着色器参数
    TArray<FOptimusCDIParameterDefinition> GetParameterDefinitions() const override;

    // 获取着色器类引用
    TSubclassOf<UComputeDataProvider> GetProviderClass() const override;
};
```

### 进阶用法 — 自定义 Component Source

```cpp
// Component Source 定义 DeformerGraph 可以作用在什么类型的组件上
// 来源: OptimusCore 模块 ComponentSource 系统

#include "OptimusComponentSource.h"
#include "OptimusComponentSourceBinding.h"

UCLASS()
class UMyComponentSource : public UOptimusComponentSource
{
    GENERATED_BODY()

public:
    // 返回此源支持的组件类
    FName GetBindingName() const override;

    // 从组件提取骨骼数据供 GPU 使用
    bool GetComponentData(
        UActorComponent* InComponent,
        FOptimusComponentDataContext& OutContext
    ) const override;
};
```

---

## Demo 示例

### 最小 DeformerGraph 使用示例

```cpp
// MyDeformerActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDeformerActor.generated.h"

class USkeletalMeshComponent;
class UOptimusDeformer;
class UOptimusDeformerInstance;

UCLASS()
class AMyDeformerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDeformerActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** DeformerGraph 资产引用 */
    UPROPERTY(EditAnywhere, Category = "Deformer")
    TObjectPtr<UOptimusDeformer> DeformerGraph;

    /** 变形强度，暴露给蓝图 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Deformer")
    float DeformStrength = 1.0f;

private:
    UPROPERTY()
    TObjectPtr<USkeletalMeshComponent> SkeletalMeshComp;
};
```

```cpp
// MyDeformerActor.cpp
#include "MyDeformerActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "OptimusDeformer.h"
#include "OptimusDeformerInstance.h"

AMyDeformerActor::AMyDeformerActor()
{
    PrimaryActorTick.bCanEverTick = true;

    SkeletalMeshComp = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = SkeletalMeshComp;
}

void AMyDeformerActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时将 DeformerGraph 绑定到骨骼网格体
    if (DeformerGraph && SkeletalMeshComp)
    {
        SkeletalMeshComp->SetDeformer(DeformerGraph);
    }
}

void AMyDeformerActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 每帧更新变形参数
    if (UOptimusDeformerInstance* Instance = SkeletalMeshComp->GetDeformerInstance())
    {
        Instance->SetScalarVariable(FName("Strength"), DeformStrength);
    }
}
```

---

## 模块依赖

### 插件级依赖

| 插件 | 用途 |
|---|---|
| `ComputeFramework` | 通用 GPU 计算调度框架，DeformerGraph 的 GPU 执行基础 |
| `ControlRig` | 动画蓝图管线集成，提供骨骼数据和动画求值上下文 |

### 模块级依赖（独特依赖）

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | GPU 计算图调度和数据接口抽象 |
| `ControlRig` | 骨骼动画管线集成 |
| `MeshDescription` | 网格体拓扑数据访问 |
| `RenderCore` | 渲染线程资源管理 |
| `RHI` | 底层图形 API 抽象 |
| `ShaderCore` | 着色器编译和参数管理 |

---

## 维护状态

### 近期更新

```
- da92084a122a 优化模块间私有头文件包含和依赖关系
- d5a5a356b9d3 移除当前模块不必要的 Public/Private IncludePaths 条目
- ba14408f3dd8 UE-162367 将 Optimus 插件从 Experimental 迁出并重命名为 DeformerGraph
```

### 维护评价

- **创建时间**：2022-08-30，约 3 年历史
- **状态**：Beta 版本（`IsBetaVersion=true`），默认未启用（`EnabledByDefault=false`）
- **活跃度**：仍在积极维护中，最近的 commit 包含模块依赖优化和从 Experimental 的正式迁移
- **已知限制**：
  - Beta 状态意味着 API 可能在版本间发生变化
  - 需要支持 Compute Shader 的 GPU（SM5+）
  - 默认未启用，需要在插件管理器中手动激活
  - 文档和示例相对有限，学习曲线较陡
- **推荐度**：⭐⭐⭐⭐ — 如果你的项目需要 GPU 端自定义网格变形，这是 Epic 官方提供的唯一解决方案。虽然处于 Beta 阶段，但核心功能已经可用，且有 Epic 持续维护。建议在生产项目中谨慎使用，关注版本更新中的 API 变更。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph)
- [官方文档]()（暂无）