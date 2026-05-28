# Landscape Patch

> Support for adding landscape patches- components that can be attached to meshes to affect the landscape as the mesh is repositioned.

| 属性 | 值 |
|---|---|
| 中文名 | 地形补丁 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LandscapePatch` (Runtime), `LandscapePatchEditorOnly` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LandscapePatch) | |

## 用途
Landscape Patch 插件解决了动态地形变形的需求。它允许开发者创建“地形补丁”组件，将这些组件附加到 Actor（尤其是带有网格体的 Actor）上。当这些 Actor 在场景中移动时，附加的补丁会实时地、局部地影响地形的高度图（Heightmap）、权重图（Weightmap）或可见性层（Visibility Layer）。核心功能是通过纹理数据或简单的几何形状（如圆形）来定义变形区域，并应用模糊、衰减等效果，从而实现与场景对象交互的动态地形效果。

## 使用场景
- **建造系统**：当玩家放置建筑或大型物体时，通过补丁自动平整或抬高地基区域的地形。
- **角色移动**：模拟角色在沼泽、雪地等地形上行走时留下的凹陷痕迹。
- **动态交互**：创建陨石坑、爆炸效果等，通过移动或生成带有补丁的 Actor 来实时改变地形。
- **关卡设计**：快速绘制或调整地形中的特定区域（如道路、河流）而不影响整个地形图层。

## 蓝图用法

### 核心节点

#### 地形纹理补丁 (`ULandscapeTexturePatch`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetResolution` | 设置补丁内部纹理/渲染目标的分辨率（像素）。 | `ULandscapeTexturePatch` |
| `GetResolution` | 获取补丁内部纹理的当前分辨率。 | `ULandscapeTexturePatch` |
| `SetUnscaledCoverage` | 设置补丁在世界空间中的覆盖尺寸（不含缩放）。 | `ULandscapeTexturePatch` |
| `SetFalloff` | 设置影响区域边缘的衰减距离（世界单位）。 | `ULandscapeTexturePatch` |
| `SetBlendMode` | 设置补丁与现有地形的混合模式（Alpha混合、加法、最小值、最大值）。 | `ULandscapeTexturePatch` |
| `SetFalloffMode` | 设置衰减形状（圆形或圆角矩形）。 | `ULandscapeTexturePatch` |
| `RequestReinitializeWeights` | 请求重新初始化权重图数据（从当前地形读取）。 | `ULandscapeTexturePatch` |
| `SnapToLandscape` | 将补丁的位置、旋转和尺寸对齐到地形网格。 | `ULandscapeTexturePatch` |
| `AssignToLandscape` | 将补丁分配到指定地形上的特定编辑图层。 | `ULandscapePatchComponent` |
| `SetIsEnabled` | 启用或禁用该补丁对地形的影响。 | `ULandscapePatchComponent` |
| `SetPriority` | 设置补丁的优先级，用于决定同一图层上多个补丁的渲染顺序。 | `ULandscapePatchComponent` |

#### 圆形高度补丁 (`ULandscapeCircleHeightPatch`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Radius` | 设置圆形的半径。 | `ULandscapeCircleHeightPatch` |
| `Falloff` | 设置圆形边缘的线性衰减距离。 | `ULandscapeCircleHeightPatch` |
| `bEditVisibility` | 切换补丁是影响高度图还是可见性层。 | `ULandscapeCircleHeightPatch` |

### 使用示例（蓝图描述）
1.  **创建动态凹陷**：
    -   在角色 Actor 上添加一个 `ULandscapeTexturePatch` 组件。
    -   设置其 `SourceMode` 为 `TextureBackedRenderTarget` 以允许运行时写入。
    -   在角色移动逻辑中，获取该补丁组件的渲染目标 (`GetHeightAlphaRenderTarget`)，然后通过 Render Target 蓝图节点写入黑色（0值）到中心区域，形成凹陷。
    -   调用 `RequestLandscapeUpdate()` 使更改生效。
2.  **放置建筑时平整地基**：
    -   创建一个带有 `ULandscapeCircleHeightPatch` 的 Actor 作为“地基清理器”。
    -   将其 `Radius` 设置为略大于建筑占地面积，`Falloff` 设为较小的平滑过渡值。
    -   使用 `SetBlendMode(Max)` 确保只抬高地形。
    -   当玩家放置建筑时，将此 Actor 实例化在目标位置，并通过 `AssignToLandscape` 绑定到指定的编辑图层。

## C++ 用法

### 头文件引入
```cpp
#include "LandscapePatchComponent.h"
#include "LandscapeTexturePatch.h"
#include "LandscapeCircleHeightPatch.h"
#include "LandscapePatchEditLayer.h"
```

### 基本用法
创建并配置一个简单的纹理补丁组件。
```cpp
// 假设在 Actor 的构造函数或初始化函数中
AEnvironmentEffect::AEnvironmentEffect()
{
    // 创建一个纹理补丁组件
    TexturePatch = CreateDefaultSubobject<ULandscapeTexturePatch>(TEXT("GroundDeformPatch"));
    TexturePatch->SetupAttachment(RootComponent);
    
    // 设置补丁的基本属性
    TexturePatch->SetUnscaledCoverage(FVector2D(1000.0f, 1000.0f)); // 10米 x 10米
    TexturePatch->SetResolution(FVector2D(64.0f, 64.0f)); // 64x64分辨率
    TexturePatch->SetFalloff(200.0f); // 2米的衰减
    TexturePatch->SetBlendMode(ELandscapeTexturePatchBlendMode::Additive); // 使用加法混合，产生位移效果
    TexturePatch->SetFalloffMode(ELandscapeTexturePatchFalloffMode::Circle); // 圆形衰减
}
```
*(示例来源：基于 `ULandscapeTexturePatch` 类定义推断的通用用法)*

### 进阶用法
在运行时修改补丁的纹理数据。
```cpp
// 在某个游戏逻辑中，例如实现“脚印”效果
void ACharacter::CreateFootprint(const FVector& WorldLocation)
{
    if (ULandscapeTexturePatch* FootprintPatch = GetFootprintPatchComponent())
    {
        // 确保补丁处于可写模式
        if (FootprintPatch->GetHeightSourceMode() != ELandscapeTexturePatchSourceMode::TextureBackedRenderTarget)
        {
            FootprintPatch->SetHeightSourceMode(ELandscapeTexturePatchSourceMode::TextureBackedRenderTarget);
        }

        // 获取补丁的渲染目标
        UTextureRenderTarget2D* RT = FootprintPatch->GetHeightAlphaRenderTarget();
        if (RT)
        {
            // 使用蓝图辅助函数或直接通过RHI写入RT数据
            // 这里简化为调用蓝图函数 WriteToRenderTarget
            FDrawToRenderTargetContext Context;
            UKismetRenderingLibrary::BeginDrawCanvasToRenderTarget(this, RT, Context.Canvas, Context.Size, Context);
            // 在Canvas上绘制黑色圆形...
            UKismetRenderingLibrary::EndDrawCanvasToRenderTarget(this, Context);
            
            // 移动补丁到脚印位置并请求更新
            FootprintPatch->SetWorldLocation(WorldLocation);
            FootprintPatch->RequestLandscapeUpdate();
        }
    }
}
```
*(示例来源：基于 `ULandscapeTexturePatch` 中 `TextureBackedRenderTarget` 模式的设计理念)*

## Demo 示例

```cpp
// MyLandscapeEffect.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LandscapeTexturePatch.h"
#include "MyLandscapeEffect.generated.h"

UCLASS()
class AMyLandscapeEffect : public AActor
{
    GENERATED_BODY()
    
public:
    AMyLandscapeEffect();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Landscape")
    ULandscapeTexturePatch* TexturePatchComponent;
};

// MyLandscapeEffect.cpp
#include "MyLandscapeEffect.h"

AMyLandscapeEffect::AMyLandscapeEffect()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并配置补丁组件
    TexturePatchComponent = CreateDefaultSubobject<ULandscapeTexturePatch>(TEXT("LandscapeTexturePatch"));
    SetRootComponent(TexturePatchComponent);

    // 设置基本参数
    TexturePatchComponent->SetUnscaledCoverage(FVector2D(2000.f, 2000.f));
    TexturePatchComponent->SetResolution(FVector2D(32.f, 32.f));
    TexturePatchComponent->SetFalloff(300.f);
    TexturePatchComponent->SetBlendMode(ELandscapeTexturePatchBlendMode::AlphaBlend);
}

void AMyLandscapeEffect::BeginPlay()
{
    Super::BeginPlay();

    // 尝试将补丁分配到场景中的第一个地形
    if (ALandscape* Landscape = GetWorld()->GetSubsystem<ULandscapeSubsystem>()->GetLandscape(0))
    {
        // 假设地形上有一个名为“Patches”的编辑图层
        TexturePatchComponent->AssignToLandscape(Landscape, FName(TEXT("Patches")));
    }
}
```

## 模块依赖
要使用 `LandscapePatch` 插件，你的模块通常需要依赖以下特有模块（除了常见的 Core, Engine 等）：
| 模块 | 用途 |
|---|---|
| `LandscapeCore` | 地形系统的核心运行时模块，提供了地形编辑图层、渲染器接口等基础功能。 |
| `LandscapePatch` | 本插件的运行时模块，包含 `ULandscapePatchComponent` 等核心类。 |
| `RenderCore` | 用于与 RDG (Render Dependency Graph) 交互，提交渲染命令。 |
| `RHI` | 底层图形硬件接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `2037f2f2` | Fixed landscape patch crash when changing BP properties. | 修复了在编辑器中修改蓝图属性时可能导致的地形补丁崩溃问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`，可能涉及日志格式标准化。 |
| 2026-02-26 | `e6de93e0` | Landscape Texture Patch - Added UseWorldPositionSampling flag to allow patches to change texture sam... | 为纹理补丁添加了 `UseWorldPositionSampling` 标志，允许补丁的纹理采样随其世界位置变化。 |
| 2026-02-06 | `bed46c8f` | Landscape Patch - Added GetWeightPatch helper function. | 添加了 `GetWeightPatch` 辅助函数，简化了获取特定权重图补丁数据的代码。 |
| 2026-01-26 | `8987ad88` | Landscape Patch - Added ability for a patch edit layer's heightmap/weightmap alpha values to impact ... | 为补丁编辑图层添加了功能，使其高度图/权重图的 Alpha 值可以影响最终效果。 |

### 维护评价
- **创建时间**：插件于 2025 年 9 月从实验状态迁移并正式发布，非常年轻。
- **最近更新**：在 2026 年初至 4 月期间有持续的功能添加（如新特性、辅助函数）和稳定性修复（崩溃修复），表明开发团队仍在积极维护和增强该插件。
- **活跃维护**：是。近期更新频率高，且包含新功能开发，属于活跃维护状态。
- **已知问题**：无已知长期未解决的问题。旧的 `LandscapePatchManager` 系统已废弃并自动迁移到新的基于优先级和编辑图层的系统。
- **推荐使用**：**强烈推荐**。该插件是 UE5 中实现高级动态地形交互的官方解决方案，正处于积极开发阶段，设计现代且功能强大。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LandscapePatch)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LandscapePatch/Tests)