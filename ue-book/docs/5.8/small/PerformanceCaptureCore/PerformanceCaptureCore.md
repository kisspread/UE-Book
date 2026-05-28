# Performance Capture Core

> Performance Capture Core Actor and Component Classes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 性能捕捉核心 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PerformanceCaptureCore` (Runtime), `PerformanceCaptureCoreEditor` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-11-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PerformanceCaptureCore) | |

## 用途

PerformanceCaptureCore 插件的核心目的是为实时动作捕捉（Motion Capture）表演提供一套易于使用的核心框架。它解决的问题是将专业动捕设备（如 Vicon, OptiTrack 等）捕捉的实时人体数据，驱动到 Unreal Engine 中的虚拟角色（如 MetaHuman）上。

**核心机制：**
1.  **数据源接入**：通过 LiveLink 系统接收动捕设备的实时表演数据（`ACapturePerformer` 或 `UPerformerComponent`）。
2.  **骨架重定向**：由于动捕数据的骨架（骨骼层级）通常与目标虚拟角色的骨架不同，插件使用 `IKRetargeter` 资产作为“映射表”，将动捕骨架的动作转换到目标骨架上（`ACaptureCharacter` 或 `URetargetComponent`）。
3.  **驱动控制**：通过组件（`UPerformerComponent`， `URetargetComponent`）提供对整个流程的精细控制，例如暂停动画、设置数据源、应用自定义重定向配置文件等。

**为什么存在：** 它提供了一套预制的 Actor 和 Component，极大地简化了搭建实时动捕驱动数字人管线的复杂性，让开发者能快速实现“动捕演员 → LiveLink → 重定向 → 虚拟角色”这一核心流程。

## 使用场景

-   你在制作**虚拟制片**项目，需要实时驱动一个数字人演员表演，其动作数据来自现场的专业动捕演员。 → 使用 `ACapturePerformer` 和 `ACaptureCharacter` 配对。
-   你在开发**实时直播或虚拟发布会**，需要一个数字人同步现实世界的主持人动作。 → 使用 `UPerformerComponent` 和 `URetargetComponent` 分别附加到 LiveLink 数据源 Actor 和数字人 Actor 上，进行解耦控制。
-   你的项目需要支持**多种不同的动捕设备**或**多种目标角色骨架**，通过更换 `IKRetargeter` 资产即可适配，无需重写逻辑。

## 蓝图用法

蓝图节点主要分布在 `PerformerComponent` 和 `RetargetComponent` 中，用于在运行时动态控制表演和重定向设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Live Link Subject` | 设置作为数据源的 LiveLink 主体名称 | `UPerformerComponent`, `ACapturePerformer` |
| `Get Live Link Subject` | 获取当前 LiveLink 主体名称 | `UPerformerComponent`, `ACapturePerformer` |
| `Set Evaluate Live Link Data` | 开启或关闭对 LiveLink 数据的求值（即播放或暂停动画） | `UPerformerComponent`, `ACapturePerformer` |
| `Get Evaluate Live Link Data` | 查询是否正在求值 LiveLink 数据 | `UPerformerComponent`, `ACapturePerformer` |
| `Set Source Performer Mesh` | 设置重定向的源骨骼网格体组件 | `URetargetComponent` |
| `Set Controlled Mesh` | 设置被重定向驱动的目标骨骼网格体组件 | `URetargetComponent` |
| `Set Retarget Asset` | 设置用于重定向的 `IKRetargeter` 资产 | `URetargetComponent` |
| `Set Custom Retarget Profile` | 设置自定义的重定向配置，覆盖资产中的设置 | `URetargetComponent`, `ACaptureCharacter` |
| `Get Custom Retarget Profile` | 获取当前的自定义重定向配置 | `URetargetComponent`, `ACaptureCharacter` |
| `Set Force Meshes Follow Leader` | 设置是否强制同一Actor上的其他网格体跟随主网格体的动画 | `UPerformerComponent`, `URetargetComponent` |

### 使用示例（蓝图描述）

1.  **基础设置**：在场景中创建两个 `SkeletalMeshActor`，一个代表动捕演员（`ACapturePerformer`），另一个代表数字人角色（`ACaptureCharacter`）。
2.  **连接数据源**：在 `ACapturePerformer` 的细节面板中，设置其 `Subject Name` 为你的 LiveLink 源名称。或者在蓝图中，使用 `Set Live Link Subject` 节点进行设置。
3.  **配置重定向**：在 `ACaptureCharacter` 的细节面板中，找到 `Retarget Component`（通常已自动添加），设置其 `Source Performer` 为场景中的 `ACapturePerformer`，并为其指定一个合适的 `Retarget Asset`（`IKRetargeter`）。
4.  **运行时控制**：在游戏逻辑中，你可以使用 `Set Evaluate Live Link Data (False)` 来暂停数字人的动作，或使用 `Set Custom Retarget Profile` 动态应用一个电影镜头专用的重定向配置。

## C++ 用法

### 头文件引入

```cpp
#include "RetargetComponent.h"
#include "PerformerComponent.h"
#include "CaptureCharacter.h"
#include "CapturePerformer.h"
#include "RetargetAnimInstance.h"
```

### 基本用法

以下代码演示如何在运行时创建一个 `URetargetComponent` 并配置它，使其将动捕源 `SourcePerformer` 的动作重定向到目标网格体 `TargetMesh` 上。

```cpp
// 假设在某个 Actor 的 PostInitializeComponents 或 BeginPlay 中
// 来源: 模拟自 RetargetComponent.cpp 中的 InitiateAnimation 和 SetSourcePerformer 逻辑

// 1. 创建并添加 RetargetComponent
URetargetComponent* RetargetComp = NewObject<URetargetComponent>(this);
AddInstanceComponent(RetargetComp);
RetargetComp->RegisterComponent();

// 2. 设置源表演者 (动捕数据来源)
ACapturePerformer* MyPerformer = /* 从场景中查找或 Spawn */;
RetargetComp->SetSourcePerformer(MyPerformer);

// 3. 设置目标控制网格体
USkeletalMeshComponent* MyCharacterMesh = GetSkeletalMeshComponent(); // 假设当前Actor有
RetargetComp->SetControlledMesh(MyCharacterMesh);

// 4. 设置重定向资产 (IKRetargeter)
UIKRetargeter* MyRetargetAsset = /* 加载或引用一个已有的 Retargeter 资产 */;
RetargetComp->SetRetargetAsset(MyRetargetAsset);

// 5. 初始化动画 (组件会自动在 OnRegister 中调用，但也可手动触发)
RetargetComp->InitiateAnimation();
```

### 进阶用法

结合 `UPerformerComponent` 和 `URetargetComponent`，实现更灵活的、解耦的架构。`PerformerComponent` 仅负责接收和驱动动画，`RetargetComponent` 仅负责重定向。

```cpp
// 来源: 结合 PerformerComponent.h 和 RetargetComponent.h 的公共接口
void AMyAnimationManager::SetupPerformancePipeline()
{
    // --- 设置“表演者”Actor (仅接收LiveLink数据并驱动自身网格) ---
    AActor* PerformerActor = /* Spawn 或获取一个 Actor */;
    UPerformerComponent* PerformerComp = NewObject<UPerformerComponent>(PerformerActor);
    PerformerActor->AddInstanceComponent(PerformerComp);
    PerformerComp->RegisterComponent();
    PerformerComp->SetLiveLinkSubject(FLiveLinkSubjectName("MyMocapSubject"));
    // 设置其控制的网格体
    USkeletalMeshComponent* MocapMesh = PerformerActor->FindComponentByClass<USkeletalMeshComponent>();
    if (MocapMesh)
    {
        PerformerComp->SetControlledMesh(MocapMesh);
    }

    // --- 设置“角色”Actor (将“表演者”的动作重定向到自己) ---
    AActor* CharacterActor = /* Spawn 或获取另一个 Actor */;
    URetargetComponent* RetargetComp = NewObject<URetargetComponent>(CharacterActor);
    CharacterActor->AddInstanceComponent(RetargetComp);
    RetargetComp->RegisterComponent();
    // 将角色的重定向组件指向表演者Actor的网格体
    RetargetComp->SetSourcePerformerMesh(PerformerMesh); // PerformerMesh 是表演者Actor的骨骼网格组件
    RetargetComp->SetRetargetAsset(MyRetargetAsset);
    // 设置角色自身的网格体
    USkeletalMeshComponent* CharacterMesh = CharacterActor->FindComponentByClass<USkeletalMeshComponent>();
    if (CharacterMesh)
    {
        RetargetComp->SetControlledMesh(CharacterMesh);
    }

    // 在某个时刻，同步启动或停止两者
    // PerformerComp->SetEvaluateLiveLinkData(true); // 表演者开始动
    // RetargetComp->InitiateAnimation(); // 角色开始跟随
}
```

## Demo 示例

一个完整的最小示例，展示如何用 C++ 创建一个带有 `URetargetComponent` 的 Actor，并将其连接到一个场景中已有的 `ACapturePerformer`。

**MyRetargetCharacter.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRetargetCharacter.generated.h"

class URetargetComponent;
class USkeletalMeshComponent;

UCLASS()
class AMyRetargetCharacter : public AActor
{
    GENERATED_BODY()

public:
    AMyRetargetCharacter();

protected:
    virtual void BeginPlay() override;

private:
    /** 用于显示角色的骨骼网格体组件 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh", meta = (AllowPrivateAccess = "true"))
    USkeletalMeshComponent* CharacterMesh;

    /** 核心的重定向组件 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
    URetargetComponent* RetargetComponent;

    /** 在编辑器或蓝图中指定的源表演者 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Capture", meta = (AllowPrivateAccess = "true"))
    TSoftObjectPtr<AActor> SourcePerformerActor; // 期望指向一个 ACapturePerformer

    /** 用于重定向的IK资产 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Capture", meta = (AllowPrivateAccess = "true"))
    TSoftObjectPtr<UIKRetargeter> RetargetAsset;
};
```

**MyRetargetCharacter.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyRetargetCharacter.h"
#include "RetargetComponent.h"
#include "CapturePerformer.h"
#include "Components/SkeletalMeshComponent.h"
#include "IKRetargeter.h"

AMyRetargetCharacter::AMyRetargetCharacter()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并设置根网格体
    CharacterMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("CharacterMesh"));
    RootComponent = CharacterMesh;

    // 创建并附加重定向组件
    RetargetComponent = CreateDefaultSubobject<URetargetComponent>(TEXT("RetargetComponent"));
    // 注意：组件会在其 OnRegister 中根据属性自动初始化，无需在此手动设置属性
}

void AMyRetargetCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时尝试连接源表演者
    if (!SourcePerformerActor.IsNull())
    {
        ACapturePerformer* Performer = Cast<ACapturePerformer>(SourcePerformerActor.Get());
        if (Performer)
        {
            // 将重定向组件的源设置为表演者的网格体
            RetargetComponent->SetSourcePerformerMesh(Performer->FindComponentByClass<USkeletalMeshComponent>());
        }
    }

    // 确保重定向资产已设置（可在此处覆盖编辑器中的设置）
    if (RetargetAsset.IsValid())
    {
        RetargetComponent->SetRetargetAsset(RetargetAsset.Get());
    }

    // 确保控制网格体是自身网格体
    RetargetComponent->SetControlledMesh(CharacterMesh);

    // 触发动画初始化（如果 OnRegister 未触发或配置更改后）
    RetargetComponent->InitiateAnimation();
}
```

## 模块依赖

该插件依赖于引擎的动画和 IK 重定向系统，这些模块在标准项目中通常已存在，但在你的 `.Build.cs` 文件中如果需要直接访问这些类型，可能需要显式依赖。

| 模块 | 用途 |
|---|---|
| `LiveLinkAnimationCore` | 提供 `FLiveLinkSubjectName` 等 LiveLink 动画角色类型定义 |
| `IKRigRuntime` | 提供 `UIKRetargeter` 资产和 `FAnimNode_RetargetPoseFromMesh` 动画节点 |
| `ControlRig` | 重定向和动画图可能涉及的 Control Rig 基础架构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `1693cbe0` | [Performance Capture Core] - Fix crash in GetCustomProfile on a null anim instance. Crash can occur | 修复在动画实例为空时调用 GetCustomProfile 导致的崩溃 |
| 2026-04-13 | `d3c17556` | [Performance Capture] | (提交信息不完整) 性能捕捉相关更新 |
| 2026-03-30 | `57683776` | Fix some UObject system access after shutdown. | 修复引擎关闭后部分 UObject 系统访问导致的问题 |
| 2025-09-08 | `cebd36ff` | MetaHuman becomes deformed during realtime animation in UEFN if Face is selected in Controlled Skele... | 修复在UEFN中，当在Controlled Skeletal Mesh上选择面部时，MetaHuman在实时动画中会出现变形的问题 |
| 2025-08-18 | `534ba4a1` | [Performance Capture Core] | (提交信息不完整) 性能捕捉核心相关更新 |

### 维护评价

-   **状态**：**活跃维护中**。
-   **证据**：插件创建于 2023 年底（🆕，约 3 年），属于较新的插件。从 Git 记录看，最近两次实质性更新（修复崩溃和修复动画选择问题）均发生在 2026 年，表明 Epic 团队仍在积极维护和修复其问题。
-   **建议**：该插件标记为 `IsBetaVersion: true`，表明其 API 和功能可能尚未完全稳定。在生产环境中使用时，需密切关注更新日志和 breaking changes。鉴于其提供的功能对于实时数字人管线至关重要，且维护活跃，**推荐用于非关键或可接受 Beta 风险的项目中**。对于追求极致稳定性的项目，可以考虑等待其正式版或密切关注其更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PerformanceCaptureCore)
-   官方文档 (暂无，.uplugin 中 DocsURL 为空)
-   测试用例 (插件目录内未发现明显的自动化测试文件)