# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 序列图媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（C++ 模块） |
| 模块 | `ExrReaderGpu` (Runtime), `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia) | |

## 用途

**ImgMedia** 插件为 Unreal Engine 提供了一种基于**图像序列**的媒体播放能力。与传统视频文件（如 MP4）不同，图像序列由一系列独立的帧图像（如 OpenEXR、PNG、JPG 等）组成。该插件：

- 允许在 UE 中像播放视频一样播放图像序列（例如 `frame_0001.exr`、`frame_0002.exr` 等）。
- 底层通过 `OpenExrWrapper` 模块高效读取 OpenEXR 格式，支持**多通道（multichannel）**、**tiled（分块）**、**mipmap（多级纹理）** 以及 GPU 加速解码（通过 `ExrReaderGpu` 模块）。
- 支持高动态范围（HDR）、宽色域等电影级画质，广泛应用于虚拟制片、后期预览、广告渲染等需要逐帧精确控制的场景。

## 使用场景

- **虚拟制片实时回放**：渲染的 EXR 序列可以直接作为媒体源在引擎中播放，与虚拟摄像机同步。
- **电影级 HDR 回放**：支持 10/16 位色彩与浮点数据，保留原始曝光与色域。
- **逐帧精确控制**：可跳转到任意帧、按帧率播放、循环等，适合动画或特效预览。
- **替代视频编码**：对于大量透明通道或专业色彩管理的项目，使用图像序列可避免视频编解码压缩损失。

## 蓝图用法

本插件的主要模块 `ImgMedia` 和 `OpenExrWrapper` 均为 C++ 底层，不直接暴露蓝图节点。但上层 **MediaPlayer** 系统提供了通用的媒体播放蓝图节点，可以播放图像序列：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开图像序列媒体源（需指定文件夹路径和命名规则） | `MediaPlayer` |
| `Play` | 开始播放图像序列 | `MediaPlayer` |
| `Set Rate` | 设置播放速率（帧/秒） | `MediaPlayer` |
| `Get Current Frame` | 获取当前帧编号 | `MediaPlayer` |
| `On Media Opened` | 媒体成功打开时的回调事件 | `MediaPlayer` |

> 详细用法请参考 UE 官方文档 [MediaPlayer 蓝图节点](https://docs.unrealengine.com/5.7/en-US/BlueprintAPI/Media/)。

## C++ 用法

`OpenExrWrapper` 模块提供对 OpenEXR 文件的底层读写封装，被上层 `ImgMedia` 模块依赖。以下为基于其头文件 `Public/OpenExrWrapper.h` 的用法。

### 头文件引入

```cpp
#include "OpenExrWrapper.h"
```

### 基本用法

1. **打开一个 EXR 文件并读取像素数据**

```cpp
// 文件路径（假设为绝对路径或相对 Content 路径）
FString ExrPath = TEXT("/Game/Sequence/frame_0001.exr");

// 创建 FRgbaInputFile 对象（支持指定线程数）
FRgbaInputFile InputFile(ExrPath, 4); // 4 线程

// 检查文件是否有效
if (!InputFile.HasInputFile())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open EXR file"));
    return;
}

// 获取数据窗口和显示窗口
FIntPoint DataWin = InputFile.GetDataWindow();
FIntRect DisplayWin = InputFile.GetDisplayWindow();
int32 Width = DisplayWin.Max.X - DisplayWin.Min.X;
int32 Height = DisplayWin.Max.Y - DisplayWin.Min.Y;

// 分配像素缓冲区（RGBA，float 类型）
TArray<FFloat16Color> Buffer;
Buffer.SetNum(Width * Height);

// 设置帧缓冲（R、G、B、A 四通道，Stride 为宽度）
FIntPoint Stride(Width, Width); // x 步长 = 宽度，y 步长 = 当前帧缓冲总行宽
InputFile.SetFrameBuffer(Buffer.GetData(), Stride);

// 读取全部像素
InputFile.ReadPixels(0, Height - 1);

// 现在 Buffer 中包含了 RGBA 的 float16 数据
```

2. **读取 EXR 文件头信息（无需解码像素）**

```cpp
// 使用 FOpenExrHeaderReader 可以更快地获取元数据
FOpenExrHeaderReader Header(TEXT("/Game/Sequence/frame_0001.exr"));
if (!Header.HasInputFile())
{
    // 错误处理
    return;
}

// 获取压缩方式名称
const TCHAR* CompressionName = Header.GetCompressionName();

// 获取帧率（从 EXR header 的 `framesPerSecond` 属性，若无则返回默认值）
FFrameRate FrameRate = Header.GetFrameRate(FFrameRate(24, 1));

// 获取像素尺寸
int32 NumChannels = Header.GetNumChannels();
int32 PixelSize = Header.GetPixelSize();    // 每像素字节数

// 判断是否包含 MipMap
if (Header.ContainsMips())
{
    int32 NumMips = Header.CalculateNumMipLevels(Header.GetDataWindow());
    UE_LOG(LogTemp, Log, TEXT("Mip levels: %d"), NumMips);
}

// 获取 tile 尺寸（若为 tiled 格式）
FIntPoint TileSize;
if (Header.GetTileSize(TileSize))
{
    UE_LOG(LogTemp, Log, TEXT("Tile size: %dx%d"), TileSize.X, TileSize.Y);
}

// 判断是否可 GPU 加速读取
bool bOptimizedForGpu = Header.IsOptimizedForGpu();
```

3. **读取自定义属性**

```cpp
int32 Value;
if (Header.GetIntAttribute(TEXT("worldToCamera"), Value))
{
    // 成功读取自定义 int 属性
}
```

### 进阶用法

- **多线程读取**：`FRgbaInputFile` 支持在构造时指定线程数，利用 OpenEXR 的多线程解码能力。
- **分块读取**：对于大型 tiled EXR，可以只读取感兴趣的区域（通过调整 SetFrameBuffer 的 stride 和 ReadPixels 的 y 范围）。
- **全局线程池**：使用 `FOpenExr::SetGlobalThreadCount(uint16 ThreadCount)` 可设置全局默认线程数，影响所有后续创建的读取对象。

## Demo 示例

以下是一个完整的最小示例，读取一个 EXR 文件的头和像素，输出到日志。

### OpenExrDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FOpenExrDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
};
```

### OpenExrDemo.cpp

```cpp
#include "OpenExrDemo.h"
#include "OpenExrWrapper.h"

void FOpenExrDemoModule::StartupModule()
{
    // 设置全局线程数（可选）
    FOpenExr::SetGlobalThreadCount(4);

    // 文件路径（请替换为真实路径）
    const FString ExrPath = TEXT("C:/MySequence/frame_0001.exr");

    // 1. 读取 header
    FOpenExrHeaderReader Header(ExrPath);
    if (Header.HasInputFile())
    {
        FIntPoint DataWin = Header.GetDataWindow();
        FFrameRate Rate = Header.GetFrameRate(FFrameRate(24, 1));
        int32 Channels = Header.GetNumChannels();
        UE_LOG(LogTemp, Log, TEXT("EXR Info: DataWindow(%d,%d), FrameRate=%d/%d, Channels=%d"),
               DataWin.X, DataWin.Y, Rate.Numerator, Rate.Denominator, Channels);
    }

    // 2. 读取像素
    FRgbaInputFile InputFile(ExrPath);
    if (InputFile.HasInputFile())
    {
        FIntRect DisplayWin = InputFile.GetDisplayWindow();
        int32 Width = DisplayWin.Max.X - DisplayWin.Min.X;
        int32 Height = DisplayWin.Max.Y - DisplayWin.Min.Y;
        TArray<FFloat16Color> Buffer;
        Buffer.AddUninitialized(Width * Height);

        FIntPoint Stride(Width, Width);
        InputFile.SetFrameBuffer(Buffer.GetData(), Stride);
        InputFile.ReadPixels(0, Height - 1);

        UE_LOG(LogTemp, Log, TEXT("Read %dx%d pixels, first pixel R=%f, G=%f, B=%f, A=%f"),
               Width, Height,
               Buffer[0].R, Buffer[0].G, Buffer[0].B, Buffer[0].A);
    }
}

IMPLEMENT_MODULE(FOpenExrDemoModule, OpenExrDemo)
```

编译时需要依赖模块 `OpenExrWrapper`。

## 模块依赖

以下为 `OpenExrWrapper` 模块的独特依赖（省略常见 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `OpenEXR` (第三方库) | 底层 EXR 文件格式解析与解码（由 OpenExrWrapper 封装） |

其他模块（如 `ImgMedia`）依赖于 `OpenExrWrapper` 和 `ExrReaderGpu`。

## 维护状态

### 近期更新

- 2025-10-17 `f81b388d` — [ImgMedia] Fix out of memory crash caused by unprotected large frame gaps.
- 2025-10-10 `ebdf8ce6` — [ImgMedia] Handle global cache frame eviction while scrubbing.
- 2025-09-29 `f131b1dc` — [ImgMedia] Fixing non-safe game tickable created in async load.
- 2025-08-21 `2c158c4d` — Change GetUsedTextures MaterialInterface to use TOptional parameters instead of Enum+bool pairs
- 2025-08-15 `ae8bb436` — ImgMedia: Setting frame duration as per the sequence frame rate instead of the value from the global

### 维护评价

该插件创建于 2025-08-15，距今仅约 3 个月，属于**🆕 新插件**。近期更新频繁且以功能性修复和改进为主（内存崩溃、缓存问题、异步安全等），表明项目处于**活跃维护**状态。推荐在需要图像序列播放的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)（注意：该链接为较早版本论坛帖子，最新文档请参考 [UE5 媒体框架](https://docs.unrealengine.com/5.7/en-US/media-framework/)）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/AutomationTool/Scripts/Tests/ImgMedia)（推测路径，实际可能位于 `Engine/Tests` 下，无公开直接链接）