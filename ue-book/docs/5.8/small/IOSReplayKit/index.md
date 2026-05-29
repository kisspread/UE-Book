# ReplayKit for iOS

> Support for local recording and broadcasting using ReplayKit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | iOS 屏幕录制 |
| 分类 | Mobile |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IOSReplayKit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-02-27 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSReplayKit) | |

## 用途

此插件为 Unreal Engine 应用程序在 iOS 设备上集成苹果的 **ReplayKit** 框架提供支持。其核心目的是让 UE 游戏或应用能够实现：
1.  **本地录制**：录制游戏屏幕视频，保存到设备相册。
2.  **屏幕捕获**：捕获屏幕内容到文件，可能用于性能分析或调试。
3.  **直播推流**：通过支持的第三方直播应用（如 Twitch、YouTube Live）进行实时游戏画面直播。

它封装了原生 iOS ReplayKit 的复杂性，提供了易于在蓝图和 C++ 中调用的接口。

## 使用场景

-   你正在开发 iOS 游戏，并希望玩家能够一键录制并分享他们的游戏高光时刻。
-   你需要为 iOS 设备上的应用实现屏幕直播功能，用于产品演示或实时互动。
-   你在进行 iOS 性能分析，需要捕获特定时间段的屏幕渲染输出。

## 蓝图用法

该插件提供了一个静态蓝图函数库，包含所有核心功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Recording` | 开始本地录制屏幕，可选择是否启用麦克风。 | `UIOSReplayKitControl` |
| `Stop Recording` | 停止本地录制。录制完成后会显示系统预览和分享界面。 | `UIOSReplayKitControl` |
| `Start Capture To File` | 开始将屏幕画面捕获到文件，可选择是否启用麦克风。 | `UIOSReplayKitControl` |
| `Stop Capture` | 停止屏幕捕获。 | `UIOSReplayKitControl` |

*注意：直播相关的函数（`StartBroadcast` 等）在 `IIOSReplayKitModuleInterface` 中定义，但未在 `UIOSReplayKitControl` 蓝图库中暴露为节点。直播功能可能需要 C++ 或通过模块接口间接调用。*

### 使用示例（蓝图描述）

1.  在蓝图中，右键搜索 “Start Recording”。
2.  将此节点连接到某个事件（例如一个按钮的 `OnClicked` 事件）。
3.  拖拽一个 `Stop Recording` 节点，并连接到另一个按钮的事件。
4.  运行后，点击录制按钮将开始录制屏幕，点击停止按钮后，系统会弹出预览窗口，用户可选择保存或分享视频。

## C++ 用法

### 头文件引入

```cpp
#include "IOSReplayKit.h"
#include "IOSReplayKitControl.h"
```

### 基本用法

通过模块接口进行控制（来自 `Source/IOSReplayKit/Public/IOSReplayKit.h`）：

```cpp
// 检查模块是否可用
if (IIOSReplayKitModuleInterface::IsAvailable())
{
    // 获取模块接口
    IIOSReplayKitModuleInterface& ReplayKitModule = IIOSReplayKitModuleInterface::Get();
    
    // 初始化，启用麦克风但禁用摄像头
    ReplayKitModule.Initialize(true, false);
    
    // 开始录制
    ReplayKitModule.StartRecording();
    
    // ... 游戏运行中 ...
    
    // 停止录制
    ReplayKitModule.StopRecording();
}
```

使用更简单的静态函数库（来自 `Source/IOSReplayKit/Public/IOSReplayKitControl.h`）：

```cpp
// 开始录制，启用麦克风（默认）
UIOSReplayKitControl::StartRecording(true);

// 停止录制
UIOSReplayKitControl::StopRecording();

// 开始捕获屏幕内容到文件
UIOSReplayKitControl::StartCaptureToFile();

// 停止捕获
UIOSReplayKitControl::StopCapture();
```

### 进阶用法

结合 `UIOSReplayKitControl` 的静态方法和 `IIOSReplayKitModuleInterface` 的更完整生命周期控制，可以实现更精细的录制管理。例如，在游戏启动时初始化模块，在特定关卡开始时开始录制，在关卡结束或玩家返回主菜单时停止录制。

## Demo 示例

一个最小的、可编译的 C++ 示例，用于在 Actor 中控制屏幕录制。

**MyRecordingActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRecordingActor.generated.h"

UCLASS()
class AMyRecordingActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyRecordingActor();

    UFUNCTION(BlueprintCallable, Category="Recording")
    void ToggleRecording();

private:
    bool bIsRecording = false;
};
```

**MyRecordingActor.cpp**
```cpp
#include "MyRecordingActor.h"
#include "IOSReplayKitControl.h"
#include "IOSReplayKit.h"

AMyRecordingActor::AMyRecordingActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyRecordingActor::ToggleRecording()
{
    if (!IIOSReplayKitModuleInterface::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("IOSReplayKit module is not available."));
        return;
    }

    if (bIsRecording)
    {
        // 停止录制
        UIOSReplayKitControl::StopRecording();
        UE_LOG(LogTemp, Log, TEXT("Recording stopped."));
        bIsRecording = false;
    }
    else
    {
        // 开始录制
        UIOSReplayKitControl::StartRecording(true); // 启用麦克风
        UE_LOG(LogTemp, Log, TEXT("Recording started."));
        bIsRecording = true;
    }
}
```

## 模块依赖

此插件本身依赖以下编辑器模块（见 `Build.cs`），但作为 Runtime 插件，你引用它时无需直接依赖这些编辑器模块。你的项目模块只需依赖标准的引擎模块。

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 编辑器框架支持（插件内部使用） |
| `UnrealEd` | Unreal 编辑器支持（插件内部使用） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏升级，从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复了在大小写敏感的 iOS 编译环境下，头文件包含的大小写错误。 |
| 2022-11-04 | `603ab8ea` | Fixed non-unity/pch errors | 修复了非 unity 构建或预编译头（PCH）下的编译错误。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了内置插件的供应商链接，使用更安全的协议。 |
| 2022-09-10 | `0eeac455` | Pass 3 on cleaning up build.cs files. | 对构建脚本（Build.cs）进行了第三轮清理。 |

### 维护评价

该插件自 2019 年创建至今已超过 7 年，属于老古董级别。从提交记录看，最近的实质性功能更新在创建初期，之后长期处于维护性更新状态。2022 年后有一些编译和构建修复，2026 年进行了日志宏迁移，表明它仍在 UE 引擎的持续集成和维护体系中，并未被完全废弃。

然而，自创建以来，其核心功能（录制、捕获、直播）的 API 和架构基本没有变化。这表明它是一个**功能稳定、相对成熟但创新停滞**的插件。如果你的需求完全符合其提供的功能（本地录制和基于 ReplayKit 的直播），它是可以正常工作的。但对于需要最新 iOS 功能或更复杂录制场景的项目，可能需要自行扩展或寻找替代方案。

**结论：可以放心使用，但不要期待新功能。对于关键项目，建议充分测试在目标 iOS 版本上的兼容性。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSReplayKit)
- [官方文档](https://developer.apple.com/documentation/replaykit)（Apple ReplayKit 官方文档）
- 测试用例：暂无