# PSD Importer

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（第三方SDK库） |
| 模块 | `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PSDImporterEditor` (Editor), `PsdSDK` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 是一个用于将 Adobe Photoshop PSD 文件导入到 Unreal Engine 5 中的实验性插件。它解决了以下核心问题：

1. **PSD 文件解析**：提供完整的 PSD 文件格式解析能力，支持解析文档头、颜色模式数据、图像资源、图层蒙版信息和图像数据等所有主要节段
2. **图层信息提取**：能够提取 PSD 文件中的图层结构，包括图层位置、尺寸、混合模式、不透明度、可见性、图层蒙版和矢量蒙版等属性
3. **多通道图像处理**：支持 8 位、16 位和 32 位（浮点）色深的图像数据，支持 RGB/RGBA 平面数据与交织数据的相互转换
4. **PSD 文件导出**：除了导入功能外，还提供创建和导出 PSD 文件的能力，支持图层、Alpha 通道、ICC 配置文件、EXIF 数据和 JPEG 缩略图

该插件集成了 Molecular Matters 的 PsdSDK 第三方库，提供了跨平台的 PSD 文件读写支持，目前仅支持 Win64 平台。

## 使用场景

- **UI 设计工作流**：美术在 Photoshop 中设计 UI 布局，直接导入 PSD 保留图层结构用于 UMG 界面构建
- **纹理资产管理**：将包含多个图层的 PSD 素材导入引擎，保留原始图层信息用于后续处理
- **动态 UI 系统**：利用 PSD 的图层结构实现可配置的动态 UI 系统
- **内容管线集成**：在自动化内容管线中批量导入 PSD 资源
- **逆向导出需求**：从引擎导出 PSD 文件用于与美术团队协作

## 蓝图用法

由于当前为实验性插件且主要面向编辑器导入流程，蓝图 API 较少。该插件主要通过编辑器资产导入流程工作。

### 核心功能

| 功能 | 说明 |
|---|---|
| 文件导入 | 通过 Content Browser 的 Import 功能导入 .psd 文件 |
| 图层解析 | 自动解析 PSD 文件中的图层结构和属性 |
| 纹理生成 | 将 PSD 图层数据转换为 UE5 纹理资产 |

## C++ 用法

PSD Importer 提供了丰富的 C++ API 用于直接操作 PSD 文件。

### 头文件引入

```cpp
// PSD 解析核心
#include "PsdParseLayerMaskSection.h"
#include "PsdParseImageResourcesSection.h"
#include "PsdParseImageDataSection.h"

// 数据类型
#include "PsdDocument.h"
#include "PsdLayer.h"
#include "PsdChannel.h"

// 文件操作
#include "PsdFile.h"
#include "PsdNativeFile.h"
#include "PsdSyncFileReader.h"

// 导出功能
#include "PsdExport.h"
```

### 基本用法 - 解析 PSD 文件

以下代码展示了如何解析 PSD 文件并提取图层信息：

```cpp
// 来源：PsdParseLayerMaskSection.h, PsdParseImageResourcesSection.h

// 创建分配器（使用默认或自定义分配器）
psd::Allocator* allocator = /* 初始化分配器 */;

// 创建文件对象并打开 PSD 文件
psd::NativeFile file(allocator);
bool bOpened = file.OpenRead(TEXT("path/to/file.psd"));

if (bOpened)
{
    // 解析文档头（获取文档基本信息）
    psd::Document* document = /* 解析文档头 */;
    
    // 解析图层蒙版节段
    psd::LayerMaskSection* layerMaskSection = psd::ParseLayerMaskSection(document, &file, allocator);
    
    // 遍历所有图层
    for (unsigned int i = 0; i < layerMaskSection->layerCount; ++i)
    {
        psd::Layer& layer = layerMaskSection->layers[i];
        
        // 获取图层名称
        const char* layerName = layer.name.c_str();
        
        // 获取图层边界
        int32_t top = layer.top;
        int32_t left = layer.left;
        int32_t bottom = layer.bottom;
        int32_t right = layer.right;
        
        // 获取图层属性
        uint8_t opacity = layer.opacity;  // 0-255
        bool isVisible = layer.isVisible;
        uint32_t blendMode = layer.blendModeKey;
        
        // 提取图层数据（可以多线程并行）
        psd::ExtractLayer(document, &file, allocator, &layer);
        
        // 访问通道数据
        for (unsigned int ch = 0; ch < layer.channelCount; ++ch)
        {
            psd::Channel& channel = layer.channels[ch];
            // channel.data 包含像素数据
        }
    }
    
    // 清理资源
    psd::DestroyLayerMaskSection(layerMaskSection, allocator);
    file.Close();
}
```

### 进阶用法 - 导出 PSD 文件

