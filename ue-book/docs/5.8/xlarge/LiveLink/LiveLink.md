# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式、资产） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 Unreal Engine 的**实时数据流式传输框架**，用于将外部动画、动作捕捉、相机跟踪、灯光控制等设备的实时数据流式传输到引擎内部。它不是一个特定的设备驱动，而是一个**通用的数据传输基础设施**，通过"源（Source）→ 主题（Subject）→ 角色（Role）"的三层架构，将任意类型的实时数据标准化后供引擎各系统消费。

核心解决的问题：
- **跨设备标准化**：不同的动捕设备、面部追踪软件、相机跟踪系统各自有不同的数据格式，Live Link 通过 Role（角色）概念将它们统一为引擎可理解的数据类型（Transform、Animation、Camera 等）
- **实时缓冲与同步**：支持引擎时间、Scene Time（Timecode）和精确帧同步三种时间模式，内置帧缓冲、插值、丢帧统计等机制
- **网络分发**：基于 Message Bus 实现跨机器、跨进程的实时数据广播与发现
- **数据预处理管线**：在数据到达引擎消费端之前，可插入坐标轴变换、死区滤波、角色转换、骨骼重映射等预处理步骤

## 使用场景

- 你在用 MotionBuilder / Maya 做动捕实时预览 → 连接 Live Link 源，实时驱动 UE 中的角色骨骼
- 你在搭建 Virtual Production 虚拟制片流程 → 用 Live Link 将外部相机跟踪数据（如 Vicon、OptiTrack）实时传入 UE
- 你需要将一部设备的动画数据同步到多台机器 → 使用 Live Link 的 Re-broadcast 功能实现数据分发
- 你在做多人协作的虚拟制片 → 使用 LiveLinkHub 在多台设备间同步时间和动画数据
- 你需要精确控制引擎时间步长以匹配外部设备的刷新率 → 使用 `ULiveLinkCustomTimeStep` 实现 Genlock 同步
- 你想把多个动捕源的骨骼合并成一个完整骨架 → 使用 `ULiveLinkAnimationVirtualSubject` 组合多个 Subject
- 你需要为 Motion Controller 系统提供外部追踪数据 → Live Link 内置了 `IMotionController` 适配器

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateLiveLinkFrameWithSpecificRole` | 按指定角色评估 Subject 的当前帧数据 | `ULiveLinkBlueprintLibrary` |
| `EvaluateLiveLinkFrameAtWorldTimeOffset` | 按世界时间偏移评估帧数据 | `ULiveLinkBlueprintLibrary` |
| `EvaluateLiveLinkFrameAtSceneTime` | 按场景时间（Timecode）评估帧数据 | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkEnabledSubjectNames` | 获取所有已启用的 Subject 名称列表 | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjects` | 获取所有 Subject 的键列表 | `ULiveLinkBlueprintLibrary` |
| `IsLiveLinkSubjectEnabled` | 检查指定名称的 Subject 是否已启用 | `ULiveLinkBlueprintLibrary` |
| `SetLiveLinkSubjectEnabled` | 启用/禁用指定 Source 的 Subject | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjectRole` | 获取 Subject 的角色类型 | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjectState` | 获取 Subject 的连接状态 | `ULiveLinkBlueprintLibrary` |
| `PauseSubject` / `UnpauseSubject` | 暂停/恢复 Subject 的数据更新 | `ULiveLinkBlueprintLibrary` |
| `IsSourceStillValid` | 检查数据源是否仍然有效 | `ULiveLinkBlueprintLibrary` |
| `RemoveSource` | 通过句柄关闭数据源 | `ULiveLinkBlueprintLibrary` |
| `GetSourceStatus` / `GetSourceType` | 获取源的状态和类型文本 | `ULiveLinkBlueprintLibrary` |
| `GetAvailableProviders` | 异步发现网络上可用的 Message Bus 提供者 | `ULiveLinkMessageBusFinder` |
| `ConnectToProvider` | 连接到发现的 Message Bus 提供者 | `ULiveLinkMessageBusFinder` |
| `ConstructMessageBusFinder` | 构造消息总线查找器对象 | `ULiveLinkMessageBusFinder` |

### Subject Frame 数据读取节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCurves` | 获取 Subject 帧中的浮点曲线数据 | `ULiveLinkBlueprintLibrary` |
| `NumberOfTransforms` | 获取帧中的变换数量 | `ULiveLinkBlueprintLibrary` |
| `TransformNames` | 获取所有变换名称 | `ULiveLinkBlueprintLibrary` |
| `GetRootTransform` | 获取根变换 | `ULiveLinkBlueprintLibrary` |
| `GetTransformByIndex` / `GetTransformByName` | 按索引或名称获取变换 | `ULiveLinkBlueprintLibrary` |
| `GetMetadata` / `GetBasicData` | 获取元数据和基础数据 | `ULiveLinkBlueprintLibrary` |
| `GetAnimationStaticData` / `GetAnimationFrameData` | 获取动画的静态数据和帧数据 | `ULiveLinkBlueprintLibrary` |

