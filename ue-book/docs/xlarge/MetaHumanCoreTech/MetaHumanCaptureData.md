# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时库、数据处理模块） |
| 模块 | `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-01-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHuman Core Tech 是 MetaHuman Creator（用于创建高保真数字人）和 MetaHuman Animator（用于将面部表演动画应用到数字人）插件的底层技术基础库。它并非一个面向最终用户的独立功能插件，而是一个提供核心算法、数据处理管线和工具集的“引擎”。它解决了从原始面部捕捉数据（如视频、深度图像序列）到可用于驱动 MetaHuman 角色的动画数据之间的转换、处理和同步问题。其存在是为了将复杂的计算机视觉和图形学算法封装成 UE 可用的模块，供上层插件调用。

## 使用场景

- 你正在开发或使用 MetaHuman Creator/Animator 插件，需要理解其底层数据处理逻辑。
- 你需要处理来自 iPhone 或其他设备的面部捕捉数据（图像序列、深度数据），并将其转换为可用于驱动 MetaHuman 角色的动画曲线。
- 你需要在不同帧率的图像序列和动画序列之间进行精确的同步和转换。
- 你需要解析和管理复杂的图像序列文件路径格式。

## 蓝图用法

本插件主要提供底层 C++ 库，直接暴露给蓝图的节点较少。其功能主要通过上层插件（如 MetaHuman Animator）的蓝图接口间接使用。在 `MetaHumanCaptureData` 模块中，存在一些可能被蓝图调用的静态工具函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTrackingFilePathAndInfo` | 从图像序列资产或路径中解析出追踪文件路径、帧偏移和总帧数。 | `FTrackingPathUtils` |
| `ExpandFilePathFormat` | 将包含帧号占位符（如 `%04d`）的路径格式字符串扩展为具体帧的文件路径。 | `FTrackingPathUtils` |

### 使用示例（蓝图描述）

在蓝图中，你可以使用 `FTrackingPathUtils` 的静态函数来获取图像序列的元数据。例如，通过一个 `UImgMediaSource` 资产引用，调用 `GetTrackingFilePathAndInfo` 节点，即可获得该序列对应的追踪数据文件路径、起始帧偏移和总帧数，用于后续的动画数据加载和同步。

## C++ 用法

核心功能通过 C++ 类和接口提供，主要用于构建数据处理管线。

### 头文件引入

```cpp
#include "MetaHumanCaptureData/FramePathResolver.h"
#include "MetaHumanCaptureData/FrameNumberTransformer.h"
#include "MetaHumanCaptureData/TrackingPathUtils.h"
```

### 基本用法

**1. 帧路径解析**
用于将帧号转换为具体的图像文件路径。
```cpp
// 来源: FramePathResolver.h
// 创建一个路径解析器，模板中 %d 会被帧号替换
UE::MetaHuman::FFramePathResolver PathResolver(TEXT("/Game/Captures/Frame_%04d.png"));

// 解析第 100 帧的路径
FString Frame100Path = PathResolver.ResolvePath(100);
// 结果: "/Game/Captures/Frame_0100.png"
```

**2. 帧号转换**
用于处理不同帧率序列之间的同步。
```cpp
// 来源: FrameNumberTransformer.h
// 源序列 30fps，目标序列 24fps，并应用 10 帧的偏移
FFrameRate SourceRate(30, 1);
FFrameRate TargetRate(24, 1);
UE::MetaHuman::FFrameNumberTransformer Transformer(SourceRate, TargetRate, 10);

// 将源序列的第 30 帧转换为目标序列的帧号
int32 TargetFrame = Transformer.Transform(30);
```

### 进阶用法

**处理图像序列的追踪信息**
结合 `FTrackingPathUtils` 和 `FFramePathResolver` 来处理一个完整的图像序列。
```cpp
// 来源: TrackingPathUtils.h, FramePathResolver.h
// 假设有一个图像序列资产
UImgMediaSource* ImageSequence = ...;
FString TrackingFilePath;
int32 FrameOffset, NumFrames;

// 1. 获取序列的追踪文件信息
if (FTrackingPathUtils::GetTrackingFilePathAndInfo(ImageSequence, TrackingFilePath, FrameOffset, NumFrames))
{
    // 2. 基于追踪文件信息，可能需要创建一个帧路径解析器来访问原始图像
    // 假设图像路径格式与追踪文件相关
    FString ImagePathTemplate = FPaths::GetPath(TrackingFilePath) / TEXT("frame_%05d.exr");
    UE::MetaHuman::FFramePathResolver ImagePathResolver(ImagePathTemplate, UE::MetaHuman::FFrameNumberTransformer(FrameOffset));

    // 3. 遍历所有帧
    for (int32 i = 0; i < NumFrames; ++i)
    {
        FString CurrentImagePath = ImagePathResolver.ResolvePath(i);
        // ... 处理当前帧图像
    }
}
```

## Demo 示例

一个最小示例，展示如何使用帧路径解析器和帧号转换器。

**MyMetaHumanDataProcessor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "FramePathResolver.h"
#include "FrameNumberTransformer.h"

class FMyMetaHumanDataProcessor
{
public:
    void ProcessImageSequence(const FString& InPathTemplate, FFrameRate InSourceRate, FFrameRate InTargetRate, int32 InFrameOffset);

private:
    UE::MetaHuman::FFramePathResolver* PathResolver = nullptr;
    UE::MetaHuman::FFrameNumberTransformer* FrameTransformer = nullptr;
};
```

**MyMetaHumanDataProcessor.cpp**
```cpp
#include "MyMetaHumanDataProcessor.h"

void FMyMetaHumanDataProcessor::ProcessImageSequence(const FString& InPathTemplate, FFrameRate InSourceRate, FFrameRate InTargetRate, int32 InFrameOffset)
{
    // 初始化转换器（处理帧率差异和偏移）
    FrameTransformer = new UE::MetaHuman::FFrameNumberTransformer(InSourceRate, InTargetRate, InFrameOffset);

    // 初始化路径解析器，并应用帧号转换
    PathResolver = new UE::MetaHuman::FFramePathResolver(InPathTemplate, *FrameTransformer);

    // 模拟处理前 10 帧
    for (int32 SourceFrame = 0; SourceFrame < 10; ++SourceFrame)
    {
        // 获取在目标时间线上对应的文件路径
        FString ResolvedPath = PathResolver->ResolvePath(SourceFrame);
        UE_LOG(LogTemp, Log, TEXT("Processing frame %d -> %s"), SourceFrame, *ResolvedPath);
        // ... 在此处加载图像并进行处理
    }

    // 清理
    delete PathResolver;
    delete FrameTransformer;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewer` | 提供图像查看和预览功能，被 `MetaHumanCaptureData` 依赖。 |
| `DirectoryWatcher` | 监控文件系统目录变化，用于实时更新捕捉数据。 |
| `OpenCVHelper` | OpenCV 的 UE 封装助手，被 `MetaHumanPipelineCore` 依赖，用于计算机视觉处理。 |
| `OpenCV` | OpenCV 库本身，提供核心的图像处理算法。 |

## 维护状态

### 近期更新

- `cd55bfb4efb7` [MetaHuman] Removed duplicated check in frame transformer test. (移除了帧转换器测试中的重复检查)
- `5a58c0a5cddf` [MetaHuman] Fixed rounding issue in frame path resolver. (修复了帧路径解析器中的舍入问题)
- `52e3dac151e1` Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n (使用 UnrealCodeFixup 更新头文件，确保 DLL 导出符号正确)

### 维护评价

该插件创建于 2025 年初，非常年轻。从近期提交记录看，开发团队仍在积极维护和修复问题（如舍入错误、测试代码清理）。作为 MetaHuman 技术栈的核心基础，它预计会随着 MetaHuman Creator/Animator 的更新而持续演进。目前没有发现已知的重大限制或废弃迹象。**推荐使用**，但需注意其作为底层库的性质，通常不直接面向最终用户，而是通过上层插件间接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- [官方文档]() (暂无)
- [测试用例]() (插件目录内未发现标准测试文件，测试可能集成在上层插件或内部流程中)