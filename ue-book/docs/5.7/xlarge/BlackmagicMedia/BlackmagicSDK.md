# BlackmagicSDK (External)

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | 黑魔法 SDK 封装 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-06-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/ThirdParty/BlackmagicLib) | |

## 用途

BlackmagicSDK 是一个外部第三方库模块，封装了 Blackmagic Design 官方 DeckLink SDK（版本 12.2）的头文件与平台库。它为 `BlackmagicMedia` 插件中其他模块（如 `BlackmagicCore`、`BlackmagicMediaOutput`）提供对 DeckLink 系列视频采集/输出卡的原生 API 访问。该模块本身不包含任何可执行的 UE 逻辑，仅作为 C/C++ 头文件集合与链接库，使得 UE 项目能够编译并调用 DeckLink 硬件的底层功能。

## 使用场景

- 你的项目需要使用 Blackmagic Design 的 DeckLink、UltraStudio 等采集/输出设备进行专业视频 I/O。
- 你在开发广播级、演播室或后期制作工具，需要实时 SDI/HDMI 视频输入输出、键混、色彩转换等功能。
- 你想基于 DeckLink SDK 编写自定义媒体捕获/播放模块，并希望统一管理 SDK 的引用与平台适配。

## 蓝图用法

该模块不暴露任何 BlueprintCallable 函数或 BlueprintType。所有接口均为原生 COM 风格的 C++ 接口，仅能通过 C++ 侧使用。

## C++ 用法

### 头文件引入

```cpp
#include "BlackmagicLib.h"          // 建议的统一包含头（由 BlackmagicCore 提供）
// 或直接使用 SDK 头文件：
#include "DeckLinkAPI.h"
```

### 基本用法

获取 DeckLink 设备迭代器并枚举设备：

```cpp
// 创建 DeckLink 迭代器
IDeckLinkIterator* DeckLinkIterator = CreateDeckLinkIteratorInstance();
if (DeckLinkIterator)
{
    IDeckLink* DeckLink = nullptr;
    while (DeckLinkIterator->Next(&DeckLink) == S_OK)
    {
        const char* ModelName = nullptr;
        if (DeckLink->GetModelName(&ModelName) == S_OK)
        {
            UE_LOG(LogTemp, Log, TEXT("Found DeckLink device: %s"), ANSI_TO_TCHAR(ModelName));
        }
        DeckLink->Release();
    }
    DeckLinkIterator->Release();
}
```

文件位置：`Engine/Plugins/Media/BlackmagicMedia/Source/ThirdParty/BlackmagicLib`

### 进阶用法

获取输入接口并设置回调（需实现 `IDeckLinkInputCallback_v11_5_1`）：

```cpp
class FMyDeckLinkCallback : public IDeckLinkInputCallback_v11_5_1
{
public:
    HRESULT STDMETHODCALLTYPE VideoInputFrameArrived(
        IDeckLinkVideoInputFrame* videoFrame,
        IDeckLinkAudioInputPacket* audioPacket) override
    {
        // 处理帧数据
        if (videoFrame)
        {
            void* FrameBytes = nullptr;
            videoFrame->GetBytes(&FrameBytes);
            // ... 复制或处理视频数据
        }
        return S_OK;
    }
    // 其他回调函数需要实现...
};

void StartCapture(IDeckLink* Device)
{
    IDeckLinkInput* Input = nullptr;
    if (Device->QueryInterface(IID_IDeckLinkInput, (void**)&Input) == S_OK)
    {
        Input->EnableVideoInput(bmdModeHD1080p24, bmdFormat8BitYUV, bmdVideoInputFlagDefault);
        Input->EnableAudioInput(bmdAudioSampleRate48kHz, bmdAudioSampleType16bitInteger, 2);
        Input->SetCallback(new FMyDeckLinkCallback());
        Input->StartStreams();
    }
}
```

## Demo 示例

以下是一个最小示例展示如何在模块中使用 BlackmagicSDK。

**BlackmagicSDKDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FBlackmagicSDKDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**BlackmagicSDKDemo.cpp**
```cpp
#include "BlackmagicSDKDemo.h"
#include "DeckLinkAPI.h"

void FBlackmagicSDKDemoModule::StartupModule()
{
    // 尝试创建 DeckLink 迭代器验证 SDK 可用
    IDeckLinkIterator* Iterator = CreateDeckLinkIteratorInstance();
    if (Iterator)
    {
        UE_LOG(LogTemp, Log, TEXT("Blackmagic DeckLink SDK loaded successfully."));
        Iterator->Release();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to create DeckLink iterator. SDK may not be installed."));
    }
}

void FBlackmagicSDKDemoModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FBlackmagicSDKDemoModule, BlackmagicSDKDemo)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | BlackmagicSDK 为第三方外部库，不依赖任何 UE 模块，仅需编译工具链。 |

## 维护状态

### 近期更新

- 2025-09-23 9d85dc0e Blackmagic - Fix Blackmagic source assigning default configuration despite having a valid one.
- 2025-08-21 8143139e Add missing #include
- 2025-08-20 2f0476a2 Add missing include
- 2025-07-22 d0ba5722 Media Profile: Specified category display order for AJA, Blackmagic, and NDI media sources and outputs
- 2025-06-18 60a45027 Disable BlackmagicMedia plugin on Windows Arm64

### 维护评价

BlackmagicSDK 模块随 BlackmagicMedia 插件一起维护，最近 2 个月内仍有修复性提交，表明其处于活跃维护状态。但该模块本质上是第三方 SDK 的包装，其稳定性依赖于 Blackmagic Design 发布的官方 SDK。当前版本基于 DeckLink SDK 12.2，涵盖从 v7.1 到 v11.5.1 的多个历史接口版本，兼容性良好。推荐需要与 Blackmagic 硬件交互的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/ThirdParty/BlackmagicLib)
- [Blackmagic DeckLink SDK 官方文档](https://www.blackmagicdesign.com/support/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/BlackmagicCore)