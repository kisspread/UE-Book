# PSD Importer

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD 文件导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（导入设置、图层数据结构、第三方库） |
| 模块 | `PSDImporterEditor` (Editor), `PSDImporter` (Runtime), `PSDImporterCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter) | |

---

## 用途

**PSD Importer** 是一个实验性插件，用于将 Adobe Photoshop 的 `.psd` 文件直接导入到 Unreal Engine 中。它使用第三方 Psd SDK 解析 PSD 文件格式，支持读取图层、蒙版、通道数据、混合模式等结构，并提供 C++ 接口供编辑器或运行时使用。

该插件解决了以下问题：
- 避免手动将 PSD 文件导出为中间格式（如 PNG/TGA），再逐层导入的繁琐流程。
- 保持图层结构、透明度、混合模式等元信息，方便在 UE 中重建复杂的合成效果。
- 支持 8/16/32 位通道深度的 PSD 文件。

**核心模块 `PSDImporterCore` 负责底层的文件解析与数据抽象**，包括：
- 读取 PSD 文件头、颜色模式、压缩方式。
- 解码 RLE/ZIP 压缩的像素数据。
- 构建图层和蒙版的数据结构（`FPSDLayerRecord`、`FPSDImageData` 等）。
- 提供访问者模式（`FPSDFileImportVisitors`）将解析过程暴露给上层。

## 使用场景

- 你在制作需要复杂图层合成的 2D UI 或纹理 → 可直接导入 PSD 文件，保留图层顺序和混合效果。
- 你需要将设计师的 Photoshop 设计稿快速转化为 UE 中的材质/贴图 → 通过访问者模式逐层处理。
- 你希望实现自定义的 PSD 导入流程（如仅导入特定图层） → 基于 `FPSDFileImporter` 编写导入器。

## 蓝图用法

由于 `PSDImporterCore` 的公开 API 主要面向 C++，且目前没有暴露 `BlueprintCallable` 函数，因此蓝图中无法直接使用。编辑器的导入动作通常通过 `PSDImporterEditor` 模块的资产工厂触发，但具体节点引擎版本可能提供。

**当前无直接可用的蓝图节点**。如需实现运行时 PSD 加载，需通过 C++ 扩展。

## C++ 用法

### 头文件引入

```cpp
#include "PSDFileImport.h"
#include "PSDFileData.h"
```

### 基本用法

创建一个简单的导入器，解析 PSD 文件并输出图层信息。

```cpp
// 文件路径：Source/PSDImporterCore/Private/Readers/DocumentReader.cpp (示例用途)

#include "PSDFileImport.h"
#include "PSDFileData.h"
#include "PSDFileDocument.h"
#include "PSDFileRecord.h"

using namespace UE::PSDImporter;

// 定义访问者，接收导入过程中的事件
class FMyImportVisitors : public FPSDFileImportVisitors
{
public:
    virtual void OnImportHeader(const FHeaderInputType& InHeader) override
    {
        // 文件头信息：宽、高、通道数、位深等
        UE_LOG(LogTemp, Log, TEXT("PSD Header: %dx%d, %d channels, %d bits"),
               InHeader.Width, InHeader.Height, InHeader.NumChannels, InHeader.Depth);
    }

    virtual void OnImportLayers(const FLayersInputType& Layers) override
    {
        // 图层与蒙版信息整体回调
        UE_LOG(LogTemp, Log, TEXT("Layer & mask info received."));
    }

    virtual void OnImportLayer(
        const FLayerInputType& InLayer,
        const FLayerInputType* InParentLayer,
        TFunction<TFuture<FImage>()> InReadLayerData,
        TFunction<TFuture<FImage>()> InReadMaskData) override
    {
        // 每个图层的回调，可异步获取像素数据
        UE_LOG(LogTemp, Log, TEXT("Layer: %s (blend mode: %d, opacity: %d)"),
               *InLayer.LayerName, (int32)InLayer.BlendMode, InLayer.Opacity);

        // 如果需要像素数据，调用 InReadLayerData() 获取 FImage
        TFuture<FImage> ImageFuture = InReadLayerData();
        // 注意：此处应在异步线程中等待，或向外部传递 Future
    }
};

void RunImport(const FString& PSDFilePath)
{
    // 创建导入器（自动管理生命周期）
    TSharedRef<FPSDFileImporter> Importer = FPSDFileImporter::Make(PSDFilePath);

    // 设置选项
    FPSDFileImporterOptions Options;
    Options.bResizeLayersToDocument = false;

    // 创建访问者并执行导入
    TSharedPtr<FPSDFileImportVisitors> Visitors = MakeShared<FMyImportVisitors>();
    bool bSuccess = Importer->Import(Visitors, Options);

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("PSD import completed successfully."));
    }
}
```

### 进阶用法

#### 手动解码 RLE 行数据

`PSDFileReader.h` 中暴露了底层解码函数，可在解析链路外使用：

```cpp
#include "PSDFileReader.h"

// 解码一行 RLE 压缩数据
bool DecodeRow(const uint8* InSource, uint16 InSourceBytes,
               uint8* OutScanline, uint64 OutScanlineSize)
{
    return UE::PSDImporter::Internal::DecodeRLERow(
        InSource, InSourceBytes, OutScanline, OutScanlineSize);
}
```

#### 扩展访问者以收集图层列表

```cpp
class FLayerCollector : public FPSDFileImportVisitors
{
public:
    TArray<File::FPSDLayerRecord> Layers;

    virtual void OnImportLayer(
        const FLayerInputType& InLayer,
        const FLayerInputType* InParentLayer,
        TFunction<TFuture<FImage>()> InReadLayerData,
        TFunction<TFuture<FImage>()> InReadMaskData) override
    {
        Layers.Add(InLayer);
    }
};
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何从 C++ 控制台程序（或游戏模块）中导入 PSD 文件并输出图层名称。

### MyPSDImportDemo.h

```cpp
#pragma once

#include "PSDFileImport.h"

class FMyPSDImportDemo
{
public:
    static bool Run(const FString& FilePath);
};
```

### MyPSDImportDemo.cpp

```cpp
#include "MyPSDImportDemo.h"
#include "PSDFileData.h"
#include "PSDFileDocument.h"
#include "PSDFileRecord.h"
#include "PSDFileImport.h"

// 自定义访问者：打印每个图层信息
class FPrintLayerVisitor : public UE::PSDImporter::FPSDFileImportVisitors
{
public:
    virtual void OnImportHeader(const FHeaderInputType& InHeader) override
    {
        UE_LOG(LogTemp, Log, TEXT("Header: %dx%d, depth %d"),
               InHeader.Width, InHeader.Height, InHeader.Depth);
    }

    virtual void OnImportLayer(
        const FLayerInputType& InLayer,
        const FLayerInputType* InParentLayer,
        TFunction<TFuture<FImage>()> InReadLayerData,
        TFunction<TFuture<FImage>()> InReadMaskData) override
    {
        UE_LOG(LogTemp, Log, TEXT("Layer[%d]: %s, blend mode = %d"),
               InLayer.Index, *InLayer.LayerName, (int32)InLayer.BlendMode);
    }
};

bool FMyPSDImportDemo::Run(const FString& FilePath)
{
    TSharedRef<UE::PSDImporter::FPSDFileImporter> Importer =
        UE::PSDImporter::FPSDFileImporter::Make(FilePath);
    
    TSharedPtr<FPrintLayerVisitor> Visitor = MakeShared<FPrintLayerVisitor>();
    UE::PSDImporter::FPSDFileImporterOptions Options;
    
    return Importer->Import(Visitor, Options);
}
```

使用方式：

```cpp
#include "MyPSDImportDemo.h"

void SomeFunction()
{
    FMyPSDImportDemo::Run(TEXT("C:/MyDesign.psd"));
}
```

## 模块依赖

根据源码中的 `#include` 及第三方库引用，`PSDImporterCore` 的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `ImageCore` | 提供 `FImage` 结构，用于传递像素数据 |
| `GeometryMask` | 插件依赖（`Plugins` 中声明），可能用于几何体蒙版相关操作 |
| `PsdSDK` | 第三方库，封装为 `ThirdParty/PsdSDK`，用于底层 PSD 文件格式解析 |

**常见依赖省略**：Core、CoreUObject、Engine、Slate、SlateCore 等标准模块不列出。

## 维护状态

### 近期更新

- 2025-07-15 `bafe5da2` Silence incorrect V1051 warnings
- 2025-06-05 `00f9a7c0` Add Windows Arm64 libraries for PSD SDK + add build helper batch file
- 2025-05-15 `41b521d3` PSD Importer: Importing 16 and 32-bit PSDs now works correctly.
- 2025-05-15 `708e8190` PSD Importer: Hidden Quad Actor property AdjustForViewDistance because it is not user friendly.
- 2025-05-15 `c35a5c0e` PSD Importer: Importing layers with special characters now sanitizes the layer name.

### 维护评价

该插件于 2025 年 5 月创建，至今约 5 个月，处于早期实验阶段。最近更新主要为修复警告、添加平台支持库（Arm64）、以及修复 16/32 位深度导入。更新频率较高（每月有提交），说明内部有持续维护。但由于仍标记为实验性，API 和行为可能不稳定，不建议在生产管线中依赖。已知限制：仅支持 Win64 平台，尚无蓝图接口。推荐追踪后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（搜索 "PSD Importer"）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter/Tests)（如果存在）