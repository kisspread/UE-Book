# KDevelop Integration

> Allows access to source code in KDevelop.

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | 是 |
| 包含内容 | 否 |
| 模块 | KDevelopSourceCodeAccess (UncookedOnly) |
| 创建时间 | 2014-11-04 |
| 年龄标签 | 🏛️ 文物(>10年) |
| 平台限制 | 仅 Linux |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/KDevelopSourceCodeAccess) | |

## 用途

这是一个 **源码访问器（Source Code Accessor）** 插件，让 Unreal Editor 能够在 Linux 上调用 [KDevelop](https://www.kdevelop.org/) IDE 来打开 C++ 源码文件。当你在编辑器中点击"打开源码文件"、双击编译错误跳转到对应代码行时，UE 需要知道用哪个 IDE 打开——这个插件就是告诉 UE "用 KDevelop"。

插件通过实现 `ISourceCodeAccessor` 接口，将 KDevelop 注册为 UE 的源码访问后端。它使用 `.kdev4` 项目文件格式，通过 `kdevelop` 命令行工具启动 IDE。

> **⚠️ 已知限制：** 当前实现中大量功能被标记为 `STUBBED`（桩代码），实际上 **只有"打开解决方案（.kdev4 项目文件）"功能完整可用**。`OpenFileAtLine`、`OpenSourceFiles`、`SaveAllOpenDocuments`、`IsIDERunning` 等方法均未真正实现。代码中留有多处 FIXME 注释，表明这是早期的骨架实现。

## 使用场景

- 你在 **Linux** 上使用 **KDevelop 4.x** 作为 UE5 的 C++ IDE
- 你希望在 Unreal Editor 中双击编译错误时，自动在 KDevelop 中打开对应源码文件
- 你使用 KDevelop 的 `.kdev4` 项目文件来管理 UE 源码工程

> 如果你使用 VS Code、Rider、CLion 等其他 IDE，应选择对应的源码访问器插件，而非此插件。

## 蓝图用法

此插件不暴露任何蓝图节点。它是一个 **Editor-only 工具插件**，仅在编辑器内部通过 `ISourceCodeAccessor` 接口与 UE 编辑器交互。

## C++ 用法

此插件是面向 UE 编辑器内部集成的，普通游戏开发者无需直接调用其 C++ API。以下信息面向需要理解或修改此插件的开发者。

### 架构概览

插件由两个类组成：

| 类 | 职责 |
|---|---|
| `FKDevelopSourceCodeAccessModule` | 模块入口，负责注册/注销 `FKDevelopSourceCodeAccessor` 到 ModularFeatures |
| `FKDevelopSourceCodeAccessor` | 实现 `ISourceCodeAccessor` 接口，处理与 KDevelop 的所有交互 |

### 注册机制

模块启动时，将 accessor 注册到 UE 的 ModularFeatures 系统：

```cpp
// KDevelopSourceCodeAccessModule.cpp
void FKDevelopSourceCodeAccessModule::StartupModule()
{
    KDevelopSourceCodeAccessor.Startup();
    IModularFeatures::Get().RegisterModularFeature(
        TEXT("SourceCodeAccessor"), &KDevelopSourceCodeAccessor);
}
```

### 解决方案路径逻辑

`GetSolutionPath()` 根据项目类型决定 `.kdev4` 文件路径：

- **引擎项目**（非外部项目）：`{RootDir}/UnrealEditor.kdev4`
- **游戏项目**：`{ProjectDir}/{ProjectName}.kdev4`

### KDevelop 路径检测

`CanRunKDevelop()` 硬编码检查 `/usr/bin/kdevelop` 是否存在。代码中有 `FIXME: search properly` 注释，说明未来需要更智能的路径搜索。

### 实现状态

| ISourceCodeAccessor 方法 | 状态 | 说明 |
|---|---|---|
| `CanAccessSourceCode()` | ✅ 可用 | 检查 `/usr/bin/kdevelop` 是否存在 |
| `OpenSolution()` | ✅ 可用 | 启动 KDevelop 打开 .kdev4 文件 |
| `OpenSolutionAtPath()` | ✅ 可用 | 启动 KDevelop 打开指定 .kdev4 文件 |
| `DoesSolutionExist()` | ✅ 可用 | 检查 .kdev4 文件是否存在 |
| `GetFName()` | ✅ 可用 | 返回 `FName("KDevelop")` |
| `GetNameText()` | ✅ 可用 | 返回 `"KDevelop 4.x"` |
| `GetDescriptionText()` | ✅ 可用 | 返回描述文本 |
| `OpenFileAtLine()` | ❌ 桩代码 | 计划通过 qdbus 实现，未完成 |
| `OpenSourceFiles()` | ❌ 桩代码 | 计划通过 qdbus 实现，未完成 |
| `SaveAllOpenDocuments()` | ❌ 桩代码 | 未实现 |
| `IsIDERunning()` | ❌ 桩代码 | 始终返回 `false` |
| `AddSourceFiles()` | ❌ 未实现 | 直接返回 `false` |

## Demo 示例

此插件无需编写代码集成。使用方式：

1. 确保在 Linux 上安装了 KDevelop 4.x（`/usr/bin/kdevelop` 存在）
2. 在 UE 编辑器中，进入 **Editor Preferences → Source Code Editor**
3. 选择 **KDevelop 4.x** 作为源码编辑器
4. 点击编辑器中的"Open Source Code"按钮，KDevelop 将启动并打开 `.kdev4` 项目文件

## 模块依赖

此插件为 Editor-only 插件，所有依赖均为 `PrivateDependencyModuleNames`：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `SourceCodeAccess` | 提供 `ISourceCodeAccessor` 接口定义 |
| `DesktopPlatform` | 平台相关功能（进程启动等） |
| `HotReload` | 热重载支持（仅 Editor 构建时依赖） |

> 这些依赖均为私有依赖，使用者无需在自己的 Build.cs 中引用。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da` | IWYU 批量更新，减少头文件依赖 | 编译维护，无功能变更 |
| 2022-11-07 | `0a10c21` | Release-Engine-Staging 同步更新 | 分支合并，无实质改动 |
| 2022-04-14 | `b935189` | 为 Code Access 插件添加 ShortName | 路径长度优化，所有同类插件统一处理 |

### 维护评价

- **创建时间**：2014 年 11 月，已有 **11 年以上** 历史
- **最后实质性功能更新**：无记录（自 2014 年创建以来未有功能提交）
- **最近更新**：2023 年 1 月，仅为 IWYU 头文件整理，属于编译维护
- **维护状态**：⚠️ **可能废弃**
  - 大量核心方法仍为 `STUBBED` 桩代码，11 年来未补全
  - 代码中有多处 `FIXME` 注释未解决
  - 仅支持 KDevelop 4.x（当前 KDevelop 已到 5.x 版本）
  - `IsIDERunning()` 始终返回 `false`，意味着重复点击"打开源码"会多次启动 KDevelop
  - `OpenFileAtLine()` 不可用，双击编译错误无法跳转到具体行号
- **是否推荐使用**：**不推荐**。此插件功能极其不完整，仅能打开 .kdev4 项目文件，无法实现跳转到具体文件和行号等核心 IDE 集成需求。如果你使用 KDevelop 5.x，建议考虑自行扩展或使用通用的命令行 IDE 集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/KDevelopSourceCodeAccess)
- [KDevelop 官网](https://www.kdevelop.org/)
- [ISourceCodeAccessor 接口定义](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Developer/SourceCodeAccess/Public/ISourceCodeAccessor.h)
