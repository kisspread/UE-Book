# Rider Integration

> Allows access to source code in Rider.

| 属性 | 值 |
|---|---|
| 中文名 | Rider 集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RiderSourceCodeAccess` (EditorNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2020-02-22 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/RiderSourceCodeAccess) | |

## 用途

该插件为 Unreal Engine 编辑器提供 JetBrains Rider IDE 的源码访问集成。它实现了 `ISourceCodeAccessor` 接口，使开发者可以在 UE 编辑器中直接用 Rider 打开源码文件、跳转到指定行、打开解决方案等。

插件的核心功能包括：

- **自动探测 Rider 安装位置**：支持通过 Toolbox V2、注册表（Windows）、应用程序目录（macOS/Linux）以及自定义路径检测 Rider 安装
- **同时支持 .sln 和 .uproject 模式**：生成两种类型的访问器，分别对应使用 `.sln` 解决方案文件和直接使用 `.uproject` 项目文件打开 Rider 的方式
- **版本管理和排序**：自动选择最新版本的 Rider，并区分 Release/Beta 版本对 `.uproject` 模式的支持状态
- **跨平台支持**：支持 Windows、macOS 和 Linux 三个平台

## 使用场景

- 你使用 JetBrains Rider 作为 UE 项目的主 IDE，需要在编辑器中双击代码文件时直接跳转到 Rider 打开
- 你安装了多个版本的 Rider（如通过 Toolbox 安装），插件会自动选择最新版本
- 你希望从 UE 编辑器的「Source Code Editor」下拉菜单中选择 Rider 作为默认编辑器
- 你想通过 UE 编辑器直接在 Rider 中打开整个解决方案

## 蓝图用法

该插件是一个纯编辑器集成插件，不提供蓝图可调用的节点。所有功能通过 UE 编辑器的源码访问系统自动集成。

### 编辑器中的配置方式

1. 打开 **Edit → Editor Preferences**
2. 导航到 **General → Source Code**
3. 在 **Source Code Editor** 下拉菜单中选择 **Rider** 或具体的 Rider 安装路径
4. 如果安装了多个 Rider 版本，下拉菜单会列出所有检测到的版本

## C++ 用法

该插件主要面向终端用户，不需要在项目代码中直接使用。其内部通过实现 `ISourceCodeAccessor` 接口与 UE 编辑器集成。

### 核心接口实现

插件的核心类 `FRiderSourceCodeAccessor` 实现了 `ISourceCodeAccessor` 接口的以下方法：

| 方法 | 说明 |
|---|---|
| `OpenFileAtLine` | 在 Rider 中打开指定文件并跳转到指定行和列 |
| `OpenSourceFiles` | 在 Rider 中打开多个源码文件 |
| `OpenSolution` | 打开整个解决方案 |
| `AddSourceFiles` | 向项目中添加源码文件并重新生成项目文件 |
| `SaveAllOpenDocuments` | 保存 Rider 中所有打开的文档 |
| `DoesSolutionExist` | 检查解决方案文件是否存在 |

### 自定义扩展（高级）

如果需要自定义 Rider 的启动行为，可以参考 `FRiderSourceCodeAccessor` 中的 `HandleOpeningRider` 方法模式：

```cpp
// 来自 Source/RiderSourceCodeAccess/Private/RiderSourceCodeAccessor.h
// 启动 Rider 并在失败时尝试生成解决方案文件
bool HandleOpeningRider(TFunction<bool()> Callback) const;
```

## 模块依赖

该插件的模块类型为 `EditorNoCommandlet`，仅在编辑器中加载。

| 模块 | 用途 |
|---|---|
| `GameProjectGeneration` | 用于生成 .sln 解决方案文件（通过 `GenerateSlnAccessors`） |

无其他特殊依赖（标准 Core/Engine/Slate 等省略）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 新日志宏 |
| 2025-09-18 | `5f62bc3a` | Fixed perf issue with mdfind taking multiple minutes due to it matching debug files emitted from Sha | 修复 macOS 上 mdfind 搜索调试文件导致的性能问题 |
| 2023-11-27 | `391ea579` | Fix missing copyright boilerplate in source control files | 补充源码控制文件中缺失的版权声明 |
| 2023-11-27 | `873e77b4` | PR #11109: Specify styles when selecting icons for SourceCodeAccess implementations | 为源码访问器实现指定图标样式 |
| 2023-10-06 | `69726f5e` | Update code using FJsonObject to use TCHAR strings instead of ANSI strings | 将 FJsonObject 使用的 ANSI 字符串更新为 TCHAR 字符串 |

### 维护评价

- **活跃维护**：最近一次更新在 2026 年 4 月，说明 JetBrains 持续维护此插件
- **更新频率**：约每 1-2 年有实质性更新，中间穿插小修复
- **维护方**：由 JetBrains 官方维护（而非 Epic），保证了与 Rider 的兼容性
- **稳定性**：作为 Editor 集成插件，功能成熟稳定，无已知重大问题
- **推荐使用**：✅ 强烈推荐 Rider 用户启用，该插件默认已启用，开箱即用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/RiderSourceCodeAccess)
- [官方文档](https://github.com/JetBrains/RiderSourceCodeAccess)