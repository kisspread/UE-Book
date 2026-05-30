# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（投影校准、媒体资产、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterConfigurator` (Runtime), `SharedMemoryMedia` (Runtime), 等共 30 个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

> **注意**：这是一个超大型插件（xlarge，1351 源文件，30 个模块），本文档聚焦于核心子模块 **DisplayClusterProjection** 的详细分析，其余子模块需单独文档覆盖。

---

## 用途

nDisplay 是 UE5 的多机集群同步渲染系统，用于在多台 PC 上驱动多屏幕、投影仪和 LED 墙等显示设备，实现同步的单目或立体渲染。

**DisplayClusterProjection** 模块是 nDisplay 的投影策略核心，负责：

1. **投影策略管理**：提供统一的投影策略接口（`IDisplayClusterProjectionPolicy`），支持多种第三方投影校准/变形/融合方案的无缝集成
2. **视锥体计算**：根据不同的投影策略（相机、手动矩阵、校准文件等）为每个视口计算正确的视图位置、旋转和投影矩阵
3. **Warp & Blend**：在渲染线程中执行图像变形（Warp）和融合（Blend），将渲染输出校正为投影仪/显示器的几何形状
4. **多 RHI 支持**：针对 DX11/DX12 等不同图形 API 提供适配器，确保第三方 SDK 正确初始化和渲染

简而言之，这个模块解决了"如何在非平面、非规则形状的显示设备上正确投影 Unreal 画面"的核心问题。

## 使用场景

- **CAVE 系统 / 穹顶投影**：多面投影系统需要复杂的几何校正 → 用 MPCDI / EasyBlend / VIOSO / Domeprojection 策略
- **LED Volume 拍摄 (ICVFX)**：虚拟制片中的 LED 墙需要精确的投影映射 → 用 MPCDI / Mesh 策略
- **多屏拼接显示**：多台投影仪拼接一个大画面 → 用 MPCDI 配置 warp mesh 和 blend 区域
- **固定 FOV 显示**：直接用相机或手动设置视锥体 → 用 Camera / Manual 策略
- **视口复用**：多个视口共享同一投影参数 → 用 Link / Reference 策略

### 支持的投影策略类型

| 策略类型 | 说明 | 适用场景 |
|---|---|---|
| `camera` | 基于场景中的相机组件 | 简单的固定视角显示 |
| `manual` | 手动指定投影矩阵或视锥角度 | 完全自定义的投影需求 |
| `mpcdi` | 从 MPCDI 文件加载变形/融合数据 | 行业标准校准文件（投影仪拼接） |
| `mesh` | 基于场景中的网格几何体 | LED Volume / 任意形状屏幕 |
| `link` | 继承父视口的投影参数 | 视口间的投影参数复用 |
| `reference` | 引用另一个视口的完整投影 | 多视口共享同一投影源 |
| `easyblend` | Scalable Display 的 EasyBlend 校准 | 专业投影仪校准系统 |
| `vioso` | VIOSO Warping & Blending | 穹顶/曲面投影系统 |
| `domeprojection` | domeprojection.com 校准系统 | 专业穹顶投影 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CameraPolicySetCamera` | 为指定视口设置相机投影策略的相机组件 | `UDisplayClusterProjectionBlueprintLib` |

### 使用示例

**设置相机投影策略的目标相机：**

1. 获取对 nDisplay 配置的引用（通常在 BeginPlay 时）
2. 调用 `CameraPolicySetCamera`，传入视口 ID（如 `"ICVFX_Stage"`）、相机组件引用和 FOV 乘数

蓝图连接示意：
```
[Event BeginPlay] → [CameraPolicySetCamera]
                        ├─ ViewportId: "viewport_0"
                        ├─ NewCamera: [CameraComponent 引用]
                        └─ FOVMultiplier: 1.0
```

> **注意**：旧版 `IDisplayClusterProjectionBlueprintAPI::CameraPolicySetCamera` 已在 5.4 中废弃，功能已移至 `UDisplayClusterProjectionBlueprintLib`，在蓝图函数列表的 "nDisplay" 分类下可直接找到。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterProjectionModule.h"
#include "IDisplayClusterProjection.h"
#include "IDisplayClusterProjectionPolicy.h"
```

### 基本用法

**获取投影模块接口并查询支持的投影类型：**

```cpp
// 来源: Public/IDisplayClusterProjection.h
// 获取投影模块单例
if (IDisplayClusterProjection::IsAvailable())
{
    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();
    
    // 查询所有支持的投影策略类型
    TArray<FString> SupportedTypes;
    ProjectionModule.GetSupportedProjectionTypes(SupportedTypes);
    // SupportedTypes 包含: "camera", "manual", "mpcdi", "mesh", "link", 
    //                      "reference", "easyblend", "vioso", "domeprojection"
}
```

**通过工厂创建投影策略实例：**

```cpp
// 来源: Private/DisplayClusterProjectionModule.h
IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();

// 获取 MPCDI 投影策略的工厂
TSharedPtr<IDisplayClusterProjectionPolicyFactory> Factory = 
    ProjectionModule.GetProjectionFactory(TEXT("mpcdi"));

if (Factory.IsValid())
{
    // 工厂根据配置创建策略实例
    // (实际调用在 nDisplay 内部的视口管理流程中自动完成)
}
```

**运行时切换相机投影的目标相机：**

```cpp
// 来源: Public/DisplayClusterProjectionBlueprintLib.h
// 通过蓝图库函数（也可在 C++ 中直接调用）
UDisplayClusterProjectionBlueprintLib::CameraPolicySetCamera(
    TEXT("viewport_0"),    // 视口 ID
    MyCameraComponent,     // UCameraComponent*
    1.5f                   // FOV 乘数
);
```

### 进阶用法

**投影策略的生命周期管理（nDisplay 内部流程）：**

```cpp
// 来源: Private/Policy/DisplayClusterProjectionPolicyBase.h
// 投影策略通过以下生命周期回调工作：

// 1. 场景启动时初始化
bool HandleStartScene(IDisplayClusterViewport* InViewport);

// 2. 每帧计算视图（GameThread）
bool CalculateView(
    IDisplayClusterViewport* InViewport,
    const uint32 InContextNum,
    FVector& InOutViewLocation,
    FRotator& InOutViewRotation,
    const FVector& ViewOffset,
    const float WorldToMeters,
    const float NCP,
    const float FCP
);

// 3. 获取投影矩阵
bool GetProjectionMatrix(
    IDisplayClusterViewport* InViewport,
    const uint32 InContextNum,
    FMatrix& OutPrjMatrix
);

// 4. 渲染线程应用 Warp & Blend
void ApplyWarpBlend_RenderThread(
    FRHICommandListImmediate& RHICmdList,
    const IDisplayClusterViewportProxy* InViewportProxy
);

// 5. 场景结束时清理
void HandleEndScene(IDisplayClusterViewport* InViewport);
```

**MPCDI 配置参数常量（用于 .cfg 配置文件）：**

```cpp
// 来源: Public/DisplayClusterProjectionStrings.h
// 使用预定义的字符串常量配置投影策略参数

// MPCDI 配置示例
TMap<FString, FString> Parameters;
Parameters.Add(DisplayClusterProjectionStrings::cfg::mpcdi::File, TEXT("calibration.mpcdi"));
Parameters.Add(DisplayClusterProjectionStrings::cfg::mpcdi::Buffer, TEXT("default"));
Parameters.Add(DisplayClusterProjectionStrings::cfg::mpcdi::Region, TEXT("region_0"));
Parameters.Add(DisplayClusterProjectionStrings::cfg::mpcdi::Origin, TEXT("camera_origin"));
Parameters.Add(DisplayClusterProjectionStrings::cfg::mpcdi::WorldScale, TEXT("1000"));

// Manual 配置示例
Parameters.Add(DisplayClusterProjectionStrings::cfg::manual::Rendering, 
               DisplayClusterProjectionStrings::cfg::manual::RenderingType::Stereo);
Parameters.Add(DisplayClusterProjectionStrings::cfg::manual::Type, 
               DisplayClusterProjectionStrings::cfg::manual::FrustumType::Angles);
Parameters.Add(DisplayClusterProjectionStrings::cfg::manual::AngleL, TEXT("-45"));
Parameters.Add(DisplayClusterProjectionStrings::cfg::manual::AngleR, TEXT("45"));
Parameters.Add(DisplayClusterProjectionStrings::cfg::manual::AngleT, TEXT("30"));
Parameters.Add(DisplayClusterProjectionStrings::cfg::manual::AngleB, TEXT("-30"));
```

## Demo 示例

以下演示如何在运行时通过代码管理 nDisplay 相机投影策略。

### MyNDisplayManager.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNDisplayManager.generated.h"

class UCameraComponent;

UCLASS()
class AMyNDisplayManager : public AActor
{
    GENERATED_BODY()

public:
    AMyNDisplayManager();

protected:
    virtual void BeginPlay() override;

    /** 在运行时切换 nDisplay 视口的投影相机 */
    UFUNCTION(BlueprintCallable)
    void SwitchProjectionCamera(const FString& ViewportId, UCameraComponent* NewCamera);

protected:
    UPROPERTY(EditAnywhere, Category = "nDisplay")
    FString TargetViewportId = TEXT("viewport_0");

    UPROPERTY(EditAnywhere, Category = "nDisplay")
    TObjectPtr<UCameraComponent> DefaultCamera;

    UPROPERTY(EditAnywhere, Category = "nDisplay", meta = (ClampMin = "0.1", ClampMax = "5.0"))
    float FOVMultiplier = 1.0f;
};
```

### MyNDisplayManager.cpp

```cpp
#include "MyNDisplayManager.h"
#include "Camera/CameraComponent.h"
#include "DisplayClusterProjectionBlueprintLib.h"

AMyNDisplayManager::AMyNDisplayManager()
{
    PrimaryActorTick.bCanEverTick = false;

    DefaultCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("DefaultCamera"));
    RootComponent = DefaultCamera;
}

void AMyNDisplayManager::BeginPlay()
{
    Super::BeginPlay();

    // 在场景开始时设置默认投影相机
    if (DefaultCamera)
    {
        SwitchProjectionCamera(TargetViewportId, DefaultCamera);
    }
}

void AMyNDisplayManager::SwitchProjectionCamera(const FString& ViewportId, UCameraComponent* NewCamera)
{
    if (!NewCamera)
    {
        UE_LOG(LogTemp, Warning, TEXT("SwitchProjectionCamera: NewCamera is null"));
        return;
    }

    // 通过蓝图库设置投影相机
    UDisplayClusterProjectionBlueprintLib::CameraPolicySetCamera(
        ViewportId,
        NewCamera,
        FOVMultiplier
    );

    UE_LOG(LogTemp, Log, TEXT("nDisplay projection camera set for viewport '%s'"), *ViewportId);
}
```

## 模块依赖

DisplayClusterProjection 模块依赖说明：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器集成（预览网格、编辑器工具） |
| `DisplayClusterWarp` | Warp & Blend 核心接口（`IDisplayClusterWarpBlend`、`IDisplayClusterWarpPolicy`） |
| `DisplayClusterShaders` | 投影校正相关的 GPU 着色器 |
| `ScalableMPCDI` | 第三方 MPCDI 文件解析库（外部依赖） |

> 该模块同时依赖标准 Core/Engine/Slate 等基础模块。多个第三方 SDK（EasyBlend、VIOSO、Domeprojection）通过动态加载 DLL 集成，运行时按需加载，不影响无 SDK 环境的编译。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 集成中新增 EXR 多图层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中将 WarpBlendAlpha 模式合并入 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名及 MPCDI/ICVFX 着色器的不透明 alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时正确处理非默认的 DisplayGamma 值 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

- **活跃维护** ✅：最近 5 次 commit 集中在 2026 年 5 月，更新非常频繁
- **持续功能开发**：持续添加 MovieGraph/EXR 多图层等新特性，不仅仅是 bug 修复
- **长期项目**：自 2018 年创建以来（约 8 年），一直是 Epic 的企业级功能重点，服务于虚拟制片和专业 AV 行业
- **平台支持**：Win64 和 Linux 双平台
- **推荐使用**：如果项目涉及多屏投影、LED Volume 虚拟制片或 CAVE 系统，nDisplay 是官方推荐且唯一支持的方案。由于默认未启用（`EnabledByDefault=false`），需在项目设置中手动启用插件

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [源码（DisplayClusterProjection 模块）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterProjection)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/MediaComposure/nDisplay/index.html)（无 .uplugin 内置链接，此为 UE 文档站点地址）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)