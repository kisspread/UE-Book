# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 中文名 | 二维纸片 |
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（示例项目、蓝图资产、材质模板） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是一套集成在 Unreal Engine 中的 2D 游戏开发工具集，旨在弥补 UE 作为 3D 引擎在 2D 游戏开发方面的功能缺口。它提供了一套完整的 2D 资产类型（如 `PaperSprite`、`PaperFlipbook`）、2D 碰撞组件、以及专为 2D 设计的关卡编辑工具，使得开发者能够在强大的 UE 引擎内高效地制作传统 2D 游戏，如平台跳跃、俯视角冒险、格斗游戏等。

它解决了以下问题：
1.  **资产管理**：提供了原生支持精灵图、图块集、序列帧动画的资产类型。
2.  **编辑体验**：内置了 2D 模式（Top-Down、Side Scroller 视角）、智能对齐、图块编辑等编辑器工具。
3.  **运行时性能**：提供了专门的 2D 物理组件（`PaperCharacter`、`PaperFlipbookComponent`）和优化的 2D 渲染路径。

## 使用场景

-   你正在制作一个 **2D 平台跳跃游戏**（如《超级马里奥》风格）。
-   你需要制作一个 **俯视角 2D RPG 或 Roguelike** 游戏。
-   你希望使用 UE 的蓝图系统和成熟的 3D 工具链来开发 **2D 格斗游戏**。
-   你从其他 2D 引擎（如 SpriteKit, LibGDX）迁移项目，并希望利用 UE 的发布平台覆盖和网络功能。
-   你需要为 3D 游戏添加 **2D UI 元素**或 **过场动画**。

## 蓝图用法

Paper2D 提供了丰富的蓝图节点用于创建和控制 2D 资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Construct Paper Flipbook Component` | 创建一个纸片翻书组件，用于播放序列帧动画 | `UPaperFlipbookComponent` |
| `Set Flipbook` | 动态设置或更换要播放的翻书资产（`UPaperFlipbook`） | `UPaperFlipbookComponent` |
| `Play` / `Stop` / `Reverse` | 控制翻书动画的播放、停止和反转 | `UPaperFlipbookComponent` |
| `Set Sprite` | 为纸片组件（`UPaperSpriteComponent`）设置精灵图（`UPaperSprite`） | `UPaperSpriteComponent` |
| `Set Tile Map` | 为图块地图组件（`UPaperTileMapComponent`）设置图块地图资产 | `UPaperTileMapComponent` |
| `Get Animated Collision Profile` | 获取用于 2D 角色动画驱动的碰撞配置信息 | `UPaperFlipbook` |
| `Paper Sprite` | 代表一个 2D 精灵图资产，是 2D 渲染的基本单位 | `UPaperSprite` |

### 使用示例（蓝图描述）

1.  **创建一个带 2D 碰撞的角色**：
    *   从 `PaperCharacter` 派生一个新的蓝图类。
    *   在其组件面板中，添加一个 `PaperFlipbookComponent` 作为根组件，并设置 `Flipbook` 属性为你的角色待机动画序列。
    *   在事件图表中，使用 `InputAction MoveRight` 等输入事件，调用 `AddMovementInput` 节点驱动角色移动。组件会自动应用 `PaperCharacter` 内置的 2D 物理和碰撞。

2.  **动态播放攻击动画**：
    *   在角色蓝图中，当按下攻击键（如 `InputAction Attack`）时：
        *   调用 `PaperFlipbookComponent` 的 `Set Flipbook` 节点，将 `Flipbook` 属性设为预定义的攻击动画序列。
        *   调用 `Play` 节点。
        *   使用 `Set Collision Profile Name` 节点临时更改碰撞 Profile 为攻击判定。
        *   监听 `On Finished` 事件，动画播放结束后切回待机动画并重置碰撞。

## C++ 用法

### 头文件引入

```cpp
#include "Paper2D/Classes/PaperSprite.h"
#include "Paper2D/Classes/PaperFlipbook.h"
#include "Paper2D/Classes/PaperFlipbookComponent.h"
#include "Paper2D/Classes/PaperCharacter.h"
```

### 基本用法

从 Paper2D 内部测试和常见用法中提取的代码示例。

```cpp
// 创建一个 PaperSprite 资产（通常在编辑器或内容管线中完成，此处为编程式创建的示例）
UPaperSprite* MySprite = NewObject<UPaperSprite>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);
// 设置精灵的源纹理、源区域等参数...
// MySprite->SetSourceTexture(MyTexture, SourceRegion);
MySprite->PostEditChange();

// 创建一个 PaperFlipbookComponent 并附加到 Actor
UPaperFlipbookComponent* FlipbookComp = NewObject<UPaperFlipbookComponent>(MyActor);
FlipbookComp->SetupAttachment(MyActor->GetRootComponent());
FlipbookComp->SetFlipbook(MyFlipbookAsset); // MyFlipbookAsset 是已加载的 UPaperFlipbook*
FlipbookComp->Play();
FlipbookComp->RegisterComponent(); // 必须注册组件才能生效
```

### 进阶用法

在 Actor 中组合使用 Paper2D 组件，并动态切换动画状态。

```cpp
// 在自定义 APaper2DCharacter 子类中
void AMy2DCharacter::OnAttackHit()
{
    // 切换到攻击动画
    PaperFlipbookComponent->SetFlipbook(AttackFlipbook);
    PaperFlipbookComponent->PlayFromStart();

    // 设置一个定时器，攻击动画结束后切回待机
    FTimerHandle TimerHandle;
    GetWorldTimerManager().SetTimer(TimerHandle, this, &AMy2DCharacter::OnAttackFinished, AttackFlipbook->GetTotalDuration(), false);
}

void AMy2DCharacter::OnAttackFinished()
{
    PaperFlipbookComponent->SetFlipbook(IdleFlipbook);
    PaperFlipbookComponent->PlayFromStart();
}
```

## Demo 示例

一个完整的、可编译的最小 2D 角色移动示例。

```cpp
// MyPaperCharacter.h
#pragma once
#include "PaperCharacter.h"
#include "MyPaperCharacter.generated.h"

class UPaperFlipbookComponent;
class UPaperFlipbook;

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
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

private:
	void MoveRight(float Value);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Paper2D", meta = (AllowPrivateAccess = "true"))
	UPaperFlipbookComponent* FlipbookComponent;

	UPROPERTY(EditDefaultsOnly, Category = "Paper2D")
	UPaperFlipbook* IdleFlipbook;

	UPROPERTY(EditDefaultsOnly, Category = "Paper2D")
	UPaperFlipbook* RunFlipbook;
};
```

```cpp
// MyPaperCharacter.cpp
#include "MyPaperCharacter.h"
#include "PaperFlipbook.h"
#include "PaperFlipbookComponent.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

AMyPaperCharacter::AMyPaperCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	// 禁用 3D 物理和碰撞，使用 PaperCharacter 内置的 2D 物理
	GetCharacterMovement()->GravityScale = 1.0f;
	GetCharacterMovement()->SetPlaneConstraintEnabled(true);
	GetCharacterMovement()->SetPlaneConstraintNormal(FVector(0.0f, 0.0f, 1.0f)); // 约束在 XY 平面
	GetCharacterMovement()->bConstrainToPlane = true;
	GetCharacterMovement()->DefaultLandMovementMode = MOVE_Walking;
	GetCharacterMovement()->DefaultWaterMovementMode = MOVE_Swimming;
	GetCharacterMovement()->SetWalkableFloorAngle(0.0f); // 通常 2D 游戏不需要坡度

	FlipbookComponent = CreateDefaultSubobject<UPaperFlipbookComponent>(TEXT("FlipbookComponent"));
	FlipbookComponent->SetupAttachment(RootComponent);
}

void AMyPaperCharacter::BeginPlay()
{
	Super::BeginPlay();
	if (FlipbookComponent && IdleFlipbook)
	{
		FlipbookComponent->SetFlipbook(IdleFlipbook);
		FlipbookComponent->Play();
	}
}

void AMyPaperCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	PlayerInputComponent->BindAxis("MoveRight", this, &AMyPaperCharacter::MoveRight);
}

void AMyPaperCharacter::MoveRight(float Value)
{
	AddMovementInput(FVector::ForwardVector, Value);
	// 根据移动方向翻转精灵
	if (Value != 0.0f)
	{
		const float SpriteDirection = (Value > 0.0f) ? 1.0f : -1.0f;
		FlipbookComponent->SetWorldRotation(FRotator(0.0f, (SpriteDirection > 0.0f) ? 0.0f : 180.0f, 0.0f));
	}
	// 切换动画
	if (GetMovementComponent()->IsMovingOnGround())
	{
		FlipbookComponent->SetFlipbook(FMath::Abs(Value) > 0.1f ? RunFlipbook : IdleFlipbook);
	}
}

void AMyPaperCharacter::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	// 其他每帧逻辑...
}
```

## 模块依赖

要在你的 C++ 项目中使用 Paper2D 功能，需要在你的模块的 `.Build.cs` 文件中添加依赖。

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Paper2D"
});
```

| 模块 | 用途 |
|---|---|
| `Paper2D` | 核心运行时模块，包含所有 2D 组件和资产类。 |
| `Paper2DEditor` | 编辑器扩展，提供 2D 模式、图块编辑工具等。仅在编辑器中使用。 |

## 维护状态

Paper2D 是一个历史悠久且相对成熟的插件，属于 UE 的官方解决方案，维护状态稳定。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `32652778` | Harden Paper2D tile map and tile layer PostEditChangeProperty paths against null entries and non-til | 增强了图块地图编辑时的属性修改路径稳定性，修复了空指针问题。 |
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回退了一次提交，可能与之前的改动冲突或引入了问题。 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 在工具栏添加了全局吸附开关，并在吸附启用时显示红色指示器，提升了编辑体验。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下产生的双精度常量截断为单精度的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，统一日志框架。 |

### 维护评价

-   **创建时间**：2014年，是 Unreal Engine 4 时代就存在的“元老级”插件。
-   **更新频率**：**活跃维护中**。从提交历史看，2026 年仍有持续的改进和修复，主要集中在编辑器体验（吸附、图块编辑）、稳定性和代码规范（日志迁移、编译警告修复）上。
-   **稳定性**：功能已经非常成熟稳定，是 Epic Games 官方推荐的 2D 游戏开发方案。
-   **已知限制**：虽然被称为“Paper2D”，但其底层仍然是 3D 引擎。对于追求极致 2D 渲染性能（如大量独立精灵）的项目，可能需要额外优化或考虑其他专用 2D 引擎。
-   **推荐使用**：**强烈推荐**。对于需要在 Unreal Engine 生态内进行 2D 或 2.5D 游戏开发的团队来说，Paper2D 是最成熟、最集成的选择，文档和社区支持也相对完善。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/2D/index.html) (Unreal Engine 官方 2D 文档页)

---

# Spriter Importer

> [Experimental] A module that allows importing Spriter SCML animation files into Paper2D assets.

| 属性 | 值 |
|---|---|
| 中文名 | Spriter 导入器 |
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SpriterImporter` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2014-09-16 (随主插件) |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Source/SpriterImporter) | |

## 用途

Spriter Importer 是一个**实验性**的导入工具模块，专门用于将 [BrashMonkey Spriter](https://brashmonkey.com/) 这款 2D 骨骼动画软件制作的动画项目（以 `.scml` 文件描述）导入到 Unreal Engine 中，并转换为 Paper2D 的资产（如 `PaperSprite` 和 `PaperFlipbook`）。

它解析 SCML 文件的 JSON 结构，构建对应的数据模型（如 `FSpriterSCON`, `FSpriterEntity`, `FSpriterAnimation`），然后在 UE 内部重新创建这些资产，实现动画从 Spriter 工具到 UE 引擎的迁移。

## 使用场景

-   你的美术团队使用 **Spriter Pro** 进行角色动画的制作和绑定。
-   你希望将 Spriter 中制作的复杂、流畅的骨骼动画序列 **批量导入**到 UE 项目中，用于 Paper2D 游戏角色。
-   你的工作流依赖 Spriter 进行动画迭代，需要与 UE 项目同步。

## 蓝图用法

该模块主要提供编辑器导入功能，不直接暴露大量运行时蓝图节点。导入过程通过 UE 编辑器的“导入”功能触发。

1.  **导入 SCML 文件**：
    *   在 Content Browser 中右键，选择 `Import`。
    *   选择你的 `.scml` 文件。
    *   Spriter Importer 工厂类（`USpriterImporterFactory`）会自动识别该文件，并弹出导入选项。
    *   导入完成后，会在目标目录下生成对应的 `PaperSprite` 和 `PaperFlipbook` 资产。

2.  **查看导入数据**（用于调试）：
    *   导入过程中会创建一个 `UPaperSpriterImportData` 资产（标记为实验性）。
    *   在内容浏览器中可以找到并打开它，在详情面板中可以查看原始的 Spriter 数据模型（`FSpriterSCON ImportedData`）。

## C++ 用法

该模块的核心功能是导入，其 API 主要供编辑器工厂类内部使用。外部模块很少直接调用。

### 头文件引入

通常无需直接引入此模块头文件，除非你要扩展或调试导入流程。

```cpp
// 如果你需要访问导入后的数据
#include "SpriterImporter/PaperSpriterImportData.h"
```

### 基本用法

该模块内部的关键类是 `USpriterImporterFactory`，它继承自 `UFactory`，重写了 `FactoryCanImport` 和 `FactoryCreateText` 方法来处理 `.scml` 文件。

```cpp
// 伪代码：描述导入过程
UObject* USpriterImporterFactory::FactoryCreateText(...)
{
    // 1. 解析 SCML 文件内容（JSON格式）到 FSpriterSCON 结构体
    FSpriterSCON SpriterData;
    SpriterData.ParseFromJSON(JsonRootObject, Filename, bSilent);

    // 2. 根据 FSpriterSCON 中的 Folders 和 Entities 信息
    //    遍历 SpriterData.Folders，为每个 SpriterFile 创建 UTexture2D 和 UPaperSprite
    //    遍历 SpriterData.Entities，为每个 SpriterAnimation 创建 UPaperFlipbook

    // 3. 保存创建的资产，并设置它们之间的引用关系
}
```

### 进阶用法

理解其数据结构有助于自定义导入逻辑或调试问题。

```cpp
// 访问导入后的原始数据（仅用于调试）
void DebugSpriterImportData(UPaperSpriterImportData* ImportData)
{
    if (ImportData && ImportData->ImportedData.bSuccessfullyParsed)
    {
        const FSpriterSCON& Scon = ImportData->ImportedData;
        UE_LOG(LogTemp, Log, TEXT("Generator: %s %s"), *Scon.Generator, *Scon.GeneratorVersion);
        UE_LOG(LogTemp, Log, TEXT("Entities Count: %d"), Scon.Entities.Num());
        for (const FSpriterEntity& Entity : Scon.Entities)
        {
            UE_LOG(LogTemp, Log, TEXT("  Entity: %s, Animations: %d"), *Entity.Name, Entity.Animations.Num());
        }
    }
}
```

## Demo 示例

演示如何通过 C++ 触发导入（通常在编辑器工具中）。

```cpp
// 假设你已经知道 SCML 文件的路径
FString SCMLFilePath = TEXT("C:/MyProject/SpriterAssets/character.scml");
FString TargetContentPath = TEXT("/Game/2D/Characters/Imported");

// 使用 UAssetImportTask 来异步导入
UAssetImportTask* ImportTask = NewObject<UAssetImportTask>();
ImportTask->Filename = SCMLFilePath;
ImportTask->DestinationPath = TargetContentPath;
ImportTask->bReplaceExisting = true;
ImportTask->bAutomated = true; // 静默导入

// 获取资产导入管理器并执行任务
UAssetImportTask* TaskArray[] = { ImportTask };
FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools");
AssetToolsModule.Get().ImportAssetTasks(TArrayView<UAssetImportTask*>(TaskArray));

// 任务完成后，可以检查 ImportTask->Result 以及 TargetContentPath 下生成的资产
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 核心库，提供基本类型、JSON 解析等。 |
| `CoreUObject` | UObject 系统基础。 |
| `Engine` | 引擎核心。 |
| `UnrealEd` | 编辑器核心，用于资产导入工厂。 |
| `Paper2D` | 依赖 Paper2D 的核心资产类型（`PaperSprite`, `PaperFlipbook`）。 |

## 维护状态

### 近期更新

（该模块的更新包含在主 Paper2D 插件的更新中，没有独立的提交记录。）

### 维护评价

-   **实验性**：模块被标记为 `Experimental`（见 `UPaperSpriterImportData` 类注释），表明其功能可能不稳定或随时会改变。
-   **维护状态**：**不活跃**。虽然整个 Paper2D 插件仍在更新，但 Spriter Importer 作为其子模块，近年来的提交记录（如用户提供的）未显示针对此模块的功能性更新。它更像是一个历史遗留的、功能完整的工具。
-   **推荐使用**：**谨慎使用**。如果你的工作流**强依赖** Spriter，并且该模块能满足你的导入需求，可以使用。否则，建议使用更主流或官方支持更好的动画方案（如 UE 内置的 2D 骨骼动画或 Spine 的官方 UE 运行时）。
-   **潜在风险**：由于长期缺乏实质性更新，未来 UE 版本升级时可能存在兼容性风险。主要风险在于其内部的数据结构（`FSpriter*`）和 JSON 解析逻辑可能无法跟上 Spriter 软件格式的更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Source/SpriterImporter)
-   [Spriter 官方网站](https://brashmonkey.com/)
-   [Paper2D 主文档](../index.md)