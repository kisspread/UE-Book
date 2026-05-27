# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体IO框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-10-02 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework) | |

## 用途
MediaIOFramework 插件为 Unreal Engine 提供了用于专业媒体输入输出（IO）的基础框架。它抽象了与外部专业媒体设备（如 AJA、Blackmagic）通信的细节，为虚拟制作（Virtual Production）工作流中的实时视频输入、输出和捕获提供了核心支持。此插件并非直接提供特定硬件的驱动，而是定义了统一的接口、配置结构体和编辑器工具，以便其他插件（如 MediaIOFramework 的具体硬件实现插件）可以基于此框架快速集成。

## 使用场景
- 你正在开发一个虚拟制作项目，需要将 Unreal Engine 的渲染画面实时输出到专业的 SDI 视频设备 → 使用此框架配置媒体输出
- 你需要将来自摄像机、采集卡等专业设备的视频流作为 Unreal Engine 的纹理输入 → 使用此框架配置媒体输入
- 你需要对媒体输入输出的设备、端口、分辨率、帧率等参数进行精确、复杂的配置 → 使用此框架提供的编辑器选择器 UI

## 蓝图用法
此插件主要提供编辑器扩展和底层 C++ 框架，蓝图直接调用的 `BlueprintCallable` 函数较少。其主要价值体现在编辑器属性的自定义 UI 上。

### 核心节点（编辑器 UI 相关）
| 节点 | 说明 | 所在类 |
|---|---|---|
| `SMediaPermutationsSelector::GetSelectedItem` | 从媒体配置排列选择器中获取当前选中的配置项 | `SMediaPermutationsSelector` |
| `FMediaIOCustomizationBase::GetMediaProperty` | 获取正在定制的属性句柄 | `FMediaIOCustomizationBase` |

### 使用示例（蓝图描述）
在“媒体输出”（Media Output）或“媒体输入”（Media Input）资产的属性面板中，当你需要设置 `MediaIOConfiguration`、`MediaIOOutputConfiguration` 等结构体属性时，编辑器会自动显示一个复杂的多列选择器（由 `SMediaPermutationsSelector` 驱动）。你通过在各个下拉列（如设备、端口、分辨率等）中进行选择，最终组合出一个完整的媒体 IO 配置，然后点击“应用”按钮完成设置。

## C++ 用法
### 头文件引入
```cpp
#include "MediaIOCore.h"
```
### 基本用法
以下示例展示了如何使用 `FMediaIOConfiguration` 结构体来描述一个媒体 IO 连接，并使用 `FMediaIOPermutationsSelectorBuilder` 提供的静态函数来获取其显示文本。此用法常见于编辑器定制逻辑中。

```cpp
// 来源: MediaIOPermutationsSelectorBuilder.h
// 创建一个 FMediaIOConfiguration 实例并填充数据
FMediaIOConfiguration MediaConfig;
MediaConfig.MediaConnection.DeviceIdentifier = FMediaIODeviceIdentifier("AJA", 0);
MediaConfig.MediaConnection.TransportType = EMediaIOTransportType::SingleLink;
MediaConfig.MediaConnection.QuadType = EMediaIOQuadType::None;
MediaConfig.MediaConnection.Standard = EMediaIOStandardType::Progressive;
MediaConfig.MediaMode.Resolution = FIntPoint(1920, 1080);
MediaConfig.MediaMode.FrameRate = FFrameRate(24, 1);

// 使用 SelectorBuilder 获取特定列的显示标签
FText DeviceLabel = FMediaIOPermutationsSelectorBuilder::GetLabel(
    FMediaIOPermutationsSelectorBuilder::NAME_DeviceIdentifier, MediaConfig);
// DeviceLabel 的值可能是 “AJA (0)”

FText ResolutionLabel = FMediaIOPermutationsSelectorBuilder::GetLabel(
    FMediaIOPermutationsSelectorBuilder::NAME_Resolution, MediaConfig);
// ResolutionLabel 的值可能是 “1920x1080”
```
### 进阶用法
更高级的用法涉及创建自定义的媒体设备提供程序（Device Provider）或扩展编辑器 UI。这通常需要实现 `IMediaIOCoreDeviceProvider` 接口（定义在 `MediaIOCore` 模块中），并使用 `MediaIOEditor` 模块中的定制化基类（如 `FMediaIOCustomizationBase`）来构建属性编辑 UI。例如，要为你的自定义硬件设备创建一个属性定制器，可以继承 `FMediaIOConfigurationCustomization` 并重写相关方法。

## Demo 示例
这是一个最小化的媒体输出资产类演示，展示了如何基于此框架创建自己的媒体输出配置。

```cpp
// MyMediaOutput.h
#pragma once
#include "MediaOutput.h"
#include "MyMediaOutput.generated.h"

UCLASS(BlueprintType)
class UMyMediaOutput : public UMediaOutput
{
    GENERATED_BODY()
public:
    // 覆写基类方法，定义如何使用配置创建媒体捕获
    virtual FIntPoint GetRequestedSize() const override { return RequestedSize; }
    virtual EPixelFormat GetRequestedPixelFormat() const override { return PF_B8G8R8A8; }
    virtual EMediaCaptureConversionOperation GetConversionOperation(EMediaCaptureSourceType InSourceType) const override { return EMediaCaptureConversionOperation::NONE; }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MediaOutput")
    FIntPoint RequestedSize;

    // 在这里可以添加你自定义的媒体IO配置属性
    // UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MediaOutput")
    // FMediaIOOutputConfiguration MediaIOOutputConfiguration;
};
```

## 模块依赖
从 `Build.cs` 文件分析，使用者需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 提供核心的媒体 IO 结构体、接口和运行时逻辑 |
| `OpenColorIO` | 用于色彩空间转换，支持专业媒体工作流中的颜色准确性 |

## 维护状态
### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为黑魔术和AJA卡的自动模式填充媒体配置 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和捕获添加了额外的引擎分析信息 |
| 2026-05-14 | `a43a62b2` | Media Profile: Changed media texture capture behavior to always preserve aspect ratio of texture even when the ratio doesn’t match the output aspect ratio | 媒体纹理捕获行为更改，始终保留纹理宽高比 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数导致的警告 |
| 2026-05-12 | `a879de69` | Fix clang warnings when compiling MediaIODeinterlacerTests | 修复编译 MediaIODeinterlacerTests 时的 clang 警告 |

### 维护评价
- **活跃维护**：插件在 2026 年 5 月有多次实质性提交，表明仍在积极维护和改进。
- **功能更新**：近期更新集中在专业硬件（AJA， Blackmagic）的自动配置支持、分析数据收集和视频处理行为优化上，与虚拟制作行业需求紧密相关。
- **稳定性**：近期也包含了编译警告和浮点精度问题的修复，表明对代码质量的关注。
- **实验性**：非实验性、非Beta版，是一个成熟的生产级框架插件。
- **推荐使用**：对于需要在 Unreal Engine 中集成专业媒体IO设备的虚拟制作项目，**强烈推荐**使用此插件作为基础框架。它提供了经过良好设计的架构和编辑器工具，能显著简化开发工作。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework)
- [官方文档]() (此插件无专门文档，其功能通常作为其他媒体插件的一部分被文档化)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/MediaIOCore/)