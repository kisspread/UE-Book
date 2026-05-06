# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产配置、工厂模板） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia) | |

## 用途

将专业广播级的 AJA 视频采集卡集成到 Unreal Engine 中，提供低延迟的视频输入/输出功能。该插件解决了实时视频流接入和输出的痛点，特别适用于虚拟演播室、广电级图文包装、现场直播、远程制作等需要极高可靠性和同步精度的场景。

核心能力包括：
- 从 AJA 采集卡获取实时视频信号，作为媒体源（MediaSource）供 UE 内部播放
- 通过 AJA 输出卡将 UE 渲染画面实时输出到外部设备（监视器、切换台等）
- 支持 Genlock（帧同步）和 Timecode（时间码），确保多设备同步
- 提供低延迟模式，减少端到端延迟

## 使用场景

- 虚拟演播室：将摄像机（通过 AJA 卡）实时画面输入 UE，叠加虚拟场景后输出到导播台
- 实时渲染输出：将 UE 的渲染结果通过 AJA 卡输出到 LED 大屏、投影机或广播信号
- 多机位同步录制：利用时间码同步多个输入源，实现后期同步剪辑
- 广电级监看：在节目中实时显示 UE 场景的 PGM 信号

## 蓝图用法

本插件的核心蓝图交互通过 **媒体资产（AjaMediaSource / AjaMediaOutput）** 和标准 `MediaPlayer` 节点完成。目前没有直接暴露的 BlueprintCallable 函数（所有配置均在编辑器中通过属性面板或工厂创建时设定）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 创建 `AjaMediaSource` 对象 | 通过右键菜单“媒体/播放器/AJA 媒体源”创建资产，或使用内容浏览器新建 | `UAjaMediaSourceFactoryNew` |
| 创建 `AjaMediaOutput` 对象 | 通过右键菜单“媒体/输出/AJA 媒体输出”创建资产 | `UAjaMediaOutputFactoryNew` |
| 使用标准媒体播放器 | 将 `AjaMediaSource` 赋值给 `MediaPlayer` 的 `Source` 属性，调用 `Open Source` 播放 | `UMediaPlayer` |

> **说明**：`AjaMediaSource` 和 `AjaMediaOutput` 均为 `UFactory` 创建，设置细节（设备、端口、帧格式、色彩空间等）在编辑器的属性自定义器（`FAjaMediaTimecodeReferenceCustomization`）中完成。蓝图无法直接更改这些配置。

## C++ 用法

### 头文件引入

```cpp
#include "AjaMediaSource.h"         // 媒体源
#include "AjaMediaOutput.h"         // 媒体输出
#include "AjaMediaSourceFactoryNew.h" // 工厂
#include "AjaMediaOutputFactoryNew.h"
```

### 基本用法：创建并打开 AJA 媒体源

```cpp
// 在 GameInstance 或 Actor 中动态创建 MediaPlayer 并加载 AJA 媒体源
#include "MediaPlayer.h"
#include "AjaMediaSource.h"

void UMyClass::PlayAJASource()
{
    // 加载一个已存在的 AJA 媒体源资产（替换为你的资产路径）
    UAjaMediaSource* Source = LoadObject<UAjaMediaSource>(nullptr, TEXT("/Game/MyAJASource.MyAJASource"));
    if (Source)
    {
        // 创建 MediaPlayer 组件（或使用已有的）
        UMediaPlayer* Player = NewObject<UMediaPlayer>(this, UMediaPlayer::StaticClass());
        Player->OpenSource(Source);
    }
}
```

### 进阶用法：使用工厂创建输出对象

```cpp
// 在编辑器模式下通过 Factory 创建 UAjaMediaOutput 对象
#include "AjaMediaOutputFactoryNew.h"
#include "AjaMediaOutput.h"

void UMyEditorUtility::CreateAJAMediaOutput()
{
    UAjaMediaOutputFactoryNew* Factory = NewObject<UAjaMediaOutputFactoryNew>();
    // FactoryCreateNew 会弹出文件保存对话框并创建资产
    UAjaMediaOutput* Output = Cast<UAjaMediaOutput>(
        Factory->FactoryCreateNew(
            UAjaMediaOutput::StaticClass(),
            /*InParent*/ GetTransientPackage(),
            FName("CustomAJARenderTarget"),
            RF_Transactional | RF_Public,
            /*Context*/ nullptr,
            /*Warn*/ nullptr
        )
    );
    if (Output)
    {
        UE_LOG(LogTemp, Log, TEXT("Created AJA Media Output!"));
    }
}
```

