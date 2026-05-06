# Pixel Streaming Editor

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流编辑器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming) | |

## 用途

PixelStreamingEditor 是 Pixel Streaming 插件的编辑器专用模块。它允许在 **Unreal Editor 内**直接启动像素流传输，将编辑器窗口（包括场景视口、编辑器 UI、浮动窗口等）合成后实时推送到远程浏览器。相比运行时流传输，编辑器流无需打包或 PIE，适合开发阶段的远程协作、评审或演示。

核心功能：

- **启动/停止编辑器流**：选择流类型（仅视口或整个编辑器窗口）
- **内置信令服务器**：可在编辑器中启动一个 C++ 信令服务器，无需额外下载 Node.js 服务
- **画面合成**：将编辑器所有顶层窗口（主窗口、独立视口、工具栏等）按位置与透明度合成到单个视频帧
- **音频捕获**：通过 `FEditorSubmixListener` 捕获编辑器音频发送给接收端
- **工具栏控制**：在编辑器工具栏中集成启停、编码器选择、信令服务器配置等 UI
- **编解码器切换**：支持 VP8、VP9、H264、AV1

## 使用场景

- **远程评审**：在编辑器中进行场景调整，远程同事通过浏览器实时查看效果
- **教学/演示**：无需录制，直接流传输编辑器操作过程
- **协作编辑**：多个观察者同时查看编辑器画面（只读）
- **开发调试**：在设备不支持运行 UE 编辑器时，通过浏览器远程控制编辑器视口

## 蓝图用法

该模块不暴露任何蓝图可调用节点。所有功能需通过 C++ 或控制台命令使用。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreamingEditorModule.h"
```

### 基本用法

获取模块接口并启动编辑器视口流：

```cpp
// 获取模块单例
IPixelStreamingEditorModule& PixelStreamingEditorModule = IPixelStreamingEditorModule::Get();

// 启动流（类型为 LevelEditorViewport）
PixelStreamingEditorModule.StartStreaming(UE::EditorPixelStreaming::EStreamTypes::LevelEditorViewport);

// 停止流
PixelStreamingEditorModule.StopStreaming();
```

### 进阶用法

#### 启动内置信令服务器

```cpp
// 设置信令服务器参数
PixelStreamingEditorModule.SetSignallingDomain(FString("ws://127.0.0.1"));
PixelStreamingEditorModule.SetStreamerPort(8888);
PixelStreamingEditorModule.SetViewerPort(80);

// 启动信令服务器
PixelStreamingEditorModule.StartSignalling();

// 获取信令服务器实例，用于控制
TSharedPtr<UE::PixelStreamingServers::IServer> Server = PixelStreamingEditorModule.GetSignallingServer();

// 停止信令服务器
PixelStreamingEditorModule.StopSignalling();
```

#### 使用外部信令服务器

```cpp
PixelStreamingEditorModule.UseExternalSignallingServer(true);
// 不调用 StartSignalling，自行连接外部信令服务器
```

#### 切换编解码器（通过控制台变量）

```cpp
// 在代码中设置（需要包含 ConsoleManager.h）
IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming.Encoder.Codec"))->Set(TEXT("H264"), ECVF_SetByCode);
```

#### 合成编辑器画面

`FPixelStreamingVideoInputBackBufferComposited` 会监听所有顶层窗口的 `OnBackBufferReady` 事件，每帧将窗口画面按屏幕坐标合成全尺寸视频帧。若只需传输主视口，可使用 `FPixelStreamingVideoInputViewport`。

```cpp
// 创建合成型视频输入
TSharedPtr<FPixelStreamingVideoInputBackBufferComposited> VideoInput = FPixelStreamingVideoInputBackBufferComposited::Create();

// 绑定帧大小变化回调
VideoInput->OnFrameSizeChanged.AddLambda([](TWeakPtr<FIntRect> NewRect) {
    // 处理合成画面尺寸变化
});

