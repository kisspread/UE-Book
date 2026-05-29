# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多机集群同步渲染**的核心系统，解决以下问题：

- **多台 PC 驱动多块大屏**：将单个场景渲染拆分到多台计算机上，每台计算机负责一个或多个视口（viewport），实现超大分辨率、超大视场角的沉浸式显示。
- **立体渲染（Stereo）**：支持单眼（Mono）和双眼立体渲染模式，用于 VR CAVE 系统或立体投影。
- **投影校正与融合（Warp & Blend）**：集成多种专业投影校正方案（MPCDI、EasyBlend、VIOSO、Domeprojection），将渲染结果经过几何变形、边缘融合、色彩校正后输出到物理投影屏幕。
- **虚拟制片（Virtual Production / ICVFX）**：为 LED 墙虚拟制片提供完整的渲染管线支持，包括摄影机内视效（In-Camera VFX）、色彩分级、Light Card 等功能。
- **集群同步**：确保所有机器上的渲染帧、时间线、游戏逻辑严格同步，所有节点在同一帧显示同一时刻的画面。

**为什么存在**：单台 PC 的 GPU 算力和显示输出有限，无法驱动专业级的大型显示装置（如天文馆穹顶、LED 虚拟墙、飞行模拟器）。nDisplay 通过多机协作+精确同步解决了这个规模问题。

## 使用场景

- 你在做**虚拟制片 LED 墙** → 用 nDisplay 配置 ICVFX 虚拟摄影棚，多台渲染节点驱动 LED 屏幕
- 你需要**多屏投影融合** → 用 nDisplay 的 MPCDI/EasyBlend/VIOSO 投影策略进行几何校正和边缘融合
- 你在搭建 **CAVE 沉浸式系统** → 用 nDisplay 配置多面墙立体渲染
- 你需要做**天文馆穹顶投影** → 用 nDisplay + Domeprojection/Vioso 进行球面投影校正
- 你有多台 PC 需要**同步渲染同一场景** → 用 nDisplay 的集群同步机制
- 你需要录制包含 nDisplay 画面的**影视序列** → 用 DisplayClusterMoviePipeline 模块

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CameraPolicySetCamera` | 为指定视口设置摄影机投影策略使用的摄像机组件，并可设置 FOV 倍率 | `UDisplayClusterBlueprintLib` |

### 使用示例（蓝图描述）

**设置摄影机投影策略的摄像机**：

1. 创建一个 **Set Camera** 节点（在 `NDisplay > Projection` 分类下）
2. 将 **Viewport ID** 连接到目标视口的字符串（如 `"viewport_1"`）
3. 将 **New Camera** 连接到场景中的 `UCameraComponent` 引用
4. 可选设置 **FOV Multiplier**（默认 1.0）

> **注意**：此 API 在 UE 5.4 中已从 `IDisplayClusterProjectionBlueprintAPI` 迁移到 `UDisplayClusterBlueprintLib`。旧的 `GetAPI` 函数已废弃。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterProjection.h"
#include "IDisplayClusterProjectionBlueprintAPI.h"
```

### 基本用法

**查询支持的投影类型并获取工厂**：

```cpp
// 来源: Private/DisplayClusterProjectionModule.h
if (IDisplayClusterProjection::IsAvailable())
{
    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();

    // 获取所有支持的投影类型
    TArray<FString> SupportedTypes;
    ProjectionModule.GetSupportedProjectionTypes(SupportedTypes);
    // SupportedTypes 包含: "camera", "manual", "mpcdi", "easyblend", "vioso",
    //                       "domeprojection", "mesh", "reference", "link"

    // 获取特定类型的投影工厂
    TSharedPtr<IDisplayClusterProjectionPolicyFactory> Factory = 
        ProjectionModule.GetProjectionFactory(TEXT("mpcdi"));
}
```

### 进阶用法

**通过蓝图库设置摄影机策略**（推荐的 C++ 调用方式）：

```cpp
// 来源: Public/Blueprints/DisplayClusterProjectionBlueprintLib.h
#include "DisplayClusterProjectionBlueprintLib.h"

// 设置视口的摄影机策略
FString ViewportId = TEXT("ICVFX_Camera");
UCameraComponent* Camera = MyActor->FindComponentByClass<UCameraComponent>();
float FOVMultiplier = 1.2f;

UDisplayClusterBlueprintLib::CameraPolicySetCamera(ViewportId, Camera, FOVMultiplier);
```

## Demo 示例

由于 nDisplay 的使用高度依赖集群配置（.ndisplay 配置文件、多机网络），无法提供单一文件的最小示例。以下展示如何在 C++ 中以编程方式查询和操作投影模块：

```cpp
// MyDisplayClusterHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyDisplayClusterHelper
{
public:
    /** 列出所有支持的投影策略类型 */
    static void ListSupportedProjectionTypes();

    /** 检查特定投影类型是否可用 */
    static bool IsProjectionTypeSupported(const FString& ProjectionType);

    /** 设置视口的摄影机投影 */
    static void SetViewportCamera(const FString& ViewportId, 
                                   UCameraComponent* Camera, 
                                   float FOVMultiplier = 1.f);
};
```

```cpp
// MyDisplayClusterHelper.cpp
#include "MyDisplayClusterHelper.h"
#include "IDisplayClusterProjection.h"
#include "DisplayClusterBlueprintLib.h"

void FMyDisplayClusterHelper::ListSupportedProjectionTypes()
{
    if (!IDisplayClusterProjection::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DisplayClusterProjection module is not loaded."));
        return;
    }

    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();

    TArray<FString> SupportedTypes;
    ProjectionModule.GetSupportedProjectionTypes(SupportedTypes);

    UE_LOG(LogTemp, Log, TEXT("Supported projection types:"));
    for (const FString& Type : SupportedTypes)
    {
        UE_LOG(LogTemp, Log, TEXT("  - %s"), *Type);
    }
}

bool FMyDisplayClusterHelper::IsProjectionTypeSupported(const FString& ProjectionType)
{
    if (!IDisplayClusterProjection::IsAvailable())
    {
        return false;
    }

    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();
    TSharedPtr<IDisplayClusterProjectionPolicyFactory> Factory = 
        ProjectionModule.GetProjectionFactory(ProjectionType);

    return Factory.IsValid();
}

void FMyDisplayClusterHelper::SetViewportCamera(const FString& ViewportId, 
                                                  UCameraComponent* Camera, 
                                                  float FOVMultiplier)
{
    UDisplayClusterBlueprintLib::CameraPolicySetCamera(ViewportId, Camera, FOVMultiplier);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayClusterWarp` | Warp & Blend 核心接口和实现，用于投影几何变形和边缘融合 |
| `DisplayClusterConfiguration` | nDisplay 配置数据模型，解析 .ndisplay 配置文件 |
| `D3D12RHI` | DirectX 12 渲染硬件接口，用于 EasyBlend/SharedMemoryMedia 等需要 D3D12 的模块 |
| `SharedMemoryMedia` | 共享内存媒体传输，用于节点间高效图像数据传输 |
| `ScalableMPCDI` | 第三方 MPCDI 库（External 模块），用于加载 MPCDI 校准文件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 管线新增 EXR 多图层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并电影管线中的 WarpBlendAlpha 模式到统一的 WarpBlend 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄影机命名问题，修复 MPCDI/ICVFX 着色器中的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码回退时未遵守非默认 DisplayGamma 的问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

nDisplay 是 Epic Games 持续活跃维护的核心虚拟制片/集群渲染解决方案。

- **创建时间**：2018 年 6 月（UE 4.20 时期），已有约 8 年历史
- **维护状态**：**活跃维护中** — 最近的提交集中在 2026 年 5 月，且均为功能性更新和 bug 修复，包含 Movie Pipeline 集成、ICVFX 着色器修复、EXR 多层支持等实质性改动
- **代码规模**：1351 个源文件，28 个模块，是 UE5 中最大的插件之一
- **依赖的第三方 SDK**：EasyBlend、VIOSO、Domeprojection、MPCDI（均为专业投影校正方案）
- **推荐使用**：✅ **强烈推荐**用于虚拟制片、LED 墙渲染、多屏投影等专业场景。需要留意的是，此插件**默认未启用**（`EnabledByDefault: false`），需在项目设置中手动启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/ndisplay-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)

---

# DisplayClusterProjection 子模块文档

> nDisplay 的投影策略系统，管理所有视口的投影矩阵计算、视图变换和外部校正设备集成

| 属性 | 值 |
|---|---|
| 中文名 | 投影策略模块 |
| 分类 | 投影策略（DisplayClusterProjection） |
| 模块 | `DisplayClusterProjection` (Runtime) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterProjection) | |

## 用途

DisplayClusterProjection 是 nDisplay 的**投影策略引擎**，负责将虚拟摄像机的视图转换为每个物理屏幕/投影仪所需的投影矩阵和几何变形数据。

核心职责：
- **投影矩阵计算**：为每个视口上下文（Context）计算精确的投影矩阵，支持非对称视锥体
- **视图变换**：根据每块屏幕在物理空间中的位置和朝向，计算正确的视图位置和旋转
- **Warp & Blend 应用**：在渲染线程中将几何变形（Warp）和边缘融合（Blend）应用到渲染结果
- **多策略支持**：通过工厂模式支持 9 种不同的投影策略，用户按需选择

## 投影策略类型

该模块支持以下 9 种投影策略（来自 `DisplayClusterProjectionStrings.h`）：

| 策略名称 | 用途 | 特点 |
|---|---|---|
| `camera` | 基于场景中摄像机组件的投影 | 使用 CineCamera 或普通 Camera，支持后处理 |
| `manual` | 手动指定投影矩阵或视锥角度 | 适合精确控制每个屏幕的投影参数 |
| `mpcdi` | 从 MPCDI 文件加载校正数据 | 支持 2D/3D/A3D/SL 配置文件格式，支持 ICVFX |
| `easyblend` | 集成 Scalable Display EasyBlend SDK | 支持 DX11/DX12，支持动态视点 |
| `vioso` | 集成 VIOSO Warp & Blend SDK | 支持 DX11/DX12，支持动态视点，带数据缓存 |
| `domeprojection` | 集成 domeprojection.com SDK | 专用于穹顶投影，支持 DX11 |
| `mesh` | 基于场景中网格体的 UV 映射投影 | 使用 StaticMesh 或 ProceduralMesh 的几何作为投影面 |
| `reference` | 引用另一个视口的投影配置 | 复用已有视口的投影数据，避免重复配置 |
| `link` | 继承父视口的投影设置 | 简单的视口投影继承机制 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CameraPolicySetCamera` | 为指定视口设置摄影机投影策略使用的摄像机组件 | `UDisplayClusterBlueprintLib` |

### 使用示例

**设置摄影机投影策略**（蓝图描述）：

1. 拖入 `Camera Policy Set Camera` 节点（在 `NDisplay > Projection` 分类下）
2. 设置 **Viewport ID** 为 `"viewport_name"`（对应 .ndisplay 配置中的视口 ID）
3. 设置 **New Camera** 引用场景中的 `CameraActor` 的 `CameraComponent`
4. 设置 **FOV Multiplier** 为需要的倍率（默认 1.0）

> 该功能已从 `IDisplayClusterProjectionBlueprintAPI` 接口迁移到 `UDisplayClusterBlueprintLib` 静态函数库（UE 5.4 起）。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterProjection.h"
#include "DisplayClusterProjectionBlueprintLib.h"
```

### 基本用法

**获取投影模块并查询支持类型**：

```cpp
// 来源: Public/IDisplayClusterProjection.h
if (IDisplayClusterProjection::IsAvailable())
{
    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();

    // 查询所有支持的投影策略类型
    TArray<FString> ProjectionTypes;
    ProjectionModule.GetSupportedProjectionTypes(ProjectionTypes);

    for (const FString& Type : ProjectionTypes)
    {
        UE_LOG(LogTemp, Log, TEXT("Available projection type: %s"), *Type);
    }

    // 获取特定类型的工厂
    auto MPCDIFactory = ProjectionModule.GetProjectionFactory(TEXT("mpcdi"));
    auto EasyBlendFactory = ProjectionModule.GetProjectionFactory(TEXT("easyblend"));
}
```

### 进阶用法

**通过蓝图库设置摄影机投影**：

```cpp
// 来源: Public/Blueprints/DisplayClusterBlueprintLib.h
#include "DisplayClusterBlueprintLib.h"

// 在运行时动态切换视口的摄影机
void SwitchViewpointCamera(const FString& ViewportId, AActor* NewViewpointActor)
{
    if (UCameraComponent* Camera = NewViewpointActor->FindComponentByClass<UCameraComponent>())
    {
        // 1.0 = 默认 FOV，可调整为 >1.0 放大、<1.0 缩小
        UDisplayClusterBlueprintLib::CameraPolicySetCamera(ViewportId, Camera, 1.0f);
    }
}
```

**配置 MPCDI 投影策略的参数字符串**（配置文件中的参数键）：

```cpp
// 来源: Public/DisplayClusterProjectionStrings.h
// MPCDI 策略支持的配置参数：
// - "file"        : MPCDI 文件路径
// - "buffer"      : Buffer ID
// - "region"      : Region ID
// - "origin"      : 原点组件名
// - "mpcdi"       : MPCDI 类型（"MPCDI" 或 "Explicit PFM"）
// - "pfm"         : PFM 文件路径
// - "scale"       : 世界缩放
// - "ue_space"    : 是否使用 UE 坐标系
// - "alpha"       : Alpha 贴图路径
// - "alpha_gamma" : Alpha Gamma 值
// - "beta"        : Beta 贴图路径
// - "EnablePreview" : 启用预览网格

// EasyBlend 策略支持的配置参数：
// - "file"        : EasyBlend 校准文件路径（.ol 或 .pol）
// - "origin"      : 原点组件名
// - "scale"       : 几何单位缩放（默认 mm）

// VIOSO 策略支持的配置参数：
// - "inifile"     : VIOSO INI 配置文件路径
// - "channel"     : 通道名
// - "file"        : VIOSO .vwf 校准文件路径
// - "index"       : 校准索引（一个文件中包含多个几何体时使用）
// - "adapter"     : 适配器
// - "gamma"       : Gamma 校正值
// - "UnitsInMeter": 每米对应的 VIOSO 单位数
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayClusterWarp` | Warp & Blend 核心接口，`IDisplayClusterWarpBlend` 和 `IDisplayClusterWarpPolicy` |
| `DisplayClusterConfiguration` | 投影配置数据模型，`FDisplayClusterConfigurationProjection` |
| `DisplayCluster` | nDisplay 核心运行时，视口和视口代理接口 |
| `ScalableMPCDI` | 第三方 MPCDI 库（External 模块），用于 MPCDI 策略的文件解析 |

## 架构概览

```
IDisplayClusterProjection (模块接口)
    └── FDisplayClusterProjectionModule (模块实现)
            └── ProjectionPolicyFactories (TMap<FString, Factory>)
                    ├── FDisplayClusterProjectionCameraPolicyFactory
                    ├── FDisplayClusterProjectionManualPolicyFactory
                    ├── FDisplayClusterProjectionMPCDIPolicyFactory
                    ├── FDisplayClusterProjectionEasyBlendPolicyFactory
                    │       └── EasyBlendLibraryDX11, EasyBlendLibraryDX12
                    ├── FDisplayClusterProjectionVIOSOPolicyFactory
                    │       └── FDisplayClusterProjectionVIOSOLibrary
                    ├── FDisplayClusterProjectionDomeprojectionPolicyFactory
                    ├── FDisplayClusterProjectionMeshPolicyFactory
                    ├── FDisplayClusterProjectionReferencePolicyFactory
                    └── FDisplayClusterProjectionLinkPolicyFactory

每个 Policy Factory 创建对应的 Policy 实例:
    IDisplayClusterProjectionPolicy (接口)
        └── FDisplayClusterProjectionPolicyBase (基类)
                ├── FDisplayClusterProjectionCameraPolicy
                ├── FDisplayClusterProjectionManualPolicy
                ├── FDisplayClusterProjectionMPCDIPolicy
                ├── FDisplayClusterProjectionEasyBlendPolicy
                ├── FDisplayClusterProjectionVIOSOPolicy
                ├── FDisplayClusterProjectionDomeprojectionPolicyBase
                │       ├── FDisplayClusterProjectionDomeprojectionPolicyDX11
                │       └── (DX12 等)
                ├── FDisplayClusterProjectionMeshPolicy
                ├── FDisplayClusterProjectionReferencePolicy
                └── FDisplayClusterProjectionLinkPolicy
```

**第三方 SDK 集成方式**：

| SDK | 加载方式 | DX11 | DX12 | 动态视点 |
|---|---|---|---|---|
| EasyBlend | DLL 动态加载 | ✅ | ✅ | ✅ (.pol 文件) |
| VIOSO | DLL 动态加载 | ✅ | ✅ | ✅ |
| Domeprojection | DLL 动态加载 | ✅ | ❌ | ✅ |
| MPCDI | 静态链接 ScalableMPCDI | ✅ | ✅ | ✅ |

所有第三方 SDK 的 DLL 均通过延迟加载（LoadLibrary）方式集成，若 DLL 缺失，对应的投影策略会被优雅降级并输出日志警告。