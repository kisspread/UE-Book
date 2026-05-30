# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 资产同步工具 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板等） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

Storm Sync 是一个用于在多个 Unreal Editor 实例或网络内其他设备之间同步资产的插件。它解决了在多人协作或虚拟制片场景中，如何高效、可靠地同步项目资产（包括其依赖关系）的核心问题。该插件为 Motion Design 工作流推荐组件，旨在简化资产分发和更新流程，避免手动拷贝带来的版本混乱和遗漏。

它通过网络传输，允许用户将选中的资产包推送到远端（Push），或从远端拉取更新（Pull），并提供冲突检测和状态比较功能。其核心思想是将资产及其依赖关系打包成一个“缓冲区”（Buffer），然后通过 TCP 进行传输。

## 使用场景

- 你在团队中进行虚拟制片或 Motion Design 项目，需要将最新的素材、材质或蓝图同步到渲染农场、其他艺术家的编辑器或特定工作站。
- 你需要确保所有参与者的项目保持相同的资产状态，避免因手动拷贝导致的版本不一致。
- 你需要从远程服务器拉取最新的资产包，并自动更新本地已有的资产。
- 你需要比较本地资产与远程资产的状态差异，以决定是否需要同步。
- 你需要将选定的资产及其依赖关系导出为一个独立的归档文件（.spak），以便离线传输或备份。

## 蓝图用法

本插件主要通过编辑器UI和上下文菜单提供功能，暴露的蓝图节点较少，其核心操作（Push/Pull/Sync）主要通过编辑器扩展点实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateWizard` | 打开资产导入向导，用于处理从缓冲区导入的资产 | `FStormSyncEditorModule` |
| `GetRegisteredConnections` | 获取当前已注册的所有 Storm Sync 网络连接 | `FStormSyncEditorModule` |
| `GetDirtyAssets` | 检查一组资产包名中是否有未保存的脏资产 | `FStormSyncEditorModule` |
| `BuildPushAssetsMenuSection` | 构建上下文菜单中“推送”操作的子菜单项 | `FStormSyncEditorModule` |
| `BuildCompareWithMenuSection` | 构建上下文菜单中“比较”操作的子菜单项 | `FStormSyncEditorModule` |
| `ShouldImport` | （Import Wizard 接口）获取用户是否确认导入的选择 | `IStormSyncImportWizard` |

### 使用示例（蓝图描述）

由于主要功能集成在编辑器UI中，典型的使用流程如下：
1. 在内容浏览器中选中一个或多个资产。
2. 右键点击，选择“Storm Sync”菜单项。
3. 根据需要选择“Push To...”或“Pull From...”或“Compare With...”。
4. 在弹出的子菜单中，选择目标连接设备或服务器。
5. 插件会自动收集资产依赖关系，并执行相应操作，同时在编辑器右下角显示进度通知。
6. 如果是导入操作（拖拽.spak文件），会触发导入向导，让用户确认要导入的文件列表。

## C++ 用法

### 头文件引入

根据具体功能，可能需要引入以下头文件：
```cpp
#include "StormSyncEditor.h" // 模块主入口
#include "Subsystems/StormSyncNotificationSubsystem.h" // 通知子系统
```

### 基本用法

从测试用例和模块接口中提取的典型用法：

1.  **获取模块实例并创建导入向导**
    ```cpp
    // 来源: StormSyncEditor.h
    // 获取 StormSyncEditor 模块
    FStormSyncEditorModule& EditorModule = FStormSyncEditorModule::Get();
    
    // 准备要导入的文件信息（通常由工厂或传输层生成）
    TArray<FStormSyncImportFileInfo> FilesToImport = ...; // 需要导入的文件
    TArray<FStormSyncImportFileInfo> BufferFiles = ...;   // 缓冲区中的所有文件
    
    // 创建并打开导入向导
    TSharedRef<IStormSyncImportWizard> Wizard = EditorModule.CreateWizard(FilesToImport, BufferFiles);
    // 用户交互后，检查结果
    if (Wizard->ShouldImport())
    {
        // 执行导入逻辑
    }
    ```

2.  **检查资产脏状态（用于UI扩展）**
    ```cpp
    // 来源: StormSyncEditor.h
    TArray<FName> PackageNames = { TEXT("/Game/MyAsset1"), TEXT("/Game/MyAsset2") };
    FText DisabledReason;
    TArray<FAssetData> DirtyAssets = EditorModule.GetDirtyAssets(PackageNames, DisabledReason);
    if (DirtyAssets.Num() > 0)
    {
        // 存在未保存的资产，DisabledReason 包含详细说明，可用于UI提示
    }
    ```

3.  **获取当前活动连接**
    ```cpp
    // 来源: StormSyncEditor.h
    TMap<FMessageAddress, FStormSyncConnectedDevice> Connections = EditorModule.GetRegisteredConnections();
    // 遍历连接，可用于构建自定义UI列表
    for (const auto& Pair : Connections)
    {
        const FMessageAddress& Address = Pair.Key;
        const FStormSyncConnectedDevice& Device = Pair.Value;
        // 处理连接信息...
    }
    ```

### 进阶用法

结合通知子系统显示自定义进度：
```cpp
// 来源: StormSyncNotificationSubsystem.h
// 获取通知子系统
UStormSyncNotificationSubsystem& NotificationSubsystem = UStormSyncNotificationSubsystem::Get();

// 添加一个简单的通知
NotificationSubsystem.AddSimpleNotification(FText::FromString(TEXT("开始同步任务...")));

// 处理传输响应（通常由传输层回调）
// 假设有一个响应 TSharedPtr<FStormSyncTransportPushResponse> Response;
NotificationSubsystem.HandlePushResponse(Response);

// 使用日志页面记录详细信息
NotificationSubsystem.NewPage(FText::FromString(TEXT("同步日志")));
NotificationSubsystem.Info(FText::FromString(TEXT("成功推送 5 个资产。")));
```

## Demo 示例

以下示例展示了如何在 C++ 中构建一个简单的资产同步命令，该命令会列出当前连接并尝试将指定资产推送到第一个连接。

**StormSyncDemoCommand.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FStormSyncDemoCommandModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterConsoleCommands();
    void UnregisterConsoleCommands();
    void ExecuteSyncCommand(const TArray<FString>& Args);
};
```

**StormSyncDemoCommand.cpp**
```cpp
#include "StormSyncDemoCommand.h"
#include "StormSyncEditor.h"
#include "Subsystems/StormSyncNotificationSubsystem.h"
#include "Interfaces/IPluginManager.h"

#define LOCTEXT_NAMESPACE "FStormSyncDemoCommandModule"

void FStormSyncDemoCommandModule::StartupModule()
{
    RegisterConsoleCommands();
}

void FStormSyncDemoCommandModule::ShutdownModule()
{
    UnregisterConsoleCommands();
}

void FStormSyncDemoCommandModule::RegisterConsoleCommands()
{
    // 注册控制台命令：Demo.SyncAssets <PackagePath1> <PackagePath2> ...
    IConsoleManager::Get().RegisterConsoleCommand(
        TEXT("Demo.SyncAssets"),
        TEXT("Sync specified assets to the first connected device via Storm Sync."),
        FConsoleCommandDelegate::CreateRaw(this, &FStormSyncDemoCommandModule::ExecuteSyncCommand),
        ECVF_Default
    );
}

void FStormSyncDemoCommandModule::UnregisterConsoleCommands()
{
    if (IConsoleManager::IsAvailable())
    {
        IConsoleManager::Get().UnregisterConsoleObject(TEXT("Demo.SyncAssets"));
    }
}

void FStormSyncDemoCommandModule::ExecuteSyncCommand(const TArray<FString>& Args)
{
    if (Args.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("Usage: Demo.SyncAssets <PackagePath1> [PackagePath2 ...]"));
        return;
    }

    // 1. 获取 StormSyncEditor 模块
    FStormSyncEditorModule& StormSyncModule = FStormSyncEditorModule::Get();

    // 2. 获取当前所有连接
    TMap<FMessageAddress, FStormSyncConnectedDevice> Connections = StormSyncModule.GetRegisteredConnections();
    if (Connections.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No active Storm Sync connections found."));
        return;
    }

    // 3. 取第一个连接
    const FMessageAddress FirstConnectionAddress = Connections.CreateConstIterator().Key;

    // 4. 将命令行参数（资产路径）转换为 FName 数组
    TArray<FName> PackageNames;
    for (const FString& Arg : Args)
    {
        PackageNames.Add(FName(*Arg));
    }

    // 5. 获取通知子系统以提供反馈
    UStormSyncNotificationSubsystem& Notifications = UStormSyncNotificationSubsystem::Get();
    Notifications.AddSimpleNotification(FText::Format(
        LOCTEXT("SyncStart", "Pushing {0} asset(s) to {1}..."),
        FText::AsNumber(PackageNames.Num()),
        FText::FromString(FirstConnectionAddress.ToString())
    ));

    // 6. 调用模块的 Push 功能（这里简化为调用模块内部的方法，实际需参考接口）
    // 注意：直接调用 Push 操作通常由 UI 触发，此处仅为演示。
    // 在实际插件中，Push 操作由 FStormSyncAssetFolderContextMenu::ExecutePushAssetsAction 封装。
    // 为保持示例简洁，我们仅展示调用链，不展开底层网络逻辑。
    UE_LOG(LogTemp, Display, TEXT("Demo: Push requested for %s to address %s"),
        *FString::Join(Args, TEXT(", ")),
        *FirstConnectionAddress.ToString()
    );

    // 在实际场景中，你会调用类似以下的函数：
    // StormSyncModule.PushAssetsToConnection(PackageNames, FirstConnectionAddress);
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，Storm Sync 插件内部模块间依赖关系复杂，但对外部模块的依赖较为常规。

| 模块 | 用途 |
|---|---|
| `MessageBus`, `Messaging` | 用于插件内部各模块间以及跨编辑器实例的通信。 |
| `Sockets`, `Networking` | 用于底层 TCP 网络传输。 |
| `AssetRegistry`, `AssetTools` | 用于资产依赖分析和操作。 |
| `AssetDefinition` | 用于资产类型的自定义定义和行为。 |
| `DeveloperTool`, `WorkspaceMenuStructure` | 用于开发工具集成和编辑器工作区扩展。 |

*注：无特殊依赖（仅标准 Core/Engine/Slate 等）* 是不准确的，因为该插件明确依赖 `MessageBus`, `Sockets`, `AssetRegistry` 等模块来实现其核心的网络资产同步功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了一个安全漏洞，该漏洞允许恶意用户创建包含特定包名/路径的spak文件。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了导出向导UI在更改路径时会创建大量嵌套文件夹的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中32位与64位参数不匹配的警告或错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将代码中的UE_LOG宏迁移到UE_LOGF（可能是新宏或封装）。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 第二次尝试修复一个糟糕的全局查找替换操作。 |

### 维护评价

- **创建时间**：插件于 2025 年 5 月创建，至今约 1 年，是一个相对较新的工具。
- **最近更新频率**：最近更新集中在 2026 年 2 月至 5 月，平均每月都有更新，且包含重要的安全修复和功能修复。
- **维护活跃度**：**活跃维护中**。近期更新不仅包含编译修复，还涉及安全漏洞修补和UI改进，表明插件仍在积极开发和维护。
- **已知问题/限制**：从提交记录看，开发者正在主动修复问题（如安全漏洞、UI bug）。作为一个新插件，用户群和测试覆盖可能还在增长中。
- **推荐使用**：**推荐使用**。作为 Epic Games 官方推出的虚拟制片工作流工具链的一部分，它解决了团队协作中的关键痛点（资产同步）。持续的维护和更新保证了其稳定性和安全性。但用户应注意，它主要针对 Motion Design 和虚拟制片工作流，在通用项目中使用前应评估其必要性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- 官方文档（无）
- 测试用例（位于源码树内的 `StormSyncTests` 模块中）