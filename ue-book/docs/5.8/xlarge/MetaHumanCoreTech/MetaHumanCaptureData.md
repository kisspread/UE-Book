# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 核心技术 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 角色资产、绑定蓝图等） |
| 模块 | `MetaHumanBodyTrackerInterface` (Runtime), `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-01（估计） |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

---

## 用途

MetaHuman Core Tech 是 MetaHuman 生态系统的底层核心技术库，为 **MetaHuman Creator**（Web 端角色创建工具）和 **MetaHuman Animator**（面部动作捕捉工具）提供基础算法支持。

该插件解决的核心问题：
- **身体追踪**：通过 `MetaHumanBodyTrackerInterface` 模块提供身体姿态估计的接口抽象
- **图像序列处理**：通过 `MetaHumanCaptureData` 模块处理视频/图像序列的帧率同步、路径解析
- **流水线处理**：通过 `MetaHumanPipelineCore` 模块提供可组合的处理流水线框架
- **OpenCV 集成**：提供计算机视觉算法支持，用于面部/身体特征点追踪

**注意**：此插件 `EnabledByDefault=false`，需要手动启用。它通常是 MetaHuman Creator 和 MetaHuman Animator 插件的依赖项，一般不会直接在项目中单独使用。

---

## 使用场景

- 你在使用 **MetaHuman Animator** 做面部动捕 → 底层依赖此插件处理视频帧和追踪算法
- 你在集成 **MetaHuman Creator** 的资产生成流程 → 此插件提供核心数据处理管道
- 你需要对图像序列进行帧率匹配和帧号转换 → 使用 `MetaHumanCaptureData` 模块
- 你需要实现自定义的身体追踪适配器 → 参考 `MetaHumanBodyTrackerInterface` 的接口定义

---

## 蓝图用法

此插件主要面向底层技术实现，公开的蓝图 API 较少。主要用途是作为其他 MetaHuman 插件的运行时依赖。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 此模块以 C++ 库为主，蓝图 API 有限 | - | - |

---

## C++ 用法

### 模块：MetaHumanCaptureData

此模块专注于图像序列数据的处理，提供帧率转换、帧路径解析等功能。

### 头文件引入

```cpp
#include "SequencedImageTrackInfo.h"
#include "FrameNumberTransformer.h"
#include "FramePathResolver.h"
#include "FramePathResolverSingleFile.h"
#include "TrackingPathUtils.h"
```

### 基本用法：帧率兼容性检查

```cpp
#include "SequencedImageTrackInfo.h"

// 创建两个轨道信息，源帧率不同
FFrameRate SourceFrameRate(24, 1);   // 24fps
FFrameRate TargetFrameRate(30, 1);   // 30fps

// 检查帧率是否兼容（整数倍关系）
bool bCompatible = UE::MetaHuman::FrameRatesAreCompatible(SourceFrameRate, TargetFrameRate);
// bCompatible == false (24和30不是整数倍关系)

// 检查一组轨道是否有兼容帧率
TArray<UE::MetaHuman::FSequencedImageTrackInfo> Tracks;
Tracks.Add(UE::MetaHuman::FSequencedImageTrackInfo(FFrameRate(24, 1), TRange<FFrameNumber>(0, 100)));
Tracks.Add(UE::MetaHuman::FSequencedImageTrackInfo(FFrameRate(24, 1), TRange<FFrameNumber>(0, 200)));

bool bSameRate = UE::MetaHuman::TracksHaveCompatibleFrameRates(Tracks);  // true
bool bDiffRate = UE::MetaHuman::TracksHaveDifferentFrameRates(Tracks);   // false
```

### 基本用法：帧号转换

```cpp
#include "FrameNumberTransformer.h"

// 简单偏移：将帧号 +10
UE::MetaHuman::FFrameNumberTransformer OffsetTransformer(10);
int32 NewFrame = OffsetTransformer.Transform(0);   // 返回 10
int32 NewFrame2 = OffsetTransformer.Transform(50);  // 返回 60

// 帧率转换：从 24fps 转换到 30fps
FFrameRate SourceRate(24, 1);
FFrameRate TargetRate(30, 1);
UE::MetaHuman::FFrameNumberTransformer RateTransformer(SourceRate, TargetRate);
int32 ConvertedFrame = RateTransformer.Transform(24);  // 返回 30
```

### 基本用法：帧路径解析

```cpp
#include "FramePathResolver.h"
#include "FramePathResolverSingleFile.h"

// 使用模板路径解析（每帧一个文件）
// 模板中的 {frame} 会被替换为帧号
UE::MetaHuman::FFramePathResolver Resolver(TEXT("/Sequences/Shot/frame_{frame}.exr"));
FString FramePath = Resolver.ResolvePath(42);
// 返回 "/Sequences/Shot/frame_0042.exr"

// 单文件解析器（所有帧返回同一路径，如视频文件）
UE::MetaHuman::FFramePathResolverSingleFile SingleResolver(TEXT("/Sequences/Shot/video.mp4"));
FString SamePath = SingleResolver.ResolvePath(0);   // "/Sequences/Shot/video.mp4"
FString SamePath2 = SingleResolver.ResolvePath(99); // "/Sequences/Shot/video.mp4"
```

### 进阶用法：帧率匹配丢帧计算

```cpp
#include "SequencedImageTrackInfo.h"

// 场景：目标帧率 24fps，但源数据混合了 24fps 和 30fps 的序列
FFrameRate TargetRate(24, 1);

TArray<UE::MetaHuman::FSequencedImageTrackInfo> MixedTracks;
MixedTracks.Add(UE::MetaHuman::FSequencedImageTrackInfo(
    FFrameRate(24, 1), TRange<FFrameNumber>(0, 100)));
MixedTracks.Add(UE::MetaHuman::FSequencedImageTrackInfo(
    FFrameRate(30, 1), TRange<FFrameNumber>(0, 120)));

// 计算需要丢弃的帧，使所有序列对齐到目标帧率
TArray<FFrameNumber> DropFrames = UE::MetaHuman::CalculateRateMatchingDropFrames(
    TargetRate, MixedTracks);

// 使用范围限制版本
TRange<FFrameNumber> Limit(TRangeBound<FFrameNumber>(10), TRangeBound<FFrameNumber>(50));
TArray<FFrameNumber> LimitedDropFrames = UE::MetaHuman::CalculateRateMatchingDropFrames(
    TargetRate, MixedTracks, Limit);

// 找到所有序列的第一个公共帧号
int32 CommonFrame = UE::MetaHuman::FindFirstCommonFrameNumber(MixedTracks);
```

### 进阶用法：追踪路径工具

```cpp
#include "TrackingPathUtils.h"

// 从图像序列源获取追踪文件路径信息
FString TrackingFilePath;
int32 FrameOffset;
int32 NumFrames;

bool bSuccess = FTrackingPathUtils::GetTrackingFilePathAndInfo(
    ImgMediaSource,  // UImgMediaSource*
    TrackingFilePath,
    FrameOffset,
    NumFrames
);

// 从文件路径格式直接解析
bool bSuccess2 = FTrackingPathUtils::GetTrackingFilePathAndInfo(
    TEXT("/Sequences/Tracking/frame_{frame}.json"),
    TrackingFilePath,
    FrameOffset,
    NumFrames
);

// 展开帧号格式占位符
FString ExpandedPath = FTrackingPathUtils::ExpandFilePathFormat(
    TEXT("/Data/frame_{frame}.exr"), 42);
```

---

## Demo 示例

### 自定义帧路径解析器

```cpp
// MyCustomFramePathResolver.h
#pragma once

#include "IFramePathResolver.h"

class FMyCustomFramePathResolver : public UE::MetaHuman::IFramePathResolver
{
public:
    explicit FMyCustomFramePathResolver(const FString& InBasePath, const FString& InExtension)
        : BasePath(InBasePath), Extension(InExtension) {}

    virtual FString ResolvePath(int32 InFrameNumber) const override
    {
        // 自定义路径格式: BasePath/frame_000001.ext
        return FString::Printf(TEXT("%s/frame_%06d.%s"), *BasePath, InFrameNumber, *Extension);
    }

private:
    FString BasePath;
    FString Extension;
};
```

```cpp
// MyCaptureProcessor.cpp
#include "SequencedImageTrackInfo.h"
#include "FrameNumberTransformer.h"
#include "MyCustomFramePathResolver.h"

void ProcessCaptureData()
{
    // 1. 创建轨道信息（30fps 输入，24fps 目标）
    FFrameRate InputRate(30, 1);
    FFrameRate OutputRate(24, 1);
    TRange<FFrameNumber> FrameRange(0, 300);

    UE::MetaHuman::FSequencedImageTrackInfo TrackInfo(InputRate, FrameRange);

    // 2. 创建帧号转换器
    UE::MetaHuman::FFrameNumberTransformer Transformer(InputRate, OutputRate);

    // 3. 创建路径解析器
    FMyCustomFramePathResolver PathResolver(TEXT("/Capture/Subject01"), TEXT("png"));

    // 4. 处理每一帧
    for (int32 Frame = FrameRange.GetLowerBoundValue();
         Frame <= FrameRange.GetUpperBoundValue(); ++Frame)
    {
        // 获取源帧路径
        FString SourcePath = PathResolver.ResolvePath(Frame);

        // 转换帧号（用于时间轴对齐）
        int32 OutputFrame = Transformer.Transform(Frame);

        UE_LOG(LogMetaHumanCaptureData, Log,
            TEXT("Frame %d -> %d, Path: %s"), Frame, OutputFrame, *SourcePath);
    }
}
```

---

## 模块依赖

### MetaHumanCaptureData

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewer` | 图像查看和预览功能 |
| `DirectoryWatcher` | 文件系统监控 |

### MetaHumanCoreTechLib

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器功能集成 |
| `OnlineSubsystem` | 在线服务支持 |

### MetaHumanPipelineCore

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器功能集成 |
| `OpenCVHelper` | OpenCV 工具封装 |
| `OpenCV` | 计算机视觉算法库 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | MetaHuman Titan 版本升级到 v9.0.8 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | MetaHuman Titan 版本升级到 v9.0.7 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | MetaHuman Titan 版本升级到 v9.0.6 |
| 2026-05-20 | `c5214fb2` | [MetaHumanBodyTracker] allow foot-locking to be toggled on or off | 身体追踪器新增脚部锁定开关功能 |
| 2026-05-19 | `a29cddd9` | [MHA] Crash during MHC assembly with body performance | 修复 MetaHuman Creator 装配时身体性能相关崩溃 |

### 维护评价

- **维护状态**：🟢 **活跃维护**
- **更新频率**：非常活跃，最近一周内有多次更新
- **版本迭代**：持续进行 Titan 版本迭代（v9.0.x 系列）
- **功能完善**：仍在添加新功能（如脚部锁定控制）
- **稳定性**：有持续的 bug 修复（崩溃修复）

**推荐使用**：✅ 强烈推荐。这是 MetaHuman 生态系统的核心组件，由 Epic Games 官方团队积极维护。如果你的项目使用 MetaHuman 角色，此插件是必须的依赖项。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-in-unreal-engine/)
- [MetaHuman Creator](https://metahuman.unrealengine.com/)