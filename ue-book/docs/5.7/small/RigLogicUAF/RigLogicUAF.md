# RigLogic for UAF

> RigLogic for UAF

| 属性 | 值 |
|---|---|
| 中文名 | RigLogic UAF 集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RigLogicUAF` (Runtime), `RigLogicUAFUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-26 |
| 年龄标签 | 🆕（约 <1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicUAF) | |

## 用途

该插件将 RigLogic（Epic 的面部动画系统）集成到 Unreal Engine 的新一代动画框架——**UAF（Unreal Animation Framework）** 与 **AnimNext** 中。它通过在 AnimNext 的 Trait 系统中提供一个名为 `FRigLogicTrait` 的节点，使得在 AnimNext 动画管道内可以直接驱动 RigLogic 的面部表情、骨骼变形和 BlendShape。

**解决什么问题？**  
UE5 原有的 RigLogic 集成（如 `UDNAAsset`、`AnimNode_RigLogic`）基于老的动画蓝图节点。而 UAF/AnimNext 是未来动画系统的发展方向，该系统使用“Trait”基于数据流执行。此插件将 RigLogic 逻辑封装为一个 AnimNext Trait，使得新框架下的动画图可以无缝使用 RigLogic 的高精度面部动画。

## 使用场景

- 你在 UAF/AnimNext 项目中使用 RigLogic 面部动画。
- 需要将 RigLogic 控制曲线（如"jaw_open"、"eye_blink_L"）映射到 UAF 姿势栈，同时驱动骨骼和 Morph Target。
- 希望在 AnimNext 的“连续混合”（Continuous Blend）或“层次结构”中嵌入面部动画计算。

## 蓝图用法

> **注意**：当前版本（v1.0）未公开任何 BlueprintCallable 函数。所有逻辑均在 C++ Trait 内部执行。蓝图用户无法直接操作该插件，必须通过 C++ 或 UAF/AnimNext 图进行配置。

不过，可在 UAF 动画图中引用该 Trait，并在 Traits 面板中设置参数：

### 核心节点（UAF 图）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RigLogic` (Trait) | 执行 RigLogic 计算，将输入姿势的面部曲线转换为骨骼、BlendShape 和动画映射曲线输出。 | `FUAFRigLogicTraitSharedData` / `FRigLogicTrait` |

**Trait 参数**：
- `Input`：输入姿势（通常来自上一个动画节点）。
- `LODThreshold`：最大 LOD 级别（-1 表示始终执行）。

### 使用示例（蓝图描述）

1. 在 UAF 动画图中添加一个 `RigLogic` Trait 作为后处理节点。
2. 将前一个动画节点的输出连接到 `Input`。
3. 可选：设置 `LODThreshold` 以控制性能。

## C++ 用法

### 头文件引入

```cpp
#include "RigLogicTrait.h"           // FRigLogicTrait
#include "RigLogicTask.h"           // FUAFRigLogicTask
#include "RigLogicInstanceData.h"   // FUE::UAF::FRigLogicInstanceData
#include "RigLogicInstanceDataPool.h" // FRigLogicInstanceDataPool
```

### 基本用法

以下示例展示了如何在 UAF/AnimNext 的自定义 Trait 或 EvaluationTask 中手动创建并使用 RigLogic Trait：

```cpp
// 来自 RigLogicTrait.cpp (部分提取)
#include "RigLogicTrait.h"
#include "RigLogicTask.h"
#include "RigLogicInstanceData.h"
#include "RigLogicInstanceDataPool.h"
#include "RigInstance.h"
#include "RigLogic.h"
#include "DNAIndexMapping.h"

// 假设已在某个 Trait 的实例数据中持有 RigInstance
void SomeTrait::OnBecomeRelevant(...)
{
    // 获取或创建 RigInstance
    // 注意：RigLogic 运行时对象来自 DNAAsset
    TSharedPtr<FSharedRigRuntimeContext> Context = /* 从 DNAAsset 获取 */;
    TUniquePtr<FRigInstance> RigInstance = MakeUnique<FRigInstance>(Context->RigLogic.Get());

    // 设置输入曲线值（如面部表情控制值）
    RigInstance->SetRawControlByName(TEXT("jaw_open"), 0.5f);
    RigInstance->SetRawControlByName(TEXT("eye_blink_L"), 1.0f);

    // 执行 RigLogic 计算（通常在 EvaluationTask 中执行）
    RigInstance->Compute(/* LOD = 0 */);
}

// 在 FUAFRigLogicTask::Execute 中实际调用的内部函数
void FUAFRigLogicTask::UpdateControlCurves(...)
{
    FRigInstance* RigInstance = GetRigInstance();
    // 将 UAF 曲线（如 AnimCurves）映射到 RigLogic 控制
    // 然后调用 RigInstance->Compute()
    // 最后将计算结果（DeltaJointValues, BlendShapeValues）写回 UAF Pose
}
```

**来源文件路径**：`Engine/Plugins/Experimental/RigLogicUAF/Source/RigLogicUAF/Private/RigLogicTrait.cpp`、`RigLogicTask.cpp`

