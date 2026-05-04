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

Paper2D 是 Unreal Engine 内置的 2D 游戏开发工具集。它并非一个简单的 2D 渲染器，而是一套完整的解决方案，旨在解决在 UE 这个以 3D 为核心的引擎中高效制作 2D 内容的核心问题。它提供了：

1.  **2D 资产管线**：将 2D 图片（PNG, TGA 等）转换为引擎可高效管理的 `UPaperSprite` 资产，并支持从精灵表（Sprite Sheet）批量导入。
2.  **2D 动画系统**：通过 `UPaperFlipbook` 和 `UPaperFlipbookComponent` 实现基于帧序列的 2D 动画，类似于传统 2D 游戏的动画播放方式。
3.  **2D 关卡构建**：提供 `UPaperTileMap` 和 `UPaperTileMapComponent`，允许开发者使用图块（Tile）像搭积木一样快速构建 2D 关卡地图，并支持图块集（Tileset）和图块层（Tile Layer）。
4.  **2D 物理与碰撞**：集成了 Box2D 物理引擎，并通过 `UPaperSprite` 的碰撞几何体和 `UPaperCharacter` 等组件，为 2D 游戏提供物理模拟和碰撞检测。
5.  **2D 渲染优化**：针对 2D 精灵和图块地图进行了渲染批处理优化，以提升大量 2D 对象的渲染性能。

它存在的意义是让熟悉 UE 工作流的开发者能够无缝地进入 2D 游戏开发领域，同时利用 UE 强大的编辑器、蓝图、物理和跨平台能力。

## 使用场景

-   你正在开发一款 **2D 平台跳跃游戏**（如《空洞骑士》风格），需要角色动画、平台碰撞和简单的物理效果 → 使用 `PaperCharacter`、`PaperFlipbook` 和 `PaperSprite` 的碰撞设置。
-   你需要制作一款 **俯视角 2D RPG 或策略游戏**，使用图块来构建庞大的游戏世界 → 使用 `PaperTileMap` 和 `PaperTileSet` 进行关卡设计。
-   你有一个 **2D 像素美术风格的游戏**，需要从 Aseprite 或 TexturePacker 导出的精灵表中快速生成动画 → 使用 `PaperSpriteSheetImporter` 模块。
-   你需要在 UE 中快速原型化一个 **2D 游戏玩法**，希望利用蓝图的快速迭代能力，而不是从头编写渲染和物理代码 → Paper2D 提供了完整的蓝图 API。
-   你希望将现有的 **2D 游戏逻辑** 移植到 UE，以利用其网络、音频、UI (UMG) 和打包发布系统。

## 蓝图用法

Paper2D 提供了丰富的蓝图节点，主要围绕其核心资产和组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Flipbook` | 从一系列 `PaperSprite` 创建一个 `PaperFlipbook` 资产。 | `UPaperFlipbookLibrary` |
| `Set Flipbook` | 为 `PaperFlipbookComponent` 设置要播放的动画。 | `UPaperFlipbookComponent` |
| `Play` / `Reverse` / `Stop` | 控制 `PaperFlipbookComponent` 的动画播放。 | `UPaperFlipbookComponent` |
| `Set Sprite` | 为 `PaperSpriteComponent` 设置显示的精灵。 | `UPaperSpriteComponent` |
| `Set Tile Map` | 为 `PaperTileMapComponent` 设置要渲染的图块地图数据。 | `UPaperTileMapComponent` |
| `Set Tile` | 在运行时动态修改 `PaperTileMapComponent` 中某个位置的图块。 | `UPaperTileMapComponent` |
| `Get Tile Map` / `Set Tile Map` | 获取或设置 `PaperTileMap` 资产的图块数据。 | `UPaperTileMap` |
| `Add Collision` / `Remove Collision` | 为 `PaperSprite` 添加或移除简单的碰撞几何体（盒体、圆形、多边形）。 | `UPaperSprite` |
| `Set Collision Enabled` | 动态启用或禁用 `PaperSpriteComponent` 的碰撞。 | `UPaperSpriteComponent` |
| `Set Sprite Color` | 设置精灵组件的着色颜色（Tint）。 | `UPaperSpriteComponent` |

### 使用示例（蓝图描述）

**创建一个带动画的 2D 角色：**
1.  在内容浏览器中，右键创建 `Paper Flipbook` 资产。
2.  打开该资产，将角色的各个动作帧（`PaperSprite`）拖入时间轴，并设置每帧的持续时间。
3.  在场景中放置一个 `Paper Character` 或 `Paper Flipbook Component`。
4.  在组件的细节面板中，将 `Flipbook` 属性设置为上一步创建的动画资产。
5.  通过蓝图，调用 `Set Flipbook` 节点可以在运行时切换不同的动画（如 Idle, Run, Jump）。

**动态修改图块地图：**
1.  在场景中放置一个 `Paper Tile Map Actor`。
2.  在蓝图中，获取该 Actor 的 `Paper Tile Map Component` 引用。
3.  使用 `Set Tile` 节点，指定图块层索引、X/Y 坐标和新的图块索引，即可在游戏运行时（如玩家挖掘）改变地图。

## C++ 用法

### 头文件引入

```cpp
#include "Paper2D.h"
#include "PaperSprite.h"
#include "PaperFlipbook.h"
#include "PaperFlipbookComponent.h"
#include "PaperTileMap.h"
#include "PaperTileMapComponent.h"
```

### 基本用法

**创建并配置一个 PaperSpriteComponent (来自测试用例 `Paper2DTests.cpp`):**
```cpp
// 假设已有一个有效的 UPaperSprite* SpriteAsset
UPaperSpriteComponent* SpriteComp = NewObject<UPaperSpriteComponent>(OwnerActor);
SpriteComp->SetSprite(SpriteAsset);
SpriteComp->SetRelativeLocation(FVector(0.f, 0.f, 0.f));
SpriteComp->SetRelativeRotation(FRotator(0.f, 0.f, 0.f));
SpriteComp->RegisterComponent();
```

**播放一个 PaperFlipbook (来自测试用例 `Paper2DTests.cpp`):**
```cpp
UPaperFlipbookComponent* FlipbookComp = NewObject<UPaperFlipbookComponent>(OwnerActor);
FlipbookComp->SetFlipbook(MyFlipbookAsset);
FlipbookComp->RegisterComponent();
FlipbookComp->Play(); // 从头开始播放
FlipbookComp->SetLooping(true); // 设置循环播放
```

### 进阶用法

**在运行时动态修改图块地图数据 (结合 `PaperTileMap` API):**
```cpp
// 获取图块地图组件
UPaperTileMapComponent* TileMapComp = OwnerActor->FindComponentByClass<UPaperTileMapComponent>();
if (TileMapComp)
{
    // 获取底层的图块地图数据资产
    UPaperTileMap* TileMapData = TileMapComp->GetTileMap();
    if (TileMapData)
    {
        // 在 (5, 3) 位置，第0层，设置为索引为10的图块
        TileMapData->SetTile(0, 5, 3, FPaperTileInfo(10));
        // 通知组件数据已更改，需要重新构建渲染数据
        TileMapComp->RebuildCollision();
        TileMapComp->RebuildRenderData();
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个带有动画的 Paper2D 角色组件。

**MyPaperCharacter.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyPaperCharacter.generated.h"

class UPaperFlipbookComponent;
class UPaperFlipbook;

UCLASS()
class AMyPaperCharacter : public AActor
{
    GENERATED_BODY()

public:
    AMyPaperCharacter();

protected:
    virtual void BeginPlay() override;

    // 动画组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D")
    UPaperFlipbookComponent* FlipbookComponent;

    // 动画资产（可在编辑器中设置）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Paper2D")
    UPaperFlipbook* IdleAnimation;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Paper2D")
    UPaperFlipbook* RunAnimation;
};
```

**MyPaperCharacter.cpp**
```cpp
#include "MyPaperCharacter.h"
#include "PaperFlipbookComponent.h"
#include "PaperFlipbook.h"

AMyPaperCharacter::AMyPaperCharacter()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并设置根组件为动画组件
    FlipbookComponent = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("FlipbookComp"));
    RootComponent = FlipbookComponent;

    // 默认启用碰撞
    FlipbookComponent->SetCollisionProfileName(TEXT("Pawn"));
    FlipbookComponent->SetGenerateOverlapEvents(true);
}

void AMyPaperCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 如果设置了闲置动画，则开始播放
    if (IdleAnimation)
    {
        FlipbookComponent->SetFlipbook(IdleAnimation);
        FlipbookComponent->Play();
        FlipbookComponent->SetLooping(true);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | Paper2D 运行时模块意外地依赖了此编辑器框架模块，可能用于某些资产编辑器的底层支持。 |
| `UnrealEd` | 同上，运行时模块依赖了编辑器模块，这在插件中不常见，可能是历史遗留或特定功能所需。 |

## 维护状态

### 近期更新

```
- 2023-10-26 4a6d973b1db6 修复了一些已弃用的FString用法。
- 2023-09-15 64658cf6ae5e GetAssetRegistryTags 弃用：将旧的 GetAssetRegistryTags 及相关函数标记为弃用。升级了 Epic 代码中所有的重写和调用点。
- 2023-08-20 da92084a122a 优化掉了更多私有模块的包含和依赖。
```

### 维护评价

Paper2D 是一个 **创建于 2014 年的“文物”级插件**。从最近的提交记录来看，过去几年的更新主要集中在 **维护性工作** 上，如修复编译器警告、适配引擎 API 的弃用变更、优化构建依赖等，**没有实质性的新功能开发**。

-   **年龄**：超过 10 年，是 UE 中历史最悠久的插件之一。
-   **活跃度**：维护不活跃。最近一次功能性更新可能要追溯到 UE 4.x 时代。Epic 的开发重心已明显转向 3D、虚拟制片和 UE for Fortnite (UEFN)。
-   **已知问题/限制**：
    1.  **实验性图块集**：.uplugin 描述中提到的 Tilesets 仍标记为实验性，多年未变。
    2.  **性能**：对于海量精灵或超大图块地图，其性能可能不如专门为 2D 优化的引擎（如 Godot）。
    3.  **功能停滞**：缺少现代 2D 引擎的常见功能，如更高级的骨骼动画、粒子编辑器、光照系统等。
-   **推荐使用**：
    -   **推荐**：如果你的项目是 **中等规模、以 UE 为主要引擎、且 2D 内容不是极端复杂** 的 2D 或 2.5D 游戏，Paper2D 仍然是一个稳定、可用且能充分利用 UE 生态（蓝图、物理、音频、打包）的选择。
    -   **不推荐**：如果你追求 **最前沿的 2D 开发功能、极致的 2D 渲染性能，或者项目是纯 2D 且规模庞大**，那么考虑 Unity 2D 或 Godot 等专业 2D 引擎可能是更好的选择。

**警告：该插件已超过 1 年没有实质性功能更新，处于维护模式。**

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/2DGameDevelopment/2DGameDevelopment/)(UE 官方 2D 开发文档入口，内容较旧)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D/Tests)