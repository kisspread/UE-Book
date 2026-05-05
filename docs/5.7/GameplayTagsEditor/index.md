# Gameplay Tags Editor

> GameplayTagsEditor provides blueprint nodes and editor UI to enable the use of GameplayTags for tagging assets and objects

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayTagsEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-11-01 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/GameplayTagsEditor) | |

## 用途

GameplayTagsEditor 是 UE5 GameplayTags 系统的**编辑器扩展层**。它不提供运行时功能，只在编辑器中工作，负责三件核心事情：

1. **属性面板自定义**：将 Details 面板中 `FGameplayTag`、`FGameplayTagContainer`、`FGameplayTagQuery` 的默认结构体展示替换为专用的选择器控件（下拉 Combo、树形 Picker、Chip 标签等）。
2. **蓝图节点**：提供 Switch on GameplayTag、Multi-Compare 等自定义 K2 节点，让蓝图中可以直接按 Tag 分支。
3. **Tag 管理器**：提供一个可停靠的编辑器窗口（Gameplay Tag Manager），用于创建、重命名、删除、搜索 Tag，以及管理 Tag Source 和清理未使用的 Tag。

如果禁用此插件，项目中仍然可以使用 GameplayTags 运行时功能，但编辑器中将无法方便地选择和管理 Tag——所有 `FGameplayTag` 属性将退化为纯文本输入。

## 使用场景

- 你在编辑器中为 Actor/资产设置 Tag 分类 → Details 面板中会出现 Tag 选择器下拉框（由本插件提供）
- 你需要在蓝图中根据不同的 GameplayTag 执行不同逻辑 → 使用本插件提供的 `Switch on Gameplay Tag` 蓝图节点
- 你需要创建新的 GameplayTag 或重命名/删除已有 Tag → 使用 `Window > Gameplay Tag Manager`（由本插件注册）
- 你需要查找项目中哪些 Tag 没有被任何资产使用 → 使用 Tag Manager 中的清理功能
- 你需要在蓝图中对 GameplayTagContainer 或 IGameplayTagAssetInterface 做多 Tag 比较 → 使用 Multi-Compare 节点

## 蓝图用法

### K2 节点一览

本插件注册了以下自定义蓝图节点：

| 节点 | 说明 | 类 |
|---|---|---|
| `Switch on Gameplay Tag` | 根据单个 FGameplayTag 值分支，每个 Tag 对应一个输出 Pin | `UGameplayTagsK2Node_SwitchGameplayTag` |
| `Switch on Gameplay Tag Container` | 根据 FGameplayTagContainer 中是否包含指定 Tag 分支 | `UGameplayTagsK2Node_SwitchGameplayTagContainer` |
| `Multi Compare Gameplay Tag` | 纯函数节点，同时比较多个 Tag 值，返回匹配的布尔结果 | `UGameplayTagsK2Node_MultiCompareGameplayTagContainer` |
| `Multi Compare Gameplay Tag (Single Tags)` | 同上，但输入为单个 Tag 而非 Container | `UGameplayTagsK2Node_MultiCompareGameplayTagContainerSingleTags` |
| `Multi Compare Gameplay Tag Asset Interface` | 对实现了 `IGameplayTagAssetInterface` 的对象做多 Tag 比较 | `UGameplayTagsK2Node_MultiCompareGameplayTagAssetInterface` |
| `Multi Compare Gameplay Tag Asset Interface (Single Tags)` | 同上，但输入为单个 Tag | `UGameplayTagsK2Node_MultiCompareGameplayTagAssetInterfaceSingleTags` |
| `Literal Gameplay Tag` | ⚠️ **已废弃**（`IsDeprecated = true`），用于创建字面量 Tag 常量 | `UGameplayTagsK2Node_LiteralGameplayTag` |

### Switch on Gameplay Tag

最常用的节点。从右键菜单添加后，可在 Details 面板中配置要匹配的 Tag 列表。每个 Tag 对应一个执行输出 Pin，加上一个默认的 `Default` Pin。

