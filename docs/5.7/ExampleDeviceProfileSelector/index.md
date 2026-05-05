# Example Device Profile Selector

> Example Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 否 |
| 模块 | ExampleDeviceProfileSelector (RuntimeNoCommandlet) |
| 加载阶段 | PostConfigInit |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（>10年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ExampleDeviceProfileSelector) | |

## 用途

这是一个 **示例插件**，演示如何通过实现 `IDeviceProfileSelectorModule` 接口来自定义设备配置文件（Device Profile）的选择逻辑。

UE5 的 Device Profile 系统允许开发者针对不同硬件平台设置不同的画质/性能配置。引擎在启动时需要决定当前设备使用哪个 Device Profile，而这个选择逻辑正是通过实现 `IDeviceProfileSelectorModule` 接口的插件来完成的。

本插件的实现极其简单：`GetRuntimeDeviceProfileName()` 直接返回 `FPlatformProperties::PlatformName()`，即当前运行平台的名称（如 `Windows`、`Android`、`IOS` 等）。这意味着它选择的 Device Profile 与平台名称完全一致，不进行任何额外的硬件检测或条件判断。

**核心价值**：作为模板，帮助开发者理解 Device Profile Selector 的接口规范，以便编写自己的自定义选择器（例如根据 GPU 型号、内存大小等选择不同的配置）。

## 使用场景

- 你想根据硬件参数（GPU、内存、CPU 核心数等）动态选择不同的画质配置 → 参考本插件实现 `IDeviceProfileSelectorModule`
- 你在为自定义平台移植 UE5 → 需要编写一个 Device Profile Selector 来匹配你的硬件
- 你想理解 UE5 Device Profile 选择机制的运作方式 → 阅读本插件源码作为起点

## 蓝图用法

本插件不提供任何蓝图接口。设备配置文件的选择在引擎启动的极早期（`PostConfigInit` 阶段）完成，此时蓝图系统尚未初始化。

## C++ 用法

### 核心接口

本插件的关键是实现 `IDeviceProfileSelectorModule` 接口。该接口定义在引擎中：

```cpp
// Engine/Source/Runtime/Engine/Public/IDeviceProfileSelectorModule.h
class IDeviceProfileSelectorModule : public IModuleInterface
{
public:
    // 必须实现：返回当前会话使用的 Device Profile 名称
    virtual const FString GetRuntimeDeviceProfileName() = 0;

    // 可选：根据设备参数选择 Profile（带参数版本）
    virtual const FString GetDeviceProfileName() { return FString(); }

    // 可选：设置选择器属性
    virtual void SetSelectorProperties(const TMap<FName, FString>& SelectorProperties) {}

    // 可选：查询选择器属性值
    virtual bool GetSelectorPropertyValue(const FName& PropertyType, FString& PropertyValueOUT) { return false; }
};
```

### 头文件引入

```cpp
#include "IDeviceProfileSelectorModule.h"
```

### 基本用法（本插件的实现）

来源：`Source/ExampleDeviceProfileSelector/Private/ExampleDeviceProfileSelectorModule.cpp`

```cpp
#include "ExampleDeviceProfileSelectorModule.h"
#include "Modules/ModuleManager.h"

// 注册模块
IMPLEMENT_MODULE(FExampleDeviceProfileSelectorModule, ExampleDeviceProfileSelector);

void FExampleDeviceProfileSelectorModule::StartupModule()
{
    // 无需初始化
}

void FExampleDeviceProfileSelectorModule::ShutdownModule()
{
    // 无需清理
}

// 核心方法：返回设备配置文件名称
const FString FExampleDeviceProfileSelectorModule::GetRuntimeDeviceProfileName()
{
    // 直接返回平台名称，如 "Windows"、"Android"、"IOS" 等
    FString ProfileName = FPlatformProperties::PlatformName();
    UE_LOG(LogInit, Log, TEXT("Selected Device Profile: [%s]"), *ProfileName);
    return ProfileName;
}
```

### 进阶用法：自定义设备选择器