### 自定义时间码参考

```cpp
// 使用 FAjaMediaTimecodeReference 配置时间码参考（通常在 Slate UI 中调用）
#include "AjaMediaTimecodeReferenceCustomization.h"
// 详情见 Customizations 中的 FAjaMediaTimecodeReferenceCustomization
```

> 来源文件：`Engine/Plugins/Media/AjaMedia/Source/AjaMediaEditor/Private/Customizations/AjaMediaTimecodeReferenceCustomization.h`

## Demo 示例

以下是一个完整的 `UObject` 类，演示如何在运行时创建 `UAjaMediaOutput` 并开始输出（简化版，仅展示骨架）：

**Header (MyAJAOutputDemo.h)**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "MyAJAOutputDemo.generated.h"

UCLASS()
class UMyAJAOutputDemo : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "AJA Demo")
    void StartAJAOutput(const FString& OutputAssetPath);
};
```

**Source (MyAJAOutputDemo.cpp)**
```cpp
#include "MyAJAOutputDemo.h"
#include "AjaMediaOutput.h"
#include "MediaOutput.h"
#include "MediaCapture.h"

void UMyAJAOutputDemo::StartAJAOutput(const FString& OutputAssetPath)
{
    // 从路径加载已配置好的 UAjaMediaOutput 资产
    UAjaMediaOutput* Output = LoadObject<UAjaMediaOutput>(nullptr, *OutputAssetPath);
    if (Output)
    {
        // 创建一个 MediaCapture 实例并开始捕获（需要 UMediaCapture 支持）
        UMediaCapture* Capture = Output->CreateMediaCapture();
        if (Capture)
        {
            // 假设你有一个 UMediaPlayer 或 UTextureRenderTarget2D 作为源
            // Capture->SetMediaOutput(Output);
            // Capture->StartCapture(/*Source*/);
        }
    }
}
```

## 模块依赖

该插件由五个模块组成，各模块的依赖项（省略标准 Core/Engine/Slate 等）如下：

| 模块 | 依赖 | 用途 |
|---|---|---|
| `AjaCore` | `AJASDK`（第三方库） | AJA 硬件底层通信与 SDK 封装 |
| `AjaMedia` | `MediaIOCore`, `MediaAssets`, `AjaCore` | 媒体源与输出资产的核心实现 |
| `AjaMediaEditor` | `MediaIOCoreEditor`, `AjaCore`, `AjaMedia` | 编辑器细节定制（时间码引用、属性面板） |
| `AjaMediaFactory` | `AjaMedia`, `UnrealEd` | 内容浏览器中的工厂菜单 |
| `AjaMediaOutput` | `MediaIOCore`, `MediaAssets`, `AjaCore` | 媒体输出资产实现 |

> 如需在自己的模块中使用 AJA 功能，最少需要依赖 `AjaMedia` 和 `AjaCore`。

## 维护状态

### 近期更新

```
- 2025-10-17 ab15e76 — Media IO - Fix crash when refreshing media properties for Aja source
- 2025-09-24 5ef7a9a — Aja - Add a new output mode that can reduce latency by up to 1 frame.
- 2025-09-24 94f6a82 — Aja - Add option to continue input, output and genlock when card timeouts
- 2025-08-20 5f63edc — Update Aja SDK to 17.5.0
- 2025-08-18 5b28eda — Aja - Add an option to discard interlace frames if they land on an odd frame.
```

### 维护评价

该插件目前处于 **活跃维护** 状态。最近的提交包括：
- 紧急崩溃修复（2025-10-17）
- 重要的性能优化（低延迟模式、超时选项）
- SDK 版本更新（跟随 AJA 官方发布）
- 针对隔行帧的改进

由于发布时间仅约 2 个月，且更新频率高，推荐在生产项目中使用。需注意：
- 仅支持 Win64 平台
- 需要安装 AJA 硬件并配置正确的 SDK
- 首次使用前需在引擎插件中手动启用（默认禁用）

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia)
- [AjaCore 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia/Source/Aja)
- [AjaMediaEditor 定制化源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia/Source/AjaMediaEditor)
- [工厂模板（创建资产）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia/Source/AjaMediaFactory)