**使用方式**：
1. 在蓝图中右键 → 搜索 "Switch on Gameplay Tag"
2. 在 Details 面板中点击 `Pin Tags` 数组添加要匹配的 Tag
3. 将输入 Tag 连接到 `Selection` Pin
4. 每个配置的 Tag 会生成一个输出执行 Pin

### Multi-Compare 节点

Multi-Compare 系列是纯函数节点（无执行 Pin），用于在单个节点中同时检查多个 Tag 条件。输出 Pin 数量可动态增减（通过节点上的 +/- 按钮）。

**使用方式**：
1. 在蓝图中右键 → 搜索 "Multi Compare Gameplay Tag"
2. 将 Tag Container 或 Asset Interface 连接到输入 Pin
3. 在每个输出 Pin 上配置要比较的 Tag
4. 每个输出 Pin 是一个布尔值，表示是否匹配

### 蓝图中的 Tag Pin

在蓝图图表中，所有 `FGameplayTag`、`FGameplayTagContainer`、`FGameplayTagQuery` 类型的 Pin 都会使用自定义控件：

- **`SGameplayTagGraphPin`**：单个 Tag Pin，点击后弹出 Tag 选择器
- **`SGameplayTagContainerGraphPin`**：Container Pin，支持选择多个 Tag
- **`SGameplayTagQueryGraphPin`**：Query Pin，点击后打开 Query 编辑器

这些 Pin 控件由 `FGameplayTagsGraphPanelPinFactory` 注册，自动应用于蓝图中所有相关类型的 Pin。

## C++ 用法

### 头文件引入

```cpp
#include "GameplayTagsEditorModule.h"  // 模块接口
#include "SGameplayTagWidget.h"        // Tag 树形选择器
#include "SGameplayTagPicker.h"        // 新版 Tag 选择器
#include "SGameplayTagCombo.h"         // 单 Tag 下拉控件
#include "SGameplayTagContainerCombo.h" // Container 下拉控件
#include "SGameplayTagChip.h"          // Tag 标签显示控件
#include "SGameplayTagQueryEntryBox.h" // Query 编辑入口
#include "AssetDefinition_GameplayTagAssetBase.h" // 资产定义基类
```

### 模块接口 (`IGameplayTagsEditorModule`)

模块接口是与本插件交互的主要 C++ 入口，提供 Tag 的增删改查和 UI 创建能力：

```cpp
// 获取模块实例
IGameplayTagsEditorModule& Module = IGameplayTagsEditorModule::Get();

// 创建新 Tag
Module.AddNewGameplayTagToINI(
    TEXT("MyCategory.MyTag"),    // Tag 名称（用 . 分隔层级）
    TEXT("This is a comment"),   // 注释
    NAME_None,                   // Tag Source（None = 默认）
    false,                       // 是否为受限 Tag
    true                         // 是否允许非受限子 Tag
);

// 删除 Tag
TSharedPtr<FGameplayTagNode> TagNode = UGameplayTagsManager::Get().FindTagNode(FName("MyCategory.MyTag"));
Module.DeleteTagFromINI(TagNode);

// 重命名 Tag
Module.RenameTagInINI(TEXT("MyCategory.OldName"), TEXT("MyCategory.NewName"), true /*bRenameChildren*/);

// 更新 Tag 信息（注释、受限状态等）
Module.UpdateTagInINI(TEXT("MyCategory.MyTag"), TEXT("New comment"), false, true);

// 在不同 Tag Source 之间移动 Tag
TArray<FString> TagsToMove = { TEXT("MyCategory.MyTag") };
TArray<FString> OutMoved, OutFailed;
Module.MoveTagsBetweenINI(TagsToMove, FName("GameplayTagDefs.ini"), OutMoved, OutFailed);

// 添加临时 Tag（仅当前编辑器会话有效）
Module.AddTransientEditorGameplayTag(TEXT("Temp.DebugTag"));

// 添加新的 Tag Source
Module.AddNewGameplayTagSource(TEXT("MyMod"), TEXT("/Game/MyMod/Config"));

// 查找未使用的 Tag
TArray<TSharedPtr<FGameplayTagNode>> UnusedTags;
Module.GetUnusedGameplayTags(UnusedTags);
```