```cpp
// 来源：PsdExport.h, PsdExportDocument.h

psd::Allocator* allocator = /* 初始化分配器 */;

// 创建导出文档
psd::ExportDocument* exportDoc = psd::CreateExportDocument(
    allocator,
    1920,    // canvasWidth
    1080,    // canvasHeight
    8,       // bitsPerChannel
    psd::exportColorMode::RGB
);

// 添加元数据
psd::AddMetaData(exportDoc, allocator, "title", "My PSD Export");
psd::AddMetaData(exportDoc, allocator, "author", "UE5");

// 添加图层
unsigned int layerIndex = psd::AddLayer(exportDoc, allocator, "Background");

// 准备图像数据（8位平面数据）
uint8_t* rData = new uint8_t[1920 * 1080];
uint8_t* gData = new uint8_t[1920 * 1080];
uint8_t* bData = new uint8_t[1920 * 1080];

// 填充图像数据...
// 更新图层数据（支持 8/16/32 位）
psd::UpdateLayer(exportDoc, allocator, layerIndex, 
    psd::exportChannel::R, 
    0, 0, 1920, 1080,  // left, top, right, bottom
    rData, psd::compressionType::RLE);

// 添加 Alpha 通道
unsigned int alphaIndex = psd::AddAlphaChannel(
    exportDoc, allocator, "Alpha 1",
    65535, 65535, 65535, 65535,  // RGBA color
    100,                          // opacity
    psd::AlphaChannel::Mode::ALPHA
);

// 设置 ICC 配置文件
// psd::SetICCProfile(exportDoc, allocator, profileData, profileSize);

// 写入文件
psd::NativeFile file(allocator);
file.OpenWrite(TEXT("output.psd"));
psd::WriteDocument(exportDoc, allocator, &file);
file.Close();

// 清理
psd::DestroyExportDocument(exportDoc, allocator);
delete[] rData;
delete[] gData;
delete[] bData;
```

### 图像数据处理工具

```cpp
// 来源：PsdInterleave.h, PsdLayerCanvasCopy.h, PsdDecompressRle.h

// 将平面 RGB 数据转换为交织 RGBA 数据
uint8_t* srcR = /* R通道数据 */;
uint8_t* srcG = /* G通道数据 */;
uint8_t* srcB = /* B通道数据 */;
uint8_t* destRGBA = new uint8_t[width * height * 4];

// 必须 16 字节对齐
psd::imageUtil::InterleaveRGB(srcR, srcG, srcB, 255, destRGBA, width, height);

// 或带 Alpha 通道
uint8_t* srcA = /* A通道数据 */;
psd::imageUtil::InterleaveRGBA(srcR, srcG, srcB, srcA, destRGBA, width, height);

// 反向转换：交织到平面
psd::imageUtil::DeinterleaveRGBA(destRGBA, srcR, srcG, srcB, srcA, width, height);

// RLE 解压缩
uint8_t* compressedData = /* RLE压缩数据 */;
uint8_t* decompressedData = new uint8_t[uncompressedSize];
psd::imageUtil::DecompressRle(compressedData, compressedSize, 
    decompressedData, uncompressedSize);

// 将图层数据复制到画布（处理图层与画布尺寸不一致的情况）
uint8_t* layerData = /* 图层像素数据 */;
uint8_t* canvasData = /* 画布缓冲区 */;
psd::imageUtil::CopyLayerData(layerData, canvasData, 
    layerLeft, layerTop, layerRight, layerBottom,
    canvasWidth, canvasHeight);
```

### 同步文件读取

```cpp
// 来源：PsdSyncFileReader.h, PsdSyncFileUtil.h

psd::NativeFile file(allocator);
file.OpenRead(TEXT("file.psd"));

// 使用同步读取器简化顺序读取
psd::SyncFileReader reader(&file);

// 读取基本类型
uint32_t signature = psd::fileUtil::ReadFromFile<uint32_t>(reader);
uint16_t version = psd::fileUtil::ReadFromFileBE<uint16_t>(reader);  // 大端序

// 跳过字节
reader.Skip(6);

// 设置读取位置
reader.SetPosition(1024);
uint64_t pos = reader.GetCurrentPosition();
```

## Demo 示例

一个完整的最小示例，展示如何解析 PSD 文件并遍历所有图层：

```cpp
// PSDImporterDemo.h
#pragma once

#include "CoreMinimal.h"

class FPSDImporterDemo
{
public:
    static void ParsePSDFile(const FString& FilePath);
    static void ListAllLayers(const FString& FilePath);
};
```

