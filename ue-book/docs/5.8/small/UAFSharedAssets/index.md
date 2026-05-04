# UAF Shared Assets

> UAF Default Assets that interact with multiple plugins

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UAF默认资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFSharedAssets) | |

## 用途

UAFSharedAssets 是 Unreal Animation Framework (UAF) 生态系统中的一个**纯内容插件**。它不包含任何代码模块，其核心作用是为 UAF 框架下的其他插件（如 `UAFEditor`、`UAFGameplay` 等）提供**共享的默认资产**。

这个插件的存在是为了解决资产复用和一致性问题。当多个 UAF 相关插件都需要使用同一套基础动画蓝图、动画蒙太奇或数据资产时，将这些资产集中存放在 `UAFSharedAssets` 中，可以避免重复，确保所有插件引用的是同一份权威资源，并简化资产管理和更新流程。

## 使用场景

-   **UAF 框架开发**：当你正在开发或扩展 UAF 框架本身，并需要为多个子插件提供一套标准的、可复用的动画资产（例如默认的角色动画蓝图、标准的动画通知类）时。
-   **快速原型开发**：在基于 UAF 框架进行游戏原型开发时，可以直接使用此插件提供的默认资产，快速搭建动画系统，而无需从头创建所有基础资源。
-   **资产一致性维护**：确保项目中所有依赖 UAF 的模块都使用相同版本的默认动画资产，避免因资产版本不一致导致的动画表现差异或错误。

## 蓝图用法

此插件为纯内容插件，不包含任何可调用的蓝图节点或函数。其价值在于提供的资产（如 `AnimationBlueprint`、`AnimMontage`、`DataAsset` 等）。

### 核心资产

| 资产类型 | 说明 | 典型用途 |
|---|---|---|
| `Animation Blueprint` | UAF 框架默认的动画蓝图 | 作为角色动画状态机的模板或基础 |
| `Anim Montage` | 预设的动画蒙太奇 | 提供标准的攻击、受击、交互等动画片段 |
| `Data Asset` | 配置数据资产 | 存储默认的动画参数、状态配置等 |

### 使用示例（资产引用）

在蓝图中，你无法直接“调用”此插件，但可以引用它提供的资产：
1.  在内容浏览器中，导航至 `Plugins/UAFSharedAssets Content/` 目录。
2.  找到你需要的资产（例如 `ABP_DefaultCharacter`）。
3.  在另一个蓝图（如你的角色蓝图）的动画图表中，将 `Anim Blueprint` 节点的类设置为 `ABP_DefaultCharacter`。
4.  或者，在 `Anim Instance` 组件中直接指定该动画蓝图类。

## C++ 用法

此插件为纯内容插件，不提供任何 C++ API。在 C++ 中，你可以通过路径引用其提供的资产。

### 头文件引入

无需引入特定头文件，但需要知道资产路径。

### 基本用法

在 C++ 中加载此插件提供的资产：
```cpp
// 加载一个动画蓝图资产
UAnimBlueprint* DefaultAnimBP = LoadObject<UAnimBlueprint>(
    nullptr,
    TEXT("/UAFSharedAssets/Characters/ABP_DefaultCharacter")
);

// 加载一个数据资产
UMyDataAsset* DefaultData = LoadObject<UMyDataAsset>(
    nullptr,
    TEXT("/UAFSharedAssets/Data/DA_DefaultConfig")
);
```

### 进阶用法

在构造函数或初始化函数中预加载资产，避免运行时卡顿：
```cpp
// 在头文件中声明
UPROPERTY()
TObjectPtr<UAnimBlueprint> CachedDefaultAnimBP;

// 在 BeginPlay 或构造函数中
if (!CachedDefaultAnimBP)
{
    CachedDefaultAnimBP = LoadObject<UAnimBlueprint>(
        this,
        TEXT("/UAFSharedAssets/Characters/ABP_DefaultCharacter")
    );
}
```

## Demo 示例

由于是纯内容插件，没有可编译的代码示例。一个典型的使用流程是：
1.  启用 `UAFSharedAssets` 插件。
2.  在你的项目中创建一个新的动画蓝图，父类选择 `UAFSharedAssets` 提供的 `ABP_DefaultCharacter`。
3.  在你的角色蓝图中，将 `Mesh` 组件的 `Anim Class` 设置为这个新创建的动画蓝图。
4.  运行游戏，角色将使用 UAF 框架的默认动画逻辑。

## 模块依赖

此插件本身没有代码模块，但它依赖其他插件才能正常工作。

| 插件 | 用途 |
|---|---|
| `Workspace` | UAF 框架的基础工作区插件，提供核心动画编辑功能和资产类型定义。`UAFSharedAssets` 中的资产很可能依赖于 `Workspace` 插件定义的类和接口。 |

## 维护状态

### 近期更新

-   `5078d880` 2026-04-13 — Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in separate plugins. (添加 UAFSharedAssets 插件，用于提供我们希望提供的、引用了在其他插件中定义的 UAF 资产的内容。)

### 维护评价

-   **创建时间**：该插件于 2026 年 4 月 13 日创建，是一个非常新的插件。
-   **更新频率**：目前仅有一次初始提交，尚无后续更新记录。
-   **维护状态**：**新创建**。作为 UAF 框架的一部分，其维护状态将跟随整个 UAF 框架的开发进度。
-   **已知限制**：作为实验性插件 (`IsExperimentalVersion: true`)，其 API 和资产结构可能在未来版本中发生重大变化。
-   **推荐使用**：如果你正在深度使用或开发 UAF 框架，此插件是获取标准默认资产的推荐方式。对于普通项目，除非明确需要 UAF 的默认资产，否则无需启用。鉴于其“实验性”标签，在生产环境中使用需谨慎，并做好应对未来变更的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFSharedAssets)