# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个用于虚拟制作工作流的资产同步插件。它解决了在多个虚幻引擎实例（例如同一网络中的不同工作站或工作站与渲染农场之间）之间高效、可靠地同步项目资产依赖关系的问题。通过分析资产间的依赖关系，它能够打包、传输和导入完整的资产包，确保所有相关资产（包括子资产和引用）在目标环境中保持一致，从而支持 Motion Design 等需要跨实例协作的复杂工作流。

## 使用场景

-   **团队协作**：你在做 Motion Design 项目，需要将场景资产和它依赖的所有材质、网格体、动画等同步给网络中另一台工作站进行渲染或进一步编辑。
-   **版本控制与备份**：你想将特定资产集（及其完整依赖）导出为一个独立的、可移植的存档文件（.stormsync），用于版本管理、备份或在不同项目间迁移。
-   **实时同步**：你希望在网络中的多个编辑器实例之间实时推送（Push）或拉取（Pull）最新的资产状态，并了解它们之间的差异（Compare）。
-   **批量导入**：你需要从一个 Storm Sync 存档文件中批量导入资产，并在导入前查看文件列表、大小和冲突状态。

## 蓝图用法

StormSyncEditor 模块主要提供编辑器内的 UI 和集成，其核心交互通过右键菜单、向导对话框和通知系统完成，而不是传统的蓝图节点。因此，其“蓝图用法”体现在编辑器中的用户操作。

### 核心节点

该模块未暴露 `BlueprintCallable` 函数供蓝图调用。其功能主要通过以下编辑器 UI 触发：

| 操作 | 说明 | 触发方式 |
|---|---|---|
| Push Assets | 将选中的资产及其依赖推送到网络上的另一个 Storm Sync 实例 | 内容浏览器右键菜单 -> Storm Sync -> Push -> [选择目标] |
| Pull Assets | 从网络上的另一个 Storm Sync 实例拉取资产（以更新本地） | 内容浏览器右键菜单 -> Storm Sync -> Pull -> [选择来源] |
| Compare With | 比较选中的资产与网络上另一个实例中同名资产的状态差异 | 内容浏览器右键菜单 -> Storm Sync -> Compare With -> [选择目标] |
| Export | 将选中的资产及其依赖导出为本地 .stormsync 存档文件 | 内容浏览器右键菜单 -> Storm Sync -> Export |
| Import | 从 .stormsync 文件导入资产 | 拖放 .stormsync 文件到内容浏览器，或通过右键菜单导入 |
| View Status | 查看与某个已连接设备之间的资产同步状态 | 内容浏览器右键菜单 -> Storm Sync -> View Status -> [选择目标] |

### 使用示例（蓝图描述）

1.  **推送资产**：
    *   在内容浏览器中，选择一个或多个资产（如 `BP_MyActor`）。
    *   右键单击，选择 `Storm Sync -> Push`。
    *   从子菜单中选择一个可用的网络连接（例如 `Workstation2`）。
    *   系统将分析依赖关系，打包资产，并通过网络发送。您将看到一个进度条通知，完成后会收到成功或失败的提示。

2.  **导出存档**：
    *   选择资产，右键单击，选择 `Storm Sync -> Export`。
    *   在弹出的向导中，确认要包含的依赖项列表。
    *   点击“Next”，选择保存路径并输入文件名。
    *   点击“Finish”，资产将被打包并保存为 `.stormsync` 文件。

## C++ 用法

StormSyncEditor 主要是一个编辑器扩展模块，其公共 API 旨在供其他编辑器模块扩展或集成。以下示例展示了如何从 C++ 代码中访问其核心功能。

### 头文件引入

```cpp
#include "StormSyncEditor.h"
```

### 基本用法

以下代码演示了如何获取模块实例并访问其公共方法。这些方法通常用于创建自定义的 UI 扩展（例如，为自定义内容浏览器添加 Storm Sync 菜单）。

