# EOS Voice Chat

> IVoiceChat integration of the EOS Voice service

| 属性 | 值 |
|---|---|
| 中文名 | EOS 语音聊天 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EOSVoiceChat` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-22 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/VoiceChat/EOSVoiceChat) | |

## 用途

EOSVoiceChat 是 Epic Online Services (EOS) RTC 语音服务的 UE5 集成层，通过实现通用 `IVoiceChat` 接口，为游戏提供跨平台的实时语音聊天功能。

它解决的核心问题是：**让使用 EOS 作为在线服务后端的游戏，能够通过统一的 `IVoiceChat` 接口接入 EOS 的 RTC（实时通信）语音通道**，而无需直接处理 EOS SDK 的底层 C API。

主要能力包括：
- **语音通道管理**：加入/离开语音频道，支持位置性（3D 空间音频）和非位置性通道
- **Lobby 集成**：通过 `AddLobbyRoom`/`RemoveLobbyRoom` 与 EOS Lobby 系统联动，Lobby 成员自动加入对应语音房间
- **音频设备管理**：管理输入/输出设备的切换、静音和音量控制
- **玩家交互控制**：屏蔽、静音、调节其他玩家音量
- **传输模式**：支持向所有频道、特定频道或不向任何频道传输语音
- **音频钩子**：提供捕获前/后、混合/非混合渲染前的音频回调，用于自定义音频处理
- **平台适配**：针对 iOS（硬件 AEC、蓝牙麦克风、后台切换）、Android（蓝牙麦克风）、Windows、Mac 各平台的专门适配

## 使用场景

- 你的游戏使用 **EOS Online Subsystem** 作为在线服务后端 → 用 EOSVoiceChat 接入 EOS 语音通道
- 你需要在 **EOS Lobby** 中实现成员间语音通话 → 用 `AddLobbyRoom` 将 Lobby 与语音通道关联
- 你的游戏需要 **3D 空间音频语音**（如大逃杀中的近距离通话）→ 用 `JoinChannel` 搭配 `Channel3dProperties` 和 `Set3DPosition`
- 你需要在语音通话中做 **自定义音频处理**（如降噪、变声）→ 用 `RegisterOnVoiceChatAfterCaptureAudioReadDelegate` 等音频钩子

## 蓝图用法

EOSVoiceChat 本身是一个 C++ 模块，不直接暴露蓝图节点。蓝图中使用语音聊天功能应通过上层的 **VoiceChat** 通用接口（`UVoiceChat`）或在线子系统间接访问。以下为 C++ 层面暴露的公共 API。

## C++ 用法

### 头文件引入

```cpp
#include "EOSVoiceChat.h"
#include "EOSVoiceChatFactory.h"
#include "EOSVoiceChatTypes.h"
```

### 基本用法

通过工厂类创建 VoiceChat 实例，初始化并登录：

```cpp
// 获取工厂单例
FEOSVoiceChatFactory* Factory = FEOSVoiceChatFactory::Get();
if (!Factory)
{
    UE_LOG(LogEOSVoiceChat, Error, TEXT("EOSVoiceChatFactory not available"));
    return;
}

// 创建 VoiceChat 实例（独立 EOS Platform）
IVoiceChatPtr VoiceChat = Factory->CreateInstance();

// 初始化（异步）
VoiceChat->Initialize(FOnVoiceChatInitializeCompleteDelegate::CreateLambda(
    [VoiceChat](const FVoiceChatResult& Result)
    {
        if (Result.IsSuccess())
        {
            UE_LOG(LogEOSVoiceChat, Log, TEXT("VoiceChat initialized successfully"));
            
            // 连接到语音服务
            VoiceChat->Connect(FOnVoiceChatConnectCompleteDelegate::CreateLambda(
                [](const FVoiceChatResult& ConnectResult)
                {
                    UE_LOG(LogEOSVoiceChat, Log, TEXT("Connect result: %s"), *ConnectResult.ToString());
                }));
        }
    }));

// 创建用户（单用户场景下可复用默认用户）
IVoiceChatUser* User = VoiceChat->CreateUser();

// 登录
User->Login(PlatformUserId, PlayerName, Credentials,
    FOnVoiceChatLoginCompleteDelegate::CreateLambda(
        [](const FString& LoggedInPlayerName, const FVoiceChatResult& Result)
        {
            if (Result.IsSuccess())
            {
                UE_LOG(LogEOSVoiceChat, Log, TEXT("Logged in as: %s"), *LoggedInPlayerName);
            }
        }));
