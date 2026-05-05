# HoldoutComposite

> Deprecated plugin now redirected to CompositeCore

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | （无） |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/HoldoutComposite) | |

## 用途

**此插件已废弃**。HoldoutComposite 是一个空壳插件（shim），其唯一作用是将依赖它的项目自动重定向到 [CompositeCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/CompositeCore) 插件。

Holdout Composite（遮挡合成）是一种视觉特效技术：在场景中标记某些物体为"holdout"——它们不渲染自身颜色，但在深度缓冲中占据空间，从而遮挡其后方的物体。这使得实拍素材可以与 CG 元素无缝合成，常见于虚拟制片（Virtual Production）和影视后期流程。

在 5.6 中，Epic 将原本分散的合成功能整合到了 CompositeCore 插件中，HoldoutComposite 保留为兼容性重定向。

## 使用场景

- **你正在迁移旧项目**：如果项目之前启用了 HoldoutComposite，升级到 5.6 后此插件会自动加载并确保 CompositeCore 可用，无需手动修改。
- **新项目**：**不要使用此插件**，请直接启用 `CompositeCore`。

## 蓝图用法

此插件没有任何模块或蓝图节点。如需 Holdout Composite 功能，请使用 CompositeCore 插件提供的节点。

## C++ 用法

此插件无任何 C++ 模块。如需编程接口，请引用 CompositeCore。

### 头文件引入

不适用——此插件无源文件。

## Demo 示例

不适用。最小示例应基于 CompositeCore 构建。

## 模块依赖

此插件本身无模块，但声明了对以下插件的依赖：

| 插件 | 用途 |
|---|---|
| `CompositeCore` | 实际提供合成功能的插件 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-23 | `c9abe926b8f7` | 将 Composure 和 CompositeCore 移至 Compositing 文件夹，HoldoutComposite 作为废弃重定向保留 |

仅此一次 commit，是组织结构调整的一部分。

### 维护评价

- **状态：已废弃（Deprecated）**
- 此插件是纯粹的兼容性重定向，.uplugin 中 `Hidden: true`、`EnabledByDefault: false`
- 不会再有功能更新
- **不推荐新项目使用**——请直接启用 `CompositeCore`
- 如果你的项目依赖此插件，建议在升级时将依赖迁移到 CompositeCore，然后移除此插件引用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/HoldoutComposite)
- [CompositeCore（实际功能插件）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/CompositeCore)
