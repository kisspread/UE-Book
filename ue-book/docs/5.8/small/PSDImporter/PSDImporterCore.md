# PSD Importer

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（PSD解析库、编辑器工具、蓝图/代码接口） |
| 模块 | `PSDImporterCore` (Runtime), `PSDImporter` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSDImporter 是一个实验性插件，其核心功能是**将 Adobe Photoshop 的 .psd 文件直接导入到 Unreal Engine 5 中**。与引擎原生仅支持导入扁平化图像不同，此插件能够解析 PSD 文件的完整结构，包括图层、图层组、混合模式、蒙版等信息。

**为什么存在？**
在游戏开发，尤其是 UI 和 2D 游戏制作中，美术资源通常以分层的 PSD 文件交付。原生的导入流程会丢失所有图层信息，迫使美术或开发者手动拆分、导出、重新组织这些图层，流程繁琐且容易出错。PSDImporter 旨在自动化这一过程，允许开发者通过代码或蓝图直接访问 PSD 文件的内部结构，并按照需求（如将每个图层映射为单独的纹理资产、Actor 组件或 Widget）进行程序化处理，极大地提升了美术资产集成的效率和灵活性。

## 使用场景

-   **UI 设计与开发**：设计师提供了一个包含多个按钮、图标、背景层的 PSD 文件。开发者可以使用此插件在运行时或编辑器中，将每个 UI 元素所在的图层独立导入为 `UTexture2D`，并自动创建对应的 `UImage` Widget。
-   **2D 游戏关卡设计**：策划或美术使用 PSD 文件来设计关卡布局（将地形、障碍物、可交互物体放在不同图层）。插件可以解析这些图层，并在引擎中自动生成对应的 Actor 或子场景。
-   **批量资产处理**：需要从大量 PSD 文件中提取特定名称图层纹理的工作流，可以通过编写一个简单的编辑器工具脚本或蓝图来自动化完成。
-   **动态内容加载**：在游戏运行时，根据玩家选择动态加载不同的 PSD 美术方案，并从中提取需要的部分进行渲染。

## 蓝图用法

插件主要通过 `FPSDFileImporter` 类和访问者模式 (`FPSDFileImportVisitors`) 提供蓝图接口。由于是实验性插件，许多高级功能可能主要面向 C++。核心的蓝图可用性体现在编辑器工具的构建上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make PSD File Importer` | 创建一个针对指定文件路径的 PSD 导入器实例。 | `UFPSDFileImporterBPLibrary` (蓝图函数库，需自行根据API推断或创建) |
| `Import` | 执行导入过程，需要传入一个实现了 `FPSDFileImportVisitors` 接口的访问者对象。 | `UFPSDFileImporterBPLibrary` |
| `On Import Header` | 访问者回调：当 PSD 文件头信息被解析后触发。 | `IFPSDFileImportVisitors` |
| `On Import Layer` | 访问者回调：当单个图层信息被解析后触发，提供异步读取图层和蒙版数据的功能。 | `IFPSDFileImportVisitors` |
| `On Import Complete` | 访问者回调：整个文件导入完成后触发。 | `IFPSDFileImportVisitors` |

### 使用示例（蓝图描述）

1.  **创建一个蓝图类**，实现 `IFPSDFileImportVisitors` 接口（在蓝图接口设置中添加 `FPSDFileImportVisitors`）。
2.  在该蓝图类的函数图表中，实现 `On Import Layer` 事件。
3.  当 `On Import Layer` 被调用时，从 `Layer` 参数中获取图层名称 (`LayerName`)、边界 (`Bounds`) 等信息。
4.  调用 `Read Layer Data` 节点，它返回一个 `TFuture<FImage>`。你需要使用 `Wait for Completion` 节点等待异步操作完成。
5.  完成后，你将得到一个 `FImage` 对象，其中包含了该图层的像素数据。你可以将其转换为 `UTexture2D` 资产。
6.  在另一个蓝图（如编辑器工具蓝图）中，调用 `Make PSD File Importer` 创建导入器，然后将上面创建的访问者蓝图对象作为参数传递给 `Import` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "PSDFileImport.h"
#include "PSDFileData.h"
#include "PSDFileDocument.h"
#include "PSDFileRecord.h"
```

### 基本用法

基于 `Public/PSDFileImport.h` 和 `Private/Readers/LayerReader.h` 的核心导入流程。

```cpp
// 示例：创建一个简单的访问者，打印所有图层信息
class FPSDSimpleVisitor : public UE::PSDImporter::FPSDFileImportVisitors
{
public:
    virtual void OnImportHeader(const UE::PSDImporter::File::FPSDHeader& InHeader) override
    {
        UE_LOG(LogTemp, Log, TEXT("PSD Header: %dx%d, %d channels"), InHeader.Width, InHeader.Height, InHeader.NumChannels);
    }

    virtual void OnImportLayer(
        const UE::PSDImporter::File::FPSDLayerRecord& InLayer,
        const UE::PSDImporter::File::FPSDLayerRecord* InParentLayer,
        TFunction<TFuture<FImage>()> InReadLayerData,
        TFunction<TFuture<FImage>()> InReadMaskData) override
    {
        UE_LOG(LogTemp, Log, TEXT("Layer '%s': Bounds [%d, %d, %d, %d]"),
            *InLayer.LayerName,
            InLayer.Bounds.Min.X, InLayer.Bounds.Min.Y,
            InLayer.Bounds.Max.X, InLayer.Bounds.Max.Y);

        // 异步读取图层数据
        TFuture<FImage> LayerDataFuture = InReadLayerData();
        LayerDataFuture.Next([LayerName = InLayer.LayerName](FImage&& Image)
        {
            UE_LOG(LogTemp, Log, TEXT("Layer '%s' data loaded, size: %dx%d"),
                *LayerName, Image.SizeX, Image.SizeY);
            // 在此处处理 Image 数据，例如创建纹理
        });
    }

    virtual void OnImportComplete() override
    {
        UE_LOG(LogTemp, Log, TEXT("PSD Import Complete!"));
    }
};

// 使用导入器
void ImportMyPSDFile(const FString& InFilePath)
{
    using namespace UE::PSDImporter;

    // 1. 创建导入器
    TSharedRef<FPSDFileImporter> Importer = FPSDFileImporter::Make(InFilePath);

    // 2. 创建访问者
    TSharedPtr<FPSDSimpleVisitor> Visitor = MakeShared<FPSDSimpleVisitor>();

    // 3. 设置导入选项
    FPSDFileImporterOptions Options;
    Options.bResizeLayersToDocument = true; // 将图层尺寸扩展到与文档画布一致

    // 4. 执行导入
    bool bSuccess = Importer->Import(Visitor, Options);
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to start PSD import for: %s"), *InFilePath);
    }
}
```

### 进阶用法

结合 `FPSDFileRecord` 中的 `FPSDLayerRecord` 结构，可以获取更详细的图层信息，并进行逻辑判断。

```cpp
// 在 OnImportLayer 回调中
virtual void OnImportLayer(
    const UE::PSDImporter::File::FPSDLayerRecord& InLayer,
    const UE::PSDImporter::File::FPSDLayerRecord* InParentLayer,
    TFunction<TFuture<FImage>()> InReadLayerData,
    TFunction<TFuture<FImage>()> InReadMaskData) override
{
    // 检查图层类型和标志
    if (InLayer.bIsGroup)
    {
        UE_LOG(LogTemp, Log, TEXT("Entering Layer Group: %s"), *InLayer.LayerName);
        return; // 对于图层组，通常不读取像素数据
    }

    // 检查图层是否可见
    if (EnumHasAnyFlags(InLayer.Flags, UE::PSDImporter::File::EPSDLayerFlags::Visible))
    {
        UE_LOG(LogTemp, Log, TEXT("Visible Layer: %s, BlendMode: %d"), *InLayer.LayerName, static_cast<int32>(InLayer.BlendMode));
        
        // 只读取可见图层的数据
        TFuture<FImage> DataFuture = InReadLayerData();
        // ... 处理数据
    }

    // 检查是否存在蒙版并读取
    if (!InLayer.MaskBounds.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT("Layer '%s' has a mask."), *InLayer.LayerName);
        TFuture<FImage> MaskFuture = InReadMaskData();
        MaskFuture.Next([LayerName = InLayer.LayerName](FImage&& MaskImage)
        {
            // 处理蒙版图像
        });
    }
}
```

## Demo 示例

以下是一个最小的、可编译的编辑器模块示例，用于在编辑器中通过控制台命令导入 PSD 文件并输出图层信息。

**PSDImporterDemo.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "PSDFileImport.h"

class FPSDDemoImporter : public UE::PSDImporter::FPSDFileImportVisitors
{
public:
    virtual void OnImportHeader(const UE::PSDImporter::File::FPSDHeader& InHeader) override;
    virtual void OnImportLayer(
        const UE::PSDImporter::File::FPSDLayerRecord& InLayer,
        const UE::PSDImporter::File::FPSDLayerRecord* InParentLayer,
        TFunction<TFuture<FImage>()> InReadLayerData,
        TFunction<TFuture<FImage>()> InReadMaskData) override;
    virtual void OnImportComplete() override;

    void StartImport(const FString& InPSDFilePath);

private:
    TArray<TFuture<FImage>> PendingLayerFutures;
};
```

**PSDImporterDemo.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "PSDImporterDemo.h"
#include "PSDFileData.h" // For EPSDBlendMode etc.
#include "PSDFileRecord.h" // For FPSDLayerRecord
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "PSDImporterModule.h" // 可能需要模块接口

void FPSDDemoImporter::OnImportHeader(const UE::PSDImporter::File::FPSDHeader& InHeader)
{
    UE_LOG(LogTemp, Display, TEXT("[PSDDemo] === Document Info ==="));
    UE_LOG(LogTemp, Display, TEXT("  Size: %d x %d pixels"), InHeader.Width, InHeader.Height);
    UE_LOG(LogTemp, Display, TEXT("  Channels: %d"), InHeader.NumChannels);
    UE_LOG(LogTemp, Display, TEXT("  Color Mode: %s"), LexToString(InHeader.Mode));
    PendingLayerFutures.Empty();
}

void FPSDDemoImporter::OnImportLayer(
    const UE::PSDImporter::File::FPSDLayerRecord& InLayer,
    const UE::PSDImporter::File::FPSDLayerRecord* InParentLayer,
    TFunction<TFuture<FImage>()> InReadLayerData,
    TFunction<TFuture<FImage>()> InReadMaskData)
{
    UE_LOG(LogTemp, Display, TEXT("[PSDDemo] Layer: \"%s\""), *InLayer.LayerName);
    if (InParentLayer)
    {
        UE_LOG(LogTemp, Display, TEXT("  Parent: \"%s\""), *InParentLayer->LayerName);
    }
    UE_LOG(LogTemp, Display, TEXT("  Bounds: X=%d, Y=%d, W=%d, H=%d"),
        InLayer.Bounds.Min.X, InLayer.Bounds.Min.Y,
        InLayer.Bounds.Width(), InLayer.Bounds.Height());
    UE_LOG(LogTemp, Display, TEXT("  Opacity: %d%%, Blend: %d"), InLayer.Opacity, static_cast<int32>(InLayer.BlendMode));

    // 异步读取图层像素数据
    TFuture<FImage> Future = InReadLayerData();
    PendingLayerFutures.Add(MoveTemp(Future));
}

void FPSDDemoImporter::OnImportComplete()
{
    UE_LOG(LogTemp, Display, TEXT("[PSDDemo] === Import Complete ==="));
    UE_LOG(LogTemp, Display, TEXT("  Pending layer data reads: %d"), PendingLayerFutures.Num());
    // 实际项目中，需要等待所有 Future 完成并处理 FImage 数据。
    // 为示例简洁，此处仅记录。
}

void FPSDDemoImporter::StartImport(const FString& InPSDFilePath)
{
    if (!FPaths::FileExists(InPSDFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("[PSDDemo] File not found: %s"), *InPSDFilePath);
        return;
    }

    TSharedRef<UE::PSDImporter::FPSDFileImporter> Importer = UE::PSDImporter::FPSDFileImporter::Make(InPSDFilePath);
    TSharedPtr<FPSDDemoImporter> Visitor = MakeShared<FPSDDemoImporter>();

    UE::PSDImporter::FPSDFileImporterOptions Options;
    Options.bResizeLayersToDocument = false;

    UE_LOG(LogTemp, Display, TEXT("[PSDDemo] Starting import of: %s"), *InPSDFilePath);
    if (!Importer->Import(Visitor, Options))
    {
        UE_LOG(LogTemp, Error, TEXT("[PSDDemo] Import failed to start."));
    }
}

// 控制台命令注册（通常在模块启动时）
static FAutoConsoleCommand CmdImportPSD(
    TEXT("PSDImporterDemo.Import"),
    TEXT("Imports a PSD file and logs layer info. Usage: PSDImporterDemo.Import <filepath>"),
    FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
    {
        if (Args.Num() == 1)
        {
            // 注意：这里简单创建对象来演示，实际项目中应管理其生命周期。
            MakeShared<FPSDDemoImporter>()->StartImport(Args[0]);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Usage: PSDImporterDemo.Import <full_path_to_psd_file>"));
        }
    })
);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ImageWrapper` | 用于将解析出的原始像素数据 (`FImage`) 转换为引擎支持的纹理格式。 |
| `GeometryMask` | 被依赖的插件，可能用于处理蒙版相关的几何或材质功能。 |
| `PsdSDK` (第三方) | 实际解析 PSD 二进制文件格式的核心第三方库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一迁移到新的 `UE_LOGF` 格式。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一次错误的查找替换操作后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了变更列表 CL51314860 的改动。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing registry. | 修复了一个因委托访问方式变更导致的注册缺失问题。 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制了静态分析工具产生的不正确 V1051 警告。 |

### 维护评价

-   **创建时间**：插件于 2025 年 4 月创建，相对年轻。
-   **更新频率与内容**：从提交记录看，近一年内有多次提交，但主要集中在代码维护（日志迁移、编译警告修复、代码回滚）和底层引擎API适配，**没有针对插件本身功能的实质性新增或改进**。最近一次功能性相关的提交是 2025 年 7 月的警告抑制。
-   **活跃度**：插件被标记为 **Experimental**，且 `Installed: false`，表明它处于早期开发或原型验证阶段，并非官方推荐的生产就绪功能。
-   **已知限制**：
    1.  仅支持 Win64 平台。
    2.  文档和描述字段为空，说明官方文档和支持可能不完整。
    3.  依赖一个外部 `PsdSDK`，增加了集成复杂性。
-   **推荐使用**：**仅建议用于研究、学习或内部原型开发**。由于其实验性状态、缺乏文档、且维护重点似乎不在功能迭代上，**不推荐用于生产项目**。如果需要稳定的 PSD 导入工作流，应考虑使用社区插件或自行实现基于成熟 PSD 库（如 psd_sdk）的导入器。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
-   官方文档：无
-   测试用例：源码中未提供明确的测试用例路径。