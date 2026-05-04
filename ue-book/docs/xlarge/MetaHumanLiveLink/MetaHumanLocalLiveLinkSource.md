# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 是 MetaHuman 实时动画的核心数据传输层。它解决的核心问题是：**如何将真实世界的面部输入（摄像头画面或麦克风音频）实时转化为 MetaHuman 角色的面部动画数据，并通过 Live Link 协议推送到引擎中。**

该插件包含两条独立的处理管线：

1. **视频管线**：摄像头画面 → Hyprsense 实时面部追踪 → 面部 Blendshape + 头部姿态动画
2. **音频管线**：麦克风音频 → 实时语音驱动动画（Speech-to-Anim）→ 面部 Blendshape 动画

两条管线均基于 MetaHuman Pipeline 框架运行在独立线程上，通过 `ILiveLinkClient` 接口将动画帧数据推送到引擎的 Live Link 系统，最终驱动 MetaHuman 角色的 Control Rig。

插件还提供了 Live Link Face iOS 应用的连接支持（通过 `LiveLinkFaceSource` 模块），以及本地设备发现功能（通过 `LiveLinkFaceDiscovery` 模块）。

## 使用场景

- 你在做虚拟制片，需要摄像头实时驱动 MetaHuman 角色面部 → 使用视频 Live Link 源
- 你在做语音驱动动画，希望麦克风输入直接驱动 MetaHuman 说话表情 → 使用音频 Live Link 源
- 你在做直播/虚拟主播，需要实时面部捕捉 → 使用视频 Live Link 源配合头部朝向/位移控制
- 你在做游戏开发，需要 NPC 的面部动画由真实演员实时控制 → 使用本插件的 Live Link 源
- 你有 iPhone 上的 Live Link Face 应用，想把面部数据传到 UE → 使用 LiveLinkFaceSource 模块
- 你需要在编辑器中预览实时面部动画效果 → 使用插件提供的监控 Widget

## 蓝图用法

### 核心节点

**主题管理**（`UMetaHumanLocalLiveLinkSubjectSettings`）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReloadSubject` | 重新加载当前 Live Link 主题，重置处理管线 | `UMetaHumanLocalLiveLinkSubjectSettings` |
| `RemoveSubject` | 移除当前 Live Link 主题 | `UMetaHumanLocalLiveLinkSubjectSettings` |

**视频控制**（`UMetaHumanVideoBaseLiveLinkSubjectSettings`）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetHeadOrientation` / `GetHeadOrientation` | 启用/禁用头部朝向输出。如果头部由其他方式追踪（如动捕），可关闭 | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |
| `SetHeadTranslation` / `GetHeadTranslation` | 启用/禁用头部位移输出。需要先设置中性头部位置 | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |
| `SetHeadStabilization` / `GetHeadStabilization` | 启用/禁用头部稳定，减少头部位置和朝向的噪声 | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |
| `SetMonitorImage` / `GetMonitorImage` | 设置监控图像模式：None（无）、Input Video（原始画面）、Trackers（带追踪标记） | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |
| `SetRotation` / `GetRotation` | 设置输入视频旋转角度（0°/90°/180°/270°），适配不同摄像头安装方式 | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |
| `CaptureNeutralHeadPose` | 捕获中性头部姿态，作为头部位移的参考基准 | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |

**音频控制**（`UMetaHumanAudioBaseLiveLinkSubjectSettings`）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMood` / `GetMood` | 设置音频驱动动画的情绪类型（Neutral 等） | `UMetaHumanAudioBaseLiveLinkSubjectSettings` |
| `SetMoodIntensity` / `GetMoodIntensity` | 设置情绪强度（0.0 ~ 1.0） | `UMetaHumanAudioBaseLiveLinkSubjectSettings` |
| `SetLookahead` / `GetLookahead` | 设置音频前瞻时间（80~240ms）。值越大动画质量越高，但延迟越大 | `UMetaHumanAudioBaseLiveLinkSubjectSettings` |

**设备枚举**（`UMetaHumanLocalLiveLinkSourceBlueprint` 蓝图函数库）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVideoDevices` | 获取系统可用的视频设备列表 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `GetAudioDevices` | 获取系统可用的音频设备列表 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `GetVideoTracks` | 获取指定视频设备的轨道列表 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `GetVideoFormats` | 获取指定视频轨道的格式列表（分辨率、帧率等） | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `GetAudioTracks` | 获取指定音频设备的轨道列表 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `GetAudioFormats` | 获取指定音频轨道的格式列表 | `UMetaHumanLocalLiveLinkSourceBlueprint` |

### 使用示例（蓝图描述）

**视频实时面部捕捉工作流：**

1. 使用 `GetVideoDevices` 节点获取可用摄像头列表
2. 从返回的 `FMetaHumanLiveLinkVideoDevice` 数组中选择目标摄像头
3. 使用 `GetVideoTracks` 和 `GetVideoFormats` 获取该摄像头支持的轨道和格式
4. 通过 Live Link 面板创建 MetaHuman Video Live Link 源，或通过蓝图函数库创建
5. 在 Live Link Subject 的设置面板中：
   - 勾选 `HeadOrientation` 启用头部朝向
   - 勾选 `HeadTranslation` 启用头部位移
   - 设置 `MonitorImage` 为 `Trackers` 以预览追踪效果
   - 如果摄像头倒置或侧装，设置 `Rotation` 为对应角度
6. 在 MetaHuman 角色的 Animation Blueprint 中，通过 Live Link 节点接收面部数据

**音频驱动动画工作流：**

1. 使用 `GetAudioDevices` 获取可用麦克风列表
2. 创建 MetaHuman Audio Live Link 源
3. 设置 `Mood` 为期望的情绪类型
4. 设置 `MoodIntensity` 控制情绪表现强度
5. 设置 `Lookahead` 平衡质量与延迟（默认 80ms 低延迟，240ms 高质量）
6. 在 MetaHuman 角色的 Animation Blueprint 中接收音频驱动的面部动画数据

## C++ 用法

### 头文件引入

```cpp
// 本地 Live Link 源核心
#include "MetaHumanLocalLiveLinkSource.h"

// 视频相关
#include "MetaHumanVideoBaseLiveLinkSubject.h"
#include "MetaHumanVideoBaseLiveLinkSubjectSettings.h"

// 音频相关
#include "MetaHumanAudioBaseLiveLinkSubject.h"
#include "MetaHumanAudioBaseLiveLinkSubjectSettings.h"

// 媒体源配置
#include "MetaHumanMediaSourceCreateParams.h"

// 蓝图函数库（设备枚举）
#include "MetaHumanLocalLiveLinkSourceBlueprint.h"
```

### 基本用法

**创建和配置视频 Live Link 主题设置：**

```cpp
// 创建视频主题设置对象
UMetaHumanVideoBaseLiveLinkSubjectSettings* VideoSettings = 
    NewObject<UMetaHumanVideoBaseLiveLinkSubjectSettings>(GetTransientPackage());
VideoSettings->Setup();

// 配置头部追踪选项
VideoSettings->SetHeadOrientation(true);   // 启用头部朝向
VideoSettings->SetHeadTranslation(true);   // 启用头部位移
VideoSettings->SetHeadStabilization(true); // 启用头部稳定

// 配置监控图像（调试用）
VideoSettings->SetMonitorImage(EHyprsenseRealtimeNodeDebugImage::Trackers);

// 配置输入视频旋转（适配摄像头安装方式）
VideoSettings->SetRotation(EMetaHumanVideoRotation::Zero);
```

**创建和配置音频 Live Link 主题设置：**

```cpp
// 创建音频主题设置对象
UMetaHumanAudioBaseLiveLinkSubjectSettings* AudioSettings = 
    NewObject<UMetaHumanAudioBaseLiveLinkSubjectSettings>(GetTransientPackage());
AudioSettings->Setup();

// 配置情绪
AudioSettings->SetMood(EAudioDrivenAnimationMood::Neutral);
AudioSettings->SetMoodIntensity(0.8f);

// 配置前瞻时间（毫秒，越大质量越高但延迟越大）
AudioSettings->SetLookahead(120);
```

### 进阶用法

**通过源对象请求主题创建：**

```cpp
// FMetaHumanLocalLiveLinkSource 是抽象基类，需要使用具体子类
// 这里展示通过源的模板方法创建主题设置
template<class T>
T* CreateSubjectSettings()
{
    T* SubjectSettings = NewObject<T>(GetTransientPackage());
    SubjectSettings->Setup();
    return SubjectSettings;
}

// 请求创建主题
FLiveLinkSubjectKey SubjectKey = Source->RequestSubjectCreation(
    TEXT("MyVideoSubject"), 
    VideoSettings
);
```

**配置媒体源参数（指定设备和格式）：**

```cpp
FMetaHumanMediaSourceCreateParams MediaParams;

// 视频设备配置
MediaParams.VideoName = TEXT("My Webcam");
MediaParams.VideoURL = TEXT("rtsp://...");
MediaParams.VideoTrack = 0;
MediaParams.VideoTrackFormat = 0;

// 音频设备配置
MediaParams.AudioName = TEXT("My Microphone");
MediaParams.AudioURL = TEXT("");
MediaParams.AudioTrack = 0;
MediaParams.AudioTrackFormat = 0;

// 超时配置
MediaParams.StartTimeout = 5.0;      // 启动超时（秒）
MediaParams.FormatWaitTime = 0.1;    // 格式等待时间（秒）
MediaParams.SampleTimeout = 5.0;     // 采样超时（秒）
```

**监听管线数据更新：**

```cpp
// UMetaHumanLocalLiveLinkSubjectSettings 提供 UpdateDelegate
// 可以绑定回调来接收管线处理的中间数据
VideoSettings->UpdateDelegate.AddLambda(
    [](TSharedPtr<UE::MetaHuman::Pipeline::FPipelineData> InPipelineData)
    {
        // 处理管线数据更新
        // 可用于自定义监控或数据转发
    }
);
```

## Demo 示例

以下是一个完整的最小示例，展示如何在 C++ 中创建 MetaHuman Live Link 源并配置视频主题。

### MetaHumanLiveLinkDemo.h

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanLiveLinkDemo.generated.h"

class FMetaHumanLocalLiveLinkSource;
class UMetaHumanVideoBaseLiveLinkSubjectSettings;

/**
 * 演示如何使用 MetaHuman Live Link 插件创建实时视频面部捕捉源
 */
