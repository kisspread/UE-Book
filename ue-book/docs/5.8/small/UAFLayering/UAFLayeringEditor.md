# UAF Layering

> Framework to define a layering setup in UAF（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动画分层框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工作区集成、资产定义） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

`UAFLayering` 插件为 Unreal Animation Framework (UAF) 提供了一个**动画分层系统**。它的核心目标是允许动画师和开发者定义复杂的动画混合逻辑，通过将动画数据组织成可配置的“层栈”(Layer Stack)来实现。这解决了在复杂角色动画中管理多个动画状态、优先级和混合权重的问题，通常用于实现诸如“在基础移动上叠加战斗动作”或“分层播放表情和肢体动画”等高级功能。插件提供了从资产定义、编辑器工具到运行时支持的完整工作流。

## 使用场景

-   你需要在一个角色上同时播放和混合多个动画（例如：跑步基础动画 + 挥剑动作 + 呼吸晃动）。
-   你正在使用 UAF 动画系统，并需要一个可视化的工具来创建和预览动画层的混合效果。
-   你的项目需要复杂的动画状态管理，需要定义层之间的覆盖、加法或优先级规则。

## 蓝图用法

### 核心资产

| 节点 | 说明 | 所在类 |
|---|---|---|
| 创建 LayerStack 资产 | 在内容浏览器中右键创建 `UUAFLayerStack` 资产。 | `UUAFLayerStackFactory` |
| 资产显示信息 | 定义 `UUAFLayerStack` 资产在编辑器中的名称、颜色和分类。 | `UAssetDefinition_UAFLayerStack` |

### 工作区与项目浏览器集成

| 节点 | 说明 | 所在类 |
|---|---|---|
| 项目浏览器项目详情 | 控制 `UUAFLayerStack` 资产及其内部层在“工作区”项目浏览器中的显示图标、行为（如双击、选择）和默认展开状态。 | `ULayerStackItemDetails`, `ULayerStackLayerItemDetails` |

## C++ 用法

### 头文件引入

```cpp
#include "UAFLayeringEditorModule.h"
```

### 基本用法（资产操作）

此示例展示了如何定义自定义资产类型的行为，源自 `UAFLayerStackAssetDefinition.h`。

```cpp
// 来自 UAFLayerStackAssetDefinition.h
UCLASS()
class UAssetDefinition_UAFLayerStack : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    // 自定义资产在内容浏览器中的显示名称
    virtual FText GetAssetDisplayName() const override;
    // 自定义资产在内容浏览器中的颜色标识
    virtual FLinearColor GetAssetColor() const override;
    // 指向此资产定义对应的 UObject 类型
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    // 定义资产所属的右键菜单分类
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    // 定义双击打开资产时执行的操作（例如打开自定义编辑器）
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override;
};
```

### 进阶用法（工作区视口控制）

此示例展示了如何向工作区预览场景中添加用于动画分层预览的网格体，源自 `LayerStackViewportController.h`。

```cpp
// 来自 LayerStackViewportController.h
class FLayerStackViewportController : public Workspace::IWorkspaceViewportController
{
public:
    // 进入工作区视口时调用
    virtual void OnEnter(const FViewportContext& InViewportContext) override;
    // 离开工作区视口时调用，用于清理资源
    virtual void OnExit(FAdvancedPreviewScene* PreviewScene) override;

private:
    // 将骨骼网格体添加到预览场景中，并应用UAF系统和LayerStack进行动画分层预览
    void AddMeshToPreview(
        FAdvancedPreviewScene* PreviewScene,
        const TObjectPtr<const UUAFSystem> System,
        const TObjectPtr<const UUAFLayerStack> LayerStack,
        USkeletalMesh* InSkeletalMesh
    );
    
    TArray<AActor*> PreviewActors; // 存储预览场景中的Actor，便于清理
};
```

## Demo 示例

一个最小示例，展示如何为自定义资产定义编辑器行为。

**MyLayerStackAssetDefinition.h**
```cpp
#pragma once

#include "AssetDefinitionDefault.h"
#include "MyLayerStackAssetDefinition.generated.h"

UCLASS()
class UMyLayerStackAssetDefinition : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    virtual FText GetAssetDisplayName() const override;
    virtual FLinearColor GetAssetColor() const override;
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override;
};
```

**MyLayerStackAssetDefinition.cpp**
```cpp
#include "MyLayerStackAssetDefinition.h"
// 假设你的自定义LayerStack类头文件
#include "MyLayerStack.h"
// 用于打开自定义编辑器
#include "MyLayerStackEditor.h"

#define LOCTEXT_NAMESPACE "AssetDefinition_MyLayerStack"

FText UMyLayerStackAssetDefinition::GetAssetDisplayName() const
{
    return LOCTEXT("AssetName", "My Layer Stack");
}

FLinearColor UMyLayerStackAssetDefinition::GetAssetColor() const
{
    return FLinearColor(FColor::Cyan); // 用青色标识
}

TSoftClassPtr<UObject> UMyLayerStackAssetDefinition::GetAssetClass() const
{
    return UMyLayerStack::StaticClass();
}

TConstArrayView<FAssetCategoryPath> UMyLayerStackAssetDefinition::GetAssetCategories() const
{
    // 将资产放入 UAF -> Layering 分类下
    static const FAssetCategoryPath Categories[] = { FAssetCategoryPath(LOCTEXT("UAF", "UAF")) / LOCTEXT("Layering", "Layering") };
    return Categories;
}

EAssetCommandResult UMyLayerStackAssetDefinition::OpenAssets(const FAssetOpenArgs& OpenArgs) const
{
    for (UMyLayerStack* LayerStack : OpenArgs.LoadObjects<UMyLayerStack>())
    {
        // 假设有一个自定义的编辑器窗口类 FMyLayerStackEditor
        // FMyLayerStackEditor::CreateEditor(EToolkitMode::Standalone, {}, LayerStack);
    }
    return EAssetCommandResult::Handled;
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Workspace` | 提供工作区（Workspace）框架，用于集成项目浏览器、视口控制器等编辑器功能。 |
| `UAF` | Unreal Animation Framework 的核心模块，提供动画系统基础架构。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏升级为更现代的 UE_LOGF 格式。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名函数以更准确地反映其获取或添加组件的功能。 |
| 2026-03-05 | `dd5531fb` | UAF Layering: | 提交信息不完整，可能为后续更新埋下伏笔。 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新了UAF的混合配置文件。 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | 设置工作区项目浏览器中的层栈项目默认为展开状态，提升易用性。 |

### 维护评价

`UAFLayering` 是一个**非常新**的插件，创建于 2026 年初，并且从 git 历史看在 2026 年 3-4 月期间有持续的活跃开发。最近的更新集中在代码优化、重构和改善用户体验上。

**主要特点与风险**：
- **实验性**：明确标记为 `IsExperimentalVersion`，且默认未启用 (`EnabledByDefault: false`)，意味着其 API 和功能在未来版本中可能发生重大变更。
- **依赖性强**：作为 UAF 框架的一部分，其稳定性与成熟度受制于 UAF 核心的演进。
- **功能聚焦**：目前代码主要围绕编辑器集成（工作区、资产定义）展开，运行时核心逻辑可能仍在快速迭代中。

**建议**：可以作为前沿功能进行探索和原型开发，但**不建议**在需要长期稳定维护的项目中作为关键依赖使用。需要密切关注 Epic 官方的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- 官方文档：暂无
- 测试用例：[Engine/Plugins/Experimental/UAF/UAFLayering/Tests/UAFLayeringTests/](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests/UAFLayeringTests/)