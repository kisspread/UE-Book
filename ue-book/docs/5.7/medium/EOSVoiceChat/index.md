# EOS Voice Chat

> IVoiceChat integration of the EOS Voice service

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EOSVoiceChat` (ClientOnlyNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2021-06-21 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/VoiceChat/EOSVoiceChat) | |

## 用途

EOSVoiceChat 是 Unreal Engine 对 **Epic Online Services (EOS) 实时通信 (RTC)** 语音服务的集成插件。它实现了 UE 的 `IVoiceChat` 接口，将底层 EOS SDK 的 RTC（Real-Time Communication）音频功能暴露为引擎统一的语音聊天 API。

**核心价值**：让使用 EOS 生态的游戏无需对接第三方语音服务（如 Vivox、Discord），即可获得由 Epic 基础设施支撑的语音聊天能力。支持全球部署、跨平台语音，且与 EOS 的 Lobby 系统深度集成——Lobby 房间可以自动关联 RTC 语音频道。

**不做什么**：这个插件不做文本聊天，不处理 EOS 的认证流程（那是 `OnlineSubsystemEOS` 的事），也不管理社交关系。它只管语音。

## 使用场景

- 你正在用 EOS 作为在线服务后端，需要为游戏添加实时语音聊天 → 用 EOSVoiceChat
- 你的游戏使用 EOS Lobby 匹配系统，希望玩家进入 Lobby 后自动开始语音通话 → EOSVoiceChat 与 Lobby RTC 深度集成
- 你需要 3D 空间语音（surround voice），让玩家根据声源方向听到不同音量 → 支持 `Set3DPosition` 和 `FVoiceChatChannel3dProperties`
- 你需要跨平台语音（PC + Mobile），同时支持 Windows、Mac、Android → 该插件支持这三个平台
- 你已经有自己的 EOS Platform Handle（比如通过 OnlineSubsystemEOS），希望复用它来创建语音实例 → 使用 `CreateInstanceWithPlatform`

**不适合的场景**：
- 你的游戏不使用 EOS 生态 → 考虑 `VivoxVoiceChat` 或其他 `IVoiceChat` 实现
- 你需要服务器端语音处理 → 该模块类型为 `ClientOnlyNoCommandlet`

## 蓝图用法

EOSVoiceChat 本身没有暴露 BlueprintCallable 节点——它是一个纯 C++ 模块，通过 `IVoiceChat` 接口注册为 `IModularFeature`。

要从蓝图使用语音聊天，应通过更高层的抽象，例如：
- **EOS Voice Chat subsystem**（如果存在对应的 Online Subsystem 包装）
- **直接在 C++ 中获取 `IVoiceChat` 接口**，然后通过蓝图可调用的包装类暴露给设计师

## C++ 用法

### 头文件引入

```cpp
#include "VoiceChat.h"                    // IVoiceChat 接口
#include "EOSVoiceChat.h"                 // FEOSVoiceChat 类（如果需要直接访问）
#include "EOSVoiceChatFactory.h"          // FEOSVoiceChatFactory
#include "EOSVoiceChatUser.h"             // FEOSVoiceChatUser
#include "EOSVoiceChatTypes.h"            // FEOSVoiceChatChannelCredentials
```

### 基本用法 — 通过 ModularFeature 获取 IVoiceChat 实例

模块启动时会自动将 `IVoiceChat` 注册为 `IModularFeature`。最常见的获取方式：

```cpp
// 通过 ModularFeature 获取已注册的 IVoiceChat 实例
#include "VoiceChat.h"
#include "Features/IModularFeatures.h"

IVoiceChat* VoiceChat = nullptr;
if (IModularFeatures::Get().IsModularFeatureAvailable(IVoiceChat::GetModularFeatureName()))
{
    VoiceChat = &IModularFeatures::Get().GetModularFeature<IVoiceChat>(
        IVoiceChat::GetModularFeatureName());
}
```

### 基本用法 — 初始化与连接

```cpp
// 初始化（同步版本）
VoiceChat->Initialize();

// 或异步版本
VoiceChat->Initialize(FOnVoiceChatInitializeCompleteDelegate::CreateLambda(
    [](const FVoiceChatResult& Result)
    {
        if (Result.IsSuccess())
        {
            UE_LOG(LogTemp, Log, TEXT("VoiceChat initialized"));
        }
    }));

