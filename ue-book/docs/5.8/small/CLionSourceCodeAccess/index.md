# CLion Integration

> Allows access to source code in CLion.

| 属性 | 值 |
|---|---|
| 中文名 | CLion集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CLionSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-12-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/CLionSourceCodeAccess) | |

## 用途

此插件为虚幻编辑器集成了 JetBrains CLion IDE 的源代码访问功能。它允许开发者在虚幻编辑器内（例如通过双击编译错误、右键点击源文件等操作）直接将代码文件在 CLion 中打开，从而使用 CLion 强大的 C++ 开发和调试能力。它解决了开发者需要在多个开发环境间切换以进行代码编辑的问题，实现了虚幻编辑器与 CLion 的无缝对接。

## 使用场景

- 你在使用 CLion 作为主要的 C++ 开发环境，但同时需要频繁在虚幻编辑器中查看和调试代码。
- 你需要快速从虚幻编辑器的输出日志或错误列表中跳转到 CLion 中对应源代码的特定行。
- 你希望利用 CLion 的高级重构和代码分析功能，同时保持与虚幻编辑器的紧密集成。

## 蓝图用法

此插件不提供任何蓝图可调用的函数或属性，它主要集成在编辑器内部菜单和操作中。

## C++ 用法

此插件通过虚幻引擎的 `ISourceCodeAccessor` 接口工作，通常不直接在游戏或插件代码中调用。其核心功能在编辑器内部通过 `FModuleManager::LoadModuleChecked` 加载并集成。

### 头文件引入

通常不需要直接引入头文件，因为它的功能已集成到编辑器中。

### 基本用法

开发者无需直接调用此插件的 API。安装并启用后，虚幻编辑器会自动将其注册为可用的源代码访问器。你可以通过编辑器设置（`Edit -> Editor Preferences -> Source Code`）选择 CLion 作为默认的源代码编辑器。

### 进阶用法

如果需要通过编程方式与源代码访问器交互，可以获取 `ISourceCodeAccessor` 接口的实例。但请注意，`FCLionSourceCodeAccessor` 是一个私有实现类，通常不直接访问。

```cpp
// 在编辑器代码中（例如，另一个需要打开文件的编辑器插件）
#include "ISourceCodeAccessModule.h"

if (ISourceCodeAccessModule* SourceCodeAccessModule = FModuleManager::GetModulePtr<ISourceCodeAccessModule>("SourceCodeAccess"))
{
    ISourceCodeAccessor* Accessor = SourceCodeAccessModule->GetAccessor();
    // Accessor->OpenFileAtLine(FilePath, LineNumber);
}
```

## Demo 示例

此插件是一个编辑器集成工具，不提供用于游戏或运行时的演示代码。其作用体现在编辑器内的操作：
1.  在“源代码编辑器”下拉菜单中选择 “CLion”。
2.  在内容浏览器中右键点击一个 `.cpp` 文件，选择 “Go to Source File”，文件将在 CLion 中打开。

## 模块依赖

此插件自身依赖较少，但作为使用者，你的模块如果需要在运行时或编辑器代码中访问源代码访问功能，可能需要依赖以下模块。

| 模块 | 用途 |
|---|---|
| `HotReload` | 用于热重载功能，可能与源代码访问器在重新加载模块时协调 |

*注：此插件主要作为编辑器扩展，其依赖大多为标准编辑器模块。对于使用者而言，无需特殊依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG迁移到UE_LOGF，更新日志宏以符合新规范。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了在可移植工具链下编译失败的模块。 |
| 2026-01-24 | `99277a85` | Fixed compile errors when building UnrealGame with portable toolchain | 修复了使用可移植工具链构建UnrealGame时的编译错误。 |
| 2025-11-18 | `40e181c3` | Add missing HideWindowsPlatformTypes | 添加了缺失的HideWindowsPlatformTypes宏，修复Windows平台编译警告。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 提交信息为目录路径，属于仓库维护性提交，无具体功能变更。 |

### 维护评价

- **创建时间**：插件创建于2017年，是一个相对成熟的编辑器插件。
- **最近更新频率和内容**：最近的更新集中在2025年底和2026年初，主要是编译修复和日志宏迁移，属于平台兼容性和代码规范维护。
- **活跃维护**：从提交记录看，插件仍在维护中，以确保其在新版本引擎和新工具链下的兼容性。
- **已知问题或限制**：作为编辑器插件，其可用性依赖于 CLion IDE 的正确安装和路径配置。
- **推荐使用**：推荐。这是一个稳定且持续维护的插件，为使用 CLion 的开发者提供了必要的集成支持。尽管功能简单，但不可或缺。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/CLionSourceCodeAccess)
- 官方文档：无
- 测试用例：无（此插件为编辑器集成工具，未提供独立测试用例）