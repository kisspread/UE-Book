# Capture Manager Devices

> The Capture Manager Devices contains devices that can be used from the Capture Manager layout of the LiveLink Hub

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器设备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（设备蓝图资产） |
| 模块 | `CPSLiveLinkDevice` (Runtime), `MonoVideoIngestDevice` (Runtime), `StereoVideoIngestDevice` (Runtime), `TakeArchiveIngestDevice` (Runtime), `VideoLiveLinkDeviceCommon` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices) | |

## 用途

本插件为 **LiveLink Hub 的 Capture Manager 布局**提供各类视频摄取设备的实现。在虚拟制片工作流中，需要从不同来源（单目视频、立体视频、Live Link Face、Take 归档文件等）采集数据，本插件将这些设备以 LiveLink Device 的形式统一接入 Capture Manager 管线。

核心解决的问题是：**将多种视频捕获硬件/数据源抽象为标准化的 LiveLink 设备**，使得 Capture Manager 能够通过统一接口发现、配置和摄取来自不同来源的视频数据与元数据（如 Slate 名称、Take 编号等）。

## 使用场景

- 你使用 **Live Link Face** 应用捕捉面部表演数据 → 用 `CPSLiveLinkDevice` 和 `MonoVideoIngestDevice`
- 你使用 **立体视频**（双目）设备进行体积捕捉 → 用 `StereoVideoIngestDevice`
- 你需要从已有的 **Take 归档文件**中重新摄取数据 → 用 `TakeArchiveIngestDevice`
- 你需要 **自定义 Take 发现规则**（按命名表达式匹配文件）→ 使用 `FTakeDiscoveryExpression` 和 `FTakeDiscoveryExpressionParser`
- 你需要从视频文件中 **提取缩略图** → 使用 `FVideoDeviceThumbnailExtractor`

## 蓝图用法

本插件的蓝图 API 主要集中在 `VideoLiveLinkDeviceCommon` 模块中定义的数据结构。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FTakeDiscoveryExpression.Value` | 可读写的发现表达式字符串 | `FTakeDiscoveryExpression` |

### FTakeDiscoveryExpression 结构体

`FTakeDiscoveryExpression` 是一个 `BlueprintType` 结构体，包含一个 `BlueprintReadWrite` 的 `FString Value` 属性。它用于在编辑器中定义 Take 文件的发现/匹配规则，支持以下预定义 Token：

| Token | 含义 |
|---|---|
| `{SlateName}` | Slate 名称 |
| `{TakeNumber}` | Take 编号 |
| `{Name}` | 设备/文件名称 |
| `{Any}` | 任意匹配 |

在蓝图中，你可以通过属性编辑器配置该表达式，它会在 Capture Manager 的设备设置面板中提供自定义属性外观。

## C++ 用法

### 头文件引入

```cpp
#include "TakeDiscoveryExpressionParser.h"
#include "VideoDeviceThumbnailExtractor.h"
```

### 基本用法 — 解析 Take 发现表达式

`FTakeDiscoveryExpressionParser` 用于根据格式表达式从文件路径或名称中解析出 Slate 名称、Take 编号等信息。

```cpp
// 定义格式和实际值
FString Format = TEXT("{SlateName}_{TakeNumber}_{Name}");
FString FormattedValue = TEXT("MySlate_003_CameraA");

// 定义允许的分隔符
TArray<FString::ElementType> Delimiters = { TEXT('_'), TEXT('-') };

// 创建解析器
FTakeDiscoveryExpressionParser Parser(Format, FormattedValue, Delimiters);

// 执行解析
if (Parser.Parse())
{
    FString SlateName = Parser.GetSlateName();    // "MySlate"
    int32 TakeNumber = Parser.GetTakeNumber();     // 3
    FString Name = Parser.GetName();              // "CameraA"
}
```

**来源**: `Public/Utils/TakeDiscoveryExpressionParser.h`

### 基本用法 — 提取视频缩略图

`FVideoDeviceThumbnailExtractor` 通过第三方编码器从视频文件中提取缩略图图像。

```cpp
using namespace UE::CaptureManager;

FVideoDeviceThumbnailExtractor Extractor;

// 从指定视频文件提取缩略图
FString VideoFilePath = TEXT("/Path/To/VideoFile.mp4");
TOptional<FTakeThumbnailData::FRawImage> Thumbnail = Extractor.ExtractThumbnail(VideoFilePath);

if (Thumbnail.IsSet())
{
    // 使用缩略图数据，例如保存为图像或显示在 UI 中
    const FTakeThumbnailData::FRawImage& ImageData = Thumbnail.GetValue();
}
```

**来源**: `Public/Utils/VideoDeviceThumbnailExtractor.h`

**注意**: `ExtractThumbnail` 内部通过调用第三方编码器进程（`ObtainThumbnailFromThirdPartyEncoder`）生成 256 像素宽的缩略图。

### 进阶用法 — 自定义属性编辑器外观

`FTakeDiscoveryExpressionCustomization` 是 `IPropertyTypeCustomization` 的实现，为 `FTakeDiscoveryExpression` 提供自定义的 Details 面板外观。在编辑器模块中注册该自定义：

```cpp
// 通常在编辑器 StartupModule 中注册
PropertyModule.RegisterCustomPropertyTypeLayout(
    FTakeDiscoveryExpression::StaticStruct()->GetFName(),
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(
        &FTakeDiscoveryExpressionCustomization::MakeInstance
    )
);
```

该自定义会在 Details 面板中提供：
- 表达式值的文本显示（`OnGetExpressionValue`）
- 实时验证（`OnExpressionValidate` / `ValidateExpression`）
- 只读模式支持（`IsReadOnly`）

## Demo 示例

以下示例展示如何在运行时使用 `FTakeDiscoveryExpressionParser` 从文件名中批量解析 Take 信息：

### TakeDiscoveryDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FTakeDiscoveryDemo
{
public:
    struct FParsedTakeInfo
    {
        FString SlateName;
        int32 TakeNumber;
        FString DeviceName;
    };

    static TArray<FParsedTakeInfo> ParseFileList(
        const FString& InFormat,
        const TArray<FString>& InFileNames
    );
};
```

### TakeDiscoveryDemo.cpp

```cpp
#include "TakeDiscoveryDemo.h"
#include "Utils/TakeDiscoveryExpressionParser.h"

TArray<FTakeDiscoveryDemo::FParsedTakeInfo> FTakeDiscoveryDemo::ParseFileList(
    const FString& InFormat,
    const TArray<FString>& InFileNames)
{
    TArray<FParsedTakeInfo> Results;

    // 常见分隔符
    TArray<FString::ElementType> Delimiters = { TEXT('_'), TEXT('-'), TEXT('.') };

    for (const FString& FileName : InFileNames)
    {
        FTakeDiscoveryExpressionParser Parser(InFormat, FileName, Delimiters);

        if (Parser.Parse())
        {
            FParsedTakeInfo Info;
            Info.SlateName = Parser.GetSlateName();
            Info.TakeNumber = Parser.GetTakeNumber();
            Info.DeviceName = Parser.GetName();

            Results.Add(MoveTemp(Info));
        }
    }

    return Results;
}
```

## 模块依赖

基于各模块的功能分析，以下为该插件特有的依赖模块：

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | LiveLink 设备接口与协议定义 |
| `LiveLinkHub` | LiveLink Hub 核心框架，提供设备注册与管理 |
| `MediaUtils` | 媒体纹理采样 (`FMediaTextureSample`) |
| `CaptureManagerCore` | Capture Manager 核心框架，提供 Take 数据结构与摄取管线 |
| `ImageWriteQueue` | 图像写入（缩略图保存） |

无特殊依赖（仅标准 Core/Engine/Slate 等）— 具体依赖需查阅各模块的 `Build.cs` 文件确认。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `222ac128` | StereoVideoIngest: Fix component name consistency across ingest devices | 修复立体视频设备中组件名称不一致的问题 |
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | CaptureManagerCore 新增 CPS 客户端模块（影响本插件的依赖链） |
| 2026-04-27 | `778f07fc` | [CaptureManager] Fix log category ODR violations in video devices | 修复视频设备中日志分类的 ODR 违规问题 |
| 2026-04-27 | `334822cd` | Add ConfigureMediaSource virtual hook to ULiveLinkFaceDevice | 为 LiveLink Face 设备添加 ConfigureMediaSource 虚函数钩子 |
| 2026-04-21 | `40065f3e` | Added connection indicator for Live Link Face devices | 为 LiveLink Face 设备添加连接状态指示器 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2025 年 2 月，插件年龄约 1 年，属于较新的插件
- **更新频率**：最近 2 个月内有 5 次更新，涉及 bug 修复、新功能和代码质量改进，维护非常活跃
- **维护状态**：由 Epic Games 官方维护，作为 Virtual Production 管线的核心组件持续迭代
- **已知限制**：默认未启用（`EnabledByDefault=false`），需手动在项目设置中启用
- **推荐程度**：⭐⭐⭐⭐ 如果你的虚拟制片工作流涉及 LiveLink Hub 的 Capture Manager，本插件是必装组件；否则无需启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices)
- [官方文档](https://docs.unrealengine.com)（暂无独立文档页面）
- [CaptureManager 主插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager)