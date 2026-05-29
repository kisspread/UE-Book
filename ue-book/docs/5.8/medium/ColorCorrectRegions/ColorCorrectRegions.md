# Color Correction Regions (CCR)

> Color correction/shading constrained to regions/volumes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 区域色彩校正 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图标） |
| 模块 | `ColorCorrectRegions` (Runtime), `ColorCorrectRegionsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ColorCorrectRegions) | |

## 用途

ColorCorrectRegions 是一个**后处理级别**的区域化色彩校正系统。它允许用户在场景中放置特定形状的体积（球体、盒体、圆柱体、锥体等），仅对该体积范围内（或范围外，通过反转选项）的像素进行色彩校正。

**解决的核心问题**：全局后处理色彩校正是全屏生效的，无法精确控制空间中的某个区域。CCR 让美术人员能够像在 DaVinci Resolve / Nuke 中对某个区域画遮罩一样，在 3D 空间中直接定义色彩校正的作用范围。

**设计架构**：
- 使用 **WorldSubsystem**（`UColorCorrectRegionsSubsystem`）管理场景中所有活跃的 CCR Actor，因为 AActor 本身无法感知编辑器中的 Add/Remove/Undo/Redo 等事件
- 通过 **SceneViewExtension** 将色彩校正注入渲染管线的后处理阶段
- 支持 **Per-Actor CC**（基于模板 ID 的逐对象色彩校正），可以只影响指定的 Actor
- 集成 **nDisplay** 虚拟制片工作流，支持 ICVFX 面板的位置参数控制

## 使用场景

- 你在做虚拟制片（Virtual Production），需要对 LED Volume 上的特定区域做局部调色 → 用 ColorCorrectionRegion
- 你需要对场景中某个房间的光照和色调做独立调整，而不影响其他区域 → 用 ColorCorrectionRegion
- 你需要让某个后处理窗口只影响它背后的物体（类似遮罩） → 用 ColorCorrectionWindow
- 你需要只对特定几个 Actor 做色彩校正，而不是整个空间区域 → 开启 Per-Actor CC 模式
- 你在多人协作编辑（Multi-User）环境下工作，需要同步 CCR 的逐对象分配 → 自动通过 Concert 同步
- 你在用 nDisplay 做多屏幕虚拟制片，需要通过 ICVFX 面板控制区域位置 → 支持 IDisplayClusterStageActor 接口

## 蓝图用法

`AColorCorrectRegion` 和 `AColorCorrectionWindow` 提供了大量 `BlueprintReadWrite` 属性和 `BlueprintCallable` 函数。由于这些 Actor 类标记为 `NotPlaceable`，需要在编辑器的 Place Actors 面板中手动注册后才能放置，或通过蓝图 Spawn。

### 核心属性

| 属性 | 说明 | 分类 |
|---|---|---|
| `Type` | 区域形状：Sphere / Box / Cylinder / Cone | Region |
| `Priority` | 渲染优先级，数值越高越后渲染（窗口类型 CCR 按距离排序，此属性隐藏） | Region |
| `Intensity` | 色彩校正强度，0-1 | Region |
| `Inner` / `Outer` | 区域的内外范围，值越大影响范围越大 | Region |
| `Falloff` | 边缘衰减/柔化程度 | Region |
| `Invert` | 反转区域，影响区域外的像素 | Region |
| `TemperatureType` | 温度算法：Legacy / WhiteBalance / ColorTemperature | Color Grading |
| `Temperature` | 色温，1500-15000K | Color Grading |
| `Tint` | 色调偏移，-1 到 1 | Color Grading |
| `ColorGradingSettings` | 完整的色彩分级参数（饱和度、对比度、伽马、增益、偏移，含阴影/中间调/高光分区） | Color Grading |
| `Enabled` | 启用/禁用此区域的色彩校正 | Color Grading |

### 核心节点（nDisplay 集成）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLongitude` / `GetLongitude` | 设置/获取经度（球面坐标，ICVFX） | `AColorCorrectRegion` |
| `SetLatitude` / `GetLatitude` | 设置/获取纬度（球面坐标，ICVFX） | `AColorCorrectRegion` |
| `SetDistanceFromCenter` / `GetDistanceFromCenter` | 设置/获取离中心距离 | `AColorCorrectRegion` |
| `SetSpin` / `GetSpin` | 设置/获取自旋 | `AColorCorrectRegion` |
| `SetPitch` / `GetPitch` | 设置/获取俯仰角 | `AColorCorrectRegion` |
| `SetYaw` / `GetYaw` | 设置/获取偏航角 | `AColorCorrectRegion` |
| `SetRadialOffset` / `GetRadialOffset` | 设置/获取径向偏移 | `AColorCorrectRegion` |
| `SetScale` / `GetScale` | 设置/获取 2D 缩放 | `AColorCorrectRegion` |
| `SetOrigin` / `GetOrigin` | 设置/获取 ICVFX 原点变换 | `AColorCorrectRegion` |
| `SetPositionalParams` / `GetPositionalParams` | 设置/获取完整位置参数 | `AColorCorrectRegion` |

