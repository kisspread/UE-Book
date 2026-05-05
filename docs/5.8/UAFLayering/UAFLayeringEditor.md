# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产模板） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAF Layering 是 Unreal Animation Framework（UAF）的动画分层子系统。它提供了一套 **Layer Stack（层栈）** 资产框架，允许开发者以结构化的方式定义动画层的叠加关系。

核心解决的问题：在复杂的动画系统中，多个动画效果（如基础运动、上半身瞄准、面部表情、布料物理等）需要按优先级和混合规则叠加播放。UAF Layering 将这些层组织为一个可复用的 Layer Stack 资产，并通过 Workspace 编辑器提供可视化的编辑体验。

该插件是 UAF 生态的一部分，依赖 AnimNext 模块和 Workspace 插件，面向需要精细控制动画分层的项目。

## 使用场景

- 你需要为角色定义多层动画叠加（基础 locomotion + 上半身 additive + 面部 morph）→ 用 UAF Layering 创建 Layer Stack 资产
- 你需要在编辑器中可视化预览动画分层效果 → 该插件集成了 Workspace 视口控制器，支持骨骼网格体预览
- 你的项目使用 UAF 动画框架，需要标准化的分层工作流 → 通过 Layer Stack 统一管理动画层

## 蓝图用法

本模块（UAFLayeringEditor）为编辑器模块，不直接暴露蓝图节点。核心蓝图 API 位于运行时模块 `UAFLayering` 中，主要围绕 Layer Stack 资产的创建和操作。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UAFLayerStack` | 动画层栈资产，定义一组动画层的叠加配置 |
| `UAFSystem` | UAF 系统对象，管理动画层栈的运行时实例化 |

### 编辑器集成

编辑器模块通过 Workspace 系统提供以下功能：

| 功能 | 说明 |
|---|---|
| 资产创建 | 通过 `UUAFLayerStackFactory` 在内容浏览器中创建 Layer Stack 资产 |
| 资产定义 | `UAssetDefinition_UAFLayerStack` 定义资产在内容浏览器中的显示名称、颜色和分类 |
| 编辑器模式 | `UUAFLayeringEditorMode` 提供专用的编辑器模式 |
| 视口预览 | `FLayerStackViewportController` 在 Workspace 中预览骨骼网格体的分层效果 |

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "UAFLayeringEditorModule.h"

// 资产工厂
#include "UAFLayerStackFactory.h"

// 资产定义
#include "UAFLayerStackAssetDefinition.h"

// 视口控制器
#include "LayerStackViewportController.h"
```

### 基本用法 — 自定义资产定义

`UAssetDefinition_UAFLayerStack` 展示了如何为自定义资产类型注册编辑器集成：

```cpp
// 来源: Private/UAFLayerStackAssetDefinition.h
UCLASS()
class UAssetDefinition_UAFLayerStack : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    // 资产在内容浏览器中的显示名称
    virtual FText GetAssetDisplayName() const override;
    
    // 资产在内容浏览器中的颜色标识
    virtual FLinearColor GetAssetColor() const override;
    
    // 关联的 UObject 类
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    
    // 资产分类路径（出现在哪个右键菜单分类下）
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    
    // 双击打开资产时的行为
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override;
};
```

### 进阶用法 — Workspace 集成

编辑器模块通过 Workspace 系统注册自定义文档和面包屑导航：

```cpp
// 来源: Private/UAFLayeringEditorModule.h
namespace UE::UAF::LayeringEditor
{
    class FUAFLayeringEditorModule : public IModuleInterface
    {
    public:
        virtual void StartupModule() override;
        virtual void ShutdownModule() override;

    private:
        // 为 Workspace 创建自定义文档 Widget
        TSharedRef<SWidget> MakeDocumentWidget(
            const UE::Workspace::FWorkspaceEditorContext& InContext);
        
        // 注册面包屑导航路径
        void GetBreadcrumbTrail(
            const UE::Workspace::FWorkspaceEditorContext& InContext,
            TArray<TSharedPtr<UE::Workspace::FWorkspaceBreadcrumb>>& OutBreadcrumbs);
    };
}
```

### 进阶用法 — 视口预览控制器

`FLayerStackViewportController` 展示了如何在 Workspace 视口中预览动画分层效果：

