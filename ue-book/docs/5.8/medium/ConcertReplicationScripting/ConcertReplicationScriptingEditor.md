# Concert Replication Scripting

> Exposes Concert Replication types for scripting, e.g. in Blueprints（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 协奏复制脚本 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI控件、蓝图脚本桥接） |
| 模块 | `ConcertReplicationScripting` (Runtime), `ConcertReplicationScriptingEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-12-08 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting) | |

## 用途

这个插件的核心用途是为 Unreal Engine 的 **Concert 复制系统** 提供一个**易于使用的脚本化接口（主要面向蓝图）** 和配套的**编辑器UI**。

Concert 是 UE 的多人协作编辑框架，其复制系统允许在多用户会话中实时同步特定对象和属性的状态。然而，直接通过代码配置“哪些对象的哪些属性需要被复制”可能比较繁琐。本插件解决了这个问题：
1.  **脚本化接口**：通过 `IConcertReplicationScriptingBridge` 接口，暴露了一系列蓝图可调用的函数，让用户（或程序员）可以动态地在蓝图中添加、移除或查询需要复制的对象和属性。
2.  **编辑器UI**：提供了一套自定义的Slate控件（如属性选择器、属性链显示等）和属性自定义器。这些工具用于在编辑器（例如，在资产编辑器或自定义窗口中）可视化地选择和管理要复制的属性，提升了设计师和开发者的配置体验。

简而言之，它是连接 **Concert 强大复制功能** 与 **用户友好配置界面（蓝图/编辑器）** 之间的桥梁。

## 使用场景

-   你正在使用 Concert 进行多用户协作编辑，并且需要精细控制哪些对象的属性（如位置、旋转、特定参数）应该实时同步给其他参与者。
-   你需要创建一个蓝图或编辑器工具，允许用户在运行时或编辑时动态地选择要复制的资产和属性，而不是在硬编码中配置。
-   你想要为你的项目定制一个专属的复制管理界面，需要一套现成的、用于选择类和属性的UI组件。

## 蓝图用法

蓝图用法的核心是通过获取 `IConcertReplicationScriptingBridge` 接口实例来操作。

### 核心节点

假设 `UBlueprintConcertLibrary` 是一个假设的蓝图函数库类（或通过其他方式获取接口指针）。

| 节点 | 说明 | 所在类/接口 |
|---|---|---|
| `AddObjectProperties` | 为指定对象添加一系列要复制的属性。 | `IConcertReplicationScriptingBridge` |
| `RemoveObjectProperties` | 从指定对象移除一系列不再需要复制的属性。 | `IConcertReplicationScriptingBridge` |
| `QueryObjectProperties` | 查询指定对象当前已注册用于复制的属性列表。 | `IConcertReplicationScriptingBridge` |
| `AddObjects` | 注册一组对象参与复制。 | `IConcertReplicationScriptingBridge` |
| `RemoveObjects` | 注销一组对象不再参与复制。 | `IConcertReplicationScriptingBridge` |
| `QueryObjects` | 查询当前已注册用于复制的对象列表。 | `IConcertReplicationScriptingBridge` |
| `ConcertPropertyChainToString` | 将 `FConcertPropertyChain` 结构体转换为可读的字符串路径（如`"StaticMeshComponent.RelativeLocation"`）。 | `UBlueprintConcertLibrary` (假设) |
| `StringToConcertPropertyChain` | 将字符串路径解析为 `FConcertPropertyChain` 结构体。 | `UBlueprintConcertLibrary` (假设) |

### 使用示例（蓝图描述）

**场景**：在蓝图中，用户希望将一个`StaticMeshActor`的`RelativeLocation`属性添加到复制列表。

1.  **获取脚本接口**：通过某个服务定位器（如 `UGameInstance` 或单例）获取 `IConcertReplicationScriptingBridge` 的实现对象引用。
2.  **调用添加函数**：
    -   从对象引用（如当前的 `StaticMeshActor`）和字符串 `"StaticMeshComponent.RelativeLocation"` 构建参数。
    -   调用 `AddObjectProperties` 节点，传入对象引用和包含该属性路径的 `FConcertPropertyChain` 数组。
3.  **查询确认**：稍后，可以调用 `QueryObjectProperties` 来获取该对象当前所有被复制的属性，并显示在UI上。

## C++ 用法

C++ 用法主要涉及两个方面：实现自定义UI，以及通过脚本接口进行底层控制。

### 头文件引入

```cpp
// 使用脚本化接口
#include "IConcertReplicationScriptingBridge.h"

// 使用编辑器UI控件（仅在Editor模块中）
#include "ConcertReplicationScriptingEditorModule.h"
#include "Widgets/SConcertPropertyChainCombo.h"
```

### 基本用法

**1. 通过脚本接口管理复制属性**

```cpp
// 假设已经获取到有效的 Bridge 指针 (IConcertReplicationScriptingBridge*)
IConcertReplicationScriptingBridge* ScriptingBridge = GetConcertScriptingBridge();

UObject* MyObject = ...; // 要复制的对象
FConcertPropertyChain PropertyChain;
PropertyChain.AddPathSegment(FName(TEXT("MyComponent")));
PropertyChain.AddPathSegment(FName(TEXT("MyVariable")));

// 添加复制属性
ScriptingBridge->AddObjectProperties(MyObject, {PropertyChain});

// 查询该对象的复制属性
TArray<FConcertPropertyChain> Properties = ScriptingBridge->QueryObjectProperties(MyObject);

// 移除复制属性
ScriptingBridge->RemoveObjectProperties(MyObject, {PropertyChain});
```

### 进阶用法

**2. 在编辑器中嵌入自定义属性选择器**

在您的自定义 `IDetailCustomization` 或 Slate 控件中，可以使用本插件提供的 `SConcertPropertyChainCombo` 来展示一个标准的属性选择下拉框。

```cpp
// 在 Slate 控件的构建函数中
SNew(SConcertPropertyChainCombo)
.InitialClassSelection(MyActorClass) // 设置初始搜索的类
.ContainedProperties(&MySelectedPropertiesSet) // 传入当前已选属性的集合
.IsEditable(true) // 允许用户编辑
.OnPropertySelectionChanged(this, &SMyPanel::OnPropertySelectionChanged) // 绑定回调
.OnClassChanged(this, &SMyPanel::OnClassChanged)
```

## Demo 示例

一个最小的示例，展示如何在编辑器工具窗口中使用属性选择UI。

**MyReplicationConfigPanel.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

struct FConcertPropertyChain;
class SConcertPropertyChainCombo;

class SMyReplicationConfigPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyReplicationConfigPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    // 持有当前选择的属性
    TSet<FConcertPropertyChain> SelectedProperties;

    // UI 控件
    TSharedPtr<SConcertPropertyChainCombo> PropertyPicker;

    // 回调函数
    void OnPropertiesChanged(const FConcertPropertyChain& Property, bool bIsSelected);
};
```

**MyReplicationConfigPanel.cpp**
```cpp
#include "MyReplicationConfigPanel.h"
#include "ConcertPropertyChain.h" // 来自 Concert 核心模块
#include "Widgets/SConcertPropertyChainCombo.h" // 来自本插件 Editor 模块

void SMyReplicationConfigPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(5.f)
        [
            SAssignNew(PropertyPicker, SConcertPropertyChainCombo)
            .InitialClassSelection(AActor::StaticClass())
            .ContainedProperties(&SelectedProperties)
            .IsEditable(true)
            .OnPropertySelectionChanged(FOnSelectedPropertiesChanged::CreateSP(this, &SMyReplicationConfigPanel::OnPropertiesChanged))
        ]
        // ... 可以添加其他控件，比如“应用”按钮来将SelectedProperties传递给复制系统
    ];
}

void SMyReplicationConfigPanel::OnPropertiesChanged(const FConcertPropertyChain& Property, bool bIsSelected)
{
    if (bIsSelected)
    {
        SelectedProperties.Add(Property);
    }
    else
    {
        SelectedProperties.Remove(Property);
    }
    // 刷新UI或触发其他逻辑
}
```

## 模块依赖

要使用本插件的功能，你的模块需要依赖以下模块（根据功能选择）：

| 模块 | 用途 |
|---|---|
| `Concert` | 提供 Concert 核心数据结构，如 `FConcertPropertyChain`。是所有 Concert 功能的基础。 |
| `ConcertReplicationScripting` | 提供 `IConcertReplicationScriptingBridge` 等运行时脚本化接口。蓝图和C++业务逻辑依赖此模块。 |
| `ConcertSharedSlate` | 提供共用的 Slate 控件（如 `IPropertyTreeView`），被 Editor 模块用于构建属性选择树。仅编辑器模块依赖。 |

**说明**：`ConcertReplicationScriptingEditor` 模块主要用于编辑器扩展和自定义UI，通常不需要被游戏运行时模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-06-03 | `c394e7b8` | Refactor FPropertyData to contain the objects for which the properties are being displayed. IPropert... | 重构属性数据结构，使其包含属性所属对象的引用，改进了属性显示逻辑。 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ItemHeight and ItemWidth are only us... | 适配Slate控件弃用项，更新列表和树视图高度相关API。 |
| 2024-04-11 | `33250188` | Refactor replication UI in preparation of matrix view: | 重构复制UI，为即将到来的矩阵视图功能做准备。 |

### 维护评价

-   **创建时间**：创建于 2023 年 12 月，是一个相对较新的插件（约2年历史）。
-   **活跃度**：在 2024 年 4-6 月期间有多次功能性更新和重构，表明**处于活跃维护中**。
-   **状态**：`IsBetaVersion=false`，`IsExperimentalVersion=false`，`EnabledByDefault=false`。表明它是一个正式的功能插件，但默认不启用（可能因为并非所有项目都使用Concert复制）。
-   **推荐使用**：**推荐使用**。如果你的项目确实需要用到 Concert 复制系统的脚本化配置或自定义UI，这是一个官方维护的、功能明确的工具。它正在持续改进中。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting)
-   [官方文档](): （暂无）
-   [测试用例]()：测试用例可能位于引擎的 `Engine/Tests/` 目录下，具体路径未在提供信息中。