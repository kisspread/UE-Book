# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、可视化资源） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-03-24 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink) | |

---

## 模块概览

Live Link 是 UE5 中用于**实时流式传输动画数据**的核心框架。它提供了一个标准化的协议和管线，让外部设备（动作捕捉、面部捕捉、虚拟摄像机、灯光控制器等）能够将数据实时推送到引擎中。

本插件包含 7 个模块，按功能划分如下：

| 模块 | 类型 | 职责 |
|---|---|---|
| **LiveLink** | Runtime | 核心框架：客户端、数据源、Subject 管理、帧处理管线 |
| **LiveLinkComponents** | Runtime | Actor 组件，用于在蓝图中消费 Live Link 数据 |
| **LiveLinkEditor** | Runtime | 编辑器 UI：Live Link 面板、源工厂、Subject 配置界面 |
| **LiveLinkGraphNode** | Runtime | 动画蓝图节点，用于在 AnimBP 中直接使用 Live Link 数据 |
| **LiveLinkMovieScene** | Runtime | Sequencer 集成，支持在时间线上录制/回放 Live Link 数据 |
| **LiveLinkMultiUser** | Runtime | 多用户编辑集成，同步 Live Link 配置到所有协作用户 |
| **LiveLinkSequencer** | Runtime | Sequencer 扩展，提供 Live Link 录制和回放的高级功能 |

---

## 用途

Live Link 解决的核心问题是：**如何将外部实时数据（动画、变换、相机、灯光等）标准化地接入 UE5**。

它存在的原因：
- **统一协议**：不同厂商的动作捕捉、面部追踪、虚拟相机等设备使用不同的数据格式，Live Link 提供统一的 Role/Subject 框架来抽象这些差异
- **实时管线**：提供完整的数据处理管线——预处理（PreProcessor）→ 帧插值（Interpolation）→ 翻译（Translator）→ 消费
- **多源管理**：同时管理多个数据源和多个 Subject，支持暂停、重映射、虚拟 Subject 组合
- **编辑器集成**：在编辑器中即可预览和调试实时数据，无需进入 Play 模式
- **录制回放**：与 Sequencer 集成，可以录制实时数据并在时间线上回放

## 使用场景

- 你在做虚拟制片（Virtual Production）→ 用 Live Link 接收摄像机追踪数据，实时驱动虚拟摄像机
- 你在做动作捕捉表演 → 用 Live Link 接收骨骼动画数据，实时预览角色动画
- 你在做面部动画 → 用 Live Link 接收面部捕捉数据（ARKit/MetaHuman Animator），驱动面部骨骼
- 你需要多个外部设备同步 → 用 Live Link 的 Timecode Provider 和 CustomTimeStep 同步引擎时间
- 你需要将动画数据广播给其他 UE 实例 → 用 LiveLinkBroadcastComponent
- 你需要在 Sequencer 中录制实时表演 → 用 LiveLinkMovieScene 模块
- 你需要组合多个动作捕捉源（如身体+手部）→ 用 Animation Virtual Subject

---

## 蓝图用法

### 核心节点

#### LiveLinkComponent（数据消费）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnLiveLinkUpdated` | 事件：当有新的 Live Link 数据可用时触发（包括编辑器中） | `ULiveLinkComponent` |

#### LiveLinkBlueprintLibrary（数据访问）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCurves` | 获取 Subject 帧中的浮点曲线数据 | `ULiveLinkBlueprintLibrary` |
| `NumberOfTransforms` | 获取 Subject 帧中的变换数量 | `ULiveLinkBlueprintLibrary` |
| `TransformNames` | 获取所有变换的名称列表 | `ULiveLinkBlueprintLibrary` |
| `GetRootTransform` | 获取根变换 | `ULiveLinkBlueprintLibrary` |
| `GetTransformByIndex` | 按索引获取变换 | `ULiveLinkBlueprintLibrary` |
| `GetTransformByName` | 按名称获取变换 | `ULiveLinkBlueprintLibrary` |
| `GetMetadata` | 获取 Subject 元数据 | `ULiveLinkBlueprintLibrary` |
| `GetBasicData` | 获取基础蓝图数据 | `ULiveLinkBlueprintLibrary` |
| `GetAnimationStaticData` | 获取动画静态数据（骨骼名称、层级等） | `ULiveLinkBlueprintLibrary` |
| `GetAnimationFrameData` | 获取动画帧数据（骨骼变换、曲线等） | `ULiveLinkBlueprintLibrary` |
| `TransformName` | 获取 LiveLinkTransform 的名称 | `ULiveLinkBlueprintLibrary` |
| `ParentBoneSpaceTransform` | 获取父骨骼空间下的变换 | `ULiveLinkBlueprintLibrary` |
| `ComponentSpaceTransform` | 获取组件空间下的变换 | `ULiveLinkBlueprintLibrary` |
| `HasParent` | 检查变换是否有父级 | `ULiveLinkBlueprintLibrary` |
| `GetPropertyValue` | 获取基础数据中的属性值 | `ULiveLinkBlueprintLibrary` |

