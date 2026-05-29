# Performance Capture Core

> Performance Capture Core Actor and Component Classes

| 属性 | 值 |
|---|---|
| 中文名 | 性能捕捉核心 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PerformanceCaptureCore` (Runtime), `PerformanceCaptureCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PerformanceCaptureCore) | |

## 用途

这个插件旨在简化使用 MetaHuman 进行实时性能捕捉（Performance Capture）的工作流程。它通过提供专门的 Actor 和 Component 类，将 IK Retargeting、Live Link 驱动等复杂配置封装成易于使用的蓝图接口。核心目标是降低用户设置 MetaHuman 面部及身体实时动画驱动的门槛，使其能够快速接入动捕数据（如 Live Link）并进行重定向。

## 使用场景

- **场景1：MetaHuman 实时动画预览**：你有一个 MetaHuman 角色，并希望通过 Live Link 连接面部或身体动捕设备进行实时驱动。使用此插件，可以快速设置一个 `Performer Character` Actor 并关联 Live Link 主题，无需手动编写大量配置代码。
- **场景2：自定义动画重定向**：你需要将一段表演者的动画重定向到另一个具有不同骨架比例的 MetaHuman 角色上。`Retarget Character` 和相关的 Retarget 组件可以帮助你通过蓝图设置重定向资产和自定义配置。
- **场景3：UEFN 项目中的面部动画**：在 Unreal Editor for Fortnite (UEFN) 环境下，需要确保 MetaHuman 面部动画在特定情况下不变形。插件的后续更新（如 `cebd36ff`）致力于解决此类特定集成问题。

## 蓝图用法

此插件的核心功能通过蓝图暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Source Performer` | 设置重定向动画的源表演者（通常是一个带有 Retarget 组件的 Actor）。 | `URetargetComponent` |
| `Set Retarget Asset` | 设置用于动画重定向的 IK Retarget 资产。 | `URetargetComponent` |
| `Set Custom Retarget Profile` | 设置自定义的重定向配置文件。 | `URetargetComponent` |
| `Get/ Set LiveLink Subject` | 获取或设置驱动当前表演者的 Live Link 主题名称。 | `UPerformerComponent` |
| `Pause Animation` | 暂停或恢复表演者的动画更新。 | `UPerformerComponent` |
| `Get Custom Profile` | 获取当前的自定义重定向配置文件。 | `URetargetAnimInstance` |

### 使用示例（蓝图描述）

1.  **设置基础表演者**：
    - 将 `Performer Skeletal Mesh Actor` 拖入场景。
    - 在其细节面板中，找到 `Performer Component`。
    - 设置其 `Live Link Subject` 属性为你的动捕数据流主题名。角色即刻开始接收并驱动动画。

2.  **设置重定向角色**：
    - 将 `Retarget Character` 拖入场景。
    - 在其细节面板中，找到 `Retarget Component`。
    - 将 `Source Performer` 指向场景中已设置好的 `Performer Skeletal Mesh Actor`。
    - 为 `Retarget Asset` 指定一个 `IK Retargeter` 资产。
    - 重定向角色将开始根据源表演者的动画进行重定向。

## C++ 用法

此插件主要面向蓝图用户设计，其核心 C++ 模块（`PerformanceCaptureCore`）提供底层的 Actor、Component 和 AnimInstance 类。另一个模块 `PerformanceCaptureCoreEditor` 可能包含一些编辑器扩展功能。

### 头文件引入

```cpp
// 核心功能
#include “RetargetComponent.h”
#include “PerformerComponent.h”
#include “RetargetAnimInstance.h”
#include “PerformerCharacter.h”
#include “RetargetCharacter.h”
```

### 基本用法

（C++ 用法通常涉及组件的创建和参数设置，但插件鼓励通过蓝图完成主要配置。此处以访问组件为例。）

```cpp
// 假设你有一个 APerformerCharacter* PerformerActor
if (PerformerActor)
{
    // 获取其上的 Performer 组件并查询 Live Link 主题
    UPerformerComponent* PerformerComp = PerformerActor->FindComponentByClass<UPerformerComponent>();
    if (PerformerComp)
    {
        FName CurrentSubject = PerformerComp->GetLiveLinkSubject();
        // 可以进行逻辑判断或切换主题
    }
}

