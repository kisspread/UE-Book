# Windows Device Profile Selector

> Windows Device Profile Selector used to determine the system settings for windows platforms

| 属性 | 值 |
|---|---|
| 分类 | Device Profile Selectors |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | WindowsDeviceProfileSelector (RuntimeNoCommandlet) |
| 加载阶段 | PostConfigInit |
| 平台限制 | Win64 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WindowsDeviceProfileSelector) | |

## 用途

这个 plugin 是 UE5 设备配置文件（Device Profile）系统的 Windows 平台选择器。它实现了 `IDeviceProfileSelectorModule` 接口，在运行时根据当前 Windows 环境自动选择最合适的设备配置文件名称。

核心逻辑在 `GetRuntimeDeviceProfileName()` 中，按以下优先级确定配置文件名：

1. **自定义覆盖**：如果定义了 `WINDOWS_OVERRIDE_DEVICEPROFILE_NAME` 宏（用于 Windows 平台扩展），直接使用该名称
2. **Cooked Editor**：如果是 Cooked Editor 环境，返回 `WindowsCookedEditor`
3. **默认平台名**：使用 `FPlatformProperties::PlatformName()`，返回 `Windows`、`WindowsEditor`、`WindowsClient` 或 `WindowsServer`
4. **RHI 特化**：在可渲染环境下，尝试追加当前 RHI 名称（如 `Windows_D3D12RHI`、`Windows_VulkanRHI`），如果该配置文件存在则使用之
5. **ES31 回退**：如果 RHI 名称包含 `_ES31`，还会尝试通用的 `_ES31` 后缀配置文件

这个机制使得项目可以在 `DeviceProfiles.ini` 中为不同的 Windows 运行环境（编辑器/客户端/服务器）和不同的图形 API（D3D11/D3D12/Vulkan）定义不同的画质和性能配置。

## 使用场景

- 你的项目需要在 Windows 上根据不同的 RHI（D3D12 vs Vulkan）自动切换画质预设 → 此 plugin 自动完成
- 你需要为 WindowsClient 和 WindowsEditor 定义不同的设备配置 → 此 plugin 自动选择正确的配置文件名
- 你正在开发 Windows 平台扩展（如 GDK），需要自定义设备配置文件名 → 使用 `WINDOWS_OVERRIDE_DEVICEPROFILE_NAME` 宏覆盖
- 你需要为 ES31 兼容模式（如通过 SwiftShader 运行 Vulkan ES31）单独配置 → plugin 会自动检测并选择 `_ES31` 后缀的配置文件

## 蓝图用法

此 plugin 不暴露任何蓝图接口。它的功能完全在引擎启动时自动执行，无需手动调用。

## C++ 用法

此 plugin 通常不需要直接调用——它由 `UDeviceProfileManager` 在引擎初始化时自动加载和使用。但你可以通过引擎 API 获取当前选中的设备配置文件名。

### 头文件引入

```cpp
#include "DeviceProfiles/DeviceProfileManager.h"
```

### 获取当前设备配置文件名

```cpp
// 获取设备配置文件选择器模块
IDeviceProfileSelectorModule* SelectorModule = UDeviceProfileManager::GetDeviceProfileSelectorModule();
if (SelectorModule)
{
    // 获取运行时选择的设备配置文件名称
    FString ProfileName = SelectorModule->GetRuntimeDeviceProfileName();
    // 结果可能是: "Windows", "WindowsClient", "Windows_D3D12RHI", "WindowsCookedEditor" 等
    UE_LOG(LogTemp, Log, TEXT("Selected Device Profile: %s"), *ProfileName);
}
```

### 自定义设备配置文件名覆盖

如果你在开发 Windows 平台扩展，可以通过定义宏来覆盖默认的配置文件名选择逻辑：

```cpp
// 在你的 Target.cs 或 Build.cs 中定义
// PublicDefinitions.Add("WINDOWS_OVERRIDE_DEVICEPROFILE_NAME=\"MyCustomPlatform\"");
```

定义后，`GetRuntimeDeviceProfileName()` 将直接返回 `MyCustomPlatform`，跳过所有其他检测逻辑。

### 配置 DeviceProfiles.ini

在项目的 `DefaultDeviceProfiles.ini` 中，可以为不同的 Windows 配置文件定义不同的设置：

```ini
[Windows DeviceProfile]
+CVars=r.DefaultFeature.AntiAliasing=2

[Windows_D3D12RHI DeviceProfile]
+CVars=r.DefaultFeature.AntiAliasing=4
+CVars=r.RayTracing=1

[Windows_VulkanRHI DeviceProfile]
+CVars=r.DefaultFeature.AntiAliasing=2
+CVars=r.RayTracing=0

[WindowsClient DeviceProfile]
+CVars=r.DefaultFeature.AntiAliasing=3

[WindowsClient_D3D12RHI DeviceProfile]
+CVars=r.RayTracing=1
+CVars=r.Lumen.ScreenTraces=1
```

## Demo 示例

此 plugin 是纯基础设施，没有可运行的独立示例。以下是一个完整的设备配置文件选择流程说明：

```
引擎启动
  → UDeviceProfileManager 初始化
    → 遍历所有 IDeviceProfileSelectorModule 实现
      → WindowsDeviceProfileSelector 插件被发现（因为模块实现了该接口）
        → 调用 GetRuntimeDeviceProfileName()
          → 检测平台: "WindowsClient"
          → 检测 RHI: "D3D12RHI"
          → 检查 DeviceProfiles.ini 中是否存在 "WindowsClient_D3D12RHI DeviceProfile"
            → 存在: 返回 "WindowsClient_D3D12RHI"
            → 不存在: 回退到 "WindowsClient"
  → 加载对应的 DeviceProfile 配置
  → 应用 CVars 设置
```

## 模块依赖

从 `WindowsDeviceProfileSelector.Build.cs` 提取：

| 模块 | 类型 | 用途 |
|---|---|---|
| `Core` | Public | 基础核心模块，提供 FString、FConfigCacheIni 等 |
| `Engine` | Private | 提供 IDeviceProfileSelectorModule 接口和 DeviceProfileManager |
| `RHI` | Private | 提供 `GetSelectedDynamicRHModuleName()` 用于检测当前 RHI |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-02 | `54090899b31b` | Separate ES31 device profile by RHI e.g. WindowsClient_ES31_D3D12RHI | 功能增强：ES31 配置文件现在也按 RHI 细分，支持 `WindowsClient_ES31_D3D12RHI` 等更精确的配置 |
| 2023-12-11 | `e9661bc76853` | Preparing for dependency cleanup | 维护性改动，为模块依赖清理做准备 |
| 2023-05-15 | `da92084a122a` | Optimized out more private modules includes and dependencies | 编译优化，减少不必要的头文件包含 |

### 维护评价

- **年龄**：创建于 2014 年，已超过 12 年，属于 🏛️ 文物级别
- **最近更新**：2025 年 6 月有功能性更新（ES31 RHI 细分），说明仍在活跃维护
- **代码规模**：极小（仅 3 个源文件，核心逻辑约 60 行），结构稳定，几乎不需要频繁修改
- **稳定性**：作为基础设施组件，逻辑简单明确，多年来核心接口未变
- **推荐使用**：✅ 默认启用，无需手动操作。如果你的项目仅面向 Windows，此 plugin 会自动生效

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WindowsDeviceProfileSelector)
- [IDeviceProfileSelectorModule 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Public/IDeviceProfileSelectorModule.h)
- [DeviceProfileManager](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Classes/DeviceProfiles/DeviceProfileManager.h)
