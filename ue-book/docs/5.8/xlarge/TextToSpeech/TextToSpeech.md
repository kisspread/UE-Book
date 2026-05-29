# TextToSpeech

> A text to speech system that can be used to make auditory speech announcements given input strings.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 文本转语音 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TextToSpeech` (Runtime), `Flite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-11 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TextToSpeech) | |

## 用途

TextToSpeech 插件为虚幻引擎提供了一个跨平台的文本转语音（TTS）系统。它解决的核心问题是：**如何在游戏或应用运行时，将文本字符串实时转换为可听见的语音输出**。

插件并非简单地集成一个语音库，而是构建了一个完整的、可扩展的框架。它通过一个 **子系统（Subsystem）** 管理多个独立的 **TTS 通道（Channel）**，允许开发者同时控制多个独立的语音流（例如，一个用于UI提示，一个用于游戏内对话）。每个通道可以独立调节音量、语速、静音或停止。

对于每个支持的平台（Windows, Mac, iOS, Android, Linux），插件都提供了开箱即用的平台默认语音实现（如 Windows 上使用 Flite 开源库，Apple 平台使用 AVSpeechSynthesizer）。更关键的是，它允许开发者通过 **工厂（Factory）** 模式注册自定义的 C++ TTS 实现，从而集成任何第三方语音合成引擎。

**本质上，该插件是一个为游戏和交互式应用打造的、可控且可扩展的实时语音播报引擎，主要用于增强可访问性和提供非视觉反馈。**

## 使用场景

- **无障碍辅助功能**：为视觉障碍玩家提供游戏内文本信息的语音播报，例如菜单选项、任务日志、系统通知。
- **游戏内语音提示**：在多人游戏中播报击杀通知、倒计时、战况简报，或为NPC提供基础的语音对话。
- **教育与培训软件**：将学习材料、指示说明朗读出来，增强学习体验。
- **动态叙事**：在非线性叙事或随机生成内容中，实时合成角色对话旁白。
- **调试与开发工具**：在开发期间快速听查变量的值或程序状态，无需查看屏幕。

## 蓝图用法

蓝图功能主要通过 `UTextToSpeechEngineSubsystem` 子系统暴露。首先需要通过 `Get Engine Subsystem` 节点获取该子系统的实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddDefaultChannel` | 创建一个新的、使用平台默认语音引擎的TTS通道。 | `UTextToSpeechEngineSubsystem` |
| `AddCustomChannel` | 创建一个新的、使用用户自定义C++语音引擎的TTS通道。 | `UTextToSpeechEngineSubsystem` |
| `ActivateChannel` | 激活一个已创建的通道，使其可以接受语音请求。 | `UTextToSpeechEngineSubsystem` |
| `SpeakOnChannel` | **核心节点**。在指定通道上立即朗读一个字符串，会中断当前正在朗读的内容。 | `UTextToSpeechEngineSubsystem` |
| `StopSpeakingOnChannel` | 立即停止指定通道上的语音播报。 | `UTextToSpeechEngineSubsystem` |
| `SetVolumeOnChannel` | 设置指定通道的音量（0.0 - 1.0）。 | `UTextToSpeechEngineSubsystem` |
| `SetRateOnChannel` | 设置指定通道的语速（0.0 - 1.0）。 | `UTextToSpeechEngineSubsystem` |
| `MuteChannel` / `UnmuteChannel` | 静音或取消静音指定通道。 | `UTextToSpeechEngineSubsystem` |
| `IsSpeakingOnChannel` | 检查指定通道是否正在播报。 | `UTextToSpeechEngineSubsystem` |
| `DoesChannelExist` | 检查指定ID的通道是否存在。 | `UTextToSpeechEngineSubsystem` |

### 使用示例（蓝图描述）

1.  **初始化**：
    *   调用 `AddDefaultChannel` 并传入一个唯一的 `FName`（如 `"UIVoice"`）来创建一个TTS通道。
    *   调用 `ActivateChannel` 并传入相同的 `FName` 来激活该通道。

2.  **播报文本**：
    *   调用 `SpeakOnChannel`，将 `"UIVoice"` 作为通道ID，将要朗读的字符串（如 `"任务开始，请前往目标点"`）作为输入。语音将立即开始播放。

3.  **控制播放**：
    *   当需要停止时，调用 `StopSpeakingOnChannel`。
    *   在播报前或播报中，可调用 `SetVolumeOnChannel` 和 `SetRateOnChannel` 来调整参数。
    *   使用 `MuteChannel` 和 `UnmuteChannel` 临时控制声音输出。

4.  **多通道管理**：
    *   可以重复步骤1，用不同的 `FName`（如 `"GameAlert"`）创建另一个通道。
    *   两个通道可以独立控制，互不干扰。

## C++ 用法

C++用法提供了更底层的控制和扩展能力，主要围绕 `ITextToSpeechModule`、`FTextToSpeechBase` 和 `ITextToSpeechFactory`。

### 头文件引入

```cpp
#include "TextToSpeechModule.h" // 主要模块接口
#include "TextToSpeechBase.h"   // TTS对象基类
#include "ITextToSpeechFactory.h" // 工厂接口
// 便捷头文件，包含以上所有
#include "TextToSpeech.h"
```

### 基本用法

使用平台默认的TTS对象进行播报。

```cpp
// 获取模块单例
ITextToSpeechModule& TTSModule = ITextToSpeechModule::Get();

// 通过平台工厂创建一个TTS对象
TSharedPtr<ITextToSpeechFactory> PlatformFactory = TTSModule.GetPlatformFactory();
if (PlatformFactory.IsValid())
{
    TSharedRef<FTextToSpeechBase> MyTTS = PlatformFactory->Create();

    // 激活
    MyTTS->Activate();

    // 播报
    MyTTS->Speak(TEXT("这是一个测试语音。"));

    // 设置属性
    MyTTS->SetVolume(0.8f);
    MyTTS->SetRate(0.5f);

    // ... 在适当的时候（如对象销毁时）
    MyTTS->Deactivate();
}
```

### 进阶用法

1.  **使用引擎子系统（推荐用于蓝图集成）**：
    ```cpp
    // 获取子系统
    UTextToSpeechEngineSubsystem* TTSSubsystem = GEngine->GetEngineSubsystem<UTextToSpeechEngineSubsystem>();
    if (TTSSubsystem)
    {
        const FName ChannelName = TEXT("MyChannel");
        // 创建并激活通道
        TTSSubsystem->AddDefaultChannel(ChannelName);
        TTSSubsystem->ActivateChannel(ChannelName);

        // 播报
        TTSSubsystem->SpeakOnChannel(ChannelName, TEXT("通过子系统播报。"));

        // 监听播报完成（需要先设置回调）
        // FTextToSpeechBase::FOnTextToSpeechFinishSpeaking FinishDelegate;
        // FinishDelegate.BindLambda([](){ UE_LOG(LogTemp, Log, TEXT("播报完成")); });
        // 内部TTS对象需要先通过某种方式获取并设置此委托。
    }
    ```

2.  **实现自定义TTS工厂和对象**：
    ```cpp
    // 1. 继承工厂类
    class FMyCustomTTSFactory : public ITextToSpeechFactory
    {
    public:
        virtual TSharedRef<FTextToSpeechBase> Create() override
        {
            return MakeShared<FMyCustomTextToSpeech>();
        }
    };

    // 2. 继承TTS基类
    class FMyCustomTextToSpeech : public FTextToSpeechBase
    {
    public:
        virtual void Speak(const FString& InStringToSpeak) override
        {
            // 调用你自己的第三方语音引擎
            MyThirdPartyTTSLib_Speak(InStringToSpeak.GetCharArray().GetData());
            // 完成后，必须调用此方法通知系统
            OnTextToSpeechFinishSpeaking_GameThread();
        }
        // ... 实现其他纯虚函数 IsSpeaking, StopSpeaking 等
    };

    // 3. 在模块启动时注册你的自定义工厂
    // 通常在某个模块的 StartupModule() 中执行
    TSharedRef<FMyCustomTTSFactory> MyFactory = MakeShared<FMyCustomTTSFactory>();
    ITextToSpeechModule::Get().SetCustomFactory(MyFactory);

    // 4. 之后，你就可以通过 AddCustomChannel 在子系统中使用它了
    ```

## Demo 示例

一个完整的、使用子系统管理单个通道并播报“Hello World”的最小示例。

### MyTTSActor.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTTSActor.generated.h"

UCLASS()
class AMyTTSActor : public AActor
{
    GENERATED_BODY()
public:
    AMyTTSActor();

    // 当Actor被生成时调用
    virtual void BeginPlay() override;

    // 一个自定义的播报函数
    UFUNCTION(BlueprintCallable, Category = "TTS Demo")
    void SpeakText(const FString& TextToSpeak);

    // 一个停止播报的函数
    UFUNCTION(BlueprintCallable, Category = "TTS Demo")
    void StopSpeaking();

private:
    // 我们的TTS通道名称
    const FName TTChannelName = FName(TEXT("DemoVoice"));
};
```

### MyTTSActor.cpp
```cpp
#include "MyTTSActor.h"
#include "TextToSpeechEngineSubsystem.h"
#include "Engine/Engine.h"

AMyTTSActor::AMyTTSActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTTSActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取引擎子系统
    UTextToSpeechEngineSubsystem* TTSSubsystem = GEngine->GetEngineSubsystem<UTextToSpeechEngineSubsystem>();
    if (TTSSubsystem)
    {
        // 创建并激活通道
        TTSSubsystem->AddDefaultChannel(TTChannelName);
        TTSSubsystem->ActivateChannel(TTChannelName);

        // 播报一段初始化文本
        SpeakText(TEXT("TTS示例已初始化。"));
    }
}

void AMyTTSActor::SpeakText(const FString& TextToSpeak)
{
    UTextToSpeechEngineSubsystem* TTSSubsystem = GEngine->GetEngineSubsystem<UTextToSpeechEngineSubsystem>();
    if (TTSSubsystem && TTSSubsystem->DoesChannelExist(TTChannelName))
    {
        TTSSubsystem->SpeakOnChannel(TTChannelName, TextToSpeak);
    }
}

void AMyTTSActor::StopSpeaking()
{
    UTextToSpeechEngineSubsystem* TTSSubsystem = GEngine->GetEngineSubsystem<UTextToSpeechEngineSubsystem>();
    if (TTSSubsystem && TTSSubsystem->DoesChannelExist(TTChannelName))
    {
        TTSSubsystem->StopSpeakingOnChannel(TTChannelName);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TextToSpeech` | 核心插件模块，提供TTS框架、子系统和平台实现。 |
| `Flite` | 第三方库模块，为Windows和Linux平台提供Flite语音合成引擎。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到新的UE_LOGF格式。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了模块对可移植工具链不支持的问题。 |
| 2026-01-13 | `4c04edd1` | [IOS/Mac] Initial pass to remove iOS/macOS sdk headers from Engine platform header files where possi | 移除引擎平台头文件中对iOS/macOS SDK头文件的直接包含。 |
| 2025-02-19 | `392e7feb` | TTS: Wrapping other maincall correctly for iOS | 正确封装了iOS平台的其他主要调用。 |
| 2025-02-19 | `623d8d9d` | TTS: Fixing up iOS issues. | 修复了iOS平台的相关问题。 |

### 维护评价

该插件自2021年3月创建以来已超过5年。从提交记录看，它**并非处于高强度活跃开发状态**，但**仍在持续维护中**，尤其是在**跨平台兼容性**方面（近期提交主要集中在iOS、Mac和工具链修复）。上一次实质性功能更新历史较久。

**优点**：框架设计清晰，扩展性好，支持多平台和自定义实现。作为实验性插件，其核心架构是稳定的。

**限制与风险**：
1.  **实验性状态**：`.uplugin` 标记为 `IsExperimental: true`，且 `EnabledByDefault: false`。这意味着它可能随时发生不兼容的API变更，不建议在需要长期稳定支持的生产项目中直接依赖。
2.  **更新频率低**：近期更新主要是编译和平台兼容性修复，而非新功能迭代。
3.  **已知限制**：根据源码注释，Flite实现当前仅支持英语（US_EN）。

**推荐使用**：**适用于需要快速集成基础文本转语音功能的原型开发、内部工具或对语音质量要求不高的项目**。如果项目对TTS有深度定制、多语言支持或高性能要求，建议评估该框架后决定是基于它扩展，还是直接集成更专业的第三方TTS解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TextToSpeech)
- [官方文档](https://docs.unrealengine.com/) (该插件暂无独立官方文档页面，请参考引擎文档的可访问性章节)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/TextToSpeech) (如果存在)