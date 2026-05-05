# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产、配置） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个专为虚拟制作（Virtual Production）和 Motion Design 工作流设计的资产同步插件。它解决的核心问题是：在分布式团队或多台设备（如渲染农场、设计师工作站、实时合成机器）之间，如何高效、可靠地同步和管理 Unreal Engine 资产及其依赖关系。

该插件提供了一套完整的客户端-服务器架构（`StormSyncTransportClient`、`StormSyncTransportServer`、`StormSyncTransportCore`），允许用户通过网络推送（Push）、拉取（Pull）和同步（Sync）资产包。它不仅仅是简单的文件复制，而是深入理解资产依赖图，确保目标机器拥有所有必需的资产，从而避免因缺失依赖导致的加载失败或渲染错误。`StormSyncEditor` 模块提供了编辑器内的集成，如右键菜单操作、进度通知和导入向导，使同步操作对用户透明且友好。

## 使用场景

- **虚拟制片现场**：在 LED 墙渲染节点和设计师工作站之间实时同步最新的场景、材质和蓝图资产。
- **Motion Design 团队协作**：多位设计师在不同机器上并行工作，需要定期合并和同步彼此创建的资产（如动画、特效、几何体）。
- **渲染农场资产分发**：将渲染任务所需的资产包从主工作站推送到所有渲染节点，确保渲染环境一致。
- **资产版本管理**：作为 Perforce 或 Git LFS 等版本控制系统的补充，用于快速同步运行时依赖，而非源代码。

## 蓝图用法

由于 StormSync 主要是一个编辑器和工作流工具，其核心交互通过编辑器 UI（如右键菜单、向导）和 C++ API 完成。直接暴露给蓝图的节点较少，主要集中在通知和状态查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取 StormSync 通知子系统的单例引用 | `UStormSyncNotificationSubsystem` |
| `AddSimpleNotification` | 在编辑器中显示一个简单的通知提示 | `UStormSyncNotificationSubsystem` |
| `HandlePushResponse` | 处理来自传输层的推送操作响应，并更新 UI 通知 | `UStormSyncNotificationSubsystem` |
| `HandlePullResponse` | 处理来自传输层的拉取操作响应，并更新 UI 通知 | `UStormSyncNotificationSubsystem` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用同步操作，而是通过编辑器扩展点（如资产右键菜单）触发。如果你想在自定义编辑器工具中集成通知，可以这样做：

1.  获取 `UStormSyncNotificationSubsystem` 的引用。
2.  当你的工具完成一个长时间操作后，调用 `AddSimpleNotification` 并传入描述性文本，向用户显示一个临时通知。
3.  如果你的工具与 StormSync 传输层交互，可以监听其委托，并调用 `HandlePushResponse` 或 `HandlePullResponse` 来自动显示标准的进度条和结果通知。

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncEditor.h"
#include "Subsystems/StormSyncNotificationSubsystem.h"
```

### 基本用法

从 `StormSyncEditor` 模块获取单例，并使用其提供的工具函数。

```cpp
// 来源: Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncEditor/Public/StormSyncEditor.h
// 获取编辑器模块实例
FStormSyncEditorModule& StormSyncEditorModule = FStormSyncEditorModule::Get();

// 检查一组资产是否有未保存的修改
TArray<FName> PackageNamesToCheck = { TEXT("/Game/MyAsset") };
FText DisabledReason;
TArray<FAssetData> DirtyAssets = StormSyncEditorModule.GetDirtyAssets(PackageNamesToCheck, DisabledReason);

if (DirtyAssets.Num() > 0)
{
    UE_LOG(LogTemp, Warning, TEXT("以下资产未保存，无法同步: %s"), *DisabledReason.ToString());
}
```

### 进阶用法

集成通知子系统以提供用户反馈。

```cpp
// 来源: Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncEditor/Public/Subsystems/StormSyncNotificationSubsystem.h
// 获取通知子系统
UStormSyncNotificationSubsystem& NotificationSubsystem = UStormSyncNotificationSubsystem::Get();

// 显示一个简单的信息通知
NotificationSubsystem.AddSimpleNotification(FText::FromString(TEXT("资产同步任务已开始...")));

// 记录一条消息到 StormSync 专用日志页面
NotificationSubsystem.NewPage(FText::FromString(TEXT("同步操作日志")));
NotificationSubsystem.Info(FText::FromString(TEXT("正在连接到服务器 192.168.1.100...")));
```

## Demo 示例

以下示例展示如何创建一个简单的编辑器命令，该命令检查选中的资产是否脏（未保存），并显示一个通知。

```cpp
// MySyncCheckCommand.h
#pragma once

