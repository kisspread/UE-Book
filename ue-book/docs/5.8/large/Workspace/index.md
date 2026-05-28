# Workspace

> Editor framework allowing multiple assets to be edited in a unified workspace UI

| 属性 | 值 |
|---|---|
| 中文名 | 工作区编辑器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WorkspaceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Workspace) | |

## 用途

Workspace 插件提供了一个**统一的多资产编辑器框架**，允许用户在一个工作区界面中同时打开、编辑和管理多个资产。

传统的 UE 编辑器中，每种资产通常有独立的编辑器窗口，资产之间的关联操作需要频繁切换窗口。Workspace 解决了这个问题：

- **统一编辑界面**：将多个相关资产集中在一个标签式工作区中编辑，支持文档标签页、大纲视图、详情面板和视口
- **Schema 驱动**：通过 `UWorkspaceSchema` 定义工作区的外观、支持的资产类型、行为约束，不同项目可以创建不同用途的工作区
- **状态持久化**：工作区状态以 JSON 文件持久化保存（基于 GUID），每个用户独立存储，包括打开的文档、布局等
- **可扩展的文档类型**：支持普通资产文档和图形文档（类似蓝图编辑器），通过委托模式注册自定义文档类型

该插件最初是为 AnimNext 动画系统开发的，但设计上是通用框架，支持任何资产类型扩展。目前处于实验阶段，默认未启用。

## 使用场景

- 你在开发 AnimNext 动画系统，需要在一个界面中同时编辑动画蓝图、Rig 资产和约束 → 用 Workspace
- 你需要为自定义资产创建一个统一的编辑环境，包含大纲视图、详情面板和视口 → 继承 `UWorkspaceSchema`
- 你有多个相互关联的资产需要频繁切换编辑 → 用 Workspace 把它们组织到一个工作区中
- 你需要自定义工作区的大纲树节点显示、图标、双击行为 → 实现 `IWorkspaceOutlinerItemDetails`

## 蓝图用法

### 核心节点（UWorkspace）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAsset` | 向工作区添加一个资产 | `UWorkspace` |
| `AddAssets` | 向工作区批量添加资产 | `UWorkspace` |
| `RemoveAsset` | 从工作区移除一个资产 | `UWorkspace` |
| `RemoveAssets` | 从工作区批量移除资产 | `UWorkspace` |

### 使用示例（蓝图描述）

1. **打开工作区编辑器**：通过 C++ 调用 `IWorkspaceEditorModule::OpenWorkspaceForObject()` 传入目标资产，插件会自动创建或复用已有工作区
2. **管理资产**：在蓝图中获取 `UWorkspace` 引用后，使用 `AddAsset`/`RemoveAsset` 节点管理工作区内的资产列表
3. **工作区选择器**：当资产存在于多个工作区中时，调用 `CreateWorkspacePicker()` 弹出选择对话框，让用户选择打开哪个工作区

## C++ 用法

### 头文件引入

```cpp
#include "IWorkspaceEditorModule.h"
#include "IWorkspaceEditor.h"
#include "WorkspaceSchema.h"
#include "WorkspaceFactory.h"
#include "WorkspaceAssetRegistryInfo.h"
```

### 基本用法：注册自定义文档类型

为特定 UObject 类型注册文档编辑器，当该类型在工作区中打开时，自动创建自定义编辑 Widget。

```cpp
// 来源: IWorkspaceEditorModule.h - RegisterObjectDocumentType / FObjectDocumentArgs

#include "IWorkspaceEditorModule.h"

void RegisterMyDocumentType()
{
    IWorkspaceEditorModule& WorkspaceModule = FModuleManager::LoadModuleChecked<IWorkspaceEditorModule>("WorkspaceEditor");

    // 配置文档参数
    UE::Workspace::FObjectDocumentArgs DocumentArgs;
    DocumentArgs.SpawnLocation = UE::Workspace::WorkspaceTabs::TopMiddleDocumentArea;
    DocumentArgs.OnMakeDocumentWidget = UE::Workspace::FOnMakeDocumentWidget::CreateLambda(
        [](const UE::Workspace::FWorkspaceEditorContext& Context) -> TSharedRef<SWidget>
        {
            // 根据上下文中的对象创建编辑 Widget
            UObject* Object = Context.Document.GetObject();
            // ... 创建自定义编辑控件 ...
            return SNew(STextBlock).Text(FText::FromString(Object->GetName()));
        }
    );

    // 可选：自定义标签名称
    DocumentArgs.OnGetTabName = UE::Workspace::FOnGetTabName::CreateLambda(
        [](const UE::Workspace::FWorkspaceEditorContext& Context) -> TAttribute<FText>
        {
            return FText::FromString(Context.Document.GetObject()->GetName());
        }
    );

    // 注册到指定资产类
    FTopLevelAssetPath ClassPath(UMyAsset::StaticClass());
    WorkspaceModule.RegisterObjectDocumentType(ClassPath, DocumentArgs);
}
```

### 基本用法：打开工作区

```cpp
// 来源: IWorkspaceEditorModule.h - OpenWorkspaceForObject

#include "IWorkspaceEditorModule.h"

void OpenWorkspaceForAsset(UObject* InAsset)
{
    IWorkspaceEditorModule& WorkspaceModule = 
        FModuleManager::LoadModuleChecked<IWorkspaceEditorModule>("WorkspaceEditor");

    // 打开工作区，Default 策略：复用已有工作区或创建新的
    UE::Workspace::IWorkspaceEditor* Editor = WorkspaceModule.OpenWorkspaceForObject(
        InAsset,
        UE::Workspace::EOpenWorkspaceMethod::Default
    );
}
```

### 进阶用法：创建自定义 Schema

通过继承 `UWorkspaceSchema` 定义工作区行为约束。

```cpp
// 来源: WorkspaceSchema.h - UWorkspaceSchema

UCLASS()
class UMyCustomSchema : public UWorkspaceSchema
{
    GENERATED_BODY()

public:
    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MySchema", "DisplayName", "自定义工作区");
    }

    // 限制仅支持特定资产类型
    virtual TConstArrayView<FTopLevelAssetPath> GetSupportedAssetClassPaths() const override
    {
        static const TArray<FTopLevelAssetPath> SupportedTypes = {
            FTopLevelAssetPath(TEXT("/Script/MyModule"), TEXT("UMyAsset")),
            FTopLevelAssetPath(TEXT("/Script/Engine"), TEXT("UBlueprint"))
        };
        return SupportedTypes;
    }

    // 启用视口支持
    virtual bool SupportsViewport() const override { return true; }

    // 支持多资产编辑
    virtual bool SupportsMultipleAssets() const override { return true; }

    // 允许保存为资产
    virtual bool CanSaveWorkspace() const override { return true; }

    // 自定义工作区状态保存
    virtual void OnSaveWorkspaceState(
        TSharedRef<UE::Workspace::IWorkspaceEditor> InWorkspaceEditor,
        FInstancedStruct& OutWorkspaceState) const override
    {
        // 保存自定义状态数据到 OutWorkspaceState
    }

    virtual void OnLoadWorkspaceState(
        TSharedRef<UE::Workspace::IWorkspaceEditor> InWorkspaceEditor,
        const FInstancedStruct& InWorkspaceState) const override
    {
        // 从 InWorkspaceState 恢复自定义状态
    }
};
```

### 进阶用法：注册图形文档编辑器

```cpp
// 来源: IWorkspaceEditorModule.h - FGraphDocumentWidgetArgs / CreateGraphDocumentArgs

void RegisterGraphDocumentType()
{
    IWorkspaceEditorModule& WorkspaceModule = 
        FModuleManager::LoadModuleChecked<IWorkspaceEditorModule>("WorkspaceEditor");

    UE::Workspace::FGraphDocumentWidgetArgs GraphArgs;
    GraphArgs.SpawnLocation = UE::Workspace::WorkspaceTabs::TopMiddleDocumentArea;

    // 设置图形选择变更回调
    GraphArgs.OnGraphSelectionChanged = UE::Workspace::FOnGraphSelectionChanged::CreateLambda(
        [](const UE::Workspace::FWorkspaceEditorContext& Context,
           const FGraphPanelSelectionSet& SelectionSet)
        {
            // 处理图形节点选中事件
            TArray<UObject*> SelectedObjects;
            for (UObject* Obj : SelectionSet)
            {
                SelectedObjects.Add(Obj);
            }
            Context.WorkspaceEditor->SetDetailsObjects(SelectedObjects);
        }
    );

    // 创建完整的图形文档参数
    UE::Workspace::FObjectDocumentArgs GraphDocArgs = 
        WorkspaceModule.CreateGraphDocumentArgs(GraphArgs);

    FTopLevelAssetPath ClassPath(UMyGraphAsset::StaticClass());
    WorkspaceModule.RegisterObjectDocumentType(ClassPath, GraphDocArgs);
}
```

### 进阶用法：自定义大纲节点显示

```cpp
// 来源: IWorkspaceOutlinerItemDetails.h

class FMyOutlinerItemDetails : public UE::Workspace::IWorkspaceOutlinerItemDetails
{
public:
    virtual FString GetDisplayString(
        const FWorkspaceOutlinerItemExport& Export) const override
    {
        return Export.GetIdentifier().ToString();
    }

    virtual const FSlateBrush* GetItemIcon(
        const FWorkspaceOutlinerItemExport& Export) const override
    {
        return FAppStyle::GetBrush(TEXT("ClassIcon.Actor"));
    }

    virtual bool HandleDoubleClick(
        const FToolMenuContext& ToolMenuContext) const override
    {
        // 自定义双击行为
        return true;
    }

    virtual bool CanDelete(
        const FWorkspaceOutlinerItemExport& Export) const override
    {
        return true;
    }

    virtual void Delete(
        TConstArrayView<FWorkspaceOutlinerItemExport> Exports) const override
    {
        // 执行删除逻辑
    }
};

// 注册
void RegisterMyOutlinerDetails()
{
    IWorkspaceEditorModule& WorkspaceModule = 
        FModuleManager::LoadModuleChecked<IWorkspaceEditorModule>("WorkspaceEditor");

    UE::Workspace::FOutlinerItemDetailsId DetailsId("MyOutlinerData");
    auto Details = MakeShared<FMyOutlinerItemDetails>();
    WorkspaceModule.RegisterWorkspaceItemDetails(DetailsId, Details);
}
```

