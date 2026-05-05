# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（2D 游戏资产和工具） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor), `SpriterImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是一个完整的 2D 游戏开发框架，旨在解决在 Unreal Engine 中高效开发 2D 游戏的需求。它不仅仅是一个简单的精灵渲染器，而是一套包含资产创建、关卡编辑、动画系统和物理交互的完整工具链。其核心价值在于将 UE 强大的编辑器和运行时功能（如蓝图、物理、音频）与 2D 游戏开发的特定需求相结合，允许开发者利用熟悉的 UE 工作流来构建 2D 游戏。

## 使用场景

-   **2D 平台跳跃游戏**：使用 `PaperCharacter` 和 `PaperFlipbook` 制作角色动画，利用 `PaperTileMap` 构建关卡。
-   **俯视角 RPG 或策略游戏**：使用 `PaperTileMap` 高效创建大型、可复用的瓦片地图。
-   **像素艺术游戏**：导入精灵图集（Sprite Sheet），使用 `PaperSprite` 和 `PaperFlipbook` 进行动画播放。
-   **需要与 3D 环境混合的 2D 游戏**：Paper2D 组件可以放置在 3D 世界中，实现 2.5D 效果。
-   **快速原型开发**：利用蓝图和 Paper2D 提供的组件，快速搭建 2D 游戏玩法原型。

## 蓝图用法

Paper2D 提供了丰富的蓝图节点，主要围绕精灵、动画和瓦片地图展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Paper Sprite Component` | 创建一个新的 Paper2D 精灵组件。 | `UBlueprintFunctionLibrary` |
| `Set Sprite` | 设置 Paper2D 组件使用的精灵资产。 | `UPaperSpriteComponent` |
| `Set Flipbook` | 设置 Paper2D 组件使用的翻书动画资产。 | `UPaperFlipbookComponent` |
| `Play` / `Reverse` / `Stop` | 控制翻书动画的播放、倒放和停止。 | `UPaperFlipbookComponent` |
| `Set Tile Map` | 设置瓦片地图组件使用的瓦片地图资产。 | `UPaperTileMapComponent` |
| `Set Tile` | 在运行时动态设置瓦片地图中某个位置的瓦片。 | `UPaperTileMapComponent` |
| `Get Tile Map` / `Get Tile` | 获取瓦片地图或特定位置的瓦片信息。 | `UPaperTileMapComponent` |

### 使用示例（蓝图描述）

1.  **创建一个会动的角色**：
    -   在角色蓝图中，添加一个 `PaperFlipbookComponent`。
    -   在组件的细节面板中，将 `Flipbook` 属性设置为你的 `PaperFlipbook` 资产（例如 `IdleAnimation`）。
    -   在事件图表中，使用 `InputAction` 节点检测移动输入，然后调用 `Play` 或 `Reverse` 节点来控制动画方向，并使用 `Set Playback Position in Seconds` 或 `Set New Time` 来同步动画与移动速度。

2.  **构建一个可交互的瓦片地图**：
    -   在关卡中放置一个 `PaperTileMapActor`。
    -   在其组件中，将 `Tile Map` 属性设置为你的 `PaperTileMap` 资产。
    -   在蓝图中，通过 `Get Component` 获取该 `PaperTileMapComponent`。
    -   当玩家角色与某个瓦片重叠时，使用 `Get Tile` 节点获取该位置的瓦片信息（如 `TileIndex`），然后根据索引执行不同逻辑（例如，索引 5 是金币，索引 10 是尖刺）。

## C++ 用法

Paper2D 的 C++ API 主要用于创建自定义组件、扩展编辑器工具或进行高性能的运行时操作。

### 头文件引入

```cpp
// 核心运行时功能
#include "Paper2D/Classes/PaperSprite.h"
#include "Paper2D/Classes/PaperFlipbook.h"
#include "Paper2D/Classes/PaperTileMap.h"
#include "Paper2D/Classes/PaperSpriteComponent.h"
#include "Paper2D/Classes/PaperFlipbookComponent.h"
#include "Paper2D/Classes/PaperTileMapComponent.h"

