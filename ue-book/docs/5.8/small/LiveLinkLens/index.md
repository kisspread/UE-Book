# LiveLinkLens

> Adds a new LiveLink LensRole and LensController to support streaming of pre-calibrated lens data

| 属性 | 值 |
|---|---|
| 中文名 | 镜头畸变数据流 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块） |
| 模块 | `LiveLinkLens` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkLens) | |

## 用途

LiveLinkLens 是 LiveLink 系统在虚拟制作领域的一个专用扩展模块。它解决的核心问题是：**如何将外部设备（如摄影机、跟踪系统）采集的、经过精确校准的镜头畸变数据，实时、高保真地流式传输并应用到虚幻引擎的虚拟摄像机中。**

标准的 LiveLink 摄像机角色 (`ULiveLinkCameraRole`) 只传输基础的变换、光圈、焦距等信息，不包含复杂的镜头畸变模型参数。而现实世界的镜头（尤其是电影镜头）存在固有的光学畸变（如桶形畸变、枕形畸变）。LiveLinkLens 通过引入 `ULiveLinkLensRole` 和 `ULiveLinkLensController`，填补了这一空白。它定义了专门的数据结构来承载畸变参数（如畸变系数数组、归一化焦距、主点坐标），并提供了一个控制器来将这些数据驱动到引擎的镜头组件上，从而在虚拟场景中精确复现真实镜头的光学特性。

## 使用场景

- **虚拟制作 (Virtual Production)**：在 LED 墙或实时绿幕拍摄中，需要将现场摄影机的镜头畸变实时应用到引擎中的虚拟摄像机，以保证画面边缘的几何匹配和透视关系正确。
- **实时渲染与合成**：当需要将渲染出的画面与实拍画面进行无缝合成时，精确的镜头畸变模拟是关键。
- **影视预演 (Previz) 与后制 (Postviz)**：在后期制作阶段，使用带有准确镜头特性的虚拟摄像机来匹配实拍素材。
- **使用 LiveLinkHub**：该插件的模块配置 `ProgramAllowlist` 包含 `LiveLinkHub`，表明其设计初衷是在 LiveLinkHub 这一中心化数据管理节点上运行，集中处理并分发镜头数据。

## 蓝图用法

LiveLinkLens 主要通过其定义的数据结构与 LiveLink 系统交互，自身不直接暴露大量可调用的蓝图函数。核心在于处理和使用其定义的专用数据结构。

### 核心数据结构

| 结构体 | 说明 | 用途 |
|---|---|---|
| `FLiveLinkLensStaticData` | 镜头静态数据，继承自摄像机静态数据。 | 存储镜头模型（`LensModel`）等不变信息。 |
| `FLiveLinkLensFrameData` | 镜头逐帧动态数据，继承自摄像机帧数据。 | 存储畸变参数、归一化焦距、主点等变化数据。 |
| `FLiveLinkLensBlueprintData` | 蓝图友好的数据容器。 | 用于在蓝图中方便地访问和设置完整的镜头主题数据（静态+动态）。 |

### 使用示例（蓝图描述）

1.  **接收镜头数据**：在蓝图中，通过 `Get Live Link Subject Data` 节点并指定 `Live Link Lens Role`，可以获取到 `FLiveLinkLensBlueprintData`。然后可以拆分该结构体，分别读取 `StaticData` 中的镜头模型名称，以及 `FrameData` 中的 `DistortionParameters`、`FxFy`、`PrincipalPoint` 等动态数据。
2.  **设置镜头数据**：要创建或设置镜头数据，可以先构建一个 `FLiveLinkLensStaticData` 结构体并设置 `LensModel`，再构建一个 `FLiveLinkLensFrameData` 结构体并填充畸变参数和光心等。最后使用 `Send Live Link Data` 节点发送数据，主题角色选择 `Lens Role`。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkLensTypes.h"
#include "LiveLinkLensRole.h"
#include "LiveLinkLensController.h"
```

### 基本用法

创建和使用镜头数据结构。
（来源：`LiveLinkLensTypes.h`）

```cpp
// 创建静态数据，通常只在镜头切换时更新一次
FLiveLinkLensStaticData LensStaticData;
LensStaticData.LensModel = FName(TEXT("CookeAnamorphic")); // 设置镜头模型名称

// 创建帧数据，每帧更新
FLiveLinkLensFrameData LensFrameData;
LensFrameData.DistortionParameters = {0.1f, -0.05f, 0.01f}; // 示例畸变参数
LensFrameData.FxFy = FVector2D(0.8f, 0.45f); // 示例归一化焦距 (Fx, Fy)
LensFrameData.PrincipalPoint = FVector2D(0.5f, 0.5f); // 光心通常在图像中心

// 可以将其打包到蓝图数据中用于蓝图逻辑
FLiveLinkLensBlueprintData BlueprintData;
BlueprintData.StaticData = LensStaticData;
BlueprintData.FrameData = LensFrameData;
```

### 进阶用法

实现一个自定义的 LiveLink 数据提供者，发送镜头数据。这通常在一个独立的模块或应用中完成。

```cpp
#include "LiveLinkProvider.h"
#include "LiveLinkTypes.h"
#include "LiveLinkLensTypes.h"

// 创建一个 LiveLink 提供者
TSharedPtr<ILiveLinkProvider> LiveLinkProvider = ILiveLinkProvider::CreateLiveLinkProvider(TEXT("MyLensProvider"));

// 定义主题名称
FName SubjectName(TEXT("MyCineLens"));

// 发送静态数据（一次即可，除非镜头更换）
FLiveLinkLensStaticData StaticData;
StaticData.LensModel = FName(TEXT("MasterPrime"));
LiveLinkProvider->UpdateSubjectStaticData(SubjectName, ULiveLinkLensRole::StaticClass(), FLiveLinkStaticDataStruct(StaticData));

// 在每帧（或数据更新时）发送帧数据
void UpdateLensData(const TArray<float>& DistortionParams, const FVector2D& InFxFy, const FVector2D& InPrincipalPoint)
{
    FLiveLinkLensFrameData FrameData;
    FrameData.DistortionParameters = DistortionParams;
    FrameData.FxFy = InFxFy;
    FrameData.PrincipalPoint = InPrincipalPoint;
    
    // 注意：实际使用时，还需要填充继承自 FLiveLinkCameraFrameData 的成员
    // 如 WorldTime, MetaData 等
    
    LiveLinkProvider->UpdateSubjectFrameData(SubjectName, FLiveLinkFrameDataStruct(FrameData));
}
```

## Demo 示例

一个最小化的镜头数据提供者类。
**LensDataProvider.h**
```cpp
#pragma once
#include "LiveLinkProvider.h"
#include "ILiveLinkClient.h"

class FLensDataProvider
{
public:
    FLensDataProvider();
    ~FLensDataProvider();

    void Initialize();
    void SendLensFrameData(const TArray<float>& Distortion, const FVector2D& FxFy, const FVector2D& PrincipalPoint);

private:
    TSharedPtr<ILiveLinkProvider> Provider;
    FName ProviderSubjectName;
};
```

**LensDataProvider.cpp**
```cpp
#include "LensDataProvider.h"
#include "LiveLinkLensTypes.h"
#include "LiveLinkLensRole.h"

FLensDataProvider::FLensDataProvider()
    : ProviderSubjectName("MinimalLens")
{
}

FLensDataProvider::~FLensDataProvider()
{
    if (Provider.IsValid())
    {
        // 提供者析构时会自动清理
        Provider.Reset();
    }
}

void FLensDataProvider::Initialize()
{
    Provider = ILiveLinkProvider::CreateLiveLinkProvider(TEXT("MinimalLensProvider"));
    
    // 设置静态数据
    FLiveLinkLensStaticData StaticData;
    StaticData.LensModel = FName("SimpleDistortion");
    
    // 需要手动初始化父类 FLiveLinkCameraStaticData 中的字段
    StaticData.bIsFocusDistanceSupported = false;
    StaticData.bIsApertureSupported = false;
    StaticData.FieldOfView = 90.0f;
    
    Provider->UpdateSubjectStaticData(ProviderSubjectName, ULiveLinkLensRole::StaticClass(), FLiveLinkStaticDataStruct(StaticData));
}

void FLensDataProvider::SendLensFrameData(const TArray<float>& Distortion, const FVector2D& FxFy, const FVector2D& PrincipalPoint)
{
    FLiveLinkLensFrameData FrameData;
    FrameData.DistortionParameters = Distortion;
    FrameData.FxFy = FxFy;
    FrameData.PrincipalPoint = PrincipalPoint;
    
    // 需要手动设置父类 FLiveLinkCameraFrameData 中的关键字段
    FrameData.WorldTime = FPlatformTime::Seconds();
    FrameData.Transform = FTransform::Identity; // 示例，实际应来自跟踪数据
    
    Provider->UpdateSubjectFrameData(ProviderSubjectName, FLiveLinkFrameDataStruct(FrameData));
}
```

## 模块依赖

从插件元数据 (`Plugins` 字段) 可知，该插件强依赖于以下模块。你的项目若要使用此插件，需确保这些模块（或其所属插件）已启用。

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 核心框架，提供角色、主题、数据传输等基础功能。 |
| `CameraCalibrationCore` | 相机校准核心，提供镜头模型、校准数据等基础类型和功能。 |
| `LensComponent` | 镜头组件插件，提供将镜头数据（畸变、像差）应用到摄像机组件的具体逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-02 | `b61181e2` | LiveLink: Fix crash when take recording Live Link and Lens Model does not exist. | 修复在镜头模型不存在时录制 Live Link 会导致的崩溃。 |
| 2024-05-16 | `1a335018` | LiveLinkLens: Remove the feature where a LiveLink Lens Controller will automatically set the distort | 移除了 LiveLink 镜头控制器自动设置镜头畸变的功能，改为由镜头组件直接处理。 |
| 2023-12-21 | `c2472ab2` | CameraCalibration: Move LensComponent into its own plugin | 镜头组件模块从 CameraCalibration 插件分离，成为独立插件，影响了此插件的依赖关系。 |
| 2023-11-16 | `65c4f129` | Add livelinkhub to program allowlists | 将 `LiveLinkHub` 加入插件的程序白名单，明确了该插件是为 LiveLinkHub 设计的。 |
| 2023-02-07 | `3be863f9` | Camera Calibration: Fix LensFile to broadcast an event when the LensModel changes. Properly update l | 修复了镜头文件在镜头模型变更时的事件广播问题，确保下游（如本插件）能正确更新。 |

### 维护评价

- **活跃维护**：插件在 **2025年5月** 仍有实质性更新（修复崩溃），表明仍在维护中。
- **功能调整**：2024年5月的提交移除了控制器的自动畸变设置功能，这是一个**重要的行为变更**，意味着现在畸变应用的职责完全转移给了 `LensComponent`。使用者需要确保自己的设置与新流程一致。
- **实验性状态**：`.uplugin` 中明确标记为 `IsBetaVersion: true`，且默认未启用（`Installed: false`，需在特定程序 `LiveLinkHub` 中使用）。这**并非一个开箱即用的稳定插件**，其 API 和行为可能会发生变化。
- **推荐度**：**推荐在明确的虚拟制作工作流中，特别是使用 LiveLinkHub 作为数据中枢的场景下使用。** 对于新项目，应关注其 2024 年的架构变更，并理解现在镜头畸变的驱动逻辑。由于其是实验性插件，在生产环境中需进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkLens)
- [官方文档]() （`.uplugin` 中未提供）
- [测试用例]() （测试用例通常位于 `Engine/Tests/LiveLinkLens`，具体路径需确认）