# Display Cluster Light Card Editor

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 灯光卡编辑器 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterLightCardEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterLightCardEditor` 是 **nDisplay** 插件中的一个核心编辑器模块。它为虚拟制作（Virtual Production）中的 LED 墙（LED Volume）场景提供了一个专用的、可视化的编辑界面，用于创建、编辑和管理“灯光卡”（Light Card）和“标志”（Flag）等舞台元素。

**核心问题解决**：在传统的 3D 视口中，艺术家难以精确地在弯曲的 LED 墙或圆顶投影场景中定位灯光和遮挡物。该模块提供了一个专门的 2D 视口，能够根据 nDisplay 配置的投影几何体（如圆柱、球体、UV 映射）来显示和编辑这些元素，确保其在实际物理舞台空间中的位置、方向和形状是正确的。

**存在原因**：它是专业虚拟制作工作流的关键工具，使得灯光美术师和视觉特效主管能够直观地调整 LED 环境中的光线和遮挡，从而实现更高效、更精确的现场拍摄效果。

## 使用场景

*   **LED 虚拟制作**：你在使用 nDisplay 驱动一个 LED 墙进行电影或广告拍摄。你需要在墙上放置“灯光卡”来模拟天空、环境光或特定方向的光源反射，并放置“标志”来遮挡光线，创造阴影或模拟建筑结构。
*   **多投影仪圆顶/环绕系统**：你在为天文馆或体验中心构建一个环绕投影系统。你需要在投影表面上精确地放置遮挡物，以控制投影内容的可见区域。
*   **复杂投影几何体**：你的 nDisplay 集群使用了非标准的投影几何体（如自定义的弯曲表面），需要一个专门的编辑器来对齐和调整舞台元素，而不是使用通用的 3D 视口。

## 蓝图用法

该模块主要是一个编辑器扩展，其核心逻辑通过 C++ 的 `FDisplayClusterLightCardEditor` 类驱动，不直接暴露大量蓝图节点。配置和状态管理通过 Project Settings 和 Editor Preferences 进行。

### 核心配置

在项目设置和编辑器偏好中可找到相关选项：

| 设置 | 说明 | 所在类 |
|---|---|---|
| `LightCardTemplateDefaultPath` | 新建灯光卡模板的默认保存路径 | `UDisplayClusterLightCardEditorProjectSettings` |
| `DefaultLightCardTemplate` | 创建新灯光卡时使用的默认模板资产 | `UDisplayClusterLightCardEditorProjectSettings` |
| `DefaultFlagTemplate` | 创建新标志时使用的默认模板资产 | `UDisplayClusterLightCardEditorProjectSettings` |
| `LightCardLabelScale` | 灯光卡标签的显示缩放 | `UDisplayClusterLightCardEditorProjectSettings` |
| `IconScale` | 编辑器中图标显示的缩放 | `UDisplayClusterLightCardEditorSettings` |

### 使用示例（蓝图描述）

1.  打开 **Project Settings > Plugins > nDisplay Light Card Editor**，设置模板路径和默认模板。
2.  打开 **Editor Preferences > Level Editor > nDisplay Light Card Editor**，调整标签和图标的显示设置。
3.  在编辑器中，通过 **Window > nDisplay > Operator** 面板或快捷键打开灯光卡编辑器。所有操作（如添加、删除、移动灯光卡）均通过该专用 UI 面板和视口完成，而非通用的蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterLightCardEditor.h"
#include "IDisplayClusterLightCardEditor.h"
```

### 基本用法

以下示例展示了如何在自定义编辑器工具中访问灯光卡编辑器的功能。

```cpp
// 假设你有一个指向 ADisplayClusterRootActor 的指针 RootActor
// 来源: 基于 DisplayClusterLightCardEditor.h 中的公共接口

// 1. 检查模块是否可用
if (IDisplayClusterLightCardEditor::IsAvailable())
{
    // 2. 获取模块单例
    IDisplayClusterLightCardEditor& LightCardEditorModule = IDisplayClusterLightCardEditor::Get();

    // 3. 创建编辑器实例（通常用于嵌入其他面板）
    TSharedRef<IDisplayClusterOperatorViewModel> ViewModel = ... // 获取或创建视图模型
    TSharedRef<IDisplayClusterOperatorApp> LightCardEditorApp = FDisplayClusterLightCardEditor::MakeInstance(ViewModel);
    LightCardEditorApp->Initialize(ViewModel);

    // 4. 通过实例调用功能
    // 例如：创建一个新的灯光卡
    // 注意：直接调用需要合适的上下文（如有效的RootActor和Level）
    // LightCardEditorApp->AddNewLightCard();
}
```

### 进阶用法

从多个 test case 和内部实现推断的用法。

```cpp
// 假设你有一个 FDisplayClusterLightCardEditor 的实例：LightCardEditor
// 来源: 结合 DisplayClusterLightCardEditor.h 和 ViewportClient.h 的逻辑

// 1. 管理选择
TArray<AActor*> ActorsToSelect;
ActorsToSelect.Add(SomeLightCardActor);
LightCardEditor->SelectActors(ActorsToSelect);

// 2. 将指定演员定位到视口中心
LightCardEditor->CenterActorInView(SomeLightCardActor);

// 3. 复制/粘贴操作
if (LightCardEditor->CanCopySelectedActors())
{
    LightCardEditor->CopySelectedActors();
}
if (LightCardEditor->CanPasteActors())
{
    TArray<AActor*> NewActors = LightCardEditor->PasteActors();
}

// 4. 创建基于模板的灯光卡
// 假设 Template 是一个有效的 UDisplayClusterLightCardTemplate*
AActor* NewActor = LightCardEditor->SpawnActor(Template);

// 5. 控制视口投影模式（通过视口客户端）
TSharedPtr<FDisplayClusterLightCardEditorViewportClient> ViewportClient = ... // 从视口获取
ViewportClient->SetProjectionMode(EDisplayClusterMeshProjectionType::Azimuthal, LVT_Perspective);
```

## Demo 示例

一个最小的 C++ 示例，演示如何注册一个操作员应用并创建灯光卡编辑器实例。

**DisplayClusterLightCardEditorDemoModule.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FDisplayClusterLightCardEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle OperatorAppHandle;
};
```

**DisplayClusterLightCardEditorDemoModule.cpp**
```cpp
#include "DisplayClusterLightCardEditorDemoModule.h"
#include "DisplayClusterLightCardEditor.h"
#include "IDisplayClusterOperatorViewModel.h"

#define LOCTEXT_NAMESPACE "LightCardEditorDemo"

void FDisplayClusterLightCardEditorDemoModule::StartupModule()
{
    // 检查灯光卡编辑器模块是否可用
    if (FModuleManager::Get().IsModuleLoaded(TEXT("DisplayClusterLightCardEditor")))
    {
        // 获取灯光卡编辑器模块接口
        IDisplayClusterLightCardEditor& LightCardEditorModule = IDisplayClusterLightCardEditor::Get();

        // 注册一个示例操作员应用
        // 注意：在实际 nDisplay 工作流中，通常通过 Operator 面板自动注册。
        // 此处仅为演示如何使用 API。
        UDisplayClusterLightCardEditorProjectSettings* Settings = GetMutableDefault<UDisplayClusterLightCardEditorProjectSettings>();
        UE_LOG(LogTemp, Log, TEXT("LightCard Editor Demo: Default template path is %s"), *Settings->LightCardTemplateDefaultPath.Path);
    }
}

void FDisplayClusterLightCardEditorDemoModule::ShutdownModule()
{
    // 清理代码...
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FDisplayClusterLightCardEditorDemoModule, DisplayClusterLightCardEditorDemo)
```

## 模块依赖

该模块的依赖关系相对特殊，主要与 nDisplay 内部生态系统相关。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，提供集群渲染基础架构和根演员（Root Actor）支持。 |
| `DisplayClusterConfiguration` | nDisplay 配置数据模块，用于读取和解析 .ndisplay 配置文件。 |
| `UnrealEd` | 用于构建编辑器扩展、属性细节面板和蓝图编译集成。 |
| `DisplayClusterShaders` | nDisplay 自定义着色器模块，可能用于灯光卡的特殊渲染效果。 |
| `DisplayClusterProjection` | nDisplay 投影模块，用于处理多种投影模式（方位角、UV 等），是灯光卡编辑器视口的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 和 nDisplay 添加 EXR 多图层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay 影片管线：将 WarpBlendAlpha 模式合并进 WarpBlend。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的相机命名；修复 MPCDI/ICVFX 着色器中的不透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退时遵循非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时的闪烁问题。 |

### 维护评价

*   **创建时间**：2018年，已有约8年历史，是一个非常成熟的模块。
*   **近期更新**：最近的提交均在2026年5月，更新频繁，内容集中在与 Movie Graph 的集成、着色器修复和渲染管线优化上，表明模块仍在积极开发和适配新的 Unreal Engine 功能。
*   **维护状态**：**活跃维护中**。该模块是 Epic Games 官方 nDisplay 解决方案的核心组成部分，持续为虚拟制作行业提供支持。
*   **已知限制**：模块默认未启用 (`EnabledByDefault: false`)，需要用户在插件设置中手动开启。这是一个大型复杂插件的一部分，单独使用意义不大，通常需要整个 nDisplay 插件协同工作。
*   **推荐**：**强烈推荐**给所有使用 Unreal Engine 进行 LED 虚拟制作或多投影仪设置的团队。它是实现专业级舞台灯光和遮挡编辑的必备工具。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
*   [官方文档](https://docs.unrealengine.com/5.8/en-US/ndisplay-overview/) (nDisplay 总览文档)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)