```

> 来源：`Source/EOSVoiceChat/Public/EOSVoiceChat.h` 中 `FEOSVoiceChat` 和 `FEOSVoiceChatFactory` 接口定义

### 加入语音频道

```cpp
// 加入非位置性频道
User->JoinChannel(
    TEXT("SquadChannel"),           // 频道名
    TEXT(""),                       // 频道凭据（可为空）
    EVoiceChatChannelType::NonPositional,
    FOnVoiceChatChannelJoinCompleteDelegate::CreateLambda(
        [](const FString& ChannelName, const FVoiceChatResult& Result)
        {
            UE_LOG(LogEOSVoiceChat, Log, TEXT("Channel %s join: %s"), *ChannelName, *Result.ToString());
        }));

// 加入 3D 空间音频频道（位置性）
TOptional<FVoiceChatChannel3dProperties> SpatialProps;
SpatialProps.Emplace(FVoiceChatChannel3dProperties{ /* 衰减参数 */ });

User->JoinChannel(
    TEXT("ProximityChannel"),
    Credentials,
    EVoiceChatChannelType::Positional,
    FOnVoiceChatChannelJoinCompleteDelegate::CreateLambda(
        [](const FString& ChannelName, const FVoiceChatResult& Result) { /* ... */ }),
    SpatialProps);

// 更新玩家 3D 位置
User->Set3DPosition(TEXT("ProximityChannel"), PlayerWorldPosition);
```

> 来源：`Source/EOSVoiceChat/Public/EOSVoiceChatUser.h` 中 `JoinChannel` 和 `Set3DPosition` 定义

### Lobby 语音集成

```cpp
// 将 EOS Lobby 绑定到语音频道（Lobby 成员自动加入语音房间）
FEOSVoiceChatUser* EOSUser = static_cast<FEOSVoiceChatUser*>(User);
EOSUser->AddLobbyRoom(LobbyId);

// 离开 Lobby 时解绑
EOSUser->RemoveLobbyRoom(LobbyId);
```

> 来源：`Source/EOSVoiceChat/Public/EOSVoiceChatUser.h` 中 `AddLobbyRoom`/`RemoveLobbyRoom`

### 音频控制

```cpp
// 设置输入/输出音量（0.0 - 1.0）
User->SetAudioInputVolume(0.8f);
User->SetAudioOutputVolume(1.0f);

// 静音麦克风
User->SetAudioInputDeviceMuted(true);

// 静音扬声器
User->SetAudioOutputDeviceMuted(true);

// 获取可用音频设备
TArray<FVoiceChatDeviceInfo> InputDevices = User->GetAvailableInputDeviceInfos();
TArray<FVoiceChatDeviceInfo> OutputDevices = User->GetAvailableOutputDeviceInfos();

// 切换输入设备
if (InputDevices.Num() > 0)
{
    User->SetInputDeviceId(InputDevices[0].Id);
}
```

> 来源：`Source/EOSVoiceChat/Public/EOSVoiceChatUser.h` 中音频控制接口

### 玩家交互

```cpp
// 屏蔽玩家（所有频道）
User->BlockPlayers({ TEXT("AnnoyingPlayer") });

// 取消屏蔽
User->UnblockPlayers({ TEXT("AnnoyingPlayer") });

// 静音特定频道中的玩家
User->SetChannelPlayerMuted(TEXT("SquadChannel"), TEXT("LoudPlayer"), true);

// 设置玩家音量
User->SetPlayerVolume(TEXT("QuietPlayer"), 2.0f);  // 放大 2 倍

// 传输模式控制
User->TransmitToAllChannels();              // 向所有频道传输
User->TransmitToNoChannels();               // 不传输（仅收听）
User->TransmitToSpecificChannels({ TEXT("SquadChannel") });  // 仅向特定频道传输
```

> 来源：`Source/EOSVoiceChat/Public/EOSVoiceChatUser.h` 中玩家管理接口

### 音频回调钩子

```cpp
// 注册捕获音频读取回调（麦克风原始数据）
FDelegateHandle CaptureHandle = User->RegisterOnVoiceChatAfterCaptureAudioReadDelegate(
    FOnVoiceChatAfterCaptureAudioReadDelegate2::FDelegate::CreateLambda(
        []() { /* 捕获音频已被读取 */ }));

