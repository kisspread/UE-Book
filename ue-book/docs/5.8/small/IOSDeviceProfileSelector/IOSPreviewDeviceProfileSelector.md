# IOS Device Profile Selector

> IOS Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 中文名 | iOS设备配置选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `IOSDeviceProfileSelector` (RuntimeNoCommandlet), `IOSPreviewDeviceProfileSelector` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSDeviceProfileSelector) | |

## 用途

该插件的核心功能是在运行时根据当前 iOS/tvOS/VisionOS 设备的硬件能力，自动选择匹配的设备配置文件（Device Profile）。它解决了移动设备型号众多、性能差异巨大，开发者需要为不同设备设置不同画质、分辨率、特效等参数的问题。插件通过识别设备型号，将游戏的图形和性能设置映射到最合适的预设配置上，确保游戏在目标设备上以最佳性能和画质运行。

同时，它包含一个编辑器模块（`IOSPreviewDeviceProfileSelector`），允许开发者在编辑器中预览特定 iOS 设备的渲染效果，而无需部署到真机，方便跨设备调试和美术资源适配。

## 使用场景

- 你正在为多款 iOS 设备（从旧款 iPhone 到最新的 iPad Pro 或 Vision Pro）开发游戏，希望游戏能自动在不同设备上以最佳配置运行。
- 你需要为某些高端设备启用更复杂的后处理效果或更高的渲染分辨率，同时为低端设备保证流畅的帧率。
- 美术或技术美术需要在编辑器中预览特定 iOS 设备（如 iPhone 15 Pro Max）的渲染效果，以确保材质和光照效果的准确性。
- 你正在为 Apple Vision Pro 开发空间计算应用，并需要为其特有的显示和性能特性设置专门的配置。

## 蓝图用法

该插件的核心功能（设备识别与配置选择）主要在引擎的底层和配置文件层面工作，不直接暴露为蓝图节点。开发者通常通过维护 `DefaultDeviceProfiles.ini` 文件来定义不同设备型号对应的配置。

### 核心节点

编辑器模块提供了用于设备预览和配置导出的函数，但这些主要在编辑器工具或插件上下文中使用，不直接出现在游戏蓝图中。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportDeviceParametersToJson` | 将当前预览设备的参数导出为 JSON 文件 | `FIOSPreviewDeviceProfileSelectorModule` |
| `GetDeviceParametersFromJson` | 从 JSON 文件加载设备参数 | `FIOSPreviewDeviceProfileSelectorModule` |
| `SetSelectorProperties` | 设置选择器的属性（如要模拟的设备型号） | `FIOSPreviewDeviceProfileSelectorModule` |

**使用示例**：
在编辑器插件或命令行工具中，可以通过 C++ 代码获取 `FIOSPreviewDeviceProfileSelectorModule` 模块实例，然后调用 `SetSelectorProperties` 并传入 `TMap<FString, FString>` 来指定要模拟的设备（例如，设置键 `”DeviceModel”` 对应值 `”iPhone15,2”`），随后调用 `ExportDeviceParametersToJson` 将该设备的配置参数导出供分析或备份。

## C++ 用法

### 头文件引入

要使用设备配置选择器的核心接口，通常需要包含设备配置系统的头文件。
```cpp
#include “DeviceProfiles/DeviceProfileSelectorModule.h”
```

### 基本用法

在 iOS/tvOS/VisionOS 平台上，引擎在启动时会加载 `IOSDeviceProfileSelector` 模块。该模块实现了 `IDeviceProfileSelectorModule` 接口，其核心函数 `GetDeviceProfileName()` 会查询当前设备的型号（如 `iPhone14,2`），并在 `DefaultDeviceProfiles.ini` 中查找匹配的配置文件段（如 `[IOS DeviceProfile iPhone142]`）。

```cpp
// 在设备启动初期，引擎会调用选择器接口
// 位于：Engine/Source/Runtime/Engine/Private/DeviceProfiles/DeviceProfileManager.cpp (逻辑示意)
IDeviceProfileSelectorModule* SelectorModule = FModuleManager::Get().LoadModulePtr<IDeviceProfileSelectorModule>(“IOSDeviceProfileSelector”);
if (SelectorModule)
{
    // 获取当前硬件对应的设备配置名称
    FString DeviceProfileName = SelectorModule->GetDeviceProfileName();
    // 该名称随后被用于从配置文件中加载对应的画质、分辨率等设置
}
```

### 进阶用法

编辑器预览模块允许你在不部署到真机的情况下，模拟特定设备的配置。这对于跨平台美术调试非常有用。
```cpp
// 在编辑器工具中模拟一台 iPhone 15 Pro
#include “IOSPreviewDeviceProfileSelectorModule.h”

