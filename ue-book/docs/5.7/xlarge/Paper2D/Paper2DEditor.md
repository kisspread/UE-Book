# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、纹理、示例关卡） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor), `SpriterImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是 Unreal Engine 内置的官方 2D 游戏开发框架。它并非一个简单的渲染层，而是一套完整的工具链和资产系统，旨在将 UE 强大的引擎能力（如物理、蓝图、音频、UI）与 2D 游戏开发需求相结合。它解决了在 UE 中高效创建、编辑和运行 2D 游戏内容的问题，提供了从精灵（Sprite）创建、动画（Flipbook）编辑、图块地图（Tile Map）构建到关卡设计的全流程支持。

## 使用场景

-   **2D 平台跳跃游戏**：使用 `PaperCharacter` 作为玩家角色，利用其内置的侧视图物理和移动组件。
-   **俯视角 RPG 或冒险游戏**：使用 `PaperTileMap` 和 `PaperTileSet` 快速搭建基于图块的关卡。
-   **像素艺术风格游戏**：利用 Paper2D 的纹理设置和材质系统，精确控制像素的渲染效果。
-   **需要复杂 2D 动画的游戏**：使用 `PaperFlipbook` 创建基于序列帧的动画，并通过蓝图或 C++ 控制播放。
-   **使用 Tiled 地图编辑器的项目**：通过 `PaperTiledImporter` 模块直接导入 `.tmx` 格式的地图文件。
-   **需要将 2D 元素与 3D 场景混合的项目**：Paper2D 的资产可以放置在 3D 世界中，实现 2.5D 效果。

## 蓝图用法

Paper2D 的核心运行时功能（如 `PaperCharacter`, `PaperFlipbookComponent`）主要通过蓝图暴露。`Paper2DEditor` 模块则提供了编辑器扩展和工具函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExtractFlipbooksFromSprites` | 根据精灵名称自动分组，尝试将一组精灵拆分为多个翻书资产。 | `FPaperFlipbookHelpers` |
| `ReadString` / `ReadObject` / `ReadArray` 等 | 一系列用于安全解析 JSON 对象的静态辅助函数。 | `FPaperJSONHelpers` |

### 使用示例（蓝图描述）

1.  **自动创建翻书动画**：
    *   在编辑器工具蓝图中，获取一个包含多个 `UPaperSprite` 资产的数组（例如，通过资产注册表筛选）。
    *   调用 `FPaperFlipbookHelpers::ExtractFlipbooksFromSprites` 节点，传入精灵数组。
    *   该节点会返回一个 `TMap`，其中键是推断出的动画名称（如 “Walk”、“Run”），值是对应的精灵数组。
    *   遍历这个 Map，为每一组精灵调用 `UPaperFlipbookFactory` 创建新的 `UPaperFlipbook` 资产。

2.  **解析自定义数据文件**：
    *   读取一个 JSON 文件并解析为 `FJsonObject`。
    *   使用 `FPaperJSONHelpers::ReadString` 等节点安全地提取字段值，避免因字段缺失或类型错误导致崩溃。

## C++ 用法

`Paper2DEditor` 模块主要为编辑器提供扩展点和工具类，其 API 通常在编写编辑器工具或自定义资产编辑器时使用。

### 头文件引入

```cpp
#include "Paper2DEditorModule.h"
#include "PaperFlipbookHelpers.h"
#include "PaperJSONHelpers.h"
```

### 基本用法

以下示例展示了如何使用 `PaperFlipbookHelpers` 来组织精灵。

```cpp
// 来源: Engine/Plugins/2D/Paper2D/Source/Paper2DEditor/Public/PaperFlipbookHelpers.h
// 假设我们有一组从文件夹加载的精灵
TArray<UPaperSprite*> LoadedSprites = ...; // 加载精灵的逻辑
TArray<FString> SpriteNames; // 可以为空，函数会使用 Sprite->GetName()

// 用于存储分组结果
TMap<FString, TArray<UPaperSprite*>> GroupedFlipbooks;

// 调用静态函数进行智能分组
FPaperFlipbookHelpers::ExtractFlipbooksFromSprites(GroupedFlipbooks, LoadedSprites, SpriteNames);

