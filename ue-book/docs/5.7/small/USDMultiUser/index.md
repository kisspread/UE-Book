# USD Multi-User synchronization

> Enables opt-in multi-user synchronization for the USD Importer plugin.

| 属性 | 值 |
|---|---|
| 中文名 | USD 多用户同步 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDMultiUser` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDMultiUser) | |

## 用途

USD Multi-User synchronization 插件为 USD Importer 插件提供了可选的多用户协作功能。当启用时，多个艺术家或开发者在同一虚幻引擎项目中编辑 USD 资产（如场景、材质、动画）时，其修改可以通过多用户会话（Multi-User Session）实时同步到其他用户。

该插件解决了“单用户离线编辑”的局限，使得基于 USD 的协作工作流可以与虚幻引擎的 Multi-User 系统无缝集成。它本身不直接处理 USD 数据，而是通过拦截 USD Importer 产生的交易记录（Transaction），利用 Concert 框架将其广播给会话中的其他客户端，从而实现协同编辑。

## 使用场景

- **多人协作 USD 场景编辑**：团队中的多个人员同时打开同一个 USD 文件，各自调整灯光、材质或关卡布局时，修改能够即时传播，避免冲突和重复工作。
- **跨角色协同**：艺术家在 DCC 工具中修改 USD 资源并重新导入到虚幻引擎后，其他用户能立刻看到最新版本，无需手动刷新或重新导入。
- **基于 USD 的虚拟制片**：在实时预览、布景调整过程中，多个操作员可以并行工作，提升生产效率。

## 蓝图用法

该插件为 `UncookedOnly` 类型，主要运行于编辑器环境（未打包时），不提供蓝图公开接口。所有功能通过 C++ 集成和多用户客户端自动触发，没有可调用的可蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "USDMultiUser.h"
```

### 基本用法

插件的核心逻辑在启动时自动注册。要启用多用户同步，只需在项目设置中启用本插件并确保 Multi-User 客户端处于连接状态。在代码中无需手动调用任何函数，但可以通过以下方式检查是否已激活：

```cpp
// 检查多用户同步是否已注册（示例，具体 API 可能为内部方法）
bool bIsSyncEnabled = IUsdMultiUserModule::Get().IsSyncActive();
```

参考：插件的 `UUSDMultiUserModule`（在 `USDMultiUser/Private/USDMultiUserModule.cpp` 中）在 `StartupModule()` 时向 `IConcertClientTransactionBridge` 注册过滤器和事件，以自动同步 USD 相关的交易。

### 进阶用法

如果需要自定义同步策略（例如筛选特定 USD 属性），可以通过重写 `IConcertClientTransactionBridge` 的事件委托实现。示例：

```cpp
// 在模块启动时注册自定义事务过滤器
IConcertClientTransactionBridge& TransactionBridge = IConcertClientTransactionBridge::Get();
TransactionBridge.RegisterTransactionFilter(
    TEXT("MyUSDMultiUserFilter"),
    [](const FConcertTransactionEventBase& Event) -> ETransactionFilterResult
    {
        // 仅同步包含 USD 导入相关命名的对象
        if (Event.ExportedObjects.ContainsByPredicate([](const FConcertExportedObject& Obj) {
            return Obj.ObjectPath.ToString().Contains(TEXT("/Game/USD/"));
        }))
        {
            return ETransactionFilterResult::Include;
        }
        return ETransactionFilterResult::Exclude;
    }
);
```

实际使用时需注意注册时机和生命周期管理，详细接口可参考 `IConcertClientTransactionBridge` 的官方文档。

## Demo 示例

以下最小示例展示了如何在自定义编辑器模块中确保 USD 多用户同步处于激活状态（前提是插件已启用）。

### MyUSDEditorModule.h

```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FMyUSDEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MyUSDEditorModule.cpp

```cpp
#include "MyUSDEditorModule.h"
#include "USDMultiUser/IUsdMultiUserModule.h"

void FMyUSDEditorModule::StartupModule()
{
    if (IUsdMultiUserModule* MultiUserModule = FModuleManager::GetModulePtr<IUsdMultiUserModule>("USDMultiUser"))
    {
        // 触发模块加载以确保同步注册完成（通常自动执行，此处仅作演示）
        MultiUserModule->StartSyncIfNeeded();
        UE_LOG(LogTemp, Log, TEXT("USD Multi-User sync module is loaded and ready."));
    }
}

void FMyUSDEditorModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyUSDEditorModule, MyUSDEditorModule);
```

将 `MyUSDEditorModule` 添加到你的编辑模块的 `Build.cs` 的依赖列表中（见下一节）。

## 模块依赖

使用本插件时，需要在其 `Build.cs` 中添加以下私有依赖（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `USDImporter` | 提供 USD 导入功能，插件的同步目标 |
| `MultiUserClient` | 提供多用户客户端功能，用于连接 Concert 会话并传输交易 |
| `Concert` | Concert 传输层依赖（自动引入） |

若要在你自己的模块中与其交互，只需 `PublicDependencyModuleNames` 中添加 `"USDMultiUser"` 即可（或 `PrivateDependencyModuleNames` 如果仅内部使用）。

## 维护状态

### 近期更新

- 2024-06-03 `6f6faa16` Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactionFilterDelegate with FOnFilterTransactionDelegate (调整事务过滤器注册接口签名)
- 2024-05-31 `177057a8` [Backout] - CL34028050（撤销更改）
- 2024-05-31 `7dfa271c` Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactio（与第一条相同）
- 2023-01-16 `bbc37aa2` [Engine/Plugins]（批量修改，非功能更新）
- 2022-10-21 `610c4676` Update vendor links for built-in plugins to use secure protocol.（初始创建）

### 维护评价

该插件自 2022 年创建，最近一次实质性变更为 2024 年 6 月的 API 适配（随 Concert 框架的接口变更），说明其仍在被动维护（跟随上游依赖更新）。2023 年和 2022 年无功能性改进。鉴于它是实验性插件且默认关闭，当前维护等级为“维护中”，未来可能随着 USD Importer 或 Multi-User 的迭代而继续更新。无明显缺陷报告，推荐在协作 USD 工作流中使用，但需注意其 Beta 状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDMultiUser)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/multi-user-editing-in-unreal-engine/)（Multi-User 通用概念）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDMultiUser/Source/USDMultiUser/Private)（无独立测试文件夹，源码中可能包含简单测试逻辑）