// 编辑器扩展（仅在编辑器模块中使用）
#include "Paper2DEditor/Classes/PaperSpriteThumbnailRenderer.h"
```

### 基本用法

以下示例展示如何在 C++ 中动态创建一个 Paper2D 精灵组件并设置其精灵。
（来源：引擎测试用例及通用用法）

```cpp
// MyActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UPaperSpriteComponent;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D")
    UPaperSpriteComponent* SpriteComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Paper2D")
    UPaperSprite* MySpriteAsset;
};

// MyActor.cpp
#include "MyActor.h"
#include "Paper2D/Classes/PaperSpriteComponent.h"
#include "Paper2D/Classes/PaperSprite.h"

AMyActor::AMyActor()
{
    // 创建并设置根组件
    SpriteComponent = CreateDefaultSubobject<UPaperSpriteComponent>(TEXT("SpriteComp"));
    RootComponent = SpriteComponent;

    // 在构造函数中设置精灵资产（通常在编辑器中设置更佳）
    // SpriteComponent->SetSprite(MySpriteAsset);
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时动态设置精灵
    if (MySpriteAsset)
    {
        SpriteComponent->SetSprite(MySpriteAsset);
    }
}
```

### 进阶用法

以下示例展示如何创建一个自定义的 Paper2D 组件，该组件可以管理多个翻书动画状态。
（来源：Paper2D 组件设计模式及测试用例）

```cpp
// PaperCharacterAnimComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "PaperCharacterAnimComponent.generated.h"

class UPaperFlipbook;
class UPaperFlipbookComponent;

UCLASS(ClassGroup=(Paper2D), meta=(BlueprintSpawnableComponent))
class UPaperCharacterAnimComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPaperCharacterAnimComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    TMap<FName, UPaperFlipbook*> AnimationMap;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
    UPaperFlipbookComponent* FlipbookComponent;

    UFUNCTION(BlueprintCallable, Category = "Animation")
    void SetAnimationState(FName StateName);

protected:
    virtual void BeginPlay() override;

private:
    FName CurrentState;
};

// PaperCharacterAnimComponent.cpp
#include "PaperCharacterAnimComponent.h"
#include "Paper2D/Classes/PaperFlipbookComponent.h"
#include "Paper2D/Classes/PaperFlipbook.h"

UPaperCharacterAnimComponent::UPaperCharacterAnimComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UPaperCharacterAnimComponent::BeginPlay()
{
    Super::BeginPlay();

    // 尝试从拥有者身上找到 PaperFlipbookComponent
    FlipbookComponent = GetOwner()->FindComponentByClass<UPaperFlipbookComponent>();
    if (FlipbookComponent)
    {
        // 设置初始动画
        SetAnimationState(FName("Idle"));
    }
}

void UPaperCharacterAnimComponent::SetAnimationState(FName StateName)
{
    if (CurrentState == StateName) return;

    if (FlipbookComponent && AnimationMap.Contains(StateName))
    {
        UPaperFlipbook* NewFlipbook = AnimationMap[StateName];
        if (NewFlipbook)
        {
            FlipbookComponent->SetFlipbook(NewFlipbook);
            FlipbookComponent->PlayFromStart();
            CurrentState = StateName;
        }
    }
}
```

## Demo 示例

一个最小的可运行 Paper2D 角色示例，包含移动和动画切换。

```cpp
// Paper2DCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "Paper2DCharacter.generated.h"

class UPaperFlipbookComponent;
class UPaperFlipbook;

UCLASS()
class APaper2DCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    APaper2DCharacter();

    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D")
    UPaperFlipbookComponent* FlipbookComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    UPaperFlipbook* IdleFlipbook;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    UPaperFlipbook* RunFlipbook;