// 注册发送前回调
FDelegateHandle BeforeSendHandle = User->RegisterOnVoiceChatBeforeCaptureAudioSentDelegate(
    FOnVoiceChatBeforeCaptureAudioSentDelegate2::FDelegate::CreateLambda(
        []() { /* 音频即将发送 */ }));

// 注册接收混合音频渲染前回调
FDelegateHandle BeforeRenderHandle = User->RegisterOnVoiceChatBeforeRecvMixedAudioRenderedDelegate(
    FOnVoiceChatBeforeRecvAudioRenderedDelegate::FDelegate::CreateLambda(
        []() { /* 混合音频即将渲染 */ }));

// 取消注册
User->UnregisterOnVoiceChatAfterCaptureAudioReadDelegate(CaptureHandle);
```

> 来源：`Source/EOSVoiceChat/Public/EOSVoiceChatUser.h` 中录音和音频回调接口

### 使用已有 EOS Platform Handle

```cpp
// 使用已有的 EOS Platform Handle（如通过 EOS Online Subsystem 创建的）
FEOSVoiceChat* EOSVoiceChat = static_cast<FEOSVoiceChat*>(VoiceChat.Get());
EOSVoiceChat->SetPlatformHandle(ExistingPlatformHandle);

// 或使用命名配置
FEOSVoiceChat* EOSVoiceChat2 = static_cast<FEOSVoiceChat*>(VoiceChat.Get());
EOSVoiceChat2->SetPlatformConfigName(TEXT("Default"));
```

> 来源：`Source/EOSVoiceChat/Public/EOSVoiceChat.h` 中 `SetPlatformHandle`/`SetPlatformConfigName`

## Demo 示例

```cpp
// EOSVoiceChatExample.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "VoiceChat.h"
#include "EOSVoiceChat.h"
#include "EOSVoiceChatFactory.h"

class FEOSVoiceChatSubsystem
{
public:
    void Initialize();
    void Shutdown();

    void Login(const FString& PlayerName);
    void JoinVoiceChannel(const FString& ChannelName);
    void LeaveVoiceChannel(const FString& ChannelName);
    void Set3DPosition(const FVector& Position);

    IVoiceChatUser* GetUser() const { return VoiceChatUser; }

private:
    IVoiceChatPtr VoiceChat;
    IVoiceChatUser* VoiceChatUser = nullptr;

    void OnInitializeComplete(const FVoiceChatResult& Result);
    void OnConnectComplete(const FVoiceChatResult& Result);
    void OnLoginComplete(const FString& PlayerName, const FVoiceChatResult& Result);
    void OnChannelJoinComplete(const FString& ChannelName, const FVoiceChatResult& Result);

    // 事件监听
    void OnPlayerTalkingUpdated(const FString& ChannelName, const FString& PlayerName, bool bIsTalking);
};
```

```cpp
// EOSVoiceChatExample.cpp
#include "EOSVoiceChatExample.h"

void FEOSVoiceChatSubsystem::Initialize()
{
    FEOSVoiceChatFactory* Factory = FEOSVoiceChatFactory::Get();
    if (!Factory)
    {
        UE_LOG(LogEOSVoiceChat, Error, TEXT("EOSVoiceChatFactory not available"));
        return;
    }

    VoiceChat = Factory->CreateInstance();
    VoiceChat->Initialize(
        FOnVoiceChatInitializeCompleteDelegate::CreateRaw(this, &FEOSVoiceChatSubsystem::OnInitializeComplete));
}

void FEOSVoiceChatSubsystem::Shutdown()
{
    if (VoiceChat.IsValid())
    {
        if (VoiceChatUser)
        {
            VoiceChat->ReleaseUser(VoiceChatUser);
            VoiceChatUser = nullptr;
        }

        // 如果已连接，先断开再反初始化
        VoiceChat->Uninitialize(FOnVoiceChatUninitializeCompleteDelegate());
        VoiceChat.Reset();
    }
}

void FEOSVoiceChatSubsystem::OnInitializeComplete(const FVoiceChatResult& Result)
{
    if (!Result.IsSuccess())
    {
        UE_LOG(LogEOSVoiceChat, Error, TEXT("VoiceChat init failed: %s"), *Result.ToString());
        return;
    }

    VoiceChatUser = VoiceChat->CreateUser();

    // 监听玩家说话状态
    VoiceChatUser->OnVoiceChatPlayerTalkingUpdated().AddRaw(
        this, &FEOSVoiceChatSubsystem::OnPlayerTalkingUpdated);

    VoiceChat->Connect(
        FOnVoiceChatConnectCompleteDelegate::CreateRaw(this, &FEOSVoiceChatSubsystem::OnConnectComplete));
}

void FEOSVoiceChatSubsystem::OnConnectComplete(const FVoiceChatResult& Result)
{
    UE_LOG(LogEOSVoiceChat, Log, TEXT("VoiceChat connected: %s"), *Result.ToString());
}

void FEOSVoiceChatSubsystem::Login(const FString& PlayerName)
{
    if (!VoiceChatUser) return;

    VoiceChatUser->Login(
        PLATFORMUSERID_NONE,
        PlayerName,
        TEXT(""),  // 由 EOS Token 替代
        FOnVoiceChatLoginCompleteDelegate::CreateRaw(this, &FEOSVoiceChatSubsystem::OnLoginComplete));
}

void FEOSVoiceChatSubsystem::OnLoginComplete(const FString& PlayerName, const FVoiceChatResult& Result)
{
    if (Result.IsSuccess())
    {
        UE_LOG(LogEOSVoiceChat, Log, TEXT("Logged in as: %s"), *PlayerName);
    }
}

void FEOSVoiceChatSubsystem::JoinVoiceChannel(const FString& ChannelName)
{
    if (!VoiceChatUser) return;

    VoiceChatUser->JoinChannel(
        ChannelName,
        TEXT(""),
        EVoiceChatChannelType::NonPositional,
        FOnVoiceChatChannelJoinCompleteDelegate::CreateRaw(
            this, &FEOSVoiceChatSubsystem::OnChannelJoinComplete));
}

void FEOSVoiceChatSubsystem::OnChannelJoinComplete(const FString& ChannelName, const FVoiceChatResult& Result)
{
    UE_LOG(LogEOSVoiceChat, Log, TEXT("Channel join %s: %s"), *ChannelName, *Result.ToString());
}

void FEOSVoiceChatSubsystem::LeaveVoiceChannel(const FString& ChannelName)
{
    if (!VoiceChatUser) return;
    VoiceChatUser->LeaveChannel(ChannelName, FOnVoiceChatChannelLeaveCompleteDelegate());
}

void FEOSVoiceChatSubsystem::Set3DPosition(const FVector& Position)
{
    if (!VoiceChatUser) return;
    for (const FString& Channel : VoiceChatUser->GetChannels())
    {
        if (VoiceChatUser->GetChannelType(Channel) == EVoiceChatChannelType::Positional)
        {
            VoiceChatUser->Set3DPosition(Channel, Position);
        }
    }
}

void FEOSVoiceChatSubsystem::OnPlayerTalkingUpdated(
    const FString& ChannelName, const FString& PlayerName, bool bIsTalking)
{
    UE_LOG(LogEOSVoiceChat, Verbose, TEXT("%s %s talking in %s"),
        *PlayerName, bIsTalking ? TEXT("started") : TEXT("stopped"), *ChannelName);
}
```

## 模块依赖

该插件依赖 `EOSShared` 和 `VoiceChat` 插件（在 .uplugin 中声明）。

| 模块 | 用途 |
|---|---|
| `EOSShared` | EOS SDK 共享层，提供 `IEOSSDKManager`、`IEOSPlatformHandle` 等 EOS 基础设施 |
| `VoiceChat` | 通用 `IVoiceChat`/`IVoiceChatUser` 接口定义，EOSVoiceChat 是其实现之一 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `6ff79bee` | Add new call stats delegate passing a channelName | 新增带频道名参数的通话统计委托（替代旧版） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移至 UE_LOGF 格式 |
| 2026-03-16 | `a456d983` | [EOSVoiceChat] Responding to feedback from last review in which the API for choosing between Mixed v… | 回应上次代码评审反馈，优化混合/非混合音频渲染的 API |
| 2026-03-06 | `8cd30921` | Set up audio loopback to EOS to allow voice chat to be routed out of the submix and into the EOS ren… | 设置 EOS 音频回环，使语音聊天可从子混音器路由到 EOS 渲染器 |
| 2026-02-20 | `dbbc3925` | EOSSDK 1.19.0.3 CL 49960398 Headers Update | 升级至 EOSSDK 1.19.0.3 头文件 |

### 维护评价

**🟢 活跃维护中**

- 该插件创建于 2021 年，是 EOS 在 UE5 中的核心语音服务组件
- 2026 年仍有持续的功能性更新（音频回环、API 优化、SDK 升级），表明活跃维护
- 代