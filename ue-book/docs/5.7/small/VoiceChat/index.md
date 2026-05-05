# Voice Chat Interface

> Voice Chat Interface

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | 否 |
| 模块 | VoiceChat (ClientOnly) |
| 创建时间 | 2019-10-29 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/VoiceChat/VoiceChat) | |

## 用途

VoiceChat plugin 提供了一套**平台无关的语音聊天抽象接口**。它本身不包含任何实现——仅定义了 `IVoiceChat` 和 `IVoiceChatUser` 两个纯虚接口类，以及相关的结果码和错误工具。

这个 plugin 存在的意义是：让上层游戏代码可以通过统一接口使用语音聊天功能，而无需关心底层是 EOS VoiceChat、Steam、PlayStation 还是 Xbox 的实现。实际的语音引擎由 `EOSVoiceChat` 等子 plugin 提供，通过 UE 的 Modular Feature 系统在运行时注册。

**这是一个 header-only 的接口层**（Build.cs 中 `Type = ModuleType.External`），不会编译出独立的 DLL。

## 使用场景

- 你需要在多人在线游戏中添加语音聊天功能 → 用 VoiceChat 接口 + 选择一个后端实现（如 EOSVoiceChat）
- 你需要跨平台一致的语音 API（PC / 主机 / 移动端）→ VoiceChat 接口屏蔽了平台差异
- 你需要 3D 空间语音（位置衰减）→ 使用 `EVoiceChatChannelType::Positional` 频道
- 你需要静音/取消静音特定玩家 → `SetPlayerMuted` / `SetChannelPlayerMuted`

## 蓝图用法

此 plugin **没有暴露任何蓝图节点**。所有接口均为 C++ 纯虚类，不包含 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。

如果需要在蓝图中使用语音聊天，需要自行编写 Blueprint Function Library 包装层，或者使用上层框架（如 OnlineSubsystem 的 VoiceInterface）提供的蓝图支持。

## C++ 用法

### 头文件引入

```cpp
#include "VoiceChat.h"
```

### 核心架构

VoiceChat 插件定义了两个关键接口：

- **`IVoiceChat`**：全局单例接口，继承自 `IVoiceChatUser` 和 `IModularFeature`。负责初始化/连接语音服务器、管理多用户。通过 `IVoiceChat::Get()` 获取实例。
- **`IVoiceChatUser`**：单个用户的语音操作接口。负责登录、加入频道、音频设备管理、玩家静音等。

所有异步操作都通过 Delegate 回调，返回 `FVoiceChatResult` 表示成功或失败。

### 基本用法：初始化并加入语音频道

```cpp
#include "VoiceChat.h"

// 1. 获取 IVoiceChat 实例（通过 Modular Feature 系统）
IVoiceChat* VoiceChat = IVoiceChat::Get();
if (!VoiceChat)
{
    UE_LOG(LogTemp, Error, TEXT("No VoiceChat implementation registered"));
    return;
}

// 2. 初始化（同步方式）
bool bInitialized = VoiceChat->Initialize();

// 3. 连接到语音服务器
VoiceChat->Connect(FOnVoiceChatConnectCompleteDelegate::CreateLambda(
    [](const FVoiceChatResult& Result)
    {
        if (Result.IsSuccess())
        {
            UE_LOG(LogTemp, Log, TEXT("Connected to voice server"));
        }
    }));

// 4. 登录
VoiceChat->Login(
    PlatformId,
    TEXT("PlayerName"),
    TEXT("AuthToken"),
    FOnVoiceChatLoginCompleteDelegate::CreateLambda(
        [](const FString& PlayerName, const FVoiceChatResult& Result)
        {
            if (Result.IsSuccess())
            {
                UE_LOG(LogTemp, Log, TEXT("Logged in as %s"), *PlayerName);
            }
        }));

// 5. 加入语音频道
VoiceChat->JoinChannel(
    TEXT("TeamChannel"),
    TEXT("ChannelToken"),
    EVoiceChatChannelType::NonPositional,
    FOnVoiceChatChannelJoinCompleteDelegate::CreateLambda(
        [](const FString& ChannelName, const FVoiceChatResult& Result)
        {
            if (Result.IsSuccess())
            {
                UE_LOG(LogTemp, Log, TEXT("Joined channel %s"), *ChannelName);
            }
        }));
```

### 进阶用法

#### 多用户支持

`IVoiceChat` 支持创建额外的用户实例（例如分屏多人游戏）：

```cpp
IVoiceChatUser* SecondUser = VoiceChat->CreateUser();
if (SecondUser)
{
    SecondUser->Login(SecondPlatformId, TEXT("Player2"), TEXT("Token2"),
        FOnVoiceChatLoginCompleteDelegate::CreateLambda(
            [SecondUser](const FString& Name, const FVoiceChatResult& Result)
            {
                // 第二个用户独立登录、加入频道
            }));
}

// 用完后释放
VoiceChat->ReleaseUser(SecondUser);
```

#### 3D 空间语音

```cpp
// 加入位置感知频道，设置衰减参数
TOptional<FVoiceChatChannel3dProperties> Props;
Props.Emplace();
Props->AttenuationModel = EVoiceChatAttenuationModel::InverseByDistance;
Props->MinDistance = 100.0f;   // 100 单位内不衰减
Props->MaxDistance = 10000.0f; // 10000 单位外静音
Props->Rolloff = 1.0f;

VoiceChat->JoinChannel(TEXT("Proximity"), TEXT("Token"),
    EVoiceChatChannelType::Positional, Delegate, Props);

// 每帧更新玩家 3D 位置
VoiceChat->Set3DPosition(TEXT("Proximity"), PlayerLocation);
```

#### 静音与音量控制

```cpp
// 全局静音某玩家（在所有频道生效，直到登出或调用 UnblockPlayers）
VoiceChat->BlockPlayers({TEXT("AnnoyingPlayer")});

// 频道级静音（仅在当前频道生效，离开频道后失效）
VoiceChat->SetChannelPlayerMuted(TEXT("TeamChannel"), TEXT("SomePlayer"), true);

// 调整某玩家音量 (0.0 ~ 2.0, 1.0 为原始音量)
VoiceChat->SetPlayerVolume(TEXT("QuietPlayer"), 1.5f);

// 麦克风静音
VoiceChat->SetAudioInputDeviceMuted(true);

// 设置输入/输出音量
VoiceChat->SetAudioInputVolume(0.8f);
VoiceChat->SetAudioOutputVolume(1.2f);
```

#### 传输模式控制

```cpp
// 向所有已加入的频道传输语音
VoiceChat->TransmitToAllChannels();

// 仅向指定频道传输
VoiceChat->TransmitToSpecificChannels({TEXT("TeamChannel")});

// 停止向所有频道传输
VoiceChat->TransmitToNoChannels();
```

#### 音频数据捕获（原始 PCM 数据）

```cpp
// 直接获取麦克风原始 PCM 数据
FDelegateHandle RecordHandle = VoiceChat->StartRecording(
    FOnVoiceChatRecordSamplesAvailableDelegate::FDelegate::CreateLambda(
        [](TArrayView<const int16> PcmSamples, int SampleRate, int Channels)
        {
            // 在音频线程上回调，处理原始 PCM 数据
            // 注意：不要在此做耗时操作
        }));

// 停止录音
VoiceChat->StopRecording(RecordHandle);
```

#### 监听事件

```cpp
// 监听玩家加入频道
VoiceChat->OnVoiceChatPlayerAdded().AddLambda(
    [](const FString& ChannelName, const FString& PlayerName)
    {
        UE_LOG(LogTemp, Log, TEXT("%s joined %s"), *PlayerName, *ChannelName);
    });

// 监听玩家说话状态变化
VoiceChat->OnVoiceChatPlayerTalkingUpdated().AddLambda(
    [](const FString& ChannelName, const FString& PlayerName, bool bIsTalking)
    {
        // 更新 UI 显示谁在说话
    });

// 监听断线重连
VoiceChat->OnVoiceChatReconnected().AddLambda(
    []()
    {
        UE_LOG(LogTemp, Log, TEXT("Voice chat reconnected"));
    });
```

## Demo 示例

### 最小完整示例：头文件 + 实现

**MyVoiceChatManager.h**

