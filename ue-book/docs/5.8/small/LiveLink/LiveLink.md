# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、样式资源） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 UE 的**实时数据流框架**，用于将外部应用（如动作捕捉系统、虚拟摄影机、自定义传感器等）产生的动画数据实时传输到引擎中。它解决了以下核心问题：

- **跨软件实时通信**：通过 Message Bus 协议在局域网内发现和连接数据源（如 MotionBuilder、Maya、Vicon 等）
- **多角色数据抽象**：通过 Role 系统（Transform、Animation、Camera、Light 等）统一不同类型的数据格式
- **帧数据缓冲与时序控制**：支持基于世界时间、场景时间码的插值评估，以及自定义时间步长同步
- **数据预处理与转换管线**：提供 PreProcessor、InterpolationProcessor、Translator、Remapper 四级数据处理管线
- **广播与转发**：支持将评估后的数据重新广播到网络，或通过虚拟主题合并多个数据源

Live Link 不仅是动画数据的传输通道，更是一个完整的**实时数据总线架构**。

## 使用场景

- 你有动捕设备（Vicon、OptiTrack、Xsens 等）需要实时驱动角色 → 用 Live Link + 对应的 Source 插件
- 你需要在 Maya/MotionBuilder 中预览或控制 UE 中的动画 → 用 Live Link + Maya/MotionBuilder 插件
- 你需要将外部虚拟摄影机数据实时应用到 UE 摄影机 → 用 Live Link Camera Role
- 你需要同步多个软件的 Timecode → 用 `ULiveLinkTimecodeProvider`
- 你需要将引擎帧率锁定到外部信号 → 用 `ULiveLinkCustomTimeStep`
- 你需要合并多个动捕源的骨骼数据 → 用 `ULiveLinkAnimationVirtualSubject`
- 你需要在网络上重新广播一个角色的骨骼动画 → 用 `ULiveLinkBroadcastComponent`
- 你需要在蓝图中实时获取动捕数据 → 用 `ULiveLinkBlueprintLibrary` 的 Evaluate 节点

## 模块说明

| 模块 | 说明 |
|---|---|
| **LiveLink** | 核心模块：Client、Subject、Source、MessageBus 通信、预处理器、插值器、翻译器 |
| **LiveLinkComponents** | Actor 组件：LiveLinkComponent（蓝图轮询）、BroadcastComponent（数据广播）、DataPreviewComponent（可视化） |
| **LiveLinkEditor** | 编辑器 UI：LiveLink 面板、源管理、主题管理、设置编辑器 |
| **LiveLinkGraphNode** | 蓝图图节点：自定义蓝图节点支持 |
| **LiveLinkMovieScene** | Sequencer 集成：Live Link 轨道录制与回放 |
| **LiveLinkMultiUser** | 多用户编辑支持 |
| **LiveLinkSequencer** | Sequencer 扩展功能 |

## 蓝图用法

### 核心节点

Live Link 的蓝图 API 主要通过 `ULiveLinkBlueprintLibrary` 的静态函数暴露，按功能分组如下：

#### 数据评估

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateLiveLinkFrameWithSpecificRole` | 按角色评估指定主题的当前帧 | `ULiveLinkBlueprintLibrary` |
| `EvaluateLiveLinkFrameAtWorldTimeOffset` | 按世界时间偏移评估指定主题的帧 | `ULiveLinkBlueprintLibrary` |
| `EvaluateLiveLinkFrameAtSceneTime` | 按场景时间码评估指定主题的帧 | `ULiveLinkBlueprintLibrary` |

#### 主题管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLiveLinkEnabledSubjectNames` | 获取所有已启用的主题名称列表 | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjects` | 获取所有主题（可包含禁用/虚拟主题） | `ULiveLinkBlueprintLibrary` |
| `IsLiveLinkSubjectEnabled` | 按名称判断主题是否已启用 | `ULiveLinkBlueprintLibrary` |
| `IsSpecificLiveLinkSubjectEnabled` | 按 Source+Name 判断主题是否已启用 | `ULiveLinkBlueprintLibrary` |
| `SetLiveLinkSubjectEnabled` | 启用/禁用指定源的主题（同名主题互斥） | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjectState` | 获取主题状态（Connected/Invalid/Paused等） | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjectRole` | 获取主题的角色类型 | `ULiveLinkBlueprintLibrary` |
| `PauseSubject` | 暂停主题，冻结到最后数据 | `ULiveLinkBlueprintLibrary` |
| `UnpauseSubject` | 恢复主题运行 | `ULiveLinkBlueprintLibrary` |

#### 源管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsSourceStillValid` | 检查源是否仍然有效 | `ULiveLinkBlueprintLibrary` |
| `RemoveSource` | 通过句柄移除源 | `ULiveLinkBlueprintLibrary` |
| `GetSourceStatus` | 获取源的状态文本 | `ULiveLinkBlueprintLibrary` |
| `GetSourceType` | 获取源的类型文本 | `ULiveLinkBlueprintLibrary` |
| `GetSourceMachineName` | 获取源所在机器名称 | `ULiveLinkBlueprintLibrary` |

#### 帧数据解包（FSubjectFrameHandle）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCurves` | 获取帧中的浮点曲线数据（TMap） | `ULiveLinkBlueprintLibrary` |
| `NumberOfTransforms` | 获取帧中变换数量 | `ULiveLinkBlueprintLibrary` |
| `TransformNames` | 获取所有变换名称 | `ULiveLinkBlueprintLibrary` |
| `GetRootTransform` | 获取根变换 | `ULiveLinkBlueprintLibrary` |
| `GetTransformByIndex` | 按索引获取变换 | `ULiveLinkBlueprintLibrary` |
| `GetTransformByName` | 按名称获取变换 | `ULiveLinkBlueprintLibrary` |
| `GetMetadata` | 获取主题元数据 | `ULiveLinkBlueprintLibrary` |
| `GetBasicData` | 获取基础数据 | `ULiveLinkBlueprintLibrary` |
| `GetAnimationStaticData` | 获取动画静态数据（骨骼名称等） | `ULiveLinkBlueprintLibrary` |
| `GetAnimationFrameData` | 获取动画帧数据 | `ULiveLinkBlueprintLibrary` |

#### FLiveLinkTransform 解包

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TransformName` | 获取变换名称 | `ULiveLinkBlueprintLibrary` |
| `ParentBoneSpaceTransform` | 获取父骨骼空间变换 | `ULiveLinkBlueprintLibrary` |
| `ComponentSpaceTransform` | 获取组件空间（根空间）变换 | `ULiveLinkBlueprintLibrary` |
| `HasParent` | 是否有父变换 | `ULiveLinkBlueprintLibrary` |
| `GetParent` | 获取父变换 | `ULiveLinkBlueprintLibrary` |
| `ChildCount` | 获取子变换数量 | `ULiveLinkBlueprintLibrary` |
| `GetChildren` | 获取所有子变换 | `ULiveLinkBlueprintLibrary` |

#### 网络发现

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConstructMessageBusFinder` | 创建 Message Bus 发现器 | `ULiveLinkMessageBusFinder` |
| `GetAvailableProviders` | 异步搜索网络上的 Live Link 提供者 | `ULiveLinkMessageBusFinder` |
| `ConnectToProvider` | 连接到发现的提供者 | `ULiveLinkMessageBusFinder` |

### 使用示例（蓝图描述）

**示例 1：实时评估动画数据**

1. 创建 `EvaluateLiveLinkFrameWithSpecificRole` 节点
2. 设置 `SubjectName` 为你的动捕主题名（如 "Body"）
3. 设置 `Role` 为 `LiveLinkAnimationRole`
4. 输出的 `OutBlueprintData` 自动转换为 `FLiveLinkAnimationFrameBlueprintData`
5. 用 `GetAnimationFrameData` 从输出结构中提取骨骼变换和曲线数据

**示例 2：搜索并连接 Message Bus 源**

1. 创建 `ConstructMessageBusFinder` 节点，返回 Finder 对象
2. 连接 `GetAvailableProviders` 节点（设置 Duration = 0.2），通过 Latent 输出获取 `AvailableProviders` 数组
3. 遍历数组，选择目标提供者（通过 `Name`、`MachineName` 过滤）
4. 调用 `ConnectToProvider` 连接选中的提供者，获得 `SourceHandle`

**示例 3：使用预构建的 LiveLinkPreset**

1. 创建 `ULiveLinkPreset` 资产，配置好源和主题
2. 在 BeginPlay 中调用 `ApplyToClientLatent` 应用预设
3. 预设会自动配置源连接和主题订阅

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkClient.h"
#include "ILiveLinkModule.h"
#include "LiveLinkBlueprintLibrary.h"
```

### 基本用法：获取 Client 并评估帧数据

来源：`Public/LiveLinkClient.h`

```cpp
// 获取 LiveLink 模块和客户端（通过 Modular Features）
ILiveLinkClient* Client = IModularFeatures::Get().GetModularFeaturePtr<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);
if (!Client) return;

// 定义要评估的主题和角色
FLiveLinkSubjectKey SubjectKey(FGuid(), FName("MySubject"));
TSubclassOf<ULiveLinkRole> Role = ULiveLinkAnimationRole::StaticClass();

