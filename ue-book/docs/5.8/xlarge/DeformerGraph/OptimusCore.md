# Deformer Graph

> Editor for creating GPU mesh deformation graphs

| 属性 | 值 |
|---|---|
| 中文名 | 变形图编辑器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 UI、蓝图资产、HLSL 模板） |
| 模块 | `OptimusSettings` (Runtime), `OptimusCore` (Runtime), `OptimusDeveloper` (Runtime), `OptimusEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph) | |

## 用途

Deformer Graph（原名 Optimus）是一个基于 GPU Compute Framework 的骨骼网格体变形系统。它允许开发者通过可视化节点图编写 GPU 计算着色器来实现自定义的网格变形效果，完全在 GPU 上运行，适合处理高顶点数的实时变形。

核心架构：`UOptimusDeformer` 资产包含节点图（Setup/Update/Trigger 图），编译后生成 `UComputeGraph`，运行时由 `UOptimusDeformerInstance` 驱动执行。每个节点可定义自定义 HLSL Compute Kernel，通过 Data Interface 读写网格数据。

与 CPU 端的 AnimBP 或 Control Rig 变形不同，Deformer Graph 将所有变形计算卸载到 GPU，适用于大规模顶点操作（如肌肉模拟、布料后处理、程序化变形等）。

**注意**：`EnabledByDefault=false` 且 `IsBetaVersion=true`，需要在项目设置中手动启用，且 API 可能在未来版本中变化。

## 使用场景

- 你需要对骨骼网格体进行 GPU 加速的实时变形 → 用 DeformerGraph
- 你需要实现肌肉挤压膨胀、次级骨骼动画等复杂变形 → 创建自定义 Compute Kernel 节点
- 你需要从 Control Rig 或动画蓝图驱动 GPU 变形参数 → 通过 DeformerInstance 设置变量
- 你需要读取骨骼权重、变形目标、动画属性等输入数据 → 使用内置 Data Interface 节点
- 你需要将多个 GPU 变形器动态组合到同一角色上 → 使用 DeformerDynamicInstanceManager
- 你需要调试 GPU 变形中间状态 → 使用 Debug Draw Data Interface

## 蓝图用法

### 核心节点

Deformer Graph 的蓝图 API 主要通过 `UOptimusDeformerInstance` 暴露，用于在运行时设置变形器变量和触发动图。

**变量设置（按类型分组）**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetBoolVariable` | 设置布尔变量 | `UOptimusDeformerInstance` |
| `SetIntVariable` / `SetInt2Variable` / `SetInt3Variable` / `SetInt4Variable` | 设置整数变量 | `UOptimusDeformerInstance` |
| `SetFloatVariable` | 设置浮点变量 | `UOptimusDeformerInstance` |
| `SetVectorVariable` / `SetVector2Variable` / `SetVector4Variable` | 设置向量变量 | `UOptimusDeformerInstance` |
| `SetLinearColorVariable` | 设置颜色变量 | `UOptimusDeformerInstance` |
| `SetQuatVariable` / `SetRotatorVariable` / `SetTransformVariable` | 设置旋转/变换变量 | `UOptimusDeformerInstance` |
| `SetNameVariable` | 设置名称变量 | `UOptimusDeformerInstance` |
| `SetXxxArrayVariable` (所有类型的数组版本) | 设置数组类型变量 | `UOptimusDeformerInstance` |
| `EnqueueTriggerGraph` | 触发指定名称的触发图在下一帧执行 | `UOptimusDeformerInstance` |

**使用示例（蓝图描述）**

1. **应用 Deformer Graph 到骨骼网格体**：
   - 获取目标 Actor 的 `SkeletalMeshComponent` → 在组件上设置 `Mesh Deformer` 属性为你的 `UOptimusDeformer` 资产
   - 配置 `UOptimusDeformerInstanceSettings` 中的 Component Bindings，将图中定义的组件绑定映射到实际的 Actor 组件

