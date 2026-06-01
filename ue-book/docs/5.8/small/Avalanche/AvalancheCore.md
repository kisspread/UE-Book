# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheText` (Runtime), `AvalancheMask` (Runtime), `AvalancheModifiers` (Runtime), + 34 more (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（原 Avalanche）是 UE5 面向虚拟制作（Virtual Production）的综合性运动设计工具集。它提供了一套完整的 2D/3D 合成、设计和广播流程，覆盖从内容创作到播出控制的全链路：

- **合成与设计**：提供基于场景树的节点化设计工作流，支持形状（Shapes）、文本（Text3D）、材质（Material Designer）、遮罩（Geometry Mask）等视觉元素的组合与编辑
- **克隆与效果器**：通过 ClonerEffector 实现阵列化运动效果，支持 Property Animator 做属性动画
- **媒体合成**：集成 Media Compositing 框架，支持视频/图像的实时合成
- **播出控制**：提供 Rundown Page、Show Control 工具栏、Scene Rig 等广播级播出管理能力
- **渲染输出**：集成 Movie Render Queue（MRQ）进行高质量离线渲染
- **远程控制**：通过 Remote Control 面板实现远程参数操控

该插件从 2025 年 5 月由 `Experimental` 迁移到 `VirtualProduction` 分类，表明已达到生产可用状态。它依赖大量辅助插件（Advanced Renamer、Dynamic Material、SVG Importer 等），形成一个庞大的虚拟制作生态系统。

## 使用场景

- 你在制作电视节目或直播的实时图形（lower thirds、全屏动画）→ 使用 Motion Design 的 Show Control 和 Rundown
- 你需要创建复杂的阵列化运动效果（粒子风、重复动画）→ 使用 ClonerEffector
- 你要做 2.5D 合成，将视频和 3D 图形混合输出 → 使用 Media Compositing 集成
- 你需要为 LED 墙或虚拟场景设计动态背景 → 使用 Shape + Text + Material Designer 组合
- 你要在 Sequencer 中做精确的属性动画 → 使用 Property Animator + Sequencer 集成
- 你需要批量管理场景中的 Actor 修改器 → 使用 ActorModifier/ActorModifierCore

## 蓝图用法

Motion Design 主要面向编辑器工作流，运行时蓝图 API 集中在场景管理和效果器系统中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetWorldSubsystem` | 获取指定类型的 World 子系统，带安全校验 | `FAvaWorldSubsystemUtils` |
| `SupportsWorldType` | 检查当前 World 是否支持指定子系统 | `TAvaWorldSubsystemInterface` |

### 使用示例（蓝图描述）

由于 Motion Design 的核心功能通过编辑器工具面板操作（如 Outliner、Scene Settings、Show Control Toolbar），运行时蓝图交互较少。主要使用方式为：

1. 在编辑器中通过 **Motion Design 选项卡** 打开设计界面
2. 使用 **Scene Tree** 面板组织视觉元素层次
3. 通过 **Show Control** 面板控制页面切换和播出

## C++ 用法

AvalancheCore 模块是整个 Motion Design 插件的基础框架，提供自定义类型系统、数据视图和属性工具。

### 头文件引入

```cpp
#include "AvaType.h"
#include "AvaTypeId.h"
#include "AvaDataView.h"
#include "AvaField.h"
#include "AvaPropertyChangeDispatcher.h"
```

### 基本用法 — 自定义类型系统

Motion Design 实现了一套独立于 UObject 的轻量级类型系统，支持运行时类型识别（RTTI）和类型转换。这在处理非 UObject 的值类型时非常有用。

```cpp
// 来源: Private/Tests/AvaTypeTest.h
// 定义一个基础类型
struct ISuperType
{
    UE_AVA_TYPE(ISuperType);
};

// 派生类型，声明继承关系
struct FSuperTypeA : ISuperType
{
    UE_AVA_TYPE(FSuperTypeA, ISuperType)
};

// 实现 IAvaTypeCastable 接口以支持 IsA 和 CastTo
struct FTypeA : FSuperTypeA, IAvaTypeCastable
{
    UE_AVA_INHERITS(FTypeA, FSuperTypeA)
};

// 使用类型检查
FTypeA Instance;
if (Instance.IsA<ISuperType>())
{
    // true — FTypeA 继承自 ISuperType
}

if (Instance.IsExactlyA<FTypeA>())
{
    // true — 精确类型匹配
}

// 类型转换
const ISuperType* Base = &Instance;
const FTypeA* Derived = Base->CastTo<FTypeA>(); // 有效，因为运行时类型确实是 FTypeA
```

### 基本用法 — 外部类型支持

对于无法修改源码的类型（如引擎内置类型），可以使用 `UE_AVA_TYPE_EXTERNAL` 宏在外部注册类型信息：

```cpp
// 来源: Private/Tests/AvaTypeTest.h
struct IExternalType {};

// 在类外注册类型信息，无需修改原类定义
UE_AVA_TYPE_EXTERNAL(IExternalType);

struct FExternalTypeB : IExternalType {};
// 注册时指定继承关系
UE_AVA_TYPE_EXTERNAL(FExternalTypeB, IExternalType);
```

### 进阶用法 — DataView 与属性变更派发

DataView 提供了对 UObject 和 UStruct 的短期引用视图，避免持有强引用：

```cpp
// 来源: Public/AvaDataView.h

