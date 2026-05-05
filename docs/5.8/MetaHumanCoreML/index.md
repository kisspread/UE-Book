# MetaHuman CoreML

> CoreML models and dependencies for MetaHuman inference on Apple platforms.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（CoreML 模型资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2026-03-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreML) | |

## 用途

该插件是一个**纯内容插件**，其核心作用是将 MetaHuman 推理所需的 CoreML 模型资产从主 MetaHuman 插件中隔离出来，并专门针对 Apple 平台（Mac, iOS, tvOS, VisionOS）进行打包。这解决了跨平台兼容性问题：主 MetaHuman 插件可以在所有平台上运行，而 CoreML 相关的模型资产仅在支持的 Apple 平台上被加载和使用，避免了在 Windows 或 Linux 等平台上加载无用的 Apple 专属资产。

## 使用场景

- 你正在为 **Mac、iPhone、iPad、Apple TV 或 Apple Vision Pro** 开发包含 MetaHuman 角色的应用程序。
- 你需要在这些 Apple 设备上利用 **CoreML** 进行高性能的 MetaHuman 面部动画推理。
- 你的项目启用了主 MetaHuman 插件，并且希望在 Apple 平台上获得完整的推理能力。

## 蓝图用法

由于这是一个纯内容插件，不包含 C++ 模块，因此没有直接的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。其功能通过提供 **CoreML 模型资产** 来实现。

### 核心资产

| 资产类型 | 说明 | 所在位置 |
|---|---|---|
| `CoreML 模型 (.mlmodel)` | 用于 MetaHuman 面部动画推理的机器学习模型。 | `Content/` 目录下 |

### 使用示例（蓝图描述）

1.  确保在项目设置中**启用** `MetaHumanCoreML` 插件。
2.  在内容浏览器中，导航到 `Plugins/MetaHumanCoreML Content/` 目录，可以找到提供的 CoreML 模型资产。
3.  这些模型资产通常由主 MetaHuman 插件的运行时逻辑（如 `MetaHumanRuntime` 模块）在 Apple 平台上自动检测和使用，无需用户在蓝图中直接操作。

## C++ 用法

该插件本身不包含 C++ 代码。其提供的 CoreML 模型资产由其他 MetaHuman 相关模块（如 `MetaHumanRuntime`）在运行时加载和使用。

### 头文件引入

不适用。

### 基本用法

不适用。使用该插件的功能主要通过依赖 `NNERuntimeCoreML` 插件来实现。

### 进阶用法

不适用。

## Demo 示例

由于是纯内容插件，没有独立的代码示例。其使用体现在主 MetaHuman 功能在 Apple 平台上的完整运行。一个最小的验证方式是：

1.  创建一个新项目，启用 `MetaHumanCoreML` 和 `NNERuntimeCoreML` 插件。
2.  在项目中导入或生成一个 MetaHuman 角色。
3.  将项目打包并部署到支持的 Apple 设备（如 Mac 或 iPhone）上运行。
4.  观察 MetaHuman 角色的面部动画是否正常工作，这间接证明了 CoreML 模型已被成功加载和使用。

## 模块依赖

该插件本身没有模块依赖。但它通过 `.uplugin` 文件声明了对另一个插件的依赖：

| 插件 | 用途 |
|---|---|
| `NNERuntimeCoreML` | 提供在 Apple 平台上运行 CoreML 模型的神经网络引擎运行时支持。这是本插件资产能够被实际执行的基础。 |

## 维护状态

### 近期更新

- 2026-04-02 c906dc4d [MHA] Create MetaHumanCoreML plugin - isolate CoreML model assets to Apple platforms
- 2026-03-30 509808ac Revert 52246754: MetaHumanCoreML plugin addition
- 2026-03-30 0ff6ecf5 [MHA] Create MetaHumanCoreML plugin - isolate CoreML model assets to Apple platforms

### 维护评价

- **创建时间**：非常新（2026年3月）。
- **近期更新**：最近一次提交在几天前，表明该插件刚刚被创建并集成到引擎中。
- **维护状态**：**活跃维护中**。作为 MetaHuman 跨平台战略的一部分，预计会持续更新以支持新的 Apple 设备和 CoreML 版本。
- **已知限制**：
    - 仅适用于 Apple 平台。
    - 默认禁用，需要手动启用。
    - 功能实现依赖于 `NNERuntimeCoreML` 插件。
- **推荐使用**：如果你的项目目标平台包含 Apple 设备，并且需要使用 MetaHuman 的完整推理功能，**强烈推荐**启用此插件。对于非 Apple 平台的项目，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreML)
- [官方文档]()
- [测试用例]()