```cpp
#pragma once

#include "VoiceChat.h"

class FMyVoiceChatManager
{
public:
    void Init();
    void JoinVoiceChannel(const FString& ChannelName, const FString& Token);
    void LeaveVoiceChannel(const FString& ChannelName);
    void Shutdown();

private:
    IVoiceChat* VoiceChatInstance = nullptr;
};
```

**MyVoiceChatManager.cpp**

```cpp
#include "MyVoiceChatManager.h"

void FMyVoiceChatManager::Init()
{
    VoiceChatInstance = IVoiceChat::Get();
    if (!VoiceChatInstance) return;

    VoiceChatInstance->Initialize();
    VoiceChatInstance->Connect(
        FOnVoiceChatConnectCompleteDelegate::CreateLambda(
            [this](const FVoiceChatResult& Result)
            {
                if (Result.IsSuccess())
                {
                    // 连接成功后登录
                    VoiceChatInstance->Login(
                        FPlatformUserId::CreateFromInternalId(0),
                        TEXT("LocalPlayer"),
                        TEXT("Token"),
                        FOnVoiceChatLoginCompleteDelegate());
                }
            }));
}

void FMyVoiceChatManager::JoinVoiceChannel(const FString& ChannelName, const FString& Token)
{
    if (!VoiceChatInstance) return;
    VoiceChatInstance->JoinChannel(
        ChannelName, Token, EVoiceChatChannelType::NonPositional,
        FOnVoiceChatChannelJoinCompleteDelegate::CreateLambda(
            [ChannelName](const FString& Ch, const FVoiceChatResult& Result)
            {
                UE_LOG(LogTemp, Log, TEXT("Join %s: %s"), *Ch,
                    Result.IsSuccess() ? TEXT("OK") : *LexToString(Result));
            }));
}

void FMyVoiceChatManager::LeaveVoiceChannel(const FString& ChannelName)
{
    if (!VoiceChatInstance) return;
    VoiceChatInstance->LeaveChannel(ChannelName, FOnVoiceChatChannelLeaveCompleteDelegate());
}

void FMyVoiceChatManager::Shutdown()
{
    if (!VoiceChatInstance) return;
    VoiceChatInstance->Disconnect(FOnVoiceChatDisconnectCompleteDelegate());
    VoiceChatInstance->Uninitialize();
    VoiceChatInstance = nullptr;
}
```

**Build.cs 依赖**

```cpp
PublicDependencyModuleNames.AddRange(new string[]
{
    "VoiceChat",
    "Core"
});
```

## 模块依赖

使用此 plugin 时，你的模块 Build.cs 需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `VoiceChat` | 声明 IVoiceChat / IVoiceChatUser 接口（header-only） |
| `Core` | 基础类型、Delegate、字符串等 |

> **注意**：VoiceChat 本身是 header-only 模块（`ModuleType.External`），仅提供头文件路径。实际运行时需要一个后端实现 plugin（如 `EOSVoiceChat`）来注册 Modular Feature。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `c851b862481e` | EOSSDK CL45343210 Release v1.18.0.4 Full update |
| 2025-09-23 | `14fcdb4e2c8d` | [Backout] - EOSSDK 更新回退 |
| 2025-09-23 | `4c26457bcc02` | EOSSDK CL45343210 Release v1.18.0.4 Full update |

近期更新主要来自 EOSVoiceChat 子 plugin 的 SDK 版本升级，VoiceChat 核心接口本身变化不大。

### 维护评价

- **创建时间**：2019 年 10 月，已有 6 年以上历史
- **接口稳定性**：接口非常稳定，最近的实质性变更是在 5.6 中添加了带 ChannelName 参数的音频回调 Delegate（旧版标记为 `UE_DEPRECATED(5.6)`）
- **后端活跃度**：EOSVoiceChat 后端持续跟随 EOSSDK 版本更新
- **评价**：**维护中**。接口层本身已趋于成熟稳定，不需要频繁改动。后端实现（EOSVoiceChat）保持活跃更新。推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/VoiceChat/VoiceChat)
- [EOSVoiceChat 后端实现](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/VoiceChat/EOSVoiceChat)
- [IVoiceChatRoom 接口（OnlineSubsystem 中）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/OnlineSubsystem/Source/Public/Interfaces/IVoiceChatRoom.h)