### 进阶用法

**实例数据池管理**：`FRigLogicInstanceDataPool` 负责缓存每个 SkeletalMesh 对应的 `FRigLogicInstanceData`，支持线程安全复用。在自定义 Trait 中可复用共享数据：

```cpp
UE::UAF::FRigLogicModule& Module = FModuleManager::GetModuleChecked<UE::UAF::FRigLogicModule>("RigLogicUAF");
UE::UAF::FRigLogicInstanceDataPool& Pool = Module.DataPool;

const UE::UAF::FReferencePose* RefPose = /* 从 UDNAAsset 获取 */;
TSharedPtr<UE::UAF::FRigLogicInstanceData> InstanceData = Pool.RequestData(RefPose);
// ... 使用 InstanceData 进行映射计算
Pool.FreeData(SkeletalMesh, InstanceData); // 归还
```

该机制适用于大量角色的并行评估，避免重复分配开销。

## Demo 示例

**最小 C++ 示例**：在 AnimNext 训练时创建一个简单 Trait，使用 RigLogicUAF 驱动面部。

### DemoTrait.h
```cpp
#pragma once
#include "TraitCore/Trait.h"
#include "TraitInterfaces/IEvaluate.h"
#include "RigLogicTask.h"
#include "RigLogicTrait.h"

USTRUCT(meta = (DisplayName = "DemoRigLogic"))
struct FDemoRigLogicSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()
    UPROPERTY()
    FAnimNextTraitHandle Input;
};

namespace UE::UAF
{
struct FDemoRigLogicTrait : FBaseTrait, IEvaluate
{
    DECLARE_ANIM_TRAIT(FDemoRigLogicTrait, FBaseTrait)
    using FSharedData = FDemoRigLogicSharedData;

    struct FInstanceData : FTrait::FInstanceData
    {
        FTraitPtr Input;
        TUniquePtr<FRigInstance> RigInstance;
    };

    virtual void PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const override;
};
}
```

### DemoTrait.cpp
```cpp
#include "DemoTrait.h"
#include "RigLogic.h"
#include "RigInstance.h"
#include "DNAAsset.h"
#include "RigLogicUAF.h"

void FDemoRigLogicTrait::PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const
{
    const auto& SharedData = Binding.GetSharedData<FSharedData>();
    auto& InstanceData = Binding.GetInstanceData<FInstanceData>();

    // 获取输入姿势
    UE::UAF::FLODPoseStack InputPose;
    Context.EvaluatePin(InstanceData.Input, InputPose);

    // 获取 RigLogic 数据（假设从 DNAAsset 获取）
    // 这里仅作示意，实际应从共享上下文中获取
    TSharedPtr<FSharedRigRuntimeContext> RigContext = /* ... */;
    if (!InstanceData.RigInstance)
    {
        InstanceData.RigInstance = MakeUnique<FRigInstance>(RigContext->RigLogic.Get());
    }
    
    // 将 InputPose 中的曲线映射到 RigInstance
    // 调用 RigInstance->Compute()
    // 将计算结果（骨骼、MorphTarget）写回输出姿势
    
    Context.SetOutputPose(OutputPose);
}
```

**依赖**：需要将 `DemoTrait` 注册到 AnimNext Trait 系统，并确保在目标模块的 Build.cs 中添加对 `RigLogicUAF` 的依赖。

## 模块依赖

**注意**：以下仅为使用 `RigLogicUAF` 模块时需要额外添加的依赖。  
常见依赖（Core、Engine 等）已省略。

| 模块 | 用途 |
|---|---|
| `RigLogic` | 提供 RigLogic 运行时库（`dna::RigLogic`）及 `UDNAAsset` 等资产类 |
| `UAF` | 提供 UAF 核心框架（`FLODPoseStack`、`FEvaluationVM` 等） |
| `UAFAnimGraph` | 提供 AnimNext 图编译、Traversal 相关基础类型 |

**在 Build.cs 中**，如使用 `RigLogicUAF`，需添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "RigLogicUAF",
    "RigLogic",
    "UAF",
    "UAFAnimGraph"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-08-26 | `d6217680` | RigLogicAnimNext to RigLogicUAF & Added node template | 插件首次创建/迁移，添加了节点模板 |

### 维护评价

- **创建时间**：2025-08-26（距今极短，不足一年）。
- **最近更新**：仅有一次创建提交。
- **激活维护**：该插件标记为 `IsExperimentalVersion = true`，属于实验性项目，未投入广泛使用。当前版本为 1.0，无后续修复或功能更新。
- **已知限制**：无公开的 bug 或限制信息，但作为实验性插件，API 和架构可能随时变动。
- **是否推荐使用**：**谨慎使用**。仅适合 UAF/AnimNext 早期使用者或需要尝鲜的用户；若需要稳定的面部动画集成，建议继续使用传统 `AnimNode_RigLogic`（基于 AnimGraph）。如果项目决定采用 UAF/AnimNext，可评估此插件，但需做好后续维护和兼容性应对。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicUAF)
- [官方文档]（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicUAF/Tests)（如有）