2. **运行时修改变形参数**：
   - 获取 `DeformerInstance` → 调用 `SetFloatVariable("MuscleScale", 1.5)` 设置名为 MuscleScale 的浮点变量
   - 变量名必须与 Deformer Graph 资产中定义的变量名完全匹配

3. **触发动图执行**：
   - 调用 `EnqueueTriggerGraph("Burst")` → 该触发图将在下一帧 Update 图执行前运行
   - 适合一次性事件驱动的变形效果（如受击弹跳）

## C++ 用法

### 头文件引入

```cpp
#include "OptimusDeformer.h"
#include "OptimusDeformerInstance.h"
#include "OptimusDeformerDynamicInstanceManager.h"
```

### 基本用法

通过 C++ 创建和配置 Deformer Graph 实例：

```cpp
// 创建 Deformer 实例设置
UOptimusDeformerInstanceSettings* Settings = NewObject<UOptimusDeformerInstanceSettings>();
Settings->InitializeSettings(DeformerAsset, SkeletalMeshComponent);

// 获取绑定的组件
TArray<UActorComponent*> BoundComponents;
Settings->GetComponentBindings(DeformerAsset, SkeletalMeshComponent, BoundComponents);
```

**来源**: `Public/OptimusDeformerInstance.h`

### 运行时设置变量

```cpp
// 获取 Deformer 实例并设置变量
UOptimusDeformerInstance* Instance = ...; // 从 DeformerDynamicInstanceManager 获取
if (Instance)
{
    Instance->SetFloatVariable(FName("MyFloatVar"), 3.14f);
    Instance->SetVectorVariable(FName("MyDirection"), FVector(1, 0, 0));
    Instance->SetTransformVariable(FName("MyTransform"), FTransform::Identity);
    Instance->EnqueueTriggerGraph(FName("MyTrigger"));
}
```

**来源**: `Public/OptimusDeformerInstance.h`

### 动态组合多个变形器

```cpp
// 通过 DynamicInstanceManager 组合多个变形器
UOptimusDeformerDynamicInstanceManager* Manager = ...;

// 添加生产者变形器
Manager->AddProducerDeformer(ProducerObject, InstanceGuid, DeformerAsset);

// 排队执行（从动画/物理线程调用）
Manager->EnqueueProducerDeformer(
    InstanceGuid,
    EOptimusDeformerExecutionPhase::AfterDefaultDeformer,
    1  // Execution Group
);
```

**来源**: `Public/OptimusDeformerDynamicInstanceManager.h`

### 进阶用法

**通过 Control Rig 集成驱动 Deformer Graph**：

Deformer Graph 提供了与 Control Rig 深度集成的 RigUnit。通过 `FRigUnit_AddOptimusDeformer` 可以在 Control Rig 中动态添加变形器，并通过各种 Trait 设置变量值。

```cpp
// 在 Control Rig 中使用 Deformer Graph
// 通过 FRigVMTrait_OptimusDeformer 指定变形器资产
// 通过 FRigVMTrait_SetDeformerFloatVariable 等设置变量
// 执行阶段由 FRigVMTrait_OptimusDeformerSettings 控制
```

**来源**: `Private/ControlRig/RigUnit_Optimus.h`

**自定义数据类型注册**：

```cpp
// 注册自定义数据类型供 Deformer Graph 使用
FOptimusDataTypeRegistry& Registry = FOptimusDataTypeRegistry::Get();

// 注册 UE 结构体类型
Registry.RegisterStructType(MyUStructType);

// 注册带自定义转换函数的类型
Registry.RegisterType(
    MyUStructType,
    ShaderValueType,
    [](TArrayView<const uint8> InRawValue, FShaderValueContainerView OutShaderValue) -> bool
    {
        // 自定义属性值到着色器值的转换
        return true;
    },
    FLinearColor::White,
    true,  // bShowElements
    EOptimusDataTypeUsageFlags::None
);

// 查找类型
FOptimusDataTypeHandle FoundType = Registry.FindType(FName("MyTypeName"));
TArray<FOptimusDataTypeHandle> AllTypes = Registry.GetAllTypes();
```

