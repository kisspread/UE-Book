# Storm Sync Motion Design Bridge

> Plugin bridge between Motion Design Plugin and Storm Sync to provide in-editor integration to synchronize assets

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步动效桥接 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `StormSyncAvaBridge` (Runtime), `StormSyncAvaBridgeEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSyncAvalancheBridge) | |

## 用途

本插件是 **StormSync**（资产同步工具）与 **Avalanche/Motion Design**（虚拟制作用动效系统）之间的桥接层。

StormSync 提供跨机器的资产包同步能力，Motion Design 提供 Rundown 编辑器用于管理动效模板和页面。本插件将两者连接起来，让用户在 Motion Design 的 Rundown 编辑器中直接右键或点击工具栏，即可将选中的动效资产推送到远程机器，或从远程拉取资产，无需手动导出/传输。

**核心价值**：在虚拟制片现场，多台渲染工作站需要保持动效资产一致。本插件将资产同步操作嵌入 Rundown 编辑器的上下文菜单和工具栏，使得资产同步成为动效工作流的原生部分。

## 使用场景

- 你在用 Motion Design 管理虚拟制片的实时动效内容 → 需要将 Rundown 中的模板资产同步到远程渲染节点
- 你在 Rundown 编辑器中选择了多个模板页面 → 右键即可将关联资产推送到指定远程地址
- 你的团队在多台工作站上协作虚拟制片 → 通过 StormSync 保持所有节点的动效资产版本一致
- 你需要在工具栏中快速触发同步操作 → 工具栏集成了 StormSync 推送按钮

## 蓝图用法

本插件不暴露任何 `BlueprintCallable` 函数。所有功能通过编辑器 UI 扩展（右键菜单和工具栏）提供，不需要蓝图调用。

### 核心 UI 扩展

| 扩展位置 | 说明 |
|---|---|
| Rundown 模板面板右键菜单 | 在 "PageListOperations" 扩展点旁添加初始化和同步操作 |
| Rundown 编辑器工具栏 | 添加同步推送按钮和下拉菜单 |

### 交互流程

1. 在 Motion Design Rundown 编辑器中选中一个或多个模板页面
2. 右键点击 → 出现 StormSync 相关的上下文菜单项
3. 或在工具栏中点击同步按钮，选择目标远程地址
4. 插件自动收集选中页面关联的资产包名称，通过 StormSync 推送到远程

## C++ 用法

本插件为编辑器内部扩展，不设计供外部直接使用的 C++ API。以下是其内部架构说明，供需要二次开发或了解集成方式的开发者参考。

### 头文件引入

```cpp
#include "StormSyncAvaRundownExtender.h"
```

### 内部架构

插件通过 `FStormSyncAvaRundownExtender` 类挂载到 Motion Design 的扩展系统：

```cpp
// 模块启动时注册 UI 扩展
void FStormSyncAvaBridgeEditorModule::StartupModule()
{
    RundownExtender = MakeShared<FStormSyncAvaRundownExtender>();
}

// FStormSyncAvaRundownExtender 构造函数中注册引擎初始化回调
// 引擎就绪后注册右键菜单和工具栏扩展
void FStormSyncAvaRundownExtender::OnPostEngineInit()
{
    RegisterMenuExtensions();
}
```

### 核心逻辑

```cpp
// 收集选中页面关联的资产包名称
// 来源: Private/StormSyncAvaRundownExtender.h
static TArray<FName> GetSelectedPackagesNames(
    const UAvaRundown* InRundown,
    const TWeakPtr<FAvaRundownEditor>& InRundownEditor
);

// 将资产包推送到指定远程地址
static void PushPackagesToRemote(
    const FString& RemoteAddressId,
    const TArray<FName>& InPackageNames
);

// 验证当前选择是否有效（是否关联了有效资产路径）
static bool GetContextMenuSelectionInfos(
    const UAvaRundown* InRundown,
    const TWeakPtr<FAvaRundownEditor>& InRundownEditor,
    bool& bOutIsValidSelection,
    FText& OutDisabledReasonTooltip,
    TArray<FName>& OutSelectedPackageNames,
    FCanExecuteAction& OutCanExecuteAction
);
```

### 进阶用法

`GetContextMenuSelectionInfos` 是上下文菜单的核心辅助函数，它会：

1. 调用 `GetSelectedPages()` 获取当前选中的 Rundown 页面
2. 通过 `GetSelectedPackagesNames()` 提取关联的资产包名
3. 检查是否存在未保存的脏资产，如有则在 `OutDisabledReasonTooltip` 中返回禁用原因
4. 通过 `OutCanExecuteAction` 委托控制菜单项是否可点击

## Demo 示例

本插件是纯编辑器 UI 扩展，不提供独立的可编译使用示例。功能通过 Motion Design Rundown 编辑器的右键菜单和工具栏自动可用，无需编写代码。

如需在自己的编辑器扩展中实现类似的 Rundown 集成，可参考 `FStormSyncAvaRundownExtender` 的扩展注册模式：

```cpp
// StormSyncAvaRundownExtender.h
// 参考模式：通过 FExtensibilityManager 注册菜单/工具栏扩展

// 1. 获取 Motion Design 的扩展管理器
// 2. 注册 FAssetEditorExtender 委托
// 3. 在委托中返回 FExtender 实例
// 4. FExtender 中调用 MenuBuilder->AddMenuEntry() 添加菜单项

static FDelegateHandle RegisterExtension(
    const TSharedPtr<FExtensibilityManager> InExtensibilityManager,
    const FAssetEditorExtender& InExtenderDelegate
);
```

## 模块依赖

从 `.uplugin` 的 Plugins 依赖和模块命名推断：

| 模块 | 用途 |
|---|---|
| `StormSync` / `StormSyncEditor` | 资产同步核心功能和编辑器集成 |
| `Avalanche` | Motion Design（动效系统）核心运行时 |
| `AvalancheEditor` | Motion Design 编辑器（Rundown 扩展系统） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换，重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的一次提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 适配引擎 API 变更，修复委托注册问题 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除动效插件的 beta 标签，标记为正式版 |

### 维护评价

- **创建时间**：2025 年 5 月，从 Experimental 目录迁移到 VirtualProduction 目录，属于 Motion Design 生态的配套插件
- **更新频率**：约 2-3 个月一次，主要是适配引擎 API 变更和代码现代化
- **维护状态**：**维护中** — 作为 Motion Design 生态的一部分随主插件一起维护
- **已知限制**：Runtime 模块排除了 Server 目标（`TargetDenyList: ["Server"]`），仅用于客户端/编辑器
- **推荐使用**：如果你在使用 Motion Design + StormSync 工作流，此插件是两者的官方桥梁，推荐启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSyncAvalancheBridge)
- [Motion Design (Avalanche) 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [StormSync 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)