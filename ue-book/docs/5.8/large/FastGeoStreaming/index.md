# Fast Geo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何流送 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据结构定义） |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

FastGeoStreaming 是一个针对 **World Partition** 大世界场景的高性能流送优化系统。它解决了大规模开放世界中静态几何体（StaticMesh 和 InstancedStaticMesh）流送性能瓶颈的问题。

核心思路是：将世界中不可变的静态几何体提取并转换为**轻量级非 UObject 数据结构**，在运行时通过**异步非 GameThread** 的方式进行流送加载和卸载，从而大幅降低主线程压力。

该系统是关卡流送流程的一部分，兼容 World Partition 的 Data Layers 和 HLOD 等功能。启用前提条件：需要开启 `p.Chaos.EnableAsyncInitBody`。

## 使用场景

- 你在做一个**大型开放世界游戏**，World Partition 的标准流送性能不足 → 用 FastGeoStreaming 加速静态几何体流送
- 你的场景中包含大量 **StaticMesh / InstancedStaticMesh**（含碰撞），需要更高效的加载/卸载机制 → 启用此插件
- 你需要在保持 **Data Layers 和 HLOD 兼容性**的前提下优化流送 → 该系统专为此设计

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`FastGeoStreaming`](FastGeoStreaming.md) | Runtime | 核心运行时模块：几何体提取、数据结构转换、异步流送加载/卸载 |
| [`FastGeoStreamingEditor`](FastGeoStreamingEditor.md) | Editor | 编辑器支持模块：WorldPartitionCellTransformer 实现，负责在编辑器中将世界几何体转换为轻量数据结构 |

## 蓝图用法

此插件主要通过 **World Partition Cell Transformer** 机制工作，不暴露通用蓝图节点。配置主要通过 CVar 控制：

| 控制台变量 | 说明 |
|---|---|
| `p.Chaos.EnableAsyncInitBody` | **必须启用**，异步物理体初始化（前提条件） |

## C++ 用法

此插件的使用主要通过 World Partition 流送管线自动集成，而非直接 API 调用。详见各子模块文档。

### 头文件引入

```cpp
#include "FastGeoStreaming/FastGeoStreamingModule.h"
```

## Demo 示例

此插件作为 World Partition 基础设施，通常不需要直接编码。启用后会自动参与关卡流送流程。具体用法详见子模块文档。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器端几何体转换器（FastGeoStreaming Runtime 模块的依赖，非典型用法） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | CVar 命名和描述规范化清理 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 支持 GPU 动画蒙皮实例化网格体 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 加固代理组件的物理查询鲁棒性 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复运行时单元转换器中未注册组件的世界变换 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 构建代理描述符时从 BodySetup 解析 WalkableSlopeOverride |

### 维护评价

- **状态**: 🟢 **活跃维护中** — 插件创建仅 1 年，最近一周内有多次功能性更新
- **实验性标记**: 仍标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，尚未正式发布
- **更新频率**: 非常活跃，2026 年 5 月密集更新，包含新功能（GPU 蒙皮网格体支持）和稳定性修复
- **推荐**: 适合在实验性项目中评估使用，生产环境需谨慎，注意兼容性风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- [FastGeoStreaming 模块文档](FastGeoStreaming.md)
- [FastGeoStreamingEditor 模块文档](FastGeoStreamingEditor.md)