**来源**: `Public/OptimusDataTypeRegistry.h`

**自定义表达式求值**：

```cpp
// 使用表达式引擎计算执行域大小
Optimus::Expression::FEngine Engine;
Optimus::Expression::FParseResult Result = Engine.Parse(
    TEXT("NumVertices / 64"),
    [](FName InConstantName) -> TOptional<float>
    {
        if (InConstantName == "NumVertices")
            return 1024.0f;
        return {};
    }
);

if (Result.IsType<Optimus::Expression::FExpressionObject>())
{
    const auto& Expr = Result.Get<Optimus::Expression::FExpressionObject>();
    float Value = Engine.Execute(Expr, InConstantEvaluator);
}
```

**来源**: `Public/OptimusExpressionEvaluator.h`

## Demo 示例

以下示例展示如何在 C++ 中获取 Deformer 实例并设置运行时变量：

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "OptimusDeformerInstance.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UFUNCTION(BlueprintCallable)
    void SetDeformationIntensity(float InIntensity);

    UFUNCTION(BlueprintCallable)
    void TriggerExplosion();

private:
    // 在编辑器中设置 Deformer Graph 资产
    UPROPERTY(EditAnywhere, Category = "Deformation")
    TSoftObjectPtr<UOptimusDeformer> DeformerAsset;

    UPROPERTY(Transient)
    TObjectPtr<UOptimusDeformerInstance> DeformerInstance;
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "OptimusDeformer.h"
#include "Components/SkeletalMeshComponent.h"

AMyCharacter::AMyCharacter()
{
    // SkeletalMeshComponent 已由 Character 基类创建
}

void AMyCharacter::SetDeformationIntensity(float InIntensity)
{
    if (DeformerInstance)
    {
        DeformerInstance->SetFloatVariable(FName("Intensity"), InIntensity);
    }
}

void AMyCharacter::TriggerExplosion()
{
    if (DeformerInstance)
    {
        DeformerInstance->EnqueueTriggerGraph(FName("Explosion"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | GPU 计算框架底层，提供 Compute Graph/Kernel/DataInterface 基础设施 |
| `MeshDeformer` | Mesh Deformer 接口基类，定义 UMeshDeformer/UMeshDeformerInstance 体系 |
| `ControlRig` | Control Rig 集成，提供 RigUnit 和 Trait 用于从动画系统驱动变形器 |
| `MeshDescription` | 网格描述数据结构，用于编辑器中读回变形后几何体 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `43a2c5ff` | Deformer Graph: programmatic component resolver | 新增编程式组件解析器，支持代码级绑定组件 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases (S | 为 Data Interface 添加逐 Kernel 输出掩码支持 |
| 2026-04-16 | `004f9e11` | Deformer Graph: ability to look for secondary bindings in parent actors if not found in the componen | 支持在父 Actor 中查找未找到的次级组件绑定 |
| 2026-04-14 | `909e5b5b` | [Deformer Graph] Move Mark Deformed to PostSubmit and GetReadableOutputBuffer to Gather dispatch dat | 重构标记变形完成的时机，移至 PostSubmit 阶段 |

### 维护评价

**活跃维护中** ✅

Deformer Graph（原 Optimus）自 2022 年从 Experimental 迁移并重命名以来，一直在持续开发。最近 1 个月内有多次功能性更新，包括新增组件解析器、性能优化和跨 Actor 绑定查找等功能。

- **优点**：更新频繁，功能持续完善，与 Control Rig 集成越来越紧密
- **注意**：仍标记为 Beta（`IsBetaVersion=true`），且默认未启用（`EnabledByDefault=false`），API 可能在未来版本中有 breaking changes
- **建议**：适合已经在使用 Compute Framework 的高级用户，以及需要 GPU 加速变形的项目。生产环境使用前需充分测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph)
- 官方文档（无公开 URL）