### 创建自定义 Tag 选择控件

```cpp
// 方式一：通过模块接口创建简单控件
TSharedRef<SWidget> TagWidget = Module.MakeGameplayTagWidget(
    FOnSetGameplayTag::CreateLambda([](const FGameplayTag& Tag) {
        UE_LOG(LogTemp, Log, TEXT("Selected tag: %s"), *Tag.ToString());
    }),
    MakeShared<FGameplayTag>(MyTag),
    TEXT("MyCategory")  // 过滤字符串，只显示此分类下的 Tag
);

// 方式二：创建 Container 控件
TSharedRef<SWidget> ContainerWidget = Module.MakeGameplayTagContainerWidget(
    FOnSetGameplayTagContainer::CreateLambda([](const FGameplayTagContainer& Container) {
        // 处理容器变化
    }),
    MakeShared<FGameplayTagContainer>(MyContainer),
    TEXT("Ability,Status")  // 逗号分隔的过滤字符串
);

// 方式三：使用 SGameplayTagCombo（推荐用于单 Tag 选择）
SNew(SGameplayTagCombo)
    .Filter(TEXT("Weapon.Type"))
    .ReadOnly(false)
    .Tag(MyTag)
    .OnTagChanged_Lambda([](const FGameplayTag NewTag) {
        // 处理 Tag 变化
    });

// 方式四：使用 SGameplayTagContainerCombo（推荐用于多 Tag 选择）
SNew(SGameplayTagContainerCombo)
    .Filter(TEXT("Ability"))
    .ReadOnly(false)
    .TagContainer(MyContainer)
    .OnTagContainerChanged_Lambda([](const FGameplayTagContainer& NewContainer) {
        // 处理容器变化
    });
```

### 属性自定义

本插件在启动时自动注册了以下属性类型自定义：

| 类型名 | 自定义类 | 说明 |
|---|---|---|
| `GameplayTag` | `FGameplayTagCustomization` | Details 面板中的单 Tag 编辑器 |
| `GameplayTagContainer` | `FGameplayTagContainerCustomization` | Details 面板中的多 Tag 编辑器 |
| `GameplayTagQuery` | `FGameplayTagQueryCustomization` | Details 面板中的 Query 编辑器 |
| `GameplayTagCreationWidgetHelper` | `FGameplayTagCreationWidgetHelperDetails` | 创建 Tag 的辅助控件 |

如果你需要在自定义 Details 面板中复用这些自定义，可以通过公共接口：

```cpp
// 获取 FGameplayTag 的属性自定义实例
TSharedRef<IPropertyTypeCustomization> TagCustomization = 
    FGameplayTagCustomizationPublic::MakeInstance();

// 获取 FGameplayTagContainer 的属性自定义实例
TSharedRef<IPropertyTypeCustomization> ContainerCustomization = 
    FGameplayTagContainerCustomizationPublic::MakeInstance();

// 获取 RestrictedTag 的属性自定义实例
TSharedRef<IPropertyTypeCustomization> RestrictedCustomization = 
    FRestrictedGameplayTagCustomizationPublic::MakeInstance();
```

### 资产定义基类

`UAssetDefinition_GameplayTagAssetBase` 是为拥有 GameplayTag 的资产提供的基类。它在资产的右键菜单中添加 "Edit Gameplay Tags" 选项：

```cpp
// 在自定义资产定义中使用
UCLASS()
class UAssetDefinition_MyAsset : public UAssetDefinition_GameplayTagAssetBase
{
    GENERATED_BODY()
    // ... 重写 GetAssetCategories() 等方法
    
    // 在 MenuExtension 中调用基类方法来添加 Tag 编辑菜单项
    static void AddGameplayTagsEditMenuExtension(FToolMenuSection& InSection, 
        TArray<UObject*> InObjects)
    {
        UAssetDefinition_GameplayTagAssetBase::AddGameplayTagsEditMenuExtension(
            InSection, InObjects, GET_MEMBER_NAME_CHECKED(UMyAsset, GameplayTags));
    }
};
```

