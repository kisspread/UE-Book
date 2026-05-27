# Media Framework Utilities

> This plugin provides utility assets and actors designed to simplify the Media Framework setup. It includes access to the the Media Profile editor.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架工具集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、资产定义） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 用途

Media Framework Utilities 是 UE 媒体框架（Media Framework）的**上层编辑器工具集**，解决了媒体管线配置复杂、缺乏统一管理界面的问题。UE 内置的 `MediaPlayer`、`MediaSource`、`MediaOutput` 等底层类各自独立，实际项目中往往需要同时管理多个输入源和输出设备，配置 Timecode 同步、Genlock 帧锁定等参数，这个插件提供了一个**集中的编辑器面板**来统一管理这一切。

核心功能包括：

- **Media Profile 资产**：将多个 MediaSource 和 MediaOutput 打包为一个可复用的配置资产，项目切换设备时只需切换 Profile
- **Media Profile 编辑器**：自定义资产编辑器，支持多面板实时预览、细节面板、时间码/帧锁定配置
- **Media Capture 面板**：在编辑器内直接捕获视口、摄像机、渲染目标并输出到 MediaOutput
- **Video Input 面板**：实时监控 MediaBundle 和 MediaSource 的视频输入状态
- **MediaBundle 资产**：将 MediaSource + MediaPlayer + MediaTexture 打包为一体化的媒体资产，简化蓝图中的使用流程

## 使用场景

- 你在做一个虚拟制片项目，需要管理 NDI/SDI/HDMI 等多个视频输入和输出设备 → 用 Media Profile 统一管理
- 你需要在编辑器中实时预览多个摄像机输入的画面 → 用 Media Profile 编辑器的多面板视图
- 你需要将编辑器视口内容捕获并输出到外部设备（如 SDI 输出卡）→ 用 Media Capture 面板
- 你需要监控所有视频输入源的连接状态和画面 → 用 Video Input 面板
- 你想简化蓝图中 MediaFramework 的使用，不想手动创建 Source + Player + Texture → 用 MediaBundle 资产
- 你需要配置多设备间的 Timecode 同步和 Genlock 帧锁定 → 用 Media Profile 的 Timecode/Genlock 面板

## 蓝图用法

> **注意**：`EnabledByDefault=false`，使用前需在项目设置中手动启用此插件。

本插件大部分功能为编辑器 UI，可蓝图调用的 API 集中在 **Media Capture Panel** 的编辑器脚本接口上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Media Capture Panel` | 获取全局 Media Capture 面板实例（单例） | `UMediaFrameworkCapturePanelBlueprintLibrary` |
| `Start Capture` | 启动所有已配置的摄像机视口和渲染目标捕获 | `UMediaFrameworkCapturePanel` |
| `Stop Capture` | 停止当前所有捕获 | `UMediaFrameworkCapturePanel` |
| `Add Viewport Capture` | 添加一个摄像机 Actor 到视口捕获列表，可指定视图模式 | `UMediaFrameworkCapturePanel` |
| `Add Render Target Capture` | 添加一个渲染目标到捕获列表 | `UMediaFrameworkCapturePanel` |
| `Empty Viewport Capture` | 清空所有视口捕获配置 | `UMediaFrameworkCapturePanel` |
| `Empty Render Target Capture` | 清空所有渲染目标捕获配置 | `UMediaFrameworkCapturePanel` |
| `Set Current Viewport Capture` | 配置当前活动视口的捕获设置（捕获编辑器主视口） | `UMediaFrameworkCapturePanel` |

### 使用示例（蓝图描述）

**示例 1：通过蓝图配置并启动视口捕获**

```
1. 使用 "Get Media Capture Panel" 节点获取 UMediaFrameworkCapturePanel 实例
2. 对该实例调用 "Empty Viewport Capture" 清空现有配置
3. 调用 "Add Viewport Capture" 传入：
   - MediaOutput：你创建的 SDI/NDI 等 MediaOutput 资产
   - Camera：场景中的摄像机 Actor
   - CaptureOptions：捕获选项（分辨率等）
   - ViewMode：选择 VMI_Lit 等视图模式
