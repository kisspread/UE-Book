# Skeletal Mesh Editing Tools

> Create skeletons, paint skin weights and edit skeletal meshes.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Gizmo 材质） |
| 模块 | `SkeletalMeshModelingTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-09-14 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/SkeletalMeshModelingTools) | |

## 用途

Skeletal Mesh Editing Tools 是 UE5 骨骼网格编辑的核心插件。它在 Skeletal Mesh Editor（Persona）中注入了一个完整的 **Skeletal Mesh Editing Mode**，将 Unreal 的 Modeling Tools 框架能力扩展到了骨骼网格资产上。

这个插件解决的核心问题是：**UE5 之前没有内置的方式在编辑器中直接编辑骨骼网格的几何形状、蒙皮权重和骨骼结构**。艺术家必须依赖外部 DCC 工具（Maya、Blender）完成这些工作，然后重新导入。这个插件让你可以直接在 UE 编辑器内完成：

- **网格几何编辑** — 多边形编辑、雕刻、平滑、简化等（复用 ModelingTools 的工具集）
- **蒙皮权重绘制** — 直接在编辑器中绘制和绑定蒙皮权重
- **骨骼编辑** — 添加/删除/重命名/复制骨骼，修改骨骼层级
- **Morph Target 编辑** — 创建、编辑、重命名变形目标
- **Static Mesh → Skeletal Mesh 转换** — 将静态网格批量转换为骨骼网格

插件的设计思路是创建一个临时的 `USkeletalMeshBackedDynamicMeshComponent`（Dynamic Mesh）作为编辑代理，工具操作 Dynamic Mesh，完成后将修改提交回原始 SkeletalMesh 资产。这种架构允许复用所有现有的 ModelingTools，同时保持骨骼网格的特殊数据结构（骨骼层级、蒙皮权重、Morph Target）。

## 使用场景

- 你在 UE 中导入了一个角色骨骼网格，需要微调几何形状（比如调整脸部拓扑）→ 使用 **Polygon Edit** 或 **Sculpt Mesh** 工具
- 你需要从零开始绘制蒙皮权重，不想切回 Maya → 使用 **Skin Weights Paint** 工具
- 你需要在现有骨架上添加新骨骼（比如武器挂点）→ 使用 **Skeleton Editing** 工具（Ctrl+N 新建骨骼）
- 你有一批 Static Mesh 需要转为 SkeletalMesh 用于动画 → 右键 Content Browser → Convert Static Mesh to Skeletal Mesh
- 你需要创建和编辑 Blend Shape / Morph Target → 使用 Morph Target 管理面板
- 你需要对骨骼网格做 Remesh / Simplify 优化拓扑 → 使用 **Remesh** 或 **Simplify** 工具

## 蓝图用法

此插件主要是 Editor Mode 和工具集，不暴露 BlueprintCallable 函数。所有操作通过 Skeletal Mesh Editor 的工具面板 UI 完成。

### 核心快捷键

| 快捷键 | 功能 | 说明 |
|---|---|---|
| `Ctrl+N` | 新建骨骼 | 在选中骨骼下创建子骨骼 |
| `Delete` / `Backspace` | 删除骨骼 | 删除选中的骨骼 |
| `Shift+P` | 解除父级 | 将选中骨骼从层级中分离 |
| `F2` | 重命名骨骼 | 重命名选中的骨骼 |
| `Ctrl+C` | 复制骨骼 | 复制选中骨骼 |
| `Ctrl+V` | 粘贴骨骼 | 粘贴已复制的骨骼 |
| `Ctrl+D` | 复制骨骼 | 复制选中骨骼（含子层级） |

## C++ 用法

### 头文件引入

```cpp
#include "SkeletalMeshModelingModeToolExtensions.h"
```

### 扩展插件注册（IModularFeature）

第三方插件可以通过 `ISkeletalMeshModelingModeToolExtension` 接口向 Skeletal Mesh Editing Mode 注册自定义工具：

```cpp
// 来源: SkeletalMeshModelingModeToolExtensions.h
class ISkeletalMeshModelingModeToolExtension : public IModelingModeToolExtension
{
public:
    static FName GetModularFeatureName()
    {
        static FName FeatureName(TEXT("SkeletalMeshModelingModeToolExtension"));
        return FeatureName;
    }
};
```

注册方式：在你的插件模块 StartupModule 中通过 `IModularFeatures::Get().RegisterModularFeature()` 注册实现。

### Static Mesh → Skeletal Mesh 转换（C++ API）

```cpp
// 来源: SkeletalMeshModelingToolsMeshConverter.h
#include "SkeletalMeshModelingToolsMeshConverter.h"

// 交互式批量转换（弹出选项对话框）
TArray<FAssetData> StaticMeshAssets = /* 从 ContentBrowser 获取 */;
ConvertStaticMeshAssetsToSkeletalMeshesInteractive(StaticMeshAssets);
```

转换选项类 `UStaticMeshToSkeletalMeshConvertOptions` 支持：
- `EReferenceSkeletonImportOption` — 创建新骨架 / 使用已有骨架 / 使用已有骨骼网格的骨架
- `ERootBonePlacementOptions` — 根骨骼位置（底部中心 / 中心 / 原点）
- 命名规则 — 前缀/后缀替换（默认 `SM_` → `SKM_`）

### 编辑缓存 API

```cpp
// 来源: SkeletalMeshEditingCache.h
USkeletalMeshEditingCache* Cache = EditorMode->GetCurrentEditingCache();

// 检查是否有未提交的修改
bool bHasChanges = Cache->HasUnappliedChanges(); // (通过 EditorMode)

// 提交修改到 SkeletalMesh 资产
Cache->ApplyChanges();

// 丢弃修改
Cache->DiscardChanges();

// 获取编辑中的 DynamicMesh 组件
USkeletalMeshBackedDynamicMeshComponent* DynaMesh = Cache->GetEditingMeshComponent();

// Morph Target 操作
TArray<FName> MorphTargets = Cache->GetMorphTargets();
FName NewMorph = Cache->AddMorphTarget(FName("MyMorph"));
Cache->RenameMorphTarget(OldName, NewName);
Cache->RemoveMorphTargets({MorphName});
```

### DynamicMesh 组件 API

```cpp
// 来源: SKMBackedDynaMeshComponent.h
USkeletalMeshBackedDynamicMeshComponent* Comp = Cache->GetEditingMeshComponent();

// 获取引用骨架
const FReferenceSkeleton& RefSkel = Comp->GetRefSkeleton();

// 获取组件空间骨骼变换（RefPose）
const TArray<FTransform>& RefPoseTransforms = Comp->GetComponentSpaceBoneTransformsRefPose();

// 检查是否有修改
bool bDirty = Comp->IsDirty();
bool bSkelDirty = Comp->IsSkeletonDirty();
int32 Changes = Comp->GetChangeCount();

// 骨骼变更追踪
const auto& SkelTracker = Comp->GetSkeletonChangeTracker();
int32 SkelChangeCount = SkelTracker.GetChangeCount();

// Morph Target 变更追踪
const auto& MorphTracker = Comp->GetMorphTargetChangeTracker();
```

## Demo 示例

### 注册自定义工具扩展

```cpp
// MySkelMeshToolExtension.h
#pragma once
#include "SkeletalMeshModelingModeToolExtensions.h"

class FMySkelMeshToolExtension : public ISkeletalMeshModelingModeToolExtension
{
public:
    virtual void GetExtensionTools(
        const FExtensionToolQueryInfo& QueryInfo,
        TArray<FExtensionToolDescription>& ToolsOut) override;
};
```

```cpp
// MySkelMeshToolExtension.cpp
#include "MySkelMeshToolExtension.h"
#include "Features/IModularFeatures.h"

void FMySkelMeshToolExtension::GetExtensionTools(
    const FExtensionToolQueryInfo& QueryInfo,
    TArray<FExtensionToolDescription>& ToolsOut)
{
    FExtensionToolDescription Desc;
    Desc.ToolName = TEXT("MyCustomSkelTool");
    Desc.ToolCommand = /* 你的 FUICommandInfo */;
    Desc.ToolBuilder = NewObject<UMyCustomToolBuilder>();
    ToolsOut.Add(Desc);
}

