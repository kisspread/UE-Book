# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、媒体资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于 **多机集群同步渲染** 的核心插件，解决的是单台 PC 无法驱动大规模显示阵列的问题。它允许多台 PC 组成渲染集群，每台 PC 负责渲染画面的一部分（一个或多个视口），通过网络同步实现帧级精确的画面拼接。

nDisplay 的核心应用场景是 **虚拟制片（Virtual Production）** 中的 **ICVFX（In-Camera VFX）** 工作流——在 LED 墙幕上实时渲染背景画面，让摄影机拍摄时获得真实的光影和反射效果。它还广泛应用于：

- **CAVE 沉浸式环境**：多面投影组成的沉浸式空间
- **穹顶/弧幕投影**：飞行模拟器、天文馆等曲面显示
- **多屏拼接显示**：大型 LED 显示墙、指挥中心
- **立体渲染（Stereo）**：支持左右眼分别渲染的 3D 显示

插件提供了完整的配置系统（JSON/ndisplay 文件格式）、投影策略（平面/曲面/MPCDI）、色彩管理（OCIO）、媒体输入输出、瓦片渲染、输出重映射等功能。

## 使用场景

- 你在搭建 LED 虚拟制片影棚，需要多台渲染 PC 驱动 LED 墙幕 → 用 nDisplay
- 你需要构建 CAVE 沉浸式投影环境（多面投影） → 用 nDisplay
- 你有多台 PC 需要同步渲染一个超宽画面并拼接 → 用 nDisplay
- 你需要在穹顶或弧幕上做投影校正 → 用 nDisplay + MPCDI 投影策略
- 你需要对集群渲染的输出做色彩管理（OCIO） → 用 nDisplay 的 OCIO 集成
- 你需要将渲染画面通过媒体框架输出到外部设备 → 用 nDisplay 的 Media 模块

## 模块架构

nDisplay 由 27 个模块组成，按功能可分为以下几组：

### 核心渲染

| 模块 | 职责 |
|---|---|
| `DisplayCluster` | 主运行时模块，集群同步、渲染管线、视口管理 |
| `DisplayClusterConfiguration` | 配置数据结构定义，JSON 配置文件的加载/保存 |
| `DisplayClusterProjection` | 投影策略（平面、MPCDI、Mesh 等） |
| `DisplayClusterWarp` | 几何校正（Warp）和边缘融合 |
| `DisplayClusterShaders` | nDisplay 专用着色器 |
| `DisplayClusterReplication` | 集群节点间的数据复制 |
| `ScalableMPCDI` | 第三方 MPCDI 投影校正库 |

### 色彩与后处理

| 模块 | 职责 |
|---|---|
| `DisplayClusterColorGrading` | 色彩分级 |
| `DisplayClusterScenePreview` | 场景预览渲染 |

### 媒体

| 模块 | 职责 |
|---|---|
| `DisplayClusterMedia` | 媒体输入输出框架 |
| `DisplayClusterMediaEditor` | 媒体编辑器工具 |
| `SharedMemoryMedia` | 共享内存媒体传输 |
| `SharedMemoryMediaEditor` | 共享内存媒体编辑器 |

### 编辑器工具

| 模块 | 职责 |
|---|---|
| `DisplayClusterConfigurator` | nDisplay 配置编辑器 UI |
| `DisplayClusterEditor` | 编辑器集成 |
| `DisplayClusterDetails` | Details 面板自定义 |
| `DisplayClusterOperator` | 运维操作面板 |
| `DisplayClusterLightCardEditor` | Light Card 编辑器 |
| `DisplayClusterLightCardEditorShaders` | Light Card 编辑器着色器 |

### 集成模块

| 模块 | 职责 |
|---|---|
| `DisplayClusterMoviePipeline` | Movie Render Queue 集成 |
| `DisplayClusterMoviePipelineEditor` | Movie Pipeline 编辑器 |
| `DisplayClusterMultiUser` | 多用户编辑集成 |
| `DisplayClusterRemoteControlInterceptor` | Remote Control API 拦截器 |
| `DisplayClusterMessageInterception` | 消息拦截 |
| `DisplayClusterStageMonitoring` | 舞台监控 |
| `DisplayClusterFillDerivedDataCache` | DDC 填充工具 |
| `DisplayClusterTests` | 自动化测试 |

## 配置系统

nDisplay 使用 `.ndisplay` 文件（JSON 格式）定义整个集群的渲染配置。配置文件版本历史：

| 版本 | 格式 |
|---|---|
| Version_426 | 4.26 JSON 格式 |
| Version_427 | 4.27 JSON 格式 |
| Version_500 | 5.00 JSON 格式（当前） |

### 配置层级结构

```
UDisplayClusterConfigurationData
├── FDisplayClusterConfigurationInfo          // 配置元信息
├── Cluster                                   // 集群节点定义
│   ├── UDisplayClusterConfigurationClusterNode  // 每个渲染节点
│   │   ├── Window                            // 窗口设置
│   │   └── Viewports[]                       // 视口列表
│   └── Network                               // 网络配置
├── Scene                                     // 场景层级
│   ├── Screens[]                             // 屏幕定义
│   ├── Xforms[]                              // 变换节点
│   └── Cameras[]                             // 摄影机
├── ICVFX                                     // In-Camera VFX 设置
│   ├── StageSettings                         // 舞台设置
│   │   ├── Chromakey                         // 色键设置
│   │   ├── LightCard                         // Light Card 设置
│   │   ├── OCIO                              // 色彩管理
│   │   └── ColorGrading                      // 色彩分级
│   └── Cameras[]                             // ICVFX 摄影机
└── Meta                                      // 元数据
```

### 关键配置类型

#### 视口配置 (`FDisplayClusterConfigurationViewport`)

每个视口定义了渲染区域、投影策略、后处理等：

- **渲染区域**：`RenderTargetRect` 定义视口在屏幕上的位置和大小
- **投影策略**：`ProjectionPolicy` 决定如何将 3D 场景映射到 2D 屏幕
- **ICVFX 设置**：`ICVFX` 控制该视口是否参与 In-Camera VFX 渲染
- **视口重映射**：`Remap` 支持对视口输出进行旋转、翻转、子区域映射
- **过扫描**：`Overscan` 在视口边缘扩展渲染区域，用于边缘融合
- **上采样**：`Upscaler` 配置 DLSS/FSR 等上采样方法
- **后处理**：`CustomPostprocess` 自定义后处理效果
- **色彩管理**：`OCIO` OpenColorIO 色彩空间转换

#### ICVFX 摄影机配置

ICVFX 摄影机定义了虚拟制片中摄影机的渲染行为：

- **内锥体（Inner Frustum）**：摄影机实际拍摄到的 LED 墙幕区域
- **色键（Chromakey）**：在内锥体区域渲染色键颜色或色键纹理
- **Light Card**：在内锥体上方渲染的灯光卡片，模拟真实光源
- **OCIO**：独立的色彩管理配置

#### 瓦片渲染 (`FDisplayClusterConfigurationTile_Settings`)

支持将单个视口分割为多个瓦片进行渲染，用于超高分辨率场景：

- `Layout`：瓦片布局（X × Y），最大 4×4
- `Overscan`：瓦片级别的过扫描和边缘混合

#### 输出重映射 (`FDisplayClusterConfigurationFramePostProcess_OutputRemap`)

对最终 backbuffer 进行屏幕空间重映射，支持三种数据源：
- 静态网格体（Static Mesh）
- 外部 .obj 文件
- 网格体组件引用

#### 媒体配置

支持通过 Media Framework 进行输入输出：
- **媒体输入**：从外部设备接收画面
- **媒体输出**：将渲染画面输出到外部设备
- **同步策略**：`UDisplayClusterMediaOutputSynchronizationPolicy` 控制输出同步
- **瓦片媒体**：支持将媒体输出分割为瓦片

## 蓝图用法

nDisplay 的配置数据结构大量使用 `BlueprintReadWrite`，主要通过配置数据对象进行访问。

### 核心配置结构

| 结构体 | 说明 | 关键属性 |
|---|---|---|
| `FDisplayClusterConfigurationViewport_Overscan` | 视口过扫描设置 | `bEnabled`, `Mode`, `Left/Right/Top/Bottom` |
| `FDisplayClusterConfigurationUpscalerSettings` | 上采样器设置 | `MethodName`, `EditingData` |
| `FDisplayClusterConfigurationViewport_Remap` | 视口重映射 | `bEnable`, `BaseRemap` |
| `FDisplayClusterConfigurationViewport_RemapData` | 重映射区域数据 | `ViewportRegion`, `OutputRegion`, `Angle`, `bFlipH/V` |
| `FDisplayClusterConfigurationFramePostProcess_OutputRemap` | 输出重映射 | `bEnable`, `DataSource`, `StaticMesh`, `ExternalFile` |
| `FDisplayClusterConfigurationTile_Settings` | 瓦片渲染设置 | `bEnabled`, `Layout` |
| `FDisplayClusterConfigurationTile_Overscan` | 瓦片过扫描 | `bEnabled`, `bOversize`, `AllSides` |
| `FDisplayClusterConfigurationPostRender_Override` | 纹理替换 | `bAllowReplace`, `SourceTexture` |
| `FDisplayClusterConfigurationPostRender_BlurPostprocess` | 模糊后处理 | `Mode`, `KernelRadius`, `KernelScale` |
| `FDisplayClusterConfigurationViewport_ICVFX` | 视口 ICVFX 设置 | `bAllowICVFX`, `bAllowInnerFrustum`, `LightcardRenderMode` |
| `FDisplayClusterConfigurationViewport_ColorGradingSettings` | 色彩分级 | `Saturation`, `Contrast`, `Gamma`, `Gain`, `Offset` |

### OCIO 配置

| 结构体 | 说明 |
|---|---|
| `FDisplayClusterConfigurationOCIOConfiguration` | 全局 OCIO 配置 |
| `FDisplayClusterConfigurationOCIOProfile` | 按对象的 OCIO 配置 |
| `FDisplayClusterConfigurationICVFX_ViewportOCIO` | 视口级 OCIO |
| `FDisplayClusterConfigurationICVFX_CameraOCIO` | 摄影机级 OCIO |
| `FDisplayClusterConfigurationICVFX_LightcardOCIO` | Light Card OCIO |

### 媒体配置

| 结构体 | 说明 |
|---|---|
| `FDisplayClusterConfigurationMediaInput` | 媒体输入源 |
| `FDisplayClusterConfigurationMediaOutput` | 媒体输出目标 |
| `FDisplayClusterConfigurationMediaInputGroup` | 媒体输入组（按集群节点） |
| `FDisplayClusterConfigurationMediaOutputGroup` | 媒体输出组（按集群节点） |

## C++ 用法

### 头文件引入

```cpp
// 配置模块
#include "IDisplayClusterConfiguration.h"
#include "DisplayClusterConfigurationTypes.h"

// 具体配置类型
#include "DisplayClusterConfigurationTypes_Viewport.h"
#include "DisplayClusterConfigurationTypes_ICVFX.h"
#include "DisplayClusterConfigurationTypes_Media.h"
#include "DisplayClusterConfigurationTypes_Upscaler.h"
#include "DisplayClusterConfigurationTypes_OCIO.h"
#include "DisplayClusterConfigurationTypes_Tile.h"
#include "DisplayClusterConfigurationTypes_OutputRemap.h"
#include "DisplayClusterConfigurationTypes_ViewportRemap.h"
#include "DisplayClusterConfigurationTypes_ViewportOverscan.h"
```

### 基本用法：加载和保存配置

```cpp
// 来源: IDisplayClusterConfiguration.h
// 获取配置模块
IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();

// 检查配置文件版本
EDisplayClusterConfigurationVersion Version = ConfigModule.GetConfigVersion(TEXT("path/to/config.ndisplay"));

// 加载配置数据
UDisplayClusterConfigurationData* ConfigData = ConfigModule.LoadConfig(TEXT("path/to/config.ndisplay"), GetTransientPackage());

// 保存配置数据
ConfigModule.SaveConfig(ConfigData, TEXT("path/to/output.ndisplay"));

// 将配置序列化为字符串
FString ConfigString;
ConfigModule.ConfigAsString(ConfigData, ConfigString);
```

### 基本用法：配置过扫描

```cpp
// 来源: DisplayClusterConfigurationTypes_ViewportOverscan.h
FDisplayClusterConfigurationViewport_Overscan OverscanSettings;
OverscanSettings.bEnabled = true;
OverscanSettings.Mode = EDisplayClusterConfigurationViewportOverscanMode::Percent;
OverscanSettings.Left = 5.0f;   // 左侧过扫描 5%
OverscanSettings.Right = 5.0f;  // 右侧过扫描 5%
OverscanSettings.Top = 3.0f;    // 顶部过扫描 3%
OverscanSettings.Bottom = 3.0f; // 底部过扫描 3%
OverscanSettings.bOversize = true; // 按过扫描分辨率渲染
```

### 基本用法：视口重映射

```cpp
// 来源: DisplayClusterConfigurationTypes_ViewportRemap.h
FDisplayClusterConfigurationViewport_Remap RemapConfig;
RemapConfig.bEnable = true;

// 基础重映射：旋转 90 度并水平翻转
RemapConfig.BaseRemap.ViewportRegion = FDisplayClusterConfigurationRectangle(0, 0, 1920, 1080);
RemapConfig.BaseRemap.OutputRegion = FDisplayClusterConfigurationRectangle(0, 0, 1080, 1920);
RemapConfig.BaseRemap.Angle = 90.0f;
RemapConfig.BaseRemap.bFlipH = true;

// 检查重映射是否有效
if (RemapConfig.BaseRemap.IsValid())
{
    // 应用重映射...
}
```

### 进阶用法：ICVFX 摄影机配置

```cpp
// 来源: DisplayClusterConfigurationTypes_ICVFX.h, DisplayClusterConfigurationTypes_Viewport.h

// 配置视口的 ICVFX 设置
FDisplayClusterConfigurationViewport_ICVFX ViewportICVFX;
ViewportICVFX.bAllowICVFX = true;
ViewportICVFX.bAllowInnerFrustum = true;
ViewportICVFX.CameraRenderMode = EDisplayClusterConfigurationICVFX_OverrideCameraRenderMode::Default;
ViewportICVFX.LightcardRenderMode = EDisplayClusterConfigurationICVFX_OverrideLightcardRenderMode::Default;
ViewportICVFX.OverrideChromakeyType = EDisplayClusterConfigurationICVFX_OverrideChromakeyType::Default;

// 按摄影机覆盖色键类型
ViewportICVFX.PerCameraOverrideChromakeyType.Add(
    TEXT("Camera_01"),
    EDisplayClusterConfigurationICVFX_OverrideChromakeyType::CustomChromakey
);

// 反转摄影机优先级（适用于时分复用显示器）
ViewportICVFX.bReverseCameraPriority = true;
```

### 进阶用法：OCIO 色彩管理

```cpp
// 来源: DisplayClusterConfigurationTypes_OCIO.h, DisplayClusterConfigurationTypes_ICVFX.h

// 配置全局 OCIO
FDisplayClusterConfigurationOCIOConfiguration GlobalOCIO;
GlobalOCIO.bIsEnabled = true;
GlobalOCIO.ColorConfiguration.ConfigurationSource = TEXT("path/to/config.ocio");
GlobalOCIO.ColorConfiguration.SourceColorSpace = FOpenColorIOColorSpace(TEXT("sRGB"));
GlobalOCIO.ColorConfiguration.DestinationColorSpace = FOpenColorIOColorSpace(TEXT("ACEScg"));

// 配置按视口的 OCIO 覆盖
FDisplayClusterConfigurationOCIOProfile ViewportOCIOProfile;
ViewportOCIOProfile.bIsEnabled = true;
ViewportOCIOProfile.ApplyOCIOToObjects = { TEXT("Viewport_01"), TEXT("Viewport_02") };
ViewportOCIOProfile.ColorConfiguration.ConfigurationSource = TEXT("path/to/config.ocio");

// 查询特定视口的 OCIO 配置
FDisplayClusterConfigurationICVFX_ViewportOCIO ViewportOCIO;
const FOpenColorIOColorConversionSettings* Settings = ViewportOCIO.FindOCIOConfiguration(TEXT("Viewport_01"));
if (Settings)
{
    // 使用 OCIO 配置...
}
```

### 进阶用法：输出重映射

```cpp
// 来源: DisplayClusterConfigurationTypes_OutputRemap.h

// 使用静态网格体进行输出重映射
FDisplayClusterConfigurationFramePostProcess_OutputRemap OutputRemap;
OutputRemap.bEnable = true;
OutputRemap.DataSource = EDisplayClusterConfigurationFramePostProcess_OutputRemapSource::StaticMesh;
OutputRemap.StaticMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Meshes/RemapMesh"));

// 或使用外部 .obj 文件
FDisplayClusterConfigurationFramePostProcess_OutputRemap OutputRemapFromFile;
OutputRemapFromFile.bEnable = true;
OutputRemapFromFile.DataSource = EDisplayClusterConfigurationFramePostProcess_OutputRemapSource::ExternalFile;
OutputRemapFromFile.ExternalFile = TEXT("C:/Remap/remap_mesh.obj");
```

### 进阶用法：瓦片渲染

```cpp
// 来源: DisplayClusterConfigurationTypes_Tile.h

// 配置 2x2 瓦片渲染
FDisplayClusterConfigurationTile_Settings TileSettings;
TileSettings.bEnabled = true;
TileSettings.Layout = FIntPoint(2, 2); // 2x2 瓦片

// 配置瓦片过扫描
FDisplayClusterConfigurationTile_Overscan TileOverscan;
TileOverscan.bEnabled = true;
TileOverscan.bOversize = true;
TileOverscan.bOptimizeTileOverscan = true; // 边缘瓦片不做过扫描
TileOverscan.Mode = EDisplayClusterConfigurationViewportOverscanMode::Percent;
TileOverscan.AllSides = 10.0f; // 所有边 10% 过扫描
TileOverscan.OverscanBlendMode = EDisplayClusterConfigurationViewportOverscanBlendMode::Percent50;
```

### 进阶用法：媒体同步策略

```cpp
// 来源: DisplayClusterConfigurationTypes_MediaSync.h

// 实现自定义媒体输出同步策略
class FMyMediaSyncHandler : public IDisplayClusterMediaOutputSynchronizationPolicyHandler
{
public:
    virtual bool IsCaptureTypeSupported(UMediaCapture* MediaCapture) const override
    {
        // 检查是否支持该捕获类型
        return true;
    }

    virtual bool StartSynchronization(UMediaCapture* MediaCapture, const FString& MediaId) override
    {
        // 启动同步逻辑
        return true;
    }

    virtual void StopSynchronization() override
    {
        // 停止同步
    }

    virtual bool IsRunning() override
    {
        return bRunning;
    }

    virtual TSubclassOf<UDisplayClusterMediaOutputSynchronizationPolicy> GetPolicyClass() const override
    {
        return UMySyncPolicy::StaticClass();
    }

private:
    bool bRunning = false;
};
```

## Demo 示例

### 最小配置加载示例

**Build.cs**:
```csharp
using UnrealBuildTool;

public class MyNDisplayModule : ModuleRules
{
    public MyNDisplayModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "DisplayClusterConfiguration"
        });
    }
}
```

**MyNDisplayActor.h**:
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DisplayClusterConfigurationTypes.h"
#include "IDisplayClusterConfiguration.h"
#include "MyNDisplayActor.generated.h"

UCLASS()
class AMyNDisplayActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNDisplayActor();

    /** 加载 nDisplay 配置文件 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay")
    bool LoadDisplayConfig(const FString& ConfigPath);

    /** 获取配置数据 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay")
    UDisplayClusterConfigurationData* GetConfigurationData() const { return ConfigurationData; }

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UDisplayClusterConfigurationData> ConfigurationData;

    /** 配置文件路径 */
    UPROPERTY(EditAnywhere, Category = "nDisplay")
    FString ConfigFilePath;
};
```

**MyNDisplayActor.cpp**:
```cpp
#include "MyNDisplayActor.h"
#include "IDisplayClusterConfiguration.h"

AMyNDisplayActor::AMyNDisplayActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNDisplayActor::BeginPlay()
{
    Super::BeginPlay();

    if (!ConfigFilePath.IsEmpty())
    {
        LoadDisplayConfig(ConfigFilePath);
    }
}

bool AMyNDisplayActor::LoadDisplayConfig(const FString& InConfigPath)
{
    if (!IDisplayClusterConfiguration::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DisplayClusterConfiguration module is not available"));
        return false;
    }

    IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();

    // 检查配置版本
    EDisplayClusterConfigurationVersion Version = ConfigModule.GetConfigVersion(InConfigPath);
    if (Version == EDisplayClusterConfigurationVersion::Unknown)
    {
        UE_LOG(LogTemp, Error, TEXT("Unknown config version: %s"), *InConfigPath);
        return false;
    }

    // 加载配置
    ConfigurationData = ConfigModule.LoadConfig(InConfigPath, this);
    if (!ConfigurationData)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load config: %s"), *InConfigPath);
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Successfully loaded nDisplay config: %s"), *InConfigPath);
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | 配置数据结构和加载/保存 |
| `DisplayCluster` | 核心运行时（集群同步、渲染） |
| `DisplayClusterProjection` | 投影策略 |
| `DisplayClusterWarp` | 几何校正 |
| `DisplayClusterShaders` | nDisplay 着色器 |
| `DisplayClusterMedia` | 媒体输入输出 |
| `SharedMemoryMedia` | 共享内存传输 |
| `ScalableMPCDI` | MPCDI 投影校正（第三方） |
| `OpenColorIO` | OCIO 色彩管理（通过配置类型间接依赖） |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（DisplayClusterMedia, SharedMemoryMedia） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 近期 | `fd10a6f7ccde` | 修复 ICVFX 相关问题 |
| 近期 | `635b729d7c9e` | 瓦片视口边缘混合功能 |
| 近期 | `cebfc41fafcf` | 修复 DCRA 渲染问题 |

### 维护评价

nDisplay 是 Epic Games **持续活跃维护** 的大型插件，是虚拟制片工作流的核心组件。从近期提交记录来看，团队仍在积极修复 ICVFX 相关问题、改进瓦片渲染的边缘混合、修复渲染问题。

**优势**：
- 作为 UE5 虚拟制片的核心组件，有 Epic 官方团队持续维护
- 功能全面：覆盖投影、色彩管理、媒体、同步等完整链路
- 支持 Win64 和 Linux 平台
- 有完善的配置版本管理系统

**注意事项**：
- `EnabledByDefault = false`，需要在项目设置中手动启用
- 模块数量多（27 个），初次理解架构有一定学习成本
- 部分模块标记为 Runtime 但实际包含编辑器功能（如 DisplayClusterConfigurator、DisplayClusterEditor），这可能是模块类型标注的简化
- 需要多台 PC 和专业显示硬件才能发挥完整功能

**推荐使用**：如果你的项目涉及虚拟制片、多屏显示或沉浸式投影，nDisplay 是唯一的选择且值得信赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/n-display-in-unreal-engine/)