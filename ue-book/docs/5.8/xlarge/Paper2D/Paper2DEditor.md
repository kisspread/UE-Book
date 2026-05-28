# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 二维纸片 |
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是 Unreal Engine 内置的官方 2D 游戏开发框架。它旨在为在三维引擎中制作二维内容提供一套完整的工具链，解决的核心问题是：**如何在 UE 中高效地创建、编辑和运行 2D 游戏元素**。它超越了简单的纹理使用，提供了专业的 2D 资产（如精灵、图块集、翻书动画）和配套的编辑器工具（如精灵编辑器、图块地图编辑器），让开发者可以像使用传统 2D 引擎一样工作，同时又能利用 UE 强大的渲染、物理和蓝图系统。

## 使用场景

- **你正在制作一个 2D 平台跳跃游戏**：使用 `UPaperSprite` 来表示角色和平台，使用 `UPaperFlipbook` 来制作角色的跑步、跳跃等逐帧动画。
- **你需要创建一个大型的瓦片地图关卡**：使用 `UPaperTileSet` 和 `UPaperTileMap` 来组织和绘制由小图块拼接而成的关卡地形和场景。
- **你想从一张已有的 sprite sheet（精灵图集）纹理中快速提取出多个独立的精灵**：使用 `PaperSpriteSheetImporter` 模块的功能或编辑器中的“Extract Sprites”工具。
- **你想导入 Tiled 等第三方地图编辑器生成的关卡数据**：使用 `PaperTiledImporter` 模块来解析和导入 `.tmx` 等格式的地图文件。
- **你需要为 2D 精灵定义精确的碰撞体（圆形、多边形）**：在精灵编辑器中进入“编辑碰撞”模式来创建和编辑碰撞几何体。

## 蓝图用法

Paper2D 的运行时蓝图 API 主要集中在 `Paper2D` 模块中，用于控制翻书动画播放、查询图块地图信息等。编辑器模块（`Paper2DEditor` 等）主要提供资产导入和编辑器设置，不直接在运行时蓝图中使用。

### 核心节点（运行时）

由于提供的源码信息主要为编辑器模块 (`Paper2DEditor`)，以下是从该模块推断出的、可在编辑器蓝图或编辑器工具中使用的核心设置节点，它们继承自 `UObject`，可在项目设置或编辑器工具蓝图中访问：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConfigureDefaultSprite` | 根据材质和光照模式，为新精灵资产配置默认的材质和渲染参数。 | `UPaperImporterSettings` |
| `ApplySettingsForTileMapInit` | 为新的图块地图资产应用默认设置，如材质、图块集等。 | `UPaperImporterSettings` |
| `AnalyzeTextureForDesiredMaterialType` | 分析纹理区域，根据Alpha通道内容推荐最适合的材质类型（不透明、遮罩、半透明）。 | `UPaperImporterSettings` |
| `GetDefaultMaterial` | 根据指定的材质类型（遮罩、不透明、半透明）和光照模式，获取对应的默认材质实例。 | `UPaperImporterSettings` |
| `ApplyTextureSettings` | 将配置的压缩和纹理组设置应用到指定的 `UTexture2D` 资产。 | `UPaperImporterSettings` |

### 使用示例（蓝图描述）

1.  **获取并修改导入设置**：在编辑器工具蓝图中，使用 `Get Default` 节点获取 `Paper Importer Settings` 类的单例。然后可以读取或设置其属性，例如修改 `Default Pixels Per Unreal Unit` 来改变默认的像素与厘米比例。
2.  **在自定义导入流程中应用设置**：在编写自定义资产导入脚本时，可以调用 `Apply Settings For Sprite Init` 节点，传入一个精灵资产的初始化参数结构体，以自动应用项目预设的默认材质和渲染设置。

## C++ 用法

Paper2D 的 C++ API 同样分为运行时和编辑器两部分。编辑器模块提供了大量用于构建自定义工具和扩展编辑器功能的接口。

### 头文件引入

```cpp
// 引入运行时核心类
#include "Paper2D/Classes/PaperSprite.h"
#include "Paper2D/Classes/PaperFlipbook.h"
#include "Paper2D/Classes/PaperTileMap.h"
// 引入编辑器设置类（仅在编辑器模块中使用）
#include "Paper2DEditor/Classes/PaperImporterSettings.h"
```

### 基本用法

以下示例展示了如何在 C++ 中访问和修改编辑器的导入设置，来源于 `PaperImporterSettings.h`。

```cpp
// 获取 Paper2D 导入设置（单例）
UPaperImporterSettings* ImporterSettings = GetMutableDefault<UPaperImporterSettings>();

// 修改默认的像素/单位比例
ImporterSettings->DefaultPixelsPerUnrealUnit = 0.5f; // 表示 0.5 像素 = 1 厘米
ImporterSettings->SaveConfig(); // 保存到配置文件

// 在创建新精灵时，分析纹理并自动应用最佳材质
UTexture2D* MyTexture = ...;
FIntPoint TextureSize(MyTexture->GetSizeX(), MyTexture->GetSizeY());
ESpriteInitMaterialType RecommendedType = ImporterSettings->AnalyzeTextureForDesiredMaterialType(MyTexture, FIntPoint::ZeroValue, TextureSize);

