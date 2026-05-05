# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、示例资源） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor), `SpriterImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是 UE 内置的 2D 游戏开发框架，提供从精灵（Sprite）渲染、逐帧动画（Flipbook）、瓦片地图（Tile Map）到 2D 地形（Terrain）的完整 2D 游戏开发工具链。它解决的核心问题是：**在以 3D 为主引擎中高效地制作 2D 游戏内容**。

具体功能包括：
- **精灵系统**：将纹理区域定义为精灵资产，支持碰撞几何体、Socket、多纹理槽位
- **翻页动画（Flipbook）**：将多个精灵帧组合为逐帧动画，支持播放控制、循环、碰撞
- **瓦片地图（Tile Map）**：基于瓦片集（Tile Set）构建 2D 关卡，支持正交/等距/六角投影、多层、碰撞
- **分组精灵（Grouped Sprite）**：将大量精灵实例合并为单个组件，减少 Draw Call
- **2D 地形（Terrain）**：沿样条线自动生成地形精灵（实验性）
- **纹理图集（Atlas）**：将精灵打包到共享纹理图集中（实验性）
- **编辑器工具**：精灵编辑器、瓦片地图编辑器、Smart Snapping、精灵表/Tiled 地图导入器

## 使用场景

- 你在做一个 2D 平台跳跃游戏 → 使用 `APaperCharacter` + `UPaperFlipbookComponent` 处理角色动画，`UPaperTileMapComponent` 构建关卡
- 你需要制作 2D 逐帧动画角色 → 使用 `UPaperFlipbook` 定义关键帧序列，`UPaperFlipbookComponent` 播放
- 你有大量静态 2D 物体需要高效渲染 → 使用 `UPaperGroupedSpriteComponent` 合并 Draw Call
- 你使用 Tiled 编辑器制作地图 → 使用 `PaperTiledImporter` 导入 `.tmx` 文件
- 你有精灵表（Sprite Sheet）需要切割 → 使用 `PaperSpriteSheetImporter` 导入
- 你需要在 UMG 中使用 2D 精灵 → 使用 `UPaperSpriteBlueprintLibrary::MakeBrushFromSprite`

## 蓝图用法

### 精灵组件（PaperSpriteComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Sprite` | 更换组件使用的精灵资产 | `UPaperSpriteComponent` |
| `Get Sprite` | 获取当前精灵资产 | `UPaperSpriteComponent` |
| `Set Sprite Color` | 设置精灵颜色（传入材质作为顶点色） | `UPaperSpriteComponent` |

### 翻页动画组件（PaperFlipbookComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Flipbook` | 设置翻页动画资产（新动画会重置播放时间） | `UPaperFlipbookComponent` |
| `Get Flipbook` | 获取当前翻页动画 | `UPaperFlipbookComponent` |
| `Play` | 从当前位置开始播放 | `UPaperFlipbookComponent` |
| `Play From Start` | 从头开始播放 | `UPaperFlipbookComponent` |
| `Reverse` | 从当前位置反向播放 | `UPaperFlipbookComponent` |
| `Reverse From End` | 从末尾反向播放 | `UPaperFlipbookComponent` |
| `Stop` | 停止播放 | `UPaperFlipbookComponent` |
| `Is Playing` | 是否正在播放 | `UPaperFlipbookComponent` |
| `Is Reversing` | 是否正在反向播放 | `UPaperFlipbookComponent` |
| `Set Playback Position` | 设置播放位置（秒） | `UPaperFlipbookComponent` |
| `Get Playback Position` | 获取当前播放位置 | `UPaperFlipbookComponent` |
| `Set Play Rate` | 设置播放速率 | `UPaperFlipbookComponent` |
| `Get Play Rate` | 获取播放速率 | `UPaperFlipbookComponent` |
| `Set Looping` | 设置是否循环 | `UPaperFlipbookComponent` |
| `Is Looping` | 是否循环播放 | `UPaperFlipbookComponent` |
| `Get Flipbook Length` | 获取动画总时长（秒） | `UPaperFlipbookComponent` |
| `Get Flipbook Frame Count` | 获取总帧数 | `UPaperFlipbookComponent` |
| `On Finished Playing` | 非循环动画播放完毕事件 | `UPaperFlipbookComponent` |

### 翻页动画资产（PaperFlipbook）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Num Frames` | 获取总帧数 | `UPaperFlipbook` |
| `Get Total Duration` | 获取总时长（秒） | `UPaperFlipbook` |
| `Get Key Frame Index At Time` | 获取指定时间的关键帧索引 | `UPaperFlipbook` |
| `Get Sprite At Time` | 获取指定时间的精灵 | `UPaperFlipbook` |

### 分组精灵组件（PaperGroupedSpriteComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Instance` | 添加精灵实例（返回实例索引） | `UPaperGroupedSpriteComponent` |
| `Get Instance Transform` | 获取实例变换 | `UPaperGroupedSpriteComponent` |
| `Update Instance Transform` | 更新实例变换 | `UPaperGroupedSpriteComponent` |
| `Update Instance Color` | 更新实例颜色 | `UPaperGroupedSpriteComponent` |
| `Remove Instance` | 移除指定实例 | `UPaperGroupedSpriteComponent` |
| `Clear Instances` | 清除所有实例 | `UPaperGroupedSpriteComponent` |
| `Get Instance Count` | 获取实例数量 | `UPaperGroupedSpriteComponent` |

### 瓦片地图工具（TileMapBlueprintLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Tile User Data` | 获取瓦片的用户数据名称 | `UTileMapBlueprintLibrary` |
| `Get Tile Transform` | 获取瓦片变换 | `UTileMapBlueprintLibrary` |
| `Break Tile` | 拆解瓦片信息（索引、瓦片集、翻转） | `UTileMapBlueprintLibrary` |
| `Make Tile` | 从信息创建瓦片 | `UTileMapBlueprintLibrary` |

### 精灵工具（PaperSpriteBlueprintLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Brush From Sprite` | 从精灵创建 Slate Brush（用于 UMG） | `UPaperSpriteBlueprintLibrary` |

### 使用示例（蓝图描述）

**2D 角色动画控制：**
1. 创建一个 `APaperCharacter`（或在 Pawn 上添加 `UPaperFlipbookComponent`）
2. 在 BeginPlay 中调用 `Set Flipbook` 设置待机动画
3. 在输入事件中，根据移动方向调用 `Set Flipbook` 切换为跑步动画
4. 监听 `On Finished Playing` 事件处理一次性动画（如攻击）结束后的状态切换

**瓦片地图关卡构建：**
1. 创建 `UPaperTileMap` 资产，设置地图宽高和瓦片尺寸
2. 创建 `UPaperTileSet` 资产，指定瓦片纹理和瓦片尺寸
3. 在 `UPaperTileMap` 的各层中使用 `Make Tile` 填充瓦片
4. 将 Tile Map 拖入关卡，自动生成 `APaperTileMapActor`

**UMG 中显示精灵：**
1. 获取 `UPaperSprite` 资产引用
2. 调用 `Make Brush From Sprite` 创建 `FSlateBrush`
3. 将 Brush 赋给 Image 控件

## C++ 用法

### 头文件引入

```cpp
#include "Paper2DModule.h"
#include "PaperSprite.h"
#include "PaperFlipbook.h"
#include "PaperFlipbookComponent.h"
#include "PaperSpriteComponent.h"
#include "PaperTileMap.h"
#include "PaperTileMapComponent.h"
#include "PaperTileSet.h"
#include "PaperGroupedSpriteComponent.h"
#include "PaperCharacter.h"
```

### 基本用法：创建翻页动画角色

```cpp
// 在自定义 Character 类中使用 PaperFlipbookComponent
// 来源: PaperCharacter.h

#include "PaperFlipbookComponent.h"
#include "PaperFlipbook.h"

class AMy2DCharacter : public APaperCharacter
{
    GENERATED_BODY()

public:
    void PlayAttackAnimation()
    {
        UPaperFlipbookComponent* SpriteComp = GetSprite();
        if (SpriteComp && AttackFlipbook)
        {
            SpriteComp->SetFlipbook(AttackFlipbook);
            SpriteComp->PlayFromStart();
        }
    }

    void SetIdleAnimation()
    {
        UPaperFlipbookComponent* SpriteComp = GetSprite();
        if (SpriteComp && IdleFlipbook)
        {
            SpriteComp->SetFlipbook(IdleFlipbook);
            SpriteComp->Play();
            SpriteComp->SetLooping(true);
        }
    }

protected:
    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    TObjectPtr<UPaperFlipbook> IdleFlipbook;

    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    TObjectPtr<UPaperFlipbook> AttackFlipbook;
};
```

### 基本用法：精灵组件操作

```cpp
// 动态创建和配置精灵组件
// 来源: PaperSpriteComponent.h

#include "PaperSpriteComponent.h"
#include "PaperSprite.h"

void AMyActor::SetupSprite()
{
    UPaperSpriteComponent* SpriteComp = NewObject<UPaperSpriteComponent>(this);
    SpriteComp->SetSprite(MySpriteAsset);
    SpriteComp->SetSpriteColor(FLinearColor(1.0f, 0.5f, 0.5f, 1.0f));
    SpriteComp->RegisterComponent();
    SpriteComp->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);
}
```

### 进阶用法：分组精灵批量渲染

```cpp
// 使用 GroupedSpriteComponent 高效渲染大量精灵实例
// 来源: PaperGroupedSpriteComponent.h

#include "PaperGroupedSpriteComponent.h"
#include "PaperSprite.h"

void AMyLevelManager::PopulateBackground()
{
    UPaperGroupedSpriteComponent* GroupedComp = NewObject<UPaperGroupedSpriteComponent>(this);
    GroupedComp->RegisterComponent();
    GroupedComp->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

    // 批量添加精灵实例
    for (int32 i = 0; i < 1000; ++i)
    {
        FTransform InstanceTransform;
        InstanceTransform.SetLocation(FVector(i * 100.0f, 0.0f, 0.0f));
        
        UPaperSprite* SpriteToUse = (i % 2 == 0) ? TreeSprite : BushSprite;
        FLinearColor TintColor = FLinearColor::MakeRandomColor();
        
        GroupedComp->AddInstance(InstanceTransform, SpriteToUse, false, TintColor);
    }

    // 动态更新某个实例
    FTransform NewTransform;
    NewTransform.SetLocation(FVector(500.0f, 0.0f, 100.0f));
    GroupedComp->UpdateInstanceTransform(42, NewTransform, false, true);
}
```

### 进阶用法：程序化瓦片地图

```cpp
// 程序化生成瓦片地图
// 来源: PaperTileMapComponent.h, PaperTileMap.h, PaperTileSet.h

#include "PaperTileMapComponent.h"
#include "PaperTileMap.h"
#include "PaperTileLayer.h"
#include "PaperTileSet.h"
#include "TileMapBlueprintLibrary.h"

void AMyDungeonGenerator::GenerateTileMap()
{
    UPaperTileMapComponent* TileMapComp = FindComponentByClass<UPaperTileMapComponent>();
    if (!TileMapComp) return;

    // 创建新的瓦片地图
    TileMapComp->CreateNewTileMap(32, 32, 32, 32, 1.0f);

    // 设置材质和碰撞
    TileMapComp->SetTileMapColor(FLinearColor::White);
    TileMapComp->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);

    // 填充瓦片
    for (int32 Y = 0; Y < 32; ++Y)
    {
        for (int32 X = 0; X < 32; ++X)
        {
            // 使用 MakeTile 创建瓦片信息
            FPaperTileInfo TileInfo;
            TileInfo.TileSet = MyTileSet;
            
            // 根据位置选择不同瓦片
            if (Y == 0 || Y == 31 || X == 0 || X == 31)
            {
                TileInfo.PackedTileIndex = 0; // 墙壁瓦片
            }
            else
            {
                TileInfo.PackedTileIndex = 1; // 地板瓦片
            }

            TileMapComp->SetTile(X, Y, 0, TileInfo);
        }
    }
}
```

## Demo 示例

### 2D 角色控制器

```cpp
// My2DCharacter.h
#pragma once

#include "PaperCharacter.h"
#include "My2DCharacter.generated.h"

class UPaperFlipbook;

UCLASS()
class AMy2DCharacter : public APaperCharacter
{
    GENERATED_BODY()

public:
    AMy2DCharacter();

    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

protected:
    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    TObjectPtr<UPaperFlipbook> IdleFlipbook;

    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    TObjectPtr<UPaperFlipbook> RunFlipbook;

    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    TObjectPtr<UPaperFlipbook> JumpFlipbook;

    UPROPERTY(EditDefaultsOnly, Category = "Movement")
    float MoveSpeed = 300.0f;

private:
    void MoveRight(float Value);
    void UpdateAnimation();

    float CurrentDirection;
};
```

```cpp
// My2DCharacter.cpp
#include "My2DCharacter.h"
#include "PaperFlipbookComponent.h"
#include "PaperFlipbook.h"
#include "Components/InputComponent.h"

AMy2DCharacter::AMy2DCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
    CurrentDirection = 1.0f;
}

void AMy2DCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    PlayerInputComponent->BindAxis("MoveRight", this, &AMy2DCharacter::MoveRight);
}

void AMy2DCharacter::MoveRight(float Value)
{
    if (Value != 0.0f)
    {
        CurrentDirection = Value;
        AddMovementInput(FVector(1.0f, 0.0f, 0.0f), Value);
    }
}

void AMy2DCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    UpdateAnimation();
}

void AMy2DCharacter::UpdateAnimation()
{
    UPaperFlipbookComponent* SpriteComp = GetSprite();
    if (!SpriteComp) return;

    const FVector Velocity = GetVelocity();
    const bool bIsInAir = GetMovementComponent()->IsFalling();

    // 翻转精灵朝向
    if (CurrentDirection < 0.0f)
    {
        SpriteComp->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
    }
    else
    {
        SpriteComp->SetRelativeRotation(FRotator::ZeroRotator);
    }

    // 选择动画
    if (bIsInAir)
    {
        if (SpriteComp->GetFlipbook() != JumpFlipbook)
        {
            SpriteComp->SetFlipbook(JumpFlipbook);
        }
    }
    else if (FMath::Abs(Velocity.X) > 10.0f)
    {
        if (SpriteComp->GetFlipbook() != RunFlipbook)
        {
            SpriteComp->SetFlipbook(RunFlipbook);
            SpriteComp->Play();
        }
    }
    else
    {
        if (SpriteComp->GetFlipbook() != IdleFlipbook)
        {
            SpriteComp->SetFlipbook(IdleFlipbook);
            SpriteComp->Play();
        }
    }
}
```

## 模块依赖

Paper2D Runtime 模块的 Build.cs 包含对 `EditorFramework` 和 `UnrealEd` 的依赖（这在 Runtime 模块中较为少见，可能用于条件编译的编辑器功能）。

使用者的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `Paper2D` | 核心运行时功能（精灵、翻页动画、瓦片地图等） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：如果你需要在编辑器中使用 Paper2D 的编辑器功能（如精灵编辑器、瓦片地图编辑器），需要额外依赖 `Paper2DEditor` 模块（仅 Editor 类型）。

## 维护状态

### 近期更新

```
- 08316dbb9bc5 Cache the ShaderPlatform inside MaterialResource, derive the FeatureLevel from that ShaderPlatform.
- 365a11c5b937 [UObject/General] - Cleanup code and convert to the new ConditionalPreload function - Fix a few thread-safety issue when resetting flags before preloading
- 6ae573356bbf Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
```

### 维护评价

**⚠️ 维护不活跃 — 可能处于半废弃状态**

Paper2D 自 2014 年创建以来已有超过 11 年历史。从近期 commit 记录来看，最近的三次提交均为**引擎全局性重构**（ShaderPlatform 缓存、ConditionalPreload 清理、dllstorage 转换），并非 Paper2D 功能性更新。这表明 Paper2D 已经很长时间没有获得专门的功能开发或 Bug 修复。

关键观察：
- **创建时间极早**：2014 年，是 UE4 时代的产物
- **无专门维护**：近期 commit 全部是引擎级全局改动的副作用
- **实验性功能未完成**：纹理图集（Atlas）、地形（Terrain）等功能仍标记为 Experimental，多年未推进
- **2D 物理已废弃**：`ESpriteCollisionMode::Use2DPhysics` 标记为 `Hidden` 和 `Deprecated`
- **社区反馈**：Paper2D 在社区中普遍被认为功能不完整，Epic 官方已多年未投入开发资源

**建议**：
- 对于简单的 2D 项目或原型开发，Paper2D 仍然可用
- 对于生产级 2D 游戏，建议评估第三方方案（如 Unreal 的 PaperZD 插件、或考虑其他引擎）
- 使用时注意实验性功能（Atlas、Terrain）可能不稳定

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/2D/Paper2D)
- 官方文档（无）