# UAF Chooser

> Chooser integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFChooser` (Runtime), `UAFChooserEditor` (Runtime), `UAFChooserUncookedOnly` (Runtime), `UAFChooserTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser) | |

## 用途

UAFChooser 是 Unreal Animation Framework (UAF) 与 Chooser 系统之间的集成插件。它解决了在 UAF 动画框架中使用 Chooser 表（ChooserTable）进行动画资产选择和混合的问题。

核心价值在于：
- **Chooser 动画表**：提供 `UUAFAnimChooserTable` 资产类型，用于在 UAF 图表中定义动画选择逻辑
- **共享变量支持**：通过 `UAFSharedVariables` 支持跨动画状态共享变量，实现更灵活的动画参数控制
- **图工厂集成**：Chooser 返回的资产可以是任何已注册 UAF Graph Factory 的类型，实现多态动画资产选择

## 使用场景

- 你需要基于运行时条件（如速度、方向、状态）动态选择不同动画资产 → 用 UAF Chooser Table
- 你在构建复杂的动画状态机，需要在多个动画之间进行条件选择 → 用 Chooser 集成
- 你需要在动画图表中使用共享变量来控制动画参数 → 用 UAFSharedVariables
- 你正在使用 UAF 框架构建动画系统，需要更灵活的动画选择机制 → 用此插件

## 蓝图用法

此插件主要通过资产类型和编辑器模式工作，核心交互通过 UAFAnimChooserTable 资产进行。

### 核心资产类型

| 资产类型 | 说明 |
|---|---|
| `UUAFAnimChooserTable` | UAF 动画选择器表，定义动画选择规则 |
| `UUAFSharedVariables` | UAF 共享变量资产，存储跨状态共享的动画参数 |

### 编辑器功能

| 功能 | 说明 |
|---|---|
| UAF Chooser Editor Mode | 专用编辑器模式，用于编辑 Chooser 表 |
| Workspace Outliner 集成 | 在工作空间大纲中显示和管理 Chooser 项目 |

## C++ 用法

### 头文件引入

```cpp
#include "UAFChooserEditorModule.h"
```

### 基本用法 - 自定义 Chooser 初始化器

```cpp
// 自定义 UAF 动画 Chooser 初始化器
// 来源: Private/UAFAnimationChooserInitializer.h
USTRUCT(DisplayName="UAF Animation Chooser", 
        meta=(ToolTip="A ChooserTable for use with the ChooserPlayer UAF Trait.\n"
              "Returns any type of Asset which has a registered UAF Graph Factory."))
struct FUAFAnimationChooserInitializer : public FChooserInitializer
{
    GENERATED_BODY()
    
    // 初始化 Chooser 签名
    virtual void InitializeSignature(UChooserSignature* Chooser) const override;
    
    // 覆盖默认类
    virtual UClass* OverrideClass(UClass* Class) const override;

    // 共享变量资产数组
    UPROPERTY(EditAnywhere, Category = "Shared Variables")
    TArray<TObjectPtr<UUAFSharedVariables>> SharedVariablesAssets;
};
```

### 进阶用法 - 资产定义

```cpp
// 自定义 UAF Anim Chooser Table 的资产定义
// 来源: Private/UAFChooserTableAssetDefinition.h
UCLASS()
class UAssetDefinition_UAFAnimChooserTable : public UAssetDefinitionDefault
{
    GENERATEDATED_BODY()

public:
    virtual FText GetAssetDisplayName() const override 
    { 
        return LOCTEXT("UAFAnimChooserTable", "UAF Anim Chooser Table"); 
    }
    
    virtual const FSlateBrush* GetThumbnailBrush(
        const FAssetData& InAssetData, const FName InClassName) const override;
    
    virtual const FSlateBrush* GetIconBrush(
        const FAssetData& InAssetData, const FName InClassName) const override;
    
    virtual FLinearColor GetAssetColor() const override 
    { 
        return FLinearColor(FColor(100, 100, 50)); 
    }
    
    virtual TSoftClassPtr<UObject> GetAssetClass() const override 
    { 
        return UUAFAnimChooserTable::StaticClass(); 
    }
    
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override;
    
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override
    {
        static const auto Categories = { 
            FAssetCategoryPath(EAssetCategoryPaths::Animation, 
                              LOCTEXT("UAFSubMenu", "Animation Framework")) 
        };
        return Categories;
    }
    
    virtual bool ShouldSaveExternalPackages() const override { return true; }
};
```

## Demo 示例

### UAF Chooser Editor Mode 基础实现

