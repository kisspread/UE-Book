# AVF Media Player

> Implements a media player using Apple AV Foundation.

| 属性 | 值 |
|---|---|
| 中文名 | AVF 媒体播放器编辑器模块 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (RuntimeNoCommandlet), `AvfMediaCapture` (RuntimeNoCommandlet), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Editor), `AvfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia) | |

## 用途

在 macOS、iOS、tvOS 平台上，使用 Apple 的 AV Foundation 框架实现视频/音频媒体文件的播放、捕捉与编辑支持。该插件是 UE 媒体框架的底层渲染提供者之一，**AvfMediaEditor** 模块负责为编辑器提供媒体文件的导入功能（通过 `UAvfFileMediaSourceFactory`），允许用户直接在内容浏览器中导入 `.mov`、`.mp4` 等 QuickTime 兼容格式。

## 使用场景

- 在 macOS/iOS 上开发需要播放本地视频或流媒体的应用（视频播放、UI 背景动画、叙事过场等）
- 编辑器内快速导入 Apple 平台支持的媒体文件（无需手动转码）
- 需要利用硬件加速解码（AV Foundation 原生支持）的高性能播放需求

## 蓝图用法

本模块是编辑器辅助模块，不提供可供蓝图调用的函数或节点。媒体播放相关的蓝图节点位于其他模块（如 `MediaPlayer`、`FileMediaSource` 等）。用户可通过内容浏览器右键菜单导入 `.mov`、`.mp4` 等文件，自动创建 `UFileMediaSource` 资产。

## C++ 用法

### 头文件引入

```cpp
#include "AvfFileMediaSourceFactory.h"
```

### 基本用法

该类在编辑器启动时自动注册，无需手动调用。当用户在内容浏览器中导入支持的媒体文件时，引擎会调用 `UAvfFileMediaSourceFactory::FactoryCanImport` 验证扩展名，并通过 `FactoryCreateFile` 创建 `UFileMediaSource` 对象。

```cpp
// AvfFileMediaSourceFactory.cpp (简化逻辑)
bool UAvfFileMediaSourceFactory::FactoryCanImport(const FString& Filename)
{
    // 只接受 QuickTime 或 MPEG-4 格式
    return FPaths::GetExtension(Filename).ToLower() == TEXT("mov") ||
           FPaths::GetExtension(Filename).ToLower() == TEXT("mp4");
}

UObject* UAvfFileMediaSourceFactory::FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags,
    const FString& Filename, const TCHAR* Parms, FFeedbackContext* Warn, bool& bOutOperationCanceled)
{
    // 创建 UFileMediaSource 并设置文件路径
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>(InParent, InClass, InName, Flags);
    if (MediaSource)
    {
        MediaSource->SetFilePath(Filename);
    }
    return MediaSource;
}
```

> 来源：`Source/AvfMediaEditor/Private/AvfFileMediaSourceFactory.h` 与 `.cpp`

### 进阶用法

若想以编程方式导入媒体文件（非编辑器流程），可直接创建 `UFileMediaSource`：

```cpp
#include "FileMediaSource.h"

UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->SetFilePath(TEXT("/Game/Movies/Intro.mp4"));
// 然后通过 MediaPlayer->OpenSource(MediaSource) 播放
```

## Demo 示例

以下是一个完整的 C++ 类，演示如何在运行时打开一个本地媒体文件并播放：

**MyMediaPlayer.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MyMediaPlayer.generated.h"

UCLASS()
class MYPROJECT_API AMyMediaPlayer : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayLocalFile(const FString& FilePath);
};
```

**MyMediaPlayer.cpp**

```cpp
#include "MyMediaPlayer.h"
#include "FileMediaSource.h"

void AMyMediaPlayer::PlayLocalFile(const FString& FilePath)
{
    if (!MediaPlayer)
    {
        MediaPlayer = NewObject<UMediaPlayer>(this);
    }

    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->SetFilePath(FilePath);

    MediaPlayer->OpenSource(MediaSource);
    MediaPlayer->Play();
}
```

## 模块依赖

以下依赖取自 `AvfMediaEditor.Build.cs`（已过滤常见模块）：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 媒体资产类型（`UFileMediaSource`） |
| `FactoryFramework` | 提供 `UFactory` 基类和导入接口 |
| `UnrealEd` | 编辑器导入功能支持 |

**其他依赖**：无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 2025-06-26 d2ec2238 将 IOSAsyncTask 泛化为 AppleAsyncTask，为 macOS WebBrowser 使用 WebKit 做准备
- 2025-06-02 2c095ca4 替换 MetalRHI 中的 EBulkDataType 为 Metal 专用 RHI 函数
- 2025-05-06 5243d97b 合并 Dev-ParallelRendering 至 Main
- 2025-04-23 6ae57335 对 UnrealGame 构建目标的文件添加 dllstorage 属性
- 2025-04-10 ea97db60 电影渲染队列：高分辨率平铺支持分页场景视图状态持久化数据
```

以上均为引擎全局改动，非针对 AvfMedia 插件自身的功能更新。最近一次对该插件的实质性修改可能更早。

### 维护评价

- **创建时间**：2025-04-10（基于 Git 历史首次出现该插件相关文件的记录）
- **活跃度**：近期没有针对该插件的功能更新或错误修复，改动均为引擎底层框架适配
- **稳定性**：该插件在 macOS/iOS 平台多年使用，核心功能稳定可靠
- **已知限制**：仅支持 Apple 平台（macOS、iOS、tvOS）；无法在 Windows/Linux 使用；对音频格式支持有限（需依赖系统能力）
- **推荐度**：✅ 推荐使用，尤其是针对 Apple 设备开发的媒体播放需求；若需要跨平台，请使用 `WmfMedia`（Windows）或 `ImgMedia`（通用）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia/Source)（未提供专用测试目录）