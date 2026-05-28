# AMFCodecs

> Adds codecs from the AMD Advanced Media Framework SDK to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | AMD编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AMFCodecs` (Runtime), `AMFCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs) | |

## 用途

本插件是 Unreal Engine 5 中 `AVCodecs` 插件的扩展后端之一。它的核心作用是将 AMD 的 Advanced Media Framework (AMF) SDK 集成到 UE5 的统一音视频编解码框架 (`AVCodecs`) 中，为使用 AMD 显卡（GPU）的用户和开发者提供**硬件加速**的视频编码（如 H.264/AVC, H.265/HEVC）和解码能力。它解决了 `AVCodecs` 框架最初缺少 AMF 支持的问题，使得依赖 AMD 硬件进行高效视频处理的应用（如游戏录制、视频编辑、视频通话）能够充分利用 GPU 资源，降低 CPU 开销。

## 使用场景

- 你正在开发一款 PC 游戏或应用，目标用户主要使用 AMD Radeon 显卡，你需要进行游戏画面实时录制或推流。
- 你的应用需要进行高质量的视频编辑或转码，并希望利用 AMD GPU 的专用媒体引擎来加速处理过程。
- 你在开发涉及视频通话或视频会议的多人在线功能，并希望在 AMD 硬件上获得更低的延迟和 CPU 占用率。

## 蓝图用法

本插件作为 `AVCodecs` 框架的编解码器后端，**不直接暴露独立的蓝图节点**。其功能通过 `AVCodecs` 插件统一对外的蓝图 API 进行访问。开发者在蓝图中调用 `AVCodecs` 的编码器/解码器节点时，如果系统检测到兼容的 AMD GPU 并且 AMFCodecs 插件已启用，则会自动使用 AMD AMF 硬件加速后端。

### 核心节点 (通过 AVCodecs 框架)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Video Encoder` | 创建视频编码器实例，AMF 后端会根据硬件自动选择 | `UAVCodecSubsystem` |
| `Create Video Decoder` | 创建视频解码器实例，AMF 后端会根据硬件自动选择 | `UAVCodecSubsystem` |

### 使用示例（蓝图描述）

1.  **确保插件启用**：在项目设置的 “Plugins” 中搜索并启用 “AVCodecs” 和 “AMFCodecs”。
2.  **创建编码器**：使用 `Create Video Encoder` 节点，在 “Codec” 选项中可能会出现如 “AMF H264 Encoder” 或 “AMF HEVC Encoder” 等选项。
3.  **进行编码**：连接后续的编码、提交帧、获取数据包等节点完成视频编码流程。

## C++ 用法

### 头文件引入

```cpp
#include "AMFCodecsModule.h" // 主模块头文件
```

### 基本用法

本插件的核心在于作为 `AVCodecs` 框架的模块化后端。典型的用法是**确保模块正确加载和初始化**，以便 `AVCodecs` 子系统能够发现并使用它。

```cpp
// 检查 AMFCodecs 模块是否已加载并可用
// 来源：Engine/Plugins/Experimental/AVCodecs/AMFCodecs/Source/AMFCodecs/Private/AMFCodecsModule.cpp
if (FModuleManager::Get().IsModuleLoaded(TEXT("AMFCodecs")))
{
    // 模块已加载，此时 AVCodecs 子系统应能通过工厂方法发现 AMF 编解码器。
    UE_LOG(LogTemp, Log, TEXT("AMFCodecs module is loaded and ready."));
}
else
{
    // 尝试加载模块（通常不需要手动调用，插件系统会处理）
    FModuleManager::Get().LoadModule(TEXT("AMFCodecs"));
}
```

### 进阶用法

在编写直接操作 `AVCodec` 对象的代码时，可以通过查询编解码器特性来确认是否正在使用 AMF 硬件后端。

```cpp
#include "Video/VideoEncoder.h"
#include "AVUtility.h"

void UseEncoder()
{
    TSharedPtr<FVideoEncoder> Encoder = FVideoEncoder::Create({ECodecType::H264});
    if (Encoder.IsValid())
    {
        // 查询编码器名称或供应商信息，以确认是否为 AMF
        FString EncoderName;
        Encoder->GetOption(AVOption::EncoderName, EncoderName);
        
        if (EncoderName.Contains(TEXT("AMF")))
        {
            UE_LOG(LogTemp, Log, TEXT("Using AMD AMF hardware encoder: %s"), *EncoderName);
        }
        
        // ... 使用编码器进行编码
    }
}
```

## Demo 示例

以下是一个展示如何查询 AMF 编解码器可用性的最小 C++ 示例。

**MyVideoCodecManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyVideoCodecManager
{
public:
    static void CheckAMFAvailability();
};
```

**MyVideoCodecManager.cpp**
```cpp
#include "MyVideoCodecManager.h"
#include "AMFCodecsModule.h"
#include "Video/VideoEncoder.h"
#include "AVUtility.h"

void FMyVideoCodecManager::CheckAMFAvailability()
{
    // 1. 检查模块
    const bool bAMFModuleLoaded = FModuleManager::Get().IsModuleLoaded(TEXT("AMFCodecs"));
    UE_LOG(LogTemp, Log, TEXT("AMFCodecs Module Loaded: %s"), bAMFModuleLoaded ? TEXT("YES") : TEXT("NO"));

    // 2. 尝试创建一个 H264 编码器，看它是否为 AMF 后端
    TSharedPtr<FVideoEncoder> H264Encoder = FVideoEncoder::Create({ECodecType::H264});
    if (H264Encoder)
    {
        FString EncoderIdentifier;
        H264Encoder->GetOption(AVOption::EncoderName, EncoderIdentifier);
        
        if (bAMFModuleLoaded && EncoderIdentifier.Contains(TEXT("AMF")))
        {
            UE_LOG(LogTemp, Log, TEXT("✅ AMF hardware encoder is active: %s"), *EncoderIdentifier);
        }
        else if (bAMFModuleLoaded)
        {
            UE_LOG(LogTemp, Warning, TEXT("⚠️ AMF module loaded, but active encoder is not AMF: %s"), *EncoderIdentifier);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("❌ Using software encoder: %s"), *EncoderIdentifier);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("❌ Failed to create any H264 encoder."));
    }
}
```

## 模块依赖

从 `Build.cs` 分析，本插件依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Vulkan` | 提供与 Vulkan RHI 的交互能力，AMF 在 UE 中通常通过 Vulkan 扩展与 GPU 通信 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中使用导致输出乱码的问题 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 在修复了错误的查找替换后，进行了第二次提交（具体修复内容） |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表 51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist... | 将引擎初始化后的委托获取方式从直接访问改为调用Get函数，以修复注册缺失的问题（因消息截断，推测完整内容） |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新了过时的构建版本设置 |

### 维护评价

AMFCodecs 插件自 2023 年初创建以来，持续有维护性更新，最近一次实质性修复在 2026 年 4 月，表明它仍处于**活跃维护**状态。作为 `AVCodecs` 生态的一部分，它随着引擎核心 AV 框架的演进而同步更新。

需要注意的是，这是一个**实验性插件**（`IsExperimentalVersion: true`），并且**默认未启用**（`EnabledByDefault: false`）。这意味着它的 API 可能在未来版本中发生不兼容的变化，且可能存在未发现的稳定性问题。它主要面向希望使用最新 AMD 硬件加速功能并愿意承担一定风险的开发者。

**结论**：**推荐在需要 AMD AMF 硬件加速支持的项目中使用，但务必注意其实验性状态。** 建议与主分支保持同步更新，以获取最新的 bug 修复和功能改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs)
- [官方文档](https://docs.unrealengine.com) (需搜索 `AVCodecs` 或 `AMD AMF` 相关内容)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs/Tests) (如果存在)