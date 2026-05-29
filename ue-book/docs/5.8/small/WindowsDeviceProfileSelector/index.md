# Windows Device Profile Selector

> Windows Device Profile Selector used to determine the system settings for windows platforms

| 属性 | 值 |
|---|---|
| 中文名 | Windows 设备配置选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WindowsDeviceProfileSelector` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WindowsDeviceProfileSelector) | |

## 用途

该插件是 UE5 设备配置选择系统（Device Profile Selector）的 Windows 平台实现。它在运行时检测当前 Windows 系统的硬件规格（如显卡型号、显存大小、CPU 核心数等），然后自动匹配最适合的设备配置（Device Profile）。

设备配置系统是 UE5 的质量设置基础架构——通过选择不同的 Device Profile，引擎会自动调整纹理质量、阴影分辨率、渲染距离等参数，确保游戏在不同硬件上获得最佳平衡的画质与性能。

该插件与 `DeviceProfileSelector`（通用设备配置选择器模块）配合使用，专注于 Win64 平台的硬件识别逻辑。

## 使用场景

- 你的游戏需要自动适配不同 Windows 硬件 → 引擎默认启用此插件，无需额外操作
- 你想根据用户显卡自动切换画质预设（低/中/高/极高）→ 依赖此插件的设备检测能力
- 你需要在 Project Settings → Device Profiles 中配置不同硬件档次的参数 → 该插件提供硬件检测依据

## 蓝图用法

该插件没有暴露蓝图接口。设备配置选择是引擎底层机制，在游戏启动阶段自动执行，不直接提供蓝图节点。

配置设备配置文件的方式是通过 Project Settings → Engine → Device Profiles 面板，或在 `DefaultDeviceProfiles.ini` 中手动定义。

## C++ 用法

### 头文件引入

```cpp
#include "IDeviceProfileSelectorModule.h"
```

### 基本用法

该插件通过引擎的模块系统自动加载。核心接口是 `IDeviceProfileSelectorModule`：

```cpp
// 获取设备配置选择器模块实例
IModuleInterface* Module = FModuleManager::Get().LoadModule(TEXT("WindowsDeviceProfileSelector"));

// 或通过接口访问
IDeviceProfileSelectorModule* SelectorModule = 
    FModuleManager::Get().LoadModulePtr<IDeviceProfileSelectorModule>("WindowsDeviceProfileSelector");

if (SelectorModule)
{
    // 获取当前系统匹配的设备配置名称
    FString ProfileName = SelectorModule->GetRuntimeDeviceProfileName();
    // ProfileName 例如: "Windows", "Windows_Mid", "Windows_Low" 等
}
```

### 进阶用法

通常不需要直接调用此插件 API。设备配置选择在引擎初始化阶段由 `FDeviceProfileManager` 自动完成。如需自定义选择逻辑，可实现自己的 `IDeviceProfileSelectorModule`：

```cpp
// 自定义设备配置选择器（替代本插件）
class FMyDeviceProfileSelector : public IDeviceProfileSelectorModule
{
public:
    virtual const FString GetRuntimeDeviceProfileName() override
    {
        // 自定义硬件检测逻辑
        if (IsHighEndGPU())
        {
            return TEXT("Windows_Ultra");
        }
        return TEXT("Windows_Low");
    }
    
    virtual void StartupModule() override {}
    virtual void ShutdownModule() override {}
};
```

## Demo 示例

该插件是纯接口实现，无独立可运行示例。其工作原理在引擎启动时自动执行——调用 `GetRuntimeDeviceProfileName()` 返回设备配置名，引擎据此加载对应的 `DeviceProfiles.ini` 配置。

验证插件是否生效：

```cpp
// 在游戏启动后检查当前设备配置
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();
    
    const UDeviceProfileManager& Manager = UDeviceProfileManager::Get();
    UE_LOG(LogTemp, Log, TEXT("Active Device Profile: %s"), *Manager.GetActiveDeviceProfileName());
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 模块及 `IDeviceProfileSelectorModule` 接口）。

该插件依赖引擎内置的设备配置选择器接口定义，位于 Engine 模块中。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-03-27 | `eeaeefb3` | Speed up InitializeCVarsForActiveDeviceProfile by skipping GetSelectedDynamicRHIModuleName when no R | 优化配置初始化性能，跳过不必要的 RHI 模块查询 |
| 2026-03-26 | `ed80a721` | Add more CPU profiling scopes to major functions that run on editor/engine startup | 添加 CPU 性能分析标记，便于启动阶段性能诊断 |
| 2026-02-11 | `4634cb99` | Adding support for ConfigRules to Windows. | 为 Windows 平台添加 ConfigRules 支持 |
| 2026-01-12 | `e8646bea` | Cache GConfig reads from FWindowsDeviceProfileSelectorModule to reduce potential hitches if GEngineI | 缓存配置读取以减少启动时的性能抖动 |

### 维护评价

该插件虽然创建于 2014 年（文物级），但**维护非常活跃**。2026 年初的更新涵盖了性能优化（缓存、跳过冗余查询）、新特性（ConfigRules 支持）和代码质量改进（日志迁移、性能分析），表明 Epic 持续投入维护。

作为引擎默认启用的基础插件，它为 Windows 平台的画质自适应提供了关键支撑。代码量极小（3 个文件），接口清晰，是一个稳定可靠的基础设施组件。**强烈推荐保留默认启用状态**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WindowsDeviceProfileSelector)
- [接口定义 - IDeviceProfileSelectorModule](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Source/Runtime/Engine/Public/IDeviceProfileSelectorModule.h)
- [通用设备配置选择器](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/DeviceProfileSelector)