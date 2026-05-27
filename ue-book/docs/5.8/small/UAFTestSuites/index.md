# UAF Tests

> UAF Automated Tests（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UAF 自动化测试 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、测试数据） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

UAFTestSuites 是 **Unreal Animation Framework (UAF)** 的自动化测试插件，为 UAF 核心功能提供全面的回归测试覆盖。该插件包含动画图（AnimGraph）、动画节点（AnimNode）以及自定义查询（Custom Query）等多个维度的测试套件，用于验证 UAF 系统在引擎开发过程中的正确性和稳定性。

由于 UAF 本身仍处于实验阶段，此测试插件配合 EngineTest 等测试项目运行，是 UAF 开发团队保障代码质量的关键基础设施。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `UAFAnimGraphTestSuite` | Runtime | UAF 动画图相关功能的自动化测试 |
| `UAFAnimNodeTestData` | Runtime | UAF 动画节点的测试数据资产和辅助资源 |
| `UAFCQTestSuite` | Runtime | UAF 自定义查询（Custom Query）的自动化测试 |
| `UAFTestSuite` | Runtime | UAF 核心功能的通用自动化测试 |

## 使用场景

- **UAF 引擎开发者**：在修改 UAF 核心代码后运行此测试套件，验证改动未引入回归问题
- **CI/CD 流水线**：在引擎构建流水线中自动执行，作为 UAF 功能的门禁测试
- **AnimSandbox / EngineTest 项目**：首次创建时即在这些测试项目中启用，用于集成验证

> ⚠️ 此插件**不面向最终用户**，仅用于 UAF 内部开发测试。普通项目无需也不应启用此插件。

## 模块依赖

由于所有模块均为测试模块，依赖较为标准：

| 模块 | 用途 |
|---|---|
| `UAF` | 被测主体 — UAF 核心框架 |

其他依赖为标准的 Core/Engine/Animation 模块，无特殊外部依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，确保 MSVC 和 Clang 编译器兼容 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配问题 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复 FBindableXxx 绑定在 UAF traits 中的序列化问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏从 UE_LOG 到 UE_LOGF |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名 GetComponent 为 GetOrAddComponent 以匹配实际行为 |

### 维护评价

- **状态**：🟢 活跃维护中
- UAF 整体仍处于实验阶段（`IsExperimentalVersion=true`），此测试插件随 UAF 核心代码同步更新
- 最近 3 个月内持续有实质性更新（编译兼容修复、序列化修复、API 重命名等）
- 作为 Epic 官方测试套件，在 UAF 正式发布前将保持活跃维护
- **建议**：仅供 UAF 开发团队使用，普通项目请勿启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [UAF 主插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)