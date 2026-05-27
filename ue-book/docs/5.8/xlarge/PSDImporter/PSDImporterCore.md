# PSD Importer

| 属性 | 值 |
|---|---|
| 中文名 | PSD导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板等） |
| 模块 | `PSDImporterCore` (Runtime), `PSDImporter` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途
该插件提供了一个完整的 Photoshop (.psd) 文件解析与导入流程。其核心功能是解析 PSD 文件的二进制结构，提取图层信息（如边界、透明度、混合模式）、通道数据以及遮罩信息，并将其转换为 UE5 可使用的 `FImage` 数据和结构化数据 (`FPSDDocument`)。它解决了在游戏开发或实时应用中，需要直接、准确地导入美术在 Photoshop 中制作的带有复杂图层和混合模式的 UI 或 2D 资源的需求，避免了手动切图和导出带来的信息丢失和工作流冗余。

## 使用场景
- **UI 资产制作**：美术在 Photoshop 中设计复杂的、带有透明度、混合模式（如正片叠底、滤色）和图层分组的游戏 UI 界面，然后通过此插件直接导入到 UE5 中，保留完整的图层结构和视觉属性，供程序员或策划在引擎内进一步调整和使用。
- **2D 游戏资源集成**：将 Photoshop 中绘制的带有遮罩、特效图层的 2D 角色或场景资源导入引擎，利用其解析出的遮罩数据（`FPSDLayerMaskData`）在引擎中实现动态效果。
- **自动化资产处理流程**：在编辑器工具或自动化脚本中，利用此插件的 C++ API 批量导入 PSD 文件，并根据图层名称、混合模式等信息自动进行资产分类、材质创建或蓝图生成。

## 蓝图用法
当前模块 (`PSDImporterCore`) 主要为底层运行时核心，不直接暴露蓝图节点。PSD 文件的导入和图层数据的获取主要通过 C++ 接口 (`FPSDFileImporter`) 和访问者模式 (`FPSDFileImportVisitors`) 在编辑器模块 (`PSDImporterEditor`) 或用户代码中实现。蓝图的可视化使用可能存在于 `PSDImporterEditor` 模块提供的编辑器工具中。

## C++ 用法

### 头文件引入
```cpp
#include "PSDFileImport.h"
#include "PSDFileData.h"
```

### 基本用法
使用 `FPSDFileImporter` 异步导入 PSD 文件，并通过 `FPSDFileImportVisitors` 回调接收解析出的图层和数据。
```cpp
// 来自 Public/PSDFileImport.h
using namespace UE::PSDImporter;

// 1. 创建导入器实例
TSharedRef<FPSDFileImporter> Importer = FPSDFileImporter::Make(TEXT("C:/Path/To/Your/File.psd"));

// 2. 定义访问者回调
class FMyImportVisitor : public FPSDFileImportVisitors
{
public:
    virtual void OnImportHeader(const FHeaderInputType& InHeader) override
    {
        // 处理文件头信息，例如获取图片尺寸
        UE_LOG(LogTemp, Log, TEXT("PSD Size: %d x %d"), InHeader.Width, InHeader.Height);
    }

    virtual void OnImportLayer(const FLayerInputType& InLayer, const FLayerInputType* InParentLayer,
        TFunction<TFuture<FImage>()> InReadLayerData, TFunction<TFuture<FImage>()> InReadMaskData) override
    {
        // 对每个图层进行处理
        UE_LOG(LogTemp, Log, TEXT("Layer: %s, BlendMode: %s"), *InLayer.LayerName, *LexToString(InLayer.BlendMode));
        
        // 异步读取图层像素数据
        InReadLayerData().Then([](TFuture<FImage> Future)
        {
            if (Future.IsValid() && !Future.HasError())
            {
                const FImage& LayerImage = Future.Get();
                // 处理图层图像数据 (LayerImage)
            }
        });
    }

    virtual void OnImportComplete() override
    {
        // 导入流程完成
        UE_LOG(LogTemp, Log, TEXT("PSD Import Completed."));
    }
};

// 3. 设置选项并开始导入
FPSDFileImporterOptions Options;
Options.bResizeLayersToDocument = true; // 将图层大小调整为画布大小

TSharedPtr<FMyImportVisitor> Visitor = MakeShared<FMyImportVisitor>();
Importer->Import(Visitor, Options);
```

### 进阶用法
结合 `PSDFileData.h` 中的结构体进行更精细的操作，例如根据图层名称和混合模式过滤图层，或处理特定的通道数据。
```cpp
// 在 OnImportLayer 回调中
virtual void OnImportLayer(const FLayerInputType& InLayer, const FLayerInputType* InParentLayer,
    TFunction<TFuture<FImage>()> InReadLayerData, TFunction<TFuture<FImage>()> InReadMaskData) override
{
    // 只处理名称包含“Background”且混合模式为“Normal”的图层
    if (InLayer.LayerName.Contains(TEXT("Background")) && InLayer.BlendMode == EPSDBlendMode::Normal)
    {
        // 读取图层数据
        InReadLayerData().Then([this, InLayer](TFuture<FImage> Future) 
        {
            // ... 处理数据
        });
        
        // 如果有遮罩数据，也进行读取
        if (InLayer.MaskBounds.Area() > 0)
        {
            InReadMaskData().Then([this, InLayer](TFuture<FImage> Future)
            {
                // ... 处理遮罩数据
            });
        }
    }
}
```

## Demo 示例

### FPSDDemoImporter.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "PSDFileImport.h"

class FPSDDemoImporter
{
public:
    void ImportDemoPSD(const FString& InFilePath);

private:
    class FDemoVisitor : public UE::PSDImporter::FPSDFileImportVisitors
    {
    public:
        virtual void OnImportHeader(const FHeaderInputType& InHeader) override;
        virtual void OnImportLayer(const FLayerInputType& InLayer, const FLayerInputType* InParentLayer,
            TFunction<TFuture<FImage>()> InReadLayerData, TFunction<TFuture<FImage>()> InReadMaskData) override;
        virtual void OnImportComplete() override;
    };
};
```

### FPSDDemoImporter.cpp
```cpp
#include "FPSDDemoImporter.h"
#include "PSDFileData.h"

void FPSDDemoImporter::ImportDemoPSD(const FString& InFilePath)
{
    using namespace UE::PSDImporter;
    
    TSharedRef<FPSDFileImporter> Importer = FPSDFileImporter::Make(InFilePath);
    TSharedPtr<FDemoVisitor> Visitor = MakeShared<FDemoVisitor>();
    
    FPSDFileImporterOptions Options;
    Options.bResizeLayersToDocument = false;
    
    Importer->Import(Visitor, Options);
}

void FPSDDemoImporter::FDemoVisitor::OnImportHeader(const FHeaderInputType& InHeader)
{
    UE_LOG(LogTemp, Display, TEXT("Demo - PSD Header: Width=%d, Height=%d, Channels=%d, Mode=%s"),
        InHeader.Width, InHeader.Height, InHeader.NumChannels, 
        UE::PSDImporter::File::LexToString(InHeader.Mode));
}

void FPSDDemoImporter::FDemoVisitor::OnImportLayer(const FLayerInputType& InLayer, const FLayerInputType* InParentLayer,
    TFunction<TFuture<FImage>()> InReadLayerData, TFunction<TFuture<FImage>()> InReadMaskData)
{
    UE_LOG(LogTemp, Display, TEXT("Demo - Layer: '%s' [Bounds: (%d,%d) - (%d,%d)] Blend: %s, Opacity: %d"),
        *InLayer.LayerName,
        InLayer.Bounds.Min.X, InLayer.Bounds.Min.Y,
        InLayer.Bounds.Max.X, InLayer.Bounds.Max.Y,
        *LexToString(InLayer.BlendMode), static_cast<int32>(InLayer.Opacity));
        
    // 异步读取并打印图层数据大小
    InReadLayerData().Then([](TFuture<FImage> Future)
    {
        if (Future.IsValid())
        {
            const FImage& Image = Future.Get();
            UE_LOG(LogTemp, Display, TEXT("Demo - Layer pixel data size: %d bytes"), Image.GetRawDataSize());
        }
    });
}

void FPSDDemoImporter::FDemoVisitor::OnImportComplete()
{
    UE_LOG(LogTemp, Display, TEXT("Demo - PSD import demo finished."));
}
```

## 模块依赖
此插件依赖于一个外部的、专有的 PSD 解析库。

| 模块 | 用途 |
|---|---|
| `PsdSDK` (External) | 提供底层的 PSD 文件二进制解析能力。该模块位于 `Source/ThirdParty/PsdSDK/` 目录下，是本插件功能的基础。 |
| `GeometryMask` | 依赖于 `GeometryMask` 插件，可能用于处理或生成基于图层的几何遮罩。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，可能是为了适配新的日志系统或统一格式。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次提交中错误的查找替换操作，进行了二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的某个变更 (CL51314860)。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修正了引擎初始化委托的使用方式，从属性改为获取函数，以解决注册缺失问题。 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 禁用了一些不正确的静态分析 (V1051) 警告。 |

### 维护评价
该插件目前处于 **实验性** 阶段 (`IsExperimentalVersion: true`, `Installed: false`)。它创建于 2025 年初，并在 2026 年仍有编译修复和引擎适配方面的更新，表明处于**活跃维护**中，但主要限于兼容性修复而非功能扩展。由于是实验性插件且默认未启用，其 API 和行为可能在未来的引擎版本中发生变化。它适合对 PSD 导入有强烈需求并愿意承担实验性功能风险的开发者进行评估和使用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [官方文档]() （无）