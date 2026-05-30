# Motion Design Scene State

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 动效场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器扩展） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 是为 **Motion Design（动效设计）** 工作流打造的场景状态管理系统。它提供了以下核心能力：

- **场景状态机（Scene State Machine）**：类似蓝图中的状态机，但专门用于管理 Motion Design 场景中对象的状态转换。通过状态机，可以定义场景中各元素在不同阶段的行为。
- **事件系统（Event System）**：提供结构化的事件定义与分发机制。通过 `EventSchemaCollection` 管理事件模式，支持用户自定义结构体作为事件载荷（payload），实现事件驱动的场景控制。
- **数据绑定（Data Binding）**：将场景状态与场景对象属性进行绑定，使状态变化能自动驱动对象属性更新。
- **游戏玩法集成（Gameplay Integration）**：将场景状态系统与游戏玩法系统对接，支持在游戏运行时使用场景状态。

该插件从 Experimental 分支迁移至 Virtual Production，是 Epic Motion Design 工具链的核心组件，用于在虚拟制作场景中实现复杂的、事件驱动的状态管理。

## 使用场景

- 你在做 Motion Design / 虚拟制作项目，需要管理场景中多个元素的状态转换 → 用 SceneState
- 你需要定义结构化的事件模式（如"播放开始"、"场景切换"等），并让场景对象响应这些事件 → 用 SceneState 的事件系统
- 你需要将场景状态变化自动映射到对象属性上，实现状态驱动的动画控制 → 用 SceneState 的数据绑定功能
- 你在开发交互式虚拟制作体验，需要状态机来控制场景流程 → 用 SceneState 状态机

## 蓝图用法

> **注意**：本模块（SceneStateEventEditor）是编辑器模块，主要提供属性编辑器自定义和资产工厂，不直接暴露蓝图节点。蓝图可调用的 API 位于其他子模块（如 SceneStateBlueprint、SceneStateGameplay）。以下列出本模块暴露的编辑器侧核心功能。

### 编辑器自定义

| 自定义项 | 说明 | 所在类 |
|---|---|---|
| 事件模式集合属性面板 | 自定义事件模式集合资产的详情面板 | `FEventSchemaCollectionCustomization` |
| 事件模板属性 | 自定义事件模板结构体的属性显示 | `FEventTemplateCustomization` |
| 事件模式句柄属性 | 自定义事件模式句柄（Handle）的属性显示 | `FEventSchemaHandleCustomization` |
| 事件处理器属性 | 自定义事件处理器的属性显示 | `FEventHandlerCustomization` |
| 事件模式选择器 | 提供选择事件模式集合及其中模式的组合控件 | `SEventSchemaPicker` |

### 资产创建

| 工厂 | 说明 | 所在类 |
|---|---|---|
| 事件模式集合工厂 | 在内容浏览器中创建新的事件模式集合资产 | `USceneStateEventSchemaCollectionFactory` |

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateEventEditorModule.h"
#include "SceneStateEventEditorUtils.h"
```

### 基本用法

```cpp
// 在事件模式中创建和删除变量
// 来源: Source/SceneStateEventEditor/Private/SceneStateEventEditorUtils.h

#include "SceneStateEventEditorUtils.h"

// 获取一个事件模式对象（通常通过资产系统获取）
USceneStateEventSchemaObject* EventSchema = GetMyEventSchema();

// 创建一个新的布尔变量（如果事件模式的结构体为空，会先创建结构体）
bool bSuccess = UE::SceneState::Editor::CreateVariable(EventSchema);

// 根据 FieldId 移除变量（如果是最后一个变量，结构体会被删除）
FGuid FieldId = GetTargetFieldId();
UE::SceneState::Editor::RemoveVariable(EventSchema, FieldId);
```

### 进阶用法：自定义事件模式属性面板节点构建器

```cpp
// 使用 FEventSchemaFieldNodeBuilder 自定义单个字段的显示
// 来源: Source/SceneStateEventEditor/Private/DetailsView/SceneStateEventSchemaFieldNodeBuilder.h

#include "SceneStateEventSchemaFieldNodeBuilder.h"

// 创建字段节点构建器
TSharedRef<IPropertyHandle> SchemaHandle = /* 获取属性句柄 */;
FGuid FieldId = /* 字段 ID */;

auto FieldBuilder = MakeShared<UE::SceneState::Editor::FEventSchemaFieldNodeBuilder>(SchemaHandle, FieldId);

// 设置兄弟节点重建回调（当需要刷新相邻字段时）
FieldBuilder->SetOnRebuildSiblings(FSimpleDelegate::CreateLambda([]()
{
    // 刷新布局
}));

// 获取当前字段的显示名
FText DisplayName = FieldBuilder->GetFieldDisplayName();

// 获取当前字段的引脚类型信息
FEdGraphPinType PinInfo = FieldBuilder->OnGetPinInfo();
```

## Demo 示例

```cpp
// MyEventSchemaWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class IPropertyHandle;
class USceneStateEventSchemaObject;

namespace UE::SceneState::Editor
{

/** 示例：创建一个显示事件模式信息的简单控件 */
class SMyEventSchemaInfo : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyEventSchemaInfo) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, const TSharedRef<IPropertyHandle>& InSchemaHandle);

private:
    /** 获取事件模式对象 */
    USceneStateEventSchemaObject* GetEventSchema() const;

    /** 获取模式名称 */
    FText GetSchemaName() const;

    TSharedRef<IPropertyHandle> SchemaHandle;
};

} // UE::SceneState::Editor
```

```cpp
// MyEventSchemaWidget.cpp
#include "MyEventSchemaWidget.h"
#include "SceneStateEventEditorUtils.h"
#include "SceneState/SceneStateEventSchemaObject.h"
#include "PropertyHandle.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBox.h"

namespace UE::SceneState::Editor
{

void SMyEventSchemaInfo::Construct(
    const FArguments& InArgs,
    const TSharedRef<IPropertyHandle>& InSchemaHandle)
{
    SchemaHandle = InSchemaHandle;

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.f)
        [
            SNew(STextBlock)
            .Text_Lambda([this]() { return GetSchemaName(); })
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.f)
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("Add Variable")))
            .OnClicked_Lambda([this]() -> FReply
            {
                USceneStateEventSchemaObject* Schema = GetEventSchema();
                if (Schema)
                {
                    UE::SceneState::Editor::CreateVariable(Schema);
                }
                return FReply::Handled();
            })
        ]
    ];
}

USceneStateEventSchemaObject* SMyEventSchemaInfo::GetEventSchema() const
{
    // 从属性句柄获取事件模式对象
    UObject* Object = nullptr;
    if (SchemaHandle->GetValue(Object) == FPropertyAccess::Success)
    {
        return Cast<USceneStateEventSchemaObject>(Object);
    }
    return nullptr;
}

FText SMyEventSchemaInfo::GetSchemaName() const
{
    USceneStateEventSchemaObject* Schema = GetEventSchema();
    if (Schema)
    {
        return FText::FromString(Schema->GetName());
    }
    return FText::FromString(TEXT("No Schema"));
}

} // UE::SceneState::Editor
```

## 模块依赖

本模块（SceneStateEventEditor）的 Build.cs 依赖关系：

| 模块 | 用途 |
|---|---|
| `SceneStateEvent` | 事件系统运行时模块，提供事件模式对象和事件定义 |
| `SceneStateEditor` | 场景状态编辑器基础模块，提供编辑器公共工具 |
| `AssetDefinition` | 资产定义框架，用于在内容浏览器中展示和操作资产 |
| `EditorFramework` | 编辑器框架，提供编辑器扩展基础设施 |

> 由于源码截断，完整依赖列表可能包含更多模块。如果要使用完整插件功能，建议同时启用所有 14 个子模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：客户端关联/取消关联通知机制优化 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退 CL53913857 的变更 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构相关变更 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复绑定未检查空事件载荷结构体的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移至 UE_LOGF 宏 |

### 维护评价

- **创建时间**：2025 年 8 月，至今约 1 年
- **活跃度**：活跃维护中。2026 年仍有实质性功能更新和 bug 修复（如事件载荷空指针检查）
- **状态**：`IsBetaVersion = true`，从 Experimental 迁移到 Virtual Production，说明正在从实验阶段向正式发布推进
- **模块规模**：14 个子模块、424 个源文件，是一个大型且仍在扩展中的插件
- **推荐程度**：适合在 Motion Design / 虚拟制作项目中试用。由于仍标记为 Beta，生产环境使用需谨慎，关注后续正式发布版本

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：暂无（.uplugin 未提供 DocsURL）