4. 调用 "Start Capture" 开始捕获
5. 不再需要时调用 "Stop Capture" 停止
```

**示例 2：捕获渲染目标**

```
1. 获取 UMediaFrameworkCapturePanel 实例
2. 调用 "Add Render Target Capture" 传入 MediaOutput 和 UTextureRenderTarget2D
3. 调用 "Start Capture"
```

## C++ 用法

### 头文件引入

```cpp
#include "MediaFrameworkUtilitiesEditorModule.h"
#include "MediaFrameworkCapturePanelBlueprintLibrary.h"
```

### 基本用法：通过 C++ 脚本操作 Media Capture 面板

```cpp
// 来源: Private/CaptureTab/MediaFrameworkCapturePanelBlueprintLibrary.h
#include "MediaFrameworkCapturePanelBlueprintLibrary.h"

// 获取全局唯一的 Media Capture 面板实例
UMediaFrameworkCapturePanel* CapturePanel = UMediaFrameworkCapturePanelBlueprintLibrary::GetMediaCapturePanel();

// 添加一个视口捕获：指定 MediaOutput、摄像机 Actor、捕获选项
CapturePanel->AddViewportCapture(MyMediaOutput, MyCameraActor, FMediaCaptureOptions(), VMI_Lit);

// 启动捕获
CapturePanel->StartCapture();

// ... 稍后停止捕获
CapturePanel->StopCapture();

// 清空配置
CapturePanel->EmptyViewportCapture();
CapturePanel->EmptyRenderTargetCapture();
```

### 基本用法：操作 Media Framework World Settings 数据

```cpp
// 来源: Private/MediaFrameworkWorldSettingsAssetUserData.h
#include "MediaFrameworkWorldSettingsAssetUserData.h"

// 在编辑器脚本中查找或创建当前世界的 Media Framework 配置数据
UMediaFrameworkWorldSettingsAssetUserData* Settings = 
    World->GetWorldSettings()->GetAssetUserData<UMediaFrameworkWorldSettingsAssetUserData>();

if (!Settings)
{
    Settings = NewObject<UMediaFrameworkWorldSettingsAssetUserData>(World->GetWorldSettings());
    World->GetWorldSettings()->AddAssetUserData(Settings);
}

// 使用模板工具函数查询特定 MediaOutput 的捕获配置
using namespace UE::MediaFrameworkWorldSettings::Helpers;

// 检查是否有任何类型的捕获配置引用了该 MediaOutput
bool bHasCapture = HasAnyOutputInfoForMediaOutput(Settings, MyMediaOutput);

// 查找第一个匹配的摄像机视口捕获配置
FMediaFrameworkCaptureCameraViewportCameraOutputInfo* CameraInfo = 
    FindFirstOutputInfoForMediaOutput<FMediaFrameworkCaptureCameraViewportCameraOutputInfo>(Settings, MyMediaOutput);

// 遍历所有匹配的渲染目标捕获配置
ForEachOutputInfoForMediaOutput<FMediaFrameworkCaptureRenderTargetCameraOutputInfo>(
    Settings, MyMediaOutput,
    [](FMediaFrameworkCaptureRenderTargetCameraOutputInfo& Info)
    {
        // 对每个找到的配置执行操作
        UE_LOG(LogTemp, Log, TEXT("Found render target capture: %s"), *Info.RenderTarget->GetName());
    }
);

// 移除所有引用特定 MediaOutput 的配置
int32 RemovedCount = RemoveAllOutputInfoForMediaOutput<FMediaFrameworkCaptureCameraViewportCameraOutputInfo>(
    Settings, MyMediaOutput);
```

### 进阶用法：理解捕获配置数据结构

```cpp
// 来源: Private/MediaFrameworkWorldSettingsAssetUserData.h

// 该插件定义了四种捕获配置类型：

// 1. 当前视口捕获 - 捕获编辑器当前活动视口
FMediaFrameworkCaptureCurrentViewportOutputInfo CurrentViewportInfo;
CurrentViewportInfo.MediaOutput = MyMediaOutput;
CurrentViewportInfo.CaptureOptions = MyCaptureOptions;
CurrentViewportInfo.ViewMode = VMI_Lit;

// 2. 摄像机视口捕获 - 为每个摄像机创建独立视口
FMediaFrameworkCaptureCameraViewportCameraOutputInfo CameraViewportInfo;
CameraViewportInfo.Cameras.Add(MyCameraActor1);
CameraViewportInfo.Cameras.Add(MyCameraActor2);
CameraViewportInfo.MediaOutput = MyMediaOutput;
CameraViewportInfo.CaptureOptions = MyCaptureOptions;

// 3. 渲染目标捕获 - 捕获 UTextureRenderTarget2D 的内容
FMediaFrameworkCaptureRenderTargetCameraOutputInfo RenderTargetInfo;
RenderTargetInfo.RenderTarget = MyRenderTarget;
RenderTargetInfo.MediaOutput = MyMediaOutput;
RenderTargetInfo.CaptureOptions = MyCaptureOptions;

// 4. MediaTexture 捕获 - 捕获 MediaTexture 的输出（带变换支持）
FMediaFrameworkCaptureMediaTextureOutputInfo MediaTextureInfo;
MediaTextureInfo.MediaTexture = MyMediaTexture;
MediaTextureInfo.Transform = MyTransform;
MediaTextureInfo.MediaOutput = MyMediaOutput;
MediaTextureInfo.CaptureOptions = MyCaptureOptions;
```

## 模块依赖

从两个模块的 Build.cs 和头文件引用推断，此插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | Media Framework 核心工具（UMediaSource, UMediaOutput 等基础类） |
| `MediaPlayerEditor` | MediaPlayer 编辑器支持 |
| `MediaAssets` | MediaBundle, MediaTexture 等资产类型 |
| `MediaIOCore` | 媒体 I/O 核心（NDI/SDI 等设备驱动接口） |
| `MediaIOFramework` | 媒体 I/O 框架（Timecode/Genlock 支持） |
| `CaptureCardMediaSource` | 采集卡媒体源支持 |
| `LiveLinkInterface` | Live Link 接口（用于 Timecode/Genlock 同步） |
| `WorkspaceMenuStructure` | 工作区菜单注册（Nomad Tab 注册） |
| `LevelEditor` | 关卡编辑器集成（视口捕获） |
| `ToolWidgets` | 自定义工具栏/菜单部件 |

> **注**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, PropertyEditor, Projects 等常见依赖已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | Blackmagic 和 Aja 采集卡使用自动模式时自动填充媒体配置 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器窗口菜单中新增共享 Media 分类 |
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had already played one | 修复 ElectraProtron 播放器在播放过视频后无法播放新视频的问题 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在一个临时 MediaProfile |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 重构视口关联通知机制，减少重复代码 |

### 维护评价

- **创建时间**：2018 年 6 月（约 8 年前），属于 UE4.20 Enterprise 时代的产物
- **活跃度**：**非常活跃**。最近 5 次 commit 均在 2026 年 5 月，间距仅几天，涵盖新功能（采集卡自动配置、菜单改进）、Bug 修复（ElectraProtron 播放问题）和代码重构
- **维护状态**：Epic Games 官方持续维护，用于虚拟制片和媒体 I/O 场景
- **已知限制**：
  - `EnabledByDefault=false`，需要手动启用
  - 两个模块虽然 Editor 模块名为 `MediaFrameworkUtilitiesEditor`，但类型标记为 Runtime（这是 UE 的一种惯用模式，便于编辑器和 Runtime 混用）
  - Timecode/Genlock 的逐源显示功能仍有 TODO 标记（UE-305891）
- **推荐**：✅ **强烈推荐**用于任何涉及 Media Framework、虚拟制片、外部视频 I/O 的项目。这是 Epic 官方提供的标准媒体管理工具，持续活跃维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/MediaFramework/)（UE Media Framework 概述）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities/Tests)（如存在）