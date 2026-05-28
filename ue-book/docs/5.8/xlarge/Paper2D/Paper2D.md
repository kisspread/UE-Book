# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 中文名 | 2D 游戏框架 |
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（默认材质、示例资产） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是 Unreal Engine 内置的 **2D 游戏开发框架**，提供了一套完整的 2D 游戏开发工具链。它解决的核心问题是：在以 3D 引擎著称的 Unreal Engine 中，高效地制作 2D 游戏。

具体功能包括：

- **Sprite 系统**：将 2D 纹理区域封装为 `UPaperSprite` 资产，支持自定义碰撞、渲染几何、材质、Socket 插槽和像素到世界单位的缩放
- **Flipbook 动画**：通过 `UPaperFlipbook` 将多个 Sprite 组成逐帧动画序列，支持播放/暂停/倒放/循环/变速控制
- **TileMap 瓦片地图**：完整的 2D 瓦片地图编辑系统，支持正交、等距菱形、等距交错、六边形交错四种投影模式，多层编辑，每瓦片碰撞和元数据
- **TileSet 瓦片集**：管理瓦片图集纹理，支持边距/间距/偏移配置，每瓦片自定义碰撞和用户数据
- **Grouped Sprite 批处理渲染**：将大量 Sprite 实例合并为单个组件渲染，减少 draw call
- **Terrain 地形系统**（实验性）：基于样条线的 2D 地形生成工具
- **纹理图集**（实验性）：将多个 Sprite 打包到共享纹理图集，优化渲染性能
- **物理集成**：支持 3D 碰撞域，可为 Sprite 和 TileMap 生成物理碰撞体
- **2D 角色**：`APaperCharacter` 封装了基于 Flipbook 的 2D 角色，继承自 `ACharacter` 可使用完整的角色移动组件

## 使用场景

- 你在做一个 **2D 平台跳跃游戏**（类似空洞骑士、蔚蓝）→ 使用 `UPaperFlipbookComponent` + `APaperCharacter` + TileMap
- 你需要制作 **逐帧动画角色** → 创建 `UPaperFlipbook` 资产，配合 `UPaperFlipbookComponent` 播放
- 你有一个 **俯视角/侧视角 2D 关卡**需要快速搭建 → 使用 `UPaperTileMap` + `UPaperTileSet` 进行瓦片编辑
- 你需要在场景中放置大量 **静态 2D 元素**（背景装饰、粒子等）→ 使用 `UPaperGroupedSpriteComponent` 批量渲染
- 你需要为 2D 精灵添加 **物理碰撞** → 在 `UPaperSprite` 中配置碰撞几何，支持自动/手动多边形
- 你需要绘制 **2D 地形轮廓** → 使用 `UPaperTerrainComponent`（实验性功能）
- 你需要将多个 Sprite **合并到一张纹理图集** 以优化渲染 → 使用 `UPaperSpriteAtlas`（实验性功能）

## 蓝图用法

### 核心节点

#### Sprite 组件（UPaperSpriteComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSprite` | 切换组件使用的 Sprite 资产 | `UPaperSpriteComponent` |
| `GetSprite` | 获取当前使用的 Sprite 资产 | `UPaperSpriteComponent` |
| `SetSpriteColor` | 设置 Sprite 顶点颜色（与材质颜色相乘） | `UPaperSpriteComponent` |

#### Flipbook 组件（UPaperFlipbookComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetFlipbook` | 设置要播放的 Flipbook 资产（新资产会重置播放时间） | `UPaperFlipbookComponent` |
| `GetFlipbook` | 获取当前 Flipbook 资产 | `UPaperFlipbookComponent` |
| `Play` | 从当前位置开始播放 | `UPaperFlipbookComponent` |
| `PlayFromStart` | 从头开始播放 | `UPaperFlipbookComponent` |
| `Reverse` | 从当前位置倒放 | `UPaperFlipbookComponent` |
| `ReverseFromEnd` | 从末尾开始倒放 | `UPaperFlipbookComponent` |
| `Stop` | 停止播放 | `UPaperFlipbookComponent` |
| `IsPlaying` | 是否正在播放 | `UPaperFlipbookComponent` |
| `IsReversing` | 是否正在倒放 | `UPaperFlipbookComponent` |
| `SetLooping` | 设置是否循环 | `UPaperFlipbookComponent` |
| `IsLooping` | 获取是否循环 | `UPaperFlipbookComponent` |
| `SetPlayRate` | 设置播放速率（1.0 为正常速度） | `UPaperFlipbookComponent` |
| `GetPlayRate` | 获取播放速率 | `UPaperFlipbookComponent` |
| `SetPlaybackPosition` | 跳转到指定时间位置（秒） | `UPaperFlipbookComponent` |
| `SetPlaybackPositionInFrames` | 跳转到指定帧位置 | `UPaperFlipbookComponent` |
| `GetPlaybackPosition` | 获取当前播放位置（秒） | `UPaperFlipbookComponent` |
| `GetPlaybackPositionInFrames` | 获取当前播放位置（帧） | `UPaperFlipbookComponent` |
| `GetFlipbookLength` | 获取 Flipbook 总时长（秒） | `UPaperFlipbookComponent` |
| `GetFlipbookLengthInFrames` | 获取 Flipbook 总帧数 | `UPaperFlipbookComponent` |
| `GetFlipbookFramerate` | 获取标称帧率（fps） | `UPaperFlipbookComponent` |
| `SetSpriteColor` | 设置 Sprite 顶点颜色 | `UPaperFlipbookComponent` |
| `GetSpriteColor` | 获取 Sprite 顶点颜色 | `UPaperFlipbookComponent` |

**Flipbook 完成事件**：`OnFinishedPlaying` — 非循环模式下，Flipbook 播放到起点或终点时触发。

#### TileMap 组件（UPaperTileMapComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateNewTileMap` | 动态创建新 TileMap（指定尺寸和像素单位） | `UPaperTileMapComponent` |
| `SetTileMap` | 设置使用的 TileMap 资产 | `UPaperTileMapComponent` |
| `OwnsTileMap` | 是否拥有独立的 TileMap 实例（可编辑） | `UPaperTileMapComponent` |
| `MakeTileMapEditable` | 将资产引用克隆为可编辑实例 | `UPaperTileMapComponent` |
| `GetMapSize` | 获取地图宽、高和层数 | `UPaperTileMapComponent` |
| `GetTile` | 获取指定坐标的瓦片信息 | `UPaperTileMapComponent` |
| `SetTile` | 设置指定坐标的瓦片（仅对 OwnsTileMap 生效） | `UPaperTileMapComponent` |
| `ResizeMap` | 调整地图尺寸 | `UPaperTileMapComponent` |
| `AddNewLayer` | 添加新图层 | `UPaperTileMapComponent` |
| `GetTileMapColor` / `SetTileMapColor` | 获取/设置全局颜色乘数 | `UPaperTileMapComponent` |
| `GetLayerColor` / `SetLayerColor` | 获取/设置单层颜色乘数 | `UPaperTileMapComponent` |
| `GetTileCornerPosition` | 获取瓦片左上角坐标 | `UPaperTileMapComponent` |
| `GetTileCenterPosition` | 获取瓦片中心坐标 | `UPaperTileMapComponent` |
| `GetTilePolygon` | 获取瓦片多边形顶点 | `UPaperTileMapComponent` |
| `SetDefaultCollisionThickness` | 设置默认碰撞厚度 | `UPaperTileMapComponent` |
| `SetLayerCollision` | 配置单层碰撞属性 | `UPaperTileMapComponent` |
| `RebuildCollision` | 重建碰撞体 | `UPaperTileMapComponent` |

#### Grouped Sprite 组件（UPaperGroupedSpriteComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddInstance` | 添加一个 Sprite 实例（返回实例索引） | `UPaperGroupedSpriteComponent` |
| `GetInstanceTransform` | 获取实例变换 | `UPaperGroupedSpriteComponent` |
| `UpdateInstanceTransform` | 更新实例变换 | `UPaperGroupedSpriteComponent` |
| `UpdateInstanceColor` | 更新实例颜色 | `UPaperGroupedSpriteComponent` |
| `RemoveInstance` | 移除实例 | `UPaperGroupedSpriteComponent` |
| `ClearInstances` | 清除所有实例 | `UPaperGroupedSpriteComponent` |
| `GetInstanceCount` | 获取实例总数 | `UPaperGroupedSpriteComponent` |
| `SortInstancesAlongAxis` | 按世界空间指定轴排序实例（用于正确的遮挡） | `UPaperGroupedSpriteComponent` |

#### Flipbook 资产（UPaperFlipbook）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumFrames` | 获取总帧数 | `UPaperFlipbook` |
| `GetTotalDuration` | 获取总时长（秒） | `UPaperFlipbook` |
| `GetKeyFrameIndexAtTime` | 获取指定时间对应的关键帧索引 | `UPaperFlipbook` |
| `GetSpriteAtTime` | 获取指定时间对应的 Sprite | `UPaperFlipbook` |
| `GetSpriteAtFrame` | 获取指定帧索引对应的 Sprite | `UPaperFlipbook` |
| `GetNumKeyFrames` | 获取关键帧数量 | `UPaperFlipbook` |
| `IsValidKeyFrameIndex` | 索引是否有效 | `UPaperFlipbook` |

#### 蓝图函数库

**UTileMapBlueprintLibrary**：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BreakTile` | 拆解瓦片信息（TileIndex, TileSet, bFlipH, bFlipV, bFlipD） | `UTileMapBlueprintLibrary` |
| `MakeTile` | 构造瓦片信息 | `UTileMapBlueprintLibrary` |
| `GetTileUserData` | 获取瓦片用户数据名称 | `UTileMapBlueprintLibrary` |
| `GetTileTransform` | 获取瓦片变换（含翻转标志） | `UTileMapBlueprintLibrary` |

**UPaperSpriteBlueprintLibrary**：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeBrushFromSprite` | 从 Sprite 创建 Slate Brush（用于 UI） | `UPaperSpriteBlueprintLibrary` |

### 使用示例（蓝图描述）

**创建一个 2D 角色动画**：
1. 在内容浏览器右键创建 `Paper Flipbook` 资产
2. 设置 `FramesPerSecond`（例如 12）
3. 在 `KeyFrames` 数组中添加帧，每帧指定一个 `UPaperSprite` 和持续帧数
4. 在蓝图 Actor 中添加 `PaperFlipbookComponent`
5. 调用 `SetFlipbook` 设置资产，然后调用 `Play` 开始播放
6. 监听 `OnFinishedPlaying` 事件处理动画结束逻辑

**动态创建和编辑 TileMap**：
1. 在 Actor 蓝图中添加 `PaperTileMapComponent`
2. 调用 `CreateNewTileMap`（参数：宽 10、高 10、瓦片宽 32、高 32、像素单位 1.0、创建层 true）
3. 使用 `MakeTile` 构造瓦片信息（传入 TileSet 资产和瓦片索引）
4. 调用 `SetTile` 逐格放置瓦片
5. 调用 `RebuildCollision` 更新碰撞

**在场景中批量放置 Sprite**：
1. 在 Actor 蓝图中添加 `PaperGroupedSpriteComponent`
2. 使用 `AddInstance` 在不同位置添加多个 Sprite 实例
3. 如需正确的前后遮挡，调用 `SortInstancesAlongAxis` 按 Y 轴排序

## C++ 用法

### 头文件引入

```cpp
#include "PaperSprite.h"
#include "PaperSpriteComponent.h"
#include "PaperFlipbook.h"
#include "PaperFlipbookComponent.h"
#include "PaperTileMap.h"
#include "PaperTileMapComponent.h"
#include "PaperTileLayer.h"
#include "PaperTileSet.h"
#include "PaperGroupedSpriteComponent.h"
#include "PaperCharacter.h"
```

### 基本用法——Flipbook 动画控制

来源：`Classes/PaperFlipbookComponent.h`

```cpp
// 获取 Flipbook 组件并控制播放
UPaperFlipbookComponent* FlipbookComp = MyActor->FindComponentByClass<UPaperFlipbookComponent>();
if (FlipbookComp)
{
    // 设置新的 Flipbook 资产
    UPaperFlipbook* RunFlipbook = LoadObject<UPaperFlipbook>(nullptr, TEXT("/Game/Sprites/RunFlipbook"));
    FlipbookComp->SetFlipbook(RunFlipbook);
    
    // 配置播放参数
    FlipbookComp->SetPlayRate(1.5f);    // 1.5倍速播放
    FlipbookComp->SetLooping(true);     // 循环播放
    
    // 开始播放
    FlipbookComp->Play();
    
    // 获取播放状态
    bool bPlaying = FlipbookComp->IsPlaying();
    float CurrentTime = FlipbookComp->GetPlaybackPosition();
    int32 CurrentFrame = FlipbookComp->GetPlaybackPositionInFrames();
    float TotalDuration = FlipbookComp->GetFlipbookLength();
    
    // 绑定播放完成事件
    FlipbookComp->OnFinishedPlaying.AddDynamic(this, &AMyActor::OnFlipbookFinished);
}
```

### 基本用法——Sprite 操作

来源：`Classes/PaperSpriteComponent.h`, `Classes/PaperSprite.h`

```cpp
// 设置 Sprite 并修改颜色
UPaperSpriteComponent* SpriteComp = MyActor->FindComponentByClass<UPaperSpriteComponent>();
if (SpriteComp)
{
    UPaperSprite* MySprite = LoadObject<UPaperSprite>(nullptr, TEXT("/Game/Sprites/CharacterIdle"));
    SpriteComp->SetSprite(MySprite);
    SpriteComp->SetSpriteColor(FLinearColor(1.0f, 0.5f, 0.5f, 1.0f)); // 染红
}

// 获取 Sprite 属性
UPaperSprite* Sprite = SpriteComp->GetSprite();
if (Sprite)
{
    float PixelsPerUU = Sprite->GetPixelsPerUnrealUnit();
    UMaterialInterface* DefaultMat = Sprite->GetDefaultMaterial();
    FBoxSphereBounds Bounds = Sprite->GetRenderBounds();
    
    // 查询 Socket
    TArray<FComponentSocketDescription> Sockets;
    Sprite->QuerySupportedSockets(Sockets);
}
```

### 基本用法——TileMap 操作

来源：`Classes/PaperTileMapComponent.h`, `Classes/PaperTileLayer.h`, `Classes/PaperTileSet.h`

```cpp
UPaperTileMapComponent* TileMapComp = MyActor->FindComponentByClass<UPaperTileMapComponent>();
if (TileMapComp)
{
    // 创建新的 TileMap
    TileMapComp->CreateNewTileMap(
        /*MapWidth=*/ 20,
        /*MapHeight=*/ 15,
        /*TileWidth=*/ 16,
        /*TileHeight=*/ 16,
        /*PixelsPerUnrealUnit=*/ 1.0f,
        /*bCreateLayer=*/ true
    );
    
    // 设置瓦片
    UPaperTileSet* TileSet = LoadObject<UPaperTileSet>(nullptr, TEXT("/Game/TileSets/GrassTileSet"));
    
    FPaperTileInfo TileInfo;
    TileInfo.TileSet = TileSet;
    TileInfo.PackedTileIndex = 0; // 第一个瓦片
    
    TileMapComp->SetTile(0, 0, 0, TileInfo); // 在 (0,0) 层 0 放置瓦片
    
    // 设置颜色
    TileMapComp->SetTileMapColor(FLinearColor::White);
    TileMapComp->SetLayerColor(FLinearColor(1.0f, 0.9f, 0.9f), 0);
    
    // 配置碰撞
    TileMapComp->SetDefaultCollisionThickness(50.0f, false);
    TileMapComp->SetLayerCollision(0, true, true, 50.0f, false, 0.0f, false);
    TileMapComp->RebuildCollision();
    
    // 查询地图信息
    int32 Width, Height, NumLayers;
    TileMapComp->GetMapSize(Width, Height, NumLayers);
    
    FPaperTileInfo RetrievedTile = TileMapComp->GetTile(0, 0, 0);
}
```

### 进阶用法——Grouped Sprite 批量渲染

来源：`Classes/PaperGroupedSpriteComponent.h`

```cpp
UPaperGroupedSpriteComponent* GroupedComp = MyActor->FindComponentByClass<UPaperGroupedSpriteComponent>();
if (GroupedComp)
{
    UPaperSprite* TreeSprite = LoadObject<UPaperSprite>(nullptr, TEXT("/Game/Sprites/Tree"));
    UPaperSprite* BushSprite = LoadObject<UPaperSprite>(nullptr, TEXT("/Game/Sprites/Bush"));
    
    // 在不同位置批量添加实例
    for (int32 i = 0; i < 100; ++i)
    {
        FTransform InstanceTransform;
        InstanceTransform.SetLocation(FVector(FMath::RandRange(-500.0f, 500.0f), 
                                              FMath::RandRange(-500.0f, 500.0f), 0.0f));
        InstanceTransform.SetScale3D(FVector(1.0f));
        
        UPaperSprite* SpriteToUse = (i % 2 == 0) ? TreeSprite : BushSprite;
        FLinearColor Color = FLinearColor::MakeRandomColor();
        
        GroupedComp->AddInstance(InstanceTransform, SpriteToUse, false, Color);
    }
    
    // 按 Y 轴排序（2D 游戏中常用的前后遮挡排序）
    GroupedComp->SortInstancesAlongAxis(FVector(0.0f, 1.0f, 0.0f));
    
    // 动态更新实例
    int32 InstanceCount = GroupedComp->GetInstanceCount();
    
    FTransform NewTransform;
    NewTransform.SetLocation(FVector(100.0f, 200.0f, 0.0f));
    GroupedComp->UpdateInstanceTransform(0, NewTransform, false, true, false);
    GroupedComp->UpdateInstanceColor(0, FLinearColor::Red, true);
}
```

### 进阶用法——TileMap 瓦片信息解析

来源：`Classes/PaperTileLayer.h`, `Classes/TileMapBlueprintLibrary.h`

```cpp
// 解析瓦片信息（翻转标志）
FPaperTileInfo TileInfo = TileMapComp->GetTile(5, 3, 0);
if (TileInfo.IsValid())
{
    // 获取基础瓦片索引（不含标志位）
    int32 TileIndex = TileInfo.GetTileIndex();
    
    // 检查翻转状态
    bool bFlipH = TileInfo.HasFlag(EPaperTileFlags::HorizontalFlipTileFlag);
    bool bFlipV = TileInfo.HasFlag(EPaperTileFlags::VerticalFlipTileFlag);
    bool bFlipD = TileInfo.HasFlag(EPaperTileFlags::DiagonalFlipTileFlag);
    
    // 使用 Blueprint Library 解析（等效蓝图 BreakTile）
    int32 BreakIndex;
    UPaperTileSet* BreakTileSet;
    bool BreakFlipH, BreakFlipV, BreakFlipD;
    UTileMapBlueprintLibrary::BreakTile(TileInfo, BreakIndex, BreakTileSet, BreakFlipH, BreakFlipV, BreakFlipD);
    
    // 获取瓦片用户数据
    FName UserData = UTileMapBlueprintLibrary::GetTileUserData(TileInfo);
}
```

## Demo 示例

以下是一个完整的最小示例，展示如何创建一个带有 Flipbook 动画的 2D 角色 Actor。

### MyPaperCharacter.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "PaperCharacter.h"
#include "MyPaperCharacter.generated.h"

class UPaperFlipbook;
class UPaperFlipbookComponent;

UCLASS()
class MYGAME_API AMyPaperCharacter : public APaperCharacter
{
    GENERATED_BODY()

public:
    AMyPaperCharacter();

    // Idle 动画资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    TObjectPtr<UPaperFlipbook> IdleFlipbook;

    // Run 动画资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    TObjectPtr<UPaperFlipbook> RunFlipbook;

    // 切换到待机动画
    UFUNCTION(BlueprintCallable, Category = "Animation")
    void PlayIdle();

    // 切换到跑步动画
    UFUNCTION(BlueprintCallable, Category = "Animation")
    void PlayRun();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    void UpdateAnimation();
};
```

### MyPaperCharacter.cpp

```cpp
#include "MyPaperCharacter.h"
#include "PaperFlipbook.h"
#include "PaperFlipbookComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

AMyPaperCharacter::AMyPaperCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyPaperCharacter::BeginPlay()
{
    Super::BeginPlay();
    PlayIdle();
}

void AMyPaperCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    UpdateAnimation();
}

void AMyPaperCharacter::UpdateAnimation()
{
    UPaperFlipbookComponent* SpriteComp = GetSprite();
    if (!SpriteComp)
    {
        return;
    }

    const FVector Velocity = GetVelocity();
    const bool bIsMoving = Velocity.SizeSquared() > 1.0f;

    if (bIsMoving)
    {
        PlayRun();
        // 根据移动方向翻转 Sprite
        const float Direction = Velocity.X >= 0.0f ? 1.0f : -1.0f;
        SpriteComp->SetRelativeScale3D(FVector(Direction, 1.0f, 1.0f));
    }
    else
    {
        PlayIdle();
    }
}

void AMyPaperCharacter::PlayIdle()
{
    UPaperFlipbookComponent* SpriteComp = GetSprite();
    if (SpriteComp && IdleFlipbook && SpriteComp->GetFlipbook() != IdleFlipbook)
    {
        SpriteComp->SetFlipbook(IdleFlipbook);
        SpriteComp->SetLooping(true);
        SpriteComp->PlayFromStart();
    }
}

void AMyPaperCharacter::PlayRun()
{
    UPaperFlipbookComponent* SpriteComp = GetSprite();
    if (SpriteComp && RunFlipbook && SpriteComp->GetFlipbook() != RunFlipbook)
    {
        SpriteComp->SetFlipbook(RunFlipbook);
        SpriteComp->SetLooping(true);
        SpriteComp->PlayFromStart();
    }
}
```

## 模块依赖

Paper2D 运行时模块自身意外地依赖了编辑器模块 `EditorFramework` 和 `UnrealEd`，这是该插件的一个特殊之处。使用者的模块通常只需依赖 `Paper2D` 即可访问所有核心类。

| 模块 | 用途 |
|---|---|
| `Paper2D` | 核心运行时模块，包含所有 Sprite、Flipbook、TileMap 等核心类 |

你的 `.Build.cs` 中需要添加：

```cpp
PublicDependencyModuleNames.AddRange(new string[] { "Paper2D" });
```

> 注意：`Paper2D` 模块内部依赖了 `EditorFramework` 和 `UnrealEd`，在纯运行时打包场景下通常不会有问题，但如果遇到编译问题需注意此依赖链。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `32652778` | Harden Paper2D tile map and tile layer PostEditChangeProperty paths against null entries and non-til | 加固 TileMap/TileLayer 编辑属性变更路径，防止空指针和非法瓦片 |
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回滚一次有问题的改动 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 工具栏增加全局吸附开关，并在启用时显示红色指示 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |

### 维护评价

**维护等级：维护中，但以稳定性修复为主**

Paper2D 自 2014 年从 Experimental 文件夹移出以来，一直是 UE 内置的 2D 游戏解决方案。经过 12 年的发展，该插件已经相当成熟稳定。

**积极方面**：
- 最近一次更新在 2026 年 5 月，说明 Epic 仍在维护
- 近期更新集中在 Bug 修复、代码加固和工具栏改进，表明项目已进入稳定维护期
- 核心功能（Sprite、Flipbook、TileMap）经过多年的迭代已经非常完善

**需要注意**：
- 📌 **TileSet（瓦片集）和 Sprite Atlas（精灵图集）仍标记为实验性功能**，可能在未来发生变化
- 📌 **Terrain（地形）系统标记为实验性**，功能不完整
- 📌 长期没有重大新功能添加，近期更新均为维护性修复
- 📌 Paper2D 的 2D 物理支持有限（使用 3D 碰撞体），没有真正的 Box2D 集成
- 📌 渲染性能对于大量精灵可能不如专门的 2D 引擎

**推荐使用场景**：如果你的游戏以 3D 为主但包含部分 2D 元素（如 UI、HUD 叠加、2D 迷你游戏），Paper2D 是很好的选择。对于纯 2D 游戏，它功能可用但应评估性能需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Tests)（如有）