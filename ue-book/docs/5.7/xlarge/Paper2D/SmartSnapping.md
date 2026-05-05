# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是 Unreal Engine 中唯一的官方 2D 游戏开发框架。它解决的核心问题是：**如何在以 3D 为核心引擎的 UE 中，高效地创建、编辑和运行 2D 游戏内容**。

它不仅仅是一个渲染器，而是一套完整的工具链，包括：
1.  **运行时核心**：提供 2D 精灵（Sprite）、图块（Tile）、动画、物理和渲染的运行时支持。
2.  **编辑器工具**：集成在 UE 编辑器中，提供 2D 视口、图块地图编辑器、精灵编辑器等，让 2D 内容的创建流程与 3D 一样直观。
3.  **资源导入器**：支持从外部工具（如 TexturePacker、Tiled Map Editor）导入精灵图集和图块地图。

其存在意义在于让开发者能够利用 UE 强大的编辑器、蓝图系统、物理引擎、音频系统等，来制作 2D 游戏，而无需从零开始构建所有工具。

## 使用场景

-   你正在制作一个 **2D 平台跳跃游戏**，需要角色动画、平台碰撞和视差滚动背景 → 使用 Paper2D 的 `PaperCharacter`、`PaperFlipbook` 和 `PaperTileMap`。
-   你需要使用 **Tiled Map Editor** 等外部工具设计关卡，并导入到 UE 中 → 使用 `PaperTiledImporter` 模块。
-   你希望为 2D 精灵添加 **基于物理的碰撞和模拟**（如布娃娃、抛射物） → Paper2D 的 2D 物理组件可以与 UE 的 Chaos 物理系统集成。
-   你需要在编辑器中 **直观地绘制和编辑基于图块的关卡** → 使用 Paper2D 提供的图块地图编辑器模式。

## 蓝图用法

Paper2D 提供了丰富的蓝图 API，主要围绕其核心资产类型和组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateFlipbookComponent` | 创建一个用于播放翻书动画（Flipbook）的组件 | `UPaperFlipbookLibrary` |
| `SetFlipbook` | 为翻书组件设置要播放的动画资产 | `UPaperFlipbookComponent` |
| `SetSpriteColor` | 设置精灵组件的颜色和不透明度 | `UPaperSpriteComponent` |
| `GetTileMap` | 从图块地图组件获取关联的图块地图资产 | `UPaperTileMapComponent` |
| `SetTile` | 设置图块地图中特定位置的图块 | `UPaperTileMapComponent` |
| `MakeTileMapEditable` | 将图块地图组件切换到可编辑模式（用于运行时动态修改） | `UPaperTileMapComponent` |

### 使用示例（蓝图描述）

1.  **创建一个可控制的 2D 角色**：
    -   创建一个继承自 `APaperCharacter` 的蓝图类。
    -   在组件面板中，为其 `Sprite` 组件指定一个 `PaperSprite` 资产作为默认外观。
    -   添加一个 `PaperFlipbookComponent`，并为其 `Flipbook` 属性指定一个包含角色行走动画的 `PaperFlipbook` 资产。
    -   在事件图表中，使用 `InputAxis MoveRight` 事件，通过 `AddMovementInput` 节点控制角色移动，并根据移动方向翻转 `Sprite` 或 `Flipbook` 组件的 `RelativeScale3D.X`。

2.  **动态生成图块地图**：
    -   在场景中放置一个 `PaperTileMapActor`。
    -   在蓝图中获取其 `PaperTileMapComponent` 的引用。
    -   使用 `SetTile` 节点，在循环中根据游戏逻辑（如随机地形生成）设置每个坐标的图块索引和图块集。

## C++ 用法

Paper2D 的 C++ API 是其蓝图功能的基础，提供了更底层和高效的控制。

### 头文件引入

```cpp
#include "Paper2D/Classes/PaperSprite.h"
#include "Paper2D/Classes/PaperFlipbook.h"
#include "Paper2D/Classes/PaperTileMap.h"
#include "Paper2D/Classes/PaperCharacter.h"
```

### 基本用法

以下示例展示如何在 C++ 中创建和配置一个 Paper2D 精灵组件。
（来源：基于 `PaperSpriteComponent` 和 `PaperFlipbookComponent` 的典型用法模式）

```cpp
// MyActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UPaperSpriteComponent;
class UPaperFlipbookComponent;
class UPaperSprite;
class UPaperFlipbook;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D")
    UPaperSpriteComponent* SpriteComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D")
    UPaperFlipbookComponent* FlipbookComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Paper2D")
    UPaperSprite* MySpriteAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Paper2D")
    UPaperFlipbook* MyFlipbookAsset;
};

// MyActor.cpp
#include "MyActor.h"
#include "PaperSpriteComponent.h"
#include "PaperFlipbookComponent.h"

