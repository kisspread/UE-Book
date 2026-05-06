# Flite

> 无（Flite 是嵌入的第三方 TTS 引擎，无独立 .uplugin 描述）

| 属性 | 值 |
|---|---|
| 中文名 | Flite 轻量语音合成引擎 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Flite 编译好的静态库及头文件） |
| 模块 | `Flite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/TextToSpeech/Source/ThirdParty/Flite) | |

## 用途

Flite（Festival Lite）是由卡内基梅隆大学开发的轻量级、可移植的语音合成（TTS）引擎。本模块将 Flite 引擎作为 UE5 TextToSpeech 插件的第三方依赖库嵌入，为插件提供从文本到音频波形的核心合成能力。Flite 特别适用于对内存占用和跨平台兼容性要求较高的应用场景（如移动设备、嵌入式环境），它支持英文等多语言的语音输出，并提供了多种合成方法（如 ClusterGen、Diphone 等）。

> **注意**：Flite 模块不直接暴露给用户使用，而是被 `TextToSpeech` 主模块内部调用。普通用户应通过 `UTextToSpeech` 类访问 TTS 功能。

## 使用场景

- 你需要为游戏或应用中的 UI 界面、过场动画、提示信息添加语音朗读功能（无障碍辅助）。
- 你正在开发需要离线语音合成的应用，不希望依赖网络服务。
- 你的目标平台包含移动设备、主机或嵌入式系统，对运行时内存占用有严格要求。
- 你希望使用一个经过多年验证、稳定且开源的 TTS 引擎作为后端。

## 蓝图用法

Flite 模块内部没有暴露任何蓝图表面的函数或类。但通过 TextToSpeech 插件，你可以使用以下蓝图表面的入口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `启动文本转语音` | 初始化指定的 TTS 后端（包括 Flite）并准备合成 | `UTextToSpeech` |
| `将文本转为语音` | 向当前 TTS 子系统发送文本，立即产生语音输出 | `UTextToSpeech` |

（具体蓝图节点名称请查看 TextToSpeech 插件文档。）

## C++ 用法

### 头文件引入

```cpp
#include "Flite.h"          // UE 封装的接口（如果存在）
// 或直接使用原始 Flite 头文件
#include "flite.h"
```

### 基本用法

Flite 提供了极简的 C 语言 API，适合直接集成：

```cpp
// 初始化 Flite（仅需调用一次）
flite_init();

// 选择一个语音（例如 CMU 默认英语语音 "cmu_us_awb"）
cst_voice *voice = flite_voice_select("cmu_us_awb");

// 将文本合成为语音并播放（自动使用默认音频设备）
flite_text_to_speech("Hello, this is a text to speech demo.", voice, "play");

// 将文本合成为 WAV 文件
flite_text_to_speech("Save this to a file.", voice, "file:/path/to/output.wav");

// 清理语音对象（插件生命周期结束时由插件管理）
// delete_voice(voice);
```

### 进阶用法

- **使用自定义音频回调**：Flite 允许通过 `cst_audiodev` 结构接管音频输出，从而实现流式播放或混音。
- **多语言支持**：加载不同的语言数据包（如中文、日语），但需额外编译对应语言模型（Flite 官方仅内置英文）。
- **动态调整语速/音高**：通过设置 `voice->features` 中的参数，例如 `feat_set_float(voice->features, "duration_stretch", 1.5f)` 可放慢语速。

## Demo 示例

以下是一个在游戏模块中直接调用 Flite 的最小 C++ 示例（需确保已包含 TextToSpeech 插件）：

**MyTTSComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "flite.h"                  // 需在 Build.cs 中添加 Flite 依赖
#include "MyTTSComponent.generated.h"

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class UMyTTSComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyTTSComponent();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category = "TTS")
    void SpeakText(const FString& Text);

private:
    cst_voice* Voice;
    bool bInitialized = false;
};
```

**MyTTSComponent.cpp**
```cpp
#include "MyTTSComponent.h"

UMyTTSComponent::UMyTTSComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyTTSComponent::BeginPlay()
{
    Super::BeginPlay();
    flite_init();   // 初始化 Flite
    Voice = flite_voice_select("cmu_us_awb");
    bInitialized = (Voice != nullptr);
}

void UMyTTSComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Voice)
    {
        delete_voice(Voice);
        Voice = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

void UMyTTSComponent::SpeakText(const FString& Text)
{
    if (!bInitialized) return;

    // 直接播放
    flite_text_to_speech(TCHAR_TO_UTF8(*Text), Voice, "play");
}
```

**Build.cs** 中添加依赖（示例）：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "TextToSpeech",     // 自动链接 Flite 库
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TextToSpeech` | Flite 模块被 TextToSpeech 主模块依赖，作为语音合成后端之一。直接使用 Flite 时需依赖 TextToSpeech。 |

无其他特殊依赖。

## 维护状态

### 近期更新

- 2025-02-19 `392e7feb` — TTS: Wrapping other maincall correctly for iOS
- 2025-02-19 `623d8d9d` — TTS: Fixing up iOS issues.
- 2025-02-18 `333f3417` — TTS: Add missing copyrights.
- 2025-02-18 `ebb840a9` — TTS: Unifying the IOS and Mac TTS implementation.
- 2024-12-16 `c6a7b0e3` — WinArm64 fixes:

### 维护评价

Flite 模块作为 TextToSpeech 插件的一部分，自 2024 年 12 月创建以来持续活跃维护，最近数次提交集中在 iOS/Mac 平台的适配和 Bug 修复，显示该项目正处于积极开发阶段。Flite 本身是一个极其成熟稳定的开源项目（首次发布于 2001 年），但 UE 插件包装是全新的，可能存在 API 不稳定性或未覆盖的边界情况。目前推荐在官方支持的平台上使用，但建议关注插件版本更新。

## 相关链接

- [Flite 官方项目](http://www.festvox.org/flite/)
- [TextToSpeech 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TextToSpeech)
- [Flite 头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TextToSpeech/Source/ThirdParty/Flite/Flite-e0a3d25/include)