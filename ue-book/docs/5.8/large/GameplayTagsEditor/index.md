# GameplayTagsEditor

> GameplayTagsEditor provides blueprint nodes and editor UI to enable the use of GameplayTags for tagging assets and objects

| 属性 | 值 |
|---|---|
| 中文名 | 游戏标签编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayTagsEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-11-01 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GameplayTagsEditor) | |

## 用途

GameplayTagsEditor 是 GameplayTags 运行时模块的**编辑器侧伴侣插件**。GameplayTags 运行时提供了 `FGameplayTag`、`FGameplayTagContainer`、`FGameplayTagQuery` 等核心数据结构，而本插件则为这些结构提供完整的编辑器支持：

1. **属性面板自定义**：当你在 C++ 或蓝图中暴露 `FGameplayTag` / `FGameplayTagContainer` 类型的 `UPROPERTY` 时，Details 面板会自动显示交互式标签选择器 UI（树形视图 + 搜索 + 勾选），而非默认的结构体编辑器。
2. **蓝图 K2 节点**：提供基于标签的 Switch 分支节点、多重比较节点等特殊蓝图节点，支持在蓝图中高效地按标签路由逻辑。
3. **标签库管理**：提供完整的标签 CRUD 操作——新增标签、重命名（自动创建重定向器）、删除、在不同标签源之间迁移、清理未使用的标签。
4. **标签源管理**：创建和管理标签源文件（基于 INI 配置）。
5. **可复用编辑器控件**：提供 `SGameplayTagPicker`、`SGameplayTagWidget`、`SGameplayTagCombo` 等 Slate 控件，其他编辑器工具或自定义面板可以嵌入使用。

简单来说：没有这个插件，GameplayTags 在编辑器中就只是一个不可交互的结构体字段；有了它，你才能真正可视化地管理标签系统。

## 使用场景

- 你在创建一个 Gameplay Ability System（GAS）项目 → 用标签控制技能激活、效果应用的条件
- 你需要为资产（动画、蒙太奇、音效等）打标签以便分类检索 → 用 Details 面板的标签选择器
- 你需要在蓝图中根据不同标签执行不同逻辑 → 用 Switch on GameplayTag 节点
- 你需要管理数百个标签的生命周期（添加、重命名、清理） → 用标签管理窗口
- 你在开发编辑器工具需要嵌入标签选择器 → 用 `MakeGameplayTagWidget` / `MakeGameplayTagContainerWidget`

## 蓝图用法

本插件的核心蓝图功能通过 K2 节点实现，这些节点在蓝图编辑器中以特殊节点形式出现。

### 核心 K2 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Switch on GameplayTag` | 根据输入的单个 GameplayTag 走不同执行分支（类似 Switch on Enum） | `UGameplayTagsK2Node_SwitchGameplayTag` |
| `Switch on GameplayTagContainer` | 根据输入的 TagContainer 走不同执行分支 | `UGameplayTagsK2Node_SwitchGameplayTagContainer` |
| `Multi Compare GameplayTagAssetInterface` | 对实现了 `IGameplayTagAssetInterface` 的对象，同时检查多个 TagContainer 是否匹配 | `UGameplayTagsK2Node_MultiCompareGameplayTagAssetInterface` |
| `Multi Compare GameplayTagAssetInterface SingleTags` | 同上，但检查的是单个 Tag 而非 Container | `UGameplayTagsK2Node_MultiCompareGameplayTagAssetInterfaceSingleTags` |
| `Multi Compare GameplayTagContainer` | 对单个 TagContainer，同时检查多个标签条件 | `UGameplayTagsK2Node_MultiCompareGameplayTagContainer` |
| `Multi Compare GameplayTagContainer SingleTags` | 同上，但检查单个标签 | `UGameplayTagsK2Node_MultiCompareGameplayTagContainerSingleTags` |

### 属性面板中的标签选择

当你在 C++ 或蓝图中声明如下属性时，Details 面板会自动显示标签选择器：

```cpp
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gameplay")
FGameplayTag MyTag;

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gameplay")
FGameplayTagContainer MyTags;
```

可通过 `meta = (Categories = "Skill.Damage,Status.Buff")` 限制可选标签范围。

### 使用示例（蓝图描述）

**Switch on GameplayTag 节点**：
1. 在蓝图中右键搜索 "Switch on GameplayTag"
2. 节点左侧有一个 Tag 输入引脚
3. 右侧默认有 1 个 Case 引脚，在节点 Details 面板中可添加更多 Pin
4. 每个 Case Pin 对应一个 GameplayTag 值
5. 运行时，输入 Tag 与哪个 Case 匹配就走哪条分支