// 在插件模块 StartupModule 中注册
void FMyPluginModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(
        ISkeletalMeshModelingModeToolExtension::GetModularFeatureName(),
        &Extension);
}
```

```csharp
// MyPlugin.Build.cs — 需要的依赖
PublicDependencyModuleNames.AddRange(new string[]
{
    "SkeletalMeshModelingTools",
    "ModelingToolsEditorMode",
    "InteractiveToolsFramework",
});
```

## 模块依赖

从 `SkeletalMeshModelingTools.Build.cs` 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（SkeletalMesh、Component 等） |
| `UnrealEd` | 编辑器框架 |
| `EditorFramework` | 编辑器基础架构 |
| `InteractiveToolsFramework` | 交互式工具框架基础 |
| `EditorInteractiveToolsFramework` | 编辑器交互式工具扩展 |
| `ModelingToolsEditorMode` | Modeling Tools 编辑器模式（父模式） |
| `MeshModelingTools` | 网格建模工具集（Sculpt、Simplify、Remesh 等） |
| `MeshModelingToolsEditorOnly` | 仅编辑器的建模工具 |
| `ModelingComponentsEditorOnly` | 仅编辑器的建模组件 |
| `ModelingComponents` | 建模组件（DynamicMesh 等） |
| `GeometryCore` | 几何核心库（DynamicMesh3 等） |
| `GeometryFramework` | 几何框架 |
| `MeshDescription` | 网格描述数据结构 |
| `StaticMeshDescription` | 静态网格描述 |
| `SkeletalMeshDescription` | 骨骼网格描述 |
| `MeshConversion` | 网格格式转换 |
| `SkeletalMeshEditor` | 骨骼网格编辑器（Persona） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格通用工具 |
| `SkeletalMeshModifiers` | 骨骼网格修改器 |
| `Persona` | Persona 编辑器框架 |
| `AnimationCore` | 动画核心库 |
| `AnimationWidgets` | 动画 UI 控件 |
| `Slate` / `SlateCore` | UI 框架 |
| `ToolMenus` | 工具菜单系统 |
| `ToolWidgets` | 工具 UI 控件 |
| `PropertyEditor` | 属性编辑器 |
| `ContentBrowser` | 内容浏览器集成 |
| `InputCore` | 输入系统 |
| `StatusBar` | 状态栏 |
| `ApplicationCore` | 应用核心 |
| `WidgetRegistration` | 控件注册 |
| `InterchangeEngine` | Interchange 导入/导出框架 |
| `EditorWidgets` | 编辑器控件库 |

> 注意：这些都是 **PrivateDependencyModuleNames**，即插件内部依赖。如果你只是想通过 `ISkeletalMeshModelingModeToolExtension` 扩展工具，只需要依赖 `SkeletalMeshModelingTools` 和 `ModelingToolsEditorMode` 即可。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-16 | `8b858c13` | 从 pending changelist 恢复（unshelved），包含 widget 模式修复 |
| 2025-10-16 | `1c26964c` | 修复使用 Dynamic Mesh 骨架时 widget 模式被错误禁用的问题 |
| 2025-09-29 | `8142ccf7` | 修正部分文本 |

### 维护评价

- **创建时间**：2022-09-14（最初在 `Experimental/Animation/` 下），2025-03-04 迁移到 `Animation/` 目录，表明已脱离实验阶段
- **最近更新**：2025-10-16，距今约 6 个月，仍在活跃维护
- **更新内容**：最近的更新集中在 bug 修复和 UI 完善，说明核心功能已经稳定
- **代码规模**：32 个源文件，中等规模，架构清晰
- **实验性状态**：`IsExperimentalVersion=false`，`IsBetaVersion=false`，正式版本
- **默认启用**：是，所有 UE5 项目默认可用

**综合评价**：这是一个**活跃维护**的核心编辑器功能插件。从 2022 年的实验性功能发展为正式工具集，已具备完整的骨骼网格编辑能力。Epic 持续投入维护，推荐在需要在 UE 内直接编辑骨骼网格时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/SkeletalMeshModelingTools)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 依赖插件：[ModelingToolsEditorMode](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ModelingToolsEditorMode)
