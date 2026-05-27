# PSD Importer

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | PSD导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `PSDImporterCore` (Runtime), `PSDImporter` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 插件的核心功能是将 Adobe Photoshop 的 `.psd` 文件直接导入到 Unreal Engine 中。它解决了一个常见的美术工作流痛点：美术师在 Photoshop 中制作的带有图层、蒙版、混合模式等信息的源文件，通常需要先导出为 PNG、JPG 等扁平格式，再导入到引擎，这个过程会丢失图层结构和编辑灵活性。此插件通过集成一个强大的第三方 PSD 解析库 (PsdSDK)，使得引擎能够直接读取并理解 PSD 文件的复杂结构，从而可能实现图层级别的资产导入与管理，极大提升了从 Photoshop 到 UE 的资产管线效率。

## 使用场景

*   **UI 设计与开发**：游戏 UI 设计师在 Photoshop 中完成界面布局和元素分层后，可以直接将 PSD 文件导入 UE，保留每个按钮、图标、背景的独立图层信息，便于在 UMG 中进行编程控制和动态组合。
*   **材质与贴图制作**：美术师创建的用于材质的多层贴图（如颜色层、细节层、遮罩层），可以作为独立的纹理资产导入，并在材质编辑器中按层进行引用和混合。
*   **动态内容合成**：对于需要运行时动态更换部分视觉元素的场景（如角色换装、可定制化外观），可以预先将各个部件在 Photoshop 中分层制作，导入后通过程序切换或显示特定图层。
*   **原型快速迭代**：在游戏开发早期，快速导入 UI 原型或概念图并保持其可编辑性，有助于加速迭代。

## 蓝图用法

本插件的主要 API 是 C++ 层面的 PSD 文件解析库 (`PsdSDK`)。编辑器模块 (`PSDImporterEditor`) 可能提供了资产导入的图形界面或编辑器蓝图节点，但从提供的公开头文件中未发现明确的 `BlueprintCallable` 或 `BlueprintReadWrite` 函数。其核心功能集成在资产导入管线中，当用户在内容浏览器中导入 `.psd` 文件时，后台会调用此插件进行解析和资产创建。

## C++ 用法

此插件的核心是其内嵌的 `PsdSDK` 第三方库。C++ 开发者主要在编辑器或工具模块中调用其 API 来解析 PSD 文件。

### 头文件引入

```cpp
// 主要包含需要使用的解析器和类型头文件
#include "Psd.h" // 假设的主头文件，通常由第三方库提供
#include "PsdDocument.h"
#include "PsdLayer.h"
#include "PsdNativeFile.h" // 用于平台原生文件操作
```

### 基本用法

以下代码展示了如何使用 `PsdSDK` 库打开并解析一个 PSD 文件的基础信息。

```cpp
// 来源: 基于 PsdSDK 的公共接口推断
#include "Psd.h"
#include "PsdDocument.h"
#include "PsdNativeFile.h"
#include "PsdAllocator.h"
#include "PsdSyncFileReader.h"

void ParseBasicPSDInfo(const TCHAR* FilePath)
{
    // 1. 创建分配器（内存管理）
    psd::Allocator* Allocator = new psd::MallocAllocator();

    // 2. 打开 PSD 文件
    psd::NativeFile File(Allocator);
    if (!File.OpenRead(FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("无法打开PSD文件: %s"), FilePath);
        delete Allocator;
        return;
    }

    // 3. 创建同步读取器
    psd::SyncFileReader Reader(&File);

    // 4. 解析文件头和文档信息 (示例概念，具体函数调用需参考SDK)
    // psd::Document* Document = psd::ParseDocument(&Reader, Allocator);
    // if (Document)
    // {
    //     UE_LOG(LogTemp, Log, TEXT("PSD尺寸: %d x %d"), Document->width, Document->height);
    //     UE_LOG(LogTemp, Log, TEXT("通道数: %d, 位深: %d"), Document->channelCount, Document->bitsPerChannel);
    //     
    //     // 5. 解析后需要销毁文档
    //     psd::DestroyDocument(Document, Allocator);
    // }

    // 6. 关闭文件并清理资源
    File.Close();
    delete Allocator;
}
```

### 进阶用法

解析 PSD 文件并提取所有图层信息。

```cpp
// 来源: 基于 PsdParseLayerMaskSection.h 和 PsdLayer.h 推断
#include "Psd.h"
#include "PsdLayerMaskSection.h"
#include "PsdLayer.h"
#include "PsdNativeFile.h"
#include "PsdAllocator.h"
#include "PsdSyncFileReader.h"

void ExtractPSDLayers(const TCHAR* FilePath)
{
    psd::Allocator* Allocator = new psd::MallocAllocator();
    psd::NativeFile File(Allocator);
    if (!File.OpenRead(FilePath)) { /* 错误处理 */ delete Allocator; return; }
    psd::SyncFileReader Reader(&File);

    // 假设先解析了文档头 (Document)
    // psd::Document* Doc = psd::ParseDocument(&Reader, Allocator);
    
    // 解析图层蒙版段落，获取图层数组
    psd::LayerMaskSection* LayerSection = psd::ParseLayerMaskSection(Doc, &File, Allocator);
    if (LayerSection)
    {
        UE_LOG(LogTemp, Log, TEXT("图层总数: %u"), LayerSection->layerCount);
        
        for (unsigned int i = 0; i < LayerSection->layerCount; ++i)
        {
            psd::Layer* CurrentLayer = &LayerSection->layers[i];
            
            // 打印图层名称
            UE_LOG(LogTemp, Log, TEXT("图层 %u: %hs (Opacity: %d, BlendMode: %u)"), 
                i, CurrentLayer->name.c_str(), CurrentLayer->opacity, CurrentLayer->blendModeKey);
            
            // 提取单个图层的实际像素数据（需要进一步调用ExtractLayer）
            psd::ExtractLayer(Doc, &File, Allocator, CurrentLayer);
            
            // 此时 CurrentLayer->channels 中包含各通道数据指针
            // 需要根据 CurrentLayer->left, top, right, bottom 计算尺寸
        }
        
        // 使用完毕后，销毁图层段落
        psd::DestroyLayerMaskSection(LayerSection, Allocator);
    }
    
    // psd::DestroyDocument(Doc, Allocator);
    File.Close();
    delete Allocator;
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何集成 `PsdSDK` 进行简单的 PSD 文件信息读取。

```cpp
// MyPSDReader.h
#pragma once

#include "CoreMinimal.h"
#include "PSDReader.generated.h"

UCLASS()
class UMyPSDReader : public UObject
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable, Category = "PSD Tool")
    static bool ReadPSDInfo(const FString& FilePath, int32& OutWidth, int32& OutHeight, int32& OutLayerCount);
};

// MyPSDReader.cpp
#include "MyPSDReader.h"
#include "Psd.h"
#include "PsdDocument.h"
#include "PsdLayerMaskSection.h"
#include "PsdNativeFile.h"
#include "PsdAllocator.h"
#include "PsdSyncFileReader.h"

bool UMyPSDReader::ReadPSDInfo(const FString& FilePath, int32& OutWidth, int32& OutHeight, int32& OutLayerCount)
{
    psd::Allocator* Allocator = new psd::MallocAllocator();
    psd::NativeFile File(Allocator);
    
    // 转换路径格式
    const TCHAR* Path = *FilePath;
    if (!File.OpenRead(Path))
    {
        UE_LOG(LogTemp, Error, TEXT("UMyPSDReader::ReadPSDInfo - 无法打开文件: %s"), *FilePath);
        delete Allocator;
        return false;
    }
    
    psd::SyncFileReader Reader(&File);
    
    // 此处为演示，实际解析逻辑需要按PSD文件规范顺序执行
    // 通常顺序为：解析文件头 -> 解析各段落 -> 提取数据
    
    // 模拟解析成功（实际代码需替换为真实解析调用）
    OutWidth = 1920;  // 假设从解析出的 Document->width 获得
    OutHeight = 1080; // 假设从解析出的 Document->height 获得
    OutLayerCount = 5; // 假设从 LayerMaskSection->layerCount 获得
    
    UE_LOG(LogTemp, Log, TEXT("PSD文件解析完成: %s (%dx%d, %d层)"), *FilePath, OutWidth, OutHeight, OutLayerCount);
    
    File.Close();
    delete Allocator;
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PsdSDK` | 核心第三方库，负责解析和导出 Adobe PSD 文件格式。 |
| `GeometryMask` | 依赖的插件，可能用于处理或生成与 PSD 图层蒙版相关的几何形状遮罩。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件内的日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 第二次尝试，修复了上一次错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了编号为 CL51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托注册问题，将 `OnPostEngineInit` 迁移为通过 `GetOnPostEngineInit()` 访问。 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 禁用代码静态分析工具发出的 V1051 错误警告。 |

### 维护评价

PSD Importer 是一个于 2025 年 4 月创建的 **实验性** 插件，目前处于活跃开发阶段。从最近的 Git 记录看，过去一年内有持续的维护和改进，主要集中在代码质量、编译警告修复以及与最新引擎版本的 API 兼容性更新上（如迁移 `UE_LOG` 和委托系统）。虽然被标记为实验性（`EnabledByDefault=false`），但其更新频率表明 Epic 可能正在持续开发此功能。**推荐在 Windows 平台（Win64）的项目中试用此插件**，但需注意其 API 可能随引擎版本更新而变化，且尚未在其他平台验证。适合对美术管线有较高要求、愿意尝试新功能的团队。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter/Tests) (推测路径)