#### LiveLinkPreset（预设管理）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyToClientLatent` | 异步应用预设到客户端（移除旧源/Subject，添加预设中的） | `ULiveLinkPreset` |
| `AddToClient` | 将预设中的源和 Subject 添加到客户端（保留现有） | `ULiveLinkPreset` |
| `BuildFromClient` | 从当前客户端状态构建预设 | `ULiveLinkPreset` |

#### LiveLinkBroadcastComponent（数据广播）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bEnable` | 控制是否广播数据 | `ULiveLinkBroadcastComponent` |
| `SubjectName` | 广播的 Subject 名称（默认为 Actor 名称） | `ULiveLinkBroadcastComponent` |
| `Role` | 选择广播的角色类型（Transform/Animation） | `ULiveLinkBroadcastComponent` |
| `SourceMesh` | 指定要广播的骨骼网格体组件 | `ULiveLinkBroadcastComponent` |
| `AllowedBoneNames` | 可选的骨骼白名单 | `ULiveLinkBroadcastComponent` |
| `AllowedCurveNames` | 可选的曲线白名单 | `ULiveLinkBroadcastComponent` |

#### LiveLinkDataPreview（数据可视化）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEnableLiveLinkData` | 启用/禁用 Live Link 数据评估 | `ALiveLinkDataPreview` |
| `InitializeSubjects` | 初始化所有 Subject 的可视化 | `ALiveLinkDataPreview` |
| `Subjects` | 要可视化的 Subject 列表 | `ALiveLinkDataPreview` |
| `bDrawLabels` | 是否绘制标签 | `ALiveLinkDataPreview` |

#### LiveLinkDataPreviewComponent（组件级可视化）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEvaluateLiveLinkData` | 启用/禁用动画评估 | `ULiveLinkDataPreviewComponent` |
| `SetDrawLabels` | 显示/隐藏标签 | `ULiveLinkDataPreviewComponent` |
| `SubjectName` | 要预览的 Subject 名称 | `ULiveLinkDataPreviewComponent` |
| `BoneVisualType` | 骨骼可视化类型（Joint/Bone） | `ULiveLinkDataPreviewComponent` |

### 使用示例（蓝图描述）

**场景 1：在 Actor 中消费 Live Link 动画数据**

1. 在 Actor 上添加 `LiveLinkComponent`（搜索 "Live Link Skeletal Animation"）
2. 在组件的 `OnLiveLinkUpdated` 事件中绑定逻辑
3. 使用 `LiveLinkBlueprintLibrary` 的 `GetAnimationFrameData` 获取骨骼变换
4. 将变换数据应用到 SkeletalMeshComponent

**场景 2：广播 Actor 的动画数据**

1. 在 Actor 上添加 `LiveLinkBroadcastComponent`
2. 设置 `SubjectName` 为广播名称
3. 选择 `Role`（如 Animation Role）
4. 将 `SourceMesh` 指向 SkeletalMeshComponent
5. 可选：设置 `AllowedBoneNames` 过滤特定骨骼

**场景 3：使用预设快速配置**

1. 创建 `ULiveLinkPreset` 资产
2. 在编辑器中配置源和 Subject
3. 在蓝图中调用 `ApplyToClientLatent` 异步应用预设

---

## C++ 用法

### 头文件引入

```cpp
// 核心客户端
#include "LiveLinkClient.h"
#include "ILiveLinkClient.h"

// 数据类型
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "Roles/LiveLinkTransformTypes.h"

// 预设
#include "LiveLinkPreset.h"

// 消息总线源
#include "LiveLinkMessageBusSource.h"
#include "LiveLinkMessageBusFinder.h"

// 虚拟 Subject
#include "LiveLinkAnimationVirtualSubject.h"
#include "VirtualSubjects/LiveLinkBlueprintVirtualSubject.h"

// 帧处理
#include "PreProcessor/LiveLinkAxisSwitchPreProcessor.h"
#include "PreProcessor/LiveLinkDeadbandPreProcessor.h"
#include "InterpolationProcessor/LiveLinkBasicFrameInterpolateProcessor.h"
#include "Translator/LiveLinkAnimationRoleToTransform.h"
```

