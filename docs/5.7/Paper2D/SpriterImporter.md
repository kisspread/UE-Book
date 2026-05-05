# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（2D游戏资产、编辑器工具） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor), `SpriterImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是 Unreal Engine 的官方 2D 游戏开发工具集。它并非一个简单的 2D 渲染器，而是一套完整的、与 UE 编辑器深度集成的 2D 游戏开发框架。其核心目的是在 UE 强大的 3D 引擎基础上，提供一套高效、直观的工具链，用于创建传统的 2D 游戏，如平台跳跃、俯视角 RPG、格斗游戏等。

它解决了在 3D 引擎中制作 2D 游戏时常见的痛点：
1.  **资产工作流**：提供了 `UPaperSprite`（精灵）和 `UPaperFlipbook`（翻书动画）资产类型，支持从纹理图集切割、动画序列编辑。
2.  **关卡设计**：提供了 `UPaperTileMap`（瓦片地图）和 `UPaperTileSet`（瓦片集）资产，以及配套的编辑器工具，用于快速搭建基于网格的 2D 关卡。
3.  **物理与碰撞**：为 2D 对象提供了简化的 2D 碰撞体（如盒体、圆形）和物理交互。
4.  **角色控制**：提供了 `APaperCharacter` 基类，内置了适合 2D 游戏的移动组件和动画逻辑。
5.  **渲染优化**：通过纹理图集、批处理渲染等技术，优化 2D 精灵的渲染性能。

## 使用场景

-   **2D 平台跳跃游戏**：使用 `APaperCharacter` 作为玩家角色，`UPaperFlipbook` 制作角色跑、跳、攻击动画，`UPaperTileMap` 搭建关卡地形。
-   **俯视角 RPG 或策略游戏**：使用 `UPaperSprite` 表示单位、建筑和道具，`UPaperTileMap` 绘制地图，利用 UE 的蓝图系统实现游戏逻辑。
-   **像素艺术游戏**：Paper2D 对像素艺术风格支持良好，可以精确控制像素的渲染和缩放。
-   **需要快速原型的 2D 项目**：利用其可视化的编辑器工具（如瓦片地图画笔、精灵编辑器），可以快速搭建出可玩的 2D 游戏原型。
-   **混合 2D/3D 游戏**：由于基于 UE，可以轻松地将 2D 元素与 3D 环境、特效、UI 结合。

## 蓝图用法

Paper2D 提供了丰富的蓝图节点，主要围绕其核心资产类型和游戏对象。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Flipbook` | 从一组 `UPaperSprite` 创建一个翻书动画资产。 | `UPaperFlipbook` |
| `Set Flipbook` | 为 `PaperFlipbookComponent` 设置要播放的翻书动画。 | `UPaperFlipbookComponent` |
| `Play` / `Reverse` / `Stop` | 控制翻书动画的播放、倒放和停止。 | `UPaperFlipbookComponent` |
| `Set Sprite` | 为 `PaperSpriteComponent` 设置要显示的精灵。 | `UPaperSpriteComponent` |
| `Set Tile Map` | 为 `PaperTileMapComponent` 设置要使用的瓦片地图资产。 | `UPaperTileMapComponent` |
| `Set Tile` | 在运行时动态修改瓦片地图上指定位置的瓦片。 | `UPaperTileMapComponent` |
| `Add Movement Input` | 向 `PaperCharacter` 添加移动输入（与 3D 角色控制类似）。 | `APaperCharacter` |

### 使用示例（蓝图描述）

1.  **创建一个会动的角色**：
    -   在蓝图中添加一个 `PaperFlipbookComponent`。
    -   在 `BeginPlay` 事件中，使用 `Create Flipbook` 节点，将一组表示角色待机帧的 `UPaperSprite` 连接起来，创建一个 `UPaperFlipbook` 资产。
    -   调用 `Set Flipbook` 节点，将创建的动画资产设置给组件。
    -   调用 `Play` 节点开始循环播放动画。

2.  **搭建一个简单的关卡**：
    -   在场景中放置一个 `PaperTileMapActor`。
    -   在其 `Details` 面板中，创建或指定一个 `UPaperTileMap` 资产。
    -   打开 `Paper Tile Map Editor`（双击资产），使用画笔工具在网格上绘制地形瓦片。
    -   在蓝图中，可以通过 `PaperTileMapComponent` 的 `Set Tile` 节点，在游戏过程中动态改变地图（例如，破坏地形）。

## C++ 用法

### 头文件引入

```cpp
// 核心运行时功能
#include "Paper2D.h"
#include "PaperSprite.h"
#include "PaperFlipbook.h"
#include "PaperFlipbookComponent.h"
#include "PaperTileMap.h"
#include "PaperTileMapComponent.h"
#include "PaperCharacter.h"

// 编辑器功能（仅在编辑器模块中使用）
#include "Paper2DEditor.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建和操作 Paper2D 资产与组件。

```cpp
// 来源：基于 Paper2D 模块的典型用法模式
// 创建一个精灵组件并设置精灵
UPaperSpriteComponent* SpriteComp = NewObject<UPaperSpriteComponent>(MyActor);
UPaperSprite* MySprite = LoadObject<UPaperSprite>(nullptr, TEXT("/Game/Sprites/MyCharacterSprite"));
if (MySprite)
{
    SpriteComp->SetSprite(MySprite);
    SpriteComp->RegisterComponent();
}

// 创建一个翻书动画组件并播放
UPaperFlipbookComponent* FlipbookComp = NewObject<UPaperFlipbookComponent>(MyActor);
UPaperFlipbook* RunAnim = LoadObject<UPaperFlipbook>(nullptr, TEXT("/Game/Animations/RunFlipbook"));
if (RunAnim)
{
    FlipbookComp->SetFlipbook(RunAnim);
    FlipbookComp->Play();
    FlipbookComp->RegisterComponent();
}
```

### 进阶用法

结合 `APaperCharacter` 和输入系统实现角色控制。

```cpp
// MyPaperCharacter.h
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
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    void MoveRight(float Value);
    void StartJump();
    void StopJump();

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D", meta = (AllowPrivateAccess = "true"))
    UPaperFlipbookComponent* FlipbookComponent;
};

// MyPaperCharacter.cpp
#include "MyPaperCharacter.h"
#include "PaperFlipbookComponent.h"
#include "Components/InputComponent.h"

AMyPaperCharacter::AMyPaperCharacter()
{
    FlipbookComponent = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("Flipbook"));
    FlipbookComponent->SetupAttachment(RootComponent);
}

void AMyPaperCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    PlayerInputComponent->BindAxis("MoveRight", this, &AMyPaperCharacter::MoveRight);
    PlayerInputComponent->BindAction("Jump", IE_Pressed, this, &AMyPaperCharacter::StartJump);
    PlayerInputComponent->BindAction("Jump", IE_Released, this, &AMyPaperCharacter::StopJump);
}

void AMyPaperCharacter::MoveRight(float Value)
{
    AddMovementInput(FVector(1.0f, 0.0f, 0.0f), Value);
    // 根据移动方向翻转精灵
    if (Value < 0.0f)
    {
        FlipbookComponent->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
    }
    else if (Value > 0.0f)
    {
        FlipbookComponent->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));
    }
}

void AMyPaperCharacter::StartJump()
{
    Jump();
}

void AMyPaperCharacter::StopJump()
{
    StopJumping();
}
```

## Demo 示例

一个最小的、可编译的 Paper2D 角色类示例。

```cpp
// SimplePaperCharacter.h
#pragma once
#include "PaperCharacter.h"
#include "SimplePaperCharacter.generated.h"

class UPaperFlipbookComponent;

UCLASS()
class ASimplePaperCharacter : public APaperCharacter
{
    GENERATED_BODY()

public:
    ASimplePaperCharacter();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UPaperFlipbookComponent* AnimComponent;
};

// SimplePaperCharacter.cpp
#include "SimplePaperCharacter.h"
#include "PaperFlipbook.h"
#include "PaperFlipbookComponent.h"

ASimplePaperCharacter::ASimplePaperCharacter()
{
    AnimComponent = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("Animation"));
    AnimComponent->SetupAttachment(RootComponent);
}

void ASimplePaperCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 加载一个翻书动画资产（假设路径正确）
    UPaperFlipbook* IdleAnim = LoadObject<UPaperFlipbook>(this, TEXT("/Game/2D/IdleFlipbook"));
    if (IdleAnim)
    {
        AnimComponent->SetFlipbook(IdleAnim);
        AnimComponent->Play();
    }
}
```

## 模块依赖

Paper2D 插件内部模块间有依赖关系，但对外部项目而言，依赖关系相对简单。

| 模块 | 用途 |
|---|---|
| `Paper2D` | 核心运行时模块，提供所有 2D 资产类型和组件。你的游戏模块需要依赖此模块。 |
| `Paper2DEditor` | 编辑器模块，提供精灵编辑器、瓦片地图编辑器等工具。仅在开发时需要。 |
| `PaperSpriteSheetImporter` | 编辑器工具，用于从精灵表（Sprite Sheet）导入切割精灵。 |
| `PaperTiledImporter` | 编辑器工具，用于导入 Tiled 地图编辑器（.tmx）格式的瓦片地图。 |
| `SmartSnapping` | 编辑器工具，提供智能对齐和吸附功能，辅助 2D 关卡设计。 |
| `SpriterImporter` | 编辑器工具，用于导入 Spriter（.scml）格式的 2D 骨骼动画。 |

**对于游戏项目**：通常只需要在项目的 `.Build.cs` 文件中添加对 `Paper2D` 模块的依赖。
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Paper2D" });
```

## 维护状态

### 近期更新

```
- 64658cf6ae5e GetAssetRegistryTags deprecation: Make the old GetAssetRegistryTags and related functions deprecated. (2024-10-03)
- d64cf417281e AssetRegistry includes (Engine Plugins): change #include "AssetData.h" -> #include "AssetRegistry/AssetData.h". (2024-09-15)
- 3b81cf820158 Merging using //UE5/Main_to_//UE5/Release-Engine-Staging @14384769 autoresolved files. (2024-08-20)
```

### 维护评价

Paper2D 是一个**历史非常悠久**的插件，创建于 2014 年。从最近的提交记录来看，其更新主要集中在**引擎底层 API 的适配和重构**（如 AssetRegistry 的变更），而非功能性的增强或 Bug 修复。这表明该插件目前处于**维护不活跃**的状态，Epic 可能已将其视为一个稳定但不再积极开发的“遗留”系统。

**优点**：
-   功能完整，覆盖了 2D 游戏开发的核心需求。
-   与 UE 编辑器集成度高，工作流相对成熟。
-   作为官方插件，稳定性和兼容性有基本保障。

**缺点与风险**：
-   **长期未更新**：超过 2 年没有实质性功能更新，可能无法充分利用 UE5 的新特性（如 Lumen, Nanite 等）。
-   **实验性功能**：.uplugin 中提到的“tilesets (experimental)”功能可能一直未脱离实验状态。
-   **社区与文档**：官方文档和社区支持可能不如主流 3D 功能活跃。
-   **未来不确定性**：在 Epic 的长期路线图中，Paper2D 的优先级可能较低。

**推荐**：
-   对于**新项目**，如果对 2D 游戏有较高要求或希望使用最新的引擎特性，建议评估第三方 2D 解决方案（如 Unreal.js, PaperZD 等）或考虑使用更专注于 2D 的引擎。
-   对于**现有项目**或**快速原型**，Paper2D 仍然是一个可用且功能齐全的选择，但需意识到其维护状态，并做好可能遇到兼容性问题的心理准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/paper-2d-in-unreal-engine/) (UE5 官方文档中的 Paper2D 部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D/Tests) (插件内测试)
- [引擎测试](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/FunctionalTests/Paper2D) (引擎功能测试)