# Example Device Profile Selector

> Example Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 中文名 | 设备配置示例选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ExampleDeviceProfileSelector` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ExampleDeviceProfileSelector) | |

## 用途

这个插件是一个**示例**，用于演示如何为特定硬件设备选择不同的设备配置文件（Device Profile）。设备配置文件是 UE 中用于根据平台（如 PC、移动设备、主机）或特定硬件配置来调整引擎设置（如图形质量、分辨率、功能开关等）的机制。`ExampleDeviceProfileSelector` 展示了如何实现 `IDeviceProfileSelectorModule` 接口，从而根据当前运行的硬件环境返回一个合适的配置文件名称，而不是使用引擎默认的设备选择逻辑。它本身不提供复杂的硬件检测，主要用于教学和作为自定义设备选择器的起点模板。

## 使用场景

- 当你需要为游戏支持多种硬件设备（如高中低端手机、不同配置的 PC）并想根据具体设备型号自动应用最合适的画质设置时。
- 你希望学习或实现一个自定义的设备配置文件选择逻辑，而不是依赖引擎默认的 `Platform` 名称来选择 Profile。
- 在开发过程中，需要快速测试不同设备配置文件在不同场景下的表现。

## 蓝图用法

此插件是一个纯粹的 C++ 模块，不提供任何蓝图节点。它通过注册一个模块接口来工作，该接口在引擎初始化时被调用。

## C++ 用法

### 头文件引入

```cpp
#include "ExampleDeviceProfileSelectorModule.h"
```

### 基本用法

此插件的核心是实现 `IDeviceProfileSelectorModule` 接口。要创建自己的设备选择器，需要继承并实现该接口。以下是一个基于该示例的基本用法说明。

```cpp
// 假设你要创建一个名为 `FMyDeviceProfileSelectorModule` 的自定义选择器
// （来源：Engine/Plugins/Runtime/ExampleDeviceProfileSelector/Source/ExampleDeviceProfileSelector/Private/ExampleDeviceProfileSelectorModule.h）

#include "IDeviceProfileSelectorModule.h"
#include "Modules/ModuleManager.h"

class FMyDeviceProfileSelectorModule : public IDeviceProfileSelectorModule
{
public:
    // 在这里实现获取运行时设备配置文件名称的逻辑
    virtual const FString GetRuntimeDeviceProfileName() override
    {
        // 在实际实现中，这里会包含复杂的硬件检测逻辑（如查询设备型号、GPU 能力等）
        // 并返回一个对应的设备配置文件名称字符串。
        // 例如：
        // if (IsHighEndDevice())
        //     return TEXT("HighEnd_Mobile");
        // else
        //     return TEXT("LowEnd_Mobile");
        return TEXT("MyCustomProfile");
    }

    // 模块生命周期函数
    virtual void StartupModule() override
    {
        // 可选：模块启动时的初始化代码
    }

    virtual void ShutdownModule() override
    {
        // 可选：模块关闭时的清理代码
    }
};
```

### 进阶用法

在实际项目中，`GetRuntimeDeviceProfileName()` 方法内部需要整合硬件检测逻辑。这通常涉及查询平台相关的 API（如 Android 的 `Build.MODEL` 或 iOS 的设备标识符）以及评估 GPU 能力等。最终返回的字符串必须与项目设置中的设备配置文件（Device Profiles）列表中的名称匹配。

## Demo 示例

一个完整且可运行的最小自定义设备配置文件选择器模块示例。

**MyDeviceSelector.h**
```cpp
#pragma once

#include "IDeviceProfileSelectorModule.h"
#include "CoreMinimal.h"

class FMyDeviceSelectorModule : public IDeviceProfileSelectorModule
{
public:
    virtual const FString GetRuntimeDeviceProfileName() override;

    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyDeviceSelector.cpp**
```cpp
#include "MyDeviceSelector.h"

const FString FMyDeviceSelectorModule::GetRuntimeDeviceProfileName()
{
    // 简单示例：根据是否为移动平台返回不同配置文件
#if PLATFORM_ANDROID || PLATFORM_IOS
    return TEXT("Mobile_Profile");
#else
    return TEXT("Desktop_Profile");
#endif
}

void FMyDeviceSelectorModule::StartupModule()
{
    // 模块启动时可以注册一些服务或执行初始化
}

void FMyDeviceSelectorModule::ShutdownModule()
{
    // 模块关闭时进行清理
}

// 注册模块
IMPLEMENT_MODULE(FMyDeviceSelectorModule, MyDeviceSelector);
```

## 模块依赖

要使用此插件或基于它创建自定义实现，你的模块需要依赖 `DeviceProfileSelector` 模块。

| 模块 | 用途 |
|---|---|
| `DeviceProfileSelector` | 提供设备配置文件选择的核心接口 `IDeviceProfileSelectorModule`。 |

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将遗留的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏，属于引擎日志系统的现代化更新。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件的批处理提交，可能包含项目设置、元数据或轻微的构建系统调整，无实质性功能变更。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的供应商链接从 HTTP 更新为 HTTPS，属于安全合规性维护。 |

### 维护评价

`ExampleDeviceProfileSelector` 作为一个创建于 2014 年的示例插件，其核心功能自诞生以来基本未发生变化。近期（2026 年）的更新仅涉及引擎内部的日志宏迁移，属于被动维护。它在 2022 年和 2023 年有过零星的维护性更新，主要是为了跟上引擎的底层变更（如安全链接、项目结构调整）。该插件状态稳定，但由于其示例性质，预计不会有新功能添加。它**适合作为学习和参考的模板**，不建议在生产环境中直接使用此插件，而是应在其基础上创建自己的实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ExampleDeviceProfileSelector)
- 官方文档：无
- 测试用例：无