### LiveLink Transform 操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TransformName` | 获取变换名称 | `ULiveLinkBlueprintLibrary` |
| `ParentBoneSpaceTransform` | 获取父骨骼空间变换 | `ULiveLinkBlueprintLibrary` |
| `ComponentSpaceTransform` | 获取组件（根）空间变换 | `ULiveLinkBlueprintLibrary` |
| `HasParent` / `GetParent` | 查询父变换关系 | `ULiveLinkBlueprintLibrary` |
| `ChildCount` / `GetChildren` | 查询子变换关系 | `ULiveLinkBlueprintLibrary` |

### 使用示例（蓝图描述）

**评估动画帧数据**：
1. 使用 `EvaluateLiveLinkFrameWithSpecificRole` 节点，Subject Name 输入目标角色名（如 "mocap_man"），Role 选择 `LiveLinkAnimationRole`
2. 输出的 `FLiveLinkBaseBlueprintData` 通过 Cast 拿到 `FLiveLinkAnimationFrameData`
3. 从 FrameData 中读取骨骼变换数组，驱动 AnimBP 中的骨骼网格体

**发现并连接远程数据源**：
1. 调用 `ConstructMessageBusFinder` 创建查找器对象
2. 调用 `GetAvailableProviders`（Latent 节点），等待指定时长后返回可用提供者列表
3. 从列表中选择目标提供者，调用 `ConnectToProvider` 获取 `FLiveLinkSourceHandle`
4. 后续可通过 `IsSourceStillValid`、`GetSourceStatus` 监控连接状态

**使用 Broadcast 组件广播动画**：
1. 在 Actor 上添加 `LiveLinkBroadcastComponent` 组件
2. 设置 SubjectName（默认使用 Actor 名称）
3. 设置 Role（Transform 或 Animation）
4. 设置 SourceMesh 为要广播的 SkeletalMeshComponent
5. 勾选 bEnable 开启广播

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkClient.h"
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkAnimationRole.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "LiveLinkBlueprintLibrary.h"
```

### 基本用法：获取 Client 并评估帧

```cpp
// 获取 Live Link Client（通过模块化特性系统）
ILiveLinkClient& LiveLinkClient = IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);

// 评估指定 Subject 的当前帧（动画角色）
FLiveLinkSubjectFrameData FrameData;
FLiveLinkSubjectName SubjectName("MySubject");
bool bSuccess = LiveLinkClient.EvaluateFrame_AnyThread(
    SubjectName,
    ULiveLinkAnimationRole::StaticClass(),
    FrameData
);

if (bSuccess)
{
    // 获取静态骨骼数据
    if (const FLiveLinkSkeletonStaticData* SkeletonStatic = FrameData.StaticData.Cast<FLiveLinkSkeletonStaticData>())
    {
        const TArray<FName>& BoneNames = SkeletonStatic->GetBoneNames();
        const TArray<int32>& BoneParents = SkeletonStatic->GetBoneParents();
    }

    // 获取动画帧数据
    if (const FLiveLinkAnimationFrameData* AnimFrame = FrameData.FrameData.Cast<FLiveLinkAnimationFrameData>())
    {
        const TArray<FTransform>& Transforms = AnimFrame->Transforms;
        const TArray<float>& Curves = AnimFrame->Curves;
    }
}
```

### 进阶用法：注册帧数据回调

```cpp
// 注册 Subject 的帧数据到达回调（任意线程安全）
FLiveLinkSubjectKey SubjectKey(SourceGuid, SubjectName);

