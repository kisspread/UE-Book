# PSD Importer

> （Description 字段为空，基于源码分析补充）将 Adobe Photoshop (.psd) 文件直接导入 Unreal Engine，保留图层结构、蒙版、混合模式等信息，无需预先在 PS 中导出为 PNG/TGA。

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（第三方 PSD 解析库、编辑器导入功能） |
| 模块 | `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 解决的核心问题是**将 Photoshop 的 PSD 文件结构完整地导入 Unreal Engine**。

传统的美术工作流中，美术在 Photoshop 中完成设计后需要手动导出每层为单独的 PNG/TGA 文件，然后逐一导入 UE。这个过程繁琐且容易出错——图层错位、分辨率不一致、蒙版丢失等问题频发。

本插件直接解析 PSD 文件的二进制格式，能够：

- **保留完整图层结构**：每个 PSD 图层可作为独立纹理资产导入，无需手动切图
- **保留蒙版信息**：支持图层蒙版（LayerMask）和矢量蒙版（VectorMask）
- **保留混合模式**：解析 28 种 Photoshop 混合模式（Normal、Multiply、Overlay 等）
- **支持多种位深**：8-bit、16-bit、32-bit 浮点通道
- **支持透明度**：提取透明蒙版通道数据

插件内部使用了 Molecular Matters GmbH 的 **PsdSDK** 第三方库作为底层 PSD 解析引擎，该库提供了完整的 PSD 文件读取和写入能力，包括 RLE 解压缩、平面/交错像素数据转换、异步文件 I/O 等功能。

插件依赖 **GeometryMask** 插件处理几何蒙版相关功能，且目前仅支持 **Win64** 平台。

## 使用场景

- 你是一名 UI 美术，在 Photoshop 中设计了多层 HUD 界面 → 使用本插件一键导入所有图层，每层自动成为独立纹理
- 你在一个 2D 游戏项目中，角色/场景由 PS 分层文件制作 → 直接导入 PSD，保留每个图层的精确位置和蒙版
- 你的团队使用 Photoshop 进行概念设计，需要快速在 UE 中预览 → 导入 PSD 后直接在引擎中查看完整图层效果
- 你需要频繁迭代美术资源，每次修改后都要重新导出 → 修改 PSD 后直接重新导入，无需中间格式转换

## 蓝图用法

本插件主要作为**编辑器导入工具**使用，其核心功能集成在 Content Browser 的导入流程中，而非蓝图运行时 API。

### 导入方式

1. 在 Content Browser 中右键 → **Import**
2. 选择 `.psd` 文件
3. 插件会解析 PSD 文件结构，提供图层导入选项
4. 导入后的资产可在内容浏览器中作为纹理使用

### 资产类型

导入的 PSD 数据可能生成：
- 单独的纹理资产（每个图层一张）
- 合并的画布纹理
- 图层蒙版相关的资产

> **注意**：由于插件仍处于实验阶段（Experimental），具体的导入对话框和配置选项可能随版本变化。建议在实际使用前查阅引擎内的导入提示。

## C++ 用法

### 头文件引入

```cpp
// 使用 PSD 核心解析功能
#include "PSDImporterCore.h"

// 使用第三方 PSD SDK
#include "Psd.h"  // SDK 主头文件
#include "PsdDocument.h"
#include "PsdLayer.h"
#include "PsdLayerMaskSection.h"
```

### 基本用法：解析 PSD 文件

以下示例展示如何使用底层 PsdSDK 解析一个 PSD 文件并获取图层信息。

```cpp
// 基于 PsdSDK API 的典型使用模式
// 参考: Includes/PsdParseLayerMaskSection.h, Includes/PsdFile.h

#include "PsdDocument.h"
#include "PsdNativeFile.h"
#include "PsdMallocAllocator.h"
#include "PsdParseLayerMaskSection.h"
#include "PsdParseImageResourcesSection.h"
#include "PsdParseImageDataSection.h"
#include "PsdLayer.h"
#include "PsdSyncFileReader.h"

