# RemoteSession

> A plugin for Unreal that allows one instance to act as a thin-client (rendering and input) to a second instance

| 属性 | 值 |
|---|---|
| 中文名 | 远程会话 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `RemoteSession` (Runtime), `RemoteSessionEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-18 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteSession) | |

## 用途

RemoteSession 插件实现了一种基于网络的高效远程协作方案，允许一台运行 Unreal Engine 的实例（Host）将其实时渲染画面和场景状态传输到另一台客户端（Client），同时接收来自客户端的输入事件（键盘、鼠标、触摸、手柄、XR 跟踪等）并回放到 Host 上。其核心目标是提供一个低延迟、可扩展的“瘦客户端”体验，使开发者或用户无需在客户端安装完整项目即可远程操控和查看 Unreal 应用。

从源码分析，该插件基于 BackChannel（一种 OSC 风格的协议）进行进程间或跨网络通信，并围绕“通道（Channel）”架构构建，支持多种数据类型传输：

- **图像通道**（`FRemoteSessionImageChannel`）：将 Host 渲染的画面编码为 JPEG 流发送给客户端，客户端解码并显示。
- **输入通道**（`FRemoteSessionInputChannel`）：在 Host 上注入来自客户端的键盘、鼠标、触摸、游戏手柄等输入，通过代理消息处理机制转发。
- **XR 跟踪通道**（`FRemoteSessionXRTrackingChannel`）：同步 Host 与客户端的 XR 设备位姿信息，支持远程 VR/AR 场景。
- **AR 系统通道**（`FRemoteSessionARSystemChannel`）：代理远程设备的 AR 系统功能（如平面检测、图像追踪），在桌面端模拟 AR 环境。
- **LiveLink 通道**（`FRemoteSessionLiveLinkChannel`）：传输 LiveLink 数据，可用于远程动作捕捉或骨骼动画同步。
- **帧缓冲区通道**（`FRemoteSessionFrameBufferImageProvider`）：通过 `FFrameGrabber` 直接捕获视口图像，压缩后发送。

插件还提供了 `URemoteSessionMediaOutput` 和 `URemoteSessionMediaCapture`，允许通过 Media Framework 管线将远程会话图像作为媒体源使用。

## 使用场景

- **远程开发与调试**：在一台开发机（Host）上运行项目，另一台设备（Client）通过 RemoteSession 远程查看画面并操作，无需在客户端安装 UE 编辑器。
- **多用户协作编辑**：结合 Pixel Streaming 或其他技术，让团队成员远程观察并交互编辑场景。
- **XR 远程辅助**：将 VR/AR 设备的追踪数据和相机画面实时同步到远程桌面，用于远程指导或培训。
- **移动设备作为控制台**：在移动端（如 iPad）运行客户端，将触摸输入回传到 PC 端，实现类似平板遥控器的体验。
- **自动化测试**：通过编程方式启动 Host 和 Client，录制输入序列并进行回放。

## 蓝图用法

RemoteSession 插件的主要接口暴露在 C++ 层，蓝图可访问的功能有限。以下是在蓝图中可直接使用的类型和属性：

### 核心类型

| 类型 | 说明 | 所在类 |
|---|---|---|
| `URemoteSessionSettings` | 远程会话的配置对象（位于项目设置中） | `URemoteSessionSettings` |
| `URemoteSessionMediaOutput` | 媒体输出，可作为媒体管线源 | `URemoteSessionMediaOutput` |

`URemoteSessionSettings` 中的以下属性可通过蓝图读写（`Config` 修饰，但非 `BlueprintReadWrite`，实际为 `UPROPERTY(Config)`，故不直接暴露；需通过 C++ 或默认配置访问）：
- `HostPort`：Host 监听端口（默认 2049）
- `ConnectionTimeout`：连接超时时间（秒）
- `ImageQuality`：JPEG 图像质量（1-100）
- `bAutoHostWithPIE`：PIE 启动时自动开启 Host

### 使用说明

由于无 `BlueprintCallable` 函数，推荐在 C++ 或通过自定义蓝图函数库封装使用。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteSession.h"
#include "IRemoteSessionRole.h"
#include "Channels/RemoteSessionImageChannel.h"
#include "Channels/RemoteSessionInputChannel.h"
#include "RemoteSessionTypes.h"
```