FDelegateHandle StaticHandle, FrameHandle;
LiveLinkClient.RegisterForFrameDataReceived(
    SubjectKey,
    FOnLiveLinkSubjectStaticDataReceived::FDelegate::CreateLambda(
        [](const FLiveLinkSubjectKey& InSubjectKey, const FLiveLinkStaticDataStruct& InStaticData)
        {
            // 静态数据到达（骨骼结构等，通常只到达一次）
        }
    ),
    FOnLiveLinkSubjectFrameDataReceived::FDelegate::CreateLambda(
        [](const FLiveLinkSubjectKey& InSubjectKey, const FLiveLinkFrameDataStruct& InFrameData)
        {
            // 帧数据到达（每一帧都触发）
        }
    ),
    StaticHandle,
    FrameHandle
);

// 不再需要时取消注册
LiveLinkClient.UnregisterForFrameDataReceived(SubjectKey, StaticHandle, FrameHandle);
```

### 进阶用法：按 Timecode 评估帧

```cpp
// 在精确时间点评估帧数据
FLiveLinkSubjectFrameData FrameData;
FQualifiedFrameTime SceneTime(FTimecode(1, 2, 30, 15, true), FFrameRate(24, 1));

bool bSuccess = LiveLinkClient.EvaluateFrameAtSceneTime_AnyThread(
    SubjectName,
    SceneTime,
    ULiveLinkAnimationRole::StaticClass(),
    FrameData
);
```

### 进阶用法：监听源和 Subject 变化

```cpp
// 监听源变化
LiveLinkClient.OnLiveLinkSourceAdded().AddLambda(
    [](FGuid SourceGuid)
    {
        UE_LOG(LogTemp, Log, TEXT("Live Link source added: %s"), *SourceGuid.ToString());
    }
);

LiveLinkClient.OnLiveLinkSourceRemoved().AddLambda(
    [](FGuid SourceGuid)
    {
        UE_LOG(LogTemp, Log, TEXT("Live Link source removed: %s"), *SourceGuid.ToString());
    }
);

// 监听 Subject 变化
LiveLinkClient.OnLiveLinkSubjectAdded().AddLambda(
    [](FLiveLinkSubjectKey SubjectKey)
    {
        UE_LOG(LogTemp, Log, TEXT("Subject added: %s from %s"),
            *SubjectKey.SubjectName.ToString(), *SubjectKey.Source.ToString());
    }
);

// 监听 Subject 状态变化（如变为无效、暂停等）
LiveLinkClient.OnLiveLinkSubjectStateChanged().AddLambda(
    [](ELiveLinkSubjectState NewState, FLiveLinkSubjectKey SubjectKey)
    {
        // 可用于检测连接断开等状态变化
    }
);
```

## Demo 示例

### 自定义 Live Link 数据评估组件

```cpp
// MyLiveLinkEvalComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "LiveLinkClient.h"
#include "Roles/LiveLinkAnimationRole.h"
#include "MyLiveLinkEvalComponent.generated.h"

UCLASS(ClassGroup=(LiveLink), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyLiveLinkEvalComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyLiveLinkEvalComponent();

    /** 要评估的 Live Link Subject 名称 */
    UPROPERTY(EditAnywhere, Category = "LiveLink")
    FLiveLinkSubjectName SubjectName;

    /** 每帧评估并驱动骨骼网格体 */
    UPROPERTY(EditAnywhere, Category = "LiveLink")
    bool bEvaluateEveryFrame = true;

protected:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
    virtual void OnRegister() override;
    virtual void OnUnregister() override;

private:
    void EvaluateAndApply();
    ILiveLinkClient* LiveLinkClient = nullptr;
};
```

```cpp
// MyLiveLinkEvalComponent.cpp
#include "MyLiveLinkEvalComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkAnimationTypes.h"

UMyLiveLinkEvalComponent::UMyLiveLinkEvalComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyLiveLinkEvalComponent::OnRegister()
{
    Super::OnRegister();
    LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);
}