FIOSPreviewDeviceProfileSelectorModule* PreviewModule = static_cast<FIOSPreviewDeviceProfileSelectorModule*>(
    FModuleManager::Get().GetModule(“IOSPreviewDeviceProfileSelector”));

if (PreviewModule)
{
    // 设置要模拟的设备属性
    TMap<FString, FString> Properties;
    Properties.Add(“DeviceModel”, “iPhone15,2”); // iPhone 15 Pro 的标识符
    PreviewModule->SetSelectorProperties(Properties);

    // 此时，引擎的预览渲染管线会尝试采用该设备对应的配置进行渲染
    // 也可以将配置导出为 JSON 供外部分析
    TArray<FString> ExportedFiles;
    PreviewModule->ExportDeviceParametersToJson(FPaths::ProjectSavedDir(), ExportedFiles);
}
```

## Demo 示例

以下示例展示如何在编辑器插件中查询并打印当前 iOS 预览设备选择器的状态。这通常用于自定义设备调试工具。

```cpp
// IosDeviceProfileDebugModule.h
#pragma once
#include “Modules/ModuleManager.h”

class FIosDeviceProfileDebugModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// IosDeviceProfileDebugModule.cpp
#include “IosDeviceProfileDebugModule.h”
#include “IOSPreviewDeviceProfileSelectorModule.h”
#include “Misc/MessageDialog.h”

void FIosDeviceProfileDebugModule::StartupModule()
{
    // 模块启动时，尝试获取预览选择器并打印信息
    FIOSPreviewDeviceProfileSelectorModule* SelectorModule = static_cast<FIOSPreviewDeviceProfileSelectorModule*>(
        FModuleManager::Get().GetModule(“IOSPreviewDeviceProfileSelector”));

    if (SelectorModule)
    {
        UE_LOG(LogTemp, Log, TEXT(“IOSPreviewDeviceProfileSelector module loaded.”));
        // 查询一个示例属性
        FString PropertyValue;
        if (SelectorModule->GetSelectorPropertyValue(FName(“CurrentDeviceModel”), PropertyValue))
        {
            UE_LOG(LogTemp, Log, TEXT(“Current Preview Device: %s”), *PropertyValue);
        }
    }
}

void FIosDeviceProfileDebugModule::ShutdownModule()
{
    // 清理
}

IMPLEMENT_MODULE(FIosDeviceProfileDebugModule, IosDeviceProfileDebug);
```

## 模块依赖

该插件的运行时模块没有特殊的公开依赖。编辑器预览模块依赖于 iOS 平台控制模块以获取设备信息。

| 模块 | 用途 |
|---|---|
| `IOSTargetPlatformControls` | 提供 iOS 平台设备信息查询、控件等功能，用于编辑器预览模块识别和模拟设备。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的日志宏迁移至新的 UE_LOGF 宏。 |
| 2026-02-24 | `6fa9a99f` | Add Aspect Ratio to IOS Preview Json | 为 iOS 预览 JSON 配置文件添加了屏幕宽高比参数。 |
| 2026-02-18 | `f5a10b68` | Add Preview json Versioning | 为预览 JSON 配置文件增加了版本控制功能。 |
| 2026-02-13 | `bbbd7847` | Add ConfigRules to Android Preview Json | (本次提交信息关联 Android，但可能影响了共享的预览 JSON 处理逻辑。) |
| 2026-02-11 | `87fe38ca` | Fix RTTI Linux | 修复了在 Linux 平台上相关的运行时类型识别(RTTI)问题。 |

### 维护评价

该插件自 2014 年创建以来一直是 UE 移动开发（尤其是 iOS）的基础组件，历经多年考验。从最近的提交记录（2026年）来看，它仍在被积极维护，近期更新包括适应新日志系统、增加预览功能参数和修复跨平台问题，表明 Epic 将其视为持续支持的核心功能。

对于 iOS/tvOS/VisionOS 开发而言，这是一个**必备且推荐启用**的插件。它没有任何已知的替代方案，且随着 Apple 新设备的发布，其设备数据库和选择逻辑会持续更新。**推荐所有面向 Apple 移动设备的 UE 项目保持该插件启用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSDeviceProfileSelector)
- [官方文档](https://docs.unrealengine.com/) (通用设备配置文档，该插件无专属文档页)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/RHI) (相关测试可能位于 RHI 或通用设备配置测试中，插件本身无独立测试目录)