// 在任意线程评估当前帧
FLiveLinkSubjectFrameData FrameData;
if (Client->EvaluateFrame_AnyThread(SubjectKey.SubjectName, Role, FrameData))
{
    // 获取动画帧数据
    if (FLiveLinkAnimationFrameData* AnimData = FrameData.FrameData.Cast<FLiveLinkAnimationFrameData>())
    {
        // 使用骨骼变换数组
        const TArray<FTransform>& Transforms = AnimData->Transforms;
        // 使用曲线数据
        const TArray<float>& CurveValues = AnimData->PropertyValues;
    }
}
```

### 基本用法：监听主题数据更新

来源：`Public/LiveLinkClient.h`

```cpp
// 注册帧数据回调
FLiveLinkSubjectKey SubjectKey(SourceGuid, FName("MySubject"));
FDelegateHandle StaticHandle, FrameHandle;

Client->RegisterForFrameDataReceived(
    SubjectKey,
    FOnLiveLinkSubjectStaticDataReceived::FDelegate::CreateLambda(
        [](const FLiveLinkSubjectKey& InKey, const FLiveLinkStaticDataStruct& InStaticData)
        {
            // 静态数据更新（骨骼名称列表等）
        }),
    FOnLiveLinkSubjectFrameDataReceived::FDelegate::CreateLambda(
        [](const FLiveLinkSubjectKey& InKey, const FLiveLinkFrameDataStruct& InFrameData)
        {
            // 每帧数据到达
        }),
    StaticHandle,
    FrameHandle
);

// 取消注册
Client->UnregisterForFrameDataReceived(SubjectKey, StaticHandle, FrameHandle);
```

### 基本用法：注册自定义 Source

来源：`Public/LiveLinkClient.h`

```cpp
// 创建自定义源并注册到客户端
TSharedPtr<IMyLiveLinkSource> MySource = MakeShared<IMyLiveLinkSource>();
FGuid SourceGuid = Client->AddSource(MySource);

// 推送静态数据（骨骼名称等）
Client->PushSubjectStaticData_AnyThread(
    FLiveLinkSubjectKey(SourceGuid, SubjectName),
    ULiveLinkAnimationRole::StaticClass(),
    MoveTemp(StaticData)
);

// 推送帧数据
Client->PushSubjectFrameData_AnyThread(
    FLiveLinkSubjectKey(SourceGuid, SubjectName),
    MoveTemp(FrameData)
);
```

### 进阶用法：基于 MessageBus 自动发现和连接

来源：`Public/LiveLinkMessageBusFinder.h`、`Public/LiveLinkMessageBusSource.h`

```cpp
// 创建 Finder 并搜索网络
ULiveLinkMessageBusFinder* Finder = ULiveLinkMessageBusFinder::ConstructMessageBusFinder();
Finder->PollNetwork();
// 等待响应后获取结果
TArray<FProviderPollResult> Providers;
Finder->GetPollResults(Providers);

// 选择并连接
if (Providers.Num() > 0)
{
    FLiveLinkSourceHandle SourceHandle;
    ULiveLinkMessageBusFinder::ConnectToProvider(Providers[0], SourceHandle);
}
```

### 进阶用法：使用预处理器管线

来源：`Public/PreProcessor/LiveLinkAxisSwitchPreProcessor.h`

```cpp
// 在主题设置中配置预处理器
// 1. 创建轴转换预处理器
ULiveLinkTransformAxisSwitchPreProcessor* AxisSwitch = NewObject<ULiveLinkTransformAxisSwitchPreProcessor>();
AxisSwitch->FrontAxis = ELiveLinkAxis::X;
AxisSwitch->RightAxis = ELiveLinkAxis::YNeg;  // 翻转 Y 轴
AxisSwitch->UpAxis = ELiveLinkAxis::Z;

// 2. 设置到主题配置中（通常在 Subject Settings 的预处理器列表中）
```

### 进阶用法：角色翻译（Translator）

来源：`Public/Translator/LiveLinkTransformRoleToAnimation.h`

```cpp
// 将 Transform 角色数据翻译为 Animation 角色
ULiveLinkTransformRoleToAnimation* Translator = NewObject<ULiveLinkTransformRoleToAnimation>();
Translator->OutputBoneName = FName("Root");

// 可手动调用 Translate
ULiveLinkTransformRoleToAnimation::FLiveLinkTransformRoleToAnimationWorker Worker;
Worker.OutputBoneName = Translator->OutputBoneName;

FLiveLinkSubjectFrameData OutFrame;
Worker.Translate(InStaticData, InFrameData, OutFrame);
```

## Demo 示例

### 最小示例：Actor 组件每帧获取 Live Link 动画数据

**MyLiveLinkActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkClient.h"
#include "Roles/LiveLinkAnimationRole.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "MyLiveLinkActor.generated.h"

UCLASS()
class AMyLiveLinkActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLiveLinkActor();

    UPROPERTY(EditAnywhere, Category = "LiveLink")
    FLiveLinkSubjectName LiveLinkSubject;

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    ILiveLinkClient* LiveLinkClient = nullptr;
    FDelegateHandle FrameDataHandle;
};
```

**MyLiveLinkActor.cpp**

```cpp
#include "MyLiveLinkActor.h"
#include "ILiveLinkClient.h"

AMyLiveLinkActor::AMyLiveLinkActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyLiveLinkActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 LiveLink Client
    LiveLinkClient = IModularFeatures::Get().GetModularFeaturePtr<ILiveLinkClient>(
        ILiveLinkClient::ModularFeatureName);

    // 注册帧数据回调（任意线程安全）
    if (LiveLinkClient)
    {
        FLiveLinkSubjectKey SubjectKey(FGuid(), LiveLinkSubject.Name);
        LiveLinkClient->RegisterForFrameDataReceived(
            SubjectKey,
            FOnLiveLinkSubjectStaticDataReceived::FDelegate::CreateLambda(
                [](const FLiveLinkSubjectKey& Key, const FLiveLinkStaticDataStruct& StaticData)
                {
                    UE_LOG(LogTemp, Log, TEXT("LiveLink: Static data received for %s"), *Key.SubjectName.ToString());
                }),
            FOnLiveLinkSubjectFrameDataReceived::FDelegate::CreateLambda(
                [this](const FLiveLinkSubjectKey& Key, const FLiveLinkFrameDataStruct& FrameData)
                {
                    // 在这里处理每帧数据
                    if (const FLiveLinkAnimationFrameData* AnimFrame = FrameData.Cast<FLiveLinkAnimationFrameData>())
                    {
                        // AnimFrame->Transforms 包含所有骨骼变换
                        // AnimFrame->PropertyValues 包含曲线数据
                    }
                }),
            // 本示例不需要静态数据句柄
            *new FDelegateHandle(),
            FrameDataHandle
        );
    }
}

void AMyLiveLinkActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!LiveLinkClient) return;

    // 方式 1：评估最新帧
    FLiveLinkSubjectFrameData FrameData;
    if (LiveLinkClient->EvaluateFrame_AnyThread(
            LiveLinkSubject.Name,
            ULiveLinkAnimationRole::StaticClass(),
            FrameData))
    {
        if (auto* AnimData = FrameData.FrameData.Cast<FLiveLinkAnimationFrameData>())
        {
            const TArray<FTransform>& BoneTransforms = AnimData->Transforms;
            // 使用变换数据...
        }
    }

    // 方式 2：按世界时间评估（带插值）
    FLiveLinkSubjectFrameData TimeFrameData;
    if (LiveLinkClient->EvaluateFrameAtWorldTime_AnyThread(
            LiveLinkSubject.Name,
            GetWorld()->GetTimeSeconds(),
            ULiveLinkAnimationRole::StaticClass(),
            TimeFrameData))
    {
        // 使用时间同步的帧数据...
    }
}
```

## 模块依赖

LiveLink 核心模块依赖了以下非标准模块：

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | LiveLink 接口定义（Role、Source、Subject 抽象基类） |
| `TimeManagement` | 时间同步、自定义时间步长、Timecode 提供者 |
| `Interpolation` | 曲线插值支持 |
| `MessageEndpoint` | UE Messaging 框架端点（MessageBus 通信） |
| `Networking` | 网络传输层 |
| `LiveLinkMessageBusFramework` | MessageBus 协议消息定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播组件编辑器崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复浮点精度警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复编辑器属性变更时的空指针崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作用品资产分类迁移 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复枚举格式化输出问题 |

### 维护评价

- **创建时间**：2018 年 2 月，约 8 年历史
- **活跃程度**：🟢 **活跃维护中** — 最近一次更新在 2026 年 5 月，更新频率稳定
- **成熟度**：作为 UE 官方动画管线核心组件，已从实验性毕业为正式模块
- **代码规模**：215 个源文件、7 个模块，属于大型插件
- **注意事项**：
  - `EnabledByDefault = false`，需要在项目设置中手动启用
  - 部分 API（如 `EvaluateLiveLinkFrame` 带 SubjectRepresentation 参数）已在 4.23 标记为 Deprecated
  - `LiveLinkCustomTimeStep` 使用了 LockStep 模式时需注意引擎性能瓶颈
- **推荐**：⭐ **强烈推荐** — 任何需要实时外部数据流入 UE 的项目都应使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/en-US/animation/live-link-in-unreal-engine/)（无 .uplugin DocsURL，使用通用文档链接）