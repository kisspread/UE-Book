# Media Framework Utilities

> Utility assets and actors to ease the use of the Media Framework.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架工具集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、媒体配置文件资产类型） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 用途

该插件是 Media Framework 的高层封装，旨在简化媒体输入/输出管理、配置切换和场景内媒体展示。主要解决以下问题：

- **媒体配置集中管理**：通过 `MediaProfile` 资产，将多个媒体源、媒体输出、时间码提供者、自定义时间步打包为一个配置文件，实现一键切换整套媒体流水线。
- **播放资源快速组装**：`MediaBundle` 将媒体源、媒体播放器、媒体纹理、材质等关联为一个原子资产，配合 `MediaBundleActor` 可以直接在场景中拖拽使用，无需手动连接各组件。
- **代理/重定向机制**：`ProxyMediaSource` 和 `ProxyMediaOutput` 提供动态重定向能力，允许在不修改引用的情况下改变实际使用的媒体源/输出，常用于开发/生产环境切换。
- **播放管理**：`MediaProfilePlaybackManager` 负责根据 `MediaProfile` 自动打开、关闭和保持媒体源输出，并支持消费计数。

## 使用场景

- 制作**虚拟演播室**或**多机位直播**系统，需要根据节目流程快速切换不同的摄像头源、输出窗口和时间同步方案。
- 构建**媒体播放墙**，将多个视频源显示在场景的不同平面上，并统一管理播放状态。
- 需要**开发/生产环境分离**的媒体管线：开发时使用本地文件，上线后切换到网络流，通过代理重定向实现。
- 在**时间同步**（Time Synchronization）系统中，为多个媒体源提供统一的帧率、时间码基准。

## 蓝图用法

以下节点按功能分组，全部为 `BlueprintCallable` 或 `BlueprintPure` 函数。

### MediaProfile（媒体配置文件）

可通过 `UMediaProfileBlueprintLibrary` 静态函数访问。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMediaProfile` | 获取当前激活的媒体配置文件 | `UMediaProfileBlueprintLibrary` |
| `SetMediaProfile` | 设置当前使用的媒体配置文件 | `UMediaProfileBlueprintLibrary` |
| `GetAllMediaSourceProxy` | 获取项目设置中配置的所有媒体源代理 | `UMediaProfileBlueprintLibrary` |
| `GetAllMediaOutputProxy` | 获取项目设置中配置的所有媒体输出代理 | `UMediaProfileBlueprintLibrary` |

### MediaBundle（媒体捆绑包）

`UMediaBundle` 和 `AMediaBundleActorBase` 提供对媒体捆绑包的操作。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMaterial` | 获取捆绑包自带的材质（用于显示视频） | `UMediaBundle` |
| `GetMediaPlayer` | 获取捆绑包内部的媒体播放器 | `UMediaBundle` |
| `GetMediaTexture` | 获取捆绑包内部的媒体纹理 | `UMediaBundle` |
| `GetLensDisplacementTexture` | 获取镜头畸变校正位移贴图渲染目标 | `UMediaBundle` |
| `GetMediaSource` | 获取捆绑包中配置的媒体源 | `UMediaBundle` |
| `GetUndistortedCameraViewInfo` | 获取无畸变空间的摄像头视图信息（来自 OpenCV 镜头畸变校正） | `UMediaBundle` |
| `GetMediaBundle` | 返回关联的 MediaBundle 资产 | `AMediaBundleActorBase` |
| `RequestOpenMediaSource` | 打开并播放关联的媒体源 | `AMediaBundleActorBase` |
| `RequestCloseMediaSource` | 关闭当前播放的媒体源 | `AMediaBundleActorBase` |
| `SetComponent` | 将媒体绑定到指定的 Primitve 组件和媒体声音组件 | `AMediaBundleActorBase` |

### Proxy 代理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsProxyValid` | 检查代理是否指向一个有效的媒体源/输出 | `UProxyMediaSource` / `UProxyMediaOutput` |

### 使用示例（蓝图描述）

**切换 MediaProfile**：
1. 在关卡蓝图中放置 `GetAllMediaSourceProxy` 和 `GetAllMediaOutputProxy` 节点，用于检查代理列表。
2. 使用 `SetMediaProfile` 传入一个 `MediaProfile` 资产引用即可立即切换。
3. 可通过 `GetMediaProfile` 获取当前配置，并在 `OnMediaProfileChanged` 委托（C++）中响应变化。

**使用 MediaBundle Actor**：
1. 在内容浏览器中创建 `MediaBundle` 资产，配置 `MediaSource`、循环选项等。
2. 将一个 `MediaBundleActorBase` 子类（如蓝图类）拖入场景，在其 `Details` 面板中指定 `MediaBundle` 资产。
3. 设置 `bAutoPlay = true` 即可在运行时自动播放视频，视频会显示在指定的 Primitve 组件上。

## C++ 用法

### 头文件引入

```cpp
#include "Profile/IMediaProfileManager.h"
#include "Profile/MediaProfile.h"
#include "MediaBundle.h"
#include "MediaBundleActorBase.h"
#include "MediaAssets/ProxyMediaSource.h"
#include "MediaAssets/ProxyMediaOutput.h"
#include "Profile/MediaProfileBlueprintLibrary.h"
```

### 基本用法

#### 获取和设置 MediaProfile（通过全局管理器）

```cpp
// 获取管理器实例
IMediaProfileManager& ProfileManager = IMediaProfileManager::Get();

// 获取当前配置
UMediaProfile* CurrentProfile = ProfileManager.GetCurrentMediaProfile();

// 设置新配置（需要先创建 UMediaProfile 资产或引用）
UMediaProfile* NewProfile = LoadObject<UMediaProfile>(nullptr, TEXT("/Game/MyMediaProfile.MyMediaProfile"));
if (NewProfile)
{
    ProfileManager.SetCurrentMediaProfile(NewProfile);
}
```

#### 获取代理列表

```cpp
TArray<UProxyMediaSource*> SourceProxies = ProfileManager.GetAllMediaSourceProxy();
TArray<UProxyMediaOutput*> OutputProxies = ProfileManager.GetAllMediaOutputProxy();
```


*来源：`IMediaProfileManager.h`、`FMediaProfileManager.cpp`（实现）*

#### 使用 MediaBundle 获取播放组件

```cpp
// 从资产加载 MediaBundle
UMediaBundle* Bundle = LoadObject<UMediaBundle>(nullptr, TEXT("/Game/MyBundle.MyBundle"));
if (Bundle)
{
    // 获取内部媒体播放器
    UMediaPlayer* Player = Bundle->GetMediaPlayer();
    
    // 获取材质（用于显示到 Primitive）
    UMaterialInterface* Material = Bundle->GetMaterial();
    
    // 获取畸变校正纹理
    UTextureRenderTarget2D* LensDisplacement = Bundle->GetLensDisplacementTexture();
}
```

*来源：`MediaBundle.h`*

#### 打开媒体源通过 MediaProfilePlaybackManager

```cpp
// 通过 UMediaProfilePlaybackManager 打开指定索引的媒体源
UMediaProfilePlaybackManager* PlaybackMgr = ...; // 可通过 GEngine 或自定义获取
int32 SourceIndex = 0;
UMediaTexture* MediaTex = PlaybackMgr->OpenSourceFromIndex(SourceIndex, this);

// 检查是否打开
if (PlaybackMgr->IsSourceOpenFromIndex(SourceIndex, this))
{
    // 使用完毕关闭
    PlaybackMgr->CloseSourceFromIndex(SourceIndex, FCloseSourceArgs{}, this);
}
```

*来源：`MediaProfilePlaybackManager.h`*

### 进阶用法

#### 监听 MediaProfile 切换事件

```cpp
// 在模块 Startup 或类构造函数中注册
IMediaProfileManager::Get().OnMediaProfileChanged().AddLambda([](UMediaProfile* Previous, UMediaProfile* New)
{
    UE_LOG(LogTemp, Log, TEXT("MediaProfile changed from %s to %s"), 
        Previous ? *Previous->GetName() : TEXT("None"),
        New ? *New->GetName() : TEXT("None"));
});
```

