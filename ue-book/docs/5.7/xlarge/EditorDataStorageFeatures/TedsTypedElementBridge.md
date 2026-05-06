# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储特性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可能包含示例资产） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

TEDS（Typed Element Data Storage） 是 UE5 引入的编辑器底层数据管理框架，它以列式存储、查询驱动的方式管理编辑器中的各种元素（如 Actor、资产、UI 等）。`EditorDataStorageFeatures` 插件是在 TEDS 基础上提供的一系列 **编辑器 UI 特性模块**，包括：

- 内容浏览器与资产数据集成
- 大纲视图（Outliner）替换
- 属性编辑器增强
- 类型信息查看与查询调试
- 版本控制集成
- 提示与警报系统
- TypedElement 桥梁（将传统 Actor 的 TypedElement Handle 与 TEDS 同步）

这些特性旨在逐步替代标准编辑器中的旧有 UI 组件，提供更高效、更可扩展的数据驱动编辑体验。

## 使用场景

- 你正在开发基于 TEDS 的编辑器增强工具或自定义编辑器面板。
- 你希望启用基于 TEDS 的新版内容浏览器、大纲视图或属性编辑器。
- 你需要将现有的 TypedElement Handle 系统（如 Actor 的 TypedElement）与 TEDS 存储桥接，以利用 TEDS 的查询、过滤和排序能力。
- 你正在构建一个复杂的编辑器子系统，需要统一的、可持久化的数据视图和查询堆栈。

## 蓝图用法

> 由于 TEDS 框架主要面向 C++ 开发，且这些模块大多作为后台服务运行，公开的 Blueprint 节点非常有限。以下列出几个可能通过编辑器扩展或 `UEditorDataStorageFactory` 子类暴露的函数（需通过 C++ 注册到蓝图上下文）。

### 核心节点（按模块）

| 节点 | 说明 | 所在模块/类 |
|---|---|---|
| `IsTypedElementBridgeEnabled` | 查询 TypedElement Bridge 是否已启用 | `TedsTypedElementBridge` / `UEditorSubsystem` |
| `OnTypedElementBridgeEnabled` | 当 Bridge 启用状态变化时触发的事件 | `TedsTypedElementBridge` / 委托 |
| `GetColumnSort`（示例） | 获取 TEDS 表格视图的排序状态 | `TedsTableViewer` / 相关 Widget |

> 更丰富的蓝图集成需等待未来版本或自定义包装。

## C++ 用法

所有子模块均通过 `UEditorDataStorageFactory` 派生类自动注册到 TEDS 核心。下面以 **TedsTypedElementBridge** 为例展示如何与 TEDS 交互。

### 头文件引入

```cpp
#include "TedsTypedElementBridge/TedsTypedElementBridgeCapabilities.h"
#include "TedsTypedElementBridge/TedsTypedElementActorHandleFactory.h"
#include "TedsTypedElementBridge/TedsTypedElementBridgeQueries.h"
```

### 基本用法

**查询 TypedElement Bridge 是否启用：**

```cpp
using namespace UE::Editor::DataStorage::Compatibility;
if (IsTypedElementBridgeEnabled())
{
    // 可以放心使用 Bridge 功能同步 Actor 与 TEDS 数据
}
```

**监听 Bridge 启用/禁用事件：**

```cpp
// 绑定委托
FDelegateHandle Handle = OnTypedElementBridgeEnabled().AddLambda([](bool bEnabled)
{
    if (bEnabled)
    {
        // Bridge 刚被启用，初始化相关逻辑
    }
});
// 记得在生命周期结束时取消绑定
```

### 进阶用法

**注册自定义查询（在 `UEditorDataStorageFactory` 子类中）：**

```cpp
UCLASS()
class  UMyCustomFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
    
    virtual void PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 注册需要前置处理的回调
        DataStorage.OnInitialize().AddUObject(this, &UMyCustomFactory::OnDataStorageInitialized);
    }
    
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 注册一个定期查询，例如同步 Actor 的 Transform
        UE::Editor::DataStorage::QueryHandle TransformQuery = DataStorage.RegisterQuery(
            UE::Editor::DataStorage::FQueryDescription()
            .SetName("SyncActorTransform")
            .Include<FActorRowTag>()     // 假设自定义的列标签
            .SetExecution([this](const UE::Editor::DataStorage::IQueryContext& Context)
            {
                // 处理匹配的行
            })
        );
    }
    
    virtual void PreShutdown(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        DataStorage.OnInitialize().RemoveAll(this);
        // 清理注册的查询
    }
};
```

## Demo 示例

以下是一个最小可编译的编辑器模块，它利用 `TedsTypedElementBridge` 的功能在 TEDS 初始化时打印一条消息。

**MyTEDSDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "MyTEDSDemo.generated.h"

UCLASS()
class UMyTEDSDemoFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

    virtual void PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
};
```

**MyTEDSDemo.cpp**

```cpp
#include "MyTEDSDemo.h"
#include "TedsTypedElementBridge/TedsTypedElementBridgeCapabilities.h"
#include "Elements/Interfaces/TypedElementDataStorageInterface.h"

void UMyTEDSDemoFactory::PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 在 TEDS 初始化前绑定事件，确保 Bridge 状态变化时收到通知
    UE::Editor::DataStorage::Compatibility::OnTypedElementBridgeEnabled().AddLambda([](bool bEnabled)
    {
        if (bEnabled)
        {
            UE_LOG(LogTemp, Log, TEXT("TypedElement Bridge 已启用，TEDS 已就绪"));
        }
    });
}

void UMyTEDSDemoFactory::RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 注册一个一次性查询，在 TEDS 完全启动后立即执行
    DataStorage.RegisterQuery(
        UE::Editor::DataStorage::FQueryDescription()
        .SetName("MyStartupQuery")
        .SetExecution(UE::Editor::DataStorage::FQueryDescription::EEventType::OnInitialize)
        .SetCallback([](const UE::Editor::DataStorage::IQueryContext& Context)
        {
            UE_LOG(LogTemp, Log, TEXT("TEDS 已启动，当前激活的 Bridge: %s"),
                UE::Editor::DataStorage::Compatibility::IsTypedElementBridgeEnabled() ? TEXT("启用") : TEXT("禁用"));
        })
    );
}
```

> 将此类注册到模块的 StartupModule 中即可生效。完整模块还需要在 Build.cs 中依赖 `EditorDataStorage`、`TedsTypedElementBridge` 等模块。

## 模块依赖

使用本插件的任何模块，其 Build.cs 中的 `PublicDependencyModuleNames` 应包含以下 **独特依赖**（标准 Core/Engine/Slate 等已省略）：

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 核心框架：列式存储、查询、行列管理 |
| `TypedElementFramework` | TypedElement 系统基础（HTypedElementHandle、ITypedElementInterface 等） |
| `TedsTypedElementBridge` | 将 Actor 的 TypedElement 与 TEDS 桥接 |
| `TedsActorCompatibility` | 兼容性处理：Actor 与 TEDS 列映射 |
| `TedsAssetData` | 资产数据列定义与填充 |
| `TedsContentBrowser` | 基于 TEDS 的内容浏览器 UI |
| `TedsOutliner` | 基于 TEDS 的大纲视图 |
| `TedsPropertyEditor` | 基于 TEDS 的属性面板 |
| `TedsTypeInfo` | 类型信息查询与显示 |
| `TedsTableViewer` | 通用表格视图 |
| `TedsSettings` | TEDS 设置面板 |
| `TedsAlerts` | 警报系统 |
| `TedsRevisionControl` | 版本控制状态列 |
| `TedsEverythingPicker` | 通用拾取器 |
| `TedsDebugger` | TEDS 调试工具 |
| `TedsQueryStack` | 查询堆栈管理 |
| `TedsEditorCompatibility` | 与标准编辑器系统的兼容层 |

**注意**：如果你只使用某个子模块（如 `TedsTypedElementBridge`），仅需依赖该模块以及 `EditorDataStorage` 和 `TypedElementFramework` 即可，其余模块按需添加。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` Fix TedsType info assert when running certain Verse automated tests  
- 2025-10-02 `1f8278e6` Re-enable Teds AssetData after resolving test and FName issues  
- 2025-09-26 `7d070444` [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions on the TEDS S  
- 2025-09-25 `8d9818a1` [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)  
- 2025-09-25 `4161c053` Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module (TedsOutlinerFilter to  

### 维护评价

- **创建时间**：2025年9月（约 1 个月），非常新。  
- **更新频率**：几乎每天都在活跃开发（从提交日志看是连续提交），修改内容包括 Bug 修复、新功能（复合查看器、筛选条）、持久化排序等，属于活跃维护。  
- **实验性状态**：`IsExperimentalVersion: true`，API 仍在快速演化，可能存在不兼容变更。  
- **推荐使用**：适合愿意跟进最新编辑器开发的前沿用户，用于评估或早期集成。对于生产项目建议谨慎，因为可能缺乏长期稳定性承诺。  

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档](https://docs.unrealengine.com/5.5/en-US/editor-data-storage-overview/) (TEDS 概览，待更新至 5.7)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests) (未在主仓库单独列出，可搜索 `TEDS` 相关自动化测试文件)