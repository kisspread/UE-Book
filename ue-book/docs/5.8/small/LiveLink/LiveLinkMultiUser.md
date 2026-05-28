# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 Unreal Engine 的核心动画数据流系统，用于在外部应用程序（如 MotionBuilder、Maya、iPhone 面部捕捉设备、VR 追踪系统等）和 UE5 之间实时传输动画数据。

该插件解决的核心问题是：**将外部设备或软件产生的实时动画数据（骨骼变换、面部表情、相机参数、光照参数等任意结构化数据）标准化、流式传输并注入到 Unreal Engine 的动画系统中**。它采用发布-订阅架构，支持任意数据主题（Subject），可以将来自不同源的数据统一到一个框架下管理。

Live Link 从 4.19 版本从 Experimental 迁移到正式的 Animation 分类，至今已成为虚拟制片（Virtual Production）、动作捕捉、实时预览等领域的基础设施。

## 使用场景

- 你在使用 Vicon、OptiTrack 等动捕系统进行实时表演捕捉 → 用 Live Link 流式传输骨骼数据
- 你需要将 iPhone 的 ARKit 面部动画数据实时应用到 MetaHuman → 用 Live Link + LiveLinkFace
- 你在 Maya 中调整动画并想实时预览 UE5 中的效果 → 用 Maya Live Link 插件
- 你需要在 Sequencer 中录制外部设备的动画数据 → 用 Live Link + LiveLinkSequencer
- 你在进行多用户虚拟制片 → 用 LiveLinkMultiUser 同步数据
- 你需要将灯光控制台的 DMX 数据映射到场景灯光 → 用 Live Link 自定义主题

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLiveLinkSubjects` | 获取所有可用的 Live Link 主题列表 | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjectRole` | 获取指定主题的角色类型 | `ULiveLinkBlueprintLibrary` |
| `GetAnimationStaticData` | 获取骨骼动画的静态数据（骨骼名称、曲线名称等） | `ULiveLinkBlueprintLibrary` |
| `GetAnimationFrameData` | 获取骨骼动画的当前帧数据（变换、曲线值） | `ULiveLinkBlueprintLibrary` |
| `GetTransformByName` | 按名称从帧数据中提取指定骨骼的变换 | `ULiveLinkBlueprintLibrary` |
| `GetPropertyValue` | 从帧数据中获取指定属性的值 | `ULiveLinkBlueprintLibrary` |
| `IsSourceValid` | 检查 Live Link 源是否有效 | `ULiveLinkBlueprintLibrary` |
| `EvaluateLiveLinkFrame` | 评估一帧 Live Link 数据 | `ULiveLinkBlueprintLibrary` |

### Live Link 组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Live Link Component` | 组件，将 Live Link 骨骼数据应用到骨骼网格体 | `ULiveLinkComponentController` |
| `Live Link Controller` | 控制器，驱动 SkeletalMeshComponent 的动画 | `ULiveLinkComponentController` |
| `Live Link Instance` | Live Link 动画实例，直接驱动角色动画蓝图 | `ULiveLinkInstance` |

### 使用示例（蓝图描述）

**基础用法 — 将外部动捕数据应用到角色：**

1. 在场景中的 Skeletal Mesh Actor 上，添加 `Live Link Component Controller`
2. 在组件属性中，设置 `Subject Representation` 选择要订阅的 Live Link 主题
3. 设置 `Skeletal Mesh Component` 引用指向目标骨骼网格体
4. 运行后，外部源的骨骼数据会实时驱动角色

**动画蓝图中使用：**

1. 在 Animation Blueprint 中，添加 `Live Link Instance` 节点
2. 将其作为动画图的输入或与现有动画混合
3. 在节点属性中指定 Live Link 主题
4. 该节点会输出标准的 Animation Pose，可与其他动画节点混合

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkComponentController.h"
#include "LiveLinkRole.h"
#include "LiveLinkTypes.h"
#include "LiveLinkSubjectSettings.h"
#include "Roles/LiveLinkAnimationRole.h"
#include "Roles/LiveLinkAnimationTypes.h"
```

### 基本用法 — 获取 Live Link 主题数据

```cpp
// 获取所有可用的 Live Link 主题
TArray<FLiveLinkSubjectKey> Subjects;
ULiveLinkBlueprintLibrary::GetAllSubjects(Subjects);

for (const FLiveLinkSubjectKey& Subject : Subjects)
{
    UE_LOG(LogTemp, Log, TEXT("Subject: %s, Source: %s"),
        *Subject.SubjectName.ToString(),
        *Subject.Source.ToString());
}

// 检查主题是否有效
FName SubjectName("MyMotionCapture");
bool bValid = ULiveLinkBlueprintLibrary::IsSubjectValid(SubjectName);
```

### 基本用法 — 评估动画帧数据

```cpp
#include "Roles/LiveLinkAnimationRole.h"
#include "Roles/LiveLinkAnimationTypes.h"

// 评估当前帧的骨骼动画数据
FLiveLinkSubjectRepresentation SubjectRep;
SubjectRep.Subject = FName("MySubject");
SubjectRep.Role = ULiveLinkAnimationRole::StaticClass();

FLiveLinkSubjectFrameData FrameData;
bool bSuccess = ULiveLinkBlueprintLibrary::EvaluateLiveLinkFrame(
    SubjectRep,
    ULiveLinkAnimationRole::StaticClass(),
    FrameData
);

if (bSuccess)
{
    FLiveLinkAnimationFrameData* AnimFrameData = 
        FrameData.FrameData.Cast<FLiveLinkAnimationFrameData>();
    
    if (AnimFrameData)
    {
        // 获取骨骼变换数组
        const TArray<FTransform>& Transforms = AnimFrameData->Transforms;
        
        // 获取曲线值
        const TArray<float>& Curves = AnimFrameData->CurveElements.Values;
        
        UE_LOG(LogTemp, Log, TEXT("Bones: %d, Curves: %d"),
            Transforms.Num(), Curves.Num());
    }
}
```

### 进阶用法 — 自定义 Live Link 角色和主题

```cpp
#include "LiveLinkRole.h"
#include "LiveLinkFrameInterpolationProcessor.h"

// 定义自定义 Live Link 角色
// 需要创建 ULiveLinkRole 子类以及对应的 StaticData / FrameData 结构

// 通过 Live Link Client 订阅数据
#include "ILiveLinkClient.h"

ILiveLinkClient* LiveLinkClient = 
    IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(
        ILiveLinkClient::ModularFeatureName);

if (LiveLinkClient)
{
    // 创建自定义源
    FLiveLinkSourceHandle SourceHandle;
    // 使用已注册的源工厂创建源
    // LiveLinkClient->CreateSource(...)
}
```

### 进阶用法 — Live Link 蓝图函数库

```cpp
#include "LiveLinkBlueprintLibrary.h"

// 获取主题的静态数据
FLiveLinkSubjectName SubjectName;
SubjectName.Name = FName("MySubject");

FLiveLinkStaticDataStruct StaticData;
bool bHasStaticData = ULiveLinkBlueprintLibrary::GetSubjectStaticDataStruct(
    SubjectName, ULiveLinkAnimationRole::StaticClass(), StaticData);

if (bHasStaticData)
{
    FLiveLinkSkeletonStaticData* SkelStatic = 
        StaticData.Cast<FLiveLinkSkeletonStaticData>();
    if (SkelStatic)
    {
        const TArray<FName>& BoneNames = SkelStatic->PropertyNames;
        UE_LOG(LogTemp, Log, TEXT("Bone count: %d"), BoneNames.Num());
    }
}
```

## Demo 示例

### 自定义 Live Link 数据处理组件

```cpp
// MyLiveLinkProcessor.h
#pragma once

#include "Components/ActorComponent.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkAnimationRole.h"
#include "MyLiveLinkProcessor.generated.h"

UCLASS(ClassGroup=(LiveLink), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyLiveLinkProcessor : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyLiveLinkProcessor();

    UPROPERTY(EditAnywhere, Category="Live Link")
    FLiveLinkSubjectName SubjectName;

    UPROPERTY(EditAnywhere, Category="Live Link")
    FName BoneNameToTrack;

    /** 获取被追踪骨骼的当前位置 */
    UFUNCTION(BlueprintCallable, Category="Live Link")
    FVector GetTrackedBoneLocation() const;

    /** 检查主题是否有有效数据 */
    UFUNCTION(BlueprintCallable, Category="Live Link")
    bool HasValidData() const;

protected:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

private:
    mutable FTransform CachedBoneTransform;
};
```

```cpp
// MyLiveLinkProcessor.cpp
#include "MyLiveLinkProcessor.h"
#include "LiveLinkBlueprintLibrary.h"