### 基本用法：获取 Live Link 客户端并查询数据

```cpp
// 来源: LiveLinkClientReference.h, ILiveLinkClient.h
#include "LiveLinkClient.h"
#include "Features/IModularFeatures.h"

// 获取 Live Link 客户端（通过 Modular Features）
ILiveLinkClient& LiveLinkClient = IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);

// 获取所有 Subject
TArray<FLiveLinkSubjectKey> Subjects = LiveLinkClient.GetSubjects(true, true);

// 检查某个 Subject 是否有效
FLiveLinkSubjectKey MySubjectKey;
MySubjectKey.Name = FName("MyMocapSubject");
bool bValid = LiveLinkClient.IsSubjectValid(MySubjectKey);

// 获取 Subject 的角色类型
TSubclassOf<ULiveLinkRole> Role = LiveLinkClient.GetSubjectRole_AnyThread(MySubjectKey);

// 获取静态数据（骨骼名称、层级等）
const FLiveLinkStaticDataStruct* StaticData = LiveLinkClient.GetSubjectStaticData_AnyThread(MySubjectKey);
if (StaticData && StaticData->GetStruct()->IsChildOf<FLiveLinkSkeletonStaticData>())
{
    const FLiveLinkSkeletonStaticData* SkelData = StaticData->Cast<FLiveLinkSkeletonStaticData>();
    TArray<FName> BoneNames = SkelData->GetBoneNames();
    TArray<int32> BoneParents = SkelData->GetBoneParents();
}

// 获取帧数据
const FLiveLinkFrameDataStruct* FrameData = LiveLinkClient.GetSubjectFrameData_AnyThread(MySubjectKey);
if (FrameData && FrameData->GetStruct()->IsChildOf<FLiveLinkAnimationFrameData>())
{
    const FLiveLinkAnimationFrameData* AnimData = FrameData->Cast<FLiveLinkAnimationFrameData>();
    TArray<FTransform> Transforms = AnimData->Transforms;
    TMap<FName, float> Curves = AnimData->Curves;
}
```

### 基本用法：通过消息总线发现和连接源

```cpp
// 来源: LiveLinkMessageBusFinder.h, LiveLinkMessageBusSourceFactory.h
#include "LiveLinkMessageBusFinder.h"
#include "LiveLinkClient.h"

// 创建 Finder 并异步搜索可用的 Live Link 源
ULiveLinkMessageBusFinder* Finder = NewObject<ULiveLinkMessageBusFinder>();

// 使用 Latent 蓝图节点搜索（C++ 中可用委托方式）
// 或者直接使用 DiscoveryManager
FLiveLinkMessageBusDiscoveryManager& DiscoveryMgr = ILiveLinkModule::Get().GetMessageBusDiscoveryManager();
DiscoveryMgr.AddDiscoveryMessageRequest();

// 获取发现结果
TArray<FProviderPollResultPtr> Results = DiscoveryMgr.GetDiscoveryResults();
for (const FProviderPollResultPtr& Result : Results)
{
    FString ProviderName = Result->Name;
    FString MachineName = Result->MachineName;
    FMessageAddress Address = Result->Address;
    bool bValid = Result->bIsValidProvider;
}
```

### 进阶用法：使用预设管理 Live Link 配置

```cpp
// 来源: LiveLinkPreset.h
#include "LiveLinkPreset.h"
#include "LiveLinkClient.h"

// 从客户端构建预设
ULiveLinkPreset* Preset = NewObject<ULiveLinkPreset>();
Preset->BuildFromClient();

// 获取预设中的源和 Subject
const TArray<FLiveLinkSourcePreset>& SourcePresets = Preset->GetSourcePresets();
const TArray<FLiveLinkSubjectPreset>& SubjectPresets = Preset->GetSubjectPresets();

// 异步应用预设到客户端
Preset->ApplyToClientLatent([](bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Live Link preset applied successfully"));
    }
});

// 或者增量添加（保留现有源）
Preset->AddToClient(true); // true = 如果已存在则重建
```

### 进阶用法：自定义帧处理管线

