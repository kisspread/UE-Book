# TextToSpeech

> A text to speech system that can be used to make auditory speech announcements given input strings.

| 属性 | 值 |
|---|---|
| 中文名 | 文本转语音 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无（纯代码插件） |
| 模块 | `TextToSpeech` (Runtime), `Flite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TextToSpeech) | |

## 用途

**TextToSpeech** 插件提供跨平台的文本转语音（TTS）功能，允许开发者将任意字符串实时合成为语音并播放。它解决了在游戏或应用中通过听觉方式传达信息的通用需求，特别适用于无障碍辅助（如屏幕朗读）、NPC 对话语音、动态通知等场景。插件封装了平台原生 TTS 引擎（Windows、macOS、iOS、Android、Linux）以及可选的离线合成引擎 Flite（跨平台后备方案），并提供统一的 C++ 和蓝图接口。

## 使用场景

- **无障碍辅助**：为视障玩家朗读 UI 文本、游戏提示、对话选项，提升游戏可及性。
- **动态语音提示**：在战斗中触发状态变化、获得道具等事件时，用语音即时播报而不打断游戏流程。
- **NPC 对话朗读**：为过场动画或剧情对话提供语音，无需提前录制音频文件。
- **多语言支持**：通过切换不同平台的 TTS 引擎（若支持）或使用自定义语言库，实现多语种语音合成。

## 蓝图用法

插件通过 `UTextToSpeechEngineSubsystem`（引擎子系统）暴露所有蓝图可调用节点。每个 TTS 通道由一个 `FName` 标识，需先添加并激活通道后才能使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddDefaultChannel` | 使用平台默认 TTS 引擎创建新通道 | `UTextToSpeechEngineSubsystem` |
| `AddCustomChannel` | 使用自定义 C++ TTS 类创建通道 | `UTextToSpeechEngineSubsystem` |
| `RemoveChannel` | 移除指定通道并释放资源 | `UTextToSpeechEngineSubsystem` |
| `ActivateAllChannels` | 激活所有已添加的通道 | `UTextToSpeechEngineSubsystem` |
| `ActivateChannel` | 激活指定通道（之后才能调用 Speak） | `UTextToSpeechEngineSubsystem` |
| `DeactivateAllChannels` | 停用所有通道 | `UTextToSpeechEngineSubsystem` |
| `DeactivateChannel` | 停用指定通道 | `UTextToSpeechEngineSubsystem` |
| `SpeakOnChannel` | 在指定通道上立即朗读一段文字（会打断当前朗读） | `UTextToSpeechEngineSubsystem` |
| `StopSpeakingOnChannel` | 停止指定通道的当前朗读 | `UTextToSpeechEngineSubsystem` |
| `StopSpeakingOnAllChannels` | 停止所有通道的朗读 | `UTextToSpeechEngineSubsystem` |
| `IsSpeakingOnChannel` | 检查指定通道是否正在朗读 | `UTextToSpeechEngineSubsystem` |
| `GetVolumeOnChannel` | 获取指定通道的音量（0.0–1.0） | `UTextToSpeechEngineSubsystem` |
| `SetVolumeOnChannel` | 设置指定通道的音量 | `UTextToSpeechEngineSubsystem` |
| `GetRateOnChannel` | 获取指定通道的语速（0.0–1.0） | `UTextToSpeechEngineSubsystem` |
| `SetRateOnChannel` | 设置指定通道的语速 | `UTextToSpeechEngineSubsystem` |
| `MuteChannel` | 静音指定通道 | `UTextToSpeechEngineSubsystem` |
| `UnmuteChannel` | 取消静音指定通道 | `UTextToSpeechEngineSubsystem` |
| `MuteAllChannels` | 静音所有通道 | `UTextToSpeechEngineSubsystem` |
| `UnmuteAllChannels` | 取消所有通道静音 | `UTextToSpeechEngineSubsystem` |
| `IsChannelMuted` | 检查指定通道是否静音 | `UTextToSpeechEngineSubsystem` |

### 使用示例（蓝图描述）

1. **初始化一个 TTS 通道**  
   - 在 `Event BeginPlay` 中调用 `Add Default Channel`（节点输入 `Channel Id` = 自定义名字，如 "Main"）。  
   - 然后调用 `Activate Channel`，传入相同的 `Channel Id`。

2. **朗读一段文字**  
   - 连接任意事件（如按钮点击）到 `Speak On Channel`，设置 `Channel Id` 为 "Main"，`String To Speak` 填入文本。  
   - 若需要监听朗读完成事件，通过 `Get TTS Channel Finished Speaking Delegate`（无 BlueprintCallable，需在 C++ 中绑定）或使用连续调用技巧。

3. **临时静音**  
   - 调用 `Mute Channel`（指定 "Main"）可使该通道停止播放，之后调用 `Unmute Channel` 恢复。

## C++ 用法

### 头文件引入

```cpp
#include "TextToSpeech.h"
#include "TextToSpeechModule.h"
#include "GenericPlatform/TextToSpeechBase.h" // 如需要直接操作 FTextToSpeechBase
```

### 基本用法

```cpp
// 通过模块获取平台默认 TTS 工厂并创建 TTS 对象
TSharedRef<FTextToSpeechBase> TTS = ITextToSpeechModule::Get().GetPlatformFactory()->Create();
TTS->Activate();

// 朗读一段文字（异步）
TTS->Speak(TEXT("Hello, World!"));

// 检查是否正在朗读
if (TTS->IsSpeaking()) { /* ... */ }

// 停止朗读
TTS->StopSpeaking();

// 设置音量 0.5，语速 0.7
TTS->SetVolume(0.5f);
TTS->SetRate(0.7f);

// 静音
TTS->Mute();

// 注册完成回调
TTS->SetTextToSpeechFinishedSpeakingDelegate(FTextToSpeechBase::FOnTextToSpeechFinishSpeaking::CreateLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Speech finished!"));
}));

// 使用完毕后停用
TTS->Deactivate();
```

**来源**：`Engine/Plugins/Experimental/TextToSpeech/Source/TextToSpeech/Public/TextToSpeechModule.h`（模块示例注释）

### 进阶用法：使用蓝图子系统直接操作通道

```cpp
// 获取引擎子系统
UTextToSpeechEngineSubsystem* TTSSubsystem = GEngine->GetEngineSubsystem<UTextToSpeechEngineSubsystem>();
if (!TTSSubsystem) return;

// 添加并激活一个默认通道
TTSSubsystem->AddDefaultChannel("VoiceOver");
TTSSubsystem->ActivateChannel("VoiceOver");

// 在通道上朗读
TTSSubsystem->SpeakOnChannel("VoiceOver", TEXT("Player health critical."));

// 检查通道是否正在朗读
bool bSpeaking = TTSSubsystem->IsSpeakingOnChannel("VoiceOver");

// 停止
TTSSubsystem->StopSpeakingOnChannel("VoiceOver");

// 移除通道（释放资源）
TTSSubsystem->RemoveChannel("VoiceOver");
```

**来源**：`Engine/Plugins/Experimental/TextToSpeech/Source/TextToSpeech/Public/TextToSpeechEngineSubsystem.h` 中的 UCLASS 声明。

### 自定义 TTS 工厂（高级）

```cpp
// 继承 ITextToSpeechFactory 实现自定义 TTS 类
class FMyTextToSpeechFactory : public ITextToSpeechFactory
{
public:
    virtual TSharedRef<FTextToSpeechBase> Create() override
    {
        return MakeShared<FMyTextToSpeech>();
    }
};

// 注册到模块
ITextToSpeechModule::Get().SetCustomFactory(MakeShared<FMyTextToSpeechFactory>());
TSharedRef<FTextToSpeechBase> CustomTTS = ITextToSpeechModule::Get().GetCustomFactory()->Create();
CustomTTS->Activate();
```

**来源**：`Engine/Plugins/Experimental/TextToSpeech/Source/TextToSpeech/Public/ITextToSpeechFactory.h` 和 `TextToSpeechModule.h` 示例。

## Demo 示例

以下是一个简单的 GameInstance 子类，在游戏启动时朗读欢迎信息。

### WelcomeGameInstance.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "TextToSpeechBase.h"
#include "TextToSpeechModule.h"
#include "WelcomeGameInstance.generated.h"

UCLASS()
class UWelcomeGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    virtual void Init() override;

private:
    TSharedPtr<FTextToSpeechBase> TTS;
};
```

### WelcomeGameInstance.cpp

```cpp
#include "WelcomeGameInstance.h"

void UWelcomeGameInstance::Init()
{
    Super::Init();

    // 获取平台默认 TTS 并激活
    if (ITextToSpeechModule::IsAvailable())
    {
        TTS = ITextToSpeechModule::Get().GetPlatformFactory()->Create();
        TTS->Activate();
    }

    if (TTS.IsValid())
    {
        // 朗读欢迎词
        TTS->Speak(TEXT("Welcome to the game!"));
        // 注册完成回调：稍后朗读另一句
        TTS->SetTextToSpeechFinishedSpeakingDelegate(
            FTextToSpeechBase::FOnTextToSpeechFinishSpeaking::CreateLambda([this]()
            {
                if (TTS.IsValid())
                {
                    TTS->Speak(TEXT("Enjoy your adventure."));
                }
            })
        );
    }
}
```

**注意**：上述示例未处理模块加载时机（`PostEngineInit` 加载），在实际项目中建议在 `PostEngineInit` 之后调用，或在 `BeginPlay` 中执行。

## 模块依赖

仅列出该插件特殊的依赖模块，省略标准核心模块（Core、Engine、Slate 等）。

| 模块 | 用途 |
|---|---|
| `Flite`（第三方） | 提供离线语音合成能力，作为平台 TTS 不可用时的后备方案（通过条件编译 `USING_FLITE` 控制） |

其他依赖：无特殊依赖（仅标准 Core/Engine/UKismet 等）。

## 维护状态

### 近期更新

- 2025-02-19 392e7feb TTS: Wrapping other maincall correctly for iOS  
- 2025-02-19 623d8d9d TTS: Fixing up iOS issues.  
- 2025-02-18 333f3417 TTS: Add missing copyrights.  
- 2025-02-18 ebb840a9 TTS: Unifying the IOS and Mac TTS implementation.  
- 2024-12-16 c6a7b0e3 WinArm64 fixes: (首次提交相关)

### 维护评价

- 创建于 2024-12-16，至今约半年，属于较新的插件。  
- 2025年2月仍有多项功能更新和平台修复，说明开发团队正在积极迭代。  
- 当前版本号为 0.1，标记为实验性，API 可能发生变化。  
- 已知限制：不推荐用于长句子或段落（建议拆分通过回调逐步朗读）；自定义工厂支持需 C++ 实现。  
- **推荐使用场景**：无障碍或简单动态语音提示；实验性质，生产环境前需充分测试平台兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TextToSpeech)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（未提供独立文档，可通过搜索引擎查找 TTS 相关页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TextToSpeech/Source/TextToSpeech/Tests)（可能位于 Engine/Tests/ 下，待验证）