#### 动态设置代理

```cpp
// 创建或获取一个 UProxyMediaSource
UProxyMediaSource* Proxy = ...; // 可以是从项目设置加载，或新建临时对象
UMediaSource* ActualSource = ...; // 要指向的实际媒体源
Proxy->SetDynamicMediaSource(ActualSource); // 仅运行时生效
```

## Demo 示例

以下是一个最小可编译的示例，展示了在游戏模块中通过 `IMediaProfileManager` 获取当前 MediaProfile 并打印其信息。

### Header（MyMediaDemo.h）

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyMediaDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### Implementation（MyMediaDemo.cpp）

```cpp
#include "MyMediaDemo.h"
#include "Profile/IMediaProfileManager.h"
#include "Profile/MediaProfile.h"

IMPLEMENT_MODULE(FMyMediaDemoModule, MyMediaDemo);

void FMyMediaDemoModule::StartupModule()
{
    // 注册 MediaProfile 变更回调
    IMediaProfileManager::Get().OnMediaProfileChanged().AddLambda([](UMediaProfile* Previous, UMediaProfile* New)
    {
        if (New)
        {
            UE_LOG(LogTemp, Log, TEXT("Current MediaProfile: %s (Sources: %d, Outputs: %d)"),
                *New->GetName(),
                New->NumMediaSources(),
                New->NumMediaOutputs());
        }
    });
    
    // 获取当前配置并输出
    UMediaProfile* Current = IMediaProfileManager::Get().GetCurrentMediaProfile();
    if (Current)
    {
        UE_LOG(LogTemp, Log, TEXT("Startup MediaProfile: %s"), *Current->GetName());
    }
}

void FMyMediaDemoModule::ShutdownModule()
{
    // 清理（可选的，模块卸载时自动清理）
}
```

### Build.cs（示例，需放在 Module 目录）

```csharp
using UnrealBuildTool;

public class MyMediaDemo : ModuleRules
{
    public MyMediaDemo(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "MediaFrameworkUtilities"
        });
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaSource`、`UMediaOutput`、`UMediaPlayer` 等基础媒体资产 |
| `MediaUtils` | 提供媒体播放实用工具和媒体播放器帮助类 |
| `TimeManagement` | 提供时间码、帧率、时间步等时间同步功能 |
| `OpenCVLensDistortion` （可选）| 提供 OpenCV 镜头畸变校正数据结构（MediaBundle 的镜头校正功能依赖） |

**注意**：`MediaFrameworkUtilities` 本身无额外特殊依赖，以上为根据头文件内容推测的典型依赖。实际使用中需要确保项目先启用 `Media Assets` 等基础媒体插件。

## 维护状态

### 近期更新

- 2026-01-23 `b00fe8fa` Media Profile: Fix for crash caused by attempting to capture from camera spawned in by PIE after PIE
- 2026-01-23 `b7b05be8` Media Profile: Fixed issue where active media sources would get stopped whenever PIE was exited
- 2025-10-17 `ab15e769` Media IO - Fix crash when refreshing media properties for Aja source
- 2025-10-01 `abe973bc` Media Profile: Created variant of media capture settings for media profile that can properly be saved
- 2025-09-26 `0f143d8f` Media Profile: Moved media capture management from media profile editor into media profile playback manager

### 维护评价

- **创建时间**：2025-09-26（约 0.4 年）
- **最近更新**：2026-01-23 仍有 bug 修复和增强，维护活跃
- **活跃度**：高，近三个月内有多次功能性提交和修复
- **推荐使用**：✅ 推荐。该插件是媒体管线生产级工具，官方持续维护，适用于需要集中管理媒体配置的项目。
- **注意事项**：插件默认禁用（`EnabledByDefault=false`），需在项目设置中手动启用。部分功能（如 MediaBundle 的镜头校正）依赖 OpenCV 模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaFrameworkUtilities)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/media-framework-in-unreal-engine/)（Media Framework 总体文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaFrameworkUtilities/Tests)