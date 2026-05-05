# Performance Capture Core

> Performance Capture Core Actor and Component Classes

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | 否（IsExperimentalVersion = true） |
| 包含内容 | 否 |
| 模块 | PerformanceCaptureCore (Runtime), PerformanceCaptureCoreEditor (Editor) |
| 插件依赖 | IKRig, LiveLink |
| 创建时间 | 2023-11-30 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PerformanceCaptureCore) | |

## 用途

PerformanceCaptureCore 是一个面向动捕（Motion Capture）工作流的运行时框架，解决的核心问题是：**如何在 UE 编辑器中实时预览 LiveLink 动捕数据，并将动捕数据通过 IK Retarget 映射到不同的角色骨架上**。

它提供了两对 Actor + Component 组合：

- **ACapturePerformer + UPerformerComponent**：接收端，从 LiveLink Subject 获取动捕数据，驱动 Skeletal Mesh 播放动画。
- **ACaptureCharacter + URetargetComponent**：目标端，接收 Performer 的动画数据，通过 IKRetargeter 将运动从源骨架重定向到目标骨架。

本质上，这个 plugin 是 Epic 为 MetaHuman 实时动捕预览搭建的基础设施。它封装了 LiveLink → AnimInstance → IKRetarget 的完整管线，让你不需要手动编写动画蓝图即可在编辑器中看到动捕效果。

## 使用场景

- 你有一个动捕设备（如 Vicon、OptiTrack、Xsens）通过 LiveLink 发送实时数据 → 用 `ACapturePerformer` 接收并预览
- 你需要把动捕演员的骨架数据重定向到 MetaHuman 或自定义角色 → 用 `ACaptureCharacter` 配合 `UIKRetargeter` 资产
- 你想在编辑器中实时预览动捕效果（不需要 Play In Editor）→ 两个组件都支持 `bTickInEditor = true`
- 你需要运行时切换 LiveLink Subject、切换重定向目标、或调整重定向参数 → 所有关键属性都可以通过蓝图在运行时修改

## 蓝图用法

### Performer 端节点（ACapturePerformer）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLiveLinkSubject` | 设置 LiveLink Subject（必须是 Animation Role） | `ACapturePerformer` |
| `GetLiveLinkSubject` | 获取当前 LiveLink Subject | `ACapturePerformer` |
| `SetEvaluateLiveLinkData` | 启用/暂停 LiveLink 动画评估 | `ACapturePerformer` |
| `GetEvaluateLiveLinkData` | 获取当前评估状态 | `ACapturePerformer` |
| `SetMocapMesh` | 设置根 Skeletal Mesh 的资产 | `ACapturePerformer` |

### Performer 组件节点（UPerformerComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLiveLinkSubject` | 设置 LiveLink Subject | `UPerformerComponent` |
| `SetControlledMesh` | 设置被驱动的 SkeletalMeshComponent | `UPerformerComponent` |
| `SetEvaluateLiveLinkData` | 启用/暂停动画评估 | `UPerformerComponent` |
| `SetForceMeshesFollowLeader` | 强制其他网格跟随主网格 | `UPerformerComponent` |

### Character 端节点（ACaptureCharacter）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSourcePerformer` | 设置源 Performer Actor | `ACaptureCharacter` |
| `SetRetargetAsset` | 设置 IKRetargeter 资产 | `ACaptureCharacter` |
| `SetCustomRetargetProfile` | 设置自定义重定向配置（覆盖 Retarget 资产设置） | `ACaptureCharacter` |
| `GetCustomRetargetProfile` | 获取当前重定向配置 | `ACaptureCharacter` |
| `SetForceAllSkeletalMeshesToFollowLeader` | 强制所有网格跟随主网格 | `ACaptureCharacter` |
| `GetRetargetComponent` | 获取内部的 RetargetComponent | `ACaptureCharacter` |