### Gameplay Tag Manager 窗口

```cpp
// 打开 Tag Manager 窗口
FGameplayTagManagerWindowArgs Args;
Args.Title = NSLOCTEXT("MyModule", "TagManager", "My Tag Manager");
Args.Filter = TEXT("Ability,Status");  // 可选过滤
Args.HighlightedTag = FGameplayTag::RequestGameplayTag(FName("Ability.Fire"));
Args.bRestrictedTags = false;
TWeakPtr<SGameplayTagPicker> Picker = UE::GameplayTags::Editor::OpenGameplayTagManager(Args);

// 或者创建一个独立的 SGameplayTagPicker 实例
TSharedRef<SGameplayTagPicker> Picker = UE::GameplayTags::Editor::Create(Args);
```

### Tag Query 编辑窗口

```cpp
// 打开 Query 编辑窗口
FGameplayTagQueryWindowArgs QueryArgs;
QueryArgs.Title = NSLOCTEXT("MyModule", "QueryEditor", "Edit Tag Query");
QueryArgs.Filter = TEXT("Weapon");
QueryArgs.bReadOnly = false;
QueryArgs.EditableQueries.Add(MyQuery);
QueryArgs.OnQueriesCommitted = SGameplayTagQueryWidget::FOnQueriesCommitted::CreateLambda(
    [](const TArray<FGameplayTagQuery>& Queries) {
        // 处理提交的 Query
    });
UE::GameplayTags::Editor::OpenGameplayTagQueryWindow(QueryArgs);
```

### 实用工具函数

`UE::GameplayTags::EditorUtilities` 命名空间提供 Tag 的导入/导出工具：

```cpp
#include "GameplayTagEditorUtilities.h"

// 导出 Tag 为文本
FString ExportedTag = UE::GameplayTags::EditorUtilities::GameplayTagExportText(MyTag);

// 从文本导入 Tag
FGameplayTag ImportedTag = UE::GameplayTags::EditorUtilities::GameplayTagTryImportText(TEXT("Ability.Fire"));

// 导出/导入 Container
FString ExportedContainer = UE::GameplayTags::EditorUtilities::GameplayTagContainerExportText(MyContainer);
FGameplayTagContainer ImportedContainer = UE::GameplayTags::EditorUtilities::GameplayTagContainerTryImportText(ExportedContainer);

// 导出/导入 Query
FString ExportedQuery = UE::GameplayTags::EditorUtilities::GameplayTagQueryExportText(MyQuery);
FGameplayTagQuery ImportedQuery = UE::GameplayTags::EditorUtilities::GameplayTagQueryTryImportText(ExportedQuery);

// 格式化 Query 描述为多行显示
FString Formatted = UE::GameplayTags::EditorUtilities::FormatGameplayTagQueryDescriptionToLines(QueryDesc);
```

## Demo 示例

### 最小可编译示例：自定义 Tag 选择面板

**MyTagEditorWidget.h**
```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "GameplayTagContainer.h"

class SMyTagEditorWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyTagEditorWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    void OnTagChanged(const FGameplayTag& NewTag);
    void OnContainerChanged(const FGameplayTagContainer& NewContainer);

    FGameplayTag CurrentTag;
    FGameplayTagContainer CurrentContainer;
};
```