```cpp
// UAFChooserEditorMode.h
#pragma once

#include "EdMode.h"
#include "UAFChooserEditorMode.generated.h"

UCLASS(MinimalAPI, Transient)
class UUAFChooserEditorMode : public UEdMode
{
    GENERATED_BODY()
    
public:
    const static FEditorModeID EM_UAFChooser;
    
    UUAFChooserEditorMode();

    virtual void Enter() override;
    virtual void Exit() override;
    virtual void CreateToolkit() override;
    virtual void BindCommands() override;
};

// UAFChooserEditorMode.cpp
#include "UAFChooserEditorMode.h"
#include "UAFChooserEditorModeToolkit.h"

const FEditorModeID UUAFChooserEditorMode::EM_UAFChooser("EM_UAFChooser");

UUAFChooserEditorMode::UUAFChooserEditorMode()
{
    Info = FEditorModeInfo(
        EM_UAFChooser,
        LOCTEXT("UAFChooserEditorMode", "UAF Chooser"),
        FSlateIcon(),
        true // bVisible
    );
}

void UUAFChooserEditorMode::Enter()
{
    UEdMode::Enter();
    // 初始化编辑器模式
}

void UUAFChooserEditorMode::Exit()
{
    UEdMode::Exit();
    // 清理编辑器模式
}

void UUAFChooserEditorMode::CreateToolkit()
{
    Toolkit = MakeShareable(new FUAFChooserEditorModeToolkit(this));
}

void UUAFChooserEditorMode::BindCommands()
{
    // 绑定编辑器命令
}
```

### Workspace Outliner 项目详情

```cpp
// ChooserOutlinerItemDetails.h
#pragma once

#include "WorkspaceItem.h"

namespace UE::UAF::ChooserEditor
{
    class FChooserOutlinerItemDetails : public Workspace::IWorkspaceOutlinerItemDetails
    {
    public:
        virtual ~FChooserOutlinerItemDetails() override = default;
        
        virtual FString GetDisplayString(
            const FWorkspaceOutlinerItemExport& Export) const override;
        
        virtual FSlateColor GetItemColor(
            const FWorkspaceOutlinerItemExport& Export) const override;
        
        virtual const FSlateBrush* GetItemIcon(
            const FWorkspaceOutlinerItemExport& Export) const override;
        
        virtual bool HandleDoubleClick(
            const FToolMenuContext& ToolMenuContext) const override;
        
        virtual bool CanDelete(
            const FWorkspaceOutlinerItemExport& Export) const override;
        
        virtual void Delete(
            TConstArrayView<FWorkspaceOutlinerItemExport> Exports) const override;
        
        virtual bool CanRename(
            const FWorkspaceOutlinerItemExport& Export) const override;
        
        virtual void Rename(
            const FWorkspaceOutlinerItemExport& Export, 
            const FText& InName) const override;
        
        virtual bool ValidateName(
            const FWorkspaceOutlinerItemExport& Export, 
            const FText& InName, 
            FText& OutErrorMessage) const override;
    };
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | Unreal Animation Framework 核心模块（必需依赖） |
| `Chooser` | Chooser 系统核心，提供选择器表基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 添加修改器动画节点基类，支持单子节点动画节点 |
| 2026-03-19 | `910301d3` | UAF Anim Node rewind debugger track | 添加 UAF 动画节点回退调试轨道 |
| 2026-03-11 | `bda4ef8e` | Add debug update counter to UAF anim node to enforce invariants | 为 UAF 动画节点添加调试更新计数器以强制不变量 |
| 2026-03-11 | `7da85466` | Implement AnimOp system for new UAF runtime | 实现新 UAF 运行时的 AnimOp 系统 |
| 2026-03-10 | `5a95823d` | AnimNodes Blend stack helper class to avoid too much code duplication (it can be used as either a b... | AnimNodes 混合栈辅助类，减少代码重复 |

### 维护评价

**活跃维护中**

- **创建时间**：2025-06-27，约 1 年前
- **更新频率**：2026 年 3-4 月有多次密集更新，非常活跃
- **维护状态**：活跃开发中，不断有新功能（AnimOp 系统、调试工具、混合栈）添加
- **已知限制**：作为实验性插件，API 可能不稳定，不建议用于生产环境
- **推荐程度**：适合早期采用者和实验性项目，不推荐生产使用

该插件是 UAF 动画框架的核心组件之一，正在快速迭代开发中。如果你正在使用或计划使用 UAF 框架，这个插件将是你动画工作流的重要组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser)
- [UAF 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF)