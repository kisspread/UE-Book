# Performance Capture Core

> Performance Capture Core Actor and Component Classes

| 属性 | 值 |
|---|---|
| 中文名 | 动捕核心 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PerformanceCaptureCore` (Runtime), `PerformanceCaptureCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PerformanceCaptureCore) | |

## 用途

PerformanceCaptureCore 是 Epic 为动作捕捉（Performance Capture）实时驱动工作流提供的基础框架插件。它解决的核心问题是：**如何在 UE5 中将外部动捕数据（通过 Live Link）实时驱动到 MetaHuman 或自定义角色上，并通过 IK Retarget 在不同骨架之间进行重定向**。

插件提供了两个关键角色类和两个关键组件：

1. **RetargetAnimInstance + 相关组件**：基于 IK Retarget Asset 在源骨架和目标骨架之间做动画重定向，使得动捕演员的动画可以映射到不同比例/骨骼结构的角色上
2. **LiveLinkInstance + 相关组件**：通过 Live Link 协议接入实时动捕数据流，驱动骨骼网格体播放

该插件将这些底层能力封装为易于使用的 Actor 和 Component，配合蓝图函数，让设计师无需编写代码即可快速搭建动捕驱动的角色。

## 使用场景

- 你在使用 Xsens、Rokoko 等动捕设备进行实时表演，需要将数据驱动到 MetaHuman 角色上
- 你在做虚拟制片（Virtual Production），需要将动捕演员的表演实时映射到数字角色
- 你在 UEFN 中做实时动捕动画，需要解决骨架差异的重定向问题
- 你需要快速原型验证一个动捕驱动的角色，不想手动配置 Live Link 和 IK Retarget 的全部细节
- 你需要在不同动捕演员和不同数字角色之间切换，通过自定义 Retarget Profile 处理特殊重定向需求

## 蓝图用法

该插件的核心设计目标就是蓝图友好。从首次提交信息和代码结构可以推断以下蓝图 API：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Set Source Performer | 设置驱动源（动捕演员） | `ACaptureCharacter` |
| Set Retarget Asset | 设置 IK 重定向资产 | `ACaptureCharacter` |
| Set Custom Retarget Profile | 设置自定义重定向配置 | `ACaptureCharacter` |
| Get LiveLink Subject | 获取 Live Link 主题名 | `APerformer` |
| Set LiveLink Subject | 设置 Live Link 主题名 | `APerformer` |
| Pause Animation | 暂停动捕动画播放 | `APerformer` |
| Get Custom Profile | 获取自定义重定向配置 | `ACaptureCharacter` |

### 使用示例

**场景 1：配置动捕驱动的 CaptureCharacter**

1. 在场景中放置一个 `ACaptureCharacter`（骨骼网格体 Actor）
2. 通过蓝图调用 `Set Retarget Asset` 节点，指定你的 IK Retarget 资产（该资产定义了源骨架到目标骨架的映射）
3. 通过 `Set Source Performer` 节点，指定提供数据的 Performer Actor
4. 如需自定义重定向行为，调用 `Set Custom Retarget Profile` 覆盖默认配置
5. 角色会自动使用 `RetargetAnimInstance` 驱动动画

**场景 2：配置 Live Link 动捕演员**

1. 在场景中放置一个 `APerformer`（Performer 骨骼网格体 Actor）
2. 通过 `Set LiveLink Subject` 节点连接到你的 Live Link 数据源（设备名/主题名）
3. 该组件会强制使用 `LiveLinkInstance` 作为动画实例，实时接收动捕数据
4. 需要暂停时调用 `Pause Animation`

**场景 3：编辑器内自定义属性面板**

放置 `ACaptureCharacter` 后，在 Detail 面板中会看到定制的 "Performance Capture" 分类，展示重定向相关的配置选项（由 `FCaptureCharacterCustomization` 提供）。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureCharacter.h"          // ACaptureCharacter 主角色类
#include "Performer.h"                 // APerformer 动捕演员类
#include "RetargetAnimInstance.h"      // 重定向动画实例
```

### 基本用法

基于插件架构推断的 C++ 用法：

```cpp
// 创建并配置一个 CaptureCharacter
ACaptureCharacter* CaptureChar = GetWorld()->SpawnActor<ACaptureCharacter>();

// 设置 IK Retarget 资产
CaptureChar->SetRetargetAsset(MyRetargetAsset);

