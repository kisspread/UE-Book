# Chaos Outfit Asset

> Outfit Asset plugin to create and assemble outfits made of Cloth Assets.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流节点） |
| 模块 | `ChaosOutfitAssetDataflowNodes` (Runtime), `ChaosOutfitAssetEditor` (Runtime), `ChaosOutfitAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosOutfitAsset) | |

## 用途

本插件提供了一套完整的工具链，用于在 Unreal Engine 中创建、编辑和管理基于 Chaos 物理系统的服装资产（Outfit Asset）。它解决了将多个独立的布料资产（Cloth Assets）组装成一个完整的、可物理模拟的服装套装的问题。插件通过数据流（Dataflow）节点定义服装部件，通过专用编辑器进行资产创建和组装，并通过运行时引擎驱动服装的物理模拟。

## 使用场景

- 你需要为角色创建复杂的、由多个布料部件（如上衣、裤子、裙子）组成的服装系统，并希望它们能作为一个整体进行物理模拟。
- 你正在开发一个角色换装系统，需要高效地管理和组装不同的服装部件。
- 你希望利用数据流（Dataflow）工具来程序化地定义或修改服装资产的构成。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `ChaosOutfitAssetDataflowNodes` | Runtime | 提供用于定义服装部件和组装逻辑的数据流节点。 |
| `ChaosOutfitAssetEditor` | Runtime | 提供用于创建、编辑和预览服装资产的编辑器工具和资产类型。 |
| `ChaosOutfitAssetEngine` | Runtime | 包含服装资产的核心运行时逻辑，驱动物理模拟和组件管理。 |

## 蓝图用法

本插件主要通过数据流节点和编辑器资产进行工作，其核心功能通常封装在编辑器工具和运行时组件中。具体的蓝图可用 API（如 `UFUNCTION(BlueprintCallable)`）需要查阅各子模块的详细文档。

### 核心节点（数据流）

| 节点 | 说明 | 所在模块 |
|---|---|---|
| （待查阅） | 用于定义服装部件和组装关系的数据流节点。 | `ChaosOutfitAssetDataflowNodes` |

*详细的蓝图节点和资产用法，请参阅各子模块文档。*

## C++ 用法

本插件的 C++ 用法主要涉及服装资产的创建、加载和运行时组件的交互。由于插件处于实验阶段，API 可能发生变化。

### 头文件引入

```cpp
// 引入服装资产引擎模块
#include "ChaosOutfitAssetEngineModule.h"
```

### 基本用法

*具体的 C++ API 示例（如创建 `UChaosOutfitAsset` 或操作 `UChaosOutfitComponent`）需要参考 `ChaosOutfitAssetEngine` 模块的文档和测试用例。*

## Demo 示例

*由于插件为实验性且版本较新，一个完整的、可编译的最小示例需要参考各子模块文档中的测试用例或官方示例项目。*

## 模块依赖

要使用本插件，你的项目模块通常需要依赖以下模块（具体取决于你使用的功能）：

| 模块 | 用途 |
|---|---|
| `ChaosOutfitAssetEngine` | 访问服装资产的核心运行时类和组件。 |
| `ChaosOutfitAssetEditor` | （仅编辑器）访问服装资产的编辑器工具和资产工厂。 |
| `Chaos` | Chaos 物理系统核心模块。 |
| `Cloth` | 布料模拟系统模块。 |

*更详细的依赖关系，请查阅各子模块的 `.Build.cs` 文件。*

## 维护状态

### 近期更新

*（由于插件创建时间为未来日期（2026-04-22），此信息可能为测试数据。基于当前信息，暂无可用的 git log 记录。）*

### 维护评价

- **创建时间**：标记为 2026 年，可能为测试或占位数据。
- **版本状态**：`VersionName` 为 “0.1”，且 `IsBetaVersion` 为 `true`，表明这是一个处于早期开发阶段的实验性插件。
- **启用状态**：`EnabledByDefault` 为 `false`，需要用户手动启用。
- **综合评价**：这是一个全新的、实验性的插件，旨在为 Chaos 物理系统提供服装资产工作流。由于其处于 Beta 阶段，API 和功能可能不稳定，不建议在生产项目中直接使用，但适合用于技术预研和原型开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosOutfitAsset)
- [官方文档]() （暂无）
- [测试用例]() （暂无，或位于各子模块内）