如果你需要根据硬件参数选择不同的 Device Profile，可以扩展这个模式：

```cpp
// MyDeviceProfileSelectorModule.h
#pragma once

#include "IDeviceProfileSelectorModule.h"

class FMyDeviceProfileSelectorModule : public IDeviceProfileSelectorModule
{
public:
    virtual const FString GetRuntimeDeviceProfileName() override;
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    virtual ~FMyDeviceProfileSelectorModule() {}

private:
    // 根据 GPU 选择配置
    FString SelectProfileByGPU();
};
```

```cpp
// MyDeviceProfileSelectorModule.cpp
#include "MyDeviceProfileSelectorModule.h"
#include "Modules/ModuleManager.h"
#include "RHI.h"

IMPLEMENT_MODULE(FMyDeviceProfileSelectorModule, MyDeviceProfileSelector);

const FString FMyDeviceProfileSelectorModule::GetRuntimeDeviceProfileName()
{
    // 先尝试根据 GPU 选择
    FString Profile = SelectProfileByGPU();
    if (!Profile.IsEmpty())
    {
        return Profile;
    }

    // 回退到平台默认
    return FPlatformProperties::PlatformName();
}

FString FMyDeviceProfileSelectorModule::SelectProfileByGPU()
{
    FString GPUName = GRHIAdapterName;
    // 根据 GPU 型号返回对应的 Profile 名称
    // ...
    return FString();
}
```

## Demo 示例

### 最小可运行的 Device Profile Selector

**Build.cs**：
```csharp
using UnrealBuildTool;

public class MyDeviceProfileSelector : ModuleRules
{
    public MyDeviceProfileSelector(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] { "Core" });
        PrivateDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
    }
}
```

**.uplugin**：
```json
{
    "FileVersion": 3,
    "Version": 1,
    "VersionName": "1.0",
    "FriendlyName": "My Device Profile Selector",
    "Description": "Custom device profile selector based on hardware",
    "Category": "Device Profile Selectors",
    "CreatedBy": "Your Company",
    "EnabledByDefault": true,
    "CanContainContent": false,
    "Modules": [
        {
            "Name": "MyDeviceProfileSelector",
            "Type": "RuntimeNoCommandlet",
            "LoadingPhase": "PostConfigInit"
        }
    ]
}
```

**注意事项**：
- 模块类型必须是 `RuntimeNoCommandlet`（不能在 Commandlet 中运行）
- 加载阶段必须是 `PostConfigInit`（在配置初始化之后立即加载）
- 只能有一个活跃的 Device Profile Selector 插件（多个会冲突）

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、平台抽象（`FPlatformProperties`） |
| `CoreUObject` | 对象系统基础 |
| `Engine` | `IDeviceProfileSelectorModule` 接口定义 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da7` | [Engine/Plugins] Another batch IWYU updates to reduce number of includes used in files | IWYU（Include What You Use）编译优化，无功能变更 |
| 2022-11-07 | `0a10c21f` | Update Release-Engine-Staging from UE5/Main | 引擎版本同步，非插件自身更新 |
| 2019-12-27 | `360d078c` | Second batch of remaining Engine copyright updates | 版权声明批量更新，无功能变更 |

### 维护评价

- **创建时间**：2014 年 3 月，已有 12+ 年历史
- **功能变更**：自创建以来，核心逻辑（`GetRuntimeDeviceProfileName` 返回平台名称）从未改变
- **维护频率**：最近的更新仅限于 IWYU 和版权等批量维护操作，无实质性功能更新
- **状态评估**：这是一个 **稳定的示例代码**，并非活跃维护的功能性插件。它作为教学模板存在，功能极度简单且成熟，不需要频繁更新
- **推荐**：✅ 适合用于学习 Device Profile Selector 接口，或作为自定义实现的起点。但不要期望它提供复杂功能

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ExampleDeviceProfileSelector)
- [IDeviceProfileSelectorModule 接口定义](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Public/IDeviceProfileSelectorModule.h)
