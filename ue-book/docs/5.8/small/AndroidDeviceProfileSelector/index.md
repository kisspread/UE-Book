# Android Device Profile Selector

> Android Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 中文名 | Android 设备配置选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidDeviceProfileSelector` (Editor), `AndroidDeviceProfileCommandlets` (Editor), `AndroidDeviceProfileSelectorRuntime` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector) | |

## 用途

这个插件用于在 Android 设备上自动识别硬件规格并选择最适合的设备配置文件（Device Profile）。Android 设备种类繁多，不同设备的 GPU、内存、CPU 能力差异巨大，此插件通过读取设备硬件信息（GPU 型号、厂商等），自动匹配并应用预设的设备配置文件，从而为不同 Android 设备提供最优的画质和性能设置。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`AndroidDeviceProfileSelector`](AndroidDeviceProfileSelector.md) | Editor | 核心编辑器模块，负责设备检测逻辑和配置文件匹配算法 |
| [`AndroidDeviceProfileCommandlets`](AndroidDeviceProfileCommandlets.md) | Editor | 提供命令行工具，用于批量生成或验证 Android 设备配置数据 |
| [`AndroidDeviceProfileSelectorRuntime`](AndroidDeviceProfileSelectorRuntime.md) | Runtime | 运行时模块，在 Android 设备启动时自动执行设备检测和配置选择 |

## 使用场景

- 你的游戏需要支持大量不同规格的 Android 设备 → 使用此插件自动根据硬件选择最佳画质配置
- 你需要为高端/中端/低端 Android 设备分别设置不同的渲染质量 → 配置设备配置文件规则，由插件自动匹配
- 你需要批量测试设备配置匹配结果 → 使用 Commandlet 模块在命令行验证配置正确性

## 蓝图用法

此插件主要在引擎启动时自动工作，无显著的蓝图可调用接口。设备配置选择在 `PostConfigInit` 阶段自动执行，开发者主要通过配置 `.ini` 文件中的 Device Profile 规则来定制行为。

## C++ 用法

此插件为引擎基础设施组件，通常无需在游戏代码中直接调用。如需扩展设备检测逻辑，参见各子模块文档中的详细 API。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AndroidDeviceDetection` | Android 硬件信息检测，获取 GPU 型号、厂商等设备参数 |
| `PIEPreviewDeviceSpecification` | PIE 预览设备规格定义，用于编辑器中模拟不同 Android 设备 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移至 UE_LOGF 新格式 |
| 2026-03-02 | `f2f207d7` | [AndroidDeviceProfileSelectorRuntime] | 运行时模块更新 |
| 2026-03-01 | `1d115ca4` | Changed codegen to only create one Z_Construct_<Type> function but with a bool as inparam to decide | 代码生成重构，合并构造函数 |
| 2026-02-18 | `f5a10b68` | Add Preview json Versioning | 添加预览 JSON 版本控制 |
| 2026-02-13 | `bbbd7847` | Add ConfigRules to Android Preview Json | 为 Android 预览 JSON 添加配置规则 |

### 维护评价

**活跃维护** — 虽然插件创建于 2014 年已有 12 年历史，但近期（2026 年）仍有持续的功能更新和代码优化，包括预览 JSON 版本控制、配置规则扩展等实质性改进。作为 Android 平台设备适配的基础设施，随着新设备不断涌现，该插件持续演进。**推荐使用**，这是 Android 平台开发的必备插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector/Tests)（如有）