# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储 UI 功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器 UI 资源） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 是基于 TEDS（Typed Element Data Storage，类型化元素数据存储）构建的编辑器 UI 功能集合。TEDS 本身是一个 ECS（Entity-Component-System）风格的数据存储引擎，而本插件在其之上实现了 Unreal 编辑器各核心面板的数据驱动化：

- **Outliner 面板改造**：将传统的 Actor 列表替换为 TEDS 查询驱动的表格视图，支持批量操作和高性能筛选
- **Content Browser 集成**：资产数据存储到 TEDS 中，支持更高效的资产浏览和查询
- **Property Editor 桥接**：通过 Typed Element Bridge 将传统 UObject 系统与 TEDS 连接，使得属性编辑器可以读写 TEDS 中的数据
- **统一收藏夹**：跨面板的统一收藏系统
- **版本控制集成**：在 TEDS 层面支持 SCM 状态查询
- **调试工具**：TEDS 数据的可视化调试器

本质上，这个插件是 Epic 将编辑器 UI 从"直接操作 UObject"迁移到"ECS 数据驱动"架构的关键实验性工作。

## 模块架构

本插件包含 17 个模块，按功能可分为以下几类：

| 分类 | 模块 | 职责 |
|---|---|---|
| **核心桥接** | `TedsTypedElementBridge` | 连接 Typed Element 系统与 TEDS，管理 Actor/Object 句柄的生命周期 |
| **编辑器兼容** | `TedsActorCompatibility`, `TedsEditorCompatibility` | 确保传统 Actor 和编辑器系统能在 TEDS 中正常工作 |
| **UI 面板** | `TedsOutliner`, `TedsContentBrowser`, `TedsPropertyEditor`, `TedsTableViewer`, `TedsEverythingPicker` | TEDS 驱动的编辑器面板实现 |
| **数据层** | `TedsAssetData`, `TedsTypeInfo`, `TedsQueryStack` | 资产数据、类型信息、查询栈管理 |
| **功能扩展** | `TedsOperations`, `TedsAlerts`, `TedsRevisionControl`, `UnifiedFavorites` | 批量操作、告警、版本控制、收藏夹 |
| **开发工具** | `TedsDebugger`, `TedsSettings` | 调试器、设置管理 |

## 使用场景

- 你在开发需要高性能 Actor 列表展示的编辑器工具 → 用 TedsOutliner
- 你需要构建自定义的资产查询/筛选面板 → 用 TedsContentBrowser + TedsQueryStack
- 你的插件需要与 TEDS 数据系统交互但仍在使用传统 UObject → 用 TedsTypedElementBridge
- 你需要批量操作大量 Actor（设置属性、移动、删除等）→ 用 TedsOperations
- 你需要在编辑器中可视化 TEDS 数据进行调试 → 用 TedsDebugger

## 蓝图用法

本插件主要面向 C++ 编辑器扩展，蓝图可用的接口有限。TedsTypedElementBridge 模块暴露了以下运行时能力：

### 核心节点

| 函数 | 说明 | 所在类/命名空间 |
|---|---|---|
| `IsTypedElementBridgeEnabled()` | 查询 Typed Element Bridge 是否已启用 | `UE::Editor::DataStorage::Compatibility` |
| `OnTypedElementBridgeEnabled()` | 获取 Bridge 启用状态变更的多播委托 | `UE::Editor::DataStorage::Compatibility` |

### 使用示例

由于 TEDS 系统本身是 ECS 架构，与蓝图的交互主要通过订阅 Bridge 启用状态来实现：

1. 调用 `IsTypedElementBridgeEnabled()` 检查当前 Bridge 是否激活
2. 通过 `OnTypedElementBridgeEnabled().AddDynamic()` 订阅状态变更事件
3. 在回调中根据 `bEnabled` 参数决定是否启用依赖 TEDS 的功能

## C++ 用法

### 头文件引入

```cpp
#include "TedsTypedElementBridge/TedsTypedElementBridgeCapabilities.h"
```

### 基本用法

检查 Typed Element Bridge 启用状态：

```cpp
#include "TedsTypedElementBridge/TedsTypedElementBridgeCapabilities.h"

void MyEditorFunction()
{
    // 检查 Bridge 是否启用
    if (UE::Editor::DataStorage::Compatibility::IsTypedElementBridgeEnabled())
    {
        // TEDS Bridge 已激活，可以安全地使用 TEDS 数据
    }

    // 订阅启用状态变更
    UE::Editor::DataStorage::Compatibility::OnTypedElementBridgeEnabled().AddLambda(
        [](bool bEnabled)
        {
            UE_LOG(LogTemp, Log, TEXT("TEDS Bridge %s"), 
                bEnabled ? TEXT("enabled") : TEXT("disabled"));
        });
}
```

### 进阶用法

通过 `UEditorDataStorageFactory` 子类注册自定义 TEDS 查询。TedsTypedElementBridge 中的两个 Factory 类展示了标准模式：

```cpp
// TedsTypedElementBridgeQueries.h 中的标准模式
UCLASS(Transient)
class UMyDataStorageFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    // 控制 Factory 执行顺序
    virtual uint8 GetOrder() const override { return 100; }
    
    // TEDS 初始化前的准备工作
    virtual void PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
    
    // 注册数据查询
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
    
    // TEDS 关闭前的清理
    virtual void PreShutdown(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;

private:
    UE::Editor::DataStorage::QueryHandle MyQuery = UE::Editor::DataStorage::InvalidQueryHandle;
};
```

TedsTypedElementActorHandleFactory 展示了如何为特定 Actor 类型注册句柄查询：

```cpp
// 为 Actor 注册 Typed Element 句柄
void UTypedElementActorHandleDataStorageFactory::PreRegister(
    UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 注册 Actor 和 ActorComponent 的句柄查询
    RegisterQuery_ActorHandlePopulate(DataStorage);
    RegisterQuery_ActorComponentHandlePopulate(DataStorage);
    
    // 订阅 Bridge 启用事件
    BridgeEnableDelegateHandle = 
        UE::Editor::DataStorage::Compatibility::OnTypedElementBridgeEnabled()
            .AddUObject(this, &UTypedElementActorHandleDataStorageFactory::HandleBridgeEnabled);
}

void UTypedElementActorHandleDataStorageFactory::HandleBridgeEnabled(bool bEnabled)
{
    if (bEnabled)
    {
        // Bridge 启用：激活 Actor 句柄填充查询
    }
    else
    {
        // Bridge 禁用：清理已注册的句柄
    }
}
```

**来源**: `Source/TedsTypedElementBridge/Private/TedsTypedElementBridge/TedsTypedElementActorHandleFactory.h`

## Demo 示例

以下是一个最小的自定义 TEDS Factory，展示如何在插件中使用 TEDS Bridge 模式：

```cpp
// MyTedsFactory.h
#pragma once

#include "Elements/Framework/TypedElementRegistry.h"
#include "EditorDataStorageFactory.h"

UCLASS(Transient)
class UMyTedsFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    virtual uint8 GetOrder() const override { return 128; }
    
    virtual void PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 初始化阶段：注册列类型、事件监听等
    }
    
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 注册查询：获取符合特定条件的实体并执行操作
    }
    
    virtual void PreShutdown(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 清理资源
    }

private:
    UE::Editor::DataStorage::QueryHandle MyCleanupQuery = 
        UE::Editor::DataStorage::InvalidQueryHandle;
};
```

```cpp
// MyTedsFactory.cpp
#include "MyTedsFactory.h"
#include "TedsTypedElementBridge/TedsTypedElementBridgeCapabilities.h"

void UMyTedsFactory::RegisterQueries(
    UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 只在 Bridge 启用时注册查询
    if (UE::Editor::DataStorage::Compatibility::IsTypedElementBridgeEnabled())
    {
        // 注册实际查询逻辑
    }
}

void UMyTedsFactory::PreShutdown(
    UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    if (MyCleanupQuery != UE::Editor::DataStorage::InvalidQueryHandle)
    {
        // 注销查询
        MyCleanupQuery = UE::Editor::DataStorage::InvalidQueryHandle;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 核心数据存储引擎 |
| `TypedElementFramework` | Typed Element 类型化元素框架 |
| `TypedElementRuntime` | Typed Element 运行时支持 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> 注意：由于本插件包含 17 个模块，各子模块的依赖各不相同。以上列出的是跨模块共有的核心依赖。具体模块的 Build.cs 可在源码中查看。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 模式中启用 TEDS Outliner |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在 TEDS Outliner 中隐藏非编辑关卡实例内未加载的 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复 TEDS Outliner 中跨关卡拖放操作的错误 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退一个变更列表的改动 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在 TEDS Outliner 中隐藏非编辑关卡实例内未加载的 Actor 行 |

### 维护评价

- **活跃维护** ✅：最近更新（2026-05-20）距今仅 1 周，且持续有功能性更新
- **实验性状态**：`.uplugin` 标记 `IsExperimentalVersion=true`，默认未启用（`Installed=false`）
- **更新频率**：高，近 1 周内有 5 次提交，集中在 TedsOutliner 模块的功能完善和 bug 修复
- **成熟度**：作为 2024 年创建的实验性插件，目前仍在快速迭代中，功能逐渐稳定
- **已知限制**：
  - 实验性插件，API 可能变更
  - 依赖 TEDS 核心系统，该系统本身也是相对较新的架构
  - 部分功能仍在开发中（如版本控制集成）
- **推荐使用**：适合编辑器扩展开发者研究和测试，不建议在生产环境中依赖此插件。如果你正在为 Unreal 编辑器开发高性能数据驱动 UI，此插件提供了完整的参考实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [TEDS 核心（EditorDataStorage）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Source/Runtime/Experimental/EditorDataStorage)
- 官方文档：暂无