```cpp
// 来源：基于 Public/StormSyncEditor.h 中的 FStormSyncEditorModule 接口推断

// 获取 StormSyncEditor 模块的单例引用
FStormSyncEditorModule& StormSyncEditor = FStormSyncEditorModule::Get();

// 检查当前可用的网络连接
TMap<FMessageAddress, FStormSyncConnectedDevice> Connections = StormSyncEditor.GetRegisteredConnections();
if (Connections.Num() > 0)
{
    UE_LOG(LogTemp, Log, TEXT("Found %d active Storm Sync connections."), Connections.Num());
}

// 在构建自定义菜单时，可以调用模块提供的辅助函数来填充 Push/Pull/Compare 子菜单。
// 假设你正在扩展 UToolMenu
FMenuBuilder MenuBuilder(/* ... */);
TArray<FName> SelectedPackageNames = /* 从选择中获取 */;

// 为“Push”构建子菜单
StormSyncEditor.BuildPushAssetsMenuSection(MenuBuilder, SelectedPackageNames, true /* bInIsPushing */);
```

### 进阶用法

更高级的用法涉及处理导入事件或创建自定义向导。

```cpp
// 来源：基于 Public/StormSyncEditor.h 中的 CreateWizard 方法推断

// 1. 准备导入文件信息
TArray<FStormSyncImportFileInfo> FilesToImport;
TArray<FStormSyncImportFileInfo> BufferFiles;
// ... 填充文件信息，通常来自拖放事件或自定义逻辑

// 2. 创建导入向导对话框
TSharedRef<IStormSyncImportWizard> Wizard = StormSyncEditor.CreateWizard(FilesToImport, BufferFiles);

// 3. 如果用户确认导入 (ShouldImport() 为 true)，则执行导入逻辑
if (Wizard->ShouldImport())
{
    // 此处可以调用 StormSyncImport 模块的接口来执行实际的导入操作
    // 具体实现依赖于 StormSyncImport 模块
    UE_LOG(LogStormSyncEditor, Log, TEXT("User confirmed import. Proceeding..."));
    // PerformActualImport(...);
}
else
{
    UE_LOG(LogStormSyncEditor, Log, TEXT("User cancelled import."));
}
```

## Demo 示例

一个完整的示例演示了如何为内容浏览器创建一个极简的自定义扩展，添加一个按钮来触发当前选中资产的“状态检查”（相当于一个简化的 View Status）。

**注意**：此示例需要将 `StormSyncEditor` 和 `ToolMenus` 模块添加到你的 `.Build.cs` 文件中。

**MyEditorExtension.h**
```cpp
// MyEditorExtension.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyEditorExtension.generated.h"

class UToolMenu;
class FMessageAddress;
struct FStormSyncConnectedDevice;

UCLASS()
class UMyEditorExtensionSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    // 子系统初始化时注册菜单扩展
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    // 菜单扩展回调函数
    static void AddMyCustomMenuEntry(UToolMenu* Menu);

    // 实际执行状态检查的函数
    static void CheckSelectedAssetsStatus();
};
```