void UMyLiveLinkEvalComponent::OnUnregister()
{
    LiveLinkClient = nullptr;
    Super::OnUnregister();
}

void UMyLiveLinkEvalComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (bEvaluateEveryFrame && LiveLinkClient)
    {
        EvaluateAndApply();
    }
}

void UMyLiveLinkEvalComponent::EvaluateAndApply()
{
    FLiveLinkSubjectFrameData FrameData;
    if (!LiveLinkClient->EvaluateFrame_AnyThread(SubjectName, ULiveLinkAnimationRole::StaticClass(), FrameData))
    {
        return;
    }

    const FLiveLinkAnimationFrameData* AnimFrame = FrameData.FrameData.Cast<FLiveLinkAnimationFrameData>();
    const FLiveLinkSkeletonStaticData* SkeletonStatic = FrameData.StaticData.Cast<FLiveLinkSkeletonStaticData>();

    if (!AnimFrame || !SkeletonStatic)
    {
        return;
    }

    USkeletalMeshComponent* SkelMeshComp = GetOwner()->FindComponentByClass<USkeletalMeshComponent>();
    if (!SkelMeshComp || !SkelMeshComp->GetSkeletalMeshAsset())
    {
        return;
    }

    const TArray<FName>& BoneNames = SkeletonStatic->GetBoneNames();
    const TArray<FTransform>& Transforms = AnimFrame->Transforms;

    // 将 Live Link 变换数据应用到骨骼网格体的组件空间变换
    for (int32 i = 0; i < Transforms.Num() && i < BoneNames.Num(); ++i)
    {
        const int32 BoneIndex = SkelMeshComp->GetBoneIndex(BoneNames[i]);
        if (BoneIndex != INDEX_NONE)
        {
            SkelMeshComp->SetBoneTransformByName(BoneNames[i], Transforms[i], EBoneSpaces::ComponentSpace);
        }
    }
}
```

## 模块依赖

从各模块 Build.cs 的依赖关系中提取：

| 模块 | 用途 |
|---|---|
| `MessageEndpoint` | Message Bus 消息端点，用于网络发现和数据传输 |
| `Messenger` | 消息总线核心模块 |
| `TimeManagement` | 时间同步和 Timecode 提供者基础设施 |
| `TimedDataMonitor` | 定时数据监控界面 |
| `MovieScene` | Sequencer 集成（LiveLinkMovieScene 模块） |
| `LiveLinkInterface` | Live Link 接口定义（Role、Source 等抽象基类） |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is unavailable | 修复广播组件在子系统不可用时的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Python scripting modifies properties | 修复 Python 脚本修改属性时 PostEditChangeProperty 空指针崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the new Virtual Production plugin | 虚拟制片资产分类迁移至新插件 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复枚举格式化时可能导致乱码输出的问题 |

### 维护评价

Live Link 是 Unreal Engine 中**最核心的实时数据流框架之一**，自 2018 年从实验性状态正式转入 Animation 分类以来，一直保持**活跃维护**。

**优势**：
- 作为 Epic 虚拟制片（Virtual Production）战略的关键组件，持续获得投入
- 架构成熟，Role/Source/Subject 三层设计高度可扩展
- 215 个源文件，包含完整的蓝图 API、Message Bus 网络层、缓冲管理、插值系统
- 内置完整的预处理器和翻译器管线（坐标轴转换、死区滤波、角色转换等）
- 从 2026 年的提交记录来看，仍在持续修复 bug 和改进

**注意事项**：
- `EnabledByDefault` 为 `false`，需要在插件设置中手动启用
- 有大量 `UE_DEPRECATED` 标记的 API，表明接口在不断演进，使用时应注意版本兼容性
- 网络传输依赖 Unreal Message Bus，不支持标准的 TCP/WebSocket 直连（需通过 Message Bus 协议）
- 线程安全性是核心设计考量，许多 `_AnyThread` 后缀的方法可从任意线程调用

**推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐。这是 UE5 中处理实时外部数据流的标准方案，几乎所有的动捕、虚拟制片、外部设备集成都会依赖此插件。