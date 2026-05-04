# Composure Shared

> Shared content assets (materials, textures, meshes) migrated from legacy Composure, accessible to both Composure and Composite plugins.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、纹理、网格体等合成资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2026-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/ComposureShared) | |

## 用途

ComposureShared 是一个**纯内容插件**，不包含任何 C++ 代码或蓝图逻辑。它存在的目的是将旧版 Composure 插件中的通用共享资产（材质、纹理、网格体等）抽取到一个独立插件中，供 **Composure** 和 **Composite** 两个合成插件共同引用。

这种拆分解决了以下问题：

- **避免资产重复**：旧版 Composure 将所有资产打包在一起，当新的 Composite 插件也需要这些通用资产时，会导致重复或依赖混乱
- **解耦依赖**：Composure 和 Composite 可以各自独立演进，同时共享同一套基础资产
- **清晰的模块边界**：通用资产有了独立的归属，不再与特定插件的逻辑代码混杂

## 使用场景

- 你正在使用 **Composure** 插件进行实时合成 → 该插件自动提供所需的共享材质和纹理
- 你正在使用新的 **Composite** 插件 → 同样依赖此插件提供的共享资产
- 你需要自定义合成材质 → 可以从此插件中找到基础材质作为参考或父材质

## 蓝图用法

本插件为纯内容插件，不包含任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。

使用方式为直接在蓝图或材质编辑器中引用本插件提供的材质、纹理等资产。

## C++ 用法

本插件无 C++ 模块，无需引入头文件或链接任何库。

如需在 C++ 中引用本插件的资产路径，使用标准的资产路径引用方式即可：

```cpp
// 引用 ComposureShared 中的材质资产
static ConstructorHelpers::FObjectFinder<UMaterialInterface> MaterialFinder(
    TEXT("/ComposureShared/Materials/YourMaterialName")
);
```

## Demo 示例

不适用。本插件为纯内容插件，无代码示例。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

本插件无任何代码模块，不产生模块依赖。其他插件（如 Composure、Composite）通过资产引用方式使用本插件的内容。

## 维护状态

### 近期更新

```
- 2026-04-08 e2f9d530 Composure: Add ComposureShared plugin and migrate generic assets from legacy Composure to be shared
```

### 维护评价

- **创建时间**：2026-04-08，极新的插件
- **更新频率**：仅有 1 次提交，为初始创建和资产迁移
- **维护状态**：🆕 刚刚创建，尚无后续维护记录
- **已知限制**：`EnabledByDefault=false`，需要手动在插件管理器中启用
- **推荐程度**：如果你使用 Composure 或 Composite 插件，此插件为必需依赖，应按需启用。作为纯内容插件，维护需求极低，风险较小。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/ComposureShared)
- [Composure 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure)
- [Composite 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composite)