// 创建分配器和文件对象
psd::MallocAllocator allocator;
psd::NativeFile file(&allocator);

// 打开 PSD 文件
if (file.OpenRead(L"test.psd"))
{
    // 同步读取文件头部
    psd::SyncFileReader reader(&file);
    // ... 解析文档头 ...

    // 解析图层蒙版段（可与其他段并行解析）
    psd::LayerMaskSection* layerMaskSection = psd::ParseLayerMaskSection(document, &file, &allocator);

    // 遍历所有图层
    for (unsigned int i = 0; i < layerMaskSection->layerCount; ++i)
    {
        psd::Layer& layer = layerMaskSection->layers[i];
        
        // 提取单个图层数据（可多线程并行）
        psd::ExtractLayer(document, &file, &allocator, &layer);
        
        // 读取图层信息
        const char* layerName = layer.name.c_str();
        int left = layer.left;
        int top = layer.top;
        int right = layer.right;
        int bottom = layer.bottom;
        bool visible = layer.isVisible;
        uint8_t opacity = layer.opacity;
        uint32_t blendMode = layer.blendModeKey;
    }

    // 清理资源
    psd::DestroyLayerMaskSection(layerMaskSection, &allocator);
    file.Close();
}
```

### 进阶用法：图层数据交错与导出

```cpp
// 展示如何将解析的平面数据交错为 RGBA，并用于纹理创建
// 参考: Includes/PsdInterleave.h, Includes/PsdExport.h, Includes/PsdLayerCanvasCopy.h

#include "PsdInterleave.h"
#include "PsdExport.h"
#include "PsdLayerCanvasCopy.h"
#include "PsdBlendMode.h"
#include "PsdChannelType.h"

// 假设已经从图层中获取了各通道的平面数据
// layer.channels[0] -> R, layer.channels[1] -> G, layer.channels[2] -> B
// 每个通道大小: (right-left) * (bottom-top) 字节

unsigned int width = layer.right - layer.left;
unsigned int height = layer.bottom - layer.top;

// 分配交错后的 RGBA 缓冲区 (必须 16 字节对齐)
uint8_t* rgbaData = /* 分配 width * height * 4 字节，16字节对齐 */;

// 将平面 RGB 数据交错为 RGBA，alpha 设为 255
psd::imageUtil::InterleaveRGB(
    rChannelData, gChannelData, bChannelData,
    static_cast<uint8_t>(255),  // 常量 alpha
    rgbaData,
    width, height
);

// --- 混合模式查询 ---
psd::blendmode::Enum mode = psd::blendMode::KeyToEnum(layer.blendModeKey);
const char* modeName = psd::blendMode::ToString(mode);
// 例如: "Normal", "Multiply", "Overlay", "Screen" 等

// --- 将图层数据复制到画布 ---
// 画布尺寸为文档尺寸
uint8_t* canvasData = /* 分配 docWidth * docHeight 字节 */;

psd::imageUtil::CopyLayerData(
    layerRChannel, canvasData,
    layer.left, layer.top, layer.right, layer.bottom,
    docWidth, docHeight
);

// --- 导出为新的 PSD 文件 ---
psd::ExportDocument* exportDoc = psd::CreateExportDocument(
    &allocator, docWidth, docHeight,
    8, psd::exportColorMode::RGB
);

// 添加图层
unsigned int layerIdx = psd::AddLayer(exportDoc, &allocator, "MyLayer");

// 更新图层数据（支持 8/16/32 位）
psd::UpdateLayer(exportDoc, &allocator, layerIdx,
    psd::exportChannel::R, left, top, right, bottom,
    rData, psd::compressionType::RLE);

// 写入文件
psd::NativeFile outFile(&allocator);
outFile.OpenWrite(L"output.psd");
psd::WriteDocument(exportDoc, &allocator, &outFile);

