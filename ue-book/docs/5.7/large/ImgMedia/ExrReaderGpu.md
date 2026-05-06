# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（C++ 模块、着色器、编辑器支持） |
| 模块 | `ExrReaderGpu` (Runtime), `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia) | |

## 用途

ExrReaderGpu 是 ImgMedia 插件中负责高性能 GPU 端 EXR 图像序列解码与数据读取的核心模块。它提供了底层 C++ 接口，能够直接读取 EXR 文件的像素数据（支持 scanline 和 tiled 格式），并通过 GPU 缓冲区传递给渲染管线。该模块的存在使得虚幻引擎能够以接近实时的速度播放高分辨率、高动态范围的 EXR 图像序列，广泛用于虚拟制片、过场动画预览、VFX 回放等场景。

## 使用场景

- **虚拟制片环境**：需要实时回放摄像机拍摄的高分辨率 EXR 序列，并叠加其他元素。
- **电影级过场动画**：播放多通道 EXR 素材（如深度、法线、漫反射），用于最终合成或编辑预览。
- **媒体播放器**：基于 ImgMedia 框架构建自定义媒体源，实现高性能的序列帧播放。

## 蓝图用法

此模块不提供任何蓝图可调用节点。所有功能通过 C++ 接口暴露给上层媒体框架（如 `ImgMedia` 模块中的 `FImgMediaPlayer`），蓝图用户应通过标准的 `MediaPlayer` 蓝图节点控制图像序列播放。

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无公开蓝图 API | 此模块专为 GPU 端高性能读取设计，无 UFUNCTION 导出 | `FExrReader` |

## C++ 用法

### 头文件引入

```cpp
#if PLATFORM_WINDOWS
#include "ExrReaderGpu.h"
#endif
```

> **注意**：`FExrReader` 当前仅支持 Windows 平台（`#if PLATFORM_WINDOWS`），且依赖 OpenEXR 库的封装模块 `OpenExrWrapper`。

### 基本用法

从 EXR 文件读取整帧像素数据到 GPU 缓冲区的最简方式（适用于 scanline 格式的 EXR）：

```cpp
// 定义缓冲区大小：宽度 * 高度 * 通道数 * sizeof(uint16)
int32 BufferSize = Width * Height * NumChannels * sizeof(uint16);
uint16* Buffer = new uint16[BufferSize];

bool bSuccess = FExrReader::GenerateTextureData(
    Buffer,
    BufferSize,
    FilePath,
    NumberOfScanlines,   // 通常等于图像高度
    NumChannels
);

if (bSuccess)
{
    // 数据已加载至 Buffer，可上传至 GPU 纹理
    // 注意：数据为平面（planar）排列，需通过 FExrSwizzlePS 着色器重排
}
else
{
    // 读取失败
}

delete[] Buffer;
```

**来源**：`Engine/Plugins/Media/ImgMedia/Source/ExrReaderGpu/Public/ExrReaderGpu.h`

### 进阶用法

对于需要流式读取大量帧或分块读取（tile）的场景，使用 `OpenExrAndPrepareForPixelReading` + `ReadExrImageChunk` 组合可以支持中断/恢复：

```cpp
FExrReader Reader;

// 预先计算每层 tile 数量（用于 tiled 文件）
TArray<int32> NumOffsetsPerLevel;
// ... 填充 NumOffsetsPerLevel 数据

// 打开文件并准备逐块读取
if (Reader.OpenExrAndPrepareForPixelReading(FilePath, NumOffsetsPerLevel))
{
    // 循环读取数据块
    int64 ChunkSize = 4096; // 自定义块大小
    TArray<uint8> ReadBuffer;
    ReadBuffer.SetNum(ChunkSize);
    
    while (Reader.ReadExrImageChunk(ReadBuffer.GetData(), ChunkSize))
    {
        // 处理读取的数据块
        // 注意：ReadBuffer 中可能包含填充字节，需根据实际偏移提取像素
    }
    
    Reader.CloseExrFile();
}
```

**高级用法**：对于 tiled EXR 文件，可使用 `CalculateTileOffsets` 计算每级 mip 的 tile 信息，然后在 `OpenExrAndPrepareForPixelReading` 传入正确的偏移数组。着色器 `FExrSwizzlePS` 可将平面排列的 RGB 数据重排为 RGBA 纹理，支持 `FRgbaSwizzle`、`FRenderTiles`、`FPartialTiles` 三种 permutation 以适配不同数据布局。

## Demo 示例

以下是一个最小 C++ 示例，展示如何使用 `FExrReader` 读取 EXR 帧并获取像素数据（仅 Windows，假设已获取文件路径和尺寸）。

**ExrReaderDemo.h**：
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ExrReaderDemo.generated.h"

UCLASS()
class MYPROJECT_API UExrReaderDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 从指定 EXR 文件读取像素数据到 uint16 数组 */
    UFUNCTION(BlueprintCallable, Category = "EXR")
    bool ReadExrFrame(const FString& FilePath, int32 Width, int32 Height, int32 NumChannels, TArray<uint16>& OutPixels);
};
```

**ExrReaderDemo.cpp**：
```cpp
#include "ExrReaderDemo.h"
#if PLATFORM_WINDOWS
#include "ExrReaderGpu.h"
#endif

bool UExrReaderDemo::ReadExrFrame(const FString& FilePath, int32 Width, int32 Height, int32 NumChannels, TArray<uint16>& OutPixels)
{
#if PLATFORM_WINDOWS
    // 缓冲区大小（每个像素 16bit）
    int32 NumPixels = Width * Height * NumChannels;
    OutPixels.SetNum(NumPixels);

    bool bSuccess = FExrReader::GenerateTextureData(
        OutPixels.GetData(),
        NumPixels * sizeof(uint16),
        FilePath,
        Height,         // NumberOfScanlines
        NumChannels
    );

    return bSuccess;
#else
    // 非 Windows 平台不支持
    return false;
#endif
}
```

> 此示例仅为概念验证，实际使用时应考虑内存管理、帧缓冲池和异步加载。

## 模块依赖

ExrReaderGpu 模块的独特依赖项（不包含 Core/Engine 等标准模块）：

| 模块 | 用途 |
|---|---|
| `OpenExrWrapper` | 封装 OpenEXR 库，提供 EXR 文件头解析、压缩/解压缩、数据类型转换等底层操作 |

其他模块依赖均为标准运行时模块，无需额外声明。

## 维护状态

### 近期更新

- 2025-10-17 f81b388d — [ImgMedia] Fix out of memory crash caused by unprotected large frame gaps.
- 2025-10-10 ebdf8ce6 — [ImgMedia] Handle global cache frame eviction while scrubbing.
- 2025-09-29 f131b1dc — [ImgMedia] Fixing non-safe game tickable created in async load.
- 2025-08-21 2c158c4d — Change GetUsedTextures MaterialInterface to use TOptional parameters instead of Enum+bool pairs.
- 2025-08-15 ae8bb436 — ImgMedia: Setting frame duration as per the sequence frame rate instead of the value from the global.

### 维护评价

- **创建时间**：2025-08-15，属于较新的插件（约 1 年）。
- **更新频率**：近两个月内有多次实质性更新，包括内存修复、缓存问题、异步加载修复，说明插件处于活跃维护阶段。
- **推荐使用**：是。ExrReaderGpu 作为 ImgMedia 的核心组件，专为高性能 GPU EXR 读取设计，适用于需要实时回放 EXR 序列的项目。但需注意仅支持 Windows 平台，且底层依赖 OpenEXR 库，编译时需确保正确链接。

## 相关链接

- [源码（树状目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia)
- [官方文档（论坛旧帖）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia/Tests)（如有）