// 现在 GroupedFlipbooks 中包含了按名称规律分组的精灵数组
for (auto& Pair : GroupedFlipbooks)
{
    FString AnimationName = Pair.Key;
    TArray<UPaperSprite*>& SpritesForFlipbook = Pair.Value;
    // 接下来可以使用这些数据创建 UPaperFlipbook 资产
}
```

### 进阶用法

以下示例展示了如何扩展 Paper2D 的编辑器界面，这需要实现 `IPaper2DEditorModule` 接口。

```cpp
// 来源: Engine/Plugins/2D/Paper2D/Source/Paper2DEditor/Public/Paper2DEditorModule.h
// 在你的编辑器模块中
class FMyPaper2DExtensionModule : public IPaper2DEditorModule
{
public:
    virtual void StartupModule() override
    {
        // 获取 Paper2D 编辑器模块的实例
        IPaper2DEditorModule& Paper2DEditor = FModuleManager::LoadModuleChecked<IPaper2DEditorModule>(PAPER2D_EDITOR_MODULE_NAME);

        // 向精灵编辑器的工具栏添加一个自定义按钮
        TSharedPtr<FExtensibilityManager> ToolBarManager = Paper2DEditor.GetSpriteEditorToolBarExtensibilityManager();
        if (ToolBarManager.IsValid())
        {
            // ... 创建并添加 FExtender 的逻辑
        }
    }

    // 实现接口要求的纯虚函数
    virtual uint32 GetPaper2DAssetCategory() const override
    {
        // 返回一个自定义的资产类别 ID，用于内容浏览器筛选
        return MyCustomAssetCategory;
    }
};
```

## Demo 示例

一个最小化的编辑器工具示例，演示如何使用 `Paper2DEditor` 模块的接口来扩展精灵编辑器。

```cpp
// MyPaper2DEditorExtension.h
#pragma once
#include "Paper2DEditorModule.h"

class FMyPaper2DEditorExtension : public IPaper2DEditorModule
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // IPaper2DEditorModule Interface
    virtual TSharedPtr<class FExtensibilityManager> GetSpriteEditorToolBarExtensibilityManager() override;
    virtual uint32 GetPaper2DAssetCategory() const override;

private:
    TSharedPtr<FExtensibilityManager> SpriteEditorToolBarExtensibilityManager;
};
```

```cpp
// MyPaper2DEditorExtension.cpp
#include "MyPaper2DEditorExtension.h"
#include "Toolkits/AssetEditorManager.h"

#define LOCTEXT_NAMESPACE "FMyPaper2DEditorExtension"

void FMyPaper2DEditorExtension::StartupModule()
{
    // 初始化扩展管理器
    SpriteEditorToolBarExtensibilityManager = MakeShareable(new FExtensibilityManager);

    // 这里可以注册具体的工具栏按钮扩展
    // 例如，监听精灵编辑器的打开事件，并注入自定义UI
}

void FMyPaper2DEditorExtension::ShutdownModule()
{
    SpriteEditorToolBarExtensibilityManager.Reset();
}

TSharedPtr<FExtensibilityManager> FMyPaper2DEditorExtension::GetSpriteEditorToolBarExtensibilityManager()
{
    return SpriteEditorToolBarExtensibilityManager;
}