// 假设你有一个 ARetargetCharacter* RetargetActor
if (RetargetActor)
{
    // 获取 Retarget 组件并手动设置重定向资产
    URetargetComponent* RetargetComp = RetargetActor->FindComponentByClass<URetargetComponent>();
    if (RetargetComp)
    {
        RetargetComp->SetRetargetAsset(MyNewRetargeterAsset);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何在游戏代码中动态创建一个 `Performer Character` 并配置其 Live Link 主题。

```cpp
// MyPerformanceCaptureActor.h
#pragma once
#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “PerformerCharacter.h”
#include “MyPerformanceCaptureActor.generated.h”

UCLASS()
class AMyPerformanceCaptureActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPerformanceCaptureActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    APerformerCharacter* MyPerformerActor;
};

// MyPerformanceCaptureActor.cpp
#include “MyPerformanceCaptureActor.h”
#include “PerformerComponent.h”

AMyPerformanceCaptureActor::AMyPerformanceCaptureActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyPerformanceCaptureActor::BeginPlay()
{
    Super::BeginPlay();

    // 在场景中生成一个 Performer Character
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    SpawnParams.Instigator = GetInstigator();

    MyPerformerActor = GetWorld()->SpawnActor<APerformerCharacter>(APerformerCharacter::StaticClass(), GetActorLocation(), GetActorRotation(), SpawnParams);

    if (MyPerformerActor)
    {
        // 通过组件接口设置 Live Link 主题
        if (UPerformerComponent* PerformerComp = MyPerformerActor->FindComponentByClass<UPerformerComponent>())
        {
            PerformerComp->SetLiveLinkSubject(FName(“MyLiveLinkSubjectName”));
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `1693cbe0` | [Performance Capture Core] - Fix crash in GetCustomProfile on a null anim instance. Crash can occur | 修复获取自定义配置文件时因动画实例为空导致的崩溃问题。 |
| 2026-04-13 | `d3c17556` | [Performance Capture] | 性能捕捉相关更新（具体内容未在摘要中展开）。 |
| 2026-03-30 | `57683776` | Fix some UObject system access after shutdown. | 修复引擎关闭后访问 UObject 系统可能导致的问题。 |
| 2025-09-08 | `cebd36ff` | MetaHuman becomes deformed during realtime animation in UEFN if Face is selected in Controlled Skeletal Mesh. | 修复在 UEFN 中选择受控骨骼网格体面部时，MetaHuman 实时动画会变形的问题。 |
| 2025-08-18 | `534ba4a1` | [Performance Capture Core] | 性能捕捉核心相关更新（具体内容未在摘要中展开）。 |

### 维护评价

该插件创建于 2023 年底，属于较新的插件（🆕）。从 git 记录来看，它在 **2025 和 2026 年持续有更新**，特别是针对 MetaHuman 在特定环境（如 UEFN）中的问题进行了修复，表明它处于 **活跃维护** 状态。

- **优点**：由 Epic Games 官方维护，专注于解决 MetaHuman 性能捕捉的实际痛点，更新能跟进 MetaHuman 和引擎的新问题。
- **注意事项**：`.uplugin` 标记为 **实验性（IsBetaVersion=true）**，且默认未启用。这意味着其 API 和行为可能在未来版本中发生变化，不建议在需要长期稳定的核心生产流程中使用，但非常适合用于原型开发、快速验证和特定的 MetaHuman 集成项目。

**推荐度**：对于需要快速搭建 MetaHuman 实时动画驱动原型或在 UEFN 中使用 MetaHuman 动画的开发者，这是一个值得尝试的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PerformanceCaptureCore)