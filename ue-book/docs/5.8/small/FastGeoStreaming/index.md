# Fast Geo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何流送 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

FastGeoStreaming 解决的是大型开放世界中静态几何体流送的性能瓶颈问题。它将 World Partition 网格中的不可变静态几何体（StaticMesh、InstancedStaticMesh，包括带碰撞的）提取并转换为轻量级非 UObject 数据结构，在运行时通过异步方式（主要在非 GameThread）进行流进和流出。

核心思路：避免传统 StaticMesh Actor 的 UObject 开销，用专用的轻量格式表示几何体，配合异步物理初始化（需启用 `p.Chaos.EnableAsyncInitBody`），显著降低世界流送的卡顿。

它作为关卡流送流程的一部分，兼容 World Partition 的 Data Layers 和 HLOD 等特性。

## 使用场景

- 你有一个大型开放世界游戏，使用 World Partition 管理地图 → 用 FastGeoStreaming 优化静态几何体的流送性能
- 你的世界中有大量 InstancedStaticMesh（植被、建筑装饰等），流送时频繁卡顿 → 用 FastGeoStreaming 将它们转换为轻量格式
- 你需要异步物理体初始化来避免主线程阻塞 → FastGeoStreaming 在非 GameThread 处理大部分逻辑

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `FastGeoStreaming` | Runtime | 核心运行时模块：实现 WorldPartitionCellTransformer、轻量几何数据结构、异步流送逻辑 |
| `FastGeoStreamingEditor` | Editor | 编辑器支持模块：提供编辑器内的 FastGeo 转换和编辑工具 |

详细 API 文档见各子模块页面：
- [FastGeoStreaming.md](FastGeoStreaming.md)
- [FastGeoStreamingEditor.md](FastGeoStreamingEditor.md)

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器集成（FastGeoStreaming 运行时模块的依赖，用于 World Partition Cell 转换） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | 清理 FastGeo/SSAM/异步物理相关控制台变量的命名和描述 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 新增对 GPU 动画实例化蒙皮网格的支持 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 加固代理组件的物理查询稳定性 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复运行时单元转换器中未注册组件的世界变换问题 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 在构建代理描述符时从 BodySetup 读取 WalkableSlopeOverride |

### 维护评价

**活跃维护中**。

- 创建于 2025 年 3 月，至今约 1 年，仍处于早期实验阶段
- 最近更新非常密集（2026 年 5 月多次提交），涵盖新功能（GPU 动画蒙皮实例）、Bug 修复、物理查询加固等
- 由 Epic 核心团队（JeanFrancois.Dube、Dominic.Couture、Sebastien.Lussier）维护
- 当前为 `ExperimentalVersion`，且 `EnabledByDefault=false`，需手动启用
- 依赖 `p.Chaos.EnableAsyncInitBody` CVar，这是使用前提

⚠️ **注意**：此插件仍为实验性，API 可能发生破坏性变更。建议在项目中谨慎评估后使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- [FastGeoStreaming 模块文档](FastGeoStreaming.md)
- [FastGeoStreamingEditor 模块文档](FastGeoStreamingEditor.md)