### Retarget 组件节点（URetargetComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSourcePerformerMesh` | 设置源 Skeletal Mesh Component | `URetargetComponent` |
| `SetControlledMesh` | 设置目标 Skeletal Mesh Component | `URetargetComponent` |
| `SetRetargetAsset` | 设置 IKRetargeter 资产 | `URetargetComponent` |
| `SetCustomRetargetProfile` | 设置自定义重定向配置 | `URetargetComponent` |
| `GetCustomRetargetProfile` | 获取自定义重定向配置 | `URetargetComponent` |
| `SetSourcePerformer` | 设置源 CapturePerformer Actor | `URetargetComponent` |
| `SetForceMeshesFollowLeader` | 强制其他网格跟随主网格 | `URetargetComponent` |

### 使用示例（蓝图描述）

**场景：将动捕数据重定向到 MetaHuman**

1. 在关卡中放置一个 `ACapturePerformer` Actor，设置 `SubjectName` 为你的 LiveLink 动捕源。
2. 放置一个 `ACaptureCharacter` Actor，给它的 Skeletal Mesh 设置 MetaHuman 的 Skeletal Mesh。
3. 在 `ACaptureCharacter` 上设置 `SourcePerformer` 指向步骤 1 的 Performer。
4. 创建一个 `UIKRetargeter` 资产（从动捕骨架到 MetaHuman 骨架），设置到 `RetargetAsset` 属性。
5. 运行时，你可以通过蓝图调用 `SetCustomRetargetProfile` 动态调整重定向参数。

**场景：纯 LiveLink 预览（无重定向）**

1. 放置一个 `ACapturePerformer`，设置 `SubjectName`。
2. Performer 会自动将根 Skeletal Mesh 设为 LiveLinkInstance 驱动，实时预览动捕姿态。

## C++ 用法

### 头文件引入

```cpp
// Performer 端
#include "CapturePerformer.h"
#include "PerformerComponent.h"

// Character/Retarget 端
#include "CaptureCharacter.h"
#include "RetargetComponent.h"
#include "RetargetAnimInstance.h"
```

### 基本用法：创建 Performer

创建一个接收 LiveLink 动捕数据的 Actor：

```cpp
// 来源: CapturePerformer.h / CapturePerformer.cpp

// Spawn 一个 Performer
ACapturePerformer* Performer = World->SpawnActor<ACapturePerformer>();

// 设置 LiveLink Subject（必须是 Animation Role 类型）
Performer->SetLiveLinkSubject(FLiveLinkSubjectName(TEXT("MyMocapSubject")));

// 设置动捕网格资产
Performer->SetMocapMesh(MyMocapSkeletalMesh);

// 暂停/恢复动画评估
Performer->SetEvaluateLiveLinkData(false); // 暂停
Performer->SetEvaluateLiveLinkData(true);  // 恢复
```

### 基本用法：创建 Character（重定向目标）

```cpp
// 来源: CaptureCharacter.h / CaptureCharacter.cpp

// Spawn 一个 Character
ACaptureCharacter* Character = World->SpawnActor<ACaptureCharacter>();

// 设置源 Performer
Character->SetSourcePerformer(Performer);

// 设置 IKRetargeter 资产
Character->SetRetargetAsset(MyIKRetargeter);

// 设置自定义重定向配置（覆盖 Retarget 资产的设置）
FRetargetProfile Profile;
Profile.bApplyTranslation = true;
Profile.bApplyRotation = true;
Character->SetCustomRetargetProfile(Profile);

// 强制所有 Skeletal Mesh 跟随主网格
Character->SetForceAllSkeletalMeshesToFollowLeader(true);

// 获取内部的 RetargetComponent（用于更精细的控制）
URetargetComponent* RetargetComp = Character->GetRetargetComponent();
```

### 进阶用法：直接使用组件

如果你不想使用预设的 Actor 类，可以直接将组件附加到任意 Actor：

