# Interchange OpenUSD

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | USD交换导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | unknown |
| 年龄标签 |  |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

## 用途

本插件为 Unreal Engine 的 **Interchange 框架** 提供了处理 **OpenUSD (Universal Scene Description)** 格式文件的能力。它专门解决在 Interchange 管线内导入和转换 USD 数据的问题，使得开发者可以使用统一的流程导入 USD 格式的场景、模型、材质等资产到 UE 内部。

## 使用场景

- **团队资产交换**：当您的美术或技术美术团队使用 Houdini、Maya (通过 USD) 或其他支持 USD 导出的 DCC 工具创建资产，并希望以标准化的方式导入 UE 时。
- **程序化内容生成 (PCG)**：在运行时或编辑器中，需要动态加载和转换 USD 格式的资产数据。
- **复杂场景导入**：导入包含复杂层次结构、实例化、材质和动画的 USD 场景文件。

## 模块概览

本插件包含两个核心运行时模块，共同协作完成 USD 的导入工作。

- **`InterchangeOpenUSDEditor`**: 负责 USD 数据到 Interchange 内部数据结构的**解析与翻译**。它定义了如何将 USD 的 Prim、属性、关系等映射到 UE 的 Interchange 节点、属性和连接。
- **`InterchangeOpenUSDImport`**: 负责**执行实际的导入操作**。它利用 `InterchangeOpenUSDEditor` 生成的中间表示，调用 UE 的资产导入系统（如 Static Mesh、Skeletal Mesh、Material 的创建器）将数据转换为可编辑的 UE 资产。

## 使用场景

- **美术工作流**：美术师在 Houdini 中创建一个包含复杂模型和材质的 USD 资产，通过 Interchange 管线一键导入到 UE 项目中，并保持材质结构和实例关系。
- **技术流程**：程序需要读取一个由外部工具生成的 USD 文件，提取其结构信息并进行处理或验证，然后导入为特定的资产类型。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Performance/Tests/InterchangeOpenUSD)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | USD 预生成：实现了对骨骼和物理资产的跟踪功能。 |
| 2026-05-22 | `e55b6ad4` | USD Pregen: Fix handling of USDZ files. | USD 预生成：修复了对 USDZ 文件的处理问题。 |
| 2026-05-19 | `fd496b57` | USD Pregen: Properly tag nodes produced by MaterialX translator with corresponding prim path so that | USD 预生成：正确标记由 MaterialX 翻译器生成的节点，并关联对应的 Prim 路径。 |
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated; | USD 预生成：修复了实例内部材质未被正确去重的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下产生关于双精度常量截断为浮点数警告的代码。 |

### 维护评价

- **状态**: **活跃维护中**。从提交历史看，开发团队在 2026 年 5 月仍在密集提交功能更新和问题修复，特别是围绕“USD Pregen”（USD 预生成）功能。
- **注意事项**: 该插件标记为 `IsExperimentalVersion = true` 且默认未启用，表明其仍处于实验阶段，API 和功能可能发生变化，不建议在生产项目的关键路径中直接依赖。
- **推荐**: 适合希望探索或构建基于 USD 的资产管线的团队和开发者进行早期集成和测试，以获取最新功能并反馈问题。在将其用于生产环境前，需充分评估稳定性风险。