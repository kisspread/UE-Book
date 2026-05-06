# Audio Capture Timecode Provider

> Decodes an LTC signal (linear timcode) from a live audio capture device (ie. the computer audio jack).

| 属性 | 值 |
|---|---|
| 中文名 | 音频时码提供器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioCaptureTimecodeProvider` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-21 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AudioCaptureTimecodeProvider) | |

## 用途

该插件提供了一种从**音频捕捉设备**（如计算机音频插孔）实时解码 **LTC（Linear Timecode，线性时间码）** 信号的方式。它继承自 `UGenlockedTimecodeProvider`，将音频流中的时间码同步到引擎的帧同步系统。

**为什么存在？**  
在虚拟制片、多机位同步、广播级音视频工作流中，往往需要从音频通道获取时间码（例如通过麦克风输入或 Line-in 录制的 LTC 信号）。此插件取代了外部硬件解码器，直接在引擎内部提取时间码，简化了同步链路。

## 使用场景

- **虚拟制片/实时预演**：将音频设备（如无线麦克风）输入的 LTC 信号同步到摄像机或引擎时间线。
- **多机位录制**：从主录音设备获取时间码，确保不同拍摄设备的时间线一致。
- **广播播出系统**：与外部调音台或音频矩阵连接，通过音频线路获取标准时间码。
- **后期制作**：在引擎内直接解码音频素材中的 LTC，用于自动对齐素材。

## 蓝图用法

`UAudioCaptureTimecodeProvider` 标记为 `Blueprintable`，可在蓝图中创建或作为时间码提供器赋值给引擎。主要操作通过 **项目设置 → Timecode Provider** 或在游戏模式中动态切换。

### 核心可设置属性

| 属性 | 说明 | 类型 |
|---|---|---|
| `Detect Frame Rate` | 是否自动从音频信号检测帧率 | `bool` |
| `Assume Drop Frame Format` | 检测帧率时，假设为丢帧格式 | `bool` |
| `Frame Rate` | 手动指定帧率（当不检测时使用） | `FFrameRate` |
| `Audio Channel` | 用于捕捉的音频通道索引（从 1 开始） | `int32` |

### 蓝图调用流程

1. **创建提供器**  
   在关卡蓝图中，通过 `Construct Object from Class` 节点生成 `AudioCaptureTimecodeProvider` 对象。

2. **设置参数**  
   将 `Audio Channel` 设为 1（默认），`Detect Frame Rate` 设为 true（或手动指定帧率）。

3. **指定为引擎时间码提供器**  
   通过 `Set Timecode Provider` 节点（位于 `Engine` 命名空间）将刚才创建的提供器赋值给引擎。引擎将自动开始解码音频输入。

4. **获取同步状态**  
   使用 `Get Synchronization State`（继承自父类）检查是否已锁定时间码。

### 示例节点连接

```
[BeginPlay] → [Construct Object from Class] → [Set Timecode Provider] → [Delay] → [Get Synchronization State] → [Branch]
                                                      ↑                                ↓
                                               [Set Audio Channel]          [Print String]
```

## C++ 用法

### 头文件引入

```cpp
#include "AudioCaptureTimecodeProvider.h"
```

### 基本用法

创建并初始化一个 `UAudioCaptureTimecodeProvider`，将其设置为引擎的时间码提供器。

```cpp
// 在 GameInstance 或 GameMode 的初始化中
UAudioCaptureTimecodeProvider* Provider = NewObject<UAudioCaptureTimecodeProvider>();
if (Provider)
{
    Provider->AudioChannel = 1;
    Provider->bDetectFrameRate = true;   // 自动检测帧率
    Provider->bAssumeDropFrameFormat = false;

    if (GEngine)
    {
        GEngine->SetTimecodeProvider(Provider);
        // 初始化（自动调用了 Provider->Initialize(this)）
    }
}
```

**来源**: `Engine/Plugins/Media/AudioCaptureTimecodeProvider/Source/AudioCaptureTimecodeProvider/Public/AudioCaptureTimecodeProvider.h`

### 进阶用法：手动指定帧率

当信号稳定且已知帧率时，关闭自动检测以减少延迟。

```cpp
Provider->bDetectFrameRate = false;
Provider->FrameRate = FFrameRate(30, 1);  // 30fps 逐行
```

### 实时获取帧时间

`FetchTimecode(FQualifiedFrameTime& OutFrameTime)` 由引擎在每帧调用，用户无需主动触发。如需在自定义逻辑中读取当前时间码，可调用：

```cpp
FQualifiedFrameTime FrameTime;
if (Provider->FetchTimecode(FrameTime))
{
    // FrameTime.Time 包含解码的 FTimecode
    uint32 Hours = FrameTime.Time.Hours;
    // ...
}
```

## Demo 示例

以下是一个完整的 C++ 范例，演示如何在自定义 `GameMode` 中动态切换音频时间码提供器。

**AudioCaptureDemoGameMode.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "AudioCaptureTimecodeProvider.h"
#include "AudioCaptureDemoGameMode.generated.h"

UCLASS()
class AAudioCaptureDemoGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    virtual void StartPlay() override;
};
```

**AudioCaptureDemoGameMode.cpp**
```cpp
#include "AudioCaptureDemoGameMode.h"
#include "Engine/Engine.h"

void AAudioCaptureDemoGameMode::StartPlay()
{
    Super::StartPlay();

    // 创建音频时码提供器
    UAudioCaptureTimecodeProvider* Provider = NewObject<UAudioCaptureTimecodeProvider>();
    if (Provider && GEngine)
    {
        Provider->AudioChannel = 1;
        Provider->bDetectFrameRate = true;

        // 替换当前时间码提供器
        GEngine->SetTimecodeProvider(Provider);

        UE_LOG(LogTemp, Log, TEXT("AudioCapture TimecodeProvider initialized."));
    }
}
```

将上述 `GameMode` 设置为默认游戏模式后，运行项目（需连接音频 LTC 源），即可在输出日志中看到时间码同步状态的变化。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioCapture` | 提供底层音频捕捉功能（WASAPI 等） |
| `LinearTimecode` | 解码线性时间码（LTC）信号 |

这两个插件必须启用，且仅在 Win64 平台受支持。

## 维护状态

### 近期更新

- 2024-10-09 `c4ad1cc7` Fix and silence new PVS 7.33 warnings
- 2023-03-22 `a381e0b7` [Audio Capture] WASAPI device support for audio capture. (3 of 3)
- 2023-02-18 `e599d19e` Removing redundant Private includes.
- 2022-10-21 `610c4676` Update vendor links for built-in plugins to use secure protocol.
- 2021-10-21 `625c3242` Merging CL 17890913 from Release 5.0

### 维护评价

- **创建时间**：2021 年 10 月，至今约 4 年。
- **近期更新**：最近一次实质性功能更新在 2023 年 3 月（WASAPI 支持），之后仅有编译警告修复和清理。
- **活跃度**：维护不活跃，超过 1 年没有功能改进。
- **稳定性**：属于实验性插件（`IsBetaVersion=true`），可能仍存在兼容性或性能问题。
- **推荐度**：如需从音频设备解析 LTC，此插件是官方唯一选择。但建议在项目中充分测试，并考虑备用的硬件解码方案以确保可靠性。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AudioCaptureTimecodeProvider)
- [公共头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/AudioCaptureTimecodeProvider/Source/AudioCaptureTimecodeProvider/Public/AudioCaptureTimecodeProvider.h)
- [官方文档（暂无）]()
- [测试用例（未找到）]()