# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 中文名 | 2D纸张 |
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D) | |

## 用途
Paper2D 是 UE5 内置的 2D 游戏开发框架。它解决的核心问题是：**在强大的 3D 引擎中高效地创建和运行 2D 游戏**。它提供了从精灵图、瓦片地图到 2D 物理和渲染的完整工具链，避免了开发者需要完全依赖第三方插件或自造轮子的麻烦。

主要功能包括：
- **精灵（Sprites）与动画**：支持将图片切割成独立的精灵，并创建复杂的骨骼动画或帧动画。
- **瓦片地图（Tile Maps）**：支持正方形、等轴测、六边形等多种瓦片地图编辑，可直接导入 Tiled 等外部编辑器的地图数据。
- **2D 物理**：使用 Paper2D 的简化碰撞系统，支持多边形、圆形等 2D 碰撞形状。
- **专用渲染器**：为 2D 对象优化了渲染管线，性能优于将 2D 元素作为 3D 网格处理。
- **编辑器集成**：提供专用的 2D 视口、资产编辑器和关卡编辑工具。

## 使用场景
- 你在制作 2D 平台跳跃游戏（如《蔚蓝》风格） → 使用 Paper2D 的 TileMap 和 Sprite 功能构建关卡。
- 你需要制作 2D RPG 游戏的地图和角色 → 使用 Paper2D 导入 Tiled 地图数据，并用 Sprite 创建角色动画。
- 你在开发 2D 物理模拟游戏（如《愤怒的小鸟》） → 使用 Paper2D 的 2D 碰撞和物理组件。
- 你想将 2D 素材快速集成到 3D 项目中作为 HUD 或特效 → 使用 Paper2D 的 Sprite 和 SpriteComponent。

## 蓝图用法
Paper2D 提供了丰富的蓝图节点，用于操作 2D 游戏对象。以下是按功能分组的核心节点：

### 精灵与动画

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Sprite` | 设置 SpriteComponent 显示的精灵资产 | `UPaperSpriteComponent` |
| `Set Flipbook` | 设置 FlipbookComponent 播放的动画 Flipbook 资产 | `UPaperFlipbookComponent` |
| `Play` / `Stop` / `Reverse` | 控制 Flipbook 动画的播放、停止和反转 | `UPaperFlipbookComponent` |
| `Set Looping` | 设置动画是否循环播放 | `UPaperFlipbookComponent` |
| `Get Playback Position` | 获取当前动画播放位置 | `UPaperFlipbookComponent` |

### 瓦片地图

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create New Tile Map` | 创建新的瓦片地图资产 | `UPaperTileMapFactory` |
| `Set Tile Map` | 设置 TileMapComponent 使用的瓦片地图资产 | `UPaperTileMapComponent` |
| `Get Tile Map Data` | 获取瓦片地图的详细数据（图层、瓦片信息等） | `UPaperTileMapComponent` |
| `Set Tile` | 在指定位置设置单个瓦片 | `UPaperTileMapComponent` |

