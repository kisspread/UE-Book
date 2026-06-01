# IOS Device Profile Selector

> IOS Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 中文名 | iOS设备配置文件选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `IOSDeviceProfileSelector` (RuntimeNoCommandlet), `IOSPreviewDeviceProfileSelector` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSDeviceProfileSelector) | |

## 用途

该插件的核心功能是根据 iOS、tvOS 和 VisionOS 设备的具体硬件型号，在应用启动时自动加载并应用对应的设备配置文件 (Device Profile)。它解决的核心问题是：不同苹果设备（如不同型号的 iPhone、iPad、Apple TV 和 Vision Pro）拥有差异化的图形处理能力、内存和分辨率。通过该插件，引擎能够识别运行设备，并自动应用由开发者预设的、针对该设备优化的配置（如画质等级、分辨率缩放、特效开关等），从而在保证最佳性能的同时，为玩家提供最合适的视觉体验。它是引擎针对 Apple 生态进行性能适配和优化的关键组件。

## 使用场景

- 你正在为 iOS、tvOS 或 VisionOS 平台开发游戏或应用。
- 你需要针对不同型号的 iPhone/iPad/Apple TV/Vision Pro 设置差异化的图形和性能预设。
- 你希望游戏在启动时能自动检测设备型号，并应用最匹配的配置，无需用户手动调整。
- 你正在开发一个对性能敏感的移动应用，需要精细化的设备适配策略。

## 蓝图用法

该插件主要在引擎启动时执行设备检测和配置文件加载逻辑，其功能主要由引擎内部调用，不直接暴露丰富的蓝图节点。通常，开发者通过在配置文件（如 `DefaultDeviceProfiles.ini`）中定义不同设备的配置规则来使用此插件，而不是在蓝图中直接调用其函数。

## C++ 用法

此插件的模块主要是设备配置文件选择逻辑的实现，其API主要被引擎的其他子系统（如平台抽象层、设备配置管理器）内部调用。在游戏或应用的 C++ 代码中，开发者通常不直接实例化或调用该插件中的类。其价值体现在配置层面。

### 基本用法

该插件的使用主要是通过配置而非代码。你需要在项目的配置目录下创建或编辑设备配置文件。

```ini
; 配置文件示例: Config/DefaultDeviceProfiles.ini
[DeviceProfile IOS_IPadPro_M4 DeviceProfile]
DeviceType=IOS
BaseProfileName=IOS
+CVars=r.MobileContentScaleFactor=2.0
+CVars=r.BloomQuality=4

[DeviceProfileSelector IOS_IPadPro_M4]
+DeviceProfileMappings=(MatchSpec="iPad13,18", ProfileName="IOS_IPadPro_M4")
```
*此示例展示了如何为特定的 iPad Pro (M4) 型号定义并映射一个专用的设备配置文件。*

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

| 模块 | 用途 |
|---|---|
| `IOSTargetPlatformControls` | (IOSPreviewDeviceProfileSelector 模块依赖) 用于在编辑器中提供 iOS 预览平台的控制接口，模拟不同设备配置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-02-24 | `6fa9a99f` | Add Aspect Ratio to IOS Preview Json | 为 iOS 预览功能添加了屏幕宽高比参数。 |
| 2026-02-18 | `f5a10b68` | Add Preview json Versioning | 为预览配置的 JSON 格式添加了版本控制。 |
| 2026-02-13 | `bbbd7847` | Add ConfigRules to Android Preview Json | 将 ConfigRules 功能也添加到了 Android 预览的 JSON 中。 |
| 2026-02-11 | `87fe38ca` | Fix RTTI Linux | 修复了在 Linux 平台上的运行时类型信息相关问题。 |

### 维护评价

该插件作为引擎的核心平台适配组件，创建于 2014 年，历史悠久。从近期提交记录来看，它在 2026 年仍有**频繁且实质性的更新**，例如添加新设备参数支持、改进配置格式和修复平台兼容性问题，表明它处于**活跃维护**状态。其功能对于 iOS/tvOS/VisionOS 平台的游戏发布至关重要。**推荐使用**，尤其当你面向苹果移动设备开发时。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSDeviceProfileSelector)