# Concert Shared Slate

> Contains UI that is shared by client UI modules only

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertClientSharedSlate` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-02-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertUI/ConcertClientSharedSlate) | |

## 用途

ConcertClientSharedSlate 是 UE5 Multi-User Editing（Concert）系统中**客户端专用的 UI 共享层**。它为 Concert 的属性复制（Replication）编辑器提供可复用的 Slate widget、数据模型和编辑器集成逻辑。

该模块解决的核心问题是：Concert 系统中有多个客户端 UI 模块（Multi-User Server、Recovery Service、CrashReportClientEditor 等）都需要相同的复制流编辑器 UI 组件——属性树视图、对象选择源、拖放支持、撤销/重做事务等。本模块将这些通用 UI 逻辑抽取为共享库，避免重复实现。

简单来说，**如果你要为 Concert 构建一个带属性复制编辑功能的客户端 UI，这个模块就是你的 UI 工具箱**。

## 使用场景

- 你正在为 Concert Multi-User 编辑系统构建客户端 UI，需要一个可过滤的属性树视图来选择要复制的属性
- 你需要支持拖拽 Actor 到复制 outliner 中添加对象
- 你需要让复制流编辑器的操作支持 Ctrl+Z 撤销（Transactional 模型）
- 你希望在用户向复制流添加对象时自动绑定默认属性和子对象（如添加 StaticMeshActor 时自动包含其 StaticMeshComponent）
- 你只希望显示当前编辑器世界中的对象，隐藏其他世界的对象

> ⚠️ **注意**：本模块 `EnabledByDefault: false` 且 `Hidden: true`，仅对 `UnrealRecoverySvc` 程序开放（`ProgramAllowList`）。普通编辑器项目不会自动加载此模块。

## 蓝图用法

本模块没有暴露 `UFUNCTION(BlueprintCallable)` 接口。所有功能均为 C++ API，面向开发者在 Concert 客户端 UI 模块内部使用。

## C++ 用法

### 头文件引入

```cpp
#include "ConcertClientFrontendUtils.h"
#include "Replication/ClientReplicationWidgetFactories.h"
#include "Replication/ClientReplicationWidgetDelegates.h"
#include "Widgets/Client/ClientInfoHelpers.h"
```

### 核心功能：创建带过滤的属性树视图

本模块最重要的公开 API 是 `CreateFilterablePropertyTreeView`，它创建一个支持类型过滤的属性树视图 widget。

```cpp
#include "Replication/ClientReplicationWidgetFactories.h"

using namespace UE::ConcertClientSharedSlate;

// 配置属性树视图参数
FFilterablePropertyTreeViewParams Params;
Params.AdditionalPropertyColumns = {
    ConcertSharedSlate::ReplicationColumns::Property::LabelColumn()
};
Params.PrimaryPropertySort = {
    ConcertSharedSlate::ReplicationColumns::Property::LabelColumnId,
    EColumnSortMode::Ascending
};

// 创建可过滤的属性树视图
TSharedRef<ConcertSharedSlate::IPropertyTreeView> PropertyTreeView =
    CreateFilterablePropertyTreeView(MoveTemp(Params));

// PropertyTreeView->GetWidget() 返回 SWidget，可嵌入任意 Slate 布局
```

源码路径：`Public/Replication/ClientReplicationWidgetFactories.h`

### 事务化复制流模型（支持撤销/重做）

```cpp
#include "Replication/ClientReplicationWidgetFactories.h"

using namespace UE::ConcertClientSharedSlate;

// 方式 1：包装已有模型
TSharedRef<ConcertSharedSlate::IEditableReplicationStreamModel> BaseModel = /* ... */;
UObject* OwnerObject = /* 拥有 FConcertObjectReplicationMap 的 UObject */;
TSharedRef<ConcertSharedSlate::IEditableReplicationStreamModel> TransactionalModel =
    CreateTransactionalStreamModel(BaseModel, *OwnerObject);

// 方式 2：自动创建内部 UObject
TSharedRef<ConcertSharedSlate::IEditableReplicationStreamModel> TransactionalModel2 =
    CreateTransactionalStreamModel();

// 之后对 TransactionalModel 的 AddObjects / RemoveObjects / AddProperties / RemoveProperties
// 操作都会自动包裹在 FScopedTransaction 中，支持 Ctrl+Z
```

源码路径：`Public/Replication/ClientReplicationWidgetFactories.h`，实现于 `Private/Replication/Editor/Model/TransactionalReplicationStreamModel.h`

### 拖放 Actor 到复制 Outliner

```cpp
#include "Replication/ClientReplicationWidgetFactories.h"

using namespace UE::ConcertClientSharedSlate;

FCreateDropTargetOutlinerWrapperParams DropParams;
DropParams.HandleDroppedObjectsDelegate.BindLambda([](TConstArrayView<UObject*> DroppedObjects) {
    // 将拖入的对象添加到复制流
    for (UObject* Obj : DroppedObjects) {
        // ... 添加到 IEditableReplicationStreamModel
    }
});
DropParams.CanDropObjectDelegate.BindLambda([](UObject& Object) -> bool {
    return Object.IsA<AActor>(); // 只接受 Actor
});

// 获取包装函数，用于包裹复制 outliner widget
ConcertSharedSlate::FWrapOutlinerWidget Wrapper = CreateDropTargetOutlinerWrapper(MoveTemp(DropParams));
```

### 客户端信息辅助函数

```cpp
#include "Widgets/Client/ClientInfoHelpers.h"

using namespace UE::ConcertClientSharedSlate;

TSharedRef<IConcertClient> Client = /* ... */;

// 获取客户端信息查询委托
ConcertSharedSlate::FGetOptionalClientInfo GetClientInfo = MakeClientInfoGetter(Client);

// 查询某个 endpoint 的客户端信息
TOptional<FConcertClientInfo> Info = GetClientInfo.Execute(SomeEndpointGuid);

// 判断是否为本地客户端
ConcertSharedSlate::FIsLocalClient IsLocal = MakeIsLocalClientGetter(Client);
bool bLocal = IsLocal.Execute(SomeEndpointGuid);

// 获取本地客户端信息（TAttribute 形式，适合绑定到 UI）
TAttribute<TOptional<FConcertClientInfo>> LocalInfo = MakeLocalClientInfoAttribute(Client);
```

### 自动绑定规则配置

```cpp
#include "Replication/Settings/ConcertStreamObjectAutoBindingRules.h"

FConcertStreamObjectAutoBindingRules Rules;

// 为 AStaticMeshActor 配置默认选择的属性
FConcertDefaultPropertySelection& Selection = Rules.DefaultPropertySelection.Add(
    FSoftClassPath(AStaticMeshActor::StaticClass())
);
Selection.DefaultSelectedProperties.Add(TEXT("RelativeLocation.X"));
Selection.DefaultSelectedProperties.Add(TEXT("RelativeLocation.Y"));
Selection.DefaultSelectedProperties.Add(TEXT("RelativeLocation.Z"));

// 为 AStaticMeshActor 配置自动添加的子对象规则
FConcertInheritableSubobjectMatchingRules& MeshRules =
    Rules.DefaultAddedSubobjectRules.SubobjectMatchingRules.Add(
        FSoftClassPath(AStaticMeshActor::StaticClass())
    );
MeshRules.IncludeAllOption = EConcertIncludeAllSubobjectsType::AllComponents;
```

## Demo 示例

### 最小复制流编辑器集成

```cpp
// MyReplicationEditor.h
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "Replication/Editor/View/IPropertyTreeView.h"

class SMyReplicationEditor : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyReplicationEditor) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<ConcertSharedSlate::IPropertyTreeView> PropertyTreeView;
};
```

```cpp
// MyReplicationEditor.cpp
#include "MyReplicationEditor.h"
#include "Replication/ClientReplicationWidgetFactories.h"
#include "Replication/Editor/UnrealEditor/HideObjectsNotInWorldLogic.h"
#include "Replication/Editor/UnrealEditor/ModifyObjectInLevelHandler.h"

void SMyReplicationEditor::Construct(const FArguments& InArgs)
{
    using namespace UE::ConcertClientSharedSlate;

    // 创建带过滤的属性视图
    FFilterablePropertyTreeViewParams Params;
    PropertyTreeView = CreateFilterablePropertyTreeView(MoveTemp(Params));

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            PropertyTreeView->GetWidget()
        ]
    ];
}
```

Build.cs 依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ConcertClientSharedSlate"
});
```

## 模块依赖

### Public 依赖

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `EditorStyle` | 编辑器样式 |
| `ConcertSharedSlate` | Concert 共享 Slate 组件（本模块的基础） |
| `ConcertSyncClient` | Concert 同步客户端 |

### Private 依赖

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 资产定义系统 |
| `AssetRegistry` | 资产注册表 |
| `EditorWidgets` | 编辑器通用 widget |
| `InputCore` | 输入核心 |
| `Projects` | 项目/插件信息 |
| `SubobjectDataInterface` | 子对象数据接口（用于组件层级） |
| `ToolMenus` | 工具菜单系统 |
| `ToolWidgets` | 工具 widget |
| `UnrealEd` | 编辑器功能（事务、撤销等） |
| `Concert` | Concert 核心 |
| `ConcertClient` | Concert 客户端 |
| `ConcertSyncCore` | Concert 同步核心 |
| `ConcertTransport` | Concert 传输层（LogConcert） |

### 依赖的插件

| 插件 | 用途 |
|---|---|
| `ConcertMain` | Concert 主插件 |
| `ConcertSharedSlate` | 共享 Slate 组件（接口定义） |
| `ConcertSyncCore` | 同步核心逻辑 |
| `ConcertSyncClient` | 同步客户端逻辑 |

## 架构概览

本模块围绕 Concert 属性复制编辑器构建，分为以下子系统：

### 1. Widget 工厂（ClientReplicationWidgetFactories）

核心工厂函数，创建各种复制编辑器 widget：

- `CreateFilterablePropertyTreeView` — 带过滤栏的属性树视图
- `CreateTransactionalStreamModel` — 支持撤销/重做的复制流模型
- `CreateDropTargetOutlinerWrapper` — 拖放支持
- `CreateObjectHierarchyForComponentHierarchy` — 组件层级树
- `CreateEditorObjectNameModel` — 编辑器对象名称模型

### 2. 对象源模型（Model/ObjectSource）

提供"从哪里获取可添加的对象"：

| 类 | 功能 |
|---|---|
| `FSelectedActorsSource` | 从编辑器当前选中的 Actor 获取 |
| `FWorldActorSource` | 从当前 GWorld 中所有 Actor 获取 |
| `FActorSelectionSourceModel` | 整合 Actor 选择逻辑，含右键菜单 |

### 3. 属性源模型（Model/PropertySource）

提供"某对象有哪些属性可选"：

| 类 | 功能 |
|---|---|
| `FReplicatablePropertySource` | 列出 UClass 中所有可复制属性 |
| `FSelectPropertyFromUClassModel` | 决策哪些属性可添加到复制流 |
| `FConcertSyncCoreReplicatedPropertySource` | ⚠️ 已废弃（5.5），旧版属性源 |

### 4. 设置/规则系统（Settings）

配置自动绑定行为：

| 类 | 功能 |
|---|---|
| `FConcertStreamObjectAutoBindingRules` | 顶层规则容器 |
| `FConcertDefaultPropertySelection` | 每类默认选中的属性 |
| `FConcertSubobjectMatchingRules` | 子对象匹配规则（类、正则、全选） |
| `FConcertPerClassSubobjectMatchingRules` | 按类绑定的子对象匹配规则（支持继承） |
| `FConcertInheritableClassOption` | 可继承的类选项基类 |
| `FStreamExtenderBySettings` | 根据设置自动扩展复制流 |

### 5. 编辑器集成（Editor/UnrealEditor）

与 Unreal Editor 深度集成：

| 类 | 功能 |
|---|---|
| `FModifyObjectInLevelHandler` | Actor 删除/组件变更时自动更新模型 |
| `FHideObjectsNotInWorldLogic` | 只显示当前世界中的对象 |

### 6. UI 辅助

| 类/函数 | 功能 |
|---|---|
| `ConcertClientFrontendUtils` | 按钮创建工具（文本/图标按钮） |
| `ClientInfoHelpers` | 从 IConcertClient 获取客户端信息的委托工厂 |
| `SReplicationDropArea` | 拖放区域 widget |
| `SFilteredPropertyTreeView` | 带过滤栏的属性树视图 widget |
| `PropertyUtils` | 添加属性时自动包含子属性（struct 成员等） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-18 | `c61e427` | Various fixes to make unreal editor compile with IWYU | IWYU（Include What You Use）编译修复，确保头文件自包含 |
| 2025-05-20 | `b668eee` | Fixing issue where a USTRUCT inherits from more than one USTRUCT | 修复 UHT 中 USTRUCT 多继承检查问题 |
| 2025-04-17 | `985b0b6` | Apply same fix for CrashReportClientEditor as for UnrealMultiUserServer | 修复 CrashReportClientEditor 的 `-allmodules` 编译问题 |

### 维护评价

- **创建时间**：2022-02-23（约 4 年）
- **最近更新**：2025-06-18，最近 3 次更新均为编译/构建修复，无功能性更新
- **维护状态**：维护中，但更新内容以基础设施修复为主
- **Beta 状态**：`IsBetaVersion=true`，API 可能在未来版本变更
- **推荐使用**：仅在构建 Concert 客户端 UI 模块时使用。普通项目无需也不应直接依赖此模块

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertUI/ConcertClientSharedSlate)
- [ConcertSharedSlate（基础接口模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertUI/ConcertSharedSlate)
- [ConcertMain（主插件）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertMain)