**Multi Compare 节点**：
1. 添加 "Multi Compare GameplayTagAssetInterface" 节点
2. 连接一个实现了 `IGameplayTagAssetInterface` 的对象引脚
3. 在节点 Details 面板中设置要比较的标签数量和具体标签
4. 所有条件都满足时走 True 分支，否则走 False 分支

## C++ 用法

### 头文件引入

```cpp
#include "GameplayTagsEditorModule.h"
```

### 基本用法——获取模块实例并管理标签

```cpp
// 获取 GameplayTagsEditor 模块实例
if (IGameplayTagsEditorModule::IsAvailable())
{
    IGameplayTagsEditorModule& TagsEditor = IGameplayTagsEditorModule::Get();
    
    // 新增标签到 INI 配置
    TagsEditor.AddNewGameplayTagToINI(
        TEXT("Ability.Skill.Fireball"),       // 标签名
        TEXT("火球术技能标签"),                   // 注释
        NAME_None,                            // 标签源（默认）
        false,                                // 是否为受限标签
        true                                  // 是否允许非受限子标签
    );
    
    // 重命名标签（自动创建重定向器）
    TagsEditor.RenameTagInINI(
        TEXT("Ability.Skill.Fireball"),
        TEXT("Ability.Skill.FireBlast"),
        true  // 同时重命名子标签
    );
    
    // 删除标签
    // 需要先获取 TagNode，通常通过 GameplayTagsManager 获取
    TagsEditor.DeleteTagFromINI(TagNodeToDelete);
    
    // 更新标签信息（修改注释、受限状态等）
    TagsEditor.UpdateTagInINI(
        TEXT("Ability.Skill.FireBlast"),
        TEXT("更新后的注释"),
        false,  // 是否受限
        true    // 允许非受限子标签
    );
}
```

### 基本用法——在自定义编辑器工具中嵌入标签选择器

```cpp
// 创建一个可嵌入的标签选择控件
TSharedPtr<FGameplayTag> MyTag = MakeShareable(new FGameplayTag());

TSharedRef<SWidget> TagWidget = IGameplayTagsEditorModule::Get().MakeGameplayTagWidget(
    FOnSetGameplayTag::CreateLambda([](const FGameplayTag& NewTag)
    {
        UE_LOG(LogTemp, Log, TEXT("Selected tag: %s"), *NewTag.ToString());
    }),
    MyTag,
    TEXT("Ability")  // 过滤器：只显示 Ability 开头的标签
);

// 创建标签容器选择控件
TSharedPtr<FGameplayTagContainer> MyContainer = MakeShareable(new FGameplayTagContainer());

TSharedRef<SWidget> ContainerWidget = IGameplayTagsEditorModule::Get().MakeGameplayTagContainerWidget(
    FOnSetGameplayTagContainer::CreateLambda([](const FGameplayTagContainer& NewContainer)
    {
        UE_LOG(LogTemp, Log, TEXT("Tags updated, count: %d"), NewContainer.Num());
    }),
    MyContainer,
    TEXT("Status,Ability")  // 过滤器：显示 Status 或 Ability 开头的标签
);
```

### 进阶用法——迁移标签源与查找未使用标签

```cpp
// 将标签从一个源迁移到另一个源
TArray<FString> TagsToMove = { TEXT("Ability.Old.Tag1"), TEXT("Ability.Old.Tag2") };
TArray<FString> OutMovedTags;
TArray<FString> OutFailedTags;

IGameplayTagsEditorModule::Get().MoveTagsBetweenINI(
    TagsToMove,
    FName("NewTagSource"),
    OutMovedTags,
    OutFailedTags
);

// 查找项目中未被任何资产引用的标签
TArray<TSharedPtr<FGameplayTagNode>> UnusedTags;
IGameplayTagsEditorModule::Get().GetUnusedGameplayTags(UnusedTags);

for (const auto& TagNode : UnusedTags)
{
    UE_LOG(LogTemp, Warning, TEXT("Unused tag: %s"), *TagNode->GetCompleteTagString());
}

// 添加临时标签（仅当前编辑器会话有效，不会写入配置文件）
IGameplayTagsEditorModule::Get().AddTransientEditorGameplayTag(TEXT("Debug.TempTag"));
```

### 进阶用法——使用属性自定义（Property Customization）

本插件自动注册了 `FGameplayTag`、`FGameplayTagContainer`、`FGameplayTagQuery` 的属性自定义。如果你需要为自定义结构体（包含标签子结构）使用相同的自定义 UI，可以使用公开的自定义类：

