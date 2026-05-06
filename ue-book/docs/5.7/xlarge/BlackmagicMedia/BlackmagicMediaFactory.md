# BlackmagicMediaFactory

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | Blackmagic 媒体工厂 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicMediaFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-06-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/BlackmagicMediaFactory) | |

## 用途

BlackmagicMediaFactory 是 Blackmagic Media Player 插件的**工厂模块**，负责在引擎启动时自动注册 Blackmagic 媒体源（`UBlackmagicMediaSource`）和媒体输出（`UBlackmagicMediaOutput`）的创建资源方式。

该模块**不包含任何运行时功能或编辑器界面**，纯粹作为一个轻量级的启动钩子，确保 UE 的内容浏览器和资产创建系统能够识别并生成 Blackmagic 相关的媒体资源。

## 使用场景

- 你想在项目中添加一个 Blackmagic DeckLink 输入设备作为媒体源 → 需要此工厂模块支持资产创建
- 你想将渲染输出发送到 Blackmagic 硬件设备 → 需要此工厂模块注册媒体输出资源
- 你在启用 BlackmagicMedia 插件后，发现无法在内容浏览器中创建 Blackmagic 相关资产 → 请检查此模块是否正确加载

## 蓝图用法

BlackmagicMediaFactory 模块本身**没有公开任何蓝图可调用函数或属性**。它是一个纯 C++ 工厂注册模块，仅在引擎启动时执行一次性的资源工厂注册。

当插件正确加载后，你可以在**内容浏览器**通过以下方式创建 Blackmagic 资源：
1. 右键点击 → **媒体** → **Blackmagic Media Source**
2. 右键点击 → **媒体** → **Blackmagic Media Output**

## C++ 用法

此模块主要供引擎内部和插件框架使用，常规项目代码几乎不需要直接引用它。

### 头文件引入
```cpp
// 通常不需要直接包含此模块的头文件
// 如果需要使用媒体资产类，请引用 BlackmagicMedia 或 BlackmagicMediaOutput 模块
#include "BlackmagicMediaSource.h"
#include "BlackmagicMediaOutput.h"
```

### 基本用法

工厂注册发生在模块启动时，代码位于 `FBlackmagicMediaFactoryModule::StartupModule()` 中：

```cpp
// Source/BlackmagicMediaFactory/Private/BlackmagicMediaFactoryModule.cpp

void FBlackmagicMediaFactoryModule::StartupModule()
{
    // 注册 UBlackmagicMediaSource 的创建方式
    // 使内容浏览器能够识别"Blackmagic Media Source"资产
    auto MediaSourceSupport = FAssetTypeActions_MediaSource::Create();
    FModuleManager::LoadModuleChecked<IMediaAssetsModule>("MediaAssets")
        .RegisterCreateMediaSource(*UBlackmagicMediaSource::StaticClass(),
            []() -> UMediaSource* { return NewObject<UBlackmagicMediaSource>(); });
    
    // 注册 UBlackmagicMediaOutput 的创建方式
    auto MediaOutputSupport = FAssetTypeActions_MediaOutput::Create();
    FModuleManager::LoadModuleChecked<IMediaAssetsModule>("MediaAssets")
        .RegisterCreateMediaOutput(*UBlackmagicMediaOutput::StaticClass(),
            []() -> UMediaOutput* { return NewObject<UBlackmagicMediaOutput>(); });
}
```

## Demo 示例

由于该模块仅注册工厂，不提供运行时功能，这里给出一个**在项目代码中创建 Blackmagic 媒体源的最小 C++ 示例**：

```cpp
// BlackmagicMediaSourceDemo.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "BlackmagicMediaSourceDemo.generated.h"

UCLASS()
class UBlackmagicMediaSourceDemo : public UObject
{
    GENERATED_BODY()

public:
    // 创建一个默认配置的 Blackmagic 媒体源
    UFUNCTION(BlueprintCallable, Category = "Blackmagic|Demo")
    static UBlackmagicMediaSource* CreateDefaultBlackmagicSource();
};
```

```cpp
// BlackmagicMediaSourceDemo.cpp
#include "BlackmagicMediaSourceDemo.h"
#include "BlackmagicMediaSource.h"

UBlackmagicMediaSource* UBlackmagicMediaSourceDemo::CreateDefaultBlackmagicSource()
{
    // NewObject 会使用 UBlackmagicMediaSource 的默认值创建实例
    // 但实际设备绑定需要通过 UBlackmagicMediaSource 的编辑器界面或 C++ API 配置
    UBlackmagicMediaSource* MediaSource = NewObject<UBlackmagicMediaSource>();
    
    // 设置基本属性（可选，更多配置请参考 UBlackmagicMediaSource 头文件）
    MediaSource->DeviceResolution = FIntPoint(1920, 1080);
    MediaSource->bCaptureAudio = true;
    MediaSource->TimecodeFormat = EMediaTimecodeFormat::LTC;
    
    return MediaSource;
}
```

**注意**：实际使用中，`UBlackmagicMediaSource` 需要通过 `UMediaPlayer` 和 `UMediaTexture` 配合播放，或通过媒体框架管线消费数据。上面的示例仅演示资产创建，不包含完整的播放流程。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `BlackmagicMedia` | Blackmagic 媒体资产定义（`UBlackmagicMediaSource`） |
| `BlackmagicMediaOutput` | Blackmagic 媒体输出资产定义（`UBlackmagicMediaOutput`） |
| `MediaAssets` | UE 媒体框架资产系统，用于注册工厂回调 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-09-23 `9d85dc0e` Blackmagic - Fix Blackmagic source assigning default configuration despite having a valid one.
- 2025-08-21 `8143139e` Add missing #include
- 2025-08-20 `2f0476a2` Add missing include
- 2025-07-22 `d0ba5722` Media Profile: Specified category display order for AJA, Blackmagic, and NDI media sources and outputs
- 2025-06-18 `60a45027` Disable BlackmagicMedia plugin on Windows Arm64

### 维护评价

- **创建时间**：2025 年 6 月（约 0 年），属于全新插件
- **更新频率**：创建以来约 3 个月内收到 5 次更新，包括 Bug 修复（设备配置分配）和平台兼容性（Disable Windows Arm64）
- **维护状态**：**活跃维护中**，团队持续修复问题并改进平台支持
- **已知限制**：
  - 不支持 Windows Arm64 平台（已明确禁用）
  - 仅在 Win64 和 Linux 上官方支持
  - 需要 Blackmagic DeckLink 硬件设备和驱动
- **推荐使用**：✅ 推荐，适用于需要使用 Blackmagic 专业视频 I/O 卡的媒体制作项目。插件成熟度处于上升期，但核心功能稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/blackmagic-media-player)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia/Tests)