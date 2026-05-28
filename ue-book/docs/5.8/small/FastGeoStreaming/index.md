# FastGeo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何流送 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、几何数据结构） |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

FastGeoStreaming 解决大世界场景中静态几何体流送的性能瓶颈问题。它将世界分区（World Partition）中的不可变静态几何体（StaticMesh、InstancedStaticMesh，含碰撞）提取并转换为轻量级非 UObject 数据结构，然后在运行时通过异步方式（大部分代码不在游戏线程上执行）进行流送。

核心价值在于：传统流送方式需要加载和实例化完整的 UObject 层级，而 FastGeoStreaming 绕过了这一开销，直接操作优化后的数据结构，大幅降低了流送延迟和内存压力。系统兼容 World Partition 的 Data Layers 和 HLOD 等特性，嵌入到已有的 Level Streaming 流程中。

**前提条件**：需要启用 `p.Chaos.EnableAsyncInitBody` CVar。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [FastGeoStreaming](FastGeoStreaming.md) | Runtime | 核心运行时：几何体提取、转换、异步流送的完整实现 |
| [FastGeoStreamingEditor](FastGeoStreamingEditor.md) | Editor | 编辑器支持：WorldPartitionCellTransformer 及编辑器集成 |

## 使用场景

- 你有一个大型开放世界游戏，静态几何体数量庞大，流送卡顿明显 → 使用 FastGeoStreaming 替代默认流送路径
- 你的 World Partition 场景包含大量 StaticMesh 和 InstancedStaticMesh → FastGeoStreaming 可自动提取并优化
- 你需要支持 GPU 动画实例化蒙皮网格的流送 → 插件已支持 `GPU Animated Instanced Skinned Meshes`
- 你希望异步处理几何体流送以减少游戏线程负担 → FastGeoStreaming 的核心设计就是异步的

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器模块依赖（用于 WorldPartitionCellTransformer 集成） |

> ⚠️ 注意：Runtime 模块依赖 `UnrealEd` 是非典型配置，表明当前实现可能包含仅编辑器环境可用的代码路径。打包时需确认依赖是否正确隔离。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | CVar 描述和命名规范化清理 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 新增 GPU 动画实例化蒙皮网格支持 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 加固代理组件的物理查询稳定性 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复运行时单元转换器中未注册组件的世界变换 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 构建代理描述符时从 BodySetup 解析可行走坡度覆盖 |

### 维护评价

**活跃维护中**。插件创建于 2025 年 3 月，至今约 1 年，近期（2026 年 5 月）仍有密集的功能增强和 bug 修复。最近一次提交涉及新特性支持（GPU 动画实例化蒙皮网格）和多项稳定性改进，表明该插件处于积极开发阶段。

⚠️ **注意事项**：
- 标记为实验性（`IsExperimentalVersion=true`），API 可能随时变化
- 默认未启用（`EnabledByDefault=false`），需手动在项目设置中开启
- 虽然处于活跃开发，但作为实验性插件，生产环境使用需谨慎评估
- **推荐使用**：适合对大世界流送性能有极致需求的项目，建议在项目早期集成测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- [FastGeoStreaming 模块文档](FastGeoStreaming.md)
- [FastGeoStreamingEditor 模块文档](FastGeoStreamingEditor.md)