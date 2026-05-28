# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ExrReaderGpu` (Runtime), `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia) | |

## 用途

这个插件的核心功能是提供一个媒体播放器，专门用于播放由一系列静态图片文件（图像序列）组成的“视频”。它解决了在Unreal Engine中无缝播放从外部渲染农场或合成软件（如Nuke、Blender、After Effects）导出的图像序列帧的问题。其关键特性包括：
-   **支持多种格式**：原生支持EXR（OpenEXR）格式，并扩展支持BMP、JPG、PNG等常见图像格式。
-   **GPU加速解码**：通过`ExrReaderGpu`模块利用GPU（Compute Shader）对EXR文件进行高效解码和色域转换，显著提升高分辨率序列的播放性能。
-   **流式加载与缓存**：采用异步加载和LRU（最近最少使用）缓存机制，可以在播放过程中按需加载和丢弃图像帧，有效管理内存。
-   **无缝集成**：作为Media Framework的一部分，与`UMediaPlayer`、`UMediaTexture`等标准媒体组件无缝集成，支持蓝图和Sequencer控制播放。

## 使用场景

-   **电影级视觉特效（VFX）与虚拟制作**：在实时渲染场景中播放由电影级渲染器（如V-Ray, Arnold）输出的高动态范围（HDR）、高分辨率EXR图像序列，用于背景投影、虚拟场景或灯光参考。
-   **游戏开发中的预渲染内容**：播放为游戏内过场动画或UI界面预先渲染好的图像序列（如BMP、PNG序列），作为“视频”播放。
-   **建筑可视化与产品展示**：播放从3D软件导出的高质量渲染动画序列。
-   **数据可视化**：播放科学计算或数据模拟生成的图像序列。

## 蓝图用法

在蓝图中，主要通过`UMediaPlayer`资产和`UMediaTexture`资产来控制图像序列的播放。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源。对于图像序列，源应为`UImgMediaSource`或指向序列文件夹的路径。 | `UMediaPlayer` |
| `Play` | 开始播放已打开的媒体源。 | `UMediaPlayer` |
| `Pause` | 暂停播放。 | `UMediaPlayer` |
| `Close` | 关闭当前媒体源。 | `UMediaPlayer` |
| `Set Looping` | 设置是否循环播放。 | `UMediaPlayer` |
| `Set Rate` | 设置播放速率（支持负数进行倒放）。 | `UMediaPlayer` |
| `Create Media Texture` | 创建一个`UMediaTexture`资产，用于将播放器输出的视频帧渲染为纹理。 | `UImgMediaFactory` (通过蓝图函数库) |

### 使用示例（蓝图描述）

1.  在内容浏览器中创建一个`MediaPlayer`资产。
2.  创建一个`ImgMediaSource`资产，在其属性中指定图像序列所在的文件夹路径（例如`/Game/Movies/RenderSequence/`）。
3.  创建一个`MediaTexture`资产，并在“Media Player”属性中选择步骤1创建的播放器。
4.  在关卡蓝图或Actor蓝图中：
    -   添加一个`Media Player`变量并设置为步骤1的资产。
    -   添加一个`Media Texture`变量并设置为步骤3的资产。
    -   添加一个`Image` UI控件或`Material Instance Dynamic`。
5.  使用`Open Source`节点，将`ImgMediaSource`资产连接到`Media Player`。
6.  调用`Play`节点开始播放。
7.  将`Media Texture`变量设置给UI的`Image`控件或材质的纹理参数，即可显示播放内容。

## C++ 用法

插件的C++ API主要通过底层的`FExrReader`类提供对EXR文件的精细控制，而更通用的图像序列播放则通过`UMediaPlayer`接口实现。

### 头文件引入

```cpp
#include "ExrReaderGpu.h"
#include "MediaPlayer.h"
#include "ImgMediaSource.h"
```

### 基本用法

使用`UMediaPlayer`播放图像序列。此示例展示了标准的媒体播放器用法。

```cpp
// 在某个Actor的BeginPlay中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 假设MediaPlayerComponent已在编辑器中创建并指向一个ImgMediaSource
    if (MediaPlayerComponent && MediaPlayerComponent->GetMediaPlayer())
    {
        UMediaPlayer* MediaPlayer = MediaPlayerComponent->GetMediaPlayer();
        
        // 打开媒体源（通过蓝图或代码设置）
        if (MediaPlayer->OpenSource(MediaSourceAsset)) // MediaSourceAsset 是 UImgMediaSource*
        {
            // 开始播放
            MediaPlayer->Play();
            // 设置循环
            MediaPlayer->SetLooping(true);
        }
    }
}
```

### 进阶用法

直接使用`FExrReader`类进行EXR文件的低层级读取，适用于自定义处理流程。

```cpp
#include "ExrReaderGpu.h"

void ReadExrFileDirectly(const FString& ExrFilePath)
{
    FExrReader ExrReader;
    
    // 1. 打开文件并准备读取（读取文件头，定位扫描线/图块偏移）
    if (ExrReader.OpenExrAndPrepareForPixelReading(ExrFilePath, {0})) // 简化：假设单级mip
    {
        // 2. 准备接收像素数据的缓冲区
        int32 TextureWidth = 1920;
        int32 TextureHeight = 1080;
        int32 NumChannels = 4; // RGBA
        TArray<uint16> PixelBuffer;
        PixelBuffer.SetNum(TextureWidth * TextureHeight * NumChannels);

        // 3. 分块读取像素数据（示例：读取整个图像为一个块）
        int64 ChunkSize = TextureWidth * TextureHeight * NumChannels * sizeof(uint16);
        if (ExrReader.ReadExrImageChunk(PixelBuffer.GetData(), ChunkSize))
        {
            // 4. 在此处处理像素数据 (PixelBuffer)
            // 注意：对于EXR，数据可能是RGB或RGBA，需要根据实际情况处理通道。
            UE_LOG(LogTemp, Log, TEXT("Successfully read EXR pixel data into buffer."));
        }

        // 5. 关闭文件句柄
        ExrReader.CloseExrFile();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open EXR file: %s"), *ExrFilePath);
    }
}
```
*来源：基于 `ExrReaderGpu.h` 中 `FExrReader` 类的公共接口推断编写。*

## Demo 示例

一个使用`FExrReader`读取EXR文件头并获取其基本信息的C++示例。

```cpp
// ExrReaderDemo.h
#pragma once

#include "CoreMinimal.h"
#include "ExrReaderGpu.h"

class FExrReaderDemo
{
public:
    static void PrintExrFileInfo(const FString& ExrFilePath);
};
```

```cpp
// ExrReaderDemo.cpp
#include "ExrReaderDemo.h"

void FExrReaderDemo::PrintExrFileInfo(const FString& ExrFilePath)
{
    FExrReader ExrReader;
    
    // 注意：OpenExrAndPrepareForPixelReading 主要用于准备像素读取。
    // 这里我们仅演示如何利用其初始化过程来获取信息。
    // 实际应用中，获取文件尺寸等信息可能需要解析文件头，但公共API未完全暴露。
    // 此示例主要展示API的调用流程。
    
    UE_LOG(LogTemp, Log, TEXT("Attempting to open EXR file: %s"), *ExrFilePath);
    
    // 为了演示，我们假设一个单级mip结构
    TArray<int32> NumOffsetsPerLevel = {0}; // 实际值由文件决定
    if (ExrReader.OpenExrAndPrepareForPixelReading(ExrFilePath, NumOffsetsPerLevel))
    {
        UE_LOG(LogTemp, Log, TEXT("EXR file opened successfully and is ready for reading."));
        // 在实际的ReadExrImageChunk调用之前，我们可以知道文件已被正确解析。
        // FExrReader内部会读取并丢弃文件头，但填充了LineOrTileOffsetsPerLevel。
        
        // 演示：立即关闭文件
        if (ExrReader.CloseExrFile())
        {
            UE_LOG(LogTemp, Log, TEXT("EXR file handle closed."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to open or parse EXR file."));
    }
}
```

## 模块依赖

要在你的模块中使用ImgMedia插件的功能，通常需要依赖以下模块。以下是根据插件内部模块关系提取的**独特依赖**：

| 模块 | 用途 |
|---|---|
| `ImgMedia` | 核心运行时模块，包含媒体播放器、加载器、缓存等主要逻辑。 |
| `ImgMediaFactory` | 提供媒体源工厂，用于创建`UMediaPlayer`和`UMediaTexture`等资产。 |
| `OpenExrWrapper` | 封装了OpenEXR库，提供基本的EXR文件读写能力。 |
| `ExrReaderGpu` | 提供GPU加速的EXR解码器和色域转换着色器。 |
| `MediaUtils` | Media Framework的通用工具库，提供播放器外观、样本队列等。 |

*注意：你的模块不需要直接依赖所有这些模块。通常，对于播放功能，依赖`ImgMedia`和`MediaUtils`即可。只有在需要使用底层EXR读写或GPU解码功能时，才需要直接依赖`OpenExrWrapper`或`ExrReaderGpu`。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `edcd0d53` | [ImgMedia] refresh single-frame sequences on tile visibility changes | 图像序列在图块可见性变化时刷新单帧序列 |
| 2026-05-26 | `cf292c45` | [ImgMedia] Use AR-constrained view rect for tile mip selection | 使用宽高比约束的视口矩形进行图块Mip选择 |
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened analytics | 媒体IO：修复了ImgMedia和NDI播放器发出不正确SourceOpened分析事件的近期提交 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and production | 媒体IO：为各种媒体播放器和捕获/生产功能添加了额外的引擎分析信息 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | [媒体] 在关卡编辑器窗口菜单中添加共享的“媒体”类别 |

### 维护评价

-   **创建时间**：2017年8月，是Media Framework 3.0重构期间的产物。
-   **维护活跃度**：**活跃维护**。尽管核心结构在2017年确立，但从最近的提交（2026年）可以看出，Epic仍在持续对插件进行优化和修复，特别是针对虚拟制作、分析（Analytics）和GPU解码路径的改进。
-   **稳定性**：经过近9年的发展，插件已非常成熟，是UE中播放图像序列（尤其是EXR）的标准方案。
-   **已知限制**：
    -   主要为EXR格式优化，其他格式（BMP/JPG/PNG）的性能和功能可能不如专用解码器。
    -   GPU解码路径（ExrReaderGpu）对硬件和驱动有一定要求。
    -   大规模、超高分辨率序列的内存管理仍需谨慎规划。
-   **推荐使用**：**强烈推荐**。对于需要在UE中播放高质量图像序列（特别是来自VFX工作流的EXR）的项目，此插件是唯一且官方的解决方案，功能完善，性能较好，且仍在积极维护。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia)
-   [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (较旧的论坛帖子，但概述了Media Framework)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia/Tests) (如果存在)