```cpp
// 在自定义属性自定义中嵌入标签选择器
#include "GameplayTagsEditorModule.h"

class FMyStructCustomization : public IPropertyTypeCustomization
{
    virtual void CustomizeHeader(TSharedRef<IPropertyHandle> PropertyHandle,
        FDetailWidgetRow& HeaderRow,
        IPropertyTypeCustomizationUtils& Utils) override
    {
        // 获取子属性的 GameplayTag 自定义
        auto TagCustomization = FGameplayTagCustomizationPublic::MakeInstance();
        
        HeaderRow
        .NameContent()
        [
            PropertyHandle->CreatePropertyNameWidget()
        ]
        .ValueContent()
        [
            // 嵌入标签选择器
            SNew(SGameplayTagCombo)
            .PropertyHandle(PropertyHandle->GetChildHandle(GET_MEMBER_NAME_CHECKED(FMyStruct, MyTag)))
        ];
    }
};
```

## Demo 示例

一个最小的编辑器工具示例，在自定义窗口中嵌入标签选择器：

### MyTagEditorWindow.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "GameplayTagContainer.h"

class SMyTagEditorWindow : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyTagEditorWindow) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    void OnTagChanged(const FGameplayTag& NewTag);
    void OnTagsContainerChanged(const FGameplayTagContainer& NewContainer);

    FGameplayTag SelectedTag;
    FGameplayTagContainer SelectedTags;
};
```

### MyTagEditorWindow.cpp

```cpp
#include "MyTagEditorWindow.h"
#include "GameplayTagsEditorModule.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBox.h"

void SMyTagEditorWindow::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        // 单标签选择
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("选择单个标签:")))
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10, 0, 10, 10)
        [
            IGameplayTagsEditorModule::Get().MakeGameplayTagWidget(
                FOnSetGameplayTag::CreateSP(this, &SMyTagEditorWindow::OnTagChanged),
                MakeShareable(new FGameplayTag(SelectedTag)),
                TEXT("")  // 不过滤
            )
        ]
        // 标签容器选择
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("选择标签容器:")))
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10, 0, 10, 10)
        [
            IGameplayTagsEditorModule::Get().MakeGameplayTagContainerWidget(
                FOnSetGameplayTagContainer::CreateSP(this, &SMyTagEditorWindow::OnTagsContainerChanged),
                MakeShareable(new FGameplayTagContainer(SelectedTags))
            )
        ]
    ];
}

void SMyTagEditorWindow::OnTagChanged(const FGameplayTag& NewTag)
{
    SelectedTag = NewTag;
    UE_LOG(LogTemp, Log, TEXT("Tag selected: %s"), *NewTag.ToString());
}

void SMyTagEditorWindow::OnTagsContainerChanged(const FGameplayTagContainer& NewContainer)
{
    SelectedTags = NewContainer;
    UE_LOG(LogTemp, Log, TEXT("Container updated, %d tags"), NewContainer.Num());
}
```

## 模块依赖

> 注：以下基于源码分析推断。`GameplayTagsEditor.Build.cs` 未直接提供，以下为该插件独特依赖项。

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 核心运行时标签数据结构（FGameplayTag、FGameplayTagContainer 等） |
| `GameplayTagsEditor` (自身) | 编辑器属性自定义、K2 节点、标签管理 UI |

其他标准依赖（无需特别关注）：Core, CoreUObject, Engine, UnrealEd, Slate, SlateCore, PropertyEditor, BlueprintGraph, KismetCompiler, EditorStyle, InputCore。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 迁移到新版 UE_LOGF 宏 |
| 2026-04-07 | `6c0a082a` | [Backout] - CL52460521 | 回退之前的一次改动 |
| 2026-04-06 | `141e29a7` | Splitting Tag ini into multiple based on parent level tag. | 将标签 INI 配置按父标签层级拆分为多个文件 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. | 废弃旧版对象遍历 API，适配引擎 API 变更 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2016 年 11 月，与 GameplayTags 系统重构同步诞生（Ben.Zeigler 将其从引擎内部分离为独立插件）
- **最近更新**：2026 年 5 月仍有提交，最近的改动包含功能性更新（标签 INI 拆分）和维护性修复（编译警告、API 迁移）
- **维护频率**：近 2 个月内有 5 次提交，保持活跃
- **重要性**：作为 GameplayTags 在编辑器中的唯一交互入口，任何使用 GameplayTags 的项目（几乎所有使用 GAS 的项目）都依赖此插件
- **风险提示**：虽然插件本身稳定，但 2026 年 4 月的 INI 拆分改动（`141e29a7`）可能影响现有项目的标签配置文件结构，升级时需注意迁移

**推荐使用**：✅ 强烈推荐。这是 GameplayTags 系统不可或缺的编辑器伴侣，且默认启用，无需额外配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GameplayTagsEditor)
- [GameplayTags 运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Source/Runtime/GameplayTags)（本插件的运行时基础）