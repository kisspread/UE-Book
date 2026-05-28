# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时数据链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、预设资产） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 Unreal Engine 的实时数据流式传输框架，用于将外部设备或应用程序（如 MotionBuilder、Maya、iPhone 面部捕捉、Xsens 动捕服等）产生的动画数据实时流式传输到引擎中。它基于 **Source → Subject → Role** 的三层架构：

- **Source（源）**：数据来源，如 Vicon、OptiTrack、Face AR 等外部设备或程序
- **Subject（主题）**：源提供的数据实体，如某个骨骼网格体的动画数据
- **Role（角色）**：数据类型，如动画角色（`ULiveLinkAnimationRole`）、变换角色（`ULiveLinkTransformRole`）、相机角色（`ULiveLinkCameraRole`）等

Live Link 解决的核心问题是：**在不重启引擎的情况下，将来自各种专业设备的实时动画数据无缝接入 Unreal Engine 的动画管线**。它广泛应用于虚拟制片（Virtual Production）、动作捕捉预览、实时面部动画驱动等场景。

## 使用场景

- 你在做虚拟制片 → 使用 Live Link 将摄像机追踪数据实时传入引擎中的虚拟摄像机
- 你在用 iPhone 做面部捕捉 → 使用 Live Link + ARKit 面部追踪将表情实时驱动到 MetaHuman 角色
- 你在 MotionBuilder 中编辑动画 → 通过 Live Link 实时预览编辑结果在 Unreal 中的效果
- 你需要在 Sequencer 中录制实时动作捕捉数据 → 使用 Live Link 录制轨道将数据烘焙为关键帧
- 你需要将多个实时数据源合并为一个虚拟主题 → 使用 Live Link 虚拟主题（Virtual Subject）
- 你需要在 Sequencer 中为特定 Live Link 主题设置过滤器 → 使用 Live Link 序列器过滤器

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Subject Names` | 获取所有可用的 Live Link 主题名称列表 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Role` | 获取指定主题的角色类型 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Transform` | 获取指定主题的变换数据 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Animation` | 获取指定主题的动画数据（骨骼姿态） | `ULiveLinkBlueprintLibrary` |
| `Is Live Link Subject Enabled` | 检查指定主题是否启用 | `ULiveLinkBlueprintLibrary` |
| `Set Live Link Subject Enabled` | 启用或禁用指定主题 | `ULiveLinkBlueprintLibrary` |
| `Evaluate Live Link Frame` | 使用指定角色评估一帧 Live Link 数据 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Preset` | 从预设资产加载 Live Link 配置 | `ULiveLinkPreset` |
| `Apply to Client LiveLink` | 将预设应用到当前 Live Link 客户端 | `ULiveLinkPreset` |

### 使用示例

**获取 Live Link 数据并应用到 Actor 变换：**

1. 创建一个事件图表
2. 添加 `Get Live Link Subject Transform` 节点，Subject Name 选择你的目标主题
3. 输出的 Transform 可以直接设置到 Actor 的 `Set Actor Transform` 节点
4. 使用 `Event Tick` 驱动每帧更新

**使用组件控制器驱动骨骼网格体：**

1. 在骨骼网格体 Actor 上添加 `LiveLink Component Controller` 组件
2. 在 Details 面板中设置 Subject Representation（主题表示）
3. 角色选择 `Animation`，控制器选择对应的控制器类
4. Live Link 数据将自动驱动骨骼动画

## C++ 用法

### 头文件引入

```cpp
// 核心 Live Link 模块
#include "LiveLinkClient.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "Roles/LiveLinkTransformTypes.h"

// 编辑器 UI（仅编辑器模块）
#include "LiveLinkClientPanelViews.h"
#include "SLiveLinkSubjectRepresentationPicker.h"
```

### 基本用法

**从 Live Link 客户端获取主题数据：**

```cpp
// 来源: Engine/Plugins/Animation/LiveLink/Source/LiveLinkEditor/Private/LiveLinkClientPanel.h

#include "ILiveLinkClient.h"

// 获取 Live Link 客户端单例
ILiveLinkClient* LiveLinkClient = ILiveLinkClient::Get();
if (LiveLinkClient)
{
    // 获取所有可用主题
    TArray<FLiveLinkSubjectKey> Subjects;
    LiveLinkClient->GetSubjects(Subjects);

    for (const FLiveLinkSubjectKey& SubjectKey : Subjects)
    {
        UE_LOG(LogTemp, Log, TEXT("Subject: %s from Source: %s"),
            *SubjectKey.SubjectName.ToString(),
            *SubjectKey.Source.ToString());
    }

    // 获取特定主题的最新帧数据
    FLiveLinkSubjectKey TargetKey = Subjects[0];
    ULiveLinkRole* Role = LiveLinkClient->GetSubjectRole(TargetKey);

    FLiveLinkStaticDataStruct StaticData;
    FLiveLinkFrameDataStruct FrameData;

    if (LiveLinkClient->EvaluateFrame_AnyThread(TargetKey, Role, FrameData))
    {
        // 处理帧数据...
    }
}
```

### 进阶用法

**使用 Subject Representation Picker 构建自定义编辑器 UI：**

```cpp
// 来源: Engine/Plugins/Animation/LiveLink/Source/LiveLinkEditor/Public/SLiveLinkSubjectRepresentationPicker.h

#include "SLiveLinkSubjectRepresentationPicker.h"

