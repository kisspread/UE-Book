# Spatial Readiness

> World readiness management for spatial physics volumes.

| 属性 | 值 |
|---|---|
| 中文名 | 空间就绪管理 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SpatialReadiness` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SpatialReadiness) | |

## 用途

SpatialReadiness 插件提供空间区域的"就绪状态"管理功能，允许标记世界中的物理空间体积为"未就绪"（Unready），从而在这些区域内禁用物理查询和模拟。该插件在流式加载场景中尤为重要——当新区域正在加载但物理数据尚未完全就绪时，可以防止不完整的物理交互。插件通过控制碰撞检测的 MidPhase 过滤、查询阻塞过滤器和模拟阻塞过滤器来实现空间就绪状态的精细控制。

## 使用场景

- **世界分区流式加载**：当 World Partition 区块正在加载时，需要临时禁用该区域的物理交互
- **关卡动态加载**：动态加载子关卡时，确保物理场景在完成初始化前不被访问
- **物理场景热更新**：需要在运行时更新物理配置的区域，暂时屏蔽物理查询以避免不一致状态
- **大型多人世界服务器**：分区域管理物理就绪状态，优化性能

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `SpatialReadiness` | Runtime | 核心模块，提供空间就绪状态管理、子系统和物理回调 |
| `SpatialReadinessTests` | Runtime | 自动化测试模块，验证空间就绪功能的正确性 |

## 模块依赖

该插件依赖 `ChaosUserDataPT` 插件（物理用户数据）。使用者的模块无特殊依赖（仅标准 Core/Engine/PhysicsCore 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 日志框架 |
| 2026-04-01 | `f85501de` | Avoid expensive includes in SpatialReadinessSubsystem.h and SpatialReadinessSimCallback.h | 优化头文件包含，减少编译开销 |
| 2026-03-03 | `ed0e1959` | Add missing physics scene lock to FSpatialReadinessSimCallback::AddUnreadyVolume_GT | 修复添加未就绪体积时缺少物理场景锁的问题 |
| 2025-12-08 | `0b36b316` | [Spatial Readiness] Ensure to disable MidPhase for Unready volumes | 确保未就绪体积禁用碰撞 MidPhase 检测 |
| 2025-11-18 | `db60e2a5` | Updated spatial readiness to not use separate query/sim block filters and instead create separate sh | 重构阻塞过滤器架构，不再使用独立的查询/模拟过滤器 |

### 维护评价

该插件创建于 2025 年初，至今约 1 年，仍处于**活跃开发**阶段。近半年内持续有功能性更新和 bug 修复，包括架构重构和性能优化。作为实验性插件且默认未启用，表明 Epic 内部正在积极迭代。最近的 commit 关注编译优化和正确性修复，说明已进入稳定期。**建议关注但谨慎用于生产环境**，等待正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SpatialReadiness)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SpatialReadiness/Tests)