```cpp
// 来源: Private/Workspace/LayerStackViewportController.h
namespace UE::UAF::LayeringEditor
{
    class FLayerStackViewportController : public Workspace::IWorkspaceViewportController
    {
    public:
        // 进入视口时添加预览 Actor
        virtual void OnEnter(const FViewportContext& InViewportContext) override;
        
        // 退出视口时清理预览 Actor
        virtual void OnExit(FAdvancedPreviewScene* PreviewScene) override;

    private:
        // 将骨骼网格体添加到预览场景
        void AddMeshToPreview(
            FAdvancedPreviewScene* PreviewScene,
            const TObjectPtr<const UUAFSystem> System,
            const TObjectPtr<const UUAFLayerStack> LayerStack,
            USkeletalMesh* InSkeletalMesh);
        
        TArray<AActor*> PreviewActors;
    };
}
```

## Demo 示例

以下示例展示如何创建一个自定义的 Workspace Outliner Item Details，用于控制 Layer Stack 中各层的显示行为：

```cpp
// MyLayerItemDetails.h
#pragma once

#include "IWorkspaceOutlinerItemDetails.h"

class UMyLayerItemDetails : public UE::Workspace::IWorkspaceOutlinerItemDetails
{
public:
    // 默认展开层级
    virtual bool IsExpandedByDefault() const override { return true; }
    
    // 自定义显示字符串
    virtual FString GetDisplayString(
        const FWorkspaceOutlinerItemExport& Export) const override;
    
    // 自定义图标
    virtual const FSlateBrush* GetItemIcon(
        const FWorkspaceOutlinerItemExport& Export) const override;
    
    // 选中时的行为
    virtual bool HandleSelected(const FToolMenuContext& ToolMenuContext) const override;
    
    // 双击时的行为
    virtual bool HandleDoubleClick(const FToolMenuContext& ToolMenuContext) const override;
};
```

```cpp
// MyLayerItemDetails.cpp
#include "MyLayerItemDetails.h"

FString UMyLayerItemDetails::GetDisplayString(
    const FWorkspaceOutlinerItemExport& Export) const
{
    // 从 Export 中获取层名称并格式化显示
    if (FString* Name = Export.FindProperty<FString>("LayerName"))
    {
        return FString::Printf(TEXT("Layer: %s"), **Name);
    }
    return TEXT("Unknown Layer");
}

const FSlateBrush* UMyLayerItemDetails::GetItemIcon(
    const FWorkspaceOutlinerItemExport& Export) const
{
    return FAppStyle::GetBrush("ClassIcon.AnimSequence");
}

bool UMyLayerItemDetails::HandleSelected(
    const FToolMenuContext& ToolMenuContext) const
{
    // 选中层时高亮对应的属性面板
    return true;
}

bool UMyLayerItemDetails::HandleDoubleClick(
    const FToolMenuContext& ToolMenuContext) const
{
    // 双击层时打开层编辑器
    return true;
}
```

## 模块依赖

从源码头文件的 `#include` 和 `.uplugin` 的 Plugins 依赖推断：

| 模块 | 用途 |
|---|---|
| `Workspace` | 编辑器 Workspace 框架，提供 Outliner、视口控制器等基础设施 |
| `AnimNext` | UAF 的动画运行时框架（AnimNextRigVMAssetEditorData、AnimNextModule） |
| `UAF` | UAF 核心模块（UAFLayerStack、UAFSystem 等运行时类型） |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-10 `797a6da6` Rename GetComponent to GetOrAddComponent to match functionality
- 2026-03-05 `dd5531fb` UAF Layering:
- 2026-03-04 `d9a06590` Update UAF blend profiles
- 2026-03-04 `95766f52` UAF Layering: Expand outliner items per default

### 维护评价

- **创建时间**：2026-03-04，全新插件
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标记为实验性
- **版本号**：0.1，处于早期开发阶段
- **模块结构**：4 个模块（Runtime、Editor、UncookedOnly、Tests），结构完整，说明设计较为成熟
- **Workspace 集成**：深度集成 Workspace 编辑器框架，表明这是 Epic 正在推进的动画工具链的一部分

⚠️ **警告**：此插件标记为实验性（Experimental），API 可能在后续版本中发生重大变更。不建议在生产项目中直接依赖，建议仅用于原型开发和技术预研。

**推荐程度**：如果你的项目正在使用 UAF/AnimNext 动画框架，可以关注此插件的演进；否则建议等待其从 Experimental 毕业后再评估采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- 官方文档：暂无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)