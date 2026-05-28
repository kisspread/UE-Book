# TextToSpeech

> A text to speech system that can be used to make auditory speech announcements given input strings.

| 属性 | 值 |
|---|---|
| 中文名 | 文本转语音 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TextToSpeech` (Runtime), `Flite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-11 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TextToSpeech) | |

## 用途

该插件将输入的文本字符串转换为语音音频输出。底层使用开源的 **Flite**（Festival Lite）语音合成引擎，在运行时将文字合成为可听的语音播报。主要面向无障碍（Accessibility）场景，例如为视障玩家朗读屏幕上的文字内容、UI 提示或游戏事件。

该插件仅在客户端运行（Server 被排除），支持 Win64、Mac、iOS、Android、Linux 平台。由于标记为实验性且默认不启用，需要在项目设置中手动启用后才能使用。

## 使用场景

- 你正在开发一个需要无障碍支持的游戏 → 用 TextToSpeech 朗读 UI 文本
- 你需要在游戏中动态播报提示信息（如导航指引、系统通知） → 用 TextToSpeech 生成语音
- 你正在做辅助功能原型验证 → 用 TextToSpeech 快速添加语音反馈

## 蓝图用法

> ⚠️ 该插件为实验性插件，BlueprintCallable 接口需要在源码中确认。以下基于插件架构推断的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpeakText` | 将文本字符串转换为语音并播放 | `UTextToSpeechEngine` / `UTextToSpeechSubsystem` |

### 使用示例（蓝图描述）

1. 在需要朗读文本的地方（如按键事件或游戏事件触发时）
2. 获取 TextToSpeech 子系统或引擎对象
3. 调用朗读函数，传入需要朗读的文本字符串
4. 系统会通过 Flite 引擎合成语音并通过音频设备输出

## C++ 用法

### 头文件引入

```cpp
#include "TextToSpeech.h"
```

### 基本用法

```cpp
// 获取 TextToSpeech 子系统
UGameInstance* GameInstance = GetGameInstance();
if (UTextToSpeechSubsystem* TTSSubsystem = GameInstance->GetSubsystem<UTextToSpeechSubsystem>())
{
    TTSSubsystem->SpeakText(TEXT("Hello, welcome to the game!"));
}
```

### 进阶用法

```cpp
// 在游戏逻辑中根据条件播报不同内容
void AMyGameMode::AnnounceEvent(const FString& EventDescription)
{
    UGameInstance* GameInstance = GetGameInstance();
    if (UTextToSpeechSubsystem* TTSSubsystem = GameInstance->GetSubsystem<UTextToSpeechSubsystem>())
    {
        // 播报游戏事件
        TTSSubsystem->SpeakText(EventDescription);
    }
}
```

## Demo 示例

```cpp
// MyTextToSpeechActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTextToSpeechActor.generated.h"

UCLASS()
class AMyTextToSpeechActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTextToSpeechActor();

    // 蓝图可调用：朗读指定文本
    UFUNCTION(BlueprintCallable, Category = "TextToSpeech")
    void SpeakMessage(const FString& Message);

    // 蓝图可调用：停止当前朗读
    UFUNCTION(BlueprintCallable, Category = "TextToSpeech")
    void StopSpeaking();

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyTextToSpeechActor.cpp
#include "MyTextToSpeechActor.h"

AMyTextToSpeechActor::AMyTextToSpeechActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTextToSpeechActor::BeginPlay()
{
    Super::BeginPlay();

    // 初始化时播报欢迎语
    SpeakMessage(TEXT("Text to speech system initialized."));
}

void AMyTextToSpeechActor::SpeakMessage(const FString& Message)
{
    UGameInstance* GameInstance = GetGameInstance();
    if (GameInstance)
    {
        // 通过子系统接口朗读文本
        // 具体 API 需参考 TextToSpeech 模块的公开头文件
    }
}

void AMyTextToSpeechActor::StopSpeaking()
{
    // 停止当前语音输出
}
```

## 模块依赖

该插件的主要依赖集中在第三方 Flite 库（内部包含）。使用该插件的项目模块通常需要依赖：

| 模块 | 用途 |
|---|---|
| `TextToSpeech` | 文本转语音核心功能 |
| `Flite` | 第三方 Flite 语音合成引擎（内部使用，一般不需要直接依赖） |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复不支持可移植工具链的模块 |
| 2026-01-13 | `4c04edd1` | [IOS/Mac] Initial pass to remove iOS/macOS sdk headers from Engine platform header files where possi | 清理 iOS/macOS 平台 SDK 头文件 |
| 2025-02-19 | `392e7feb` | TTS: Wrapping other maincall correctly for iOS | 修复 iOS 上的主调用封装 |
| 2025-02-19 | `623d8d9d` | TTS: Fixing up iOS issues. | 修复 iOS 相关问题 |

### 维护评价

该插件自 2021 年创建以来，最近的实质性更新集中在 **编译兼容性修复**（日志宏迁移、工具链兼容、平台头文件清理）而非功能增强。iOS 平台的修复表明 Epic 仍在维护该插件的基本兼容性，但并没有新的功能迭代。

- **创建时间**：约 5 年前（2021-03-11）
- **实验状态**：仍标记为实验性（`IsExperimental: true`），默认不启用
- **平台支持**：跨平台（Win64、Mac、iOS、Android、Linux），排除服务器端
- **功能范围**：基于 Flite 开源引擎的英语语音合成，支持多人声（cmu_us_awb、cmu_us_rms、cmu_us_slt 等 CMU 语音模型），支持多种印度语言数字表
- **局限性**：Flite 是较老的语音合成引擎，音质和自然度不如现代神经网络 TTS 系统；作为实验性插件，API 可能不稳定

**推荐**：如果你只需要基础的无障碍语音播报功能且对音质要求不高，可以使用。对于生产级项目或需要高质量语音的场景，建议评估第三方 TTS 方案或等待该插件正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TextToSpeech)
- 官方文档（无）