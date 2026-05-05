# ReplayKit for iOS

> Support for local recording and broadcasting using ReplayKit

| 属性 | 值 |
|---|---|
| 分类 | Mobile |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | IOSReplayKit (Runtime), LoadingPhase: PreDefault |
| 创建时间 | 2019-02-27 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/IOSReplayKit) | |

## 用途

IOSReplayKit 是 Apple ReplayKit 框架在 UE5 中的封装，为 iOS/tvOS 设备提供屏幕录制和直播推流能力。它解决的核心问题是：在 iOS 设备上无需越狱或第三方 SDK，即可录制游戏画面并保存为 MP4 文件，或将画面实时推流到支持 ReplayKit 的直播平台。

该 plugin 封装了 `RPScreenRecorder`、`RPBroadcastController` 等 Apple 原生 API，屏蔽了 Objective-C 细节，通过 C++ 接口和蓝图节点暴露给开发者使用。

## 使用场景

- 你在做一款 iOS 手游，需要内置"一键录屏"功能，让玩家录制精彩操作 → 用 `StartRecording` / `StopRecording`
- 你需要将游戏画面录制为 MP4 文件保存到设备相册 → 用 `StartCaptureToFile` / `StopCapture`
- 你的游戏需要支持 iOS 原生直播推流（如 Twitch、YouTube 等支持 ReplayKit 的平台）→ 用 `StartBroadcast` / `StopBroadcast`
- 你需要在控制台命令中快速测试录屏功能 → 用 `RKStart` / `RKStop` 控制台命令

## 蓝图用法

所有蓝图节点都在 `UIOSReplayKitControl` 类中，属于 `IOSReplayKit` 分类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartRecording` | 开始屏幕录制（可选开启麦克风），停止后弹出预览/分享界面 | `UIOSReplayKitControl` |
| `StopRecording` | 停止屏幕录制，自动显示 iOS 原生预览控制器 | `UIOSReplayKitControl` |
| `StartCaptureToFile` | 开始捕获屏幕内容到 MP4 文件（可选开启麦克风） | `UIOSReplayKitControl` |
| `StopCapture` | 停止捕获，自动将 MP4 保存到设备相册 | `UIOSReplayKitControl` |

### 使用示例（蓝图描述）

**录制屏幕并分享：**

1. 在你的 HUD 蓝图中，创建一个"开始录制"按钮
2. 按钮的 `OnClicked` 事件连接到 `StartRecording` 节点（`bMicrophoneEnabled` 设为 `true` 以录制玩家语音）
3. 创建一个"停止录制"按钮
4. 按钮的 `OnClicked` 事件连接到 `StopRecording` 节点
5. 停止后 iOS 会自动弹出原生预览界面，用户可选择保存或分享

**录制屏幕到文件：**

1. 在游戏结束时调用 `StartCaptureToFile`（`bMicrophoneEnabled` 默认 `true`）
2. 在需要停止时调用 `StopCapture`
3. 录制的 MP4 文件会自动保存到设备的"照片"相册中

## C++ 用法

### 头文件引入

```cpp
#include "IOSReplayKit.h"           // 模块接口
#include "IOSReplayKitControl.h"    // 蓝图控制类（也可在 C++ 中直接调用静态方法）
```

### 基本用法

通过模块接口直接控制录制（来源：`IOSReplayKit.cpp`）：

```cpp
// 检查模块是否可用
if (IIOSReplayKitModuleInterface::IsAvailable())
{
    // 初始化，启用麦克风
    IIOSReplayKitModuleInterface::Get().Initialize(true, false);
    
    // 开始录制
    IIOSReplayKitModuleInterface::Get().StartRecording();
    
    // ... 一段时间后 ...
    
    // 停止录制（会弹出 iOS 预览界面）
    IIOSReplayKitModuleInterface::Get().StopRecording();
}
```

### 捕获到文件

```cpp
// 初始化并开始捕获到 MP4 文件
IIOSReplayKitModuleInterface::Get().Initialize(true, false);
IIOSReplayKitModuleInterface::Get().StartCaptureToFile();

// ... 一段时间后 ...

// 停止捕获，文件自动保存到相册
IIOSReplayKitModuleInterface::Get().StopCapture();
```

### 直播推流

```cpp
// 开始直播（会弹出 iOS 原生的直播服务选择界面）
IIOSReplayKitModuleInterface::Get().StartBroadcast();

// 暂停/恢复直播
IIOSReplayKitModuleInterface::Get().PauseBroadcast();
IIOSReplayKitModuleInterface::Get().ResumeBroadcast();

// 停止直播
IIOSReplayKitModuleInterface::Get().StopBroadcast();
```

### 控制台命令

该模块注册了两个控制台命令（来源：`IOSReplayKit.cpp` 的 `Exec` 方法）：

| 命令 | 说明 |
|---|---|
| `RKStart` | 开始录制（等同于 `StartRecording()`） |
| `RKStop` | 停止录制（等同于 `StopRecording()`） |

### 进阶用法

也可以直接调用蓝图函数库的静态方法：

```cpp
#include "IOSReplayKitControl.h"

// 通过蓝图函数库调用
UIOSReplayKitControl::StartRecording(true);  // 启用麦克风
UIOSReplayKitControl::StopRecording();

UIOSReplayKitControl::StartCaptureToFile(false);  // 不启用麦克风
UIOSReplayKitControl::StopCapture();
```

## Demo 示例

以下是一个最小的 C++ 示例，在 GameMode 中通过按键控制录屏：

### MyGameMode.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Recording")
    void ToggleRecording();

private:
    bool bIsRecording = false;
};
```

### MyGameMode.cpp

```cpp
#include "MyGameMode.h"
#include "IOSReplayKit.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();
}

void AMyGameMode::ToggleRecording()
{
    if (!IIOSReplayKitModuleInterface::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("IOSReplayKit module not available"));
        return;
    }

    if (!bIsRecording)
    {
        IIOSReplayKitModuleInterface::Get().Initialize(true, false);
        IIOSReplayKitModuleInterface::Get().StartRecording();
        bIsRecording = true;
    }
    else
    {
        IIOSReplayKitModuleInterface::Get().StopRecording();
        bIsRecording = false;
    }
}
```

### Build.cs 依赖

```csharp
// 不需要额外添加依赖，IOSReplayKit 的依赖都是 Private 的
// 只需确保在 .uproject 或 DefaultEngine.ini 中启用该 plugin
```

## 模块依赖

所有依赖均为 **Private**（来源：`IOSReplayKit.Build.cs`），使用者无需在自己的 Build.cs 中额外声明依赖。

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（GameViewport 等） |
| `EditorFramework` | 编辑器框架（仅编辑器构建） |
| `UnrealEd` | 编辑器功能（仅编辑器构建） |

iOS 平台还会链接 Apple 的 `ReplayKit` framework，并通过 UPL 自动添加 `NSPhotoLibraryAddUsageDescription` 到 Info.plist。

## 注意事项

- **仅 iOS/tvOS 平台有效**：在非 iOS 平台上调用所有 API 均为空操作（no-op），会输出日志 `ReplayKit not available on this platform`
- **需要手动启用**：`EnabledByDefault: false`，需在项目设置或 `.uproject` 中手动启用
- **录制与直播互斥**：开始录制会自动停止正在进行的直播，反之亦然
- **摄像头功能已禁用**：源码中 `bCameraEnabled` 被硬编码为 `NO`（需要 UIView 支持）
- **捕获到文件的路径**：MP4 文件保存在 App 的 Documents/Captures/ 目录下，文件名为随机 GUID
- **停止捕获后自动保存到相册**：在 iOS 上会调用 `UISaveVideoAtPathToSavedPhotosAlbum`
- **音频格式**：捕获到文件模式使用 AAC 44100Hz 立体声，H.264 视频编码

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2022-11-07 | `0a10c21f` | Update Release-Engine-Staging from UE5/Main | 引擎 staging 同步更新，非功能性改动 |
| 2022-09-09 | `3377a914` | Pass 3 on cleaning up build.cs files | Build.cs 清理，非功能性改动 |
| 2021-02-11 | `9756461b` | Quick pass at some plugin category clean up | 插件分类调整，非功能性改动 |

### 维护评价

- **创建时间**：2019 年 2 月，已超过 7 年
- **最后实质性更新**：最近 3 次提交均为批量维护性改动（Build.cs 清理、分类调整、staging 同步），没有功能性更新
- **活跃度**：**维护不活跃** — 超过 3 年没有实质性功能更新
- **已知限制**：摄像头捕获被硬编码禁用；麦克风音频捕获（`RPSampleBufferTypeAudioMic`）未实现（代码中有 `// todo?` 注释）
- **推荐程度**：功能基本完整，可满足基础录屏和直播需求，但长期未维护，若 Apple ReplayKit API 有变更可能需要自行适配

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/IOSReplayKit)
- [Apple ReplayKit 官方文档](https://developer.apple.com/replaykit/)