**MyTagEditorWidget.cpp**
```cpp
#include "MyTagEditorWidget.h"
#include "SGameplayTagCombo.h"
#include "SGameplayTagContainerCombo.h"
#include "GameplayTagsEditorModule.h"

void SMyTagEditorWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            SNew(STextBlock).Text(FText::FromString(TEXT("Select a Tag:")))
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            SNew(SGameplayTagCombo)
                .Filter(TEXT("Ability"))
                .Tag(CurrentTag)
                .OnTagChanged_Raw(this, &SMyTagEditorWidget::OnTagChanged)
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            SNew(STextBlock).Text(FText::FromString(TEXT("Select Tag Container:")))
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(4)
        [
            SNew(SGameplayTagContainerCombo)
                .Filter(TEXT("Status"))
                .TagContainer(CurrentContainer)
                .OnTagContainerChanged_Raw(this, &SMyTagEditorWidget::OnContainerChanged)
        ]
    ];
}

void SMyTagEditorWidget::OnTagChanged(const FGameplayTag& NewTag)
{
    CurrentTag = NewTag;
    UE_LOG(LogTemp, Log, TEXT("Tag selected: %s"), *NewTag.ToString());
}

void SMyTagEditorWidget::OnContainerChanged(const FGameplayTagContainer& NewContainer)
{
    CurrentContainer = NewContainer;
    UE_LOG(LogTemp, Log, TEXT("Container has %d tags"), NewContainer.Num());
}
```

**YourModule.Build.cs** 依赖说明：
```csharp
PrivateDependencyModuleNames.AddRange(new string[]
{
    "GameplayTags",
    "GameplayTagsEditor",  // 仅在 Editor 模块中依赖
    "Slate",
    "SlateCore",
});
```

> ⚠️ 注意：`GameplayTagsEditor` 模块类型为 `UncookedOnly`，只能在编辑器模块中依赖。运行时模块不应依赖此模块。

## 模块依赖

本插件的 `GameplayTagsEditor` 模块依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 核心 Tag 运行时系统 |
| `Core` / `CoreUObject` / `Engine` | UE 基础框架 |
| `Slate` / `SlateCore` | UI 框架，所有 Tag 选择器控件基于 Slate |
| `UnrealEd` | 编辑器框架 |
| `BlueprintGraph` | 蓝图图表节点支持 |
| `KismetCompiler` | K2 节点编译支持 |
| `GraphEditor` | 蓝图图表编辑器 |
| `PropertyEditor` | Details 面板属性自定义 |
| `AssetTools` / `AssetRegistry` / `AssetDefinition` | 资产管理 |
| `ContentBrowser` / `ContentBrowserData` | 内容浏览器集成 |
| `InputCore` | 输入处理 |
| `SourceControl` | 版本控制集成（Tag 文件的 checkout） |
| `SettingsEditor` | 项目设置面板集成 |
| `ToolMenus` / `ToolWidgets` / `EditorWidgets` | 编辑器工具框架 |
| `ApplicationCore` | 应用核心功能 |
| `EditorStyle` / `EditorFramework` / `MainFrame` | 编辑器 UI 框架 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-03 | `14e5b5d7` | 为 Tag 自定义添加空指针检查，增加编辑器蓝图工具函数 |
| 2025-07-18 | `462ec4ed` | 修复 V623 警告：三元运算符中临时对象的创建和销毁问题 |
| 2025-07-10 | `9803c443` | 为有对应 .gen.cpp 的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` |

### 维护评价

- **创建时间**：2016-11-01，是 UE4.13 时代的产物
- **维护状态**：**活跃维护** — 最近 6 个月内有实质性更新（空指针检查修复）
- **更新频率**：约每 1-2 个月有更新，以 bug 修复和代码质量改进为主
- **核心稳定性**：功能非常成熟，近年来主要是小修小补而非大重构
- **已知限制**：
  - 模块类型为 `UncookedOnly`，运行时代码无法依赖
  - `FGameplayTagCustomizationOptions` 和 `FGameplayTagContainerCustomizationOptions` 已在 UE 5.3 中废弃
  - `UGameplayTagsK2Node_LiteralGameplayTag` 节点已废弃
- **推荐程度**：✅ 强烈推荐 — 这是 GameplayTags 系统不可或缺的编辑器配套插件，几乎所有使用 GameplayTags 的项目都默认启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/GameplayTagsEditor)
- [GameplayTags 运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/GameplayTags)