```cpp
// 来源: LiveLinkAxisSwitchPreProcessor.h, LiveLinkDeadbandPreProcessor.h
#include "PreProcessor/LiveLinkAxisSwitchPreProcessor.h"
#include "PreProcessor/LiveLinkDeadbandPreProcessor.h"
#include "LiveLinkSubjectSettings.h"

// 轴切换预处理器 - 用于坐标系转换（如 Maya Z-Up → UE Z-Up）
ULiveLinkTransformAxisSwitchPreProcessor* AxisSwitch = NewObject<ULiveLinkTransformAxisSwitchPreProcessor>();
AxisSwitch->FrontAxis = ELiveLinkAxis::X;
AxisSwitch->RightAxis = ELiveLinkAxis::Y;
AxisSwitch->UpAxis = ELiveLinkAxis::Z;
AxisSwitch->bUseOffsetPosition = true;
AxisSwitch->OffsetPosition = FVector(0, 0, 100);

// 死区预处理器 - 用于过滤抖动
ULiveLinkTransformDeadbandPreProcessor* Deadband = NewObject<ULiveLinkTransformDeadbandPreProcessor>();
Deadband->bEnableDeadband = true;
Deadband->TranslationDeadband = 0.5f;  // 平移变化小于 0.5 不更新
Deadband->RotationDeadbandInDegrees = 0.1f;  // 旋转变化小于 0.1 度不更新

// 将预处理器应用到 Subject 设置
// （通常在编辑器 UI 中配置，或通过项目设置 DefaultRoleSettings）
```

### 进阶用法：创建蓝图虚拟 Subject

```cpp
// 来源: LiveLinkBlueprintVirtualSubject.h, LiveLinkAnimationVirtualSubject.h
#include "VirtualSubjects/LiveLinkBlueprintVirtualSubject.h"
#include "LiveLinkAnimationVirtualSubject.h"

// 动画虚拟 Subject - 组合多个源的骨骼数据
// 通常在编辑器中配置 Attachments 数组
// C++ 中可以继承 ULiveLinkAnimationVirtualSubject 实现自定义逻辑

// 蓝图虚拟 Subject - 在蓝图中创建自定义数据源
// 继承 ULiveLinkBlueprintVirtualSubject 并实现 OnInitialize/OnUpdate
// 在 OnUpdate 中调用 UpdateVirtualSubjectStaticData/UpdateVirtualSubjectFrameData
```

### 进阶用法：Timecode Provider 和自定义时间步

```cpp
// 来源: LiveLinkTimecodeProvider.h, LiveLinkCustomTimeStep.h
#include "LiveLinkTimecodeProvider.h"
#include "LiveLinkCustomTimeStep.h"

// 配置 Timecode Provider（通常在项目设置中）
ULiveLinkTimecodeProvider* TimecodeProvider = NewObject<ULiveLinkTimecodeProvider>();
TimecodeProvider->SetTargetSubjectKey(MySubjectKey);

// 配置自定义时间步 - 用 Live Link 数据率控制引擎帧率
ULiveLinkCustomTimeStep* CustomTimeStep = NewObject<ULiveLinkCustomTimeStep>();
CustomTimeStep->LiveLinkDataRate = FFrameRate(120, 1); // 期望 120fps 数据率
CustomTimeStep->SubjectKey = MySubjectKey;
```

---

## Demo 示例

### 自定义 Live Link 数据消费组件

```cpp
// MyLiveLinkConsumerComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "MyLiveLinkConsumerComponent.generated.h"

class ILiveLinkClient;

UCLASS(ClassGroup=(LiveLink), meta=(BlueprintSpawnableComponent))
class UMyLiveLinkConsumerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyLiveLinkConsumerComponent();

    // 要监听的 Subject 名称
    UPROPERTY(EditAnywhere, Category = "Live Link")
    FLiveLinkSubjectName SubjectName;

    // 获取最新的骨骼变换（蓝图可调用）
    UFUNCTION(BlueprintCallable, Category = "Live Link")
    bool GetLatestBoneTransform(FName BoneName, FTransform& OutTransform);

    // 获取最新的曲线值（蓝图可调用）
    UFUNCTION(BlueprintCallable, Category = "Live Link")
    bool GetLatestCurveValue(FName CurveName, float& OutValue);

protected:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    ILiveLinkClient* LiveLinkClient = nullptr;
    
    // 缓存的最新数据
    FLiveLinkSkeletonStaticData CachedStaticData;
    FLiveLinkAnimationFrameData CachedFrameData;
    bool bHasValidData = false;
};
```

