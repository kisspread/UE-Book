# Example Device Profile Selector

> Example Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 中文名 | 示例设备配置选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ExampleDeviceProfileSelector` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ExampleDeviceProfileSelector) | |

## 用途

该插件是一个**参考实现**和**示例**，用于演示如何创建自定义的设备配置文件选择器。其核心功能是让引擎能够根据当前运行的硬件平台或设备类型，动态选择并加载对应的设备配置文件（Device Profile）。设备配置文件允许开发者为不同硬件（如高端PC、低端PC、不同主机、移动设备等）定义不同的图形、性能和质量设置，以实现游戏的自适应优化。

## 使用场景

- 你在开发一款需要跨多种硬件平台（PC、主机、移动设备）运行的游戏，希望根据设备性能自动应用不同的画质预设。
- 你需要实现比引擎内置设备配置文件选择逻辑更复杂的判断规则（例如，根据具体GPU型号、内存大小、操作系统版本等综合判断）。
- 你正在学习如何编写引擎的底层模块，特别是如何实现 `IDeviceProfileSelectorModule` 接口。

## 蓝图用法

该插件主要通过 C++ 模块接口工作，不提供直接可用的蓝图节点。

## C++ 用法

### 头文件引入

由于这是一个示例模块，通常不会直接引用它。如果你需要编写自己的设备配置选择器，则需要实现 `IDeviceProfileSelectorModule` 接口，该接口定义在 `DeviceProfileServices` 模块中。

```cpp
#include “IDeviceProfileSelectorModule.h”
```

### 基本用法

要创建一个设备配置选择器，你需要实现 `IDeviceProfileSelectorModule` 接口。下面是一个基于本示例插件结构的简化说明：

1.  **声明模块类**：继承 `IDeviceProfileSelectorModule`。
2.  **实现核心函数**：`GetRuntimeDeviceProfileName()`，该函数负责返回当前设备应使用的配置文件名称。

```cpp
// 你的自定义选择器模块头文件 (示例)
#pragma once

#include “IDeviceProfileSelectorModule.h”

class FMyDeviceProfileSelectorModule : public IDeviceProfileSelectorModule
{
public:
    // 返回当前设备对应的配置文件名称
    virtual const FString GetRuntimeDeviceProfileName() override;
    
    // 模块生命周期函数
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// 你的自定义选择器模块实现 (示例)
#include “MyDeviceProfileSelectorModule.h”

const FString FMyDeviceProfileSelectorModule::GetRuntimeDeviceProfileName()
{
    // 在这里编写你的硬件检测和配置文件选择逻辑
    // 例如：根据GPU名称、内存、分辨率等返回 “PC_Low”, “PC_Medium”, “Console_Xbox” 等字符串
    FString ProfileName = TEXT(“Default”);
    // ... 复杂判断逻辑 ...
    return ProfileName;
}

void FMyDeviceProfileSelectorModule::StartupModule()
{
    // 模块启动时的初始化代码（如果需要）
}

void FMyDeviceProfileSelectorModule::ShutdownModule()
{
    // 模块关闭时的清理代码（如果需要）
}
```

### 进阶用法

实际应用中，`GetRuntimeDeviceProfileName()` 的实现会非常复杂，可能需要：
*   查询 `FPlatformMisc` 获取系统信息。
*   检查 `GRHIAdapterName` 获取GPU信息。
*   结合多个条件（如平台、GPU、内存、用户设置）进行综合判断。
*   加载一个配置文件或数据表来定义映射规则。

## Demo 示例

下面是一个最小的自定义设备配置选择器模块示例，它根据当前平台简单返回一个配置文件名。

**MyDeviceProfileSelector.h**
```cpp
#pragma once

#include “IDeviceProfileSelectorModule.h”

class FMyDeviceProfileSelectorModule : public IDeviceProfileSelectorModule
{
public:
    virtual const FString GetRuntimeDeviceProfileName() override;
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    virtual ~FMyDeviceProfileSelectorModule() {}
};
```

**MyDeviceProfileSelector.cpp**
```cpp
#include “MyDeviceProfileSelector.h”
#include “Misc/PlatformMisc.h”

const FString FMyDeviceProfileSelectorModule::GetRuntimeDeviceProfileName()
{
    // 简单的平台判断逻辑
    FString PlatformName = FPlatformProperties::PlatformName();
    if (PlatformName == TEXT(“Windows”))
    {
        return TEXT(“PC_Default”);
    }
    else if (PlatformName == TEXT(“XSX”) || PlatformName == TEXT(“PS5”))
    {
        return TEXT(“NextGenConsole”);
    }
    else if (PlatformName == TEXT(“Android”) || PlatformName == TEXT(“IOS”))
    {
        return TEXT(“Mobile”);
    }
    // 默认返回
    return TEXT(“Default”);
}

void FMyDeviceProfileSelectorModule::StartupModule()
{
    // 注册模块逻辑（通常由引擎自动处理，此处可留空）
}

void FMyDeviceProfileSelectorModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyDeviceProfileSelectorModule, MyDeviceProfileSelector)
```

## 模块依赖

从插件的用途推断，它主要依赖引擎的核心设备配置服务模块。

| 模块 | 用途 |
|---|---|
| `DeviceProfileServices` | 提供 `IDeviceProfileSelectorModule` 接口定义和设备配置文件管理的核心功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏统一迁移到新的 UE_LOGF 宏，属于代码现代化清理。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件相关的通用提交，可能是路径或构建系统调整。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接，使用安全协议（HTTPS），属于维护性更新。 |
| 2019-12-27 | `360d078c` | Second batch of remaining Engine copyright updates. | 批量更新引擎版权年份，纯文本修改。 |
| 2018-12-14 | `7598af05` | Update copyright notices to 2019. | 更新版权年份至2019年，纯文本修改。 |

### 维护评价

该插件创建于 **2014年**，是一个历史悠久的示例模块。查看其近期提交记录可以发现，过去 **超过10年** 的所有提交均为版权更新、日志宏迁移或通用的插件系统维护，**没有任何实质性功能更新或bug修复**。它作为一个稳定的 API 示例存在，其核心接口（`IDeviceProfileSelectorModule`）已成为引擎标准部分。

**结论**：这是一个**功能稳定但已停止活跃开发**的示例插件。它仍然可以作为学习和实现自定义设备配置选择器的**有效参考**，但不应期待任何新功能。对于生产环境，通常建议直接实现 `IDeviceProfileSelectorModule` 接口，而不是依赖或修改此示例插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ExampleDeviceProfileSelector)
- [官方文档]( )（无）