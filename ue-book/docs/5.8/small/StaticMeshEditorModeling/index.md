# Static Mesh Editor Modeling Mode

> Enable a Modeling Tools Tab in the Static Mesh Editor

| 属性 | 值 |
|---|---|
| 中文名 | 静态网格编辑器建模模式 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StaticMeshEditorModeling` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-02-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StaticMeshEditorModeling) | |

## 用途

该插件将 Unreal Editor 的 **建模模式 (Modeling Mode)** 中的工具，以选项卡的形式集成到了 **静态网格编辑器 (Static Mesh Editor)** 中。它解决了在传统工作流中，用户若想对静态网格资产进行简单编辑（如拓扑调整、UV修改、属性设置等），必须切换到独立的建模编辑器或主编辑器建模模式，从而中断当前资产检查和编辑流程的问题。

通过此插件，美术或技术美术人员可以在同一个静态网格编辑器窗口内，直接访问建模工具，实现更流畅、高效的资产局部修改和迭代，无需在不同编辑器上下文间切换。

## 使用场景

- 你在静态网格编辑器中检查资产时，发现网格拓扑或UV需要微调，希望立即进行修改，而不用打开另一个窗口。
- 你是一位经常需要对网格进行程序化调整的创作者，希望在调整网格参数的同时，能快速使用平滑、切片等基础建模工具。

## 蓝图用法

该插件主要通过编辑器命令和工具栏按钮触发，没有公开的 `BlueprintCallable` 或 `BlueprintReadWrite` 函数。其交互主要发生在静态网格编辑器界面内部。

### 核心操作

| 操作 | 说明 | 所在类 |
|---|---|---|
| 切换建模模式 | 通过静态网格编辑器工具栏上的按钮，进入或退出建模模式。 | `FStaticMeshEditorModelingCommands` |

### 使用示例（界面描述）

1.  打开任意静态网格资产，进入其编辑器。
2.  在编辑器顶部工具栏，找到“**建模模式**”选项卡或按钮。
3.  点击后，编辑器界面将切换，左侧出现建模工具的调色板，中央视口变为交互式建模视图。
4.  从左侧调色板中选择一个工具（如 `Move`、`Sculpt`），即可在视口中对网格进行操作。
5.  完成后，可切换回其他选项卡（如 `LOD Settings`）以退出建模模式。

## C++ 用法

### 头文件引入

```cpp
#include "StaticMeshEditorModelingModule.h"
#include "StaticMeshEditorModelingMode.h"
```

### 基本用法

该插件的核心是提供了一个新的编辑器模式 (`UStaticMeshEditorModelingMode`)。在编辑器插件中，通常通过模块来管理和控制它。

```cpp
// 获取模块实例
FStaticMeshEditorModelingModule& ModelingModule = FModuleManager::GetModuleChecked<FStaticMeshEditorModelingModule>(TEXT("StaticMeshEditorModeling"));

// 检查给定的静态网格编辑器是否处于建模模式
// InEditor 是指向当前 IStaticMeshEditor 接口的弱指针
TWeakPtr<IStaticMeshEditor> EditorPtr = /* ... */;
bool bIsActive = ModelingModule.IsStaticMeshEditorModelingModeActive(EditorPtr);

// 手动触发切换建模模式 (通常由 UI 命令驱动)
ModelingModule.OnToggleStaticMeshEditorModelingMode(EditorPtr);
```

### 进阶用法

插件的 `UStaticMeshEditorModelingMode` 类继承自 `UBaseLegacyWidgetEdMode`，它负责创建和管理该模式下的工具集 (`FStaticMeshEditorModelingToolkit`)。在编辑器模式的生命周期中，`Enter()` 方法被调用以初始化模式。

## Demo 示例

一个最小的示例，展示如何在编辑器插件中查询和响应静态网格编辑器建模模式的状态。这模拟了其他编辑器工具需要感知当前是否处于建模模式的场景。

**MyEditorPlugin.h**
```cpp
// MyEditorPlugin.h
#pragma once

#include "CoreMinimal.h"

class FMyEditorPluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnStaticMeshEditorOpened(TSharedRef<IStaticMeshEditor> Editor);
};
```

**MyEditorPlugin.cpp**
```cpp
// MyEditorPlugin.cpp
#include "MyEditorPlugin.h"
#include "StaticMeshEditorModelingModule.h"

#define LOCTEXT_NAMESPACE "FMyEditorPluginModule"

void FMyEditorPluginModule::StartupModule()
{
    // 监听静态网格编辑器被打开的事件
    IStaticMeshEditorModule& StaticMeshEditorModule = FModuleManager::GetModuleChecked<IStaticMeshEditorModule>("StaticMeshEditor");
    StaticMeshEditorModule.OnStaticMeshEditorOpened().AddRaw(this, &FMyEditorPluginModule::OnStaticMeshEditorOpened);
}

void FMyEditorPluginModule::ShutdownModule()
{
    // 清理委托绑定...
}

void FMyEditorPluginModule::OnStaticMeshEditorOpened(TSharedRef<IStaticMeshEditor> Editor)
{
    // 获取建模模式模块
    FStaticMeshEditorModelingModule& ModelingModule = FModuleManager::GetModuleChecked<FStaticMeshEditorModelingModule>(TEXT("StaticMeshEditorModeling"));

    // 检查新打开的编辑器是否处于建模模式 (首次打开通常为 false)
    bool bInitiallyInModelingMode = ModelingModule.IsStaticMeshEditorModelingModeActive(Editor);
    UE_LOG(LogTemp, Log, TEXT("Static Mesh Editor opened. In Modeling Mode: %s"), bInitiallyInModelingMode ? TEXT("Yes") : TEXT("No"));

    // 这里可以添加其他逻辑，例如根据模式状态禁用/启用你插件中的某些功能
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorPluginModule, MyEditorPlugin);
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

该插件作为编辑器插件，其 `.Build.cs` 中通常依赖 `EditorCore`、`LevelEditor` 等编辑器模块，但这些对于编写编辑器插件来说是标准依赖，无需特别列出。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-20 | `2ce45174` | [Viewport ITF] Allow editor modes to opt-in to the new gizmos. When editor modes change, the ITF Tra... | 为新视口交互框架（ITF）更新了编辑器模式，允许选择启用新的 Gizmo，涉及编辑器模式切换时的处理。 |
| 2025-03-05 | `7ab43c2f` | Add and address deprecation warning after UEditorInteractiveToolsContext classes move to UnrealEd | 适配了 UEditorInteractiveToolsContext 类迁移到 UnrealEd 模块后产生的废弃警告。 |
| 2024-02-01 | `18df41a3` | Move StaticMeshEditorModeling into Editor plugins folder | 插件首次创建，从其他位置移入 Editor 插件文件夹。 |

### 维护评价

-   **创建时间**：插件于 2024 年 2 月创建，相对年轻。
-   **更新频率**：在创建后有实质性更新，最近一次在 2026 年 2 月，针对底层视口框架进行了适配，表明仍在跟随引擎核心发展。
-   **活跃状态**：**活跃维护中**。更新内容涉及核心功能框架的兼容性调整。
-   **已知限制**：插件本身标记为 `IsBetaVersion: true`，且默认未启用（`Installed: false`），表明 Epic 可能认为其功能或稳定性尚未达到正式发布标准，属于实验性功能。
-   **推荐使用**：对于需要频繁在静态网格编辑器内进行建模操作的用户，此插件能显著提升效率。但由于其 Beta 状态，在关键生产流程中使用需自行评估稳定性。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StaticMeshEditorModeling)
-   官方文档：暂无
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StaticMeshEditorModeling/Tests) （如果存在测试文件）