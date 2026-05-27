# PSD Importer

> *（.uplugin Description 为空）*

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（第三方 PSD SDK） |
| 模块 | `PSDImporterCore` (Runtime), `PSDImporter` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

该插件提供了将 Adobe Photoshop（PSD）文件直接导入 UE5 的能力。它封装了一个第三方 PSD 解析库（PsdSDK），能够：

- 解析 PSD 文件头信息（签名、版本、通道数、尺寸、色彩深度、色彩模式）
- 逐层读取图层数据，包括图层组（Group）、混合模式、不透明度、裁切关系、图层标志
- 读取图层的像素数据和蒙版数据（支持异步 `TFuture<FImage>`）
- 支持多种压缩格式（Raw、RLE、ZIP）
- 支持多种色彩模式（RGB、CMYK、Grayscale、Lab 等）

该插件目前为 **实验性** 状态，仅支持 **Win64** 平台，需要手动启用。它依赖 GeometryMask 插件。

## 使用场景

- 你在 Photoshop 中制作了 UI 布局图，希望直接导入 UE5 作为 UMG 控件的参考或素材
- 你需要从 PSD 文件中提取独立图层，用于动态合成或材质系统
- 美术团队需要将分层的 Photoshop 文件快速转换为 UE 可用的纹理资源

## 蓝图用法

该插件主要面向 C++ 使用者。公开的蓝图类型有限：

### 蓝图类型

| 类型 | 说明 | 来源 |
|---|---|---|
| `EPSDBlendMode` | PSD 混合模式枚举（BlueprintType），包含 Normal、Multiply、Screen 等 30+ 种模式 | `PSDFileData.h` |

插件的核心导入流程（`FPSDFileImporter::Import`）为纯 C++ API，不暴露 BlueprintCallable 节点。蓝图中可直接使用 `EPSDBlendMode` 枚举进行类型判断和参数传递。

## C++ 用法

### 头文件引入

```cpp
#include "PSDFileImport.h"
#include "PSDFileData.h"
#include "PSDFileRecord.h"
#include "PSDFileDocument.h"
```

### 基本用法

通过访客模式（Visitor Pattern）导入 PSD 文件并获取图层信息：

```cpp
// 来源: Public/PSDFileImport.h
#include "PSDFileImport.h"

// 1. 创建导入器实例
TSharedRef<UE::PSDImporter::FPSDFileImporter> Importer = 
    UE::PSDImporter::FPSDFileImporter::Make(TEXT("/Path/to/file.psd"));

// 2. 自定义访客以处理导入事件
class FMyImportVisitor : public UE::PSDImporter::FPSDFileImportVisitors
{
public:
    virtual void OnImportHeader(const FHeaderInputType& InHeader) override
    {
        // 获取 PSD 文件头信息：宽度、高度、通道数、色彩模式等
        UE_LOG(LogTemp, Log, TEXT("PSD Size: %d x %d, Channels: %d"),
            InHeader.Width, InHeader.Height, InHeader.NumChannels);
    }

    virtual void OnImportLayer(const FLayerInputType& InLayer, const FLayerInputType* InParentLayer,
        TFunction<TFuture<FImage>()> InReadLayerData, TFunction<TFuture<FImage>()> InReadMaskData) override
    {
        UE_LOG(LogTemp, Log, TEXT("Layer: %s, Blend: %d, Opacity: %d"),
            *InLayer.LayerName, (int32)InLayer.BlendMode, InLayer.Opacity);

        // 异步读取图层像素数据
        TFuture<FImage> LayerDataFuture = InReadLayerData();
        LayerDataFuture.Then([](TFuture<FImage> InFuture)
        {
            FImage Image = InFuture.Get();
            // 处理图层图像数据...
        });

        // 可选：读取蒙版数据
        TFuture<FImage> MaskDataFuture = InReadMaskData();
    }

    virtual void OnImportComplete() override
    {
        UE_LOG(LogTemp, Log, TEXT("PSD import complete!"));
    }
};

// 3. 执行导入
TSharedPtr<FMyImportVisitor> Visitor = MakeShared<FMyImportVisitor>();
UE::PSDImporter::FPSDFileImporterOptions Options;
Options.bResizeLayersToDocument = true; // 将图层尺寸调整为文档画布大小

bool bSuccess = Importer->Import(Visitor, Options);
```

*来源: `Public/PSDFileImport.h`*

### 进阶用法

结合图层记录与文档结构进行高级处理：

```cpp
#include "PSDFileDocument.h"
#include "PSDFileRecord.h"
#include "PSDFileData.h"

// 在 OnImportLayers 回调中获取完整图层树
virtual void OnImportLayers(const FLayersInputType& InLayers) override
{
    UE_LOG(LogTemp, Log, TEXT("Total layers: %d, Has transparency mask: %s"),
        InLayers.NumLayers, InLayers.bHasTransparencyMask ? TEXT("Yes") : TEXT("No"));

    // 遍历所有图层记录
    for (UE::PSDImporter::File::FPSDLayerRecord* Layer : InLayers.Layers)
    {
        // 检查图层类型
        if (Layer->bIsGroup)
        {
            UE_LOG(LogTemp, Log, TEXT("Group: %s"), *Layer->LayerName);
        }

        // 检查图层标志
        if (EnumHasAnyFlags(Layer->Flags, UE::PSDImporter::File::EPSDLayerFlags::Visible))
        {
            UE_LOG(LogTemp, Log, TEXT("Visible layer: %s"), *Layer->LayerName);
        }

        // 遍历通道信息
        for (UE::PSDImporter::File::FPSDChannelInformation* Channel : Layer->Channels)
        {
            // Channel->Id: 0=Red, 1=Green, 2=Blue, -1=Transparency, -2=UserMask, -3=BothMasks
            UE_LOG(LogTemp, Log, TEXT("  Channel %d, Length: %lld"), Channel->Id, Channel->Length);
        }
    }
}
```

*来源: `Public/PSDFileRecord.h`、`Public/PSDFileData.h`*

## Demo 示例

一个可编译的最小 PSD 导入示例（编辑器工具）：

```cpp
// MyPSDImportTool.h
#pragma once

#include "CoreMinimal.h"
#include "PSDFileImport.h"

class FMyPSDImportTool
{
public:
    void ImportPSDFile(const FString& InFilePath);

private:
    class FImportVisitor;
};
```

```cpp
// MyPSDImportTool.cpp
#include "MyPSDImportTool.h"
#include "PSDFileRecord.h"
#include "PSDFileData.h"

class FMyPSDImportTool::FImportVisitor : public UE::PSDImporter::FPSDFileImportVisitors
{
public:
    virtual void OnImportHeader(const FHeaderInputType& InHeader) override
    {
        UE_LOG(LogTemp, Display, TEXT("Document: %dx%d, %d-bit, %d channels"),
            InHeader.Width, InHeader.Height, InHeader.Depth, InHeader.NumChannels);
    }

    virtual void OnImportLayer(const FLayerInputType& InLayer, const FLayerInputType* InParentLayer,
        TFunction<TFuture<FImage>()> InReadLayerData, TFunction<TFuture<FImage>()> InReadMaskData) override
    {
        UE_LOG(LogTemp, Display, TEXT("Layer[%d]: %s (%s, opacity=%d)"),
            InLayer.Index, *InLayer.LayerName,
            LexToString(InLayer.BlendMode), InLayer.Opacity);

        // 异步读取并处理图层数据
        InReadLayerData().Then([](TFuture<FImage> Future)
        {
            if (FImage Image = Future.Get(); Image.SizeX > 0 && Image.SizeY > 0)
            {
                // Image.RawData 中包含原始像素数据
                UE_LOG(LogTemp, Display, TEXT("  Layer image: %dx%d"), Image.SizeX, Image.SizeY);
            }
        });
    }

    virtual void OnImportComplete() override
    {
        UE_LOG(LogTemp, Display, TEXT("Import complete!"));
    }
};

void FMyPSDImportTool::ImportPSDFile(const FString& InFilePath)
{
    TSharedRef<UE::PSDImporter::FPSDFileImporter> Importer =
        UE::PSDImporter::FPSDFileImporter::Make(InFilePath);

    auto Visitor = MakeShared<FImportVisitor>();
    UE::PSDImporter::FPSDFileImporterOptions Options;
    Options.bResizeLayersToDocument = false;

    if (!Importer->Import(Visitor, Options))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import PSD: %s"), *InFilePath);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PsdSDK` | 第三方 PSD 文件解析库，提供底层的 PSD 文件格式读取能力 |
| `GeometryMask` | 几何蒙版插件（插件级依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换，重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复委托 API 迁移导致的注册缺失问题 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制静态分析工具的误报警告 |

### 维护评价

- **创建时间**：2025-04-28，约 1 年前，属于较新的插件
- **实验性标记**：`IsExperimentalVersion=true` 且 `Installed=false`，属于 UE5 实验性功能
- **平台限制**：仅支持 Win64
- **更新频率**：近期有编译兼容性维护（日志宏迁移、委托 API 迁移），但没有功能性更新
- **已知限制**：不支持色彩模式数据（ColorModeData）、图像资源（ImageResources）、像素数据（ImageData）的解析，仅支持图层与蒙版信息

**综合评价**：该插件仍处于实验阶段，API 可能在未来版本中发生变化。核心导入流程设计合理（访客模式 + 异步读取），适合需要在编辑器中自动化处理 PSD 文件的场景。建议关注后续版本的 API 变化，暂不建议用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [核心导入 API](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/PSDImporter/Source/PSDImporterCore/Public/PSDFileImport.h)
- [PSD 文件数据结构](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/PSDImporter/Source/PSDImporterCore/Public/PSDFileData.h)
- [PSD 图层记录](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/PSDImporter/Source/PSDImporterCore/Public/PSDFileRecord.h)
- [PSD 文件格式官方参考](https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PSDFileFormats.htm)