**MyEditorExtension.cpp**
```cpp
// MyEditorExtension.cpp
#include "MyEditorExtension.h"

#include "StormSyncEditor.h"
#include "ToolMenus.h"
#include "ContentBrowserModule.h"

void UMyEditorExtensionSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 延迟注册，确保所有模块加载完毕
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateLambda([]()
    {
        // 扩展内容浏览器的资产上下文菜单
        UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("ContentBrowser.AssetContextMenu");
        FToolMenuSection& Section = Menu->FindOrAddSection("MyCustomSection");
        Section.AddDynamicEntry(
            "MyDynamicEntry",
            FNewToolMenuSectionDelegate::CreateStatic(&UMyEditorExtensionSubsystem::AddMyCustomMenuEntry)
        );
    }));
}

void UMyEditorExtensionSubsystem::Deinitialize()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
    Super::Deinitialize();
}

void UMyEditorExtensionSubsystem::AddMyCustomMenuEntry(UToolMenu* Menu)
{
    FToolMenuSection& Section = Menu->FindOrAddSection("MyCustomSection");
    Section.AddMenuEntry(
        "MyCheckStatusEntry",
        FText::FromString("Check Storm Sync Status (My Extension)"),
        FText::FromString("Check if selected assets are in sync with a remote instance."),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateStatic(&UMyEditorExtensionSubsystem::CheckSelectedAssetsStatus))
    );
}

void UMyEditorExtensionSubsystem::CheckSelectedAssetsStatus()
{
    // 1. 获取选中的资产包名
    TArray<FName> SelectedPackageNames;
    // ... 从内容浏览器选择中获取

    if (SelectedPackageNames.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No assets selected."));
        return;
    }

    // 2. 检查是否有可用的连接
    FStormSyncEditorModule& StormSyncEditor = FStormSyncEditorModule::Get();
    TMap<FMessageAddress, FStormSyncConnectedDevice> Connections = StormSyncEditor.GetRegisteredConnections();

    if (Connections.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No active Storm Sync connections found."));
        return;
    }

    // 3. 简单逻辑：使用第一个连接进行状态检查（实际应用中可能需要用户选择）
    const FMessageAddress& FirstAddress = Connections.CreateConstIterator().Key();
    // 此处需要调用 StormSyncTransportClient 或 Core 模块的方法来发送状态请求并处理响应。
    // 由于我们只演示 StormSyncEditor 模块，这里仅作日志输出。
    UE_LOG(LogTemp, Log, TEXT("Would send status request for %d assets to connection: %s"),
        SelectedPackageNames.Num(), *FirstAddress.ToString());

    // 实际的状态检查和 UI 显示通常由 SStormSyncStatusWidget 处理，
    // 可以通过 StormSyncEditor 模块的内部逻辑触发。
}
```

## 模块依赖

根据 `StormSyncEditor.Build.cs` 及其所属插件的上下文，其主要依赖如下（省略了通用依赖如 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 提供核心数据类型（如文件依赖信息、连接设备信息）和基础逻辑。 |
| `StormSyncTransportCore` | 提供网络传输层的核心类型和接口。 |
| `StormSyncTransportClient` | 提供客户端网络通信功能，用于与远程服务器实例交互。 |
| `ToolMenus` | 提供编辑器菜单和工具栏扩展框架。 |
| `PropertyEditor` | 用于实现自定义的属性细节面板（Details Customization）。 |
| `MessageLog` | 用于将同步状态和错误信息输出到编辑器的消息日志面板。 |
| `NotificationSystem` | 用于显示编辑器内的通知和进度条。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了恶意用户制作特殊存档文件可能利用的安全漏洞。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了导出向导在用户更改路径时错误创建大量嵌套文件夹的 UI 问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32 位和 64 位格式说明符与实际参数不匹配的编译器警告/错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF，这是引擎内部日志宏的现代化改进。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 第二次尝试修复之前一次错误的全局查找替换操作带来的问题。 |

### 维护评价

StormSync 插件（及其 StormSyncEditor 模块）处于**积极维护**状态。

-   **创建时间**：约 1 年前（2025年5月），属于较新的插件。
-   **更新频率**：从 Git 历史看，近期有多次更新，最近一次在 2026 年 5 月，主要集中在 **安全漏洞修复**、**UI 问题修复** 和 **代码现代化**。
-   **活跃度**：更新由 Epic Games 团队进行，并且关联了内部 JIRA（`#jira UE-207892`），表明它是官方认可并持续投入资源的项目。
-   **已知问题**：近期修复了安全漏洞和 UI 缺陷，表明开发团队在主动响应和解决问题。
-   **推荐使用**：**推荐使用**。作为 Motion Design 工作流的推荐组件，它得到了官方支持。但鉴于它相对较新，且主要服务于虚拟制作这一特定领域，建议在非此工作流中谨慎评估其必要性。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
-   [官方文档]() (暂无公开文档链接)
-   [测试用例]() (测试代码位于 `Source/StormSyncTests/`)