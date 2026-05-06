# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器特性集 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 UI 组件、处理器、查询工厂、表定义） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

---

## 用途

该插件是 TEDS（Typed Element Data Storage）系统的编辑器侧功能扩展集合。TEDS 本身提供了一套基于类型化表格（Entity-Component 风格）的高性能数据存储方案，而 `EditorDataStorageFeatures` 则将这一底层能力转化为编辑器可直接使用的 UI 组件和数据处理管线。

每个独立模块（如 `TedsRevisionControl`、`TedsOutliner`、`TedsPropertyEditor`）分别解决编辑器中的一个具体场景：

- **版本控制集成**（`TedsRevisionControl`）：监听资源包文件的版本控制状态，在编辑器元素上应用颜色覆盖和图标叠加层，直观反映文件是否被修改、冲突、锁定等。
- **大纲视图**（`TedsOutliner`）：基于 TEDS 数据的世界大纲，替代传统的 `SWorldHierarchy`。
- **属性面板**（`TedsPropertyEditor`）：基于 TEDS 的详细面板，替代传统 `IDetailsView`。
- **资产数据**（`TedsAssetData`）：将资产注册表信息映射到 TEDS 表格，支持高效查询和过滤。
- **内容浏览器**（`TedsContentBrowser`）：基于 TEDS 的内容浏览替代方案。
- **类型信息**（`TedsTypeInfo`）：提供类型元数据的存储与访问。
- **查询堆栈**（`TedsQueryStack`）：调试和可视化 TEDS 查询的执行堆栈。
- **调试器**（`TedsDebugger`）：TEDS 调试工具 UI。

总之，该插件集群是 TEDS 系统在编辑器中的“官方”应用层，旨在逐步替换旧的编辑器 UI 实现。

---

## 使用场景

- **编辑器 UI 现代化**：如果你的编辑器模块希望基于 TEDS 构建更高效、可组合的 UI（如自定义大纲、属性面板、内容浏览），可以依赖这些模块作为起点或参考。
- **版本控制视觉反馈**：在自定义资源视图中，需要根据源控制状态（修改、新增、冲突等）更新元素颜色和图标，可以直接使用 `TedsRevisionControl` 的处理器，无需自行轮询 `ISourceControlModule`。
- **TEDS 学习参考**：插件中各模块的 `UEditorDataStorageFactory` 子类展示了如何注册表、查询和处理器，是 TEDS API 的最佳实践示例。

---

## 蓝图用法

当前插件所有模块均**不提供 `BlueprintCallable` 函数**，主要作为 C++ 框架供编辑器模块使用。蓝图端无法直接调用这些功能。

---

## C++ 用法

### 头文件引入

```cpp
// 根据使用的模块引入对应头文件
#include "Processors/RevisionControlProcessors.h" // TedsRevisionControl
#include "Queries/ObjectPackagePathToColumnQueries.h"
```

### 基本用法

以下示例展示了如何通过 `URevisionControlDataStorageFactory` 注册版本控制相关的表格、查询和处理器。该工厂在模块启动时自动被 TEDS 核心发现并调用。

**来源**：`Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsRevisionControl/Private/Processors/RevisionControlProcessors.h`

```cpp
// 1. 在模块 StartupModule 中不需要显式注册工厂，
//    URevisionControlDataStorageFactory 被 UCLASS 标记，TEDS 核心会自动收集。

// 2. 在 URevisionControlDataStorageFactory::RegisterTables 中定义自定义表格（如有）
void URevisionControlDataStorageFactory::RegisterTables(ICoreProvider& DataStorage)
{
    // 此处可调用 DataStorage.RegisterTable(...)
}

// 3. 在 RegisterQueries 中注册查询处理器，例如源控制状态更新
void URevisionControlDataStorageFactory::RegisterQueries(ICoreProvider& DataStorage)
{
    RegisterFetchUpdates(DataStorage);     // 异步获取 SCC 最新状态
    RegisterApplyOverlays(DataStorage);     // 将 SCC 状态映射为覆盖层（颜色+图标）
    RegisterRemoveOverlays(DataStorage);    // 当元素不再受 SCC 管理时清理覆盖层
    RegisterGeneralQueries(DataStorage);    // 处理选择变化、包引用等通用查询
}
```

### 进阶用法

如果需要手动触发版本控制覆盖层的更新（例如自定义扩展点），可调用工厂提供的工具方法：

```cpp
// 假设已获取到 URevisionControlDataStorageFactory* Factory
Factory->UpdateOverlaysForSCCState(DataStorage, &FTypedElementPackagePathColumn::StaticStruct());
// 上述调用会为所有包含 FTypedElementPackagePathColumn 的 SCC 行重新计算覆盖层。

Factory->UpdateOverlayColors(DataStorage);
// 刷新所有已应用覆盖层元素的前景色/背景色。
```

这些方法通常在内部查询处理器运行后被调用，但也可以根据外部事件（如自定义 SCC 插件）手动触发。

---

## Demo 示例

以下是一个最小化的编辑器模块，演示如何使用 `URevisionControlDataStorageFactory` 中的查询和更新逻辑。

### MyCppModule.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyCppModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MyCppModule.cpp

```cpp
#include "MyCppModule.h"
#include "Processors/RevisionControlProcessors.h"
#include "Elements/Interfaces/TypedElementDataStorageInterface.h"
#include "UObject/UObjectIterator.h"

IMPLEMENT_MODULE(FMyCppModule, MyCppModule);

void FMyCppModule::StartupModule()
{
    // 查找已有的 RevisionControlFactory（应在 TedsRevisionControl 模块启动时自动被创建）
    if (URevisionControlDataStorageFactory* Factory = FindObject<URevisionControlDataStorageFactory>())
    {
        // 获取 TEDS provider
        ITypedElementDataStorageInterface* Storage = ITypedElementDataStorageInterface::Get();
        if (Storage)
        {
            UE::Editor::DataStorage::ICoreProvider& Provider = Storage->GetCoreProvider();

            // 手动触发一次源控制状态更新（例如用户按下某个按钮）
            Factory->UpdateOverlaysForSCCState(&Provider, &FTypedElementPackagePathColumn::StaticStruct());
            Factory->UpdateOverlayColors(&Provider);
        }
    }
}

void FMyCppModule::ShutdownModule()
{
    // 无需特殊清理，TEDS 核心管理工厂生命周期
}
```

**注意**：实际使用时，通常由 `TedsRevisionControl` 内部的处理器自动执行，无需手动调用。此示例仅用于演示工厂公开的工具方法。

---

## 模块依赖

以下为使用 `TedsRevisionControl` 模块时，您的模块需要在 `Build.cs` 的 `PublicDependencyModuleNames` 中添加的依赖（仅列出独特、非标准依赖）：

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` | TEDS 核心数据存储接口与处理器框架 |
| `TypedElementDataStorageInterface` | 公开的 TEDS Provider 接口 |
| `TypedElementFramework` | 类型化元素框架基础（列、行句柄等） |
| `EditorSubsystem` | 编辑器子系统支持（用于 Factory 注册与生命周期） |
| `SourceControl` | 版本控制状态获取接口（`ISourceControlModule`） |
| `AssetRegistry` | 资源注册表（包路径列依赖） |

其他常见依赖（Core、CoreUObject、Engine、Slate、SlateCore 等）无需列出。

---

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` — Fix TedsType info assert when running certain Verse automated tests  
- 2025-10-02 `1f8278e6` — Re-enable Teds AssetData after resolving test and FName issues  
- 2025-09-26 `7d070444` — [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions  
- 2025-09-25 `8d9818a1` — [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)  
- 2025-09-25 `4161c053` — Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module  

### 维护评价

- **创建时间**：2025-09-25，距今约 1 个月，非常新的插件。
- **近期更新**：近两周内有多次功能性提交（修复、功能增强、新增查看器），更新活跃。
- **活跃度**：由 Epic 官方维护，当前处于实验性阶段，可能仍存在 API 变动和不稳定。
- **已知问题**：作为实验性插件，可能存在未公开的 bug，且不保证向前兼容。`IsExperimentalVersion=true` 表明 Epic 尚未将其视为稳定。
- **推荐使用**：仅供体验和早期评估。不建议在生产项目中使用，除非愿意承担 API 变更和潜在崩溃的风险。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [TedsRevisionControl 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsRevisionControl/Private/Processors/RevisionControlProcessors.h)
- [官方文档](https://docs.unrealengine.com/5.7/TEDS) (尚未提供，可关注 Epic 后续更新)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests) (当前未包含在用户提供的信息中)