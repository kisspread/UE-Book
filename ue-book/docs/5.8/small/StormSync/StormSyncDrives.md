# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个用于在虚幻引擎项目中管理、同步和分发资产及其依赖关系的框架。它旨在解决分布式团队或复杂工作流中，资产散落在不同机器、不同路径（本地或网络驱动器）时的访问与同步问题。其核心功能是将文件系统目录（如本地路径 `D:\Assets\ProjectX` 或网络路径 `\\Server\Share\Assets`）映射为UE的“虚拟挂载点”（如 `/ProjectX/`），使得引擎能够统一处理这些外部资产的引用、打包和传输。它是 Motion Design 工作流的核心组成部分，确保了资产在多人协作、不同工作站环境下的路径一致性。

## 使用场景

-   **Motion Design 工作流**：当多个动画师或技术美术需要共享和同步用于运动设计的资产（如特效、模型、材质）时，使用 StormSync 配置统一的资产挂载点，确保所有工作站上的项目引用一致。
-   **本地与网络资产混合项目**：项目资产一部分在本地磁盘，一部分在共享的网络驱动器上。通过 StormSync 将它们注册为不同的挂载点（例如 `/LocalAssets/`, `/NetworkAssets/`），引擎可以无缝访问。
-   **资产依赖打包与迁移**：需要将项目资产及其所有依赖项打包并发送到另一台机器或归档时，可以使用 StormSync 的同步功能来解析和收集正确的文件。

## 蓝图用法

该模块主要提供 C++ API，蓝图直接可用的功能较少。核心功能是通过 `IStormSyncDrivesModule` 接口在运行时管理挂载点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterMountPoint` | 向引擎注册一个新的挂载点映射（将路径映射到目录），如果路径合法且未冲突则返回true。 | `IStormSyncDrivesModule` |
| `UnregisterMountPoint` | 从引擎注销一个已注册的挂载点。 | `IStormSyncDrivesModule` |

**使用示例（蓝图描述）：**
蓝图中可以通过 `FStormSyncDrivesModule::Get()` 获取模块单例，然后调用 `RegisterMountPoint`。通常，你更可能在项目设置（Project Settings）的 “Mount Points Settings” 中进行配置，该设置界面由 `UStormSyncDrivesSettings` 提供。

## C++ 用法

### 头文件引入

```cpp
#include "IStormSyncDrivesModule.h"
#include "StormSyncDrivesSettings.h"
```

### 基本用法

注册和注销挂载点。
（来源：基于 `IStormSyncDrivesModule.h` 接口文档）

```cpp
// 确保模块已加载
if (IStormSyncDrivesModule::IsAvailable())
{
    IStormSyncDrivesModule& StormSyncDrives = IStormSyncDrivesModule::Get();

    // 创建一个挂载点配置：将 `/MyGameAssets/` 映射到 `D:\ProjectX\Content\`
    FStormSyncMountPointConfig MountConfig;
    MountConfig.MountPoint = TEXT("/MyGameAssets/");
    MountConfig.MountDirectory.Path = TEXT("D:\\ProjectX\\Content\\");

    FText ErrorText;
    if (StormSyncDrives.RegisterMountPoint(MountConfig, ErrorText))
    {
        UE_LOG(LogTemp, Log, TEXT("挂载点 /MyGameAssets/ 注册成功"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("挂载点注册失败: %s"), *ErrorText.ToString());
    }

    // ... 使用资产 ...

    // 当不再需要时注销
    if (StormSyncDrives.UnregisterMountPoint(MountConfig, ErrorText))
    {
        UE_LOG(LogTemp, Log, TEXT("挂载点 /MyGameAssets/ 已注销"));
    }
}
```

### 进阶用法

通过开发者设置（`UStormSyncDrivesSettings`）读取和验证配置。
（来源：基于 `StormSyncDrivesSettings.h` 和 `FStormSyncDrivesUtils` 静态工具类）

```cpp
#include "StormSyncDrivesUtils.h"

// 获取开发者设置
const UStormSyncDrivesSettings* Settings = GetDefault<UStormSyncDrivesSettings>();
if (Settings)
{
    // 遍历所有配置并进行验证
    TArray<FText> ValidationErrors;
    if (!FStormSyncDrivesUtils::ValidateNonDuplicates(Settings->MountPoints, ValidationErrors))
    {
        for (const FText& Error : ValidationErrors)
        {
            UE_LOG(LogTemp, Warning, TEXT("配置验证错误: %s"), *Error.ToString());
        }
    }
}
```

## Demo 示例

一个在模块启动时注册自定义挂载点的示例。
**StormSyncDrivesDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FStormSyncDrivesDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    /** 我们自己注册的挂载点配置 */
    FStormSyncMountPointConfig DemoMountConfig;
};
```
**StormSyncDrivesDemo.cpp**
```cpp
#include "StormSyncDrivesDemo.h"
#include "IStormSyncDrivesModule.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_MODULE(FStormSyncDrivesDemoModule, StormSyncDrivesDemo);

void FStormSyncDrivesDemoModule::StartupModule()
{
    if (IStormSyncDrivesModule::IsAvailable())
    {
        // 定义一个演示挂载点
        DemoMountConfig.MountPoint = TEXT("/DemoDrive/");
        DemoMountConfig.MountDirectory.Path = FPaths::ProjectContentDir() / TEXT("DemoAssets");

        FText ErrorText;
        IStormSyncDrivesModule::Get().RegisterMountPoint(DemoMountConfig, ErrorText);
    }
}

void FStormSyncDrivesDemoModule::ShutdownModule()
{
    if (IStormSyncDrivesModule::IsAvailable() && !DemoMountConfig.MountPoint.IsEmpty())
    {
        FText ErrorText;
        IStormSyncDrivesModule::Get().UnregisterMountPoint(DemoMountConfig, ErrorText);
    }
}
```

## 模块依赖

（基于 `StormSyncDrives` 模块的典型依赖分析）
无特殊依赖（仅标准 Core/Engine/Slate 等）。`StormSyncDrives` 作为 Runtime 模块，其依赖项应已包含在标准引擎模块中。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了一个安全漏洞，该漏洞允许恶意用户通过特定的包名发起攻击。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了 Storm Sync 导出向导在更改路径时错误创建大量嵌套文件夹的UI问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了日志中格式化说明符与64位参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 继上一次错误查找替换后的二次修正。 |

### 维护评价

**活跃维护**。该插件创建于2025年5月，非常年轻。从提交历史看，团队仍在**持续积极地进行维护**，近期的提交集中于安全漏洞修复、UI体验优化和代码规范改进。作为 Motion Design 工作流的推荐组件，其维护优先级较高。目前没有发现已知的废弃警告，推荐在相关项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)