# HoldoutComposite

> Deprecated plugin now redirected to CompositeCore

| 属性 | 值 |
|---|---|
| 中文名 | 遮罩合成（已废弃） |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/HoldoutComposite) | |

## 用途

这是一个**已废弃的空壳插件**，自身不包含任何源码或模块。它的唯一作用是作为旧插件名 `HoldoutComposite` 的兼容性重定向，自动启用 `CompositeCore` 插件。

在 UE 的合成管线重构过程中，原有的 HoldoutComposite 功能被整合进了 CompositeCore 插件。此插件保留是为了：
- 让引用了 `HoldoutComposite` 的旧项目不会因为找不到插件而报错
- 通过插件依赖声明自动拉起 `CompositeCore`

**⚠️ 你不需要使用此插件。** 如果你需要 Holdout（遮罩）合成能力，请直接使用 [CompositeCore](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/CompositeCore) 插件。

## 使用场景

- **不适用。** 这是一个废弃的兼容性重定向，没有独立使用场景。
- 如果你的旧项目 `.uproject` 中引用了 `HoldoutComposite`，它会自动启用 `CompositeCore`，无需手动修改。

## 蓝图用法

无。此插件不包含任何蓝图节点或资产。

## C++ 用法

无。此插件不包含任何 C++ 代码或头文件。

## Demo 示例

不适用。此插件无内容可演示。

## 模块依赖

无特殊依赖。此插件自身无模块，仅通过插件依赖声明启用 `CompositeCore`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-17 | `2ffd7304` | Composure: Move new Composure (Composite) plugin and Composite Core in the Compositing engine plugin folder. | 将合成相关插件移入 Compositing 目录，创建此废弃重定向插件 |

### 维护评价

- **状态：已废弃，不会有任何后续更新**
- 此插件于 2025 年 9 月创建时即标记为废弃（`Hidden=true`，`Installed=false`），仅保留一个 commit
- 它是 Composure/合成管线重构过程中的产物，目的仅为保持旧项目的向后兼容
- **不推荐使用。** 请直接使用 CompositeCore 插件获取 Holdout 合成功能

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/HoldoutComposite)
- [CompositeCore 插件（实际替代）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/CompositeCore)