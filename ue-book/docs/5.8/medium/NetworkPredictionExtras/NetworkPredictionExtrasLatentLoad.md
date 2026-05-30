# Network Prediction Extras

> Non essential classes for Network Prediction. Samples, test maps, etc intended to help developers start using the system. Not intended to be used directly in a shipping product.

| 属性 | 值 |
|---|---|
| 中文名 | 网络预测扩展 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例地图、测试资源、辅助类） |
| 模块 | `NetworkPredictionExtras` (Runtime), `NetworkPredictionExtrasLatentLoad` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-27 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPredictionExtras) | |

## 用途

NetworkPredictionExtras 是 Epic 为 **NetworkPrediction** 核心插件提供的配套示例与辅助插件。它本身不包含可直接用于正式项目的功能模块，而是作为开发者学习和理解 NetworkPrediction 网络预测系统的**入门参考**。

该插件解决的问题：NetworkPrediction 核心系统概念抽象、学习曲线陡峭，开发者难以直接上手。本插件通过提供可运行的示例蓝图资产、测试地图、以及一些非核心的辅助 C++ 类（如延迟加载存根），帮助开发者快速理解网络预测的工作流。

**注意**：此插件明确标注"Not intended to be used directly in a shipping product"，不应作为正式项目的运行时依赖。

## 使用场景

- 你刚开始学习 UE5 的 NetworkPrediction 系统 → 启用本插件，参考其中的示例地图和蓝图
- 你需要理解网络预测的状态同步/回滚机制如何在实际场景中工作 → 打开测试地图进行研究
- 你正在为自己的项目实现网络预测功能 → 参考本插件中的辅助类和示例模式

## 蓝图用法

本插件的核心价值在于**示例资产和测试地图**（CanContainContent=true），而非运行时 API。启用插件后可在 Content Browser 中找到相关资产进行学习。

由于本插件的 C++ 源码极为精简（主要模块以蓝图资产为主），`BlueprintCallable` 节点较少。以下是从源码中提取的可用辅助类：

### 核心类

| 类 | 说明 | 所在模块 |
|---|---|---|
| `UNetworkPredictionExtrasLatentLoadStubObject` | 延迟加载存根对象，用于支持按需加载 | `NetworkPredictionExtrasLatentLoad` |

### 使用示例

1. 启用插件：在 Plugins 面板搜索 "Network Prediction Extras" 并启用
2. 打开示例地图：在 Content Browser 中浏览插件内容目录
3. 运行测试地图，观察网络预测的行为表现
4. 参考蓝图实现，理解状态定义和预测流程

## C++ 用法

本插件的 C++ 层非常薄，核心价值在内容资产。以下是可用的代码接口：

### 头文件引入

```cpp
#include "NetworkPredictionExtrasLatentLoadModule.h"
```

### 基本用法

`NetworkPredictionExtrasLatentLoad` 模块提供一个存根 UObject 类，用于延迟加载场景：

```cpp
// 存根类定义（简化示意）
// UNetworkPredictionExtrasLatentLoadStubObject 继承自 UObject
// 用于在延迟加载场景中作为占位符或触发器
UCLASS()
class UNetworkPredictionExtrasLatentLoadStubObject : public UObject
{
    GENERATED_BODY()
    UNetworkPredictionExtrasLatentLoadStubObject() { }
};
```

> **注意**：此模块的 LoadingPhase 为 `None`，意味着它不会随引擎自动加载，需要显式引用才会被编译链接。

## Demo 示例

本插件本身就是 NetworkPrediction 的 Demo 集合。建议的工作流程：

1. 启用 `NetworkPrediction` 和 `NetworkPredictionExtras` 插件
2. 在 Content Browser 中导航至 NetworkPredictionExtras 插件内容目录
3. 打开示例关卡地图
4. 使用编辑器 PIE（Play In Editor）运行，观察预测和回滚行为
5. 切换 NetMode 为 "Standalone" 与 "Listen Server" 对比行为差异

## 模块依赖

本插件显式依赖 `NetworkPrediction` 核心插件（在 .uplugin 的 Plugins 字段中声明）。

| 模块 | 用途 |
|---|---|
| `NetworkPrediction` | 核心网络预测系统，本插件的示例均围绕此系统构建 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 printf 格式说明符与参数位宽不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF 新宏 |
| 2026-03-05 | `af6df933` | Fixed various callsites of FString::Printf/Appendf that used scoped enums | 修复 FString::Printf 中使用作用域枚举的调用 |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 移除已废弃的头文件包含保护 |

### 维护评价

⚠️ **该插件已超过 1 年没有功能性更新。**

从 git 历史来看，最近的所有提交（2026 年）均为**编译器警告修复和代码风格统一**，没有任何功能性改动。结合以下信息：

- 创建于 2019 年，已有约 7 年历史
- 标记为 Beta 版本（IsBetaVersion=true）
- 默认未启用（EnabledByDefault=false）
- 描述明确声明"not intended to be used directly in a shipping product"
- 最近几年的更新全部是编译器兼容性/代码清理性质

**结论**：本插件处于**维护不活跃**状态，作为学习参考仍有价值，但不建议在正式项目中依赖。NetworkPrediction 核心系统的实际演进可能已超出此示例插件的覆盖范围。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPredictionExtras)
- [核心依赖：NetworkPrediction 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPrediction)