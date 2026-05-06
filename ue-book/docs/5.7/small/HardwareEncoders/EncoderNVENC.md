# HardwareEncoders

> Adds support of hardware encoders to AVEncoder

| 属性 | 值 |
|---|---|
| 中文名 | 硬件编码器支持 |
| 分类 | Encoders |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EncoderAMF` (Runtime), `EncoderNVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HardwareEncoders) | |

## 用途

本插件为 **AVEncoder** 框架提供 NVIDIA NVENC 和 AMD AMF 硬件加速编码器的支持。它封装了 GPU 供应商的专有编码库，使 UE 应用能够利用显卡硬件进行视频编码，从而显著降低 CPU 负载并提高编码性能。主要解决以下问题：

- 游戏直播、云游戏、录屏等场景需要实时高质量的视频编码
- 纯软件编码（如 x264）消耗大量 CPU，影响游戏帧率
- 硬件编码器延迟更低，效率更高

该插件实验性较强，是 AVEncoder 生态的一部分，目前正处于过渡维护阶段（AVEncoder 已被标记为计划移除）。

## 使用场景

- **实时游戏串流**：使用 NVENC 或 AMF 编码视频帧，推流至直播平台
- **本地录像**：以低开销录制高分辨率游戏画面
- **云游戏 / 远程播放**：在服务端利用 GPU 编码，传输至终端设备
- **视频会议 / 协作**：需要低延迟实时编码的应用

## 蓝图用法

本插件模块未暴露任何蓝图可调用函数或可访问属性。所有 API 均为 C++ 原生，需在 C++ 项目中通过 AVEncoder 框架调用。

## C++ 用法

### 头文件引入

```cpp
#include "HardwareEncoders/NVENC_Common.h"
#include "HardwareEncoders/NVENC_EncoderH264.h"
#include "HardwareEncoders/NVENCStats.h"
```

### 基本用法

1. **初始化 NVENC 公共模块**（加载 NVENC DLL 并获取函数指针）

```cpp
// 文件：Engine/Plugins/Media/HardwareEncoders/Source/EncoderNVENC/Private/NVENC_Common.h
AVEncoder::FNVENCCommon& NVENC = AVEncoder::FNVENCCommon::Setup();
if (NVENC.GetIsAvailable())
{
    // NVENC 可用
}
```

2. **创建 NVENC H.264 编码器**（通过 AVEncoder 工厂注册）

```cpp
// 文件：Engine/Plugins/Media/HardwareEncoders/Source/EncoderNVENC/Private/NVENC_EncoderH264.cpp
FVideoEncoderFactory& Factory = FVideoEncoderFactory::Get();
FVideoEncoderNVENC_H264::Register(Factory);
```

3. **检查编码器是否可用**

```cpp
// 文件：Engine/Plugins/Media/HardwareEncoders/Source/EncoderNVENC/Private/NVENC_EncoderH264.h
FVideoEncoderInfo EncoderInfo;
bool bAvailable = FVideoEncoderNVENC_H264::GetIsAvailable(InputFrameFactory, EncoderInfo);
```

4. **输出性能统计**（可打印到屏幕或日志）

```cpp
// 文件：Engine/Plugins/Media/HardwareEncoders/Source/EncoderNVENC/Private/NVENCStats.h
FNVENCStats::Get().SetOutputToScreen(true);      // 显示在 HUD 上
FNVENCStats::Get().SetOutputToLog(true);         // 同时输出到日志
```

### 进阶用法

完整编码流程通常通过 AVEncoder 框架驱动，核心步骤包括：

```cpp
// 创建编码器实例
auto Encoder = Factory.Create<FVideoEncoderNVENC_H264>(EncoderInfo, InitConfig);

// 输入帧处理（从纹理或内存）
TSharedPtr<FVideoEncoderInputFrameImpl> Frame = ...;
FVideoEncoder::FEncodeOptions Options;

// 开始编码
Encoder->Encode(Frame, Options);

// 获取统计信息
FNVENCStats::Get().SetProcessFramesFuncLatency(SomeValue);
```

更多细节可参考 `NVENC_EncoderH264.cpp` 中的 `FNVENCLayer::EncodeBuffer` 和 `ProcessEncodedBuffer` 实现。

## Demo 示例

以下是一个简单的最小示例，展示如何加载 NVENC 并输出统计信息（假设已正确设置 AVEncoder 输入框架）。

**HardwareEncodersDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HardwareEncodersDemo.generated.h"

UCLASS()
class AHardwareEncodersDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

**HardwareEncodersDemo.cpp**

```cpp
#include "HardwareEncodersDemo.h"
#include "HardwareEncoders/NVENC_Common.h"
#include "HardwareEncoders/NVENC_EncoderH264.h"
#include "HardwareEncoders/NVENCStats.h"

void AHardwareEncodersDemo::BeginPlay()
{
    Super::BeginPlay();

    // 初始化 NVENC
    AVEncoder::FNVENCCommon& NVENC = AVEncoder::FNVENCCommon::Setup();
    if (!NVENC.GetIsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("NVENC is not available on this system."));
        return;
    }

    // 注册编码器
    AVEncoder::FVideoEncoderFactory& Factory = AVEncoder::FVideoEncoderFactory::Get();
    AVEncoder::FVideoEncoderNVENC_H264::Register(Factory);

    // 启用统计输出到屏幕
    FNVENCStats::Get().SetOutputToScreen(true);

    UE_LOG(LogTemp, Log, TEXT("NVENC hardware encoder initialized successfully."));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VideoCommon` | 提供视频帧公共数据结构（`FVideoEncoderInputFrameImpl` 等） |
| `VideoEncoder` | 基础编码器接口和工厂（`FVideoEncoder`, `FVideoEncoderFactory`） |
| `AVEncoder` | 上层音视频编码框架（本插件为其提供硬件支持） |
| `NVENC` / `AMF` | 供应商 SDK 动态库加载（通过第三方库间接依赖） |

> **说明**：本插件的两个运行时模块 `EncoderNVENC` 和 `EncoderAMF` 各自依赖对应的供应商 SDK 和系统库（如 Windows 上的 `nvEncodeAPI`、`AMF`）。Build.cs 中通常还会添加 `VideoCommon`、`VideoEncoder` 等模块的引用。详细依赖需参考各模块的 `.Build.cs` 文件。

## 维护状态

### 近期更新

- 2025-10-01 — d7bd17da Don't include windows things if not windows（修复非 Windows 平台编译）
- 2025-03-13 — b059f7b4 Fix trivial unreachable code warnings.（消除可达性警告）
- 2024-10-09 — c4ad1cc7 Fix and silence new PVS 7.33 warnings（修复 PVS 静态分析警告）
- 2024-03-15 — ee20867f QOL: Deprecate AVEncoder (for removal) and its dependencies（标记 AVEncoder 及其依赖项废弃）
- 2024-03-14 — 0b34b68d [Backout] - 回退某次提交

### 维护评价

该插件 **创建于 2024 年**，距今约 1.5 年，属于较新的功能模块。最近的更新（2025-10-01）表明仍在积极维护，但主要是**编译兼容性修复和警告清理**，未涉及功能性增强。插件被标记为 **实验性**（`IsBetaVersion=true`），且其上层框架 AVEncoder 已被官方宣布为**计划移除**（详见 commit `ee20867f`）。因此，**不建议在新项目中直接依赖**，应关注官方的后续替代方案（如 Pixel Streaming、WebMMedia 等）。如果现有项目正在使用 AVEncoder，需要注意未来可能需要对编码器部分进行迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HardwareEncoders)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/audio-video-encoding-in-unreal-engine/)（AVEncoder 通用文档，可能已过时）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HardwareEncoders/Source/EncoderNVENC/Private)（头文件和实现文件即主要测试来源）