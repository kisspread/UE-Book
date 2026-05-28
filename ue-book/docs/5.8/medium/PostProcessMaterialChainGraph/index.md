# Post Process Material Chain Graph

> Post Process Material Chain Graph allows users to stack post process materials and render those into render targets separate from Scene Color.\nThis can operate on textures other than scene color without writing those into scene color.

| 属性 | 值 |
|---|---|
| 中文名 | 材质链图 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `PPMChainGraph` (Runtime), `PPMChainGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PostProcessMaterialChainGraph) | |

## 用途

该插件提供了一个“后处理材质链图”（Post Process Material Chain Graph）系统，用于在后处理阶段，将多个材质效果串联或并行地应用于 **非场景颜色（Non-Scene Color）** 的纹理，并将结果输出到独立的临时渲染目标（Render Target）中。

它解决了传统后处理材质只能直接操作场景颜色（Scene Color）的限制，使得开发者可以在不修改原始场景颜色的情况下，对特定的辅助纹理（如光照、自定义遮罩等）应用复杂的材质效果链，为实现更灵活和复杂的渲染管线提供了工具。

## 使用场景

- 你需要实现一种复杂的自定义后处理效果，但该效果需要作用于特定的纹理（例如，一个自定义的光照图或遮罩），而不希望它直接影响最终合成的场景颜色。
- 你的渲染管线需要将多个后处理步骤的结果串联起来，每一步都使用不同的输入纹理，并希望将中间结果保存到独立的缓冲区中以供后续步骤使用。
- 你需要构建一个数据驱动或可动态编辑的后处理流程图，让美术或技术美术能够方便地调整后处理材质的混合和执行顺序。

## 蓝图用法

该插件的主要功能由 `PPMChainGraph` 运行时模块暴露给蓝图。核心节点允许你创建和运行后处理材质链图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 获取子系统 | 获取用于管理后处理材质链图实例的子系统。 | `UPPMChainGraphSubsystem` |
| 创建材质链图实例 | 创建一个新的后处理材质链图对象实例。 | `UPPMChainGraphSubsystem` |
| 运行材质链图 | 执行一个已配置的材质链图，并将结果输出到指定的渲染目标。 | `UPPMChainGraph` |

*(更详细的蓝图API列表请参阅子模块 `PPMChainGraph` 的文档)*

## C++ 用法

### 头文件引入

```cpp
#include "PPMChainGraph.h"
```

### 基本用法

通过子系统获取或创建材质链图实例，并配置其材质节点，然后执行。

*(具体的C++使用示例和API细节请参阅子模块 `PPMChainGraph` 的文档)*

## Demo 示例

在蓝图中，典型的使用流程可能如下：
1.  通过 `UPPMChainGraphSubsystem::Get()` 获取子系统。
2.  调用子系统的 `CreatePPMChainGraph` 方法创建一个新的链图实例。
3.  向链图实例中添加后处理材质节点并连接。
4.  调用链图实例的 `Execute` 方法，传入输入纹理和目标输出纹理。

*(一个完整的、可编译的 C++ 最小示例请参阅子模块 `PPMChainGraph` 的文档)*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | `PPMChainGraph` 运行时模块依赖于此，可能是为了访问某些编辑器功能或资产类型，具体原因需查阅其 `Build.cs`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `5c7314c3` | Fix Color Correct Regions render rect being truncated when dynamic resolution scales below 1.0. | 修复了动态分辨率缩放低于1.0时色彩校正区域渲染矩形被截断的bug。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了旧的 GPU 性能分析器相关宏。 |
| 2025-02-18 | `8c3ee882` | PPMChainGraph: Export public classes & structs, per third-party request. | 响应第三方请求，导出了 PPMChainGraph 模块的公共类和结构体。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 替换了 Engine 目录下其余位置的 `IsValid(this)` 调用。 |

### 维护评价

该插件创建于 2024 年初，是一个相对年轻的实验性插件。从提交历史看，它仍在持续维护中，最近的更新主要是bug修复、宏迁移和API导出等常规维护工作，没有大的功能新增。由于其状态为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明它尚未稳定，不建议在生产环境中默认使用。目前看来功能稳定，适合进行实验和原型开发。

**建议**：该插件目前处于 **维护中但功能稳定** 的状态，适合用于项目原型和技术验证。如需在生产项目中使用，应密切关注其未来版本变化，并自行承担实验性功能带来的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PostProcessMaterialChainGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PostProcessMaterialChainGraph/Tests)