AMyActor::AMyActor()
{
    // 创建并设置根组件为精灵组件
    SpriteComponent = CreateDefaultSubobject<UPaperSpriteComponent>(TEXT("Sprite"));
    RootComponent = SpriteComponent;

    // 创建翻书动画组件并附加到精灵组件
    FlipbookComponent = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("Flipbook"));
    FlipbookComponent->SetupAttachment(SpriteComponent);

    // 在构造函数中设置资产（通常在编辑器中设置更佳）
    // SpriteComponent->SetSprite(MySpriteAsset);
    // FlipbookComponent->SetFlipbook(MyFlipbookAsset);
    // FlipbookComponent->Play(); // 开始播放动画
}
```

### 进阶用法

结合图块地图组件进行运行时操作。
（来源：基于 `UPaperTileMapComponent` 的 API 和测试用例模式）

```cpp
// 在某个游戏逻辑类中
void AMyGameMode::GenerateLevel()
{
    // 假设已经获取到场景中的 PaperTileMapActor
    APaperTileMapActor* TileMapActor = ...;
    UPaperTileMapComponent* TileMapComp = TileMapActor->GetRenderComponent();

    if (TileMapComp && TileMapComp->TileMap)
    {
        // 获取图块地图的尺寸
        int32 MapWidth, MapHeight, NumLayers;
        TileMapComp->TileMap->GetMapSize(MapWidth, MapHeight, NumLayers);

        // 遍历并设置图块
        for (int32 X = 0; X < MapWidth; ++X)
        {
            for (int32 Y = 0; Y < MapHeight; ++Y)
            {
                // 根据某种算法（如柏林噪声）决定图块索引
                int32 TileIndex = CalculateTileIndex(X, Y);
                // 设置第0层，坐标(X,Y)处的图块
                TileMapComp->SetTile(X, Y, 0, FPaperTileInfo(TileIndex));
            }
        }
        // 修改后需要通知组件数据已变更
        TileMapComp->RebuildCollision();
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个带有静态精灵和动画的 Actor。

```cpp
// Paper2DDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "Paper2DDemoActor.generated.h"

class UPaperSpriteComponent;
class UPaperFlipbookComponent;

UCLASS()
class APaper2DDemoActor : public AActor
{
    GENERATED_BODY()

public:
    APaper2DDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, Category = "Components")
    UPaperSpriteComponent* SpriteComp;

    UPROPERTY(VisibleAnywhere, Category = "Components")
    UPaperFlipbookComponent* FlipbookComp;

    // 在编辑器中指定的资产
    UPROPERTY(EditAnywhere, Category = "Paper2D")
    class UPaperSprite* IdleSprite;

    UPROPERTY(EditAnywhere, Category = "Paper2D")
    class UPaperFlipbook* RunAnimation;
};

// Paper2DDemoActor.cpp
#include "Paper2DDemoActor.h"
#include "PaperSpriteComponent.h"
#include "PaperFlipbookComponent.h"

APaper2DDemoActor::APaper2DDemoActor()
{
    // 创建静态精灵组件作为默认外观
    SpriteComp = CreateDefaultSubobject<UPaperSpriteComponent>(TEXT("StaticSprite"));
    RootComponent = SpriteComp;

    // 创建翻书动画组件，用于播放动画
    FlipbookComp = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("Animation"));
    FlipbookComp->SetupAttachment(RootComponent);
    // 默认隐藏动画组件
    FlipbookComp->SetVisibility(false);
}

void APaper2DDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 设置资产（如果在编辑器中未设置）
    if (IdleSprite)
    {
        SpriteComp->SetSprite(IdleSprite);
    }

    if (RunAnimation)
    {
        FlipbookComp->SetFlipbook(RunAnimation);
        // 示例：2秒后切换到动画状态
        FTimerHandle TimerHandle;
        GetWorldTimerManager().SetTimer(TimerHandle, [this]()
        {
            SpriteComp->SetVisibility(false);
            FlipbookComp->SetVisibility(true);
            FlipbookComp->Play();
        }, 2.0f, false);
    }
}
```

## 模块依赖

Paper2D 插件的模块依赖如下（已省略 Core, CoreUObject, Engine 等通用依赖）：

| 模块 | 用途 |
|---|---|
| `EditorFramework` | Paper2D 编辑器工具与 UE 编辑器框架集成 |
| `UnrealEd` | Paper2D 编辑器模块（如图块地图编辑器）的核心依赖 |
| `ContentBrowser` | 用于在内容浏览器中集成 Paper2D 资产的创建和导入操作 |
| `AssetTools` | 用于注册 Paper2D 特有的资产类型和操作 |
| `PropertyEditor` | 用于自定义 Paper2D 资产（如 PaperSprite, PaperTileMap）在细节面板中的显示 |
| `Slate`, `SlateCore` | 用于构建 Paper2D 编辑器自定义 UI（如图块集选择器、动画时间轴） |
| `RenderCore`, `RHI` | Paper2D 运行时渲染模块的底层图形接口依赖 |
| `PhysicsCore` | 用于将 Paper2D 的 2D 碰撞几何体与 UE 物理系统集成 |

## 维护状态

### 近期更新

```
- 2025-10-03 a0ebf8dd47ad [Viewport Toolbar] Update level editor viewport toolbar icons
- 2025-09-15 82ef0e8c29a8 Rename "Enable Planar Snapping" to just "Planar"
- 2025-08-20 fc49b3b34f87 Fix C4855: implicit capture of 'this' via '[=]' is deprecated in '/std:c++20'
```

### 维护评价

Paper2D 是一个**历史悠久但仍在维护**的插件。

-   **年龄**：创建于 2014 年，是 UE 中“元老级”的插件之一。
-   **活跃度**：从近期提交记录看，它仍在被维护。最近的更新主要是**兼容性修复**（如 C++20 标准适配）和**编辑器 UI 微调**（如工具栏图标更新、属性重命名），而非重大功能添加。
-   **状态**：它处于一种**稳定维护**状态。核心功能已经非常成熟和完整，Epic 团队主要确保其与新版 UE 的兼容性，而不是积极开发新特性。
-   **限制**：其“实验性”的图块集（Tileset）功能多年来一直未正式转为稳定版。对于复杂的 2D 游戏，其性能和工作流可能不如一些专门的第三方 2D 引擎。
-   **推荐**：**推荐使用**。对于希望在 UE 生态内开发 2D 游戏（尤其是需要与 3D 元素混合、或利用 UE 强大编辑器和蓝图系统的项目）的开发者来说，Paper2D 仍然是官方且可靠的选择。它足够稳定，能够满足大多数 2D 游戏的需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/paper-2d-in-unreal-engine/)