### 碰撞

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Collision Enabled` | 启用或禁用 2D 碰撞 | `UPaperSpriteComponent` / `UPaperTileMapComponent` |
| `Set Collision Profile` | 设置碰撞配置文件 | `UPaperSpriteComponent` / `UPaperTileMapComponent` |
| `Add Collision Shape` | 添加自定义 2D 碰撞形状（圆形、多边形等） | `UPaperSpriteComponent` |

### 使用示例（蓝图描述）
要让一个 SpriteComponent 动起来：
1. 创建一个 `PaperFlipbookComponent`。
2. 创建一个 `PaperFlipbook` 资产，其中包含多个 `PaperSprite` 帧。
3. 在蓝图中，使用 `Set Flipbook` 节点将资产赋予组件。
4. 调用 `Play` 节点开始播放动画。

要从 Tiled 导入地图：
1. 在内容浏览器中右键 → 导入到项目。
2. 选择 `.tmx` 或 `.json` 文件。
3. Paper2D 会自动生成对应的 `PaperTileMap` 和 `PaperTileSet` 资产。
4. 将 `PaperTileMap` 拖入场景，自动创建 `PaperTileMapComponent`。

## C++ 用法
Paper2D 的 C++ API 主要用于创建自定义的 2D 游戏逻辑和工具。

### 头文件引入
```cpp
#include "Paper2D.h"
#include "PaperSpriteComponent.h"
#include "PaperFlipbookComponent.h"
#include "PaperTileMapComponent.h"
```

### 基本用法
**创建并操作一个 SpriteComponent：**
```cpp
// 在 Actor 中创建 SpriteComponent
UPaperSpriteComponent* SpriteComp = CreateDefaultSubobject<UPaperSpriteComponent>(TEXT("MySprite"));
SpriteComp->SetSprite(MyPaperSpriteAsset);
SpriteComp->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
```

**播放 Flipbook 动画：**
```cpp
UPaperFlipbookComponent* FlipbookComp = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("MyAnim"));
FlipbookComp->SetFlipbook(MyFlipbookAsset);
FlipbookComp->PlayFromStart();
FlipbookComp->SetLooping(true);
```

**在瓦片地图上操作瓦片：**
```cpp
// 获取瓦片地图组件
UPaperTileMapComponent* TileMapComp = GetPaperTileMapComponent();

// 在坐标 (X, Y) 的图层 LayerIndex 上设置瓦片
FPaperTileInfo TileInfo;
TileInfo.TileSet = MyTileSetAsset;
TileInfo.GetTileIndex() = 5; // 瓦片在 TileSet 中的索引
TileMapComp->SetTile(X, Y, LayerIndex, TileInfo);
```

### 进阶用法
**自定义瓦片地图导入器（参考 PaperTiledImporter 模块）：**
```cpp
// 解析 Tiled 的 JSON 数据
TSharedPtr<FJsonObject> JsonRoot = ParseJsonString(JsonString);
FTileMapFromTiled ParsedMap;
ParsedMap.IsValid();

// 将解析的数据转换为 Paper2D 资产
UPaperTileMap* NewTileMap = CreateNewAsset<UPaperTileMap>(PackagePath, AssetName);
ConvertTileSets(ParsedMap, NewTileMap);
FinalizeTileMap(ParsedMap, NewTileMap);
```

**运行时动态生成碰撞形状：**
```cpp
FSpriteGeometryCollection GeomCollection;
TArray<FTiledObject> CollisionObjects; // 来自导入数据

// 将 Tiled 中定义的碰撞对象转换为 Paper2D 几何形状
FTiledObject::AddToSpriteGeometryCollection(FVector2D::ZeroVector, CollisionObjects, GeomCollection);

// 应用到 SpriteComponent
MySpriteComponent->SetSpriteGeometryCollection(GeomCollection);
```

## 模块依赖
Paper2D 各模块之间依赖关系紧密。要使用此插件，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `Paper2D` | 核心运行时模块，提供所有基础类（Sprite, TileMap, Flipbook 等） |
| `Paper2DEditor` | 编辑器工具，提供资产编辑器和自定义关卡编辑器功能 |
| `PaperTiledImporter` | 导入 Tiled 瓦片地图编辑器的 `.tmx`/`.json` 文件 |
| `PaperSpriteSheetImporter` | 从精灵表（Sprite Sheet）中批量导入精灵 |
| `SmartSnapping` | 提供 2D 元素间的智能对齐和吸附功能 |
| `SpriterImporter` | 导入 Spriter 骨骼动画工具的文件 |

**特殊依赖**：Paper2D 运行时模块依赖 `PhysicsCore` 和 `NavigationSystem` 用于 2D 物理和寻路。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `32652778` | Harden Paper2D tile map and tile layer PostEditChangeProperty paths against null entries and non-til | 增强瓦片地图和瓦片图层的编辑器属性修改路径，防止空条目和非瓦片数据崩溃 |
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回退了之前的某项更改 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 工具栏添加全局吸附开关，启用时显示红色指示器 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下将双精度常量截断为浮点数的代码警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 迁移至新版 UE_LOGF 宏 |

### 维护评价
- **年龄**：创建于 2014 年，已有 12 年历史，是 UE4 早期就存在的成熟插件。
- **维护状态**：**活跃维护**。最近半年有多次实质性更新（修复崩溃、改进编辑器 UX、代码现代化），表明 Epic 仍在关注此插件。
- **已知限制**：
  1. 瓦片地图功能仍标记为“实验性”（但 .uplugin 中 `IsBetaVersion=false`）。
  2. 不支持 3D 视角的 2D 游戏（如 2.5D 等轴测视角需要自行处理）。
  3. 物理系统是简化的 2D 物理，无法替代完整的 Box2D 等专业物理引擎。
  4. 社区资料相对较少，很多高级功能需要直接阅读源码。
- **推荐使用**：**强烈推荐**。对于中等复杂度的 2D 游戏（特别是平台跳跃、RPG、策略类），Paper2D 是 UE5 中最成熟、集成度最高的解决方案。对于需要物理模拟的重度 2D 游戏，可能需要结合其他物理引擎。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/2D/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Tests)

# PaperTiledImporter

> Paper2D Tiled Map Importer

| 属性 | 值 |
|---|---|
| 中文名 | 瓦片地图导入器 |
| 分类 | 2D |
| 默认启用 | ✅ 是（作为 Paper2D 插件的一部分） |
| 包含内容 | ❌ 无 |
| 模块 | `PaperTiledImporter` (Editor) |
| 实验性 | 否（但导入的瓦片地图功能整体标记为实验性） |
| 创建时间 | 2014-09-16（与 Paper2D 同期） |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Source/PaperTiledImporter) | |

## 用途
PaperTiledImporter 是 Paper2D 插件中的一个编辑器专用模块，核心功能是**将 Tiled 地图编辑器（[Tiled Map Editor](https://www.mapeditor.org/)）导出的 `.json` 或 `.tmx` 文件导入到 UE5 中**。

它解决的具体问题是：
- **数据格式转换**：将 Tiled 的 JSON/TMX 数据结构（包含图层、瓦片集、对象、属性等）解析并转换为 UE5 可用的 `UPaperTileMap`、`UPaperTileSet` 等资产。
- **资产创建**：自动处理纹理导入、瓦片集切割、碰撞形状生成等复杂步骤，一次性生成完整的关卡资源。
- **重新导入支持**：允许在 Tiled 中修改后，更新已导入的地图资产，保留部分引擎内修改（如光照、额外 Actor 放置）。

## 使用场景
- 你使用 Tiled 编辑器作为关卡设计主工具 → 用此模块将设计好的地图无缝导入 UE5。
- 你的美术团队习惯使用 Tiled 进行瓦片地图创作 → 自动化流水线可直接从 `.json` 文件生成游戏关卡。
- 你需要在 Tiled 中定义简单的碰撞和逻辑触发区 → 导入时会自动转换为 Paper2D 的碰撞几何或游戏对象。
- 你希望批量更新多个关卡地图 → 使用重新导入功能快速同步修改。

## 蓝图用法
**此模块没有暴露任何蓝图可调用节点**。它是一个纯编辑器模块，所有功能都通过编辑器界面触发。

**在编辑器中的使用方式：**
1. **导入**：
   - 在内容浏览器中右键 → **导入到项目**。
   - 选择 `.json` 或 `.tmx` 文件。
   - 在导入对话框中选择目标路径和选项。
2. **重新导入**：
   - 在内容浏览器中右键已导入的 `PaperTileMap` 资产 → **重新导入**。
   - 或双击资产打开编辑器，在编辑器内选择重新导入。

## C++ 用法
此模块主要由引擎内部的资产工厂类使用，开发者通常不直接调用其 API。但了解其内部结构有助于自定义导入行为。

### 头文件引入
```cpp
#include "PaperTiledImporterFactory.h" // 核心工厂类
```

### 基本用法
**检查文件是否可被导入：**
```cpp
UPaperTiledImporterFactory Factory;
FString FilePath = TEXT("Path/To/YourMap.json");
if (Factory.FactoryCanImport(FilePath))
{
    UE_LOG(LogTemp, Log, TEXT("File %s is a valid Tiled map."), *FilePath);
}
```

**手动触发导入（高级用法，通常由引擎的导入系统调用）：**
```cpp
UPaperTiledImporterFactory* ImporterFactory = NewObject<UPaperTiledImporterFactory>();
UObject* ImportedAsset = ImporterFactory->FactoryCreateText(
    UPaperTileMap::StaticClass(),
    GetTransientPackage(),
    FName("MyImportedMap"),
    RF_NoFlags,
    nullptr,
    TEXT("JSON"), // 文件类型
    JsonStringBuffer,
    JsonStringBufferEnd,
    Warn
);
```

### 进阶用法
**自定义 Tiled 属性映射：**
PaperTiledImporter 解析 Tiled 中对象的自定义属性（Key-Value pairs）。你可以通过继承工厂类并重写解析方法，将特定属性映射到 UE5 的游戏逻辑：

```cpp
// 假设你在 Tiled 中为对象定义了 "SpawnType" 属性
struct FTiledObject
{
    TArray<FTiledStringPair> Properties; // 包含 {"SpawnType": "Enemy"}
    // ...
};

// 在自定义的导入后处理中读取
for (const FTiledStringPair& Prop : TiledObject.Properties)
{
    if (Prop.Key == TEXT("SpawnType"))
    {
        if (Prop.Value == TEXT("Enemy"))
        {
            // 在导入的地图中生成一个敌人生成器Actor
        }
    }
}
```

**注意**：直接修改 `PaperTiledImporter` 模块需要重新编译引擎插件。更推荐的做法是使用 `Paper2DEditor` 模块提供的钩子，或在导入后通过蓝图/Python脚本处理资产。

## Demo 示例
以下是一个极简示例，展示如何在 C++ 中使用 `PaperTiledImporterFactory` 来检查文件类型。实际的导入过程由编辑器的资产导入系统自动处理。

```cpp
// MyTiledUtils.h
#pragma once
#include "CoreMinimal.h"
#include "PaperTiledImporterFactory.h"

class FMyTiledUtils
{
public:
    static bool IsTiledMapFile(const FString& FilePath);
};
```

```cpp
// MyTiledUtils.cpp
#include "MyTiledUtils.h"
#include "PaperTiledImporterLog.h"

bool FMyTiledUtils::IsTiledMapFile(const FString& FilePath)
{
    UPaperTiledImporterFactory* Factory = NewObject<UPaperTiledImporterFactory>();
    bool bCanImport = Factory->FactoryCanImport(FilePath);
    
    if (bCanImport)
    {
        UE_LOG(LogPaperTiledImporter, Log, TEXT("Valid Tiled map: %s"), *FilePath);
    }
    return bCanImport;
}
```

## 模块依赖
要使用此模块（通常作为 Paper2D 的一部分），你的项目需要依赖：

| 模块 | 用途 |
|---|---|
| `Paper2D` | 提供被导入的核心资产类型（PaperTileMap, PaperTileSet） |
| `Paper2DEditor` | 提供资产编辑器界面和后处理逻辑 |
| `Json` | 解析 Tiled 导出的 JSON 文件 |
| `Slate`, `SlateCore` | 导入对话框的 UI 框架 |

**注意**：此模块是 `Editor` 类型，仅在编辑器中可用，打包后的游戏不包含此代码。

## 维护状态
作为 Paper2D 的子模块，其维护状态与主插件一致。

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `32652778` | Harden Paper2D tile map and tile layer PostEditChangeProperty paths against null entries and non-til | 直接增强了瓦片地图导入后的编辑器稳定性 |

### 维护评价
- **活跃度**：与主插件同步更新，最近有稳定性改进。
- **状态**：**维护中**。虽然 Tiled 导入是成熟功能，但 Epic 仍在修复相关崩溃和问题。
- **建议**：对于使用 Tiled 工作的团队，此模块是稳定可用的。注意备份导入的资产，因为重新导入有时可能覆盖在引擎内进行的修改。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Source/PaperTiledImporter)
- [Tiled 官网](https://www.mapeditor.org/)
- [Paper2D 总体文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/2D/)