```cpp
// PSDImporterDemo.cpp
#include "PSDImporterDemo.h"
#include "PsdAllocator.h"
#include "PsdNativeFile.h"
#include "PsdSyncFileReader.h"
#include "PsdDocument.h"
#include "PsdLayer.h"
#include "PsdLayerMaskSection.h"
#include "PsdParseLayerMaskSection.h"
#include "PsdSyncFileUtil.h"
#include "PsdKey.h"

// 默认内存分配器实现
class FDefaultPSDAllocator : public psd::Allocator
{
private:
    virtual void* DoAllocate(size_t Size, size_t Alignment) override
    {
        return FMemory::Malloc(Size, Alignment);
    }
    
    virtual void DoFree(void* Ptr) override
    {
        FMemory::Free(Ptr);
    }
};

void FPSDImporterDemo::ParsePSDFile(const FString& FilePath)
{
    FDefaultPSDAllocator Allocator;
    
    // 打开文件
    psd::NativeFile File(&Allocator);
    if (!File.OpenRead(*FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open PSD file: %s"), *FilePath);
        return;
    }
    
    // 创建同步读取器
    psd::SyncFileReader Reader(&File);
    
    // 读取并验证签名
    uint32_t Signature = psd::fileUtil::ReadFromFileBE<uint32_t>(Reader);
    if (Signature != psd::util::Key<'8', 'B', 'P', 'S'>::VALUE)
    {
        UE_LOG(LogTemp, Error, TEXT("Invalid PSD file signature"));
        File.Close();
        return;
    }
    
    // 读取版本
    uint16_t Version = psd::fileUtil::ReadFromFileBE<uint16_t>(Reader);
    UE_LOG(LogTemp, Log, TEXT("PSD Version: %d"), Version);
    
    // 跳过保留字节
    Reader.Skip(6);
    
    // 读取通道数
    uint16_t ChannelCount = psd::fileUtil::ReadFromFileBE<uint16_t>(Reader);
    
    // 读取尺寸
    uint32_t Height = psd::fileUtil::ReadFromFileBE<uint32_t>(Reader);
    uint32_t Width = psd::fileUtil::ReadFromFileBE<uint32_t>(Reader);
    uint16_t BitsPerChannel = psd::fileUtil::ReadFromFileBE<uint16_t>(Reader);
    uint16_t ColorMode = psd::fileUtil::ReadFromFileBE<uint16_t>(Reader);
    
    UE_LOG(LogTemp, Log, TEXT("PSD Size: %dx%d, Channels: %d, Bits: %d, Mode: %d"),
        Width, Height, ChannelCount, BitsPerChannel, ColorMode);
    
    File.Close();
}

void FPSDImporterDemo::ListAllLayers(const FString& FilePath)
{
    FDefaultPSDAllocator Allocator;
    
    psd::NativeFile File(&Allocator);
    if (!File.OpenRead(*FilePath))
    {
        return;
    }
    
    // 注意：实际使用中需要先解析文档头获取 Section 信息
    // 这里简化演示图层遍历逻辑
    
    psd::Document Document;
    // Document 需要从文件头部解析填入...
    
    // 解析图层蒙版节段
    psd::LayerMaskSection* LayerSection = psd::ParseLayerMaskSection(&Document, &File, &Allocator);
    
    if (LayerSection)
    {
        UE_LOG(LogTemp, Log, TEXT("Found %d layers"), LayerSection->layerCount);
        
        for (uint32_t i = 0; i < LayerSection->layerCount; ++i)
        {
            const psd::Layer& Layer = LayerSection->layers[i];
            
            // 输出图层信息
            UE_LOG(LogTemp, Log, TEXT("Layer %d: %hs"), i, Layer.name.c_str());
            UE_LOG(LogTemp, Log, TEXT("  Bounds: (%d,%d) - (%d,%d)"), 
                Layer.left, Layer.top, Layer.right, Layer.bottom);
            UE_LOG(LogTemp, Log, TEXT("  Opacity: %d, Visible: %s"),
                Layer.opacity, Layer.isVisible ? TEXT("Yes") : TEXT("No"));
            
            // 解析图层数据
            psd::ExtractLayer(&Document, &File, &Allocator, &Layer);
        }
        
        // 清理
        psd::DestroyLayerMaskSection(LayerSection, &Allocator);
    }
    
    File.Close();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 几何遮罩功能，用于处理 PSD 中的蒙版数据 |
| 无特殊依赖（仅标准 Core/Engine 等） | PsdSDK 是独立的第三方库，不依赖 UE 模块 |

**模块内部依赖关系**：
- `PSDImporterCore` (Runtime) - 核心解析逻辑
- `PSDImporter` (Runtime) - 运行时功能
- `PSDImporterEditor` (Editor) - 编辑器集成
- `PsdSDK` (External) - 第三方 PSD 解析库，提供底层文件格式支持

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 迁移日志宏到新版本格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace | 修复错误的查找替换后重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复委托获取方式以解决注册缺失问题 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 消除错误的 V1051 警告 |

### 维护评价

**评级：实验性/开发中**

- **创建时间**：2025 年 4 月，相对年轻的插件
- **最近更新频率**：2026 年有多次更新，主要是编译修复和 API 迁移
- **维护状态**：活跃维护中，持续进行代码改进
- **实验性标识**：`IsExperimentalVersion=true`，API 可能发生变化
- **平台限制**：仅支持 Win64 平台
- **依赖插件**：依赖 GeometryMask 插件

**使用建议**：
1. 该插件为实验性功能，不建议在生产环境关键路径使用
2. API 可能在后续版本中发生变化
3. 仅支持 Windows 64 位平台
4. 如需稳定版本，等待插件移出 Experimental 目录
5. 适合用于原型开发和工作流验证

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [PsdSDK 第三方库文档](Includes/PsdDocumentation.h) - 详细的 SDK 模块文档（查看源码内文档注释）
- PSD 文件格式规范参考 - Adobe 官方 Photoshop File Formats Specification