// 对 UObject 创建数据视图
UObject* MyObject = GetSomeObject();
UE::Ava::FDataView ObjectView(MyObject);

if (ObjectView.IsValid())
{
    if (ObjectView.IsValidFor<UMyClass>())
    {
        UMyClass* Typed = ObjectView.GetMutable<UMyClass>();
        // 安全地操作数据
    }
}

// 对 UStruct 创建数据视图
FMyStruct MyData;
UE::Ava::FDataView StructView(FMyStruct::StaticStruct(), &MyData);
```

属性变更派发器可简化 `PostEditChangeProperty` 的分发逻辑：

```cpp
// 来源: Public/AvaPropertyChangeDispatcher.h

class UMyActor : public AActor
{
    static TAvaPropertyChangeDispatcher<UMyActor> PropertyDispatcher;

    void PostEditChangeProperty(FPropertyChangedEvent& Event)
    {
        PropertyDispatcher.OnPropertyChanged(this, Event);
        Super::PostEditChangeProperty(Event);
    }

    void OnLocationChanged();
    void OnColorChanged();
};

// 在 .cpp 中注册
TAvaPropertyChangeDispatcher<UMyActor> UMyActor::PropertyDispatcher({
    { GET_MEMBER_NAME_CHECKED(UMyActor, Location), &UMyActor::OnLocationChanged },
    { GET_MEMBER_NAME_CHECKED(UMyActor, Color), &UMyActor::OnColorChanged },
});
```

## Demo 示例

一个完整的最小示例，展示如何定义自己的 Ava 类型并使用类型检查：

```cpp
// MyDesignElement.h
#pragma once
#include "AvaType.h"

class IMyDesignElement : public IAvaTypeCastable
{
    UE_AVA_INHERITS_WITH_SUPER(IMyDesignElement, IAvaTypeCastable)
};

class FMyTextElement : public IMyDesignElement
{
    UE_AVA_INHERITS_WITH_SUPER(FMyTextElement, IMyDesignElement)
public:
    FString Text;
};

class FMyShapeElement : public IMyDesignElement
{
    UE_AVA_INHERITS_WITH_SUPER(FMyShapeElement, IMyDesignElement)
public:
    int32 Sides = 4;
};
```

```cpp
// MyDesignElement.cpp
#include "MyDesignElement.h"

void ProcessElement(const IMyDesignElement* InElement)
{
    if (InElement->IsA<FMyTextElement>())
    {
        const FMyTextElement* TextEl = InElement->CastTo<FMyTextElement>();
        UE_LOG(LogTemp, Log, TEXT("Text: %s"), *TextEl->Text);
    }
    else if (InElement->IsA<FMyShapeElement>())
    {
        const FMyShapeElement* ShapeEl = InElement->CastTo<FMyShapeElement>();
        UE_LOG(LogTemp, Log, TEXT("Shape with %d sides"), ShapeEl->Sides);
    }
}

// 使用 TSharedPtr 进行安全类型转换
TSharedPtr<IAvaTypeCastable> ElementPtr = MakeShared<FMyTextElement>();
TSharedPtr<FMyTextElement> TextPtr = UE::AvaCore::CastSharedPtr<FMyTextElement>(ElementPtr);
```

## 模块依赖

Motion Design 依赖大量辅助插件。以下是该插件**独特**的、非标准的依赖：

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | Actor 批量重命名 |
| `CustomDetailsView` | 自定义 Details 面板 |
| `DynamicMaterial` | 动态材质系统 |
| `GeometryCache` | 几何缓存 |
| `GeometryScripting` | 几何脚本操作 |
| `MediaCompositing` | 媒体合成 |
| `MediaIOFramework` | 媒体 IO 框架 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验性） |
| `RemoteControl` | 远程控制 API |
| `SVGImporter` | SVG 文件导入 |
| `Text3D` | 3D 文本渲染 |
| `ActorModifierCore` | Actor 修改器核心框架 |
| `Sequencer` | 属性动画的序列器集成（AvalanchePropertyAnimator） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 面板从关卡编辑器分离到独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 新增 Rundown 页面使用 MRQ 渲染时的分析埋点 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | Show Control 工具栏新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口关联/脱离通知机制，消除重复代码 |

### 维护评价

**活跃维护中** ✅

Motion Design 是 Epic 官方重点维护的虚拟制作工具：

- **创建时间**：2025 年 5 月从 Experimental 迁移至 VirtualProduction，至今约 1 年
- **更新频率**：最近一周内有多次提交（2026-05-14 至 2026-05-20），更新极为活跃
- **更新内容**：涵盖功能新增（MRQ 分析、页面加载选项）、UI 优化（面板重组）、项目设置扩展（碰撞控制）等，属于积极的功能迭代
- **代码规模**：2060+ 源文件、42 个模块，是 UE5 中规模最大的插件之一
- **稳定性**：已脱离 Experimental 分类，达到生产可用标准

推荐在虚拟制作项目中使用。注意该插件依赖众多其他插件，需确保所有依赖可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCore/Private/Tests)