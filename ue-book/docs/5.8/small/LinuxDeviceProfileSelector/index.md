# Linux Device Profile Selector

> Linux Device Profile Selector

| 属性 | 值 |
|---|---|
| 中文名 | Linux 设备配置选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LinuxDeviceProfileSelector` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2015-09-24 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LinuxDeviceProfileSelector) | |

## 用途

Linux Device Profile Selector 是一个**自动运行**的设备配置选择器，用于在 Linux 平台上根据当前硬件和驱动状况自动选择合适的 Device Profile。

它解决的核心问题是：Linux 硬件和驱动组合多样（NVIDIA、AMD、Intel 集显、不同 Mesa 版本等），引擎需要一种机制在运行时检测当前环境并自动应用合适的画质/性能配置。类似于 Android 上根据芯片型号自动选择设备配置，这个插件为 Linux 提供了同等能力。

典型场景包括：检测到旧版或有缺陷的驱动时自动降低画质设置，或根据 GPU 厂商/型号选择优化的渲染配置。

## 使用场景

- 你在开发 Linux 客户端（如 Steam Deck、Linux 桌面游戏），需要根据硬件自动调整画质 → 此插件自动生效
- 你需要为不同 Linux GPU 驱动版本配置不同的默认设置 → 配合 Device Profile 系统使用
- 你在做 XR/VR 项目且目标平台包含 Linux → 近期更新已增加 XR 设备配置选择支持

## 蓝图用法

该插件**无蓝图接口**。它完全在引擎启动阶段自动工作，通过注册为 `IDeviceProfileSelectorModule` 实现，在 `PostConfigInit` 加载阶段自动选择设备配置。用户无需手动调用任何节点。

## C++ 用法

该插件是纯自动运行模块，不暴露任何公共 API 给用户代码。其内部实现基于 `IDeviceProfileSelectorModule` 接口。

### 工作原理

```cpp
// 插件核心接口（内部实现，用户无需直接调用）
class FLinuxDeviceProfileSelectorModule : public IDeviceProfileSelectorModule
{
    // 引擎在启动时自动调用此函数获取设备配置名称
    virtual const FString GetRuntimeDeviceProfileName() override;
    
    // 模块生命周期
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

插件在 `PostConfigInit` 加载阶段注册自己，引擎随后调用 `GetRuntimeDeviceProfileName()` 获取适用于当前 Linux 环境的 Device Profile 名称。

## Demo 示例

该插件无用户可调用的代码。所有功能在引擎启动时自动执行。如需自定义 Linux 设备配置选择逻辑，可参考此插件的实现模式创建自己的 `IDeviceProfileSelectorModule`。

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。插件仅依赖 `IDeviceProfileSelectorModule` 接口所在的引擎核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，代码维护性更新 |
| 2026-03-25 | `a14ea175` | OpenXR SteamFrame and Android support improvements | OpenXR 和平台支持改进 |
| 2026-02-26 | `abd943b8` | PR #13368: Adding support for XR device profile selection on Linux | 新增 Linux 上 XR 设备配置选择支持 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理废弃的预处理宏 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件批量更新 |

### 维护评价

- **状态**：活跃维护中
- **分析**：虽然插件创建于 2015 年已超过 10 年，但 2026 年仍有实质性功能更新（XR 设备配置支持），说明该插件仍在活跃使用和维护
- **代码规模**：极小（仅 3 个文件），维护成本低
- **平台限制**：仅在 Linux 和 LinuxArm64 平台加载，不影响其他平台
- **推荐度**：✅ 如果你的项目需要在 Linux 上发布，该插件默认启用无需额外配置；如需自定义 Linux 设备配置选择逻辑，可参考其实现

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LinuxDeviceProfileSelector)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)（插件自身无专属测试）