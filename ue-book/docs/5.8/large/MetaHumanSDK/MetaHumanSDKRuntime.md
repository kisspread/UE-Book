# MetaHuman SDK

> Utilities and tools for working with MetaHumans in Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman工具包 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `InterchangeDNA` (Runtime), `MetaHumanSDKEditor` (Runtime), `MetaHumanSDKRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK) | |

## 用途

MetaHuman SDK 插件为在 Unreal Engine 中集成和使用 MetaHuman 角色提供了一套完整的工具链和运行时框架。它解决了将高保真 MetaHuman 角色高效地引入游戏项目的关键问题。该插件提供运行时组件，用于管理 MetaHuman 角色的身体和面部动画、物理模拟以及 LOD 优化，同时通过编辑器工具简化资产的导入、配置和管理流程。其存在是为了弥合 Epic Games 官方 MetaHuman 角色创建工具与游戏项目实际应用之间的鸿沟，让开发者能够更便捷地在项目中利用这些高精度数字人资产。

## 使用场景

- **你正在开发一个需要高保真角色的 3A 级或电影级质量的游戏项目** -> 使用 MetaHuman SDK 来管理和驱动你从 MetaHuman Creator 导入的数字人角色，确保其动画、物理和性能表现符合项目要求。
- **你需要为大量 MetaHuman 角色优化运行时性能** -> 通过 `MetaHumanComponent` 精细控制面部动画（Rig Logic）、身体修正（Body Correctives）以及物理模拟在不同 LOD 级别的启用状态，以实现性能与视觉质量的平衡。
- **你的项目涉及复杂的角色身体部位定制** -> 利用 `FMetaHumanCustomizableBodyPart` 结构，为 MetaHuman 角色的不同身体部位（躯干、腿、脚）独立配置控制装备（Control Rig）和物理资产（Physics Asset）。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MetaHuman Component` | 可添加到任何 Actor 的组件，用于管理其 MetaHuman 的动画、物理和 LOD 设置。 | `UMetaHumanComponentUE` |
| `Body` 属性组 | 配置身体骨骼网格体组件名称、身体类型以及是否启用身体修正和头颈控制装备。 | `UMetaHumanComponentBase` |
| `Face` 属性组 | 配置面部骨骼网格体组件名称、Rig Logic 的 LOD 阈值以及颈部修正和颈部程序化控制装备的设置。 | `UMetaHumanComponentBase` |
| `Body Parts` 属性组 | 为 Torso (躯干)、Legs (腿部)、Feet (脚部) 分别指定后处理 Control Rig 和物理资产，并设置其 LOD 阈值。 | `UMetaHumanComponentBase` |

### 使用示例（蓝图描述）

1.  **添加组件**：在你的 MetaHuman 角色蓝图中，添加一个 `MetaHuman Component` 组件。它将自动管理该 Actor 上的 MetaHuman 相关设置。
2.  **配置身体**：在 `Body` 分类下，确认 `BodyComponentName` 指向你角色身体部分的骨骼网格体组件（通常为 “Body”）。根据你的 MetaHuman 身体模板设置 `BodyType`。
3.  **调整性能**：
    *   要优化低端 LOD 性能，可以调整 `RigLogicLODThreshold`，例如设置为 2，则在 LOD 2 及以上级别会停止计算面部动画。
    *   同样，可以设置 `Body LOD Threshold` 来控制身体控制装备的评估 LOD。
4.  **配置身体部件**：展开 `Body Parts`，为 `Torso`、`Legs`、`Feet` 分别设置 `ControlRigClass` 和 `PhysicsAsset`，并为其 `ControlRigLODThreshold` 和 `RigidBodyLODThreshold` 设置合适的值。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanComponentBase.h"
#include "MetaHumanComponentUE.h"
#include "MetaHumanTypes.h"
```

### 基本用法

从 `MetaHumanComponentBase.h` 分析，该插件提供了管理 MetaHuman 角色各部位动画和物理的核心基类。

```cpp
// 在一个Actor类中获取或添加MetaHuman组件
void AMyMetaHumanActor::SetupMetaHuman()
{
    // 查找已有的MetaHuman组件
    UMetaHumanComponentUE* MetaHumanComp = FindComponentByClass<UMetaHumanComponentUE>();
    if (!MetaHumanComp)
    {
        // 如果没有，则创建并添加一个
        MetaHumanComp = NewObject<UMetaHumanComponentUE>(this);
        MetaHumanComp->RegisterComponent();
    }

    // 获取该组件管理的身体骨骼网格体（基于组件名称）
    USkeletalMeshComponent* BodyMesh = MetaHumanComp->GetBodySkelMeshComponent();
    if (BodyMesh)
    {
        // 可以对身体网格体进行额外设置
        BodyMesh->SetComponentTickEnabled(true);
    }
}
```

### 进阶用法

从 `MetaHumanComponentBase.h` 和 `MetaHumanTypes.h` 的接口推断，可以进行更精细的控制。

```cpp
// 动态配置MetaHuman角色的身体部件
void AMyMetaHumanActor::ConfigureBodyParts()
{
    UMetaHumanComponentUE* MetaHumanComp = FindComponentByClass<UMetaHumanComponentUE>();
    if (MetaHumanComp)
    {
        // 注意：通常在编辑器中通过细节面板设置，动态修改需要确保组件已初始化
        // 例如，为腿部配置一个自定义的控制装备（需要TSubclassOf<UControlRig>）
        // MetaHumanComp->Legs.ControlRigClass = MyLegControlRigClass;
        // MetaHumanComp->Legs.ControlRigLODThreshold = 1; // 仅在 LOD0 和 LOD1 上评估

        // 使用类型枚举判断身体类型
        EMetaHumanBodyType CurrentBodyType = MetaHumanComp->BodyType;
        if (CurrentBodyType == EMetaHumanBodyType::BlendableBody)
        {
            // BlendableBody 模式下，某些颈部设置可能被禁用
            // MetaHumanComp->bEnableNeckCorrectives 会被自动隐藏或禁用
        }
    }
}
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何创建一个包含 MetaHuman 核心功能的自定义组件。

**MyMetaHumanManagerComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MetaHumanComponentBase.h" // 包含基础类
#include "MyMetaHumanManagerComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMetaHumanManagerComponent : public UMetaHumanComponentBase
{
    GENERATED_BODY()

public:
    UMyMetaHumanManagerComponent();

protected:
    virtual void BeginPlay() override;

public:
    // 蓝图可调用函数：打印当前MetaHuman配置信息
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void PrintMetaHumanConfig() const;

private:
    // 重写虚函数以连接自定义的AnimBP变量
    virtual void PostInitAnimBP(USkeletalMeshComponent* SkeletalMeshComponent, UAnimInstance* AnimInstance) const override;
};
```

**MyMetaHumanManagerComponent.cpp**
```cpp
#include "MyMetaHumanManagerComponent.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Animation/AnimInstance.h"

UMyMetaHumanManagerComponent::UMyMetaHumanManagerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    // 为组件设置一个默认的身体部件配置
    Torso.ComponentName = TEXT("Torso");
    Legs.ComponentName = TEXT("Legs");
}

void UMyMetaHumanManagerComponent::BeginPlay()
{
    Super::BeginPlay();
    PrintMetaHumanConfig();
}

void UMyMetaHumanManagerComponent::PrintMetaHumanConfig() const
{
    FString ConfigMsg = FString::Printf(TEXT("Body Component: %s, Type: %s, RigLogic LOD Threshold: %d"),
        *BodyComponentName,
        *UEnum::GetValueAsString(BodyType),
        RigLogicLODThreshold);
    UKismetSystemLibrary::PrintString(this, ConfigMsg, true, true, FLinearColor::Green, 5.0f);
}

void UMyMetaHumanManagerComponent::PostInitAnimBP(USkeletalMeshComponent* SkeletalMeshComponent, UAnimInstance* AnimInstance) const
{
    Super::PostInitAnimBP(SkeletalMeshComponent, AnimInstance);
    // 在这里，你可以将自定义变量连接到加载的AnimBP实例
    // 例如，获取AnimBP并设置一些参数
    // if (UYourCustomAnimInstance* CustomAnimBP = Cast<UYourCustomAnimInstance>(AnimInstance))
    // {
    //     CustomAnimBP->SetSomeParam(MyValue);
    // }
}
```

## 模块依赖

基于 MetaHuman 插件的常见架构，使用本插件可能需要以下模块：

| 模块 | 用途 |
|---|---|
| `ControlRig` | MetaHuman 角色广泛使用 Control Rig 来驱动程序化动画和修正。 |
| `PhysicsCore` | 用于配置和运行身体部件的物理资产（Physics Asset）。 |
| `AnimGraphRuntime` | 运行时 AnimGraph 相关功能，用于加载和执行 AnimBP。 |
| `RigLogicModule` | MetaHuman 面部动画的核心逻辑模块，用于解析和驱动面部骨骼。 |

*注：确切的依赖关系需查阅各模块的 Build.cs 文件，上表为基于功能推断的常见关键依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `5c0dc0e5` | [MHSDK] Remove the VersionInfo.txt existence check when discovering MetaHuman character assemblies a | 移除了发现MetaHuman角色组合时对VersionInfo.txt文件存在性的检查。 |
| 2026-05-21 | `418099aa` | Fix the incorrectly converted parent bones for Legacy DNAConfig case | 修复了Legacy DNAConfig情况下父骨骼错误转换的问题。 |
| 2026-05-14 | `d477b10c` | [MHSDK] Replace path-based related-asset filtering in MetaHuman Manager with dependency walking now | 在MetaHuman管理器中，用依赖遍历替换了基于路径的资产筛选方式。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-12 | `c0e92a2b` | [MHSDK] Fix MetaHuman skeletal clothing verification reading incorrect texture dimensions by ensurin | 修复了MetaHuman骨骼服装验证因读取错误纹理尺寸导致的问题。 |

### 维护评价

MetaHuman SDK 插件由 Epic Games 官方维护，是 Unreal Engine 中 MetaHuman 技术栈的核心组成部分。从 Git 历史来看，该插件在 2026 年 5 月仍有密集的功能性提交和 Bug 修复，包括资产发现逻辑优化、骨骼转换修复、管理器依赖分析改进等，表明其处于**活跃维护**状态。插件创建于 2025 年 4 月，相对较新，并且随着 MetaHuman 技术的普及而持续更新。没有证据表明其已废弃。**强烈推荐**在需要集成和运行 MetaHuman 角色的项目中使用此插件，它能提供官方支持的最佳实践和性能优化方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK)
- [官方文档](https://docs.unrealengine.com/)（请在 Epic Games 官方文档中搜索 “MetaHuman” 获取最新信息）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK/Tests) （路径为推断，需确认）