# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 玩法摄像机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、资产定义、调试面板） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

Gameplay Cameras 是一个全新的、模块化且以数据驱动的摄像机系统，旨在彻底取代 Unreal Engine 传统的基于 `UCameraComponent` 和 `UCameraShake` 的摄像机系统。它的核心思想是将摄像机的**行为逻辑（节点图）** 与**数据配置（资产）** 分离。开发者和设计师可以通过创建 `CameraAsset`（定义摄像机行为树）和 `CameraRigAsset`（定义具体的摄像机操作，如跟随、瞄准）等资产，以可视化、非代码的方式构建复杂的摄像机行为，并能在运行时动态切换和混合。它解决了传统摄像机系统在面对复杂、动态的游戏玩法（如大型开放世界、角色能力多样的动作游戏）时，代码难以维护和扩展的问题。

## 使用场景

-   你的游戏需要在不同的游戏状态（如探索、战斗、过场动画）之间无缝切换摄像机行为。
-   你需要策划能够通过编辑器资产而非修改代码来调整和实验摄像机参数（如弹簧臂长度、摇晃幅度、混合时间）。
-   你的项目需要一个可复用、可组合的摄像机行为库（例如，“标准第三人称跟随摄像机”、“瞄准过肩摄像机”、“载具摄像机”都可以定义为独立的 `CameraRig` 资产）。
-   你需要在 Sequencer 中对摄像机的行为参数进行精确的动画控制。

## 蓝图用法

*注意：当前提供的源码信息主要来自编辑器模块 (`GameplayCamerasEditor`)，运行时模块 (`GameplayCameras`) 的蓝图 API（如 `UCameraComponent` 相关的节点）未在提供的头文件中完整体现。以下为基于编辑器模块推断的、主要在编辑器工具或运行时逻辑中可能涉及的蓝图交互点。*

### 核心节点（编辑器/资产创建相关）

由于提供的头文件主要是编辑器基础设施（工厂、资产定义），典型的蓝图节点将围绕资产创建和引用。运行时蓝图节点（如`Get Camera Variable`, `Set Camera Variable`)很可能存在于`GameplayCameras`模块中。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建摄像机资产 (Create Camera Asset)` | 工厂类，用于在编辑器中创建新的 `UCameraAsset` 资产。 | `UCameraAssetFactory` |
| `创建摄像机装备资产 (Create Camera Rig Asset)` | 工厂类，用于创建新的 `UCameraRigAsset` 资产。 | `UCameraRigAssetFactory` |
| `创建摄像机变量集合 (Create Camera Variable Collection)` | 工厂类，用于创建 `UCameraVariableCollection` 资产，用于管理一组摄像机变量。 | `UCameraVariableCollectionFactory` |

### 使用示例（蓝图描述）

1.  **在编辑器内容浏览器中创建资产**：右键 -> 资产 -> 摄像机 -> 选择“摄像机资产”、“摄像机装备资产”等。这会调用上述工厂类，创建出对应的 UObject 资产。
2.  **在 Sequencer 中控制摄像机**：添加 `UGameplayCameraComponentBase` 到 Actor 上后，在 Sequencer 轨道编辑器中，可以为该组件的特定参数（如蓝图中暴露的、或通过节点图定义的参数）添加关键帧动画。这涉及到 `FGameplayCameraComponentTrackEditor` 类。

## C++ 用法

### 头文件引入

对于运行时集成（使用摄像机组件和变量）：
```cpp
#include "GameplayCameras.h" // 或更具体的头文件，如 “Components/GameplayCameraComponent.h”
```

对于编辑器扩展（自定义资产、节点、调试工具）：
```cpp
#include "GameplayCamerasEditor.h"
```

### 基本用法（编辑器扩展 - 自定义资产定义）

你可以为自定义的摄像机资产类型创建专门的编辑器定义。

```cpp
// 假设你定义了一个继承自 UCameraAsset 的自定义资产 UMyCameraAsset
// 头文件：AssetDefinition_MyCameraAsset.h
#include "Core/CameraAsset.h"
#include "AssetDefinitionDefault.h"
#include "AssetDefinition_MyCameraAsset.generated.h"

UCLASS()
class UAssetDefinition_MyCameraAsset : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    // 定义在内容浏览器中显示的名称
    virtual FText GetAssetDisplayName() const override { return NSLOCTEXT("AssetTypeActions", "AssetTypeActions_MyCamera", "我的摄像机资产"); }
    // 定义资产图标颜色
    virtual FLinearColor GetAssetColor() const override { return FLinearColor::Red; }
    // 关联资产类
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    // 定义资产分类路径（如“摄像机/我的分类”）
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    // 其他接口实现...
};
```
*来源：参考 `Private/AssetTools/AssetDefinition_CameraAsset.h` 的结构。*

### 进阶用法（编辑器扩展 - 自定义调试面板）

你可以为你的自定义摄像机功能创建调试面板。

```cpp
// 头文件：SCustomCameraDebugPanel.h
#include "Widgets/SCompoundWidget.h"

namespace UE::Cameras // 建议保持在UE::Cameras命名空间下以保持一致性
{

class SCustomCameraDebugPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SCustomCameraDebugPanel) {}
    SLATE_END_ARGS();

    void Construct(const FArguments& InArgs)
    {
        ChildSlot
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("我的自定义摄像机调试信息")))
        ];
    }
};

} // namespace UE::Cameras
```
*来源：参考 `Private/Debugger/SCameraNodeTreeDebugPanel.h` 等调试面板的结构。*

## Demo 示例

以下是一个极简的、概念性的示例，展示如何在 C++ 中定义一个基本的摄像机节点（运行时逻辑单元）。**注意：此示例是推断性的，具体基类和接口需要参考 `GameplayCameras` 模块的实际头文件。**

```cpp
// MyCameraNode.h
#pragma once

#include "Core/CameraNode.h" // 假设的基类头文件
#include "MyCameraNode.generated.h"

UCLASS()
class UMyCameraNode : public UCameraNode // 假设的基类
{
    GENERATED_BODY()

public:
    UMyCameraNode();

    // 定义一个可被其他节点或变量引用的输出参数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Camera")
    float CustomOffset = 100.0f;

    // 核心评估函数，计算并设置摄像机姿态
    virtual void EvaluateCamera(float DeltaTime, struct FCameraNodeEvaluationResult& OutResult) override
    {
        // 基础的逻辑：在默认姿态上应用一个自定义偏移
        FCameraPose& Pose = OutResult.CameraPose;
        Pose.Location.Z += CustomOffset;
    }

protected:
    // 定义此节点接收的输入引脚（从其他节点或变量接收数据）
    virtual void GetInputs(FCameraNodeInputs& Inputs) override
    {
        // 例如，可以接收一个位置偏移量输入
        Inputs.AddVectorInput("OffsetInput");
    }
};

// MyCameraNode.cpp
#include "MyCameraNode.h"

UMyCameraNode::UMyCameraNode()
{
    // 设置节点在编辑器图表中的显示标题
    NodeTitle = NSLOCTEXT("CameraNode", "MyCameraNode", "自定义摄像机节点");
}
```
**构建说明**：将此 `.h` 和 `.cpp` 文件放入你的项目模块或 `GameplayCameras` 模块源码目录中。在 `Build.cs` 文件中，你需要依赖 `GameplayCameras` 模块。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 插件的核心运行时逻辑、摄像机组件、资产和评估系统。你的项目模块需要依赖它来使用摄像机功能。 |
| `GameplayCamerasEditor` | 插件的编辑器集成，包括资产定义、工厂、自定义编辑器、调试工具和 Sequencer 轨道编辑器。 |
| `GameplayCamerasUncookedOnly` | 包含仅在编辑器中未打包状态下使用的功能，可能用于资产验证或特殊的编辑器蓝图节点。 |

## 维护状态

### 近期更新

```
- 2026-04-14 35e60df1 将UE_LOG迁移到UE_LOGF，日志基础设施更新。
- 2026-04-13 6f1ea925 状态树：更新了状态树引用结构的详细信息，以显示结构的显示名称而非类型名。
- 2026-04-08 81eea83d [内容浏览器] 新的“添加”菜单中的“Gameplay”分类菜单。
- 2026-03-03 76a32825 [后处理] 将FilmGrainTexelSize替换为float2 FilmGrainScale，允许缩放噪声纹理。
- 2026-03-03 ea1a72ff 摄像机：使播放模式仅影响GPC组件是否写入输出组件。
```

### 维护评价

**活跃维护**。该插件创建于约1年前，正处于早期但积极的开发阶段。从最近的提交记录可以看出，开发团队正在持续进行功能完善（如状态树集成、内容浏览器菜单优化）、底层重构（日志系统迁移）和引擎集成改进（后处理、播放模式）。虽然标记为实验性 (`IsExperimentalVersion=true`)，但这表明它是一个正在快速迭代的新系统，而非被遗弃的代码。**强烈推荐**对现代化、数据驱动摄像机系统有需求的项目关注和试用，但需注意其API可能随版本更新而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras/Tests) *(路径为推断，可能存在)*