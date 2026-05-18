# USDPregen

> Library to assist with pre-generating USD-based content.

| 属性 | 值 |
|---|---|
| 中文名 | USD内容预生成库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UsdPregenCore` (Runtime), `USDPregenHttpWorker` (Runtime), `USDPregenInterchange` (Runtime), `USDPregenInterchangeEditor` (Runtime), `USDPregenPy` (Runtime), `USDPregenUObjectStorage` (Runtime), `USDPregenWrapper` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen) | |

## 用途

USDPregen 是一个用于在运行时之前“预生成”基于 USD 的资产内容的库。其核心目的是通过离线或管线化的处理，将复杂的 USD 资产预先转换、优化或缓存为更易于引擎实时加载和使用的格式，从而显著提升大型项目的加载性能和运行时稳定性。它解决的是大规模 USD 资产生产流水线中的性能瓶颈问题。

## 使用场景

-   你在开发一个拥有海量 USD 资产的大型开放世界或虚拟制片项目，需要优化资产加载时间和运行时内存占用。
-   你的美术团队需要定期从 DCC 工具（如 Maya, Houdini）导出 USD 场景，你希望在 CI/CD 管线中自动对这些资产进行预处理和优化。
-   你需要使用 Python 脚本大规模批量处理 USD 文件，以执行自定义的资产清理、LOD 生成或材质烘焙逻辑。
-   你希望将预生成的结果通过 Unreal 的 Interchange 框架，灵活、模块化地导入引擎。

## 模块列表

| 模块名 | 类型 | 一句话总结 |
|---|---|---|
| [`UsdPregenCore`](UsdPregenCore.md) | Runtime | 核心库，定义了预生成任务、资产定义、序列化等基础数据结构和流程。 |
| [`USDPregenHttpWorker`](USDPregenHttpWorker.md) | Runtime | 负责与远程服务器通信，用于任务调度、状态汇报和分布式预生成。 |
| [`USDPregenInterchange`](USDPregenInterchange.md) | Runtime | 提供将预生成资产通过 Interchange 框架导入 UE 的基础能力。 |
| [`USDPregenInterchangeEditor`](USDPregenInterchangeEditor.md) | Runtime | 扩展 Interchange 导入流程，提供编辑器专用的资产处理节点和选项。 |
| [`USDPregenPy`](USDPregenPy.md) | Runtime | 提供 Python 绑定，允许使用 Python 脚本驱动整个预生成流程。 |
| [`USDPregenUObjectStorage`](USDPregenUObjectStorage.md) | Runtime | 管理预生成过程中产生的 UObject 资产（如纹理、材质）的存储与序列化。 |
| [`USDPregenWrapper`](USDPregenWrapper.md) | Runtime | 提供面向用户的高级封装接口，简化常见预生成操作的调用。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen)