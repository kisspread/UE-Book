# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师工具包 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（素材、材质、蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 角色动画制作工具集。它解决的核心问题是将真实的面部捕捉数据（如 iPhone 深度摄像头、专业动捕设备或视频素材）高效、准确地驱动到 UE5 中的 MetaHuman 角色上，生成高质量的动画。

该插件并非一个简单的功能库，而是一个包含从数据捕获、面部追踪、解算、到最终动画序列生成的完整工作流程引擎。它整合了面部轮廓追踪、面部拟合解算器、深度图生成、性能优化、语音驱动面部动画以及批处理等复杂模块，旨在为电影、电视、游戏等领域提供工业级的虚拟人动画解决方案。

## 使用场景

- **电影级虚拟人表演**：你需要将演员的真实表演（通过专业动捕设备或 iPhone）精确地映射到一个超写实的 MetaHuman 角色上。
- **快速生成对话动画**：你有一段对话音频，希望自动生成对应的口型和面部表情动画（Speech2Face）。
- **批量处理动画数据**：你拥有大量捕捉到的原始数据，需要通过批处理流程将其高效地转换为可用的动画序列。
- **自定义动画解算**：你需要调整面部追踪点的拟合参数或动画解算器的权重，以获得更符合艺术需求的动画效果。
- **实时预览与编辑**：在动画制作过程中，你需要一个强大的图像查看器来实时预览捕捉画面、深度图以及追踪轮廓，并对追踪点进行手动编辑。

## 蓝图用法

该插件主要面向编辑器工具和C++开发者，其核心功能（如面部解算、追踪）通常通过编辑器界面（MetaHuman Animator面板）驱动，而非直接暴露给蓝图。插件中的 `UCLASS` 和 `USTRUCT` 主要用于内部数据结构和组件，并非为蓝图可视化脚本设计。因此，**没有直接面向蓝图开发者的核心节点**。

主要的交互发生在编辑器中：
1.  **资产创建**：在内容浏览器中右键创建 `MetaHumanIdentity` 资产。
2.  **数据捕获**：在 `MetaHumanAnimator` 编辑器面板中，导入捕捉数据（如 `.usdc` 文件、视频序列等）。
3.  **追踪与解算**：使用面板中的按钮对面部进行标记、追踪和动画解算。
4.  **序列生成**：将解算好的动画数据导出为关卡序列。

## C++ 用法

### 头文件引入

```cpp
// 引入图像查看器编辑器模块的核心类
#include "STrackerImageViewer.h"
#include "MetaHumanFootageComponent.h"
#include "SABImage.h"
```

### 基本用法

从提供的源码来看，`MetaHumanImageViewerEditor` 模块的核心是创建和操作一个高级的图像查看器，用于显示面部追踪数据。

```cpp
// 示例：创建一个追踪图像查看器控件
TSharedRef<STrackerImageViewer> TrackerViewer = SNew(STrackerImageViewer)
    .Image(MyBrushPtr) // 设置显示的纹理资源
    .ShouldDrawPoints(true) // 是否绘制追踪点
    .ShouldDrawCurves(true) // 是否绘制追踪曲线
    .DefaultCurvesColor(FLinearColor::Blue)
    .DefaultPointsColor(FLinearColor::Red);

// 假设我们有一个面部追踪数据控制器
TSharedPtr<FMetaHumanCurveDataController> CurveDataController = GetMyCurveDataController();
TrackerViewer->SetDataControllerForCurrentFrame(CurveDataController);

// 将查看器添加到编辑器面板中
MyEditorPanel->AddSlot()
[
    TrackerViewer
];
```

**文件路径**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanImageViewerEditor/Public/STrackerImageViewer.h`

### 进阶用法

组合使用 `UMetaHumanFootageComponent` 在场景中展示原始素材和深度信息，并通过 `STrackerImageViewer` 进行叠加编辑。

```cpp
// 1. 创建并配置一个 Footage Component 来显示场景中的视频素材
UMetaHumanFootageComponent* FootageComponent = NewObject<UMetaHumanFootageComponent>(MyActor);
FootageComponent->SetFootageResolution(FVector2D(1920, 1080));
FootageComponent->SetMediaTextures(ColorTexture, DepthTexture);

// 2. 创建深度网格组件，用于将深度数据可视化为3D网格
UMetaHumanDepthMeshComponent* DepthMesh = NewObject<UMetaHumanDepthMeshComponent>(MyActor);
DepthMesh->SetDepthTexture(DepthTexture);
DepthMesh->SetCameraCalibration(MyCameraCalibration);
DepthMesh->SetDepthRange(10.0f, 55.5f);

// 3. 在编辑器逻辑中，处理图像查看器的用户交互（如鼠标拖动点）
// 在 STrackerImageViewer 的 OnMouseMove 中，会调用类似 ResolveHighlightingForMouseMove 的方法来更新高亮和选择状态。
// 用户也可以通过 SetEditCurvesAndPointsEnabled 控制是否允许交互编辑。
```

## 模块依赖

以下是使用 `MetaHumanImageViewerEditor` 模块时，你的 Build.cs 中需要添加的独特依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewerEditor` | 提供核心的图像查看器控件（STrackerImageViewer, SABImage）和相关操作 |
| `MetaHumanFootageIngest` | 用于处理和管理原始捕捉素材（Footage）数据 |
| `MetaHumanFaceContourTracker` | 提供面部轮廓追踪算法和数据结构 |
| `MetaHumanFaceFittingSolver` | 提供面部拟合解算器，将追踪数据映射到MetaHuman面部网格 |
| `CameraCalibration` | 用于处理相机标定数据，计算图像平面在3D空间中的位置 |
| `ControlRig` | 用于驱动最终的MetaHuman角色动画 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了MetaHuman角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | (MetaHuman Animator) 支持为已存在的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了序列器缓存问题 |

### 维护评价

**活跃维护中**。基于提供的最近提交记录，该插件在最近一周内（2026年5月）仍有频繁的功能更新和Bug修复。这表明 Epic Games 的团队正在积极地开发和维护 MetaHuman Animator 工具集，以增加新功能（如身体追踪支持）、修复问题并优化性能。

作为一个官方工具，它通常会与 UE 版本的更新同步进行维护。对于致力于使用 MetaHuman 进行高品质虚拟人动画制作的项目，这是一个推荐使用且持续获得支持的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/meta-human-animator-in-unreal-engine/) (假定链接，具体以官方发布为准)