uint32 FMyPaper2DEditorExtension::GetPaper2DAssetCategory() const
{
    // 返回一个在编辑器中注册的资产类别
    // 通常通过 FAssetEditorToolkit 或 IAssetTypeActions 注册
    return 0; // 示例，实际应返回有效ID
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyPaper2DEditorExtension, MyPaper2DEditorExtension)
```

## 模块依赖

`Paper2DEditor` 模块依赖于 Paper2D 的运行时模块以及标准的编辑器框架。

| 模块 | 用途 |
|---|---|
| `Paper2D` | Paper2D 的核心运行时模块，提供所有基础资产类型和组件。 |
| `EditorFramework` | 提供编辑器框架支持，如资产编辑器。 |
| `UnrealEd` | Unreal 编辑器核心模块，提供工厂、缩略图渲染、资产导入等基础设施。 |

## 维护状态

### 近期更新

```
- bb3758b4bb5f SEditorViewport::MakeViewportToolbar() is deprecated. (修复了编辑器视口工具栏的废弃API调用)
- 2057280165b3 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n (代码规范更新，确保DLL导出符号正确)
- 1a832d69d5bc Move the StringOutputDevice into a separate header. (代码重构，将工具类移至独立头文件)
```

### 维护评价

Paper2D 是一个历史悠久且功能完整的插件，自 2014 年随 UE4 发布以来一直是引擎的一部分。尽管 Epic Games 官方近年来将开发重心更多地放在 3D 和跨平台功能上，但 Paper2D 作为官方解决方案，其核心代码仍然会随着引擎版本进行必要的维护和兼容性更新（如上述的 API 废弃修复和代码规范调整）。

**优点**：
-   官方支持，与引擎深度集成，稳定可靠。
-   功能全面，覆盖了 2D 游戏开发的主要需求。
-   文档和社区资源相对丰富。

**限制与注意事项**：
-   官方已明确表示 **不再为 Paper2D 添加重大新功能**，其状态类似于“维护模式”。
-   对于复杂的现代 2D 游戏需求（如高性能粒子、复杂着色器），可能需要结合其他插件或自行扩展。
-   部分功能（如图块集）仍标记为实验性。

**推荐**：对于中小型 2D 项目、原型开发、或需要将 2D 元素与 UE 3D 功能结合的项目，Paper2D 仍然是一个优秀且可靠的选择。对于追求最新 2D 技术特性的大型项目，可能需要评估社区插件或自研方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/2DGameDevelopment/)

---
# Paper2DEditor 模块文档

`Paper2DEditor` 是 Paper2D 插件的编辑器模块，负责提供所有与 2D 资产创建、编辑和导入相关的编辑器功能、工厂类、缩略图渲染器以及编辑器扩展接口。

## 属性表

| 属性 | 值 |
|---|---|
| 模块名 | `Paper2DEditor` |
| 类型 | Editor |
| 加载阶段 | Default |

## 核心功能

1.  **资产工厂 (Factories)**：提供创建各种 Paper2D 资产（精灵、翻书、图块集、图块地图）的工厂类。
2.  **缩略图渲染器 (Thumbnail Renderers)**：为内容浏览器中的 Paper2D 资产生成预览图。
3.  **编辑器扩展接口**：通过 `IPaper2DEditorModule` 接口，允许其他模块扩展精灵和翻书编辑器的菜单和工具栏。
4.  **导入器支持**：包含用于处理图块地图导入数据的类。
5.  **工具类**：提供用于翻书创建辅助和 JSON 解析的静态工具类。

## 关键类说明

### 资产工厂

| 类名 | 功能 |
|---|---|
| `UPaperSpriteFactory` | 从纹理创建 `UPaperSprite` 资产。 |
| `UPaperFlipbookFactory` | 从一组关键帧创建 `UPaperFlipbook` 资产。 |
| `UPaperTileSetFactory` | 从纹理创建 `UPaperTileSet` 资产。 |
| `UPaperTileMapFactory` | 创建空的 `UPaperTileMap` 资产。 |
| `UPaperTileMapPromotionFactory` | 用于将实例化的图块地图对象提升为独立资产。 |

### 缩略图渲染器

| 类名 | 功能 |
|---|---|
| `UPaperSpriteThumbnailRenderer` | 渲染 `UPaperSprite` 的缩略图，支持绘制网格背景。 |
| `UPaperFlipbookThumbnailRenderer` | 渲染 `UPaperFlipbook` 的缩略图，显示第一帧。 |
| `UPaperTileSetThumbnailRenderer` | 渲染 `UPaperTileSet` 的缩略图，显示图块集纹理。 |

### Actor 工厂

| 类名 | 功能 |
|---|---|
| `UPaperSpriteActorFactory` | 允许从 `UPaperSprite` 资产拖拽生成 `APaperSpriteActor`。 |
| `UPaperFlipbookActorFactory` | 允许从 `UPaperFlipbook` 资产拖拽生成 `APaperFlipbookActor`。 |
| `UTileMapActorFactory` | 允许从 `UPaperTileMap` 资产拖拽生成 `ATileMapActor`。 |
| `UTerrainSplineActorFactory` | 允许从 `UPaperTerrainSpline` 资产拖拽生成 Actor。 |

### 工具类

| 类名 | 功能 |
|---|---|
| `FPaperFlipbookHelpers` | 提供 `ExtractFlipbooksFromSprites` 静态方法，用于根据命名规律自动将精灵分组为翻书。 |
| `FPaperJSONHelpers` | 提供一系列安全的 JSON 字段读取静态方法，用于解析外部数据（如 Spriter 文件）。 |
| `UPaperImporterSettings` | 存储 Paper2D 资产导入的全局设置，如默认像素比、材质选择策略、纹理压缩等。 |
| `UTileMapAssetImportData` | 存储图块地图资产的导入源信息和图块集映射关系。 |

## 编辑器扩展点

通过 `IPaper2DEditorModule` 接口，其他编辑器模块可以扩展 Paper2D 的编辑器体验：

```cpp
// 获取 Paper2D 编辑器模块
IPaper2DEditorModule& Paper2DEditor = FModuleManager::LoadModuleChecked<IPaper2DEditorModule>(PAPER2D_EDITOR_MODULE_NAME);

// 向精灵编辑器的菜单栏添加自定义菜单项
TSharedPtr<FExtensibilityManager> MenuManager = Paper2DEditor.GetSpriteEditorMenuExtensibilityManager();
// ... 使用 MenuManager 添加 FMenuExtensionDelegate

// 向翻书编辑器的工具栏添加自定义按钮
TSharedPtr<FExtensibilityManager> ToolBarManager = Paper2DEditor.GetFlipbookEditorToolBarExtensibilityManager();
// ... 使用 ToolBarManager 添加 FToolBarExtensionDelegate
```