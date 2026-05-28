# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 中文名 | 2D游戏开发套件 |
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、示例资源） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor), `SpriterImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是 Unreal Engine 内置的一套用于创建 2D 游戏的完整工具链和资产类型集合。它并非简单的图片渲染器，而是一个包含了渲染、物理、动画、关卡编辑和资源导入工作流的完整 2D 框架。其存在是为了填补 UE 主要面向 3D 游戏开发的空白，为开发者提供原生、高效且与引擎深度集成的 2D 游戏开发解决方案，避免依赖第三方插件或使用 3D 模拟 2D 的笨重方法。

## 使用场景

- 你正在开发一款传统的 2D 平台跳跃游戏（如《空洞骑士》风格），需要精灵动画、2D 物理和精确的关卡编辑工具。
- 你正在制作一款俯视角或侧视角的 2D 塔防、RPG 或冒险游戏，需要使用图块集（Tileset）来快速构建地图。
- 你需要从外部工具（如 TexturePacker）导入精灵图集（Sprite Sheet）或使用 Spriter 等工具制作的 2D 骨骼动画。
- 你希望利用 UE 强大的渲染管线、材质系统和物理引擎（Chaos）来实现 2D 游戏的高级效果（如光照、法线、复杂的碰撞体）。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Sprite` | 设置 `PaperSpriteComponent` 显示的 Sprite 资产 | `UPaperSpriteComponent` |
| `Set Flipbook` | 设置 `PaperFlipbookComponent` 播放的 Flipbook 动画 | `UPaperFlipbookComponent` |
| `Play` / `Stop` / `Set Play Rate` | 控制 Flipbook 动画的播放、停止和速率 | `UPaperFlipbookComponent` |
| `Set Texture` | 为 `PaperTileMapComponent` 运行时设置图块纹理 | `UPaperTileMapComponent` |
| `Set Collision Enabled` | 设置 2D 组件的碰撞类型（无、仅查询、仅物理、碰撞和查询） | `UPaperSpriteComponent` / `UPaperTileMapComponent` |
| `Get Sprite Source Size` | 获取精灵原始像素尺寸 | `UPaperSprite` |
| `Set World Rotation (Z only)` | 专门设置 2D 组件在 XY 平面上的旋转 | `UPaperSpriteComponent` |

### 使用示例（蓝图描述）

1.  **创建一个移动的精灵角色**：
    - 在角色蓝图中，添加一个 `PaperFlipbookComponent` 作为根组件。
    - 在事件图表中，使用 `InputAxis MoveForward` 节点获取输入。
    - 将输入值连接到 `Add Movement Input` 节点（确保在 `CharacterMovement` 组件中设置为侧视图移动模式）。
    - 根据角色朝向（`Get Actor Forward Vector`），使用 `Set Flipbook` 节点切换左/右行走的 Flipbook 资产。

2.  **构建一个图块地图**：
    - 使用 `Paper Tile Map Actor` 放置一个空地图。
    - 在详情面板中，导入或创建 `PaperTileSet` 资产，并分配一个 Tile 材质。
    - 在编辑器中使用绘制工具直接在视口中绘制图块。
    - 为图块地图添加碰撞：在 `Tile Set` 资产中配置 `Tile` 的碰撞域（矩形、圆形等）。

## C++ 用法

### 头文件引入

```cpp
#include "Paper2D/Classes/PaperSprite.h"
#include "Paper2D/Classes/PaperFlipbook.h"
#include "Paper2D/Classes/PaperSpriteComponent.h"
#include "Paper2D/Classes/PaperFlipbookComponent.h"
```

### 基本用法

*来源: `Engine/Plugins/2D/Paper2D/Source/Paper2D/Private/PaperSpriteComponent.cpp`*

```cpp
// 创建一个 PaperSpriteComponent 并设置 Sprite
UPaperSpriteComponent* SpriteComp = NewObject<UPaperSpriteComponent>(this);
SpriteComp->RegisterComponent();
SpriteComp->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

// 加载一个 Sprite 资产
UPaperSprite* MySprite = LoadObject<UPaperSprite>(nullptr, TEXT("/Game/Sprites/MyCharacter"));
if (MySprite)
{
    SpriteComp->SetSprite(MySprite);
    // 设置 Sprite 颜色
    SpriteComp->SetSpriteColor(FLinearColor::Green);
}

// 控制 Flipbook 动画
UPaperFlipbookComponent* FlipbookComp = FindComponentByClass<UPaperFlipbookComponent>();
if (FlipbookComp && FlipbookComp->IsPlaying())
{
    FlipbookComp->Stop();
    FlipbookComp->SetPlayRate(0.5f); // 设置半速播放
    FlipbookComp->PlayFromStart();
}
```

### 进阶用法

*来源: `Engine/Plugins/2D/Paper2D/Source/Paper2D/Private/PaperTileMapComponent.cpp`*

```cpp
// 动态修改图块地图
UPaperTileMapComponent* TileMapComp = FindComponentByClass<UPaperTileMapComponent>();
if (TileMapComp)
{
    // 在特定层、X， Y位置设置一个图块索引
    const int32 LayerIndex = 0;
    const int32 TileX = 5;
    const int32 TileY = 10;
    const FPaperTileInfo TileInfo = FPaperTileInfo(); // 创建一个默认图块信息
    TileInfo.TileSet = MyTileSet; // 指定使用的 Tile Set
    TileInfo.PackedTileIndex = 3; // 指定 Tile Set 中的索引

    TileMapComp->SetTile(LayerIndex, TileX, TileY, TileInfo);
    TileMapComp->RebuildCollision(); // 重建碰撞体以反映地图变化
}
```

## Demo 示例

以下是一个最小的可编译 C++ 示例，创建一个会沿着 X 轴来回移动并播放走路动画的 Sprite 角色。

**MyPaperCharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "PaperCharacter.h" // Paper2D 提供的 Pawn 基类
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
	class UPaperFlipbookComponent* FlipbookComp;

	float MoveDirection;
	float MoveSpeed;
};
```

**MyPaperCharacter.cpp**
```cpp
#include "MyPaperCharacter.h"
#include "PaperFlipbookComponent.h"

AMyPaperCharacter::AMyPaperCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	// 创建并设置 Flipbook 组件为根组件
	FlipbookComp = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("Flipbook"));
	FlipbookComp->SetupAttachment(RootComponent);

	// 初始化移动参数
	MoveDirection = 1.0f;
	MoveSpeed = 200.0f;
}

void AMyPaperCharacter::BeginPlay()
{
	Super::BeginPlay();

	// 加载并播放走路动画 (确保资产路径正确)
	UPaperFlipbook* WalkFlipbook = LoadObject<UPaperFlipbook>(nullptr, TEXT("/Game/Sprites/WalkAnim"));
	if (WalkFlipbook)
	{
		FlipbookComp->SetFlipbook(WalkFlipbook);
		FlipbookComp->Play();
	}
}

void AMyPaperCharacter::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 简单的来回移动逻辑
	FVector CurrentLocation = GetActorLocation();
	CurrentLocation.X += MoveDirection * MoveSpeed * DeltaTime;

	// 简单的边界检查并反转方向
	if (CurrentLocation.X > 500.0f || CurrentLocation.X < -500.0f)
	{
		MoveDirection *= -1.0f;
		// 翻转角色朝向
		FlipbookComp->SetRelativeRotation(FRotator(0.0f, (MoveDirection > 0.0f) ? 0.0f : 180.0f, 0.0f));
	}

	SetActorLocation(CurrentLocation);
}
```

## 模块依赖

从 Build.cs 分析，使用者通常只需关注运行时模块。

| 模块 | 用途 |
|---|---|
| `Paper2D` | 核心运行时模块，提供所有 2D 渲染、物理和资产类型 |
| `Paper2DEditor` | 编辑器模块，提供 Sprite/Flipbook/TileMap 编辑器、资产编辑器和内容浏览器集成 |
| `PaperSpriteSheetImporter` | 编辑器工具，用于导入纹理图集（Sprite Sheet）并自动切割生成多个 Sprite 资产 |
| `PaperTiledImporter` | 编辑器工具，用于导入 Tiled (TMX/TSX) 地图编辑器格式的文件 |
| `SmartSnapping` | 编辑器辅助模块，为 2D 对象（如 Sprite、TileMap）提供智能网格和对齐吸附功能 |
| `SpriterImporter` | 编辑器工具，用于导入 Spriter Pro 制作的 2D 骨骼动画数据 |

**对于游戏运行时项目**，通常只依赖 `Paper2D` 模块。
**对于编辑器工具开发**，可能需要依赖 `Paper2DEditor` 或特定的 Importer 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `32652778` | Harden Paper2D tile map and tile layer PostEditChangeProperty paths against null entries and non-til | 加固图块地图编辑属性变更流程，防止空指针和非图块相关属性变更导致崩溃 |
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回滚了之前的某个提交（CL53903539） |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 在编辑器工具栏中添加全局吸附开关，并在任一吸附选项启用时显示红色指示器 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量隐式转换为浮点数导致的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |

### 维护评价

Paper2D 作为 UE 的官方 2D 插件，历史悠久。从近期更新记录（2026年）来看，它仍在被 Epic Games 积极维护，主要针对编辑器稳定性和开发者体验进行小幅改进和 bug 修复，例如加固代码、改进编辑器工具和清理编译警告。然而，其核心架构和功能已多年未有革命性更新。虽然作为官方解决方案可靠性高，但面对更现代、功能更丰富的第三方 2D 插件（如 PaperZD），其功能和易用性可能显得陈旧。**推荐使用**，尤其适用于追求引擎原生集成、稳定性和长期维护的项目。但对于追求最新 2D 功能（如 2D 骨骼动画、高级视效）的团队，可能需要评估是否满足需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/2D-Game-Development-in-Unreal-Engine/)（UE 2D 游戏开发官方指南，涵盖 Paper2D 用法）