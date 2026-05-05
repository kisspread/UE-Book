# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（2D游戏资产） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是在 Unreal Engine 中进行 2D 游戏开发的核心工具集。它解决了一个根本问题：如何在以 3D 为核心架构的引擎中高效、直观地创建 2D 游戏内容。该插件提供了一整套从资产导入、编辑到运行时渲染的完整工作流，包括精灵（Sprite）、图块集（Tile Set）、2D 物理、动画以及专门的关卡编辑工具，使得开发者无需从零开始构建 2D 游戏框架。

## 使用场景

-   **2D 平台跳跃游戏**：使用 `PaperCharacter` 作为玩家角色，利用 `PaperFlipbook` 制作角色动画，通过 `PaperTileMap` 快速搭建关卡地形。
-   **俯视角或等距视角的 2D 游戏**：利用图块集（Tile Set）和图块地图（Tile Map）高效地构建大型、可重复使用的关卡。
-   **像素艺术游戏**：导入像素风格的精灵表（Sprite Sheet），并使用 Paper2D 的工具进行切片和动画制作。
-   **需要 2D 元素的 3D 游戏**：在 3D 场景中嵌入 2D 精灵作为 UI 元素、特效或装饰物。

## 蓝图用法

Paper2D 提供了丰富的蓝图节点，主要围绕其核心资产类型和组件。详细 API 请参阅各模块文档。

### 核心节点类型

| 节点类型 | 说明 | 所在模块 |
|---|---|---|
| **精灵 (Sprite) 操作** | 创建、编辑和查询 `UPaperSprite` 资产。 | `Paper2D` |
| **翻页书 (Flipbook) 操作** | 控制 `UPaperFlipbook` 动画的播放、暂停和状态查询。 | `Paper2D` |
| **图块集 (Tile Set) 操作** | 管理 `UPaperTileSet`，获取图块信息。 | `Paper2D` |
| **图块地图 (Tile Map) 操作** | 动态修改 `UPaperTileMap` 的图块数据。 | `Paper2D` |
| **渲染组件** | `UPaperSpriteComponent`, `UPaperFlipbookComponent`, `UPaperTileMapComponent` 用于在场景中显示 2D 内容。 | `Paper2D` |
| **角色组件** | `UPaperCharacter` 和 `UPaperCharacterMovementComponent` 提供 2D 角色的移动和物理支持。 | `Paper2D` |

### 使用示例（蓝图描述）

1.  **创建一个会动的 2D 角色**：
    -   创建一个继承自 `PaperCharacter` 的蓝图类。
    -   在组件面板中，为其添加一个 `PaperFlipbookComponent` 作为根组件。
    -   在事件图表中，使用 `Set Flipbook` 节点根据移动方向切换不同的动画翻页书。
2.  **动态生成图块地图**：
    -   使用 `Create Tile Map` 节点在运行时生成一个新的图块地图资产。
    -   使用 `Set Tile` 节点循环设置地图中每个位置的图块索引和图块集。
    -   将生成的图块地图资产赋给一个 `PaperTileMapComponent` 进行显示。

## C++ 用法

### 头文件引入

```cpp
#include "Paper2D/Classes/PaperSprite.h"
#include "Paper2D/Classes/PaperFlipbook.h"
#include "Paper2D/Classes/PaperTileMap.h"
#include "Paper2D/Classes/PaperCharacter.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建和操作 Paper2D 的核心对象。

```cpp
// 来源：基于 Paper2D 模块的典型用法
// 1. 加载一个精灵资产
UPaperSprite* MySprite = LoadObject<UPaperSprite>(nullptr, TEXT("/Game/Sprites/MySprite.MySprite"));

// 2. 创建一个精灵组件并附加到 Actor
UPaperSpriteComponent* SpriteComp = NewObject<UPaperSpriteComponent>(MyActor);
SpriteComp->SetSprite(MySprite);
SpriteComp->RegisterComponent();
MyActor->AddInstanceComponent(SpriteComp);

// 3. 控制翻页书动画
UPaperFlipbookComponent* FlipbookComp = MyActor->FindComponentByClass<UPaperFlipbookComponent>();
if (FlipbookComp)
{
    FlipbookComp->Play(); // 播放动画
    FlipbookComp->SetPlaybackPosition(0.0f, true); // 重置到开头
}
```

### 进阶用法

结合多个模块的功能，实现更复杂的逻辑。

```cpp
// 来源：结合 Paper2D 和 Paper2DEditor 模块的思路
// 在编辑器工具中，批量处理精灵资产
void BatchProcessSprites(const TArray<FAssetData>& SpriteAssets)
{
    for (const FAssetData& AssetData : SpriteAssets)
    {
        UPaperSprite* Sprite = Cast<UPaperSprite>(AssetData.GetAsset());
        if (Sprite)
        {
            // 修改精灵的源纹理区域或碰撞形状
            // ... 具体操作 ...
            Sprite->PostEditChange(); // 标记为已修改
            Sprite->MarkPackageDirty();
        }
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个简单的 Paper2D 角色。

**MyPaperCharacter.h**
```cpp
#pragma once
#include "PaperCharacter.h"
#include "MyPaperCharacter.generated.h"

UCLASS()
class AMyPaperCharacter : public APaperCharacter
{
    GENERATED_BODY()

public:
    AMyPaperCharacter();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D", meta = (AllowPrivateAccess = "true"))
    UPaperFlipbookComponent* IdleFlipbookComp;
};
```

**MyPaperCharacter.cpp**
```cpp
#include "MyPaperCharacter.h"
#include "PaperFlipbookComponent.h"
#include "PaperFlipbook.h"

AMyPaperCharacter::AMyPaperCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建并设置翻页书组件作为根组件
    IdleFlipbookComp = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("IdleFlipbook"));
    IdleFlipbookComp->SetupAttachment(RootComponent);
    // 假设有一个名为 IdleAnimation 的翻页书资产
    static ConstructorHelpers::FObjectFinder<UPaperFlipbook> IdleAnimAsset(TEXT("/Game/Animations/IdleAnimation.IdleAnimation"));
    if (IdleAnimAsset.Succeeded())
    {
        IdleFlipbookComp->SetFlipbook(IdleAnimAsset.Object);
    }
}

void AMyPaperCharacter::BeginPlay()
{
    Super::BeginPlay();
    IdleFlipbookComp->Play(); // 开始播放待机动画
}

void AMyPaperCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 可以在此处添加自定义逻辑，例如根据输入切换动画
}
```

## 模块依赖

Paper2D 插件本身包含多个模块，对于使用者而言，主要依赖关系如下：

| 模块 | 用途 |
|---|---|
| `Paper2D` | **核心运行时模块**。包含所有 2D 资产类型（Sprite, Flipbook, TileMap）和组件。你的游戏模块需要依赖此模块。 |
| `Paper2DEditor` | **编辑器扩展模块**。提供资产编辑器、自定义细节面板和关卡编辑工具。仅在编辑器环境下需要。 |
| `PaperSpriteSheetImporter` | **编辑器工具**。用于从精灵表图片导入和切片精灵。 |
| `PaperTiledImporter` | **编辑器工具**。用于导入 Tiled 地图编辑器（.tmx）格式的文件。 |
| `SmartSnapping` | **编辑器工具**。提供智能对齐和吸附功能，辅助 2D 关卡布局。 |

**注意**：`SpriterImporter` 模块（用于导入 Spriter 动画）在提供的模块列表中存在，但未在 .uplugin 的 Modules 数组中声明，可能为遗留或未启用模块。

## 维护状态

### 近期更新

（基于典型维护模式推断，具体 commit 需查询仓库）
- 2024-XX-XX `xxxxxxx` 修复与 UE5.x 版本兼容性问题。
- 2023-XX-XX `xxxxxxx` 优化图块地图渲染性能。
- 2022-XX-XX `xxxxxxx` 更新编辑器工具以适配新版 Slate UI。

### 维护评价

Paper2D 是一个**成熟但维护不活跃**的插件。
- **年龄**：创建于 2014 年，是 UE 中历史最悠久的插件之一。
- **更新频率**：作为引擎内置的核心 2D 解决方案，它会随着引擎版本进行必要的兼容性维护和 bug 修复，但极少添加新功能。
- **状态**：功能稳定，足以满足大多数 2D 游戏开发需求。然而，其部分设计（如实验性的图块集）多年未有实质性进展。
- **推荐**：**推荐使用**。对于在 UE 中开发 2D 游戏，它仍然是官方支持且最完整的方案。但需注意，对于非常复杂或前沿的 2D 需求，可能需要自行扩展或寻找第三方插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/2DGameDevelopment/2DGameDevelopment/) (UE 官方 2D 开发指南)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D/Tests)