```cpp
// MyLiveLinkConsumerComponent.cpp
#include "MyLiveLinkConsumerComponent.h"
#include "ILiveLinkClient.h"
#include "Features/IModularFeatures.h"
#include "Roles/LiveLinkAnimationRole.h"

UMyLiveLinkConsumerComponent::UMyLiveLinkConsumerComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

void UMyLiveLinkConsumerComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 获取 Live Link 客户端
    if (!LiveLinkClient)
    {
        if (IModularFeatures::Get().IsModularFeatureAvailable(ILiveLinkClient::ModularFeatureName))
        {
            LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);
        }
        if (!LiveLinkClient) return;
    }

    // 构建 Subject Key
    FLiveLinkSubjectKey SubjectKey;
    SubjectKey.Name = SubjectName.Name;

    // 检查 Subject 是否有效
    if (!LiveLinkClient->IsSubjectValid(SubjectKey))
    {
        bHasValidData = false;
        return;
    }

    // 获取静态数据
    const FLiveLinkStaticDataStruct* StaticData = LiveLinkClient->GetSubjectStaticData_AnyThread(SubjectKey);
    if (StaticData && StaticData->IsValid())
    {
        CachedStaticData = *StaticData->Cast<FLiveLinkSkeletonStaticData>();
    }

    // 获取帧数据
    const FLiveLinkFrameDataStruct* FrameData = LiveLinkClient->GetSubjectFrameData_AnyThread(SubjectKey);
    if (FrameData && FrameData->IsValid())
    {
        CachedFrameData = *FrameData->Cast<FLiveLinkAnimationFrameData>();
        bHasValidData = true;
    }
}

bool UMyLiveLinkConsumerComponent::GetLatestBoneTransform(FName BoneName, FTransform& OutTransform)
{
    if (!bHasValidData) return false;

    const TArray<FName>& BoneNames = CachedStaticData.GetBoneNames();
    int32 BoneIndex = BoneNames.IndexOfByKey(BoneName);
    if (BoneIndex == INDEX_NONE || BoneIndex >= CachedFrameData.Transforms.Num())
    {
        return false;
    }

    OutTransform = CachedFrameData.Transforms[BoneIndex];
    return true;
}

bool UMyLiveLinkConsumerComponent::GetLatestCurveValue(FName CurveName, float& OutValue)
{
    if (!bHasValidData) return false;

    const float* Value = CachedFrameData.Curves.Find(CurveName);
    if (!Value) return false;

    OutValue = *Value;
    return true;
}
```

---

## 模块依赖

### LiveLink（核心模块）

| 模块 | 用途 |
|---|---|
| `MessageEndpoint` | 消息总线通信 |
| `TimeManagement` | 时间同步和 Timecode 支持 |
| `LiveLinkInterface` | Live Link 接口定义（独立模块） |
| `RenderCore` | 渲染相关支持 |

### LiveLinkComponents

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 Live Link 框架 |

### LiveLinkEditor

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 Live Link 框架 |
| `LiveLinkInterface` | Live Link 接口定义 |

### LiveLinkMovieScene

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 Live Link 框架 |
| `MovieScene` | Sequencer 核心 |
| `LevelSequence` | 关卡序列支持 |

### LiveLinkMultiUser

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 Live Link 框架 |
| `MultiUserClientLibrary` | 多用户编辑支持 |

### LiveLinkSequencer

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 Live Link 框架 |
| `LiveLinkMovieScene` | Sequencer 集成 |

---

## 维护状态

### 近期更新

```
- 8c74408af8e2 LiveLinkHub - Allow using a virtual subject as a timecode source
- 9cef1e99aea8 LiveLinkHub - Fix animation virtual subject not setting root bone parent to -1
- 21f2805707ac LiveLinkHub - Fix loading source with only Virtual Subject not working
```

近期更新集中在 **LiveLinkHub** 功能的完善：
- 虚拟 Subject 现在可以作为 Timecode 源使用
- 修复了动画虚拟 Subject 的根骨骼父级索引问题
- 修复了仅包含虚拟 Subject 的源加载问题

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建时间**：2017 年，已有 8 年历史，是 UE 动画管线的核心组件
- **更新频率**：持续活跃更新，近期 commit 集中在 LiveLinkHub 功能增强
- **维护状态**：由 Epic Games 官方维护，是 Virtual Production 工作流的关键组件
- **重要性**：这是 UE5 实时数据接入的标准框架，被 MetaHuman Animator、Virtual Camera、ICVFX 等核心功能依赖
- **已知限制**：默认未启用（`EnabledByDefault: false`），需要在插件设置中手动启用
- **推荐使用**：✅ **强烈推荐**。任何涉及外部实时数据接入的项目都应该使用 Live Link

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/)（UE 官方 Live Link 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink/Source/LiveLink/Tests)（如存在）