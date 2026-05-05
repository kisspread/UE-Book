# Linux Device Profile Selector

> Linux Device Profile Selector

| 属性 | 值 |
|---|---|
| 分类 | Device Profile Selectors |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | LinuxDeviceProfileSelector (RuntimeNoCommandlet, PostConfigInit) |
| 创建时间 | 2015-09-24 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LinuxDeviceProfileSelector) | |

## 用途

LinuxDeviceProfileSelector 是 UE5 Device Profile 系统在 Linux 平台上的"选择器"模块。它实现 `IDeviceProfileSelectorModule` 接口，在运行时决定引擎应该加载哪一个 Device Profile。

**核心逻辑极其简单**：正常情况下直接返回平台名称 `"Linux"` 或 `"LinuxArm64"`（即 `FPlatformProperties::PlatformName()`）；如果是 Cooked Editor 构建（`UE_IS_COOKED_EDITOR`），则返回 `"LinuxCookedEditor"`。

这使得引擎在启动时能根据当前平台自动应用对应的 Device Profile（分辨率、纹理池大小、画质设置等），而无需手动指定。

### 工作原理

1. 引擎启动时，`UDeviceProfileManager::GetDeviceProfileSelectorModule()` 从 `GEngineIni` 中读取 `[DeviceProfileManager] DeviceProfileSelectionModule` 配置项
2. 对于 Linux 平台，该值为 `"LinuxDeviceProfileSelector"`（配置在 `Engine/Config/Linux/LinuxEngine.ini` 和 `LinuxArm64/LinuxArm64Engine.ini` 中）
3. 引擎加载本模块，调用 `GetRuntimeDeviceProfileName()` 获取 profile 名称
4. 使用该 profile 名称查找对应的 Device Profile 配置并应用

命令行参数 `-DeviceProfile=XXX` 或 `-DP=XXX` 可以覆盖选择器的结果。

## 使用场景

- 你部署 UE5 游戏到 Linux 服务器（Dedicated Server） → 引擎自动通过此插件选择 Linux Device Profile
- 你在 Steam Deck 等 Linux 游戏设备上运行 → 引擎自动选择对应的 Device Profile 来适配硬件
- 你在 Linux ARM64（如树莓派、Jetson）上运行 → 引擎选择 LinuxArm64 平台的 Device Profile
- 你使用 Cooked Editor 工作流 → 选择器会返回专用的 `LinuxCookedEditor` profile

## 蓝图用法

本插件不暴露任何蓝图接口。它是一个纯运行时基础设施模块，完全由引擎在启动阶段自动调用，无需也不支持蓝图交互。

## C++ 用法

### 头文件引入

```cpp
#include "IDeviceProfileSelectorModule.h"
```

### 基本用法

本插件不是作为库来使用的——它是引擎 Device Profile 系统的平台适配组件。如果你需要在代码中与 Device Profile 系统交互：

```cpp
// 获取当前平台的 Device Profile 名称
FString PlatformProfileName = UDeviceProfileManager::Get().GetActiveDeviceProfileName();

// 或者直接获取平台名（等同于本插件的输出）
FString PlatformName = FPlatformProperties::PlatformName(); // "Linux" 或 "LinuxArm64"
```

### 进阶：替换选择器

如果你需要自定义 Linux 平台的 Device Profile 选择逻辑（例如根据 GPU 型号选择不同 profile），可以：

1. 创建新模块实现 `IDeviceProfileSelectorModule` 接口
2. 在 `Engine/Config/Linux/LinuxEngine.ini` 中修改 `DeviceProfileSelectionModule` 指向你的模块名
3. 或者在项目的 `.ini` 配置中覆盖该值

```cpp
// 自定义选择器示例
class FMyLinuxDeviceProfileSelector : public IDeviceProfileSelectorModule
{
public:
    virtual const FString GetRuntimeDeviceProfileName() override
    {
        // 自定义逻辑：根据 GPU 选择不同 profile
        FString GPUName = GRHIAdapterName;
        if (GPUName.Contains(TEXT("NVIDIA")))
        {
            return TEXT("LinuxNVIDIA");
        }
        return FPlatformProperties::PlatformName();
    }

    virtual void StartupModule() override {}
    virtual void ShutdownModule() override {}
};
```

## Demo 示例

本插件太简单，不需要独立示例。但如果你想测试 Device Profile 系统的工作情况：

```bash
# 启动时指定 device profile 覆盖
./MyGame -DeviceProfile=Linux

# 查看日志中的 profile 选择信息
./MyGame -Log | grep "Selected Device Profile"
```

日志输出应为：
```
LogLinux: Selected Device Profile: [Linux]
```

## 模块依赖

从 Build.cs 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块，提供 FString、FPlatformProperties 等 |

私有依赖（本模块内部使用）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础功能 |
| `CoreUObject` | UObject 系统支持 |
| `Engine` | 提供 `IDeviceProfileSelectorModule` 接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-11-09 | `66e9bb39ff7e` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理已废弃的 include 条件编译宏，纯代码清理 |
| 2023-01-13 | `3c9aacb1ad24` | Updated public headers for ~170 engine plugins using IWYU | 批量 IWYU 头文件更新，非功能改动 |
| 2023-01-12 | `2f78497e6753` | Updated private files with IWYU for all plugins | 批量 IWYU 私有文件更新，非功能改动 |

### 维护评价

**核心逻辑自 2015 年创建以来从未修改过。** 2023-2024 年的所有 commit 都是 Epic 进行全仓库级别的 IWYU 清理和废弃宏移除，与本插件的功能无关。

- **创建时间**: 2015 年（随 UE4 Linux 支持一起引入）
- **最近实质性更新**: 2015 年（`FIXME: support different environments` 注释至今未解决）
- **活跃度**: 极低——核心逻辑仅 10 行，无需频繁维护
- **已知限制**: 不支持根据不同 Linux 硬件环境（不同 GPU、CPU 等）选择不同 profile。代码中有 `FIXME` 注释暗示此功能计划但从未实现
- **推荐使用**: 作为基础设施模块，它默认启用且工作正常。但如果你需要更精细的 Linux 设备适配（例如针对不同 GPU 的优化），需要自己实现替代选择器

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LinuxDeviceProfileSelector)
- [接口定义](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Public/IDeviceProfileSelectorModule.h)
- [Linux 引擎配置](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Config/Linux/LinuxEngine.ini)（注册本模块为选择器）
- [LinuxArm64 引擎配置](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Config/LinuxArm64/LinuxArm64Engine.ini)
