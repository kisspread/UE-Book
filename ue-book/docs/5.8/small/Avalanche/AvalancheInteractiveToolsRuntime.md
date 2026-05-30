# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态图形设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（Motion Design）是 UE5 虚拟制片管线中的**动态图形（Motion Graphics）全流程制作工具**。它将传统广播级动态图形制作（如 After Effects、Cinema 4D）的核心能力——合成、设计、播出——整合到 Unreal Engine 的实时渲染环境中。

**核心能力包括：**

- **场景管理**：通过 Scene Tree 和 Outliner 管理复杂的动态图形场景层级结构
- **动画驱动**：深度集成 Sequencer，支持关键帧动画、属性动画和时间轴控制
- **媒体合成**：Media Compositing 实现多图层合成，支持实时视频输入/输出
- **MRQ 渲染**：通过 Media Render Queue 进行离线/实时的高质量渲染输出
- **克隆与效果器**：Cloner/Effector 系统实现对象批量生成和参数化变形
- **材质设计**：专用 Material Designer 面板进行材质参数化编辑
- **3D 文字与图形**：Text3D、SVG 导入、Shapes 几何体生成
- **遮罩系统**：GeometryMask 实现复杂的场景遮罩效果
- **远程控制**：Remote Control 支持外部设备实时控制参数
- **场景装配**：Scene Rig 提供可复用的场景配置模板
- **过渡动画**：Transition 管理场景状态之间的平滑过渡
- **自定义编辑器**：提供专用的 Motion Design 模式和交互式工具

**为什么存在：** 虚拟制片和广播行业需要在 Unreal Engine 中直接完成从设计到播出的全流程，Motion Design 插件填补了 UE 在动态图形领域的工具链空白。

## 使用场景

- 你在做**电视直播动态图形**（如新闻台标、体育比分板）→ 用 Motion Design 全流程
- 你需要**实时可变数据驱动的图形**（如天气、股票）→ 用 Remote Control + Property Animator
- 你在做**虚拟制片中的 AR/图形叠加**→ 用 Media Compositing + MRQ
- 你需要**批量生成并参数化控制对象**（如粒子阵列、文字矩阵）→ 用 Cloner/Effector
- 你要**为直播活动设计可切换的场景**→ 用 Scene Rig + Transition
- 你需要**将 SVG 矢量图转为 3D 几何体**→ 用 SVG Importer + Shapes

## 蓝图用法

Motion Design 的大部分功能通过专用编辑器面板（Motion Design Mode）而非蓝图节点暴露。以下是从源码中提取的核心接口：

### 核心接口

| 接口 | 说明 | 所在模块 |
|---|---|---|
| `IAvaInteractiveToolsModeDetailsObjectProvider` | 提供交互式工具的细节面板对象，用于在 Motion Design 模式下显示工具属性 | `AvalancheInteractiveToolsRuntime` |
| `IAvaInteractiveToolsModeDetailsObject` | 标记对象可作为交互式工具的细节面板数据源 | `AvalancheInteractiveToolsRuntime` |

### 主要功能入口

Motion Design 的使用主要通过以下编辑器 UI 面板：

1. **Motion Design Mode**：切换到专用模式，激活所有设计工具
2. **Scene Tree 面板**：管理场景对象层级
3. **Outliner 面板**：与 Scene Tree 联动的对象大纲视图
4. **Timeline**：与 Sequencer 联动的动画时间轴
5. **Scene Settings 面板**：场景全局配置
6. **Media 面板**：媒体源管理和预览
7. **Scene Rig 面板**：可复用场景模板管理
8. **Show Control 工具栏**：播控操作（页面加载选项：All/Next/Selected）

### 使用示例

1. 在 Level Editor 中启用 **Motion Design** 模式
2. 通过 Scene Tree 创建 3D 文字、SVG 图形或几何体
3. 在 Timeline 中为对象属性添加关键帧动画
4. 使用 Cloner/Effector 批量生成对象并添加动态效果
5. 通过 Material Designer 调整材质参数
6. 使用 MRQ 进行最终渲染输出

## C++ 用法

### 头文件引入

```cpp
#include "AvalancheInteractiveToolsRuntimeModule.h"
#include "IAvaInteractiveToolsModeDetailsObjectProvider.h"
#include "IAvaInteractiveToolsModeDetailsObject.h"
```

### 基本用法：实现工具细节面板提供者

当自定义交互式工具需要在 Motion Design 模式下显示专属属性面板时，实现此接口：

```cpp
// Source: Source/AvalancheInteractiveToolsRuntime/Public/IAvaInteractiveToolsModeDetailsObjectProvider.h

#include "IAvaInteractiveToolsModeDetailsObjectProvider.h"
#include "IAvaInteractiveToolsModeDetailsObject.h"

UCLASS()
class UMyCustomToolDetails : public UObject, public IAvaInteractiveToolsModeDetailsObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Tool Settings")
    float Intensity = 1.0f;

    UPROPERTY(EditAnywhere, Category = "Tool Settings")
    bool bEnabled = true;
};

UCLASS()
class UMyInteractiveTool : public UObject, public IAvaInteractiveToolsModeDetailsObjectProvider
{
    GENERATED_BODY()

public:
    // 实现 GetModeDetailsObject，返回工具的细节面板数据对象
    UObject* GetModeDetailsObject_Implementation() const override
    {
        return DetailsObject;
    }

    UPROPERTY()
    UMyCustomToolDetails* DetailsObject;
};
```

### 进阶用法：自定义 Motion Design 交互工具

```cpp
// 创建自定义交互工具并将其集成到 Motion Design 模式

UCLASS()
class UMyMotionDesignToolBuilder : public UInteractiveToolBuilder
{
    GENERATED_BODY()

public:
    virtual bool CanBuildTool(const FToolBuilderState& SceneState) const override
    {
        return true;
    }

    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override
    {
        UMyMotionDesignTool* Tool = NewObject<UMyMotionDesignTool>(SceneState.ToolManager);
        Tool->SetTargetScene(SceneState);
        return Tool;
    }
};

UCLASS()
class UMyMotionDesignTool : public UInteractiveTool, public IAvaInteractiveToolsModeDetailsObjectProvider
{
    GENERATED_BODY()

public:
    virtual void Setup() override;
    virtual void Shutdown(EToolShutdownType ShutdownType) override;
    virtual void Render(IToolsContextRenderAPI* RenderAPI) override;

    // 提供细节面板对象，Motion Design 模式会自动显示
    virtual UObject* GetModeDetailsObject_Implementation() const override
    {
        return this;
    }

    UPROPERTY(EditAnywhere, Category = "Motion Design Tool")
    float EffectRadius = 100.0f;

    UPROPERTY(EditAnywhere, Category = "Motion Design Tool")
    FLinearColor EffectColor = FLinearColor::White;
};
```

## Demo 示例

> 由于 Motion Design 主要通过编辑器 UI 面板操作，以下展示如何在 C++ 中创建一个集成到 Motion Design 模式的自定义工具对象：

```cpp
// MyMotionDesignActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IAvaInteractiveToolsModeDetailsObjectProvider.h"
#include "IAvaInteractiveToolsModeDetailsObject.h"
#include "MyMotionDesignActor.generated.h"

UCLASS(BlueprintType)
class UMotionDesignActorSettings : public UObject, public IAvaInteractiveToolsModeDetailsObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Motion Design")
    FText DisplayText;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Motion Design")
    float FontSize = 72.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Motion Design|Animation")
    bool bAnimate = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Motion Design|Animation")
    float AnimationSpeed = 1.0f;
};

UCLASS(BlueprintType)
class AMyMotionDesignActor : public AActor, public IAvaInteractiveToolsModeDetailsObjectProvider
{
    GENERATED_BODY()

public:
    AMyMotionDesignActor();

    virtual UObject* GetModeDetailsObject_Implementation() const override
    {
        return Settings;
    }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Motion Design")
    UMotionDesignActorSettings* Settings;
};
```

```cpp
// MyMotionDesignActor.cpp
#include "MyMotionDesignActor.h"

AMyMotionDesignActor::AMyMotionDesignActor()
{
    PrimaryActorTick.bCanEverTick = true;

    Settings = CreateDefaultSubobject<UMotionDesignActorSettings>(TEXT("Settings"));
    Settings->DisplayText = FText::FromString(TEXT("Motion Design"));
    Settings->FontSize = 72.0f;
    Settings->bAnimate = true;
    Settings->AnimationSpeed = 1.0f;
}
```

## 模块依赖

Motion Design 依赖以下外部插件（非标准模块依赖）：

| 模块/插件 | 用途 |
|---|---|
| `AdvancedRenamer` | 批量重命名工具 |
| `CustomDetailsView` | 自定义细节面板视图 |
| `DynamicMaterial` | 动态材质系统 |
| `GeometryCache` | 几何缓存支持 |
| `GeometryScripting` | 几何脚本工具 |
| `MediaCompositing` | 媒体合成管线 |
| `MediaIOFramework` | 媒体 I/O 框架 |
| `MeshModelingToolsetExp` | 网格建模工具集 |
| `RemoteControl` | 远程控制系统 |
| `SVGImporter` | SVG 矢量图导入 |
| `Text3D` | 3D 文字渲染 |
| `ActorModifierCore` | Actor 修改器核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲视图标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为 Rundown 页面设置添加 MRQ 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 播控工具栏新增页面加载选项（全部/下一个/已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口客户端关联/解除关联的通知机制 |

### 维护评价

- **活跃维护**：Motion Design 是 Epic Games 官方维护的核心虚拟制片工具，近期（2026年5月）持续有功能性更新
- **开发强度高**：包含 43 个模块、2060 个源文件，是 UE5 中规模最大的插件之一
- **从 Experimental 正式毕业**：2025年5月从 Experimental 迁移到 VirtualProduction 目录，标志着正式稳定版发布
- **推荐使用**：适合所有虚拟制片和广播动态图形制作场景。由于是 Epic 官方维护且持续活跃更新，生产环境可放心使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/Avalanche/index.html)