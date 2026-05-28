# Deformer Graph

> Editor for creating GPU mesh deformation graphs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 变形图编辑器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、计算内核资产、材质模板） |
| 模块 | `OptimusSettings` (Runtime), `OptimusCore` (Runtime), `OptimusDeveloper` (Runtime), `OptimusEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph) | |

## 用途

Deformer Graph（原名 Optimus）是一个基于GPU的、可编程的网格变形框架与可视化编辑器。它解决的核心问题是：**在GPU上高效执行复杂的、自定义的顶点动画后处理**。传统基于CPU的动画后处理（如 AnimBP 中的节点）在面对大规模顶点或复杂逻辑时可能成为性能瓶颈。此插件允许开发者通过创建由计算着色器组成的“变形图”，直接在GPU上并行处理成千上万个顶点，实现高性能的程序化动画效果，如布料模拟、肌肉抖动、程序化变形等。

## 使用场景

- **高性能角色特效**：你需要为角色添加基于物理或逻辑的、实时的肌肉膨胀、衣物波动或变形效果，且要求极高的性能。
- **程序化动画系统**：你希望将动画逻辑（如根据速度拉长角色）从CPU转移到GPU，以释放CPU性能。
- **自定义蒙皮后处理**：标准的骨骼蒙皮流程无法满足你的需求，你需要在最终渲染前对顶点位置、法线进行自定义计算。
- **技术美术工具**：技术美术需要一种直观的、节点式的方式来创建和调试复杂的GPU变形效果，而无需直接编写HLSL代码。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Apply Deformer Graph` | 将一个 `UDeformerGraphAsset` 资产应用到指定的 `USkeletalMeshComponent` 上，开始GPU变形计算。 | `UOptimusComponent` |
| `Get Deformer Graph Instance` | 获取与组件关联的当前活动的图表实例，用于查询状态或运行时参数。 | `UOptimusComponent` |
| `Set Deformer Graph Parameter` | 在运行时设置图表中暴露的参数（如向量、浮点数），以动态改变变形效果。 | `UDeformerGraphInstance` |

### 使用示例（蓝图描述）

1.  **准备资产**：在内容浏览器中，右键创建一个 **Deformer Graph** 资产（例如 `DG_CharacterCloth`）。
2.  **创建组件**：在你的角色蓝图中，为 `SkeletalMeshComponent` 添加一个 **Optimus Component**。
3.  **应用图表**：在 `BeginPlay` 事件中，使用 `Apply Deformer Graph` 节点，将 `DG_CharacterCloth` 资产和角色的 `SkeletalMeshComponent` 作为输入连接。
4.  **运行时控制**（可选）：通过 `Set Deformer Graph Parameter` 节点，在游戏运行时（如根据风速变量）动态修改图表中的“风力强度”参数。

## C++ 用法

### 头文件引入

```cpp
#include "OptimusDeformerComponent.h"
```

### 基本用法

创建并应用一个变形图到骨骼网格体组件。

```cpp
// 在你的 Actor 或 Component 类中
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 获取或创建 Optimus 组件
    UOptimusDeformerComponent* DeformerComp = FindComponentByClass<UOptimusDeformerComponent>();
    if (!DeformerComp)
    {
        DeformerComp = NewObject<UOptimusDeformerComponent>(this);
        DeformerComp->RegisterComponent();
    }

    // 加载变形图资产
    UDeformerGraphAsset* DeformerAsset = LoadObject<UDeformerGraphAsset>(nullptr, TEXT("/Game/DG_MyDeformerGraph"));
    
    // 应用图表
    if (DeformerAsset && DeformerComp)
    {
        DeformerComp->SetDeformerGraphAsset(DeformerAsset);
        // 确保它附加到正确的网格体组件上
        DeformerComp->AttachToComponent(GetMesh(), FAttachmentTransformRules::KeepRelativeTransform);
    }
}
```

### 进阶用法

在运行时动态修改图表参数。

```cpp
// 假设你已经通过蓝图或代码持有了 UOptimusDeformerComponent 的引用
UOptimusDeformerComponent* DeformerComp = GetDeformerComponent();

if (DeformerComp && DeformerComp->GetGraphInstance())
{
    // 获取图表实例
    UOptimusGraphInstance* GraphInstance = DeformerComp->GetGraphInstance();
    
    // 查找名为 “WindStrength” 的参数输入端口
    FOptimusParameterBindingId ParamId(FOptimusParameterBindingPath(“WindStrength”));
    
    // 设置新的浮点数值
    GraphInstance->SetFloatValue(ParamId, CurrentWindSpeed);
}
```
*（来源：基于 DeformerGraph 的 API 设计模式推断）*

## Demo 示例

```cpp
// MyDeformerActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OptimusDeformerComponent.h"
#include "MyDeformerActor.generated.h"

UCLASS()
class AMyDeformerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDeformerActor();

    virtual void BeginPlay() override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    USkeletalMeshComponent* MeshComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UOptimusDeformerComponent* DeformerComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    UDeformerGraphAsset* DeformerGraphAsset;
};

// MyDeformerActor.cpp
#include "MyDeformerActor.h"

AMyDeformerActor::AMyDeformerActor()
{
    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = MeshComponent;

    DeformerComponent = CreateDefaultSubobject<UOptimusDeformerComponent>(TEXT("DeformerGraph"));
    // 组件会自动寻找同级的 SkeletalMeshComponent
}

void AMyDeformerActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 在蓝图编辑器中设置好 DeformerGraphAsset 属性后，此处无需额外代码
    // DeformerComponent 会自动应用设置的资产
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | Deformer Graph 的后端执行框架，管理计算着色器的调度和资源绑定。 |
| `OptimusCore` | 插件核心逻辑，包含数据模型、图表编译、参数绑定等。 |
| `OptimusEditor` | 可视化节点编辑器界面，用于创建和编辑变形图。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `43a2c5ff` | Deformer Graph: programmatic component resolver | 新增编程方式的组件解析器功能 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数产生的警告 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases (S... | 为数据接口添加了按计算内核的输出掩码，用于特定情况下的资源访问控制 |
| 2026-04-16 | `004f9e11` | Deformer Graph: ability to look for secondary bindings in parent actors if not found in the componen | 支持在组件中未找到次级绑定时，在父级Actor中查找 |
| 2026-04-14 | `909e5b5b` | [Deformer Graph] Move Mark Deformed to PostSubmit and GetReadableOutputBuffer to Gather dispatch dat | 将“标记已变形”移至后期提交阶段，并将“获取可读输出缓冲区”移至收集调度数据阶段 |

### 维护评价

- **活跃维护**：从提交记录看，最近一个月内有多次功能性更新（如新增解析器、改进数据接口绑定、优化调度流程），表明该插件仍在积极开发和完善中。
- **实验性状态**：尽管功能强大，但其 `.uplugin` 中 `IsBetaVersion=true` 且默认禁用（`EnabledByDefault=false`），说明 Epic 官方仍将其视为实验性/测试功能，API 可能发生变化。
- **推荐使用**：适用于追求极致GPU动画性能的技术向项目。由于其复杂性和Beta状态，不建议在稳定性要求极高的生产项目中作为核心功能依赖，但非常适合用于原型验证和技术预研。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Optimus)