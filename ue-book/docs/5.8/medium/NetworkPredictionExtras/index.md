# Network Prediction Extras

> Non essential classes for Network Prediction. Samples, test maps, etc intended to help developers start using the system. Not intended to be used directly in a shipping product.

| 属性 | 值 |
|---|---|
| 中文名 | 网络预测附加内容 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产、测试地图） |
| 模块 | `NetworkPredictionExtras` (Runtime), `NetworkPredictionExtrasLatentLoad` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-27 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPredictionExtras) | |

## 用途

此插件是 **NetworkPrediction** 核心插件的配套示例和辅助资源集合。其主要目的是提供**可运行的实例、测试地图和蓝图资产**，帮助开发者理解、测试和学习 UE 的网络预测（Network Prediction）系统框架。它不是一个可以直接用于正式游戏产品的生产级插件，而是一个教学和原型开发工具箱。

## 使用场景

-   **学习网络预测系统**：当你想要了解 UE 的网络预测（如物理状态同步、客户端预测、服务器校正）工作原理时，可以查阅和运行此插件中的示例。
-   **为项目搭建原型**：在项目初期，需要快速验证某种移动或物理对象的网络同步行为是否可行，可以参考此插件中的实现来搭建原型。
-   **测试与调试**：此插件提供的测试地图和资产可用于对网络预测系统进行压力测试、边界条件测试或复现特定问题。

## 蓝图用法

作为示例插件，其核心价值在于提供完整的、可交互的蓝图示例资产，而非提供可被其他项目直接复用的蓝图节点库。**主要在插件内容的测试地图和蓝图中演示用法**。

### 核心节点（推断）

通常，此类示例插件会暴露一些可配置的组件或 Actor 蓝图类，用于展示预测功能。

| 节点 | 说明 | 所在类 |
|---|---|---|
| （示例）组件属性 | 展示可预测的物理参数或状态变量 | （示例）移动组件或自定义 Actor |

### 使用示例（蓝图描述）

1.  启用插件后，在 **Content Browser** 中找到 `NetworkPredictionExtras` 文件夹。
2.  打开其中的 **测试地图**（如 `TestMap_...`）。
3.  运行游戏或 PIE（Play In Editor），通过蓝图中预设的 UI 或操作，观察不同物体的预测、插值和同步效果。
4.  在测试地图中选中 Actor，查看其蓝图图表，学习 `NetworkPrediction` 系统相关组件和函数的连接方式。

## C++ 用法

此插件主要提供运行时示例代码，学习其源码是了解网络预测系统最佳实践的重要途径。

### 头文件引入

```cpp
#include "NetworkPredictionExtras.h" // 或其他相关头文件，根据具体功能
```

### 基本用法

从插件内的示例 Actor 和组件代码中学习如何集成 `NetworkPrediction` 系统。
（具体代码示例请参考插件源码目录 `Source/NetworkPredictionExtras/` 下的 `.cpp` 和 `.h` 文件）

### 进阶用法

分析插件中 **测试 Actor** 的完整生命周期管理，以及 **物理驱动移动组件** 的预测与校正逻辑实现，是深入理解该系统的有效方法。

## Demo 示例

本插件本身即为一个完整的 Demo。请直接启用插件并加载其提供的 **测试地图** 资产进行体验和学习。

## 模块依赖

要使用此插件的功能（主要是查看和运行其示例），你需要依赖 `NetworkPrediction` 插件。在你的项目 `.uproject` 文件或模块 `.Build.cs` 中，通常无需显式添加依赖，因为它们仅在编辑器和示例地图中使用。

| 模块 | 用途 |
|---|---|
| `NetworkPrediction` | 此插件的核心依赖，提供网络预测系统的框架。 |
| `PhysicsCore` | （可能）用于处理物理相关的预测。 |
| `ChaosPhysics` | （可能）与 Chaos 物理引擎集成，进行状态预测。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正格式化字符串中类型说明符与参数位数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-03-05 | `af6df933` | Fixed various callsites of FString::Printf/Appendf that used scoped enums | 修复了 FString::Printf/Appendf 中作用域枚举的使用错误。 |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 清理被弃用标记的头文件包含语句。 |

### 维护评价

-   **创建时间**：该插件创建于 **2019 年**，已有较长历史。
-   **维护情况**：从最近的提交记录看，**近一年的更新全部是编译器警告修复、代码规范调整和宏迁移**，没有新的功能或示例添加。这表明该插件**已停止积极的功能开发**，当前的维护仅为保证其与最新引擎版本编译兼容。
-   **推荐度**：**对于学习网络预测系统的原理和早期实现方式，此插件仍有参考价值。** 但对于新项目，**不建议直接启用或依赖此插件**，应关注 `NetworkPrediction` 核心模块的最新文档和示例。该插件更适合被视为一个**历史参考和教学资源**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPredictionExtras)
-   [官方文档]( ) （无直接链接）
-   [测试用例] （测试地图资产位于插件 `Content` 目录下）