## Demo 示例

一个最小的工作区 Schema 和文档类型注册示例：

```cpp
// MyWorkspaceSchema.h
#pragma once

#include "WorkspaceSchema.h"
#include "MyWorkspaceSchema.generated.h"

UCLASS()
class UMyWorkspaceSchema : public UWorkspaceSchema
{
    GENERATED_BODY()

public:
    virtual FText GetDisplayName() const override;
    virtual TConstArrayView<FTopLevelAssetPath> GetSupportedAssetClassPaths() const override;
    virtual bool SupportsMultipleAssets() const override { return true; }
    virtual bool CanSaveWorkspace() const override { return true; }
};
```

```cpp
// MyWorkspaceSchema.cpp
#include "MyWorkspaceSchema.h"
#include "IWorkspaceEditorModule.h"

FText UMyWorkspaceSchema::GetDisplayName() const
{
    return NSLOCTEXT("MyWorkspace", "SchemaName", "我的工作区");
}

TConstArrayView<FTopLevelAssetPath> UMyWorkspaceSchema::GetSupportedAssetClassPaths() const
{
    static const TArray<FTopLevelAssetPath> Types = {
        FTopLevelAssetPath(TEXT("/Script/MyModule"), TEXT("UMyDataAsset"))
    };
    return Types;
}

// 在你的 Editor 模块 StartupModule 中注册文档类型
void FMyEditorModule::StartupModule()
{
    IWorkspaceEditorModule& WorkspaceModule =
        FModuleManager::LoadModuleChecked<IWorkspaceEditorModule>("WorkspaceEditor");

    UE::Workspace::FObjectDocumentArgs Args;
    Args.SpawnLocation = UE::Workspace::WorkspaceTabs::TopMiddleDocumentArea;
    Args.OnMakeDocumentWidget = UE::Workspace::FOnMakeDocumentWidget::CreateLambda(
        [](const UE::Workspace::FWorkspaceEditorContext& Ctx) -> TSharedRef<SWidget>
        {
            return SNew(STextBlock)
                .Text(FText::FromString(
                    FString::Printf(TEXT("Editing: %s"),
                        *Ctx.Document.GetObject()->GetName())));
        });

    WorkspaceModule.RegisterObjectDocumentType(
        FTopLevelAssetPath(TEXT("/Script/MyModule"), TEXT("UMyDataAsset")),
        Args);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SceneOutliner` | 工作区大纲视图（树形资产列表） |
| `GraphEditor` | 图形文档编辑器支持 |
| `WorkflowOrientedApp` | 文档标签页管理框架（FDocumentTracker） |
| `Toolkits` | 资产编辑器工具包基类（FBaseAssetToolkit） |
| `AdvancedPreviewScene` | 视口预览场景 |
| `AssetDefinition` | 资产定义（编辑器打开行为） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 |
| 2026-03-30 | `e225d752` | Request a details panel refresh instead of forcing it as it can be called after property changes are | 修复详情面板刷新时机，改为请求式刷新 |
| 2026-03-23 | `34a186ba` | EditorUsability : Workspace | 工作区编辑器可用性改进 |
| 2026-03-12 | `c1faf18c` | Fix a few places to use verify() instead of check() as check compiles out in shipping. | 将 check() 改为 verify() 防止 Shipping 构建中编译移除 |
| 2026-03-09 | `e23652d8` | Workspace: Fix selection changes between different graph documents clearing the selected object | 修复切换图形文档时选中状态被错误清除的问题 |

### 维护评价

- **活跃维护**：最近更新距今不到 1 个月（2026-04-14），且近 2 个月内有多次实质性更新
- **实验状态**：`.uplugin` 中 `IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **代码质量**：近期修复包含类型安全（verify 替代 check）、UI 可用性改进、选择状态修复等，表明仍在积极打磨
- **功能稳定**：核心框架（Schema、文档类型注册、大纲视图、状态持久化）已完整，但 API 仍可能随实验阶段变化
- **推荐使用**：适合需要自定义多资产编辑器的项目，但需注意实验性 API 可能变动。不建议直接用于生产环境，适合作为参考或在可控范围内使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Workspace)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Workspace/Tests)（如有）