protected:
    void MoveRight(float Value);

private:
    float Direction;
};

// Paper2DCharacter.cpp
#include "Paper2DCharacter.h"
#include "Paper2D/Classes/PaperFlipbookComponent.h"
#include "Paper2D/Classes/PaperFlipbook.h"
#include "GameFramework/CharacterMovementComponent.h"

APaper2DCharacter::APaper2DCharacter()
{
    // 创建翻书组件并设为根组件
    FlipbookComponent = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("FlipbookComp"));
    FlipbookComponent->SetupAttachment(RootComponent);
    FlipbookComponent->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f)); // 面向摄像机

    // 配置角色移动组件（2D 常用设置）
    GetCharacterMovement()->bOrientRotationToMovement = false; // 不根据移动方向旋转
    GetCharacterMovement()->RotationRate = FRotator(0.0f, 0.0f, 0.0f); // 禁用旋转
    GetCharacterMovement()->GravityScale = 1.0f;
    GetCharacterMovement()->AirControl = 0.8f;
    GetCharacterMovement()->JumpZVelocity = 1000.f;
    GetCharacterMovement()->GroundFriction = 3.0f;
    GetCharacterMovement()->MaxWalkSpeed = 600.0f;
    GetCharacterMovement()->MaxFlySpeed = 600.0f;

    Direction = 1.0f;
}

void APaper2DCharacter::BeginPlay()
{
    Super::BeginPlay();
    if (IdleFlipbook)
    {
        FlipbookComponent->SetFlipbook(IdleFlipbook);
    }
}

void APaper2DCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 根据移动速度切换动画
    const FVector Velocity = GetVelocity();
    const float Speed = Velocity.Size2D();

    if (Speed > 10.0f && RunFlipbook)
    {
        if (FlipbookComponent->GetFlipbook() != RunFlipbook)
        {
            FlipbookComponent->SetFlipbook(RunFlipbook);
        }
        // 根据移动方向翻转精灵
        Direction = (Velocity.X >= 0.0f) ? 1.0f : -1.0f;
        FlipbookComponent->SetRelativeScale3D(FVector(Direction, 1.0f, 1.0f));
    }
    else if (IdleFlipbook)
    {
        if (FlipbookComponent->GetFlipbook() != IdleFlipbook)
        {
            FlipbookComponent->SetFlipbook(IdleFlipbook);
        }
    }
}

void APaper2DCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    PlayerInputComponent->BindAxis("MoveRight", this, &APaper2DCharacter::MoveRight);
    PlayerInputComponent->BindAction("Jump", IE_Pressed, this, &ACharacter::Jump);
}