// 获取对应的默认材质
UMaterialInterface* BestMaterial = ImporterSettings->GetDefaultMaterial(RecommendedType, false); // false 表示使用无光照材质
```

### 进阶用法

Paper2DEditor 模块提供了丰富的编辑器扩展点。以下示例基于 `IPaper2DEditorModule` 接口，展示如何注册自定义的编辑器菜单扩展。

```cpp
// 在你的编辑器模块中，获取 Paper2D 编辑器模块的接口
IPaper2DEditorModule& Paper2DEditorModule = FModuleManager::LoadModuleChecked<IPaper2DEditorModule>(TEXT("Paper2DEditor"));

// 获取精灵编辑器的工具栏扩展管理器
TSharedPtr<FExtensibilityManager> SpriteToolbarExtensibility = Paper2DEditorModule.GetSpriteEditorToolBarExtensibilityManager();
if (SpriteToolbarExtensibility.IsValid())
{
    // 创建并注册一个扩展
    TSharedPtr<FExtender> MyToolbarExtender = MakeShareable(new FExtender);
    MyToolbarExtender->AddToolBarExtension(
        “Asset”,
        EExtensionHook::After,
        CommandList,
        FToolBarExtensionDelegate::CreateLambda([](FToolBarBuilder& Builder)
        {
            Builder.AddToolBarButton(
                FUIAction(FExecuteAction::CreateStatic(&MyFunction)),
                NAME_None,
                LOCTEXT(“MyButton_Label”, “My Tool”),
                LOCTEXT(“MyButton_Tooltip”, “Description of my tool”),
                FSlateIcon(FAppStyle::GetAppStyleSetName(), “LevelEditor.FoliageMode”)
            );
        })
    );
    SpriteToolbarExtensibility->AddExtender(MyToolbarExtender);
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在运行时代码中引用 Paper2D 的核心资产类型。

**MyPaperActor.h**
```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "PaperActor.generated.h"

class UPaperFlipbookComponent;
class UPaperSpriteComponent;

UCLASS()
class APaperActor : public AActor
{
    GENERATED_BODY()

public:
    APaperActor();

protected:
    // 用于静态2D精灵的组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D")
    UPaperSpriteComponent* SpriteComponent;

    // 用于逐帧动画的组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D")
    UPaperFlipbookComponent* FlipbookComponent;
};
```

**MyPaperActor.cpp**
```cpp
#include "MyPaperActor.h"
#include "PaperSpriteComponent.h"
#include "PaperFlipbookComponent.h"
#include "PaperFlipbook.h"

APaperActor::APaperActor()
{
    SpriteComponent = CreateDefaultSubobject<UPaperSpriteComponent>(TEXT("Sprite"));
    RootComponent = SpriteComponent;

    FlipbookComponent = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("Flipbook"));
    FlipbookComponent->SetupAttachment(RootComponent);
    // 可以在此设置默认的翻书资源：FlipbookComponent->SetFlipbook(MyDefaultFlipbookAsset);
}

// 蓝图或C++中控制动画播放的示例函数
void APaperActor::PlayFlipbookAnimation()
{
    if (FlipbookComponent && FlipbookComponent->GetFlipbook())
    {
        FlipbookComponent->Play();
        FlipbookComponent->SetLooping(true);
    }
}
```

## 模块依赖

要使用 Paper2D 的完整功能（包括编辑器扩展），你的项目或模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Paper2D` | 包含所有运行时核心类，如精灵、翻书、图块地图。 |
| `Paper2DEditor` | 提供资产编辑器（精灵、翻书、图块集、图块地图编辑器）、导入设置和扩展管理器。 |
| `PaperSpriteSheetImporter` | 提供从精灵图集纹理中批量导入精灵的功能。 |
| `PaperTiledImporter` | 提供导入第三方地图编辑器（如Tiled）文件的功能。 |
| `SmartSnapping` | 提供智能对齐和吸附功能，增强2D编辑精度。 |

**注意**：`Paper2DEditor`, `PaperSpriteSheetImporter`, `PaperTiledImporter`, `SmartSnapping` 均为编辑器模块，仅在开发时可用，不会被打包到最终发布版本中。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `32652778` | Harden Paper2D tile map and tile layer PostEditChangeProperty paths against null entries and non-til | 增强图块地图和图块层的属性编辑后通知路径的健壮性，防止空条目和非图块相关属性引发错误。 |
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回退之前的提交 CL53903539。 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 在工具栏添加全局吸附开关，并在启用任一吸附选项时显示红色指示器。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数会产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移至 UE_LOGF 格式。 |

### 维护评价

Paper2D 是一个**历史悠久且仍处于活跃维护状态**的插件。

- **创建时间**：2014年，是 UE4 早期就存在的核心插件。
- **近期更新频率**：非常活跃，在 2026 年 4 月和 5 月有多次提交，内容涉及功能增强（吸附系统改进）、代码健壮性修复和编译警告清理。
- **维护状态**：**积极维护中**。尽管是“文物”，但 Epic 仍在持续进行小规模的改进和修复，保证其在最新 UE 版本中的稳定性和可用性。
- **已知问题/限制**：由于其设计年代较早，某些编辑器交互可能不如现代 UE 编辑器流畅。图块集（Tileset）功能在.uplugin描述中仍标记为“(experimental)”，但整体插件是稳定可用的。
- **推荐使用**：**推荐用于 2D 或 2.5D 游戏项目**。它是 UE 官方提供的、集成度最高的 2D 解决方案，与蓝图、物理、渲染管线无缝结合。对于非常核心的 2D 重度游戏，开发者有时会选择社区插件或自行封装，但 Paper2D 依然是可靠且功能完备的首选起点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/2D/index.html) (Epic 官网搜索 Paper2D 相关文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Tests) (如果存在)