### Per-Actor CC（逐对象色彩校正）

| 属性 | 说明 |
|---|---|
| `bEnablePerActorCC` | 启用逐对象色彩校正模式 |
| `PerActorColorCorrection` | 模式选择：`ExcludeStencil`（排除所选 Actor）/ `IncludeStencil`（仅影响所选 Actor） |
| `AffectedActors` | 受影响的 Actor 集合（TSet） |

### 使用示例（蓝图描述）

**放置一个球形色彩校正区域**：
1. Spawn `AColorCorrectionRegion` Actor
2. 设置 `Type` 为 `Sphere`
3. 设置 `Priority` 为 0（最先渲染）
4. 设置 `Intensity` 为 1.0
5. 设置 `Inner` 为 0.3，`Outer` 为 0.8（定义球体的影响范围）
6. 在 `ColorGradingSettings` 中调整饱和度/对比度等参数
7. 放置到需要调色的区域上方

**创建仅影响特定物体的色彩校正窗口**：
1. Spawn `AColorCorrectionWindow` Actor
2. 设置 `WindowType` 为 `Square` 或 `Circle`
3. 开启 `bEnablePerActorCC`
4. 设置 `PerActorColorCorrection` 为 `IncludeStencil`
5. 在 `AffectedActors` 中添加目标 Actor
6. 调整色彩校正参数 → 只有列表中的 Actor 会受到影响

## C++ 用法

### 头文件引入

```cpp
#include "ColorCorrectRegion.h"
#include "ColorCorrectWindow.h"
```

### 基本用法：程序化创建色彩校正区域

```cpp
// 在任意拥有 UWorld 的上下文中创建色彩校正区域
UWorld* World = GetWorld();
FActorSpawnParameters SpawnParams;
SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

// 创建一个球形色彩校正区域
AColorCorrectionRegion* Region = World->SpawnActor<AColorCorrectionRegion>(
    AColorCorrectionRegion::StaticClass(), 
    FTransform(FVector(0, 0, 200)), 
    SpawnParams);

// 配置区域属性
Region->Type = EColorCorrectRegionsType::Sphere;
Region->Priority = 0;
Region->Intensity = 1.0f;
Region->Inner = 0.3f;
Region->Outer = 0.8f;
Region->Falloff = 0.1f;
Region->Invert = false;
Region->Enabled = true;

// 配置色温
Region->TemperatureType = EColorCorrectRegionTemperatureType::WhiteBalance;
Region->Temperature = 6500.0f;  // 日光色温
Region->Tint = 0.0f;

// 配置色彩分级（增加饱和度和对比度）
Region->ColorGradingSettings.Global.ColorSaturation = FVector4f(1.2f, 1.2f, 1.2f, 1.0f);
Region->ColorGradingSettings.Global.ColorContrast = FVector4f(1.1f, 1.1f, 1.1f, 1.0f);
```

### 进阶用法：程序化创建色彩校正窗口

```cpp
// 创建一个圆形色彩校正窗口
AColorCorrectionWindow* Window = World->SpawnActor<AColorCorrectionWindow>(
    AColorCorrectionWindow::StaticClass(), 
    FTransform(FRotator(0, 90, 0), FVector(0, 0, 200)), 
    SpawnParams);

// 窗口类型：影响窗口背后的物体
Window->WindowType = EColorCorrectWindowType::Circle;
Window->Intensity = 1.0f;
Window->Falloff = 0.2f;

// 冷色调处理
Window->TemperatureType = EColorCorrectRegionTemperatureType::ColorTemperature;
Window->Temperature = 8000.0f;
Window->Tint = -0.3f;

// 降低整体亮度和饱和度
Window->ColorGradingSettings.Global.ColorSaturation = FVector4f(0.7f, 0.7f, 0.7f, 1.0f);
Window->ColorGradingSettings.Global.ColorGain = FVector4f(0.9f, 0.9f, 1.0f, 1.0f);
```

### 进阶用法：通过 StencilManager 管理逐对象校正

```cpp
#include "ColorCorrectRegionsStencilManager.h"

// 为指定 Region 的特定 Actor 分配模板 ID
UWorld* World = GetWorld();
AColorCorrectRegion* Region = /* 获取已有的 Region */;

// 启用 Per-Actor CC
Region->bEnablePerActorCC = true;
Region->PerActorColorCorrection = EColorCorrectRegionStencilType::IncludeStencil;

// 添加目标 Actor
TSoftObjectPtr<AActor> TargetActor(ExistingActor);
Region->AffectedActors.Add(TargetActor);

// 通过 StencilManager 手动分配模板 ID（通常由 Subsystem 自动处理）
FColorCorrectRegionsStencilManager::AssignStencilNumberToActorForSelectedRegion(
    World, Region, TargetActor, 
    false,  // bIgnoreUserNotifications
    false   // bSoftAssign
);

// 验证已分配的 Actor 模板 ID 有效性
FColorCorrectRegionsStencilManager::CheckAssignedActorsValidity(Region);
```

## Demo 示例

```cpp
// MyCCRManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCCRManager.generated.h"

class AColorCorrectionRegion;
class AColorCorrectionWindow;

UCLASS(BlueprintType)
class AMyCCRManager : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "CCR")
    bool bCreateOnStart = true;

    /** 创建并配置一个预设的色彩校正区域 */
    UFUNCTION(BlueprintCallable, Category = "CCR")
    AColorCorrectionRegion* CreateWarmRegion(const FTransform& Transform);

    /** 创建并配置一个色彩校正窗口 */
    UFUNCTION(BlueprintCallable, Category = "CCR")
    AColorCorrectionWindow* CreateCoolWindow(const FTransform& Transform);

protected:
    UPROPERTY()
    TArray<AColorCorrectionRegion*> CreatedRegions;

    UPROPERTY()
    TArray<AColorCorrectionWindow*> CreatedWindows;
};
```

```cpp
// MyCCRManager.cpp
#include "MyCCRManager.h"
#include "ColorCorrectRegion.h"
#include "ColorCorrectWindow.h"

void AMyCCRManager::BeginPlay()
{
    Super::BeginPlay();

    if (bCreateOnStart)
    {
        // 在玩家前方 500 单位处创建暖色调区域
        CreateWarmRegion(FTransform(FVector(500, 0, 100)));

        // 在上方创建冷色调窗口
        CreateCoolWindow(FTransform(FRotator(-90, 0, 0), FVector(300, 0, 400)));
    }
}

AColorCorrectionRegion* AMyCCRManager::CreateWarmRegion(const FTransform& Transform)
{
    UWorld* World = GetWorld();
    if (!World) return nullptr;

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    AColorCorrectionRegion* Region = World->SpawnActor<AColorCorrectionRegion>(
        AColorCorrectionRegion::StaticClass(), Transform, Params);
    if (!Region) return nullptr;

    // 球形区域
    Region->Type = EColorCorrectRegionsType::Sphere;
    Region->Priority = 0;
    Region->Intensity = 1.0f;
    Region->Inner = 0.2f;
    Region->Outer = 0.6f;
    Region->Falloff = 0.15f;
    Region->Enabled = true;

    // 暖色调：提高色温，增加橙色增益
    Region->TemperatureType = EColorCorrectRegionTemperatureType::WhiteBalance;
    Region->Temperature = 4000.0f;
    Region->Tint = 0.15f;

    // 提高饱和度，偏向暖色
    Region->ColorGradingSettings.Global.ColorSaturation = FVector4f(1.3f, 1.2f, 1.0f, 1.0f);
    Region->ColorGradingSettings.Global.ColorGain = FVector4f(1.1f, 1.0f, 0.9f, 1.0f);

    CreatedRegions.Add(Region);
    return Region;
}

AColorCorrectionWindow* AMyCCRManager::CreateCoolWindow(const FTransform& Transform)
{
    UWorld* World = GetWorld();
    if (!World) return nullptr;

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    AColorCorrectionWindow* Window = World->SpawnActor<AColorCorrectionWindow>(
        AColorCorrectionWindow::StaticClass(), Transform, Params);
    if (!Window) return nullptr;

    // 矩形窗口
    Window->WindowType = EColorCorrectWindowType::Square;
    Window->Intensity = 0.8f;
    Window->Outer = 0.7f;
    Window->Falloff = 0.2f;

    // 冷色调：降低色温，偏向蓝色
    Window->TemperatureType = EColorCorrectRegionTemperatureType::ColorTemperature;
    Window->Temperature = 9000.0f;
    Window->Tint = -0.2f;

    // 轻微降低饱和度和增益
    Window->ColorGradingSettings.Global.ColorSaturation = FVector4f(0.85f, 0.85f, 0.9f, 1.0f);
    Window->ColorGradingSettings.Global.ColorGain = FVector4f(0.95f, 0.95f, 1.1f, 1.0f);

    CreatedWindows.Add(Window);
    return Window;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `nDisplayModularFeatures` | nDisplay 虚拟制片集成，提供 IDisplayClusterStageActor 接口支持 |
| `ColorGrading` | 提供 FColorGradingSettings 等色彩分级基础类型 |
| `ObjectMixer` | 对象混音器集成（可选） |
| `ConcertSyncClient` | 多人协作同步支持（可选，用于 Per-Actor CC 的跨客户端同步） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `5c7314c3` | Fix Color Correct Regions render rect being truncated when dynamic resolution scales below 1.0. | 修复动态分辨率缩放低于 1.0 时渲染矩形被截断的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-04-06 | `a7ea00e7` | ColorCorrectActors: Promote CustomDepth/SceneDepth from half to float to preserve precision | 将自定义深度/场景深度从半精度提升到单精度以保留精度 |
| 2026-04-01 | `12ae598f` | Color Correction Actors Multi-User: fixed an issue where stencil id's assignment on some actors were | 修复多人协作模式下部分 Actor 的模板 ID 分配问题 |

### 维护评价

- **创建时间**：2020 年 9 月，约 6 年历史
- **最近更新**：最近一次提交为 2026-05-13（约 1 天前），非常活跃
- **更新质量**：近期更新集中在**渲染精度修复**（half→float 提升、动态分辨率修复、浮点截断警告）和**多人协作 bug 修复**，表明该插件正处于稳定打磨阶段
- **活跃度**：✅ **活跃维护**，2026 年 4-5 月有多次实质性更新
- **稳定性**：虽然路径仍位于 `Experimental/` 目录下，但 `.uplugin` 中 `IsBetaVersion=false`、`IsExperimentalVersion=false`，且 `Installed=false`（需要手动启用），功能已相当成熟
- **推荐程度**：✅ **推荐使用**。对于虚拟制片、建筑可视化等需要局部色彩校正的场景，这是 Epic 官方提供的解决方案，维护活跃，架构合理（Subsystem + SceneViewExtension）。注意需要手动启用插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ColorCorrectRegions)
- 官方文档：无（.uplugin 中 DocsURL 为空）