### 基本用法

#### 启动 Host（服务器端）

```cpp
// 获取模块并初始化 Host
IRemoteSessionModule& Module = FModuleManager::LoadModuleChecked<IRemoteSessionModule>("RemoteSession");
Module.InitHost(IRemoteSessionModule::kDefaultPort); // 默认端口 2049

// 监听连接状态
TSharedPtr<IRemoteSessionRole> Host = Module.GetHost();
Host->RegisterConnectionChangeDelegate(
    FOnRemoteSessionConnectionChange::FDelegate::CreateLambda(
        [](IRemoteSessionRole* Role, ERemoteSessionConnectionChange State)
        {
            if (State == ERemoteSessionConnectionChange::Connected)
            {
                UE_LOG(LogTemp, Log, TEXT("Client connected"));
            }
        }
    )
);
```

#### 创建客户端（接收端）

```cpp
IRemoteSessionModule& Module = FModuleManager::LoadModuleChecked<IRemoteSessionModule>("RemoteSession");
TSharedPtr<IRemoteSessionRole> Client = Module.CreateClient(TEXT("127.0.0.1"));

// 注册图像接收通道
Client->RegisterChannelListDelegate(
    FOnRemoteSessionReceiveChannelList::FDelegate::CreateLambda(
        [](IRemoteSessionRole* Role, TArrayView<FRemoteSessionChannelInfo> Channels)
        {
            for (const FRemoteSessionChannelInfo& Info : Channels)
            {
                if (Info.Type == FRemoteSessionImageChannel::StaticType())
                {
                    Role->OpenChannel(Info);
                }
            }
        }
    )
);
```

#### 获取远程画面（客户端）

```cpp
// 在 Tick 中获取远程图像
TSharedPtr<FRemoteSessionImageChannel> ImageChannel = Client->GetChannel<FRemoteSessionImageChannel>();
if (ImageChannel.IsValid())
{
    UTexture2D* RemoteScreen = ImageChannel->GetHostScreen(); // 返回的纹理由插件内部管理
    // 可将此纹理赋予 UI 或材质
}
```

### 进阶用法

#### 自定义通道注册

```cpp
// 注册第三方通道工厂
class FMyChannelFactory : public IRemoteSessionChannelFactoryWorker
{
public:
    virtual TSharedPtr<IRemoteSessionChannel> Construct(
        ERemoteSessionChannelMode InMode,
        TBackChannelSharedPtr<IBackChannelConnection> InConnection) const override
    {
        return MakeShared<FMyCustomChannel>(InMode, InConnection);
    }
};

IRemoteSessionModule& Module = FModuleManager::LoadModuleChecked<IRemoteSessionModule>("RemoteSession");
TSharedPtr<FMyChannelFactory> Factory = MakeShared<FMyChannelFactory>();
Module.AddChannelFactory(TEXT("MyCustomChannel"), ERemoteSessionChannelMode::Write, Factory);

// 使用自动注册宏（放在 .cpp 中）
REGISTER_CHANNEL_FACTORY(MyCustomChannel, FMyChannelFactory, ERemoteSessionChannelMode::Write);
```

#### 使用 Media Output 管线

```cpp
// 在 Host 上创建 URemoteSessionMediaOutput 并设置图像通道
URemoteSessionMediaOutput* MediaOutput = NewObject<URemoteSessionMediaOutput>();
TSharedPtr<FRemoteSessionImageChannel> ImageChannel = /* 获取或创建 */;
MediaOutput->SetImageChannel(ImageChannel);

// 将 MediaOutput 赋值给 AMediaPlate 或 UCameraComponent 的 MediaSource
// 参考 Engine 的 Media Framework 文档
```

## Demo 示例

以下为一个最小化的独立 GameInstance 子类，展示在游戏启动时自动开启 Host 并在客户端获取画面。

**RemoteSessionDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "RemoteSessionDemo.generated.h"

UCLASS()
class URemoteSessionDemoGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    TSharedPtr<IRemoteSessionRole> HostRole;
    TSharedPtr<IRemoteSessionRole> ClientRole;
};
```

**RemoteSessionDemo.cpp**

```cpp
#include "RemoteSessionDemo.h"
#include "RemoteSession.h"
#include "IRemoteSessionRole.h"
#include "Channels/RemoteSessionImageChannel.h"

