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
| 创建时间 | 2025-08-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Workspace) | |

---

## 用途

Workspace 插件是一个**实验性**的编辑器框架，允许在统一的用户界面中同时打开和编辑多个资产。它通过一个可配置的“工作区”（Workspace）来组织资产，每个工作区可以绑定特定的 `UWorkspaceSchema`，从而限定支持的资产类型。

该插件解决了传统编辑器一次只能编辑一个资产（或通过单独的编辑器窗口）的局限性，提供一个多文档界面（MDI）+ 大纲视图（Outliner）的环境，适合需要频繁在多个关联资产之间切换的工作流（例如关卡蓝图、动画蓝图、材质实例等）。它还支持**视图端口**（Viewport）图表编辑器集成以及**导出项**（Export）的层次化管理。

由于处于早期实验阶段，该插件尚未开放给所有用户，需要手动启用（`EnabledByDefault=false`），API 和功能随时可能发生大改。

---

## 使用场景

- 你正在制作一个复杂的 Blueprint 或 Control Rig，需要在同一个编辑器窗口中同时编辑相关图表和配置资产。
- 你需要在动画图表、状态机和 blendspace 之间快速跳转，而不打开多个独立编辑器。
- 你希望将多个资产（如关卡、蓝图、材质）组织到一个逻辑工作区中，统一管理选项卡和大纲视图。
- 你正在开发一个自定义的编辑器工具，希望提供类似 Substance Designer 或 Logic Pro 那样的“面板式”工作环境。

---

## 蓝图用法

该插件主要面向 C++ 扩展，蓝图中可用的类和服务非常有限。目前暴露的 BlueprintType 类只有 `UWorkspaceFactory`，但其功能仅限于创建新的工作区资产，并未提供直接的蓝图节点用于操作工作区内容。

### 核心节点（仅限 C++/编辑器脚本）

由于插件实验性且 API 未标记 `BlueprintCallable`，蓝图无法直接调用大多数编辑器功能。建议使用 C++ 实现自定义工作区行为。

---

## C++ 用法

### 头文件引入

```cpp
#include "IWorkspaceEditor.h"
#include "IWorkspaceEditorModule.h"
#include "WorkspaceSchema.h"
#include "WorkspaceFactory.h"
#include "WorkspaceAssetRegistryInfo.h"
```
来源：`Source/WorkspaceEditor/Public/IWorkspaceEditor.h` 等

### 基本用法

#### 1. 创建和打开工作区

```cpp
// 通过 UWorkspaceFactory 创建新的工作区资产
UWorkspaceFactory* Factory = NewObject<UWorkspaceFactory>();
Factory->SetSchemaClass(UDefaultWorkspaceSchema::StaticClass()); // 使用默认 schema

UObject* Asset = Factory->FactoryCreateNew(
    UWorkspace::StaticClass(),
    GetTransientPackage(),
    FName(TEXT("MyWorkspace")),
    RF_Standalone | RF_Public,
    nullptr,
    nullptr
);

// 打开工作区编辑器
UAssetEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UAssetEditorSubsystem>();
Subsystem->OpenEditorForAsset(Asset);
```
来源：`Source/WorkspaceEditor/Public/WorkspaceFactory.h`

#### 2. 自定义 WorkspaceSchema

继承 `UWorkspaceSchema` 以定义工作区支持的资产类型和视图行为：

```cpp
// MyCustomSchema.h
#include "WorkspaceSchema.h"
#include "MyCustomSchema.generated.h"

UCLASS()
class UMyCustomSchema : public UWorkspaceSchema
{
    GENERATED_BODY()

public:
    virtual FText GetDisplayName() const override
    {
        return FText::FromString(TEXT("My Custom Workspace"));
    }

    // 仅支持 SkeletalMesh 和 AnimBlueprint 资产
    virtual TConstArrayView<FTopLevelAssetPath> GetSupportedAssetClassPaths() const override
    {
        static TArray<FTopLevelAssetPath> SupportedPaths = {
            FTopLevelAssetPath(TEXT("/Script/Engine"), TEXT("SkeletalMesh")),
            FTopLevelAssetPath(TEXT("/Script/Engine"), TEXT("AnimBlueprint"))
        };
        return SupportedPaths;
    }

    // 可选：持久化工作区状态
    virtual void OnSaveWorkspaceState(TSharedRef<UE::Workspace::IWorkspaceEditor> InEditor,
                                      FInstancedStruct& OutState) const override
    {
        // 保存自定义状态
    }
};
```
来源：`Source/WorkspaceEditor/Public/WorkspaceSchema.h`

#### 3. 通过 IWorkspaceEditor 操作文档

```cpp
// 在编辑器模块中获取 IWorkspaceEditor
void FMyModule::OpenAssetsInCurrentWorkspace()
{
    // 假设已有 IWorkspaceEditor 实例
    TSharedPtr<UE::Workspace::IWorkspaceEditor> WorkspaceEditor = /* ... */;

    // 打开一组资产
    TArray<FAssetData> AssetsToOpen;
    // ... 填充资产 ...
    WorkspaceEditor->OpenAssets(AssetsToOpen);

    // 获取当前打开的所有 UStaticMesh 资产
    TArray<UObject*> Meshes;
    WorkspaceEditor->GetOpenedAssetsOfClass(UStaticMesh::StaticClass(), Meshes);

    // 在详情面板中显示特定对象
    TArray<UObject*> Selection = { MyObject };
    WorkspaceEditor->SetDetailsObjects(Selection);
}
```
来源：`Source/WorkspaceEditor/Public/IWorkspaceEditor.h`

### 进阶用法

#### 自定义 Outliner 项（Export）

你可以注册 `IWorkspaceOutlinerItemDetails` 的派生类来控制大纲视图中每个条目的显示、颜色、右键菜单等：

```cpp
class FMyOutlinerDetails : public UE::Workspace::IWorkspaceOutlinerItemDetails
{
    virtual FString GetDisplayString(const FWorkspaceOutlinerItemExport& Export) const override
    {
        if (Export.HasData())
        {
            // 根据 Export 中存储的自定义数据生成显示文本
            return Export.GetData().Get<FMyExportData>().Name.ToString();
        }
        return Export.GetIdentifier().ToString();
    }

    virtual const FSlateBrush* GetItemIcon(const FWorkspaceOutlinerItemExport& Export) const override
    {
        // 返回自定义图标
        return FMyStyle::Get().GetBrush(TEXT("MyIcon"));
    }

    // 更多方法：GetItemColor, HandleDoubleClick, CanDelete, Rename ...
};
```
来源：`Source/WorkspaceEditor/Public/IWorkspaceOutlinerItemDetails.h`

#### 集成视图端口

如果你的 WorkspaceSchema 支持 Viewport，可重写 `SupportsViewport()` 并创建 `UWorkspaceViewportSceneDescription`：

```cpp
virtual bool SupportsViewport() const override { return true; }

virtual TObjectPtr<UWorkspaceViewportSceneDescription> CreateSceneDescription() const override
{
    return NewObject<UWorkspaceViewportSceneDescription>();
}
```
视图端口将通过 `SWorkspaceViewport` 控件显示，支持自由视角和预览资产。

---

## Demo 示例

一个完整的 C++ 模块，展示如何创建自定义 WorkspaceSchema 并注册到编辑器。

### MyWorkspacePlugin.h

```cpp
#pragma once

#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyWorkspacePluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MyWorkspacePlugin.cpp

```cpp
#include "MyWorkspacePlugin.h"
#include "WorkspaceSchema.h"
#include "WorkspaceFactory.h"
#include "AssetToolsModule.h"
#include "IAssetTools.h"

IMPLEMENT_MODULE(FMyWorkspacePluginModule, MyWorkspacePlugin);

void FMyWorkspacePluginModule::StartupModule()
{
    // 注册自定义 WorkspaceSchema
    // 可在 Editor 模块的 StartupModule 中调用，使 UFactory 使用该 Schema
    // 此处仅为概念演示，实际注册方式取决于插件需求
}

UWorkspaceFactory* CreateCustomWorkspaceFactory()
{
    UWorkspaceFactory* Factory = NewObject<UWorkspaceFactory>();
    // 假设已定义 UMyCustomSchema
    // Factory->SetSchemaClass(UMyCustomSchema::StaticClass());
    return Factory;
}
```

**注意**：该插件目前没有公开的 `RegisterWorkspaceSchema` 或类似机制，Schema 的绑定需要在 `UWorkspaceFactory` 创建时手动设置。更完整的集成需要参考 `IWorkspaceEditorModule` 中的注册 API。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WorkspaceEditor` | 插件唯一模块，必须依赖 |
| `AssetTools` | 处理资产类型和工厂 |
| `EditorFramework` | 编辑器核心框架（FBaseAssetToolkit 等） |
| `WorkspaceUIFramework` | 工作区 UI 组件（SWorkspaceView 等） |
| `SceneOutliner` | 大纲视图（WorkspaceOutliner 基于此） |
| `StructUtils` | 使用 FInstancedStruct 存储自定义数据 |
| `GraphEditor` | 图表文档 SGraphDocument 支持 |

**特殊依赖**：以下模块非标准，需要手动添加（在 Build.cs 中列出）：
- `WorkspaceEditor`（自身）
- `SceneOutliner`（用于大纲模式）
- `StructUtils`（用于 InstancedStruct）
- `GraphEditor`（用于图文档）

其余依赖均为标准 Editor 模块（Core, Engine, Slate, UnrealEd 等），无需额外声明。

---

## 维护状态

### 近期更新

```
2025-09-12  41051563  添加“在新标签页中打开”功能，针对折叠节点和函数节点的上下文菜单
2025-08-29  1d7d2cdb  修复某些无 PCH 配置缺少 GCObject.h 包含的问题
2025-08-22  fce2a29c  UAF: 修复创建/撤销/重做函数时的崩溃
2025-08-20  b0efc88e  修复工作区编辑器中慢速文档导航问题
2025-08-19  e2419b2a  [回退] - CL44983746
```

### 维护评价

该插件于 2025 年 8 月创建，处于非常早期的开发阶段（Version 0.1，实验性标记）。最近一个月内有多次功能性更新和 bug 修复，说明仍在活跃开发中。但 API 尚不稳定，大量类为内部/私有，缺少文档和测试。推荐仅用于探索性实验或需要该特定多资产编辑功能的早期原型，**不建议在生产项目中依赖**。

---

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Workspace)
- [WorkspaceEditor 模块头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Workspace/Source/WorkspaceEditor/Public/IWorkspaceEditor.h)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Workspace/Tests)（可能为空或不完整）