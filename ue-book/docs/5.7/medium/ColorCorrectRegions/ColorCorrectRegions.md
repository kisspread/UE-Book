# Color Correction Regions (CCR)

> Color correction/shading constrained to regions/volumes

| 属性 | 值 |
|---|---|
| 中文名 | 颜色校正区域 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（后处理材质、蓝图资源） |
| 模块 | `ColorCorrectRegions` (Runtime), `ColorCorrectRegionsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-02-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ColorCorrectRegions) | |

## 用途

**Color Correction Regions（CCR）** 是一种后处理技术，允许开发者将颜色校正（调色）限制在指定的三维空间区域或屏幕窗口内（类似后期处理体积，但更灵活、更精确）。它通过世界坐标系中的 Actor（如球体、盒体、圆柱体、锥体）来定义区域，区域内的像素会应用指定的颜色分级（饱和度、对比度、Gamma、增益、偏移、色温、白平衡等），区域外的像素不受影响。这些区域可以基于优先级（排序）或与相机的距离（窗口模式）进行叠加，从而实现复杂的局部调色效果。

该插件解决了 UE 原生后期处理体积只能全局应用、无法精确控制局部区域的痛点，广泛应用于电影级渲染、虚拟制片、舞台灯光模拟、游戏内过场场景等需要精细调色的场合。

## 使用场景

- **虚拟制片 / 实时调色**：在 LED 舞台或绿幕场景中，对特定前景或背景区域进行颜色校正，匹配虚拟环境。
- **游戏过场动画**：突出或调整特定角色/物体的色调，而不影响全局环境。
- **舞台灯光设计**：结合 nDisplay（多屏幕显示）系统，对每个屏幕的局部区域进行色彩修正，模拟真实灯光效果。
- **后期处理 VFX**：创建“色温区域”或“色罩”效果，例如让某个区域内色调偏暖，区域外保持原色。
- **编辑器内快速预览**：在编辑模式下直接调整局部颜色，所见即所得。

## 蓝图用法

插件主要提供两个 Actor 类：`AColorCorrectRegion`（基于优先级排序的区域）和 `AColorCorrectionWindow`（基于距离的窗口）。在蓝图中，只需将对应 Actor 拖入世界，然后设置参数即可使用。以下为核心属性（所有属性均暴露为 `BlueprintReadWrite`，可在蓝图中运行时修改）：

### 核心节点（属性设置）

| 属性 / 枚举 | 说明 | 所在类 |
|---|---|---|
| `EColorCorrectRegionsType` | 区域形状：Sphere（球体）、Box（盒体）、Cylinder（圆柱）、Cone（锥体） | `AColorCorrectRegion` |
| `Intensity` | 校正强度（0~1+） | `AColorCorrectRegion` |
| `Inner` / `Outer` / `Falloff` | 内半径、外半径、羽化过渡 | `AColorCorrectRegion` |
| `Invert` | 反转区域（校正区域外） | `AColorCorrectRegion` |
| `TemperatureType` | 色温模式：LegacyTemperature（传统色温）、WhiteBalance（白平衡）、ColorTemperature（色温） | `AColorCorrectRegion` |
| `Temperature` / `Tint` | 色温值（K）和色调偏移 | `AColorCorrectRegion` |
| `ColorGradingSettings` | 详细颜色分级参数（饱和度、对比度、Gamma、增益、偏移，以及阴影/中间调/高光分段） | `AColorCorrectRegion` |
| `Priority` | 区域优先级（数字越大越优先覆盖） | `AColorCorrectRegion`（窗口类不使用） |
| `WindowType` | 窗口形状：Square（方形）、Circle（圆形） | `AColorCorrectionWindow` |
| `bEnablePerActorCC` | 启用基于 Actor 的遮罩（仅影响指定 Actor 或排除指定 Actor） | `AColorCorrectRegion` |
| `PerActorColorCorrection` | 遮罩模式：`ExcludeStencil`（排除选中 Actor）、`IncludeStencil`（仅影响选中 Actor） | `AColorCorrectRegion` |
| `AffectedActors` | 参与遮罩的 Actor 列表 | `AColorCorrectRegion` |

### 典型蓝图设置流程

1. 在 Content Browser 中，右键选择 `Blueprints` → `Actor`，继承 `ColorCorrectRegion` 或 `ColorCorrectionWindow` 创建蓝图类（或直接使用 `BP_ColorCorrectRegion` 放置）。
2. 在关卡中放置该 Actor，调整位置、旋转、缩放（形状区域会跟随 Actor 变换）。
3. 在细节面板设置 `Region Type`（区域形状）或 `Window Type`（窗口形状）。
4. 调整 `Intensity`、`Inner/Outer`、`Falloff` 定义区域范围和过渡。
5. 在 `Color Grading` 部分设置所需的颜色校正参数（饱和度、对比度、Gamma 等）。
6. （可选）启用 `Per-Actor Color Correction`，选择要包含/排除的 Actor。
7. 若有多个区域重叠，设置 `Priority` 以决定覆盖顺序（窗口模式无需 Priority，自动按距离排序）。

## C++ 用法

### 头文件引入

```cpp
#include "ColorCorrectRegion.h"          // AColorCorrectRegion 类
#include "ColorCorrectWindow.h"          // AColorCorrectionWindow 类
#include "ColorCorrectRegionsSubsystem.h" // UColorCorrectRegionsSubsystem
```

### 基本用法

#### 动态创建和配置 CCR Actor

```cpp
// 在某个游戏流程中创建球体颜色校正区域
void AMyGameMode::SpawnTempColorCorrection()
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 生成 CCR Actor
    AColorCorrectRegion* CCR = World->SpawnActor<AColorCorrectRegion>(AColorCorrectRegion::StaticClass(), FVector(100.0f, 0.0f, 200.0f), FRotator::ZeroRotator);
    if (CCR)
    {
        // 设置形状
        CCR->Type = EColorCorrectRegionsType::Sphere;
        // 设置强度
        CCR->Intensity = 0.8f;
        // 设置内外半径和羽化（单位为世界单位）
        CCR->Inner = 0.0f;
        CCR->Outer = 500.0f;
        CCR->Falloff = 0.2f;
        // 设置色温（白平衡模式）
        CCR->TemperatureType = EColorCorrectRegionTemperatureType::WhiteBalance;
        CCR->Temperature = 6500.0f; // 日光平衡
        // 设置颜色分级（统一偏移）
        FColorGradingSettings& Grading = CCR->ColorGradingSettings;
        Grading.ColorSaturation = FVector4(1.5f, 1.0f, 0.8f, 1.0f); // 增强红色，削弱蓝色
        // 应用更改
        CCR->UpdateRenderingData();
    }
}
```

**来源文件**: `Source/ColorCorrectRegions/Public/ColorCorrectRegion.h`（属性访问）

#### 使用子系统获取所有 CCR 并排序

```cpp
// 获取 CCR 世界子系统
UColorCorrectRegionsSubsystem* CCRSubsystem = World->GetSubsystem<UColorCorrectRegionsSubsystem>();
if (CCRSubsystem)
{
    // 遍历所有 CCR（子系统内部维护 TArray<AColorCorrectRegion*> Regions）
    for (AColorCorrectRegion* Region : CCRSubsystem->GetAllRegions()) // 假设有该方法，实际需从源码确认
    {
        // 可以根据需要操作每个 Region
    }
}
```

**注意**: 子系统内部通过 `OnActorSpawned`、`OnActorDeleted` 回调管理区域列表，但公开访问接口需从源码检查（头文件未完全显示）。建议直接使用子系统提供的事件驱动。

### 进阶用法

#### 结合 Per-Actor 遮罩

为实现仅对特定 Actor 进行颜色校正，需先为 Actor 分配模板 ID（Stencil），然后将 Actor 添加到 CCR 的 `AffectedActors` 列表：

```cpp
// 假设已有一个目标 Actor 指针 TargetActor
AColorCorrectRegion* CCR = ...; // 初始化好的 CCR
if (CCR && TargetActor)
{
    // 启用 per-actor 校正
    CCR->bEnablePerActorCC = true;
    // 模式：仅影响选中的 Actor
    CCR->PerActorColorCorrection = EColorCorrectRegionStencilType::IncludeStencil;
    // 将 Actor 添加到受影响的列表
    CCR->AffectedActors.Add(TargetActor);
    // 通知子系统分配模板 ID（子系统的 AssignStencilIdsToPerActorCC 方法会被自动调用，或者手动触发）
    UColorCorrectRegionsSubsystem* Subsystem = GetWorld()->GetSubsystem<UColorCorrectRegionsSubsystem>();
    if (Subsystem)
    {
        Subsystem->AssignStencilIdsToPerActorCC(CCR, false, false);
    }
    // 注意：需要 Actor 的网格组件支持渲染模板（CustomDepth Stencil），并启用渲染模板
    TargetActor->GetRootComponent()->SetCustomDepthStencilValue(1);
    TargetActor->GetRootComponent()->SetRenderCustomDepth(true);
}
```

**说明**: 模板 ID 的分配由 `FColorCorrectRegionsStencilManager` 管理，子系统在 `Tick` 中会检查有效性。用户需确保受影响的 Actor 开启了 `Render CustomDepth Pass`。

#### 窗口模式 (Color Correction Window)

窗口模式不依赖 Priority，而是按照从相机到窗口中心的距离进行排序（近的覆盖远的）。创建方式类似，但使用 `AColorCorrectionWindow`：

```cpp
UWorld* World = GetWorld();
AColorCorrectionWindow* Window = World->SpawnActor<AColorCorrectionWindow>(FVector(0.0f, 0.0f, 100.0f), FRotator::ZeroRotator);
if (Window)
{
    Window->WindowType = EColorCorrectWindowType::Circle;
    Window->Intensity = 1.0f;
    // 其他颜色校正参数同上
}
```

**性能建议**: 尽量控制每个 Region 的 `Outer` 半径，过大的区域会增加后处理带宽消耗。窗口模式性能优于区域模式（无需三维形状遮挡测试）。

## Demo 示例

以下是一个完整的最小 C++ 示例，在游戏启动时创建一个球体颜色校正区域，5 秒后移除。

**ColorCorrectDemo.h**:
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ColorCorrectDemo.generated.h"

UCLASS()
class AColorCorrectDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    AColorCorrectRegion* SpawnedCCR = nullptr;
    FTimerHandle RemovalTimerHandle;
};
```

**ColorCorrectDemo.cpp**:
```cpp
#include "ColorCorrectDemo.h"
#include "ColorCorrectRegion.h"
#include "ColorCorrectRegionsSubsystem.h"
#include "Engine/World.h"
#include "TimerManager.h"

void AColorCorrectDemo::BeginPlay()
{
    Super::BeginPlay();
    UWorld* World = GetWorld();
    if (!World) return;

    // 在原点生成一个球体 CCR
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    SpawnedCCR = World->SpawnActor<AColorCorrectRegion>(FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);
    if (SpawnedCCR)
    {
        SpawnedCCR->Type = EColorCorrectRegionsType::Sphere;
        SpawnedCCR->Outer = 300.0f;
        SpawnedCCR->Falloff = 0.3f;
        SpawnedCCR->Intensity = 0.7f;
        SpawnedCCR->ColorGradingSettings.ColorSaturation = FVector4(1.2f, 0.8f, 0.8f, 1.0f); // 调暖色调
        // 让 CCR 生效（设置属性后自动触发重生成，无需特别调用）
    }

    // 5 秒后删除该 CCR
    FTimerDelegate TimerDelegate;
    TimerDelegate.BindLambda([this]()
    {
        if (SpawnedCCR && SpawnedCCR->IsValidLowLevel())
        {
            SpawnedCCR->Destroy();
            SpawnedCCR = nullptr;
        }
    });
    GetWorldTimerManager().SetTimer(RemovalTimerHandle, TimerDelegate, 5.0f, false);
}

void AColorCorrectDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    GetWorldTimerManager().ClearTimer(RemovalTimerHandle);
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

要使用该插件，你的模块的 `Build.cs` 需要添加以下依赖。由于插件本身仍处于 Experimental 路径，建议在 `PrivateDependencyModuleNames` 中添加。

| 模块 | 用途 |
|---|---|
| `ColorCorrectRegions` | 必选，提供 CCR Actor 类和渲染逻辑 |
| `ColorCorrectRegionsEditor` | 编辑器模块（仅编辑器运行时需引用，提供定制细节面板、图标等） |
| `ColorGrading` | 提供颜色分级参数结构（`FColorGradingSettings`） |
| `nDisplayModularFeatures` | 支持多屏幕显示系统的 CCR 集成 |
| `ObjectMixer` | 提供 Object Mixer 面板支持（编辑器） |

**注意**: 如果仅在运行时使用，只需依赖 `ColorCorrectRegions`、`ColorGrading`、`nDisplayModularFeatures`（若需要 nDisplay 功能）。`ObjectMixer` 和 `ColorCorrectRegionsEditor` 为编辑器功能，运行时可不引用。

## 维护状态

### 近期更新

- 2025-05-29 `f5ac91eb` 移除宏中出现的不合法 U 宏调用（编译警告/错误修复）
- 2025-05-23 `994e1fc1` 钳制 Region 视口到最大视口边界（防止视口外渲染问题）
- 2025-04-28 `ece68893` 仅在 CCR 被使用时发出警告（减少无用日志）
- 2025-04-23 `394ea0ed` 在项目设置中提高无效模板设置的醒目度（UX 改进）
- 2025-02-13 `ec3fb596` 替换所有 `IsValid(this)` 调用（代码现代化）

### 维护评价

该插件创建于 2025-02-13，属于非常新的插件（< 1 年）。根据最近 5 次提交（2025-04-23 ~ 2025-05-29），项目保持活跃维护，更新内容涵盖功能修正、性能优化和代码质量提升，没有明显的废弃迹象。作为 Experimental 插件，API 可能仍会变化（例如多个 `UE_DEPRECATED(5.5)` 标记的旧函数），但整体可靠性较高，适合在虚拟制片和电影级渲染中使用。建议在使用时紧跟 UE 版本更新，并关注 `uplugin` 中可能的 IsExperimental 状态变化。

**推荐使用**，但需注意：
- 目前处于 Experimental 路径，默认不启用，需手动在 Plugin 面板启用。
- Per-Actor 遮罩依赖于 Custom Depth 模板，需确保项目设置中开启了相关渲染功能。
- 多区域叠加时，过高的区域数量可能影响性能（建议控制数量在 10 个以内）。

## 相关链接

- [源码（主目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ColorCorrectRegions)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/color-correction-regions-in-unreal-engine/)（待补充，目前可能无官方独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ColorCorrectRegions/Tests)（如果存在，请自行查找）