```cpp
// 来源: PerformerComponent.h / RetargetComponent.h

// --- Performer 组件 ---
UPerformerComponent* PerfComp = NewObject<UPerformerComponent>(MyActor);
PerfComp->SetLiveLinkSubject(FLiveLinkSubjectName(TEXT("MySubject")));
// 必须设置被驱动的 SkeletalMeshComponent（必须在同一 Actor 上）
PerfComp->SetControlledMesh(MyActor->GetSkeletalMeshComponent());
PerfComp->bForceOtherMeshesToFollowControlledMesh = true;
MyActor->AddInstanceComponent(PerfComp);

// --- Retarget 组件 ---
URetargetComponent* RetargetComp = NewObject<URetargetComponent>(MyActor);
RetargetComp->SetSourcePerformerMesh(SourceSkeletalMeshComponent);
RetargetComp->SetControlledMesh(TargetSkeletalMeshComponent);
RetargetComp->SetRetargetAsset(MyIKRetargeter);
RetargetComp->bForceOtherMeshesToFollowControlledMesh = true;
MyActor->AddInstanceComponent(RetargetComp);
```

### 进阶用法：运行时动态切换重定向配置

```cpp
// 来源: RetargetComponent.cpp

// 动态切换 Retarget 资产
RetargetComp->SetRetargetAsset(NewIKRetargeter);

// 动态更新重定向配置（支持 Sequencer Interp）
FRetargetProfile NewProfile;
NewProfile.bApplyTranslation = true;
NewProfile.bApplyRotation = false;
RetargetComp->SetCustomRetargetProfile(NewProfile);

// 动态切换源 Performer
RetargetComp->SetSourcePerformer(NewPerformer);
```

## 内部架构

### 数据流

```
LiveLink Subject
    │
    ▼
ACapturePerformer
  └─ UPerformerComponent
       └─ ULiveLinkInstance (AnimInstance)
            └─ 驱动 Skeletal Mesh A
                    │
                    │ (源骨架姿态)
                    ▼
ACaptureCharacter
  └─ URetargetComponent
       └─ URetargetAnimInstance
            └─ FAnimNode_RetargetPoseFromMesh
                 └─ UIKRetargeter (骨架映射)
                      └─ 驱动 Skeletal Mesh B (目标角色)
```

### 关键类关系

- `ACapturePerformer` 内部持有 `UPerformerComponent`，后者管理 `ULiveLinkInstance` 的创建和配置。
- `ACaptureCharacter` 内部持有 `URetargetComponent`，后者管理 `URetargetAnimInstance`。
- `URetargetAnimInstance` 使用 `FRetargetAnimInstanceProxy` 将 `FAnimNode_RetargetPoseFromMesh` 注入动画评估管线。
- `FRetargetAnimInstanceProxy` 是 `FAnimInstanceProxy` 的子类，手动管理 Retarget 节点的 Initialize/Update/Evaluate/CacheBones 生命周期。

### Leader Pose 机制

两个组件都支持 `bForceOtherMeshesToFollowControlledMesh`（默认为 true）。启用后，Owner Actor 上的所有其他 `USkeletalMeshComponent` 会被设为 ControlledMesh 的 Leader Pose Component，实现多网格同步跟随。这对于拥有身体 + 头发 + 布料等多个 Skeletal Mesh 的 MetaHuman 特别重要。

## Demo 示例

### 最小可运行示例（C++ Actor）

```cpp
// MyPCapActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyPCapActor.generated.h"

class ACapturePerformer;
class ACaptureCharacter;

UCLASS()
class AMyPCapActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "PCap")
    FName LiveLinkSubjectName = TEXT("MySubject");

    UPROPERTY(EditAnywhere, Category = "PCap")
    TObjectPtr<USkeletalMesh> MocapMesh;

    UPROPERTY(EditAnywhere, Category = "PCap")
    TObjectPtr<USkeletalMesh> TargetMesh;

    UPROPERTY(EditAnywhere, Category = "PCap")
    TObjectPtr<UIKRetargeter> RetargetAsset;

private:
    UPROPERTY()
    TObjectPtr<ACapturePerformer> Performer;

    UPROPERTY()
    TObjectPtr<ACaptureCharacter> Character;
};
```