// 连接到语音服务
VoiceChat->Connect(FOnVoiceChatConnectCompleteDelegate::CreateLambda(
    [](const FVoiceChatResult& Result)
    {
        if (Result.IsSuccess())
        {
            UE_LOG(LogTemp, Log, TEXT("VoiceChat connected"));
        }
    }));
```

### 进阶用法 — 登录、加入频道、发送/接收语音

```cpp
// 创建用户实例
IVoiceChatUser* User = VoiceChat->CreateUser();

// 登录（PlayerName 通常是 EOS ProductUserId 字符串）
User->Login(PlatformUserId, PlayerName, Credentials,
    FOnVoiceChatLoginCompleteDelegate::CreateLambda(
        [User](const FString& LoggedInPlayerName, const FVoiceChatResult& Result)
        {
            if (Result.IsSuccess())
            {
                UE_LOG(LogTemp, Log, TEXT("Logged in as %s"), *LoggedInPlayerName);
            }
        }));

// 监听频道加入事件
User->OnVoiceChatChannelJoined().AddLambda(
    [](const FString& ChannelName, const FVoiceChatResult& Result)
    {
        UE_LOG(LogTemp, Log, TEXT("Joined channel: %s"), *ChannelName);
    });

// 加入频道
User->JoinChannel(ChannelName, ChannelCredentials, EVoiceChatChannelType::NonPositional,
    FOnVoiceChatChannelJoinCompleteDelegate::CreateLambda(
        [](const FString& JoinedChannelName, const FVoiceChatResult& Result)
        {
            // Handle join result
        }));

// 监听玩家说话状态
User->OnVoiceChatPlayerTalkingUpdated().AddLambda(
    [User](const FString& PlayerName, bool bIsTalking)
    {
        if (bIsTalking)
        {
            UE_LOG(LogTemp, Log, TEXT("%s is talking"), *PlayerName);
        }
    });

// 静音某个玩家
User->SetPlayerMuted(TargetPlayerName, true);

// 设置音量
User->SetAudioInputVolume(0.8f);
User->SetAudioOutputVolume(0.8f);
```

### 进阶用法 — 通过 Factory 创建独立实例

当你需要一个独立的 EOS Platform（不复用已有的 OnlineSubsystem 平台）：

```cpp
#include "EOSVoiceChatFactory.h"

FEOSVoiceChatFactory* Factory = FEOSVoiceChatFactory::Get();
if (Factory)
{
    // 创建独立实例（会创建自己的 EOS Platform）
    IVoiceChatPtr VoiceChatInstance = Factory->CreateInstance();
    
    // 或者复用已有的 EOS Platform Handle
    IVoiceChatPtr SharedVoiceChat = Factory->CreateInstanceWithPlatform(ExistingPlatformHandle);
}
```

### 进阶用法 — Lobby 语音集成

```cpp
// 如果使用 Lobby 系统，可以通过 AddLobbyRoom/RemoveLobbyRoom 管理 Lobby 语音
FEOSVoiceChatUser* EOSUser = static_cast<FEOSVoiceChatUser*>(User);
EOSUser->AddLobbyRoom(LobbyId);     // 将 Lobby 关联到 RTC 语音频道
EOSUser->RemoveLobbyRoom(LobbyId);  // 断开关联
```

### 进阶用法 — 3D 空间语音

```cpp
// 加入 Positional 类型的频道
User->JoinChannel(ChannelName, Credentials, EVoiceChatChannelType::Positional,
    Delegate, FVoiceChatChannel3dProperties(ChannelName));

// 持续更新玩家 3D 位置（每帧调用）
User->Set3DPosition(ChannelName, PlayerWorldPosition);
```

### 进阶用法 — 传输模式控制

```cpp
// 向所有已加入的频道发送语音
User->TransmitToAllChannels();

// 不向任何频道发送语音（只听不说）
User->TransmitToNoChannels();

// 只向指定频道发送
TSet<FString> SpecificChannels;
SpecificChannels.Add(TEXT("TeamChannel"));
User->TransmitToSpecificChannels(SpecificChannels);
```

### 进阶用法 — 音频录制回调

```cpp
// 开始录音（获取原始音频数据）
FDelegateHandle RecordHandle = User->StartRecording(
    FOnVoiceChatRecordSamplesAvailableDelegate::FDelegate::CreateLambda(
        [](const FString& PlayerName, const TArray<uint8>& AudioData,
           int32 SamplingRate, int32 NumChannels, int32 NumFrames)
        {
            // 处理原始音频数据
        }));

// 停止录音
User->StopRecording(RecordHandle);
```

### 进阶用法 — 音频输入/输出设备管理

```cpp
// 获取可用设备
TArray<FVoiceChatDeviceInfo> InputDevices = User->GetAvailableInputDeviceInfos();
TArray<FVoiceChatDeviceInfo> OutputDevices = User->GetAvailableOutputDeviceInfos();

// 切换设备
User->SetInputDeviceId(InputDevices[0].Id);
User->SetOutputDeviceId(OutputDevices[0].Id);

// 获取当前设备信息
FVoiceChatDeviceInfo CurrentInput = User->GetInputDeviceInfo();
FVoiceChatDeviceInfo CurrentOutput = User->GetOutputDeviceInfo();

// 静音输入/输出设备
User->SetAudioInputDeviceMuted(true);
User->SetAudioOutputDeviceMuted(true);
```

## 配置项

在 `Engine.ini` 的 `[EOSVoiceChat]` 节中配置：

```ini
[EOSVoiceChat]
bEnabled=true
; EOS 产品信息（如果 VoiceChat 自行创建 Platform）
ProductId=your_product_id
SandboxId=your_sandbox_id
DeploymentId=your_deployment_id
ClientId=your_client_id
ClientSecret=your_client_secret
ClientEncryptionKey=your_encryption_key
; RTC 后台模式（KeepRoomsAlive / LeaveRooms / Disabled）
RTCBackgroundMode=KeepRoomsAlive
; 是否在 Monolithic 构建中禁用
bDisableInMonolithic=false
```

## Demo 示例

### 完整的最小语音聊天流程

**MyVoiceChatManager.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "VoiceChat.h"

class FMyVoiceChatManager
{
public:
    void Init();
    void JoinVoiceChannel(const FString& ChannelName, const FString& Token);
    void LeaveVoiceChannel(const FString& ChannelName);
    void Shutdown();

private:
    IVoiceChat* VoiceChat = nullptr;
    IVoiceChatUser* VoiceChatUser = nullptr;

    void OnConnectComplete(const FVoiceChatResult& Result);
    void OnLoginComplete(const FString& PlayerName, const FVoiceChatResult& Result);
    void OnChannelJoined(const FString& ChannelName, const FVoiceChatResult& Result);
    void OnPlayerTalking(const FString& PlayerName, bool bIsTalking);
};
```

**MyVoiceChatManager.cpp**

```cpp
#include "MyVoiceChatManager.h"
#include "Features/IModularFeatures.h"
#include "VoiceChat.h"
#include "EOSVoiceChatTypes.h"

void FMyVoiceChatManager::Init()
{
    // 通过 ModularFeature 获取 IVoiceChat 实例
    if (IModularFeatures::Get().IsModularFeatureAvailable(IVoiceChat::GetModularFeatureName()))
    {
        VoiceChat = &IModularFeatures::Get().GetModularFeature<IVoiceChat>(
            IVoiceChat::GetModularFeatureName());
    }

    if (!VoiceChat)
    {
        UE_LOG(LogTemp, Error, TEXT("No IVoiceChat implementation found"));
        return;
    }

    // 初始化
    VoiceChat->Initialize(FOnVoiceChatInitializeCompleteDelegate::CreateLambda(
        [this](const FVoiceChatResult& Result)
        {
            if (Result.IsSuccess())
            {
                // 连接
                VoiceChat->Connect(
                    FOnVoiceChatConnectCompleteDelegate::CreateRaw(
                        this, &FMyVoiceChatManager::OnConnectComplete));
            }
        }));
}

void FMyVoiceChatManager::OnConnectComplete(const FVoiceChatResult& Result)
{
    if (!Result.IsSuccess()) return;

    // 创建用户
    VoiceChatUser = VoiceChat->CreateUser();

    // 监听事件
    VoiceChatUser->OnVoiceChatPlayerTalkingUpdated().AddRaw(
        this, &FMyVoiceChatManager::OnPlayerTalking);

    // 登录（使用 EOS ProductUserId 作为 PlayerName）
    VoiceChatUser->Login(
        PLATFORMUSERID_NONE,
        TEXT("your_eos_product_user_id"),
        TEXT(""),
        FOnVoiceChatLoginCompleteDelegate::CreateRaw(
            this, &FMyVoiceChatManager::OnLoginComplete));
}

void FMyVoiceChatManager::OnLoginComplete(const FString& PlayerName, const FVoiceChatResult& Result)
{
    if (Result.IsSuccess())
    {
        UE_LOG(LogTemp, Log, TEXT("Voice logged in as %s"), *PlayerName);
    }
}

void FMyVoiceChatManager::JoinVoiceChannel(const FString& ChannelName, const FString& Token)
{
    if (!VoiceChatUser) return;

    // 构造频道凭据
    FEOSVoiceChatChannelCredentials Creds;
    Creds.ParticipantToken = Token;
    FString CredsJson;
    // Creds 序列化为 JSON 字符串传入

    VoiceChatUser->JoinChannel(ChannelName, CredsJson,
        EVoiceChatChannelType::NonPositional,
        FOnVoiceChatChannelJoinCompleteDelegate::CreateRaw(
            this, &FMyVoiceChatManager::OnChannelJoined));
}

void FMyVoiceChatManager::OnChannelJoined(const FString& ChannelName, const FVoiceChatResult& Result)
{
    UE_LOG(LogTemp, Log, TEXT("Channel joined: %s (Success: %s)"),
        *ChannelName, Result.IsSuccess() ? TEXT("Yes") : TEXT("No"));
}

void FMyVoiceChatManager::OnPlayerTalking(const FString& PlayerName, bool bIsTalking)
{
    UE_LOG(LogTemp, Log, TEXT("%s %s talking"), *PlayerName,
        bIsTalking ? TEXT("started") : TEXT("stopped"));
}

void FMyVoiceChatManager::LeaveVoiceChannel(const FString& ChannelName)
{
    if (!VoiceChatUser) return;
    VoiceChatUser->LeaveChannel(ChannelName,
        FOnVoiceChatChannelLeaveCompleteDelegate::CreateLambda(
            [](const FString& LeftChannelName, const FVoiceChatResult& Result)
            {
                UE_LOG(LogTemp, Log, TEXT("Left channel: %s"), *LeftChannelName);
            }));
}

void FMyVoiceChatManager::Shutdown()
{
    if (VoiceChat && VoiceChatUser)
    {
        VoiceChat->ReleaseUser(VoiceChatUser);
        VoiceChatUser = nullptr;
    }
    if (VoiceChat)
    {
        VoiceChat->Uninitialize();
        VoiceChat = nullptr;
    }
}
```

**Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "VoiceChat",        // IVoiceChat 接口定义
    "EOSVoiceChat",     // EOS VoiceChat 实现
    "EOSShared",        // EOS 共享工具
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VoiceChat` | IVoiceChat/IVoiceChatUser 接口定义（PublicIncludePathModuleNames） |
| `Json` | FEOSVoiceChatChannelCredentials 的 JSON 序列化（PublicDependency） |
| `Core` | UE 核心库（PrivateDependency） |
| `Projects` | 模块和插件管理（PrivateDependency） |
| `EOSShared` | EOS 共享模块，提供 WITH_EOS_RTC 等编译宏和 SDK 管理器接口（PrivateDependency） |
| `EOSSDK` | Epic Online Services SDK 本体，RTC/Lobby 等原生 API（PrivateDependency） |
| `ApplicationCore` | 仅 iOS 平台，用于应用生命周期事件监听 |

插件还依赖 `EOSShared` 插件（在 .uplugin 中声明）。

## 架构概览

### 类层次

```
IVoiceChat (接口，定义在 VoiceChat 模块)
└── FEOSVoiceChat (核心实现，EOSVoiceChat.h)
    ├── FWindowsEOSVoiceChat  (Windows 平台扩展，覆盖 EOSPlatformCreate)
    ├── FIOSEOSVoiceChat      (iOS 平台扩展，覆盖 Initialize/User 管理，添加硬件 AEC、蓝牙麦克风)
    ├── FAndroidEOSVoiceChat  (Android 平台扩展，覆盖 CreateUser)
    └── Mac/Linux: 直接使用 FEOSVoiceChat（FPlatformEOSVoiceChat = FEOSVoiceChat）

