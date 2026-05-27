# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF测试套件 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（自动化测试资产） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

此插件为 Unreal Animation Framework (UAF) 提供了全面的自动化测试套件。它是一个仅包含测试逻辑和数据的集合，用于验证UAF框架中核心功能（如动画图、动画节点、自定义查询）的正确性与稳定性。其存在是为了确保UAF在开发和迭代过程中不引入回归错误，是保障动画框架质量的关键基础设施。

## 使用场景

- **引擎开发者/贡献者**：在修改或扩展UAF框架后，运行此测试套件以验证改动没有破坏现有功能。
- **动画系统集成**：在将UAF框架集成到自定义项目或维护引擎分支时，使用此测试套件确保集成的兼容性。
- **质量保证 (QA)**：作为自动化回归测试的一部分，定期运行以监控动画系统的健康状况。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `UAFAnimGraphTestSuite` | Runtime | 针对动画图编辑器及运行时功能的自动化测试。 |
| `UAFAnimNodeTestData` | Runtime | 存储动画节点测试所需的数据资产和蓝图。 |
| `UAFCQTestSuite` | Runtime | 针对UAF自定义查询 (Custom Query) 系统的自动化测试。 |
| `UAFTestSuite` | Runtime | UAF框架通用功能的核心自动化测试套件。 |

## C++ 用法

此插件主要用于运行自动化测试，而非提供给外部项目的运行时API。其测试用例通常通过 Unreal Automation 系统触发。

### 运行测试
测试可通过编辑器中的 `Session Frontend` -> `Automation` 窗口找到并运行，或通过命令行调用。

## 模块依赖

此插件是纯测试插件，其模块主要依赖于UAF框架本身及其他核心动画模块。使用此插件（即运行其测试）通常不需要在你的项目中添加额外的模块依赖。

| 模块 | 用途 |
|---|---|
| `UAFCore` | UAF框架核心模块 |
| `AnimationCore` | 动画核心数学和类型 |
| `AnimationBlueprintLibrary` | 动画蓝图相关工具 |
| `AnimationGraph` | 动画图系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复编译警告，提升跨平台兼容性。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化打印中关于32/64位的说明符错误。 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复了UAF特性与绑定序列化交互时的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式UE_LOG迁移到新的UE_LOGF宏。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将函数重命名为`GetOrAddComponent`以更准确反映其行为。 |

### 维护评价

这是一个非常新的测试插件（创建于2026年2月），并且近期（2026年5月）仍有活跃的更新，主要集中在编译兼容性修复、代码质量改进和框架bug修复上。这表明该插件正在被**积极维护**，并且与UAF核心框架的开发同步。作为实验性插件，它仅用于开发和测试，不建议在生产环境中使用。**强烈推荐**UAF框架的开发者和贡献者使用此插件来保障代码质量。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source)