```cpp
// MyPCapActor.cpp
#include "MyPCapActor.h"
#include "CapturePerformer.h"
#include "CaptureCharacter.h"
#include "Components/SkeletalMeshComponent.h"

void AMyPCapActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建 Performer
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;

    Performer = GetWorld()->SpawnActor<ACapturePerformer>(
        GetActorLocation() + FVector(0, -200, 0),
        FRotator::ZeroRotator,
        SpawnParams);

    if (MocapMesh)
    {
        Performer->SetMocapMesh(MocapMesh);
    }
    Performer->SetLiveLinkSubject(FLiveLinkSubjectName(LiveLinkSubjectName));

    // 2. 创建 Character
    Character = GetWorld()->SpawnActor<ACaptureCharacter>(
        GetActorLocation() + FVector(0, 200, 0),
        FRotator::ZeroRotator,
        SpawnParams);

    if (TargetMesh)
    {
        Character->GetSkeletalMeshComponent()->SetSkeletalMeshAsset(TargetMesh);
    }
    Character->SetSourcePerformer(Performer);
    Character->SetRetargetAsset(RetargetAsset);
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "PerformanceCaptureCore",
    "IKRig",
    "LiveLinkInterface"
});
```

## 模块依赖

### Runtime 模块（PerformanceCaptureCore）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 系统 |
| `Engine` | SkeletalMeshComponent、AnimInstance 等核心引擎类 |
| `Slate` | UI 框架（编辑器属性面板） |
| `SlateCore` | Slate 核心类型 |
| `IKRig` | IKRetargeter、RetargetProfile 等重定向核心 |
| `LiveLinkAnimationCore` | LiveLink 动画评估（ULiveLinkInstance） |
| `LiveLinkInterface` | LiveLink Subject 类型定义 |

### Editor 模块（PerformanceCaptureCoreEditor）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `IKRig` | IKRetargeter 类型引用 |
| `LiveLinkAnimationCore` | LiveLink 类型引用 |
| `LiveLinkInterface` | LiveLink 类型引用 |
| `PerformanceCaptureCore` | Runtime 模块 |

### 你的模块需要依赖

如果你要在自己的代码中使用这个 plugin：

```csharp
// Build.cs
PrivateDependencyModuleNames.Add("PerformanceCaptureCore");
// 如果需要 UIKRetargeter 类型：
PrivateDependencyModuleNames.Add("IKRig");
```

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-09-08 | `250bf6e` | MetaHuman becomes deformed during realtime animation in UEFN if Face is selected in Controlled Skeletal Mesh | Bug 修复：修复在 UEFN 中选择 Face 作为 Controlled Mesh 时 MetaHuman 变形的问题 |
| 2025-08-18 | `534ba4a` | Prevent pre-requisite cycle when SourceMesh == ControlledMesh | Bug 修复：当源网格和目标网格相同时避免 Tick 依赖循环 |
| 2025-08-12 | `e190488` | Correcting logic surrounding changing the Source Skeletal mesh Component Reference | Bug 修复：修正更换源 Skeletal Mesh 引用时的逻辑问题 |

### 维护评价

- **创建时间**：2023-11-30，约 2.5 年历史
- **实验性状态**：`IsExperimentalVersion = true`，尚未标记为正式版本
- **活跃度**：活跃维护中。最近 3 次提交集中在 2025 年 8-9 月，全部是 bug 修复，说明 Epic 内部在持续使用和打磨这个 plugin
- **近期趋势**：修复主要围绕 UEFN（Unreal Editor for Fortnite）中的 MetaHuman 实时动捕场景，表明这是 Epic 当前重点推进的方向
- **已知限制**：
  - 实验性 plugin，API 可能在未来版本中发生变化（5.7 已有多个 `_DEPRECATED` 属性标记）
  - `ACaptureCharacter` 的部分属性在 5.7 已迁移到 `URetargetComponent`（`SourcePerformer`、`RetargetAsset`、`bForceAllSkeletalMeshesToFollowLeader`）
  - 没有公开文档（DocsURL 为空）
- **推荐度**：⭐⭐⭐ 推荐使用，但需注意是实验性 API，升级引擎版本时需要关注废弃标记

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PerformanceCaptureCore)
- 官方文档：无（DocsURL 为空）
- [IKRig Plugin 文档](https://docs.unrealengine.com/5.6/en-US/ik-rig-in-unreal-engine/)（作为依赖项，包含 UIKRetargeter 的详细说明）