IVoiceChatUser (接口)
└── FEOSVoiceChatUser (核心用户实现)
    ├── FIOSEOSVoiceChatUser  (iOS 专用，硬件 AEC 与蓝牙支持)
    └── FAndroidEOSVoiceChatUser (Android 专用)

FEOSVoiceChatFactory (IModularFeature 工厂)
└── CreateInstance() / CreateInstanceWithPlatform()

FEOSVoiceChatModule (IModuleInterface)
└── 注册 Factory 和 IVoiceChat 到 ModularFeatures
```

### 状态机

**初始化状态** (`FEOSVoiceChat::EInitializationState`)：
`Uninitialized` → `Initializing` → `Initialized` → `Uninitializing` → `Uninitialized`

**连接状态** (`FEOSVoiceChat::EConnectionState`)：
`Disconnected` → `Connecting` → `Connected` → `Disconnecting` → `Disconnected`

**登录状态** (`FEOSVoiceChatUser::ELoginState`)：
`LoggedOut` → `LoggingIn` → `LoggedIn` → `LoggingOut` → `LoggedOut`

**频道加入状态** (`FEOSVoiceChatUser::EChannelJoinState`)：
`NotJoined` → `Joining` → `Joined` → `Leaving` → `NotJoined`

### 平台差异

| 平台 | 类型别名 | 特殊功能 |
|---|---|---|
| Windows | `FWindowsEOSVoiceChat` | 自定义 Platform 创建 |
| iOS | `FIOSEOSVoiceChat` | 硬件 AEC、蓝牙麦克风、前后台切换处理 |
| Android | `FAndroidEOSVoiceChat` | 自定义 CreateUser |
| Mac | 直接用 `FEOSVoiceChat` | 无特殊处理 |
| Linux | 直接用 `FEOSVoiceChat` | 无特殊处理 |

## 错误处理

EOS SDK 的错误码通过 `ResultFromEOSResult()` 映射为 UE 统一的 `FVoiceChatResult`：

| EOS 错误 | 映射的 VoiceChat 错误 |
|---|---|
| `EOS_InvalidCredentials` / `EOS_InvalidAuth` | `CredentialsInvalid` |
| `EOS_InvalidUser` / `EOS_InvalidParameters` | `InvalidArgument` |
| `EOS_AccessDenied` / `EOS_MissingPermissions` | `NotPermitted` |
| `EOS_TooManyRequests` | `Throttled` |
| `EOS_AlreadyPending` | `AlreadyInProgress` |
| `EOS_NotConfigured` | `MissingConfig` |
| 其他 | `ImplementationError` + 原始错误描述 |

## 维护状态

### 近期更新

- `c851b86` (2025-09-23) — **EOSSDK CL45343210 Release v1.18.0.4 Full update**
  EOS SDK 更新到 v1.18.0.4，属于例行 SDK 版本升级，包含 RTC 和 Lobby 接口的 API 更新。

- `14fcdb4` (2025-09-23) — **[Backout] CL45934846**
  回退操作，说明上述 SDK 更新可能引入了问题需要暂时撤回，随后又被重新提交。

- `4c26457` (2025-09-23) — **EOSSDK CL45343210 Release v1.18.0.4 Full update**
  与第一条相同，是重新提交的 SDK 更新。

### 维护评价

- **创建时间**：2021 年 6 月，随 UE5 早期开发引入
- **最近更新**：2025 年 9 月，最近一次实质性更新是 EOS SDK 版本升级
- **维护状态**：**活跃维护中**。作为 Epic 自家在线服务的核心语音组件，随 EOS SDK 版本持续更新。
- **平台支持**：声明支持 Android、Mac、Win64；代码中存在 iOS 和 Linux 实现但不在 .uplugin 的 PlatformAllowList 中（iOS 通过单独的 PlatformAllowList 配置可能已支持）。
- **已知限制**：FEOSVoiceChatUser 中有 TODO 注释指出部分状态跟踪（如 bAudioMuted）与 VivoxVoiceChat 的实现方式不一致，状态值在 API 回调前就被设置，而不是在成功回调后更新。
- **推荐度**：如果你的项目使用 EOS 生态，这是唯一的 EOS 语音集成方案，**推荐使用**。如果不用 EOS，考虑 VivoxVoiceChat。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/VoiceChat/EOSVoiceChat)
- [VoiceChat 模块（接口定义）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/VoiceChat)
- [EOSShared 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/EOSShared)