UCLASS()
class UMetaHumanLiveLinkDemo : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 启动视频面部捕捉 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void StartVideoCapture();

    /** 停止视频面部捕捉 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void StopVideoCapture();

    /** 切换头部朝向追踪 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void ToggleHeadOrientation(bool bEnable);

    /** 设置监控图像模式 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void SetMonitorMode(int32 Mode);

private:
    TSharedPtr<FMetaHumanLocalLiveLinkSource> LiveLinkSource;
    UPROPERTY()
    TObjectPtr<UMetaHumanVideoBaseLiveLinkSubjectSettings> VideoSettings;
};
```

### MetaHumanLiveLinkDemo.cpp

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MetaHumanLiveLinkDemo.h"

#include "MetaHumanLocalLiveLinkSource.h"
#include "MetaHumanVideoBaseLiveLinkSubjectSettings.h"
#include "MetaHumanMediaSourceCreateParams.h"

#include "LiveLinkClient.h"
#include "ILiveLinkClient.h"

void UMetaHumanLiveLinkDemo::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UMetaHumanLiveLinkDemo::Deinitialize()
{
    StopVideoCapture();
    Super::Deinitialize();
}

void UMetaHumanLiveLinkDemo::StartVideoCapture()
{
    if (LiveLinkSource.IsValid())
    {
        return; // 已经在运行
    }

    // 创建视频主题设置
    VideoSettings = NewObject<UMetaHumanVideoBaseLiveLinkSubjectSettings>(
        GetTransientPackage());
    VideoSettings->Setup();

    // 配置默认参数
    VideoSettings->SetHeadOrientation(true);
    VideoSettings->SetHeadTranslation(true);
    VideoSettings->SetHeadStabilization(true);
    VideoSettings->SetRotation(EMetaHumanVideoRotation::Zero);

    // 监听管线数据更新
    VideoSettings->UpdateDelegate.AddLambda(
        [this](TSharedPtr<UE::MetaHuman::Pipeline::FPipelineData> InPipelineData)
        {
            // 此处可添加自定义数据处理逻辑
            // 例如记录动画数据、转发到网络等
        }
    );

    // 注意：实际的源创建需要通过 Live Link 面板或
    // 使用具体的 FMetaHumanLocalLiveLinkSource 子类
    // 此处展示设置对象的配置方式
}

void UMetaHumanLiveLinkDemo::StopVideoCapture()
{
    if (VideoSettings && VideoSettings->Subject)
    {
        VideoSettings->RemoveSubject();
    }
    VideoSettings = nullptr;
    LiveLinkSource.Reset();
}

void UMetaHumanLiveLinkDemo::ToggleHeadOrientation(bool bEnable)
{
    if (VideoSettings)
    {
        VideoSettings->SetHeadOrientation(bEnable);
    }
}

void UMetaHumanLiveLinkDemo::SetMonitorMode(int32 Mode)
{
    if (VideoSettings)
    {
        VideoSettings->SetMonitorImage(
            static_cast<EHyprsenseRealtimeNodeDebugImage>(Mode));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架（ILiveLinkClient、ILiveLinkSource、LiveLinkSourceSettings） |
| `MetaHumanPipeline` | MetaHuman 处理管线框架（FPipeline、FPipelineData、各处理节点） |
| `Hyprsense` | Hyprsense 实时面部追踪引擎（FHyprsenseRealtimeNode） |
| `MediaUtils` | 媒体设备访问和捕获支持（IMediaCaptureSupport） |
| `UnrealEd` | 编辑器工具支持（MetaHumanLocalLiveLinkSource 模块依赖） |

> 注意：以上仅列出该插件独特的依赖。标准依赖（Core、CoreUObject、Engine、Slate、SlateCore 等）已省略。

## 维护状态

### 近期更新

```
- d4a8efe9cd5c Bughawk fixes #rb robert.hillary
- 09c462fbc626 GUI pass #rb robert.hillary
- 78e58f806644 Live Link Hub build issue #rb trivial
```

- `d4a8efe9cd5c` — Bug 修复（Bughawk 是 Epic 内部 bug 追踪系统）
- `09c462fbc626` — GUI 界面改进
- `78e58f806644` — 修复 Live Link Hub 构建问题

### 维护评价

**活跃维护** ⭐⭐⭐⭐

- **创建时间**：2025 年 2 月，是一个非常新的插件
- **更新频率**：近期有持续的 bug 修复和 GUI 改进，开发活跃
- **维护状态**：作为 MetaHuman 套件的核心组件，由 Epic Games 团队（robert.hillary 等）持续维护
- **成熟度**：虽然较新，但已标记为非实验性（IsExperimentalVersion=false），属于正式发布状态
- **推荐程度**：**推荐使用**。如果你的工作流涉及 MetaHuman 实时动画，这是官方推荐的 Live Link 集成方案。作为 MetaHuman 生态的核心组件，预计会持续获得支持和更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- 官方文档：暂无（.uplugin 中 DocsURL 为空）