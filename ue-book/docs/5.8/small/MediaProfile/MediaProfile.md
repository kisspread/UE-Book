# Media Profile

> This plugin contains the Media Profile asset and related entities, which help manage media sources and outputs

| 属性 | 值 |
|---|---|
| 中文名 | 媒体配置 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产，配置） |
| 模块 | `MediaProfile` (Runtime), `MediaProfileEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile) | |

## 用途

MediaProfile 插件解决的是**媒体输入输出配置的集中管理和动态切换**问题。

它允许开发者在编辑器或运行时创建一个“媒体配置文件”（`UMediaProfile`），该文件定义了一组媒体源（输入）和媒体输出（捕获）。这套配置可以随时被应用或重置，从而快速地在不同的媒体设置间切换，例如：
- **多路推流**：在不同的直播平台或编码设置间切换。
- **测试场景**：快速应用用于测试的特定媒体输入/输出组合。
- **生产环境**：确保所有媒体资产（视频流、音频、时间码、同步信号）都符合特定生产配置。

插件还引入了 **Proxy**（代理）机制（`UProxyMediaSource`, `UProxyMediaOutput`），允许在不直接引用实际媒体资产的情况下使用媒体功能，提高了灵活性。

## 使用场景

- 你需要在多个媒体输入源（如网络流、视频文件）和输出设备（如采集卡、流媒体服务）之间频繁切换配置。
- 你在开发一个需要稳定和可管理媒体管线的项目，并希望将媒体输入/输出配置与游戏逻辑解耦。
- 你需要在编辑器中快速预览不同的媒体管线设置。
- 你的媒体资产（如RTMP地址、文件路径）可能会变化，你希望使用代理资产来避免直接修改核心配置。

## 蓝图用法

从源码中分析，该插件的主要蓝图节点集中在 `UMediaProfile` 和 `UMediaProfilePlaybackManager` 类上。以下按功能分组列出核心节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Media Source` | 获取配置文件中指定索引的媒体源资产。 | `UMediaProfile` |
| `Set Media Source` | 设置配置文件中指定索引的媒体源资产。 | `UMediaProfile` |
| `Num Media Sources` | 获取当前配置文件中定义的媒体源数量。 | `UMediaProfile` |
| `Get Media Output` | 获取配置文件中指定索引的媒体输出资产。 | `UMediaProfile` |
| `Set Media Output` | 设置配置文件中指定索引的媒体输出资产。 | `UMediaProfile` |
| `Num Media Outputs` | 获取当前配置文件中定义的媒体输出数量。 | `UMediaProfile` |
| `Is Proxy Valid` | 检查媒体源/输出代理是否指向一个有效的资产。 | `UProxyMediaSource`, `UProxyMediaOutput` |
| `Open Source` | 通过播放管理器打开并播放指定的媒体源，返回对应的媒体纹理。 | `UMediaProfilePlaybackManager` |
| `Close Source` | 通过播放管理器关闭指定的媒体源。 | `UMediaProfilePlaybackManager` |
| `Is Source Open` | 检查指定的媒体源是否正在播放。 | `UMediaProfilePlaybackManager` |
| `Open Managed Viewport Output` | 为指定的媒体输出开始捕获一个管理视口。 | `UMediaProfilePlaybackManager` |
| `Open Active Viewport Output` | 为指定的媒体输出开始捕获一个现有的引擎活动视口。 | `UMediaProfilePlaybackManager` |
| `Open Render Target Output` | 为指定的媒体输出开始捕获一个渲染目标。 | `UMediaProfilePlaybackManager` |
| `Close Output` | 关闭对指定媒体输出的捕获。 | `UMediaProfilePlaybackManager` |
| `Is Output Capturing` | 检查指定的媒体输出是否正在被捕获。 | `UMediaProfilePlaybackManager` |

### 使用示例（蓝图描述）

**场景：应用媒体配置并开始录制输出**
1.  获取一个 `UMediaProfile` 资产的引用。
2.  调用 `Apply` 函数，将该配置文件中定义的时间码、同步步长应用到引擎。
3.  通过该配置文件的 `GetPlaybackManager` 函数获取其播放管理器。
4.  使用播放管理器的 `Open Managed Viewport Output` 节点，选择一个媒体输出索引并设置捕获选项，即可开始录制该输出。
5.  在不需要时，调用播放管理器的 `Close Output` 停止捕获。
6.  最后，可以调用配置文件的 `Reset` 函数，恢复引擎之前的媒体设置。

## C++ 用法

### 头文件引入

```cpp
#include "MediaProfile.h"
#include "Profile/MediaProfilePlaybackManager.h"
```

### 基本用法

获取当前的媒体配置管理器并应用一个配置文件。这通常发生在项目初始化或配置切换时。
```cpp
// 获取模块接口
IMediaProfileModule& MediaProfileModule = FModuleManager::LoadModuleChecked<IMediaProfileModule>(TEXT("MediaProfile"));
IMediaProfileManager& Manager = MediaProfileModule.GetProfileManager();

// 假设你有一个 UMediaProfile* 指针，例如从资产加载
UMediaProfile* MyProfile = LoadObject<UMediaProfile>(nullptr, TEXT("/Game/Media/MyProductionProfile.MyProductionProfile"));
if (MyProfile)
{
    // 应用此配置文件
    Manager.SetCurrentMediaProfile(MyProfile);
    MyProfile->Apply();
}
```

### 进阶用法

使用播放管理器控制媒体源的播放和媒体输出的捕获。
```cpp
// 继续上面的例子，获取已应用配置文件的播放管理器
UMediaProfilePlaybackManager* PlaybackManager = MyProfile->GetPlaybackManager();
if (PlaybackManager)
{
    // 1. 播放一个媒体源 (例如，索引0对应的可能是某个摄像机RTMP流)
    UMediaTexture* CameraTexture = PlaybackManager->OpenSourceFromIndex(0);
    if (CameraTexture)
    {
        // 可以将此纹理赋给某个 UI 材质或用于后处理
        // ...
    }

    // 2. 开始捕获一个媒体输出 (例如，索引0对应某个流媒体服务器地址)
    FMediaCaptureOptions CaptureOptions;
    CaptureOptions.bAutoRestart = true;
    UMediaCapture* Capture = PlaybackManager->OpenManagedViewportOutputFromIndex(0, CaptureOptions);
    if (Capture)
    {
        // 捕获已开始，可以通过 IsOutputCapturingFromIndex(0) 检查状态
    }

    // ... 一段时间后 ...

    // 3. 关闭媒体源播放和输出捕获
    PlaybackManager->CloseSourceFromIndex(0);
    PlaybackManager->CloseOutputFromIndex(0);
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建并应用一个简单的媒体配置文件。

**MediaProfileDemo.h**
```cpp
// MediaProfileDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MediaProfileDemo.generated.h"

class UMediaProfile;

UCLASS()
class YOURPROJECT_API UMediaProfileDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    void ApplyMyTestProfile();

private:
    UPROPERTY()
    TObjectPtr<UMediaProfile> TestProfile;
};
```

**MediaProfileDemo.cpp**
```cpp
// MediaProfileDemo.cpp
#include "MediaProfileDemo.h"
#include "MediaProfile.h"
#include "IMediaProfileModule.h"

void UMediaProfileDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 在这里创建或加载一个 MediaProfile 资产
    TestProfile = NewObject<UMediaProfile>(GetTransientPackage(), NAME_None, RF_Transient);
    // 可以根据需要向 TestProfile 添加媒体源/输出（通常在编辑器中完成）
    // TestProfile->AddMediaSource(MySource);
    // TestProfile->AddMediaOutput(MyOutput);
}

void UMediaProfileDemoSubsystem::ApplyMyTestProfile()
{
    if (TestProfile)
    {
        IMediaProfileModule& MediaProfileModule = FModuleManager::LoadModuleChecked<IMediaProfileModule>(TEXT("MediaProfile"));
        IMediaProfileManager& Manager = MediaProfileModule.GetProfileManager();

        Manager.SetCurrentMediaProfile(TestProfile);
        TestProfile->Apply();

        UE_LOG(LogTemp, Log, TEXT("Test Media Profile Applied."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 核心依赖，提供 `UMediaSource`, `UMediaOutput`, `UMediaTexture`, `UMediaPlayer` 等基础媒体资产类型。 |
| `MediaFrameworkUtilities` | (MediaProfileEditor依赖) 提供媒体框架编辑器工具和UI支持。 |
| `EditorFramework` | (MediaProfileEditor依赖) 提供编辑器框架基础，如工具栏扩展。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了使用 Electra 播放器时，切换新视频失败的问题。 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保应用启动时始终存在一个临时的 MediaProfile。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了某个提交（CL53913857），可能引入了问题。 |

### 维护评价

- **状态**：**活跃维护中**。
- **分析**：该插件创建于 2026 年 4 月，至今约 1 年。从 Git 历史看，近期内仍有功能性的 Bug 修复和稳定性改进（如回退有问题的提交）。作为 `IsExperimentalVersion=true` 的实验性插件，其 API 和行为可能在后续版本中调整，但目前仍在积极维护。
- **推荐**：**推荐**在需要管理复杂或可配置媒体管线的项目中**谨慎使用**。由于其“实验性”标签，建议密切关注引擎版本更新日志，并在生产环境中充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile)
- 官方文档 (暂无)