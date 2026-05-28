# Paper Sprite Sheet Importer

> Parses a JSON from FileContents and imports / reimports a spritesheet.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 精灵表导入器 |
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（导入器资产） |
| 模块 | `PaperSpriteSheetImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Source/PaperSpriteSheetImporter) | |

## 用途

该模块是 Paper2D 插件的组成部分，专门用于将外部 2D 资源打包工具（如 TexturePacker 等）生成的 **JSON 格式的精灵表（Sprite Sheet）描述文件** 导入到 UE5 中。它解决了从第三方美术工具工作流向引擎资产迁移的关键环节，能够解析 JSON 数据，自动创建纹理资产（包括法线贴图）和对应的 `UPaperSprite` 对象，并支持后续的重新导入更新。

## 使用场景

- 你的美术使用 TexturePacker 等工具将大量 2D 图标、角色动画帧打包成单张大纹理图（精灵表）和一个 JSON 配置文件。
- 你需要将这份打包好的素材快速、批量地导入到 UE5 项目中，生成可直接用于 Paper2D 系统（如 `PaperFlipbook`）的引擎资产。
- 美术更新了素材后，你需要通过重新导入功能同步最新的精灵表数据和纹理，而无需手动重新创建和配置每个精灵。

## 蓝图用法

此模块为编辑器工具模块，**不暴露任何蓝图可调用的函数或属性**。其所有功能均通过编辑器内的资产导入操作提供。

## C++ 用法

### 头文件引入

```cpp
// 核心导入器类
#include "PaperJsonSpriteSheetImporter.h"
```

### 基本用法：从字符串或文件导入精灵表

（基于 `FPaperJsonSpriteSheetImporter` 的公共接口设计）

```cpp
#include "PaperJsonSpriteSheetImporter.h"

// 示例：假设你已经从文件读取了 JSON 内容
FString JsonContent = TEXT("{ \"frames\": {...}, \"meta\": {...} }");
FString ErrorContext = TEXT("MySpriteSheet.json");

// 1. 创建导入器实例
FPaperJsonSpriteSheetImporter Importer;

// 2. 解析 JSON 内容
if (Importer.ImportFromString(JsonContent, ErrorContext, /*bSilent=*/false))
{
    // 解析成功，数据已加载到 Importer 内部 (Frames 数组等)
    // 3. 设置目标导入路径和标志
    FString LongPackagePath = TEXT("/Game/Sprites");
    EObjectFlags Flags = RF_Public | RF_Standalone;

    // 4. 执行实际导入，创建/更新资产
    UPaperSpriteSheet* SpriteSheet = nullptr; // 可传入现有资产进行更新
    if (Importer.PerformImport(LongPackagePath, Flags, SpriteSheet))
    {
        // 导入成功，SpriteSheet 指向创建或更新的资产
        UE_LOG(LogTemp, Log, TEXT("成功导入精灵表: %s"), *SpriteSheet->GetName());
    }
}
```

**说明**：通常情况下，开发者不需要直接调用此类。引擎的导入框架会自动通过 `UPaperSpriteSheetImportFactory` 使用它。直接使用主要适用于自动化导入管线或测试。

### 进阶用法：支持重新导入

```cpp
#include "PaperJsonSpriteSheetImporter.h"
#include "PaperSpriteSheet.h"

// 假设你已经有了一个已存在的 UPaperSpriteSheet 资产
UPaperSpriteSheet* ExistingSheet = ...;

// 配置重新导入数据
FPaperJsonSpriteSheetImporter Importer;
TArray<FString> ExistingNames;
TArray<TSoftObjectPtr<UPaperSprite>> ExistingPtrs;

// 从现有资产中提取精灵信息用于比对
for (int32 i = 0; i < ExistingSheet->SpriteNames.Num(); ++i)
{
    ExistingNames.Add(ExistingSheet->SpriteNames[i]);
    ExistingPtrs.Add(ExistingSheet->Sprites[i]);
}

Importer.SetReimportData(ExistingNames, ExistingPtrs);
Importer.bIsReimporting = true;

// ... 接着按基本用法进行 ImportFromString 和 PerformImport。
// 重新导入时，系统会尝试匹配并更新现有精灵，而非全部创建新的。
```

## Demo 示例

下面是一个最小化的编辑器工具类，演示如何在一个编辑器命令中触发精灵表的 JSON 导入。

**头文件 (MySpriteSheetImportTool.h)**

```cpp
#pragma once
#include "CoreMinimal.h"

class UMySpriteSheetImportTool
{
public:
    // 一个模拟从文件路径导入的静态函数
    static bool ImportSpriteSheetFromJsonFile(const FString& JsonFilePath, const FString& TargetFolder);
};
```

**源文件 (MySpriteSheetImportTool.cpp)**

```cpp
#include "MySpriteSheetImportTool.h"
#include "PaperJsonSpriteSheetImporter.h"
#include "HAL/PlatformFilemanager.h"

bool UMySpriteSheetImportTool::ImportSpriteSheetFromJsonFile(const FString& JsonFilePath, const FString& TargetFolder)
{
    // 读取 JSON 文件内容
    FString JsonContent;
    if (!FFileHelper::LoadFileToString(JsonContent, *JsonFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("无法读取文件: %s"), *JsonFilePath);
        return false;
    }

    // 初始化导入器
    FPaperJsonSpriteSheetImporter Importer;

    // 第一步：解析 JSON
    if (!Importer.ImportFromString(JsonContent, JsonFilePath, false))
    {
        UE_LOG(LogTemp, Error, TEXT("解析 JSON 失败: %s"), *JsonFilePath);
        return false;
    }

    // 第二步：导入纹理（可选，通常 PerformImport 内部会处理，但此步可提前获取纹理路径）
    FString TextureLongPackagePath; // 纹理将导入到此包路径
    // Importer.ImportTextures(TargetFolder, FPaths::GetPath(JsonFilePath));

    // 第三步：执行主导入流程，创建资产
    UPaperSpriteSheet* NewSpriteSheet = nullptr;
    EObjectFlags Flags = RF_Public | RF_Standalone | RF_Transactional;
    if (!Importer.PerformImport(TargetFolder, Flags, NewSpriteSheet))
    {
        UE_LOG(LogTemp, Error, TEXT("执行导入失败: %s"), *JsonFilePath);
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("成功导入精灵表到: %s"), *NewSpriteSheet->GetPathName());
    return true;
}
```

## 模块依赖

基于典型 Paper2D 模块依赖模式，此编辑器模块通常依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Paper2D` | 访问核心 `UPaperSprite`、`UPaperSpriteSheet` 等运行时类型 |
| `Json` | 解析 JSON 格式的精灵表描述文件 |
| `AssetTools` | 集成编辑器的资产导入和操作界面 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `32652778` | Harden Paper2D tile map and tile layer PostEditChangeProperty paths against null entries and non-til | 强化 TileMap 和 TileLayer 的 PostEditChangeProperty 流程，防止空条目和无效 Tile 引发问题。 |
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回退了一个提交（CL53903539）。 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 在工具栏添加全局对齐开关，当任一对齐选项启用时显示（红色）指示器。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下，因双精度常量截断为浮点数而产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移至 UE_LOGF 格式。 |

### 维护评价

**维护状态：活跃维护中**
- **年龄**：该模块自 2014 年随 Paper2D 插件一同创建，属于引擎的“文物级”组件。
- **更新频率**：近期的提交（2026年5月）表明 Epic 仍在积极维护 Paper2D 插件，修复问题并改进工作流。
- **功能相关性**：虽然提交不直接针对 `PaperSpriteSheetImporter` 模块，但属于同插件维护，表明插件整体仍在维护范围内。
- **建议**：由于 Paper2D 是成熟模块，API 稳定，功能明确，**推荐使用**。对于新的 2D 项目，它仍然是官方支持的 2D 开发解决方案的一部分。没有迹象表明该模块即将被废弃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Source/PaperSpriteSheetImporter)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/paper-2d-in-unreal-engine/)（Paper2D 整体文档）