void APaper2DCharacter::MoveRight(float Value)
{
    AddMovementInput(FVector(1.0f, 0.0f, 0.0f), Value);
}
```

## 模块依赖

Paper2D 插件本身依赖于 UE 核心模块。如果你要在自己的项目或插件中使用 Paper2D 的功能，需要在你的模块的 `Build.cs` 文件中添加依赖。

| 模块 | 用途 |
|---|---|
| `Paper2D` | 核心运行时模块，包含所有 2D 组件和资产类。 |
| `Paper2DEditor` | 编辑器模块，提供资产编辑器、缩略图渲染、自定义资产操作等。 |
| `PaperSpriteSheetImporter` | 编辑器模块，提供从精灵图集（Sprite Sheet）导入精灵的功能。 |
| `PaperTiledImporter` | 编辑器模块，提供从 Tiled 地图编辑器导入瓦片地图的功能。 |
| `SmartSnapping` | 编辑器模块，提供增强的 2D 对象对齐和吸附功能。 |
| `SpriterImporter` | 编辑器模块，提供从 Spriter 动画工具导入资产的功能。 |

**注意**：`Paper2D` 模块本身在 `Build.cs` 中依赖了 `EditorFramework` 和 `UnrealEd`，这表明其运行时部分可能包含一些编辑器相关的功能或数据结构。在纯运行时项目中使用时，需要确认这些依赖是否会导致打包问题。

## 维护状态

### 近期更新

```
- 2023-10-26 98a8e0e0df23 Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes
- 2023-10-25 4a6d973b1db6 Fixed some 'deprecated' FString usage.
- 2023-10-25 b6ee3a6c648d Fix UE_LOG callsites that have format string-related UB
```

### 维护评价

Paper2D 是一个历史悠久的插件，创建于 2014 年，是 UE4 早期为支持 2D 游戏开发而引入的重要功能。然而，从近期的 Git 提交记录来看，该插件的维护状态**不活跃**。

-   **年龄**：超过 10 年，属于“文物”级别。
-   **近期更新**：最近的提交（2023年10月）全部是代码清理和编译警告修复（如移除废弃的宏、修复字符串格式化问题），没有任何新功能或实质性 bug 修复。这表明 Epic 可能仅在进行大规模引擎重构时顺带维护其编译兼容性。
-   **活跃度**：自 UE 4.2x 版本后，Paper2D 的核心功能和 API 基本没有变化。Epic 官方已将 2D 游戏开发的重心转向更现代、跨平台的 **PaperZD**（一个社区维护的动画蓝图插件）和 **CommonUI** 等框架。
-   **已知问题**：社区反馈中，Paper2D 存在一些长期未修复的 bug，例如在特定平台上的渲染问题、物理交互的边缘情况等。其“实验性”的瓦片集功能也始终未正式完善。
-   **推荐使用**：对于**新项目**，特别是计划长期维护的商业项目，**不推荐**将 Paper2D 作为核心框架。它更适合用于：
    1.  学习 UE 的组件化架构和编辑器扩展。
    2.  快速原型验证或 Game Jam 项目。
    3.  维护已使用 Paper2D 的老项目。
    对于新项目，建议评估 **PaperZD**、**Pixel2D**（商业插件）或直接使用 UE 的基础组件（`Sprite`, `Flipbook`）配合自定义逻辑。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/2DStarterKit/) (UE 官方已将 Paper2D 归类为“2D Starter Kit”，文档内容陈旧)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D/Tests) (引擎内测试)

---

# PaperTiledImporter 子模块文档

## 用途

`PaperTiledImporter` 是一个编辑器专用模块，其核心功能是**将 Tiled 地图编辑器 (http://www.mapeditor.org/) 导出的 JSON 格式瓦片地图文件 (.tmj/.json) 导入到 Unreal Engine 中**，并自动转换为引擎原生的 `UPaperTileMap` 资产。它解决了在外部专业工具中设计复杂瓦片地图，然后无缝集成到 UE 项目中的工作流问题。

## 蓝图用法

该模块主要通过编辑器操作（拖拽导入或通过内容浏览器）使用，不直接暴露运行时蓝图节点。其核心是 `UPaperTiledImporterFactory` 工厂类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import` (编辑器操作) | 在内容浏览器中右键 -> Import，选择 .tmj 文件。 | `UPaperTiledImporterFactory` |
| `Reimport` (编辑器操作) | 在已导入的 PaperTileMap 资产上右键 -> Reimport。 | `UPaperTiledImporterFactory` |

### 使用示例（蓝图描述）

1.  **导入 Tiled 地图**：
    -   在 Tiled 编辑器中完成地图设计，导出为 JSON 格式 (.tmj)。
    -   在 UE 编辑器的内容浏览器中，导航到目标文件夹。
    -   点击 “Import” 按钮或直接将 .tmj 文件拖入内容浏览器。
    -   在弹出的导入对话框中，确认设置（如纹理导入路径），点击 “Import All”。
    -   导入完成后，将生成 `PaperTileMap` 资产以及相关的 `PaperTileSet` 和纹理资产。

