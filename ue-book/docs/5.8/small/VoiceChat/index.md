# Voice Chat Interface

> Voice Chat Interface

| 属性 | 值 |
|---|---|
| 中文名 | 语音聊天接口 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VoiceChat` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-29 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/VoiceChat/VoiceChat) | |

## 用途

这个插件提供了一套**纯头文件的抽象接口**，用于统一语音聊天功能的接入。它本身不实现任何具体的语音聊天功能（如 Vivox、EOS Voice），而是定义了所有语音聊天服务必须遵循的通用接口和数据结构。其核心价值在于：
1.  **解耦**：游戏逻辑可以基于 `IVoiceChatUser` 等接口编程，而不依赖于任何具体的语音服务商实现。
2.  **标准化**：统一了错误处理 (`FVoiceChatResult`)、设备管理、频道类型（非定位/3D定位/回声）、音频数据流委托等关键概念。
3.  **可扩展性**：为 Vivox、EOS Voice 等不同后端提供了标准的接入点，开发者可以编写与实现无关的代码。

它本质上是一个**接口层（Interface Layer）**，是游戏接入语音聊天系统的“契约”定义。

## 使用场景

-   你的项目需要接入语音聊天，但希望保持代码的灵活性，未来可以轻松切换不同的服务商（如从自研切换到 EOS Voice）。
-   你正在开发一个需要语音聊天功能的多人游戏，希望用一套统一的API来管理登录、加入频道、麦克风/扬声器设备等。
-   你需要对原始的PCM音频数据进行访问或处理（如降噪、变声），该插件提供了相关的委托接口。
-   **注意**：该插件默认未启用 (`EnabledByDefault: false`)，并且是一个纯接口插件，你需要同时启用一个具体的实现插件（如 `EOSVoiceChat` 或 `VivoxVoiceChat`）才能使用语音功能。

## 蓝图用法

该插件是一个纯C++头文件接口库，**不包含任何`UFUNCTION(BlueprintCallable)`函数或蓝图资产**。
其所有接口和类均为C++抽象类，旨在被C++实现类继承和使用。

蓝图中使用语音聊天功能的典型方式是通过一个继承自 `UObject` 并实现了 `IVoiceChatUser` 等接口的**管理器类**。该管理器类可以暴露 `BlueprintCallable` 函数供蓝图调用，例如 `JoinVoiceChannel`, `SetMicrophoneVolume` 等。具体的实现逻辑和蓝图节点由提供实际语音服务的插件（如 EOSVoiceChat）或项目自行开发的管理器类决定。

## C++ 用法

### 头文件引入

```cpp
// 核心接口和类型定义
#include "VoiceChat.h"

// 错误处理相关
#include "VoiceChatResult.h"
#include "VoiceChatErrors.h"
```

### 基本用法

1.  **实现 `IVoiceChatUser` 接口**：
    你需要创建一个类（通常是 `UObject` 或其子类）来实现 `IVoiceChatUser` 接口。这个类将封装与特定语音后端的交互。

    ```cpp
    // MyVoiceChatUser.h
    #pragma once
    #include "VoiceChat.h"

    class UMyVoiceChatUser : public UObject, public IVoiceChatUser
    {
        GENERATED_BODY()

    public:
        // 实现 IVoiceChatUser 的纯虚函数
        virtual void SetSetting(const FString& Name, const FString& Value) override;
        virtual FString GetSetting(const FString& Name) override;
        // ... 实现其他接口函数，如 Login, JoinChannel, Set3DPosition 等
    };
    ```

2.  **使用错误处理**：
    利用 `FVoiceChatResult` 和 `VoiceChat::Errors` 命名空间来标准化错误返回。

    ```cpp
    #include "VoiceChatErrors.h"

    FVoiceChatResult UMyVoiceChatUser::SomeOperation()
    {
        if (!bIsInitialized)
        {
            // 返回标准的“未初始化”错误
            return VoiceChat::Errors::NotInitialized();
        }

        // ... 业务逻辑

        // 操作成功
        return FVoiceChatResult::CreateSuccess();
    }
    ```

### 进阶用法

**处理异步操作和委托**：
`IVoiceChatUser` 接口为登录、加入频道等操作定义了完成委托。你需要在实现中绑定并广播这些委托。

```cpp
// 绑定登录完成回调
void UMyVoiceChatUser::Login(FPlatformUserId PlatformId, const FString& PlayerName, const FString& Credentials, const FOnVoiceChatLoginCompleteDelegate& Delegate)
{
    // 发起异步登录请求...
    // 在登录完成时（例如在回调函数中）调用：
    Delegate.ExecuteIfBound(PlayerName, FVoiceChatResult::CreateSuccess());
    // 广播多播委托，通知其他监听者
    OnVoiceChatLoggedInDelegate.Broadcast(PlayerName);
}

// 监听音频数据
// 在你的实现中，当捕获到音频PCM数据时，可以广播委托
void UMyVoiceChatUser::HandleCapturedAudio(const TArray<int16>& PcmSamples, int32 SampleRate, int32 Channels)
{
    // 广播捕获后的音频数据，供其他系统（如VAD）处理
    OnVoiceChatAfterCaptureAudioReadDelegate2.Broadcast(/* ... 参数 ... */);
}
```

## Demo 示例

下面是一个最小化的 `IVoiceChatUser` 接口实现框架，展示了基本结构和错误处理。

**MyVoiceChatUser.h**
```cpp
#pragma once
#include "VoiceChat.h"
#include "VoiceChatResult.h"
#include "MyVoiceChatUser.generated.h"

UCLASS()
class UMyVoiceChatUser : public UObject, public IVoiceChatUser
{
    GENERATED_BODY()

public:
    // --- IVoiceChatUser Interface ---
    virtual void SetSetting(const FString& Name, const FString& Value) override;
    virtual FString GetSetting(const FString& Name) override;
    virtual void SetAudioInputVolume(float Volume) override;
    virtual float GetAudioInputVolume() const override;
    // ... 其他必需的纯虚函数声明 ...

    // 登录接口实现示例
    virtual void Login(FPlatformUserId PlatformId, const FString& PlayerName, const FString& Credentials, const FOnVoiceChatLoginCompleteDelegate& Delegate) override;

    // 委托接口实现
    virtual FOnVoiceChatLoggedInDelegate& OnVoiceChatLoggedIn() override { return OnVoiceChatLoggedInDelegate; }

private:
    // 内部状态
    float CurrentInputVolume = 1.0f;
    bool bIsInitialized = false;
    bool bIsLoggedIn = false;

    // 多播委托实例
    FOnVoiceChatLoggedInDelegate OnVoiceChatLoggedInDelegate;
};
```

**MyVoiceChatUser.cpp**
```cpp
#include "MyVoiceChatUser.h"
#include "VoiceChatErrors.h"

void UMyVoiceChatUser::SetSetting(const FString& Name, const FString& Value)
{
    // 实现设置功能，记录日志或存储配置
    UE_LOG(LogTemp, Log, TEXT("Setting '%s' set to '%s'"), *Name, *Value);
}

FString UMyVoiceChatUser::GetSetting(const FString& Name)
{
    // 返回对应的设置值
    return TEXT("Default");
}

void UMyVoiceChatUser::SetAudioInputVolume(float Volume)
{
    // 将音量限制在0.0到2.0之间
    CurrentInputVolume = FMath::Clamp(Volume, 0.0f, 2.0f);
}

float UMyVoiceChatUser::GetAudioInputVolume() const
{
    return CurrentInputVolume;
}

void UMyVoiceChatUser::Login(FPlatformUserId PlatformId, const FString& PlayerName, const FString& Credentials, const FOnVoiceChatLoginCompleteDelegate& Delegate)
{
    // 模拟一个需要初始化的异步操作
    if (!bIsInitialized)
    {
        // 使用预定义的错误
        Delegate.ExecuteIfBound(PlayerName, VoiceChat::Errors::NotInitialized());
        return;
    }

    // 模拟异步登录
    FTimerHandle TimerHandle;
    GetWorld()->GetTimerManager().SetTimer(TimerHandle, [this, PlayerName, Delegate]()
    {
        bIsLoggedIn = true;
        // 操作成功，通知委托
        Delegate.ExecuteIfBound(PlayerName, FVoiceChatResult::CreateSuccess());
        // 广播全局登录事件
        OnVoiceChatLoggedInDelegate.Broadcast(PlayerName);
    }, 2.0f, false); // 模拟2秒延迟
}
```

## 模块依赖

该插件是纯头文件插件，其 `VoiceChat.Build.cs` 文件内容未提供。但作为接口层，它通常**不引入任何额外的运行时模块依赖**。具体实现插件（如 EOSVoiceChat）会处理底层SDK的依赖。

对于使用此接口的游戏模块，在 `Build.cs` 中通常只需添加模块名到 `PublicIncludePathModuleNames` 以便头文件可被找到，或者直接包含头文件路径。无需声明运行时依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `6ff79bee` | - Add new call stats delegate passing a channelName | 新增了带频道名称的通话统计委托接口 |
| 2026-03-16 | `a456d983` | [EOSVoiceChat] Responding to feedback from last review in which the API for choosing between Mixed v... | EOS语音插件根据评审反馈调整了混合模式API |
| 2026-03-06 | `8cd30921` | Set up audio loopback to EOS to allow voice chat to be routed out of the submix and into the EOS ren... | 为EOS设置音频回环，支持将语音从子混音路由到EOS渲染器 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 执行了引擎代码修正，将所有自定义析构函数改为默认 |
| 2025-10-29 | `58d2776d` | - Add LexToString for some VoiceChat enums | 为一些VoiceChat枚举添加了LexToString转换函数 |

### 维护评价

**接口层处于稳定维护状态。**
-   **年龄**：该接口插件已存在约6年，是一个相对成熟的抽象层。
-   **活跃度**：最近一次更新在2026年5月，主要为接口添加了新功能（带频道名的统计委托），这表明它仍在根据实际需求（如支持多频道场景）进行演进。
-   **性质**：作为基础接口，其变更通常与具体实现插件（如EOSVoiceChat）的更新同步。近期更新多数与EOS语音插件的改进相关。
-   **推荐度**：**推荐使用**。如果你的项目需要一个与具体服务商解耦的语音聊天系统架构，这个接口是标准的选择。但请注意，它本身不提供功能，必须配合一个实现插件使用。由于是纯接口，其稳定性很高。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/VoiceChat/VoiceChat)
-   [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/voice-chat-plugin-in-unreal-engine) (参考官方在线子系统文档)
-   **无专门测试用例**：作为接口定义插件，其测试通常包含在实现插件的测试中。