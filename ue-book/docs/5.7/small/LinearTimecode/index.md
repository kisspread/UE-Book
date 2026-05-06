# Legacy - Linear Timecode Reader

> Component to read a linear timecode from a media source. Does not use synchronization mechanism.

| 属性 | 值 |
|---|---|
| 中文名 | 线性时码读取器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LinearTimecode` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-21 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/LinearTimecode) | |

## 用途

本插件提供一个 **USceneComponent** 组件，用于从 **UMediaPlayer** 播放的音频源中实时解码线性时间码（Linear Timecode, LTC）。LTC 是以特定频率编码在音频信号中的时间信息，常见于专业广播电视和电影制作中。插件通过分析音频采样，提取出 SMPTE 标准的时码（小时、分钟、秒、帧），并转换为 `FDropTimecode` 结构体。

**为什么存在？** 虚幻引擎原生支持媒体播放，但缺少从媒体音频中解析 LTC 的组件。此插件填补了该空白，允许用户将外部时间码信号（如录播、直播信号）与引擎内部时钟或场景同步，适用于虚拟制片、视效同步、多机位剪辑等场景。

**设计限制**：插件**不包含同步机制**——它仅读取和暴露时码，同步逻辑需由使用者自行实现。此外，它假定媒体音频包含有效的 LTC 信号，且未对帧率作自动检测（需要用户理解 LTC 编码约定）。

## 使用场景

- **虚拟制片 / 实时合成**：将外部摄像机或摄影机记录的 LTC 音轨与虚幻引擎渲染画面同步，实现精确的实时合成。
- **后期制作 / 离线同步**：在编辑器中导入含 LTC 的媒体文件，提取时码以便与非线性编辑系统（如 Avid、Premiere）对齐剪辑。
- **多机位同步**：从多个媒体源的音频流中同时解码 LTC，统一各源的时间基准。
- **教学 / 测试**：学习和验证 LTC 编解码算法，或测试媒体播放器的时间线准确性。

## 蓝图用法

在蓝图中，将 `LinearTimecodeComponent` 附加到任意 Actor，并连接一个包含 LTC 音轨的 `MediaPlayer`。该组件会在 Tick 中自动解码音频，并可绑定 `OnTimecodeChange` 事件以响应时码更新。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Drop Frame Number` | 获取当前解码出来的帧序号（基于 `DropTimecode` 中的帧率计算） | `ULinearTimecodeComponent` |
| `Get Drop Time Code Frame Number` | 将 `FDropTimecode` 转换为帧号（根据其帧率和 drop flag） | `ULinearTimecodeComponent` |
| `Set Drop Timecode Frame Number` | 将指定帧号转换为 `FDropTimecode`（原 Timecode 的帧率不变） | `ULinearTimecodeComponent` |

### 绑定时间码变化事件

1. 在关卡蓝图或 Actor 蓝图中，放置 `LinearTimecodeComponent` 节点（通过“添加组件”）。
2. 将其 `MediaPlayer` 引脚连接到有效的 `UMediaPlayer` 对象。
3. 选中组件，在细节面板的“事件”分类中绑定 `On Timecode Change`：
   - 或使用蓝图节点“绑定事件到 OnTimecodeChange”。
4. 在事件触发时访问 `Timecode` 参数（`FDropTimecode` 结构体），可使用 `Get Drop Frame Number` 等节点进一步计算。

### 静态转换节点示例

- **帧号→时间码**：`Set Drop Timecode Frame Number (Timecode, FrameNumber, OutTimecode)`：传入一个模板 `FDropTimecode`（通常来自事件）和想要的帧号，返回完整的时间码。
- **时间码→帧号**：`Get Drop Time Code Frame Number (Timecode, FrameNumber)`：从时间码结构体提取帧号。

## C++ 用法

### 头文件引入

```cpp
#include "LinearTimecodeComponent.h"
#include "DropTimecode.h"
```

### 基本用法

```cpp
// 创建组件（通常在 Actor 的构造函数中）
ULinearTimecodeComponent* TimecodeComponent = CreateDefaultSubobject<ULinearTimecodeComponent>(TEXT("LTCReader"));
TimecodeComponent->MediaPlayer = MyMediaPlayer;

// 绑定事件
TimecodeComponent->OnTimecodeChange.AddDynamic(this, &AMyActor::OnTimecodeChanged);

// 在 Activate 时自动开始解码
TimecodeComponent->Activate();

// 实现回调
void AMyActor::OnTimecodeChanged(const FDropTimecode& Timecode)
{
    UE_LOG(LogTemp, Log, TEXT("New Timecode: %s, Frame: %d"),
        *Timecode.Timecode.ToString(),
        TimecodeComponent->GetDropFrameNumber());
}
```

### 进阶用法

手动更新（替代 Activate/Deactivate）：
```cpp
// 在 Tick 中调用 UpdatePlayer 手动刷新（已自包含 TickComponent，通常无需手动）
// 但若需要精确定时刷新，可禁用 Tick 并定期调用：
TimecodeComponent->Deactivate(); // 关闭自动 Tick
// 在自定义循环里：
TimecodeComponent->UpdatePlayer(); // 强制读取最新音频样本并更新 DropTimecode
```

静态转换函数：
```cpp
FDropTimecode Template;
Template.FrameRate = 30; // 假设为 30fps drop frame
Template.Timecode.bDropFrameFormat = true;

int32 FrameNumber = 100;
FDropTimecode Result;
ULinearTimecodeComponent::SetDropTimecodeFrameNumber(Template, 100, Result);
```

## Demo 示例

以下是一个可放置在关卡中的 Actor 最小示例，展示如何加载媒体文件并提取 LTC。

### MyTimecodeReader.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LinearTimecodeComponent.h"
#include "MyTimecodeReader.generated.h"

UCLASS()
class AMyTimecodeReader : public AActor
{
    GENERATED_BODY()
public:
    AMyTimecodeReader();

    UFUNCTION()
    void OnTimecodeChanged(const FDropTimecode& Timecode);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    ULinearTimecodeComponent* TimecodeComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaPlayer* MediaPlayer;
};
```

### MyTimecodeReader.cpp

```cpp
#include "MyTimecodeReader.h"
#include "MediaPlayer.h"

AMyTimecodeReader::AMyTimecodeReader()
{
    PrimaryActorTick.bCanEverTick = true;

    TimecodeComponent = CreateDefaultSubobject<ULinearTimecodeComponent>(TEXT("LTC Reader"));
    RootComponent = TimecodeComponent;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
}

void AMyTimecodeReader::OnTimecodeChanged(const FDropTimecode& Timecode)
{
    UE_LOG(LogTemp, Log, TEXT("Timecode updated: %02d:%02d:%02d:%02d"),
        Timecode.Timecode.Hours,
        Timecode.Timecode.Minutes,
        Timecode.Timecode.Seconds,
        Timecode.Timecode.Frames);
}

// 在 BeginPlay 中连接并激活
void AMyTimecodeReader::BeginPlay()
{
    Super::BeginPlay();
    if (MediaPlayer && TimecodeComponent)
    {
        TimecodeComponent->MediaPlayer = MediaPlayer;
        TimecodeComponent->OnTimecodeChange.AddDynamic(this, &AMyTimecodeReader::OnTimecodeChanged);
        TimecodeComponent->Activate();
    }
}
```

## 模块依赖

此插件本身不引入额外依赖，但使用方若要播放媒体，通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Media` | 提供 `UMediaPlayer`, `IMediaAudioSample` 等类型 |
| `MediaAssets` | 提供媒体播放器资产相关支持 |

**注意**：若您的 Project Build.cs 中未包含 `Media` 和 `MediaAssets`，只需将它们加入 `PublicDependencyModuleNames` 即可。此插件内部无其他特殊依赖。

## 维护状态

### 近期更新

- 2023-02-18 — 移除多余的 Private includes（代码清理）
- 2023-01-16 — 引擎大版本合并（无实质功能变化）
- 2022-10-21 — 将内置插件供应商链接更新为安全协议（注释/URL 修改）
- 2022-08-18 — 为编辑器插件更新 ObjectPtr 升级（自动代码变更）
- 2021-01-21 — 首次合并入主分支

### 维护评价

- **创建时间**：2021年1月，至今约4年。
- **更新频率**：自2023年2月后无实质性功能更新（最近一年半仅维护性提交）。
- **功能完整度**：当前功能可稳定运行，API 简单清晰，但缺少自动帧率检测、丢帧检测等高级特性。
- **已知问题**：插件在 `Deactivate` 状态下不会主动更新；需依赖媒体播放器的音频采样率与 LTC 编码匹配；未对非常规帧率（如 23.976fps）作特殊处理（依赖用户输入正确的帧率）。
- **推荐使用**：对于需要简单 LTC 读取的场景适用于原型和有限生产的项目。因长期未更新，不建议用于复杂、高可靠性的生产管线。可考虑手动封装或寻找替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/LinearTimecode)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/linear-timecode-plugin-in-unreal-engine/)（UE5.3 版本，内容基本一致）
- [测试用例（未提供）]()