2.  **更新已导入的地图**：
    -   在 Tiled 中修改地图并重新导出。
    -   在 UE 内容浏览器中，找到之前导入的 `PaperTileMap` 资产。
    -   右键点击该资产，选择 “Reimport”。
    -   资产将根据最新的 .tmj 文件更新。

## C++ 用法

该模块的 C++ 代码主要服务于编辑器导入流程，普通开发者很少直接调用。其核心是解析 Tiled 的 JSON 结构并构建 UE 资产。

### 头文件引入

```cpp
// 仅在编辑器模块中需要
#include "PaperTiledImporter/Classes/PaperTiledImporterFactory.h"
```

### 基本用法

以下代码片段展示了 `UPaperTiledImporterFactory` 如何解析 JSON 并创建资产的核心逻辑（简化版）。
（来源：`PaperTiledImporterFactory.cpp` 中的 `FactoryCreateText` 方法）

```cpp
// 伪代码，展示导入流程
UObject* UPaperTiledImporterFactory::FactoryCreateText(...)
{
    // 1. 解析 JSON 字符串
    TSharedPtr<FJsonObject> RootObject = ParseJSON(FileContents, NameForErrors);
    if (!RootObject.IsValid()) return nullptr;

    // 2. 解析全局信息（地图尺寸、方向、图层等）
    FTileMapFromTiled GlobalInfo;
    ParseGlobalInfoFromJSON(RootObject, GlobalInfo, NameForErrors);

    // 3. 创建或查找目标 PaperTileMap 资产
    UPaperTileMap* TileMap = Cast<UPaperTileMap>(CreateNewAsset(UPaperTileMap::StaticClass(), TargetPath, DesiredName, Flags));

    // 4. 转换并导入瓦片集 (Tilesets)
    ConvertTileSets(GlobalInfo, CurrentSourcePath, LongPackagePath, Flags);

    // 5. 将解析的图层数据填充到 TileMap 资产中
    FinalizeTileMap(GlobalInfo, TileMap);

    return TileMap;
}
```

### 进阶用法

该模块定义了多个枚举来映射 Tiled 的配置选项，这些枚举在解析过程中被使用。

```cpp
// PaperTiledImporterFactory.h 中定义的枚举，用于映射 Tiled 的地图属性
enum class ETiledOrientation : uint8
{
    Unknown,
    Orthogonal, // 标准直角
    Isometric,  // 等距视角
    Staggered,  // 交错等距
    Hexagonal   // 六边形
};

enum class ETiledRenderOrder : uint8
{
    RightDown, // Tiled 默认
    RightUp,
    LeftDown,
    LeftUp
};

// 在解析函数中，会根据这些枚举值设置 PaperTileMap 的对应属性
void UPaperTiledImporterFactory::ParseGlobalInfoFromJSON(...)
{
    // ... 解析代码 ...
    const FString OrientationStr = Tree->GetStringField(TEXT("orientation"));
    if (OrientationStr == TEXT("orthogonal"))
    {
        GlobalInfo.Orientation = ETiledOrientation::Orthogonal;
        // 对应设置 TileMap->ProjectionMode = ETileMapProjectionMode::Orthogonal;
    }
    else if (OrientationStr == TEXT("isometric"))
    {
        GlobalInfo.Orientation = ETiledOrientation::Isometric;
        // 对应设置 TileMap->ProjectionMode = ETileMapProjectionMode::IsometricDiamond;
    }
    // ... 其他方向处理 ...
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Paper2D` | 核心依赖，提供 `UPaperTileMap`, `UPaperTileSet` 等资产类。 |
| `UnrealEd` | 编辑器核心框架，提供 `UFactory`, `FReimportHandler` 等基类。 |
| `Json` | UE 的 JSON 解析库，用于读取 Tiled 导出的 .tmj 文件。 |
| `AssetTools` | 编辑器资产操作工具，用于创建和管理导入的资产。 |