// 创建主题选择器
TSharedRef<SLiveLinkSubjectRepresentationPicker> Picker =
    SNew(SLiveLinkSubjectRepresentationPicker)
    .ShowSource(true)   // 显示源名称
    .ShowRole(true)     // 显示角色图标
    .Value_Lambda([this]() -> SLiveLinkSubjectRepresentationPicker::FLiveLinkSourceSubjectRole
    {
        return CurrentSubjectRole;
    })
    .OnValueChanged_Lambda([this](SLiveLinkSubjectRepresentationPicker::FLiveLinkSourceSubjectRole NewValue)
    {
        CurrentSubjectRole = NewValue;
        // 应用新的主题选择...
    });
```

**创建自定义细节面板自定义：**

```cpp
// 来源: Engine/Plugins/Animation/LiveLink/Source/LiveLinkEditor/Private/LiveLinkComponentDetailCustomization.h

#include "LiveLinkComponentDetailCustomization.h"

// 在模块启动时注册自定义细节面板
FPropertyEditorModule& PropertyModule =
    FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

PropertyModule.RegisterCustomClassLayout(
    ULiveLinkComponentController::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FLiveLinkComponentDetailCustomization::MakeInstance));
```

## Demo 示例

### 自定义 Live Link 数据监听器组件

**LiveLinkListenerComponent.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LiveLinkTypes.h"
#include "LiveLinkClient.h"
#include "LiveLinkListenerComponent.generated.h"

UCLASS(ClassGroup=(LiveLink), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API ULiveLinkListenerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    ULiveLinkListenerComponent();

    /** 要监听的 Live Link 主题名称 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Live Link")
    FLiveLinkSubjectName SubjectName;

    /** 是否自动驱动所在 Actor 的变换 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Live Link")
    bool bApplyTransformToOwner = true;

protected:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

private:
    /** 内部缓存：用于判断主题是否存在 */
    bool bSubjectValid = false;
};
```

**LiveLinkListenerComponent.cpp**

```cpp
#include "LiveLinkListenerComponent.h"
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"

ULiveLinkListenerComponent::ULiveLinkListenerComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

void ULiveLinkListenerComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    ILiveLinkClient* Client = ILiveLinkClient::Get();
    if (!Client || SubjectName.IsNone())
    {
        return;
    }

    // 检查主题是否存在
    TSubclassOf<ULiveLinkRole> Role = Client->GetSubjectRole(
        FLiveLinkSubjectKey(FGuid(), SubjectName));

    if (!Role)
    {
        return;
    }

    // 评估帧数据
    FLiveLinkFrameDataStruct FrameData;
    if (Client->EvaluateFrame_AnyThread(
        FLiveLinkSubjectKey(FGuid(), SubjectName), Role, FrameData))
    {
        // 如果是变换类型的数据，应用到 Owner Actor
        if (bApplyTransformToOwner && Role->IsChildOf(ULiveLinkTransformRole::StaticClass()))
        {
            const FLiveLinkTransformFrameData* TransformFrame =
                FrameData.Cast<FLiveLinkTransformFrameData>();

            if (TransformFrame && GetOwner())
            {
                FTransform WorldTransform(
                    TransformFrame->Transform.GetRotation(),
                    TransformFrame->Transform.GetLocation(),
                    TransformFrame->Transform.GetScale3D());
                GetOwner()->SetActorTransform(WorldTransform);
            }
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 核心接口定义（角色、静态数据、帧数据类型） |
| `LiveLink` | Live Link 运行时客户端和核心逻辑 |
| `LiveLinkComponents` | 用于将 Live Link 数据绑定到组件的运行时组件 |
| `LiveLinkEditor` | 编辑器 UI 面板、细节面板自定义、主题选择器 |
| `LiveLinkGraphNode` | 蓝图节点图中的自定义引脚和图形节点支持 |
| `LiveLinkMovieScene` | Sequencer 集成，支持在序列中录制和回放 Live Link 数据 |
| `LiveLinkMultiUser` | 多用户编辑（Multi-User Editing）集成 |
| `LiveLinkSequencer` | Sequencer 轨道过滤器，用于在 Sequencer 中过滤 Live Link 轨道 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播子系统不可用时广播组件编辑崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复 Python 脚本修改属性时 MemberProperty 为空导致的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整虚拟制片相关资产的分类和目录结构 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的输出错误 |

### 维护评价

**活跃维护** — Live Link 作为 Epic Games 虚拟制片管线的核心组件，持续获得积极维护。从 2018 年创建至今已约 8 年，它已从实验性插件（4.18 之前的 Experimental 文件夹）成长为 Production 级别的成熟功能。最近的提交集中在崩溃修复和稳定性提升方面，表明 Epic 仍在持续投入资源。

**注意事项**：
- 该插件默认未启用（`EnabledByDefault: false`），需要手动在项目设置中启用
- 作为 7 个模块组成的大型插件（215+ 源文件），架构复杂度较高
- 深度依赖 Unreal 的 Slate UI 框架，自定义编辑器 UI 扩展需要熟悉 Slate 编程模式
- 与 Sequencer、多用户编辑、蓝图系统等多个子系统紧密集成

**推荐使用**：如果你的项目涉及任何实时外部数据流（动作捕捉、面部追踪、摄像机追踪、MoCap 数据），Live Link 是官方推荐的标准化解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/en-US/animation-plugins-and-tools/live-link-in-unreal-engine/)