void URemoteSessionDemoGameInstance::Init()
{
    Super::Init();

    IRemoteSessionModule& Module = FModuleManager::LoadModuleChecked<IRemoteSessionModule>("RemoteSession");
    Module.InitHost(2049);
    HostRole = Module.GetHost();

    if (HostRole.IsValid())
    {
        HostRole->RegisterConnectionChangeDelegate(
            FOnRemoteSessionConnectionChange::FDelegate::CreateLambda(
                [](IRemoteSessionRole* Role, ERemoteSessionConnectionChange State)
                {
                    if (State == ERemoteSessionConnectionChange::Connected)
                    {
                        UE_LOG(LogTemp, Log, TEXT("Host: Client connected"));
                    }
                }
            )
        );
    }

    // 在本地启动一个客户端连接自己（仅用于演示）
    ClientRole = Module.CreateClient(TEXT("127.0.0.1"));
    if (ClientRole.IsValid())
    {
        ClientRole->RegisterChannelListDelegate(
            FOnRemoteSessionReceiveChannelList::FDelegate::CreateLambda(
                [this](IRemoteSessionRole* Role, TArrayView<FRemoteSessionChannelInfo> Channels)
                {
                    for (const FRemoteSessionChannelInfo& Info : Channels)
                    {
                        if (Info.Type == FRemoteSessionImageChannel::StaticType())
                        {
                            Role->OpenChannel(Info);
                        }
                    }
                }
            )
        );
    }
}

void URemoteSessionDemoGameInstance::Shutdown()
{
    if (ClientRole.IsValid())
    {
        ClientRole->Close(TEXT("Shutdown"));
    }
    if (HostRole.IsValid())
    {
        HostRole->Close(TEXT("Shutdown"));
    }
    IRemoteSessionModule& Module = FModuleManager::LoadModuleChecked<IRemoteSessionModule>("RemoteSession");
    Module.StopHost(TEXT("Shutdown"));
    Module.StopClient(ClientRole, TEXT("Shutdown"));

    Super::Shutdown();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 底层像素流送基础功能（图像编码、传输） |
| `PixelStreamingServers` | 信令服务器管理 |
| `PixelStreamingEditor` | 编辑器集成扩展 |
| `PixelStreaming2` | Pixel Streaming 2.0 模块（新版本通道） |
| `PixelStreaming2Settings` | Pixel Streaming 2.0 配置 |
| `EditorFramework` | 编辑器基础框架（用于视口捕获） |
| `UnrealEd` | 编辑器模块（用于 `FFrameGrabber`、`FSceneViewport` 等） |

> 注意：上述依赖中大部分为 Pixel Streaming 相关，RemoteSession 复用了其图像编码和网络通道能力。

## 维护状态

### 近期更新

- 2025-09-23 `85a3d914` — Added RemoteSession Hello protocol to sync PixelStreaming version and the Signalling server port.
- 2025-09-03 `a69fe537` — [Backout] - CL45425636
- 2025-09-03 `28e61d07` — Added RemoteSession Hello protocol to sync PixelStreaming version and the Signalling server port.
- 2025-05-31 `52e3dac1` — Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types.
- 2025-03-18 `a6af603c` — Catch missing specifiers in FormatStringSan.

### 维护评价

- **创建时间**：2025-03-18，距今约 9 个月（截至文档生成时）。
- **近期更新**：最近一次功能性更新在 2025-09-23，添加了 Hello 协议；说明插件正在积极开发中。
- **活跃度**：代码提交频繁，且有回退/重提交记录，表明处于迭代阶段。
- **实验性质**：插件位于 `Engine/Plugins/Experimental` 目录下，但 .uplugin 中未标记为 `IsBetaVersion`，功能相对稳定。
- **推荐度**：对于需要远程桌面或远程协作功能的项目，该插件提供了良好的基础。但尚属新插件，API 可能变化，建议在非生产环节先行验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteSession)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteSession/Source/RemoteSession/Private/Tests)（如果存在，此处为推测路径）
- 官方文档：本插件无独立文档，可参考 UE 官方文档中关于 Pixel Streaming 的类似概念。