// 设置源动捕演员
CaptureChar->SetSourcePerformer(MyPerformerActor);

// 设置自定义重定向配置
CaptureChar->SetCustomRetargetProfile(MyProfile);
```

```cpp
// 创建并配置一个 Performer
APerformer* Performer = GetWorld()->SpawnActor<APerformer>();

// 设置 Live Link 主题
Performer->SetLiveLinkSubject(FName("MyMocapDevice"));

// 暂停/恢复动捕动画
Performer->PauseAnimation(true);
```

### 编辑器自定义（PerformanceCaptureCoreEditor 模块）

`FCaptureCharacterCustomization` 继承自 `IDetailCustomization`，用于在属性面板中定制 `ACaptureCharacter` 的显示方式：

```cpp
// 注册 Detail Customization（通常在编辑器模块启动时）
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    ACaptureCharacter::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FCaptureCharacterCustomization::MakeInstance)
);
```

## Demo 示例

```cpp
// MyMocapSetup.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMocapSetup.generated.h"

class ACaptureCharacter;
class APerformer;

UCLASS()
class AMyMocapSetup : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Mocap")
    TSubclassOf<APerformer> PerformerClass;

    UPROPERTY(EditAnywhere, Category = "Mocap")
    TSubclassOf<ACaptureCharacter> CaptureCharacterClass;

    UPROPERTY(EditAnywhere, Category = "Mocap")
    FName LiveLinkSubjectName;

    UPROPERTY(EditAnywhere, Category = "Mocap")
    UObject* RetargetAsset;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Mocap")
    void SetupMocapPipeline();
};
```

```cpp
// MyMocapSetup.cpp
#include "MyMocapSetup.h"
#include "CaptureCharacter.h"
#include "Performer.h"

void AMyMocapSetup::SetupMocapPipeline()
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 1. 生成动捕演员（数据源端）
    FActorSpawnParameters SpawnParams;
    APerformer* Performer = World->SpawnActor<APerformer>(PerformerClass, FTransform::Identity, SpawnParams);
    if (Performer)
    {
        Performer->SetLiveLinkSubject(LiveLinkSubjectName);
    }

    // 2. 生成捕获角色（接收端）
    ACaptureCharacter* Character = World->SpawnActor<ACaptureCharacter>(CaptureCharacterClass, FTransform(FVector(0, 0, 0)), SpawnParams);
    if (Character)
    {
        Character->SetRetargetAsset(RetargetAsset);
        Character->SetSourcePerformer(Performer);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `IKRig` | IK 重定向系统，提供 Retarget AnimInstance 的底层支持 |
| `LiveLink` | Live Link 框架，用于接入实时动捕数据流 |
| `LiveLinkInterface` | Live Link 接口定义 |
| `AnimGraphRuntime` | 动画图运行时，支持动画实例节点 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `1693cbe0` | [Performance Capture Core] - Fix crash in GetCustomProfile on a null anim instance. Crash can occur | 修复获取自定义配置时动画实例为空导致的崩溃 |
| 2026-04-13 | `d3c17556` | [Performance Capture] | 动捕相关更新（具体细节不详） |
| 2026-03-30 | `57683776` | Fix some UObject system access after shutdown. | 修复引擎关闭后访问 UObject 系统的问题 |
| 2025-09-08 | `cebd36ff` | MetaHuman becomes deformed during realtime animation in UEFN if Face is selected in Controlled Skele | 修复 UEFN 中 MetaHuman 选择 Face 控制骨骼时实时动画变形问题 |
| 2025-08-18 | `534ba4a1` | [Performance Capture Core] | 动捕核心相关更新（具体细节不详） |

### 维护评价

- **状态**：**活跃维护中** — 最近一次更新距今不到 1 个月，近半年内有多次实质性修复
- **创建时间**：2023 年 11 月，插件相对年轻
- **风险提示**：`IsBetaVersion=true`，API 和功能可能在后续版本中发生变化
- **更新趋势**：主要集中在 crash 修复和 MetaHuman/UEFN 兼容性改进，说明该插件已在实际生产中使用，Epic 持续维护
- **推荐程度**：适合用于动捕工作流的原型开发和生产验证，但注意 Beta 状态，关键项目中需做好版本锁定和回归测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PerformanceCaptureCore)
- [官方文档]()（暂无）