UMyLiveLinkProcessor::UMyLiveLinkProcessor()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PrePhysics;
    SubjectName.Name = FName("Default");
    BoneNameToTrack = FName("head");
}

bool UMyLiveLinkProcessor::HasValidData() const
{
    return ULiveLinkBlueprintLibrary::IsSubjectValid(SubjectName.Name);
}

FVector UMyLiveLinkProcessor::GetTrackedBoneLocation() const
{
    return CachedBoneTransform.GetLocation();
}

void UMyLiveLinkProcessor::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!HasValidData())
    {
        return;
    }

    // 评估当前帧
    FLiveLinkSubjectRepresentation SubjectRep;
    SubjectRep.Subject = SubjectName.Name;
    SubjectRep.Role = ULiveLinkAnimationRole::StaticClass();

    FLiveLinkSubjectFrameData FrameData;
    if (ULiveLinkBlueprintLibrary::EvaluateLiveLinkFrame(
            SubjectRep, ULiveLinkAnimationRole::StaticClass(), FrameData))
    {
        FLiveLinkAnimationFrameData* AnimData = 
            FrameData.FrameData.Cast<FLiveLinkAnimationFrameData>();

        if (AnimData)
        {
            // 通过静态数据找到骨骼索引
            FLiveLinkSubjectFrameData StaticFrameData;
            FLiveLinkStaticDataStruct StaticData;
            
            if (ULiveLinkBlueprintLibrary::GetSubjectStaticDataStruct(
                    SubjectName, ULiveLinkAnimationRole::StaticClass(), StaticData))
            {
                FLiveLinkSkeletonStaticData* SkelStatic = 
                    StaticData.Cast<FLiveLinkSkeletonStaticData>();
                
                if (SkelStatic)
                {
                    int32 BoneIndex = SkelStatic->PropertyNames.IndexOfByKey(BoneNameToTrack);
                    if (BoneIndex != INDEX_NONE && BoneIndex < AnimData->Transforms.Num())
                    {
                        CachedBoneTransform = AnimData->Transforms[BoneIndex];
                    }
                }
            }
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 核心接口和类型定义（角色、主题、数据类型） |
| `LiveLink` | Live Link 运行时核心，包含客户端、源、连接管理 |
| `LiveLinkComponents` | Actor 组件，将 Live Link 数据应用到场景对象 |
| `LiveLinkEditor` | 编辑器 UI，Live Link 面板、源配置等 |
| `LiveLinkGraphNode` | 动画蓝图中的 Live Link 节点 |
| `LiveLinkMovieScene` | Sequencer 集成，录制和回放 Live Link 数据 |
| `LiveLinkMultiUser` | 多用户编辑支持 |
| `LiveLinkSequencer` | Sequencer 中的 Live Link 录制功能 |

使用该插件时，你的模块通常需要依赖 `LiveLink`、`LiveLinkInterface` 和 `LiveLinkComponents`。如果需要在编辑器中配置 Live Link 源，还需依赖 `LiveLinkEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播组件属性变更时崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的类型截断警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Python 脚本触发 | 修复 Python 脚本触发的属性编辑崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories | 虚拟制片资产分类调整 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复枚举格式化导致的错误输出 |

### 维护评价

Live Link 是 Unreal Engine 虚拟制片管线的核心组件，自 2018 年引入以来持续活跃维护。2026 年 5 月仍有多次功能性提交，包括 bug 修复和稳定性改进。该插件：

- **状态**：🟢 活跃维护中
- **成熟度**：经过 8 年演进，已从实验性功能发展为稳定的基础设施
- **更新频率**：近期内仍有多次实质性更新，主要是稳定性修复
- **推荐**：✅ 强烈推荐使用，这是 UE5 虚拟制片和实时动捕的标准方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/en-US/animation-live-link-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink/Source/LiveLink)