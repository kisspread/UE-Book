# Media Framework Utilities

> Utility assets and actors to ease the use of the Media Framework.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架编辑器工具 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、素材模板） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 用途

Media Framework Utilities 是基于 Unreal Engine 内置 Media Framework 的实用工具集，旨在简化媒体工作流在编辑器中的配置和管理。

该插件主要解决以下问题：

- **媒体配置文件管理**：提供 `MediaProfile` 资产，允许预先配置一组媒体源（`UMediaSource`）和媒体输出（`UMediaOutput`），并在编辑器中一键应用。避免在多个地方手动设置大量媒体资产。
- **编辑器内媒体预览**：在编辑器中提供专门的标签页（Video Input Tab），可以同时预览多个媒体源（来自 `UMediaBundle` 或 `UMediaSource`），监控播放状态，并支持自动重连。
- **编辑器内媒体捕获**：提供 Capture Tab，允许用户在编辑器中配置并启动媒体捕获（如捕获视口、摄影机视口或渲染目标到 `UMediaOutput`），无需启动 PIE 即可验证捕获流程。
- **蓝图脚本支持**：通过 `UMediaFrameworkCapturePanelBlueprintLibrary` 和 `UMediaFrameworkCapturePanel`，暴露了一组可在蓝图（编辑器脚本）中调用的 API，用于在 Editor Utility Widgets 或 Python 中控制媒体捕获的启停。
- **代理资产简化**：提供 `UProxyMediaSource` 和 `UProxyMediaOutput` 代理资产，可以用于在媒体配置文件中，方便地指向或替换不同类型的媒体源和输出，无需逐个修改底层资产。

## 使用场景

- **项目需要管理多个输入/输出媒体流**：例如，你在做一个需要同时采集多路摄像机信号并实时推流的直播工具项目。
- **希望简化媒体源/输出切换**：在不开源的情况下，想要快速切换不同的采集设备或渲染输出目标来测试效果。
- **在编辑器启动 PIE 前验证捕获**：需要在编辑器环境中先验证媒体捕获配置是否工作，再正式发布或启动 PIE。
- **制作自动化测试或编辑器工具**：需要在 Editor Utility Widget 中脚本化控制媒体捕获的启动和停止。

## 蓝图用法

以下蓝图节点可在 Editor Utility Widget 或 Level Blueprint 等编辑脚本蓝图环境中使用（通过 `UMediaFrameworkCapturePanel` 和 `UMediaFrameworkCapturePanelBlueprintLibrary`）。

### 核心节点 (编辑脚本 | 蓝图)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMediaCapturePanel` | 获取全局唯一的媒体捕获面板实例 | `UMediaFrameworkCapturePanelBlueprintLibrary` |
| `StartCapture` | 启动当前配置的所有媒体捕获（视口/渲染目标） | `UMediaFrameworkCapturePanel` |
| `StopCapture` | 停止所有正在运行的媒体捕获 | `UMediaFrameworkCapturePanel` |
| `EmptyRenderTargetCapture` | 清空所有已配置的渲染目标捕获项 | `UMediaFrameworkCapturePanel` |
| `AddRenderTargetCapture` | 添加一个渲染目标捕获项（指定输出、渲染目标和捕获选项） | `UMediaFrameworkCapturePanel` |
| `EmptyViewportCapture` | 清空所有已配置的视口捕获项 | `UMediaFrameworkCapturePanel` |
| `AddViewportCapture` | 添加一个摄影机视口捕获项（指定输出、摄影机和捕获选项） | `UMediaFrameworkCapturePanel` |
| `SetCurrentViewportCapture` | 设置当前视口的捕获配置（输出和捕获选项） | `UMediaFrameworkCapturePanel` |

### 使用示例（蓝图描述）

**示例：从 Editor Utility Widget 启动默认捕获**

1. 在 Editor Utility Widget 蓝图的事件图表中，拖出一个 `GetMediaCapturePanel` 节点。
2. 从返回的 `Return Value` 引脚执行 `StartCapture` 节点。
3. （可选）在调用 `StartCapture` 之前，先用 `AddViewportCapture` 或 `AddRenderTargetCapture` 节点配置捕获项。

## C++ 用法

### 头文件引入

```cpp
#include "MediaFrameworkUtilitiesEditorModule.h"
#include "MediaFrameworkWorldSettingsAssetUserData.h"
#include "Profile/MediaProfile.h"
#include "CaptureTab/MediaFrameworkCapturePanelBlueprintLibrary.h"
```

### 基本用法

**启动/停止编辑器捕获**

```cpp
// 获取全局面板实例
UMediaFrameworkCapturePanel* CapturePanel = UMediaFrameworkCapturePanelBlueprintLibrary::GetMediaCapturePanel();
if (CapturePanel)
{
    // 启动捕获（需先通过设置面板配置好捕获项）
    CapturePanel->StartCapture();

    // 一段时间后停止
    // CapturePanel->StopCapture();
}
```

来源文件: `MediaFrameworkUtilitiesEditor/Private/CaptureTab/MediaFrameworkCapturePanelBlueprintLibrary.h`

**创建媒体配置资产**

```cpp
// 代码创建 UMediaProfile 资产（示例）
// 通常通过编辑器 UI 创建，此方法在编辑器中触发工厂创建
UMediaProfile* NewProfile = Cast<UMediaProfile>(UMediaProfileFactoryNew::StaticClass()->GetDefaultObject<UMediaProfileFactoryNew>()->FactoryCreateNew(
    UMediaProfile::StaticClass(),
    GetTransientPackage(),
    TEXT("MyMediaProfile"),
    RF_Transactional | RF_Public | RF_Standalone,
    nullptr,
    GWarn));
```

来源文件: `MediaFrameworkUtilitiesEditor/Private/Factories/MediaProfileFactoryNew.h`

**配置视口捕获（C++ API）**

```cpp
UMediaFrameworkWorldSettingsAssetUserData* UserData = ...; // 从 WorldSettings 获取

FMediaFrameworkCaptureCurrentViewportOutputInfo CaptureInfo;
CaptureInfo.MediaOutput = MyMediaOutput;
CaptureInfo.CaptureOptions = FMediaCaptureOptions();

// 添加到用户数据
UserData->CurrentViewportMediaOutput = MyMediaOutput;
UserData->CurrentViewportCaptureOptions = CaptureInfo.CaptureOptions;
```

来源文件: `MediaFrameworkUtilitiesEditor/Private/MediaFrameworkWorldSettingsAssetUserData.h`

### 进阶用法

**创建并配置代理资产**

```cpp
// 创建新的代理媒体源
UProxyMediaSource* ProxySource = NewObject<UProxyMediaSource>(GetTransientPackage(), NAME_None, RF_Transactional);

// 设置代理指向的源（可以是任意 UMediaSource 子类）
ProxySource->SetMediaSource(MyRealMediaSource);

// 类似地，创建代理输出
UProxyMediaOutput* ProxyOutput = NewObject<UProxyMediaOutput>(GetTransientPackage(), NAME_None, RF_Transactional);
ProxyOutput->SetDynamicMediaOutput(MyRealMediaOutput);
```

来源文件: `MediaFrameworkUtilitiesEditor/Private/Factories/ProxyMediaSourceFactoryNew.h`, `ProxyMediaOutputFactoryNew.h`

**监听媒体资产变化并刷新捕获**

```cpp
// 注册资产变化事件
FCoreUObjectDelegates::OnObjectPropertyChanged.AddLambda([](UObject* Object, FPropertyChangedEvent& Event)
{
    if (Object->IsA<UMediaProfile>() || Object->IsA<UMediaSource>() || Object->IsA<UMediaOutput>())
    {
        // 刷新捕获配置（通过 SMediaFrameworkCapture 面板）
        // ...
    }
});
```

## Demo 示例

### 启动编辑器视口捕获的最小代码

**MyMediaCapturer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMyMediaCapturerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyMediaCapturer.cpp**
```cpp
#include "MyMediaCapturer.h"
#include "MediaFrameworkUtilitiesEditorModule.h"
#include "CaptureTab/MediaFrameworkCapturePanelBlueprintLibrary.h"

void FMyMediaCapturerModule::StartupModule()
{
    UE_LOG(LogMediaFrameworkUtilitiesEditor, Log, TEXT("MyMediaCapturer module started."));

    // 示例：在编辑器中直接启动捕获（需先手动配置好设置）
    UMediaFrameworkCapturePanel* CapturePanel = UMediaFrameworkCapturePanelBlueprintLibrary::GetMediaCapturePanel();
    if (CapturePanel)
    {
        UE_LOG(LogMediaFrameworkUtilitiesEditor, Log, TEXT("Starting Media Capture from module."));
        CapturePanel->StartCapture();
    }
}

void FMyMediaCapturerModule::ShutdownModule()
{
    if (UMediaFrameworkCapturePanel* CapturePanel = UMediaFrameworkCapturePanelBlueprintLibrary::GetMediaCapturePanel())
    {
        CapturePanel->StopCapture();
    }
}

IMPLEMENT_MODULE(FMyMediaCapturerModule, MyMediaCapturer);
```

## 模块依赖

以下模块是 `MediaFrameworkUtilitiesEditor` 的**独特**依赖，已省略标准核心模块：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 核心媒体资产类型（`UMediaSource`, `UMediaPlayer`, `UMediaTexture`） |
| `MediaFrameworkUtilities` | 运行时部分的依赖（包括媒体配置文件类） |
| `MediaIOCore` | 媒体 IO 核心类型和平台抽象 |
| `MediaIOEditor` | 编辑器内媒体 IO 相关设置和配置 |
| `WorkspaceMenuStructure` | 用于注册标签页到编辑器工作区菜单 |
| `JsonUtilities` | JSON 序列化支持（配置持久化） |
| `DeveloperSettings` | 编辑器用户配置（`UMediaFrameworkVideoInputSettings` 等） |

**总结**：使用此模块时，你的模块需要在 `PublicDependencyModuleNames` 中添加 `MediaFrameworkUtilities`、`MediaAssets` 和 `DeveloperSettings` 等依赖。

## 维护状态

### 近期更新

- 2026-01-23 `b00fe8fa` — Media Profile: Fix for crash caused by attempting to capture from camera spawned in by PIE after PIE
- 2026-01-23 `b7b05be8` — Media Profile: Fixed issue where active media sources would get stopped whenever PIE was exited
- 2025-10-17 `ab15e769` — Media IO - Fix crash when refreshing media properties for Aja source
- 2025-10-01 `abe973bc` — Media Profile: Created variant of media capture settings for media profile that can properly be save
- 2025-09-26 `0f143d8f` — Media Profile: Moved media capture management from media profile editor into media profile playback

### 维护评价

该插件创建于 2025-09-26，属于全新插件。从 git 历史看，在上线后的前几个月有密集的 bug 修复和功能重构，最近的更新（2026-01-23）修复了两个重要的 PIE 相关问题。总体处于**积极维护**状态。

- **推荐使用**：适合需要管理复杂媒体工作流的项目。
- **注意事项**：`EnabledByDefault=false`，需要在项目设置中手动启用该插件。
- **已知限制**：无公开已知严重问题，但作为新插件，部分边界条件（如特殊硬件异常）可能仍有待完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaFrameworkUtilities)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/media-framework-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaFrameworkUtilities/Tests)