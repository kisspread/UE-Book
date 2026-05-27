# Terminal

> Native Slate terminal emulator.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器终端 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Terminal` (Editor), `TerminalTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal) | |

## 用途

Terminal 插件在 UE5 编辑器内部嵌入了一个原生的终端仿真器，基于 Slate 框架构建。它解决了开发者需要频繁在 UE5 编辑器和外部命令行窗口之间切换的问题——将类 Unix PTY（伪终端）会话直接集成到编辑器面板中，让开发者可以在编辑器内运行 Shell 命令、查看输出、执行构建脚本或自动化工具，无需离开 UE5 工作环境。

从提交记录可以看出，该插件实现了完整的键盘输入翻译层（将 UE 键事件转换为终端转义序列）、会话生命周期管理（含活动状态提示以防止意外关闭），以及可配置的终端设置系统。

## 使用场景

- 你在 UE5 编辑器内频繁执行命令行操作（如 Git、构建脚本、测试工具）→ 用 Terminal
- 你需要一个嵌入式终端来运行 UnrealBuildTool 或自动化测试 → 用 Terminal
- 你希望避免在 UE5 和外部终端之间来回切换 → 用 Terminal
- 你在开发编辑器扩展，需要集成一个可编程的终端面板 → 用 Terminal

## 蓝图用法

此插件是纯编辑器 UI 工具，主要通过 Slate 面板交互，不暴露蓝图可调用函数。终端的所有交互均通过编辑器内嵌的终端面板完成。

## C++ 用法

### 头文件引入

```cpp
#include "TerminalModule.h"
```

### 基本用法

该插件通过 Slate 面板集成到编辑器中，核心类 `UTerminalSettings` 提供终端行为配置。以下为典型的 C++ 集成模式：

```cpp
// 访问终端设置（来源：UTerminalSettings 重构提交 2832901f）
// 终端设置不再使用 defaultconfig，需通过 GetMutableDefault 获取
UTerminalSettings* Settings = GetMutableDefault<UTerminalSettings>();
```

### 进阶用法

插件内部实现了键位到 PTY 的完整转译层（来源：提交 `c9454ad1`）。如果你需要在自定义终端实现中复用类似的键位翻译逻辑，可以参考 `Terminal` 模块中的专用翻译器类，它将 UE 的 FKey / FModifierKeyState 矩阵完整映射为终端转义序列。

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，兼容 MSVC 和 Clang 编译器 |
| 2026-05-12 | `91d5944f` | [Terminal] Surface session activity and prompt before closing the editor mid-output. | 关闭编辑器时如有活动会话会弹出确认提示 |
| 2026-04-28 | `2832901f` | [Terminal] Drop `defaultconfig` from `UTerminalSettings`. | 移除设置类的 defaultconfig 标记，调整配置持久化方式 |
| 2026-04-20 | `c9454ad1` | [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator. | 实现完整的键盘输入到 PTY 转义序列的转译层 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF |

### 维护评价

Terminal 是一个**非常新的实验性插件**，于 2026 年 4 月从内部仓库迁移至 `Engine/Plugins/Experimental`。从提交记录来看，该插件处于**活跃开发**状态：

- **开发节奏密集**：创建后约一个月内有 5 次提交，涵盖功能实现（键位转译）、UX 改进（关闭确认）、代码质量（编译器兼容、日志迁移）和架构调整（设置重构）
- **实验性标记**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能发生重大变更
- **不可再分发**：`NoRedist=true`，仅限引擎内部使用
- **无公开文档**：`DocsURL` 为空

**推荐**：适合对编辑器扩展开发感兴趣的高级开发者提前体验和探索。不建议在生产环境中依赖此插件，API 稳定性无法保证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal/Source/TerminalTests)