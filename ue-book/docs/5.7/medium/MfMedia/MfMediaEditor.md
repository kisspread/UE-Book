# Media Foundation Media Player

> Implements a media player using the Microsoft Media Foundation framework. Requires Xbox One or Windows 7 and higher.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体基础播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MfMedia` (RuntimeNoCommandlet), `MfMediaEditor` (Editor), `MfMediaFactory` (Editor), `MfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia) | |

---

## 用途

`MfMediaEditor` 模块是 **Media Foundation Media Player** 插件在编辑器侧的集成层。它主要提供 **UMfFileMediaSourceFactory** 工厂类，用于在编辑器中通过“导入”对话框将本地媒体文件（如 `.mp4`、`.wmv`、`.avi` 等）创建为 `UFileMediaSource` 资产。

该插件本身（`MfMedia`）是 Windows 平台首选的媒体播放后端，利用系统自带的 Media Foundation 框架实现硬件加速解码、多格式支持（取决于系统安装的编解码器）。它解决了在 Windows 7+ 上播放本地或流式媒体文件的需求，提供比旧版 `WmfMedia` 更现代的 API。

## 使用场景

- 在 Windows 游戏或应用中嵌入过场动画、UI 视频背景、射击游戏中的监控画面等。
- 需要播放受 DRM 保护的流媒体（Media Foundation 提供 PlayReady 支持）。
- 希望利用显卡硬件加速解码（如 H.264/H.265）以减少 CPU 负载。
- 在编辑器中将视频素材导入为媒体资产，然后用蓝图或 C++ 控制播放。

## 蓝图用法

`MfMediaEditor` 模块不直接暴露任何蓝图可调用函数或可蓝图类型。所有与媒体播放相关的蓝图节点都位于 `MediaPlayer`、`MediaSource`、`MediaTexture` 等通用媒体系统类中。

要在蓝图中使用，请遵循以下步骤：

1. 在内容浏览器中右键导入媒体文件（例如 `.mp4`）→ 系统会自动调用 `UMfFileMediaSourceFactory` 生成一个 `FileMediaSource` 资产。
2. 创建一个 `MediaPlayer` 资产（蓝图类或直接拖入关卡蓝图）。
3. 将 `FileMediaSource` 赋值给 `MediaPlayer` 的 `Source` 属性（或通过 “Open Source” 节点）。
4. 使用 `MediaTexture` 将 `MediaPlayer` 的视频渲染到材质或控件上。

## C++ 用法

### 头文件引入

```cpp
#include "MfFileMediaSourceFactory.h"
```

（通常你不需要手动包含工厂头文件，因为工厂由编辑器自动调用。）

### 基本用法

在 C++ 中，你可以通过 `UFactory` 机制手动创建 `UFileMediaSource` 资产：

```cpp
// 获取工厂对象
UMfFileMediaSourceFactory* Factory = NewObject<UMfFileMediaSourceFactory>();

// 模拟导入文件（例如从蓝图或自定义编辑器工具中调用）
bool bOperationCanceled = false;
UObject* NewAsset = Factory->FactoryCreateFile(
    UFileMediaSource::StaticClass(),
    InParent,
    FName(TEXT("MyVideo")),
    RF_Standalone | RF_Public,
    TEXT("E:/MyProject/Content/Videos/intro.mp4"),
    nullptr,
    GWarn,
    bOperationCanceled
);
// 此时 NewAsset 即为 UFileMediaSource 对象
```

> 注：`UMfFileMediaSourceFactory` 继承自 `UFactory`，重写了 `FactoryCanImport` 和 `FactoryCreateFile`。在编辑器中通常无需手动调用，上述代码仅在自定义工具/插件中需要编程式导入时使用。

### 进阶用法

结合 `IMediaPlayer` 和 `IMediaSource` 手动创建播放器：

```cpp
#include "IMediaPlayer.h"
#include "IMediaSource.h"
#include "MediaPlayer.h"
#include "FileMediaSource.h"

// 创建一个 MediaPlayer 实例
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->FilePath = TEXT("E:/Movies/intro.mp4");

// 打开媒体
MediaPlayer->OpenSource(MediaSource);
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何通过 `UMfFileMediaSourceFactory` 在编辑器工具模块中导入媒体文件：

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Factories/Factory.h"
#include "MfFileMediaSourceFactory.h"
#include "MyEditorTool.generated.h"

UCLASS()
class UMyEditorTool : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Media")
    static UFileMediaSource* ImportMediaFile(const FString& FilePath);
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"

UFileMediaSource* UMyEditorTool::ImportMediaFile(const FString& FilePath)
{
    // 检查文件是否存在
    if (!FPaths::FileExists(FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("File not found: %s"), *FilePath);
        return nullptr;
    }

    // 创建工厂实例
    UMfFileMediaSourceFactory* Factory = NewObject<UMfFileMediaSourceFactory>();

    // 设置目标包（可在编辑器中选择）
    UPackage* Package = CreatePackage(nullptr, TEXT("/Game/ImportedMedia"));
    Package->FullyLoad();

    FName AssetName = FName(*FPaths::GetBaseFilename(FilePath));

    bool bOperationCanceled = false;
    UFileMediaSource* NewSource = Cast<UFileMediaSource>(
        Factory->FactoryCreateFile(
            UFileMediaSource::StaticClass(),
            Package,
            AssetName,
            RF_Standalone | RF_Public,
            FilePath,
            nullptr,
            GWarn,
            bOperationCanceled
        )
    );

    if (NewSource)
    {
        // 保存资产
        NewSource->MarkPackageDirty();
        UPackage::Save(Package, NewSource, RF_Standalone | RF_Public, *FPackageName::LongPackageNameToFilename(Package->GetName(), FPackageName::GetAssetPackageExtension()));
        return NewSource;
    }

    return nullptr;
}
```

> 注意：实际项目中使用 `FAssetToolsModule` 来创建资产会更好，此示例仅用于演示工厂的直接调用。

## 模块依赖

`MfMediaEditor` 模块的 `Build.cs` 通常依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `MfMedia` | 提供媒体播放核心（播放器、源、轨道等） |
| `MediaAssets` | 定义 `UFileMediaSource`、`UMediaPlayer` 等资产类 |
| `UnrealEd` | 提供编辑器集成（`UFactory` 基类、资产操作等） |

其余均为常见依赖（Core、CoreUObject、Engine、Slate 等），此处省略。

## 维护状态

### 近期更新

```
- 2025-06-20 642aa84f — Fix PVS warnings
- 2025-02-18 0ecd6846 — Media: reworking the timestamp associated sequence index
- 2025-02-06 81c434be — Media: Added a new "MediaBufferingComplete" event
- 2024-12-18 6ed576ac — [FormatStringSan] disallow printing TCHAR*'s via %d (fix all occurrences)
- 2024-05-06 1d0682a5 — Media: Changed CanPlayUrl() to return a value indicating the confidence
```

### 维护评价

- **创建时间**：2024-05-06（约 1 年）
- **更新频率**：近一年内有功能性更新（时间戳改进、新增事件）和代码质量修复
- **活跃度**：活跃维护，最近 6 个月内有实际更新
- **已知问题**：Windows 平台专属，需用户系统安装了相应的 Media Foundation 解码器
- **推荐使用**：✅ 推荐用于 Windows 平台的媒体播放需求，社区支持良好

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia/Source)