# Storm Sync

> Sync, Pull, Push, asset dependencies. This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，配置资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

**StormSyncDrives** 模块的核心功能是**将文件系统中的物理目录（如网络共享文件夹或本地驱动器）动态映射为虚幻引擎内容浏览器中的虚拟挂载点**。

这解决了在大型项目或需要跨团队协作（如 Motion Design 工作流）中，资产依赖项可能分布在不同物理位置（如艺术家本地磁盘、版本控制沙箱、网络存储）的问题。通过配置 `MountPoints`，团队成员可以像访问本地 `/Game` 内容一样访问这些外部资产，从而简化资产管理、同步和依赖项解析，确保项目引用路径的一致性。

## 使用场景

- **多人协作与资产共享**：美术师 A 的资产在本地磁盘 `D:\ArtAssets\Character`，美术师 B 的资产在网络共享 `\\NAS\Shared\Props`。通过 `StormSyncDrives` 配置，两者可以分别映射到 `/Game/Characters` 和 `/Game/Props`，在同一个项目中无缝引用。
- **版本控制沙箱**：从版本控制系统（如 Perforce）拉取的特定 changelist 可以映射到独立挂载点，避免污染主项目目录。
- **运动设计工作流**：作为推荐的一部分，用于同步和管理运动图形项目所需的字体、图像、3D 模型等外部资源。

## 蓝图用法

`StormSyncDrives` 模块主要通过**开发者设置**和 **C++ API** 进行配置和交互，未暴露专门的蓝图函数节点。其配置通过项目设置（Project Settings）中的 `Mount Points Settings` 界面完成。

### 核心设置面板
在编辑器中，转至 **编辑 > 项目设置 > 项目 > Mount Points Settings** 进行配置。

### 使用示例（蓝图描述）
虽然不能直接调用模块函数，但可以在蓝图中通过读取 `UStormSyncDrivesSettings` 类来获取挂载点配置信息，用于自定义的资产验证或加载逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "IStormSyncDrivesModule.h"
#include "StormSyncDrivesSettings.h"
```

### 基本用法

通过模块的公共接口注册和取消注册挂载点。

```cpp
// 注册一个挂载点
FStormSyncMountPointConfig NewMount;
NewMount.MountPoint = TEXT("/MyAssets");
NewMount.MountDirectory.Path = TEXT("D:/Shared/ProjectAssets");

FText ErrorText;
if (IStormSyncDrivesModule::Get().RegisterMountPoint(NewMount, ErrorText))
{
    UE_LOG(LogTemp, Log, TEXT("Mount point /MyAssets registered successfully."));
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Failed to register mount point: %s"), *ErrorText.ToString());
}

// 取消注册一个挂载点
if (IStormSyncDrivesModule::Get().UnregisterMountPoint(NewMount, ErrorText))
{
    UE_LOG(LogTemp, Log, TEXT("Mount point /MyAssets unregistered."));
}
```

**来源参考**: `Public/IStormSyncDrivesModule.h`

### 进阶用法

1.  **检查模块可用性与初始化**:
    ```cpp
    if (IStormSyncDrivesModule::IsAvailable())
    {
        IStormSyncDrivesModule& DrivesModule = IStormSyncDrivesModule::Get();
        // 使用模块 API ...
    }
    ```

2.  **使用配置验证工具**:
    ```cpp
    FStormSyncMountPointConfig ConfigToTest;
    ConfigToTest.MountPoint = TEXT("/Invalid/Path"); // 故意设置错误的路径
    FText ValidationError;
    
    if (!FStormSyncDrivesUtils::ValidateMountPoint(ConfigToTest, ValidationError))
    {
        UE_LOG(LogTemp, Warning, TEXT("Validation failed: %s"), *ValidationError.ToString());
        // ValidationError 中会包含详细的错误信息，如路径级别不正确
    }
    ```
    **来源参考**: `Public/StormSyncDrivesUtils.h` 和 `Public/StormSyncDrivesSettings.h` 中定义的规则。

## Demo 示例

以下示例展示如何在游戏模块启动时，通过代码注册一个额外的挂载点。

**MyGameModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyGameModule.cpp**
```cpp
#include "MyGameModule.h"
#include "IStormSyncDrivesModule.h"
#include "StormSyncDrivesSettings.h"

#define LOCTEXT_NAMESPACE "FMyGameModule"

void FMyGameModule::StartupModule()
{
    // 尝试注册一个用于开发测试的额外挂载点
    if (IStormSyncDrivesModule::IsAvailable())
    {
        FStormSyncMountPointConfig DevAssetsMount;
        DevAssetsMount.MountPoint = TEXT("/DevTest");
        DevAssetsMount.MountDirectory.Path = FPaths::ProjectDir() / TEXT("../DevAssets");

        FText ErrorText;
        if (!IStormSyncDrivesModule::Get().RegisterMountPoint(DevAssetsMount, ErrorText))
        {
            UE_LOG(LogTemp, Warning, TEXT("Could not register /DevTest mount point: %s"), *ErrorText.ToString());
        }
    }
}

void FMyGameModule::ShutdownModule()
{
    // 在模块关闭时，通常不需要手动取消注册挂载点，
    // 因为 `StormSyncDrives` 模块在关闭时会自行清理。
    // 但如果你有明确的清理逻辑，可以在此处调用 UnregisterMountPoint。
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyGameModule, MyGame)
```

## 模块依赖

要使用 `StormSyncDrives` 模块的功能，你的模块需要在 `Build.cs` 文件中添加以下依赖项：

| 模块 | 用途 |
|---|---|
| `StormSyncDrives` | 提供挂载点管理核心功能和公共接口 |

你的 `Build.cs` 中应包含：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "StormSyncDrives" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了一个安全漏洞，防止恶意制作的资产包包含恶意路径名。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了风暴同步导出向导在切换目录时错误创建大量嵌套文件夹的 UI 问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志输出中格式说明符与参数位宽不匹配的问题，提升了稳定性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF`，是引擎内部日志系统升级的一部分。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上次提交中错误的查找替换操作（“修复错误的查找替换，第二轮”）。 |

### 维护评价

- **活跃维护**：插件于 2025 年 5 月创建，属于较新的工具。从最近提交记录看，在 2026 年持续有更新，包括**安全漏洞修复**、**UI 问题修复**和**代码现代化**（如日志系统迁移），表明 Epic Games 团队仍在积极维护和改进此插件。
- **实验性/默认启用**：该插件**默认启用**，并非实验性功能，已整合进主流的虚拟制作工作流。
- **已知问题**：最近的提交修复了两个明确的 Bug（安全路径和向导 UI），未在提交信息中提及其他重大已知问题。
- **推荐使用**：**强烈推荐**在涉及外部资产依赖、网络共享或 Motion Design 的项目中使用。它是一个成熟的、由 Epic 官方维护的工具，能显著简化跨团队资产管理工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)