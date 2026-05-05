# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、图标等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具包。它不仅仅是一个简单的插件，而是一个完整的、端到端的面部动画制作流程解决方案。该插件的核心目的是将现实世界中的面部表演（通常通过视频捕获）转化为驱动 MetaHuman 数字角色的高质量动画数据。

它解决的问题是：如何高效、准确地从原始视频素材中提取面部运动信息，并将其应用于高保真的数字人角色，从而大幅简化数字人角色动画的制作流程，使其更接近传统影视制作的工作流。

## 使用场景

- **数字人角色动画制作**：你正在开发一个需要逼真数字人角色的游戏或影视项目，需要从演员的面部表演视频生成动画。
- **从视频生成面部动画**：你拥有一段或多段演员的面部表演视频（例如 iPhone 的 TrueDepth 相机录制的深度视频），希望将其转化为驱动 MetaHuman 角色的动画序列。
- **批量处理动画数据**：你需要对大量的面部表演数据进行统一的处理、求解和导出。
- **面部动画调试与优化**：你需要一个可视化的工具来检查、编辑和优化从视频中提取的面部曲线、关键点以及最终的动画结果。
- **集成外部捕获设备**：你使用专业的面部捕获设备（如 HMC），需要通过协议栈将其数据接入 Unreal Engine。

## 蓝图用法

**重要说明**：MetaHuman Animator 主要是一个**编辑器工具集**，其核心功能通过编辑器 UI（如专用面板、视口）和资产工作流暴露，而非传统的蓝图节点。大部分关键操作（如导入素材、运行求解器、编辑曲线）都在编辑器内完成。

从提供的头文件分析，其公开的蓝图可调用 API 相对有限，主要集中在一些底层组件和数据结构上。以下是一些可能通过蓝图或编辑器脚本访问的核心功能类：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCameraCalibration` | 根据相机校准数据定位和缩放素材显示平面 | `UMetaHumanFootageComponent` |
| `SetMediaTextures` | 设置用于显示颜色和深度数据的媒体纹理 | `UMetaHumanFootageComponent` |
| `SetDepthRange` | 设置素材平面材质中使用的深度范围 | `UMetaHumanFootageComponent` |
| `SetViewMode` | 设置 AB 图像查看器的视图模式（单视图、并排、分割等） | `SABImage` |
| `SetNavigationMode` | 设置图像查看器的导航模式（2D/3D） | `SABImage` |
| `SetTrackerImageSize` | 设置跟踪图像的尺寸，用于计算曲线和点的正确位置 | `STrackerImageViewer` |
| `SetDataControllerForCurrentFrame` | 为当前帧设置曲线数据控制器 | `STrackerImageViewer` |
| `UpdateDisplayedDataForWidget` | 从底层轮廓数据更新此控件上显示的点和曲线的视觉数据 | `STrackerImageViewer` |

### 使用示例（蓝图描述）

由于核心工作流在编辑器中，蓝图主要用于底层组件控制或自动化脚本。例如，你可以通过蓝图动态控制一个 `UMetaHumanFootageComponent` 的显示：

1.  在场景中放置一个 Actor，并添加 `UMetaHumanFootageComponent` 组件。
2.  通过蓝图获取该组件引用。
3.  调用 `SetFootageResolution` 或 `SetCameraCalibration` 来设置其显示的素材尺寸和位置。
4.  调用 `SetMediaTextures` 来指定要显示的颜色和深度纹理。
5.  调用 `ShowColorChannel` 或 `SetUndistortionEnabled` 来控制显示通道和去畸变。

## C++ 用法

MetaHuman Animator 的 C++ API 主要用于其内部模块间的交互以及扩展编辑器功能。对于插件使用者，直接使用其 C++ API 的场景较少，更多是通过编辑器资产和蓝图进行操作。

### 头文件引入

根据你要使用的功能，引入相应模块的头文件。例如：

```cpp
#include "MetaHumanFootageComponent.h"
#include "STrackerImageViewer.h"
#include "MetaHumanCurveDataController.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建和配置一个 `UMetaHumanFootageComponent`，用于在自定义视口中显示 MetaHuman 素材。

```cpp
// 假设你有一个 AActor* MyActor
UMetaHumanFootageComponent* FootageComp = NewObject<UMetaHumanFootageComponent>(MyActor);
FootageComp->RegisterComponent();
MyActor->AddInstanceComponent(FootageComp);

// 设置素材分辨率（当没有相机校准时）
FootageComp->SetFootageResolution(FVector2D(1920, 1080));

// 或者，使用相机校准数据
// UCameraCalibration* MyCalibration = ...;
// FootageComp->SetCameraCalibration(MyCalibration);

// 设置媒体纹理
UTexture* ColorTexture = LoadObject<UTexture>(nullptr, TEXT("/Game/Path/To/ColorMedia"));
UTexture* DepthTexture = LoadObject<UTexture>(nullptr, TEXT("/Game/Path/To/DepthMedia"));
FootageComp->SetMediaTextures(ColorTexture, DepthTexture);

// 显示颜色通道
FootageComp->ShowColorChannel(EABImageViewMode::A);
```

**来源文件**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanImageViewerEditor/Public/MetaHumanFootageComponent.h`

### 进阶用法

结合 `STrackerImageViewer` 和 `FMetaHumanCurveDataController` 可以实现对跟踪曲线的程序化控制。这通常发生在编辑器工具或自定义求解流程中。

```cpp
// 假设你有一个 STrackerImageViewer 实例 TrackerViewerWidget
TSharedPtr<FMetaHumanCurveDataController> CurveController = MakeShared<FMetaHumanCurveDataController>();
// ... 初始化 CurveController，加载或计算曲线数据 ...

// 将控制器设置给查看器
TrackerViewerWidget->SetDataControllerForCurrentFrame(CurveController);

// 更新显示
TrackerViewerWidget->UpdateDisplayedDataForWidget();

// 获取屏幕上某点对应的图像坐标
FVector2D ScreenPos(500, 300);
FVector2D ImageUV = TrackerViewerWidget->GetPointPositionOnImage(ScreenPos, true);
```

**来源文件**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanImageViewerEditor/Public/STrackerImageViewer.h`

## Demo 示例

由于 MetaHuman Animator 是一个复杂的编辑器工具集，提供一个完整的可编译最小示例意义不大。其“Demo”就是插件本身提供的编辑器功能。建议的实践方式是：

1.  启用插件。
2.  在内容浏览器中右键，查找 “MetaHuman” 相关的资产类型（如 `MetaHuman Identity`, `MetaHuman Performance`）。
3.  打开 “MetaHuman Animator” 编辑器面板（通常在 “窗口” -> “MetaHuman” 菜单下）。
4.  按照官方文档或教程，导入一段面部表演视频，体验从捕获到动画生成的完整流程。

## 模块依赖

从模块列表和依赖关系可以看出，这是一个高度模块化的插件。使用者的项目模块如果需要直接引用其功能，可能需要依赖以下**独特**的模块（省略了常见的 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，包含底层算法和数据结构 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供资产类型和编辑器集成 |
| `ControlRigDeveloper` | 用于开发和管理 Control Rig，MetaHuman 动画驱动的核心 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具，用于处理 MetaHuman 的网格体 |
| `CameraCalibration` | 相机校准数据，用于将 2D 视频映射到 3D 空间 |

**注意**：大多数情况下，使用者无需直接依赖这些模块。通过插件提供的编辑器工具和资产工作流即可完成所有操作。

## 维护状态

### 近期更新

```
- dd18b17eca86 Fix the Preview Mesh for SceneCaptureComponent & its derivatives.
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
```

### 维护评价

- **创建时间**：2024年2月，是一个相对较新的插件。
- **最近更新频率和内容**：最近的提交（截至提供的信息）主要是代码维护和编译修复（如修复预览网格体、添加内联宏、调整头文件导出标记），没有看到重大的新功能提交。这表明插件处于稳定维护期。
- **活跃维护**：是。作为 Epic Games 官方支持的 MetaHuman 工具链核心部分，预计会持续维护以适配引擎新版本和修复问题。
- **已知问题或限制**：作为大型复杂插件，可能存在特定硬件、驱动或工作流下的兼容性问题。其功能高度依赖于 Epic 的 MetaHuman 云服务和特定的捕获数据格式。
- **推荐使用**：**强烈推荐**。如果你需要制作高质量的 MetaHuman 角色动画，这是官方且功能最完整的解决方案。尽管它是一个复杂的工具集，但它是目前将视频表演转化为 MetaHuman 动画的最直接路径。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (Epic 官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (插件内包含的测试模块)