// 将视频输入绑定到流
TSharedPtr<IPixelStreamingStreamer> Streamer = /* 获取或创建流 */;
Streamer->SetVideoInput(VideoInput);
```

## Demo 示例

以下是一个迷你编辑器模块，在编辑器启动时自动流传输主视口。

**MyEditorStreamModule.h**

```cpp
#pragma once

#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyEditorStreamModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyEditorStreamModule.cpp**

```cpp
#include "MyEditorStreamModule.h"
#include "IPixelStreamingEditorModule.h"
#include "PixelStreamingEditorUtils.h"

void FMyEditorStreamModule::StartupModule()
{
    // 仅在启用 PixelStreamingEditor 时执行
    if (IPixelStreamingEditorModule::IsAvailable())
    {
        IPixelStreamingEditorModule& Module = IPixelStreamingEditorModule::Get();
        
        // 配置信令服务器（可选）
        Module.SetSignallingDomain(TEXT("ws://127.0.0.1"));
        Module.SetStreamerPort(8888);
        Module.SetViewerPort(80);
        
        // 启动信令服务器
        Module.StartSignalling();
        
        // 启动编辑器视口流
        Module.StartStreaming(UE::EditorPixelStreaming::EStreamTypes::LevelEditorViewport);
        
        UE_LOG(LogTemp, Log, TEXT("Editor Pixel Streaming started automatically."));
    }
}

void FMyEditorStreamModule::ShutdownModule()
{
    if (IPixelStreamingEditorModule::IsAvailable())
    {
        IPixelStreamingEditorModule& Module = IPixelStreamingEditorModule::Get();
        Module.StopStreaming();
        Module.StopSignalling();
    }
}

IMPLEMENT_MODULE(FMyEditorStreamModule, MyEditorStreamModule)
```

**MyEditorStreamModule.Build.cs**

```csharp
using UnrealBuildTool;

public class MyEditorStreamModule : ModuleRules
{
    public MyEditorStreamModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "PixelStreamingEditor"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "Engine",
            "CoreUObject",
            "Slate",
            "SlateCore"
        });
    }
}
```

## 模块依赖

以下为 `PixelStreamingEditor` 模块的非标准特有依赖（省略 Core/Engine/Slate 等常见模块）。

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 核心像素流运行时（编码、信令流） |
| `PixelStreamingServers` | 内置信令服务器逻辑 |
| `PixelStreamingInput` | 输入反走（在编辑器流中传递按键/鼠标） |
| `PixelStreamingHMD` | HMD 支持（编辑器流可能涉及 VR） |
| `AudioMixer` | 音频捕获（通过 `EditorSubmixListener`） |
| `ToolMenus` | 编辑器工具栏菜单扩展 |
| `LevelEditor` | 与关卡编辑器集成 |
| `Slate` | 窗口枚举与合成 |

## 维护状态

### 近期更新

- 2025-09-30 `4bfe7f55` — Updating the infra scripts to point to the new release branch.
- 2025-09-25 `1fdac7d5` — [PixelCapture, PS, PS2] Fix: MediaCapture could get into a bad state due to use of queues and praying
- 2025-09-23 `30db91bd` — [PS1, PS2] Fix: Internal signalling server hitting an ensure during creation due FTickableGameObject
- 2025-09-23 `cc062cea` — [PS1, PS2] Fix a crash in editor when setting the streamID on the command line
- 2025-08-29 `32884de4` — Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.

### 维护评价

该模块处于**活跃维护**状态（最近一个月内有多次功能性修复）。更新记录覆盖了编辑器流崩溃、信令服务器 ensure、捕获状态异常等核心问题。尽管插件本身已有多年历史，但 `PixelStreamingEditor` 作为编辑器专用模块持续得到更新，推荐用于需要编辑器内流传输的场景。已知限制：合成画面性能受编辑器窗口数量和分辨率影响；需同时启用主模块 `PixelStreaming`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreamingEditor/Private/Tests)（如果存在）