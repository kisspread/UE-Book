# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动效设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、媒体合成相关资产） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Editor), `AvalancheMedia` (Runtime), `AvalancheSequence` (Runtime), `AvalancheText` (Runtime), `AvalancheShapes` (Runtime), `AvalancheOutliner` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheModifiers` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMediaEditor` (Editor), `AvalancheSVGEditor` (Editor), `AvalancheShapesEditor` (Editor), `AvalancheTextEditor` (Editor), `AvalancheModifiersEditor` (Editor), `AvalanchePropertyAnimatorEditor` (Editor), `AvalancheRemoteControlEditor` (Editor), `AvalancheMRQEditor` (Editor) ... 等共44个模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design (Avalanche) 是一个专注于虚拟制作（Virtual Production）场景下**实时动态图形（Motion Graphics）和广播图形**设计与播放的综合工具集。它并非简单的单一功能插件，而是一个庞大的、模块化的框架，旨在提供从素材导入、图形设计、属性动画、场景编排到最终渲染和远程控制的**全流程解决方案**。

该插件解决的核心问题是：如何在虚幻引擎中高效地创建、管理和播出电视节目、实况转播、虚拟演播室中所需的复杂动态叠加图形（Lower Thirds、标题、过渡、数据驱动图形等），并实现与广播设备（如视频服务器、切换台）的深度集成。

## 使用场景

-   你在制作一档电视新闻或体育直播的虚拟演播室，需要实时叠加选手数据、比分和动态标题条 → 用 **Avalanche** + **AvalancheMedia** + **AvalancheRemoteControl**。
-   你需要为一场大型活动（如颁奖典礼）设计复杂的场景过渡、灯光效果和粒子动画，并希望设计师能在引擎内直接调整 → 用 **Avalanche** + **AvalancheSequence** + **AvalancheModifiers** + **AvalanchePropertyAnimator**。
-   你负责一个虚拟广告牌网络，需要通过数据接口（如JSON）动态更新图形内容 → 用 **Avalanche** + **AvalancheRemoteControl** + **AvalancheSceneTree**。
-   你需要将设计好的动效序列通过Movie Render Queue (MRQ) 高质量渲染为视频文件用于后期 → 用 **AvalancheMRQ**。

## 蓝图用法

由于Avalanche是一个包含44个模块的超大插件，其蓝图API非常庞大且分布在各个子模块中。核心的`AvalancheCore`模块提供了基础的类型系统和工具类，更具体的蓝图节点（如创建形状、应用效果器、控制媒体输出）需在对应的子模块（如`AvalancheShapes`, `AvalancheEffectors`, `AvalancheMedia`）中查找。

### 核心节点（基于源码分析）

在提供的`AvalancheCore`源码中，没有直接暴露的`BlueprintCallable`函数。其主要贡献是底层C++框架（类型系统、数据视图）。实际可用的蓝图节点存在于其他子模块。

**通常子模块可能提供的蓝图节点示例（需查阅对应模块源码）：**

| 节点 | 说明 | 所在模块 |
|---|---|---|
| `Create Avalanche Text Actor` | 在场景中创建一个可配置的3D文本动效演员 | `AvalancheText` |
| `Apply Effector` | 对一组几何体应用克隆或变形效果 | `AvalancheEffectors` |
| `Set Media Output` | 配置一个媒体输出通道，用于播放合成结果 | `AvalancheMedia` |
| `Play/Stop Sequence` | 控制一个Avalanche动效序列的播放 | `AvalancheSequence` |
| `Animate Material Parameter` | 通过蓝图控制材质参数的动画 | `AvalancheMaterial` |

### 使用示例（概念描述）

1.  **设计阶段**：使用 `AvalancheOutliner` 和 `AvalancheSceneTree` 面板组织和管理你的动效场景元素。
2.  **创建内容**：从内容浏览器拖拽 `AvalancheText`、`AvalancheShapes` 资产到场景，或使用 `AvalancheSVGEditor` 导入矢量图形。
3.  **动画制作**：使用 `AvalancheSequence` 创建时间线，为演员的变换、材质参数等关键帧。
4.  **渲染输出**：配置 `AvalancheMRQ` 模块，设置渲染输出路径和格式，然后通过 Movie Render Queue 面板进行高质量渲染。
5.  **实时控制**：在直播时，通过 `AvalancheRemoteControl` 模块暴露的API，从外部设备或应用程序控制场景中的参数。

## C++ 用法

### 头文件引入

根据所需功能，引入对应子模块的头文件。
```cpp
// 核心类型系统
#include "AvaType.h"
#include "AvaDataView.h"
#include "AvaTypeConcepts.h"

// 其他功能模块 (示例)
#include "AvalancheSequenceTypes.h"
#include "AvalancheOutlinerTypes.h"
```

### 基本用法：Avalanche 类型系统 (AvaType)

`AvalancheCore` 定义了一套自有的类型系统（`FAvaTypeId`, `IAvaTypeCastable`），用于在插件内部进行类型识别和转换，独立于UObject系统。
**来源文件: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCore/Public/AvaType.h`**

```cpp
// 定义一个继承自 IAvaTypeCastable 的类型
class FMyMotionDesignObject : public IAvaTypeCastable
{
public:
    // 声明类型信息：FMyMotionDesignObject 继承自 IAvaTypeCastable
    UE_AVA_INHERITS(FMyMotionDesignObject, IAvaTypeCastable)

    // ... 其他成员和方法
};

// 使用
void Example(const FMyMotionDesignObject& Obj)
{
    // 类型检查
    if (Obj.IsA<IAvaTypeCastable>())
    {
        // 类型转换
        if (const IAvaTypeCastable* Base = Obj.CastTo<IAvaTypeCastable>())
        {
            // 使用 Base...
        }
    }
}
```

### 进阶用法：数据视图 (FDataView)

`FDataView` 是一个轻量级、非拥有式的对象/结构体指针包装器，用于在框架内部传递数据。
**来源文件: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCore/Public/AvaDataView.h`**

```cpp
#include "AvaDataView.h"

struct FMyAnimData
{
    float Alpha;
    FVector Location;
};

// 创建一个指向 FMyAnimData 的视图
FMyAnimData AnimData = {0.5f, FVector(10, 20, 30)};
UE::Ava::FDataView DataView(FMyAnimData::StaticStruct(), &AnimData);

// 通过视图安全地访问数据
if (DataView.IsValidFor<FMyAnimData>())
{
    FMyAnimData& MutableData = DataView.GetMutable<FMyAnimData>();
    MutableData.Alpha = 0.7f;
}

// 传递视图到其他系统
void ProcessAnimData(const UE::Ava::FDataView& Data)
{
    if (Data.IsValid())
    {
        // 处理数据...
    }
}
```

## Demo 示例

以下是一个定义自定义Avalanche类型并在简单场景中使用的最小C++示例。

**MyAvalancheActor.h**
```cpp
#pragma once

#include "AvaType.h"
#include "GameFramework/Actor.h"
#include "MyAvalancheActor.generated.h"

UCLASS(BlueprintType)
class AMyAvalancheActor : public AActor
{
    GENERATED_BODY()

public:
    // 在UObject派生类中使用AvaType系统
    UE_AVA_TYPE(AMyAvalancheActor)

    // 一个简单的测试函数
    UFUNCTION(BlueprintCallable, Category = "Avalanche Demo")
    void TestAvaTypeCast();
};
```

**MyAvalancheActor.cpp**
```cpp
#include "MyAvalancheActor.h"
#include "AvaTypeCastable.h" // 假设IAvaTypeCastable在此

// 示例：一个同时继承AActor和IAvaTypeCastable的类型
class FMyAvalancheComponentData : public IAvaTypeCastable
{
public:
    UE_AVA_INHERITS(FMyAvalancheComponentData, IAvaTypeCastable)

    float Value = 42.0f;
};

void AMyAvalancheActor::TestAvaTypeCast()
{
    // 创建一个Avalanche类型实例
    FMyAvalancheComponentData ComponentData;

    // 使用类型系统进行检查
    if (ComponentData.IsA<IAvaTypeCastable>())
    {
        UE_LOG(LogTemp, Log, TEXT("ComponentData is castable as IAvaTypeCastable."));
    }

    // 获取类型ID
    FAvaTypeId TypeId = TAvaType<FMyAvalancheComponentData>::GetTypeId();
    UE_LOG(LogTemp, Log, TEXT("Type ID: %s"), *TypeId.ToString());
}
```

## 模块依赖

从插件描述和模块命名可知，Avalanche依赖于大量其他UE插件/模块。以下是其独特的、不常见的依赖：

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | 用于批量重命名资产 |
| `CustomDetailsView` | 提供高度自定义的细节面板 |
| `DynamicMaterial` | 动态材质创建与编辑 |
| `GeometryCache` | 处理几何体缓存数据 |
| `GeometryScripting` | 通过蓝图或脚本操作几何体 |
| `MediaCompositing` | 媒体合成框架 |
| `MediaIOFramework` | 媒体输入输出框架 |
| `MeshModelingToolsetExp` | 实验性网格建模工具集 |
| `RemoteControl` | 远程控制面板与API |
| `SVGImporter` | SVG矢量图形导入 |
| `Text3D` | 3D文本生成 |
| `ActorModifierCore` | Actor修改器核心框架 |
| `ClonerEffector` | 克隆器和效果器系统 |
| `PropertyAnimatorCore` | 属性动画核心系统 |

## 维护状态

### 近期更新

从提供的git日志看，插件非常活跃，有密集的功能更新。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将动效设计相关面板（场景设置、大纲视图）整合到其专属编辑器分组中，优化工作流。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用“节目单页面”设置时的Movie Render Queue添加了分析数据。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加了页面加载选项（全部、下一个、已选），并增加了相关设置。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用Text3D和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口代码，通过通知客户端其关联状态来减少重复代码。 |

### 维护评价

**综合评价：活跃维护，处于积极开发期。**

-   **创建时间**：2025年5月从Experimental目录迁移至VirtualProduction，标志着其正式化。
-   **更新频率**：最近一次更新在2026年5月，距今不到1年，且更新内容密集，全是功能性新增和优化。
-   **维护状态**：**非常活跃**。Epic Games显然将其作为虚拟制作管线的核心组件在持续投入开发。
-   **已知问题/限制**：作为大型框架，学习曲线较陡，且部分模块可能仍标记为实验性（如依赖项`MeshModelingToolset Exp`）。模块化设计也意味着需要正确理解和使用众多子模块。
-   **推荐使用**：**强烈推荐**给需要在UE中进行专业级实时图形和广播制作的团队和个人。这是一个强大且官方维护的工具链。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
-   [官方文档] (暂无链接，通常需查阅 Epic 官方文档站或学习中心)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCore/Private/Tests/AvaTypeTest.h) (示例)