#include "CoreMinimal.h"

class FMySyncCheckCommand
{
public:
    static void Register();
    static void Unregister();

private:
    static void Execute();
};
```

```cpp
// MySyncCheckCommand.cpp
#include "MySyncCheckCommand.h"
#include "StormSyncEditor.h"
#include "Subsystems/StormSyncNotificationSubsystem.h"
#include "ContentBrowserModule.h"
#include "IContentBrowserSingleton.h"

void FMySyncCheckCommand::Register()
{
    // 注册一个控制台命令
    IConsoleManager::Get().RegisterConsoleCommand(
        TEXT("My.CheckSyncAssets"),
        TEXT("检查当前选中的资产是否可以安全同步"),
        FConsoleCommandDelegate::CreateStatic(&FMySyncCheckCommand::Execute),
        ECVF_Default
    );
}

void FMySyncCheckCommand::Unregister()
{
    // 清理命令（在模块关闭时调用）
}

void FMySyncCheckCommand::Execute()
{
    // 1. 获取内容浏览器中选中的资产
    FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
    TArray<FAssetData> SelectedAssets;
    ContentBrowserModule.Get().GetSelectedAssets(SelectedAssets);

    if (SelectedAssets.Num() == 0)
    {
        UStormSyncNotificationSubsystem::Get().AddSimpleNotification(FText::FromString(TEXT("未选中任何资产。")));
        return;
    }

    // 2. 提取包名
    TArray<FName> PackageNames;
    for (const FAssetData& Asset : SelectedAssets)
    {
        PackageNames.Add(Asset.PackageName);
    }

    // 3. 使用 StormSyncEditor 模块检查脏状态
    FText DisabledReason;
    TArray<FAssetData> DirtyAssets = FStormSyncEditorModule::Get().GetDirtyAssets(PackageNames, DisabledReason);

    // 4. 显示结果通知
    if (DirtyAssets.Num() > 0)
    {
        UStormSyncNotificationSubsystem::Get().Warning(DisabledReason);
    }
    else
    {
        UStormSyncNotificationSubsystem::Get().AddSimpleNotification(
            FText::FromString(FString::Printf(TEXT("选中的 %d 个资产均已保存，可以同步。"), SelectedAssets.Num()))
        );
    }
}
```

## 模块依赖

从模块结构和命名推断，使用者可能需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 核心同步逻辑、资产依赖分析、数据格式定义 |
| `StormSyncTransportCore` | 网络传输协议、消息定义、序列化基础 |
| `StormSyncTransportClient` | 客户端连接管理、发送请求 |
| `StormSyncTransportServer` | 服务器端监听、请求处理、资产分发 |
| `StormSyncDrives` | 可能用于管理本地或网络驱动器路径映射 |
| `StormSyncImport` | 资产导入逻辑、冲突解决 |
| `StormSyncEditor` | 编辑器集成、UI、通知、向导 |

**注意**：实际依赖关系需查阅各模块的 `Build.cs` 文件。通常，你的项目模块只需直接依赖 `StormSyncCore` 和 `StormSyncTransportClient`（如果作为客户端）或 `StormSyncTransportServer`（如果作为服务器）。

## 维护状态

### 近期更新

```
- bb5a24f9caed Storm Sync: fix crash when using context menu on class items in content browser
- d53ec51b85c0 Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

**解读**：
1.  `bb5a24f9caed`：修复了一个具体的崩溃问题，表明插件仍在积极修复 bug。
2.  `d53ec51b85c0`：这是一个重要的里程碑，插件从 `Experimental` 目录正式迁移到 `VirtualProduction` 目录，意味着它已达到稳定状态，被 Epic 官方认可为虚拟制作工作流的正式组成部分。

### 维护评价

- **活跃维护**：插件创建于 2024 年 1 月，非常年轻。最近的提交（2024 年内）显示它正在被积极使用和修复问题。
- **官方支持**：作为 Epic Games 官方维护的插件，且已从实验性升级为正式类别，其长期维护和兼容性有保障。
- **推荐使用**：**强烈推荐**。对于任何涉及虚拟制作或多机协作的 Motion Design 项目，StormSync 是解决资产同步痛点的官方推荐方案。它提供了比手动复制或简单脚本更可靠、更集成的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)