psd::DestroyExportDocument(exportDoc, &allocator);
```

## Demo 示例

以下是一个最小可编译的 UE5 插件示例，展示如何在编辑器工具中使用 PsdSDK 读取 PSD 文件：

```cpp
// PsdReaderTool.h
#pragma once

#include "CoreMinimal.h"

class FPsdReaderTool
{
public:
    /** 解析 PSD 文件并输出图层信息到日志 */
    static void ReadPsdLayers(const FString& FilePath);
};
```

```cpp
// PsdReaderTool.cpp
#include "PsdReaderTool.h"
#include "Psd.h"
#include "PsdDocument.h"
#include "PsdNativeFile.h"
#include "PsdMallocAllocator.h"
#include "PsdSyncFileReader.h"
#include "PsdParseDocument.h"
#include "PsdParseLayerMaskSection.h"
#include "PsdParseImageResourcesSection.h"
#include "PsdParseImageDataSection.h"
#include "PsdLayer.h"
#include "PsdLayerMask.h"
#include "PsdBlendMode.h"
#include "PsdInterleave.h"
#include "PsdLayerCanvasCopy.h"
#include "Misc/Paths.h"

void FPsdReaderTool::ReadPsdLayers(const FString& FilePath)
{
    psd::MallocAllocator Allocator;
    psd::NativeFile File(&Allocator);

    const FString FullPath = FPaths::ConvertRelativePathToFull(FilePath);
    
    if (!File.OpenRead(*FullPath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open PSD file: %s"), *FullPath);
        return;
    }

    // 读取并验证文档头
    psd::SyncFileReader Reader(&File);
    psd::Document* Document = psd::ParseDocument(&Reader, &Allocator);
    if (!Document)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to parse PSD document header"));
        File.Close();
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("PSD Document: %ux%u, %u channels, %u bits/channel"),
        Document->width, Document->height,
        Document->channelCount, Document->bitsPerChannel);

    // 解析图层蒙版段
    psd::LayerMaskSection* LayerMask = psd::ParseLayerMaskSection(Document, &File, &Allocator);
    if (LayerMask)
    {
        UE_LOG(LogTemp, Log, TEXT("Found %u layers, has transparency: %s"),
            LayerMask->layerCount,
            LayerMask->hasTransparencyMask ? TEXT("Yes") : TEXT("No"));

        for (unsigned int i = 0; i < LayerMask->layerCount; ++i)
        {
            psd::Layer& Layer = LayerMask->layers[i];
            
            // 提取图层像素数据
            psd::ExtractLayer(Document, &File, &Allocator, &Layer);

            psd::blendmode::Enum BlendMode = psd::blendMode::KeyToEnum(Layer.blendModeKey);
            const TCHAR* LayerName = StringCast<const TCHAR>(Layer.name.c_str());

            UE_LOG(LogTemp, Log, TEXT("  Layer[%u]: '%s' | Rect(%d,%d,%d,%d) | Blend=%s | Opacity=%u%% | Visible=%s | Channels=%u"),
                i,
                LayerName,
                Layer.left, Layer.top, Layer.right, Layer.bottom,
                StringCast<const TCHAR>(psd::blendMode::ToString(BlendMode)).Get(),
                static_cast<uint32_t>(Layer.opacity) * 100 / 255,
                Layer.isVisible ? TEXT("Yes") : TEXT("No"),
                Layer.channelCount);
        }

        // 清理图层数据
        psd::DestroyLayerMaskSection(LayerMask, &Allocator);
    }

    // 解析图像资源段（获取 ICC Profile、缩略图等）
    psd::ImageResourcesSection* ImageResources = psd::ParseImageResourcesSection(Document, &File, &Allocator);
    if (ImageResources)
    {
        UE_LOG(LogTemp, Log, TEXT("ICC Profile: %s, EXIF: %s, Alpha Channels: %u"),
            ImageResources->iccProfile ? TEXT("Present") : TEXT("None"),
            ImageResources->exifData ? TEXT("Present") : TEXT("None"),
            ImageResources->alphaChannelCount);

        psd::DestroyImageResourcesSection(ImageResources, &Allocator);
    }

    // 清理
    psd::DestroyDocument(Document, &Allocator);
    File.Close();
}
```

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `GeometryMask` | 几何蒙版处理，用于支持矢量蒙版功能 |

### 模块依赖

根据各模块的 Build.cs 分析（省略 Core/CoreUObject/Engine 等标准模块）：

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 蒙版相关功能 |
| `PsdSDK` | 第三方 PSD 文件解析/导出库（内置于插件中） |

> **注意**：本插件目前仅支持 **Win64** 平台，所有三个模块都设置了 `PlatformAllowList: ["Win64"]`。

### 模块说明

| 模块名 | 类型 | 说明 |
|---|---|---|
| `PSDImporter` | Runtime | 运行时核心功能，PSD 文件的基础解析能力 |
| `PSDImporterCore` | Runtime | 核心数据结构和处理逻辑 |
| `PSDImporterEditor` | Editor | 编辑器集成，Content Browser 导入流程、资产工厂 |
| `PsdSDK` | External | Molecular Matters 的第三方 PSD 解析/导出库 |

## PsdSDK 第三方库概览

PsdSDK 是由 Molecular Matters GmbH 开发的 PSD 文件解析库（2-clause BSD License），内置于本插件中。它是本插件的核心依赖，提供了：

### 解析功能
- **文档头解析** (`ParseDocument`)：读取 PSD 文件的基本信息（尺寸、通道数、色彩模式）
- **图层蒙版段解析** (`ParseLayerMaskSection`)：解析所有图层及其蒙版
- **图像资源段解析** (`ParseImageResourcesSection`)：获取 ICC Profile、EXIF、缩略图、Alpha 通道信息
- **图像数据段解析** (`ParseImageDataSection`)：解析合并的图像数据

### 导出功能
- **创建导出文档** (`CreateExportDocument`)
- **添加/更新图层** (`AddLayer` / `UpdateLayer`)：支持 8/16/32 位数据
- **Alpha 通道管理** (`AddAlphaChannel` / `UpdateChannel`)
- **合并图像数据** (`UpdateMergedImage`)
- **写入 PSD 文件** (`WriteDocument`)

### 图像工具
- **平面↔交错转换**：`InterleaveRGB/RGBA`、`DeinterleaveRGB/RGBA`
- **RLE 压缩/解压**：`DecompressRle`、`CompressRle`
- **图层数据复制到画布**：`CopyLayerData`

### 抽象层
- **文件 I/O**：`File` 基类、`NativeFile`（Win/Mac/Linux 平台实现）、`SyncFileReader`/`SyncFileWriter`
- **内存分配**：`Allocator` 基类、`MallocAllocator`

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新 API |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托调用方式 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 静默 PVS-Studio 误报警告 |

### 维护评价

- **状态**：实验性插件，仍在活跃维护中
- **创建时间**：2025 年 4 月，约 1 年历史，属于较新的插件
- **近期活动**：最近一次更新在 2026 年 4 月，主要是编译适配（UE_LOG 迁移）和平台兼容性修复
- **稳定性**：更新内容以修复和适配为主，尚未有功能性扩展，表明代码趋于稳定但仍处于实验阶段
- **平台限制**：仅支持 Win64，尚未扩展到其他平台
- **推荐程度**：如果你的项目需要 PSD 直接导入功能且仅面向 Windows 平台，可以尝试使用。但作为实验性插件，**不建议在生产环境的正式项目中依赖**，需关注后续版本的 API 变化。建议通过源码编译方式验证是否满足需求后再做决策。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [PsdSDK 第三方库](https://www.molecular-matters.com/products_psd.html)（Molecular Matters 官网，库来源）
- 官方文档：暂无
- 测试用例：暂未发现独立测试文件