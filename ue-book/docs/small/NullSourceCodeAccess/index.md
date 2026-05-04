# Null Source Code Access (Linux Compiler-only Integration)

> Allows access to c++ projects while only looking for clang++

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | NullSourceCodeAccess (UncookedOnly) |
| 平台限制 | Linux only |
| 创建时间 | 2015-04-20 |
| 年龄标签 | 🏛️ 文物 (>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/NullSourceCodeAccess) | |

## 用途

NullSourceCodeAccess 是 UE5 **源码访问器 (Source Code Accessor)** 的一个空实现（stub）。它解决的核心问题是：

**在 Linux 上，你可能只有 `clang++` 编译器，而没有安装任何 IDE（如 Visual Studio、Rider、VS Code 等）。** UE5 的编辑器在处理 C++ 项目时需要一个源码访问器来"打开文件"、"跳转到行"等操作。如果没有注册任何访问器，编辑器会报错或阻止你创建 C++ 项目。

这个 plugin 提供了一个最小化的、什么都不做的源码访问器：
- `CanAccessSourceCode()` 始终返回 `true` —— 让编辑器认为源码工具链可用
- `DoesSolutionExist()` 返回 `false` —— 承认没有 IDE 解决方案文件
- `OpenFileAtLine()` / `OpenSourceFiles()` / `AddSourceFiles()` 全部返回 `false` —— 无法打开文件，但不会崩溃
- `OpenSolutionAtPath()` 会尝试用文件管理器打开路径（`FPlatformProcess::ExploreFolder`）

本质上，它是一个 **"让编辑器不再抱怨没有 IDE"的占位符**。

## 使用场景

- 你在 Linux 上用纯命令行（clang++）编译 UE5，不想安装 IDE → 这个 plugin 会自动生效
- 你在 Linux 服务器上运行 UE5 编辑器进行蓝图开发，偶尔需要创建 C++ 类但不需要 IDE 集成
- 你在 CI/CD 环境中构建 UE5 项目，不需要源码编辑功能

**注意**：此 plugin 仅在 Linux 平台加载（`PlatformAllowList: ["Linux"]`），在 Windows/macOS 上不会被加载。在那些平台上，你通常有 Visual Studio 或 Xcode 作为源码访问器。

## 蓝图用法

此 plugin 没有暴露任何蓝图接口。它完全在编辑器后台工作，通过 `IModularFeatures` 注册为 `SourceCodeAccessor`。

## C++ 用法

此 plugin 不提供公共 API。它通过 UE5 的 Modular Feature 系统自动注册，不需要用户代码调用。

### 工作原理

```
编辑器启动
  → FNullSourceCodeAccessModule::StartupModule()
    → IModularFeatures::Get().RegisterModularFeature("SourceCodeAccessor", &NullSourceCodeAccessor)
      → 编辑器调用 CanAccessSourceCode() → 返回 true → 允许 C++ 项目操作
```

如果你需要在自己的代码中检查当前使用的源码访问器：

```cpp
#include "Features/IModularFeatures.h"

// 获取所有注册的源码访问器
TArray<ISourceCodeAccessor*> Accessors;
IModularFeatures::Get().GetModularFeatureImplementations<ISourceCodeAccessor>(TEXT("SourceCodeAccessor"));
```

## Demo 示例

无需编写任何代码。启用 plugin 后，UE5 编辑器会自动使用它作为源码访问器。

验证方式：
1. 在 Linux 上打开 UE5 编辑器
2. 创建一个 C++ 项目（不需要安装 VS Code 或任何 IDE）
3. 项目创建成功，不会报"找不到 IDE"的错误
4. 尝试在编辑器中双击 C++ 类 → 会打开文件管理器（而非 IDE）

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心基础库 |
| `DesktopPlatform` | 平台相关功能（文件夹浏览等） |
| `SourceCodeAccess` | 源码访问器接口（ISourceCodeAccessor） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da71ab9` | IWYU updates to reduce includes | 清理头文件依赖，无功能变更 |
| 2022-11-07 | `0a10c21ff628` | Update Release-Engine-Staging | 批量同步更新，无针对性改动 |
| 2022-04-14 | `b935189461f3` | Add ShortNames to Code Access plugins | 添加 ShortName 减少路径长度压力 |

### 维护评价

- **年龄**：2015 年创建，已超过 10 年
- **最近更新**：最近一次功能性更新在 2022 年 4 月（添加 ShortName），之后仅有维护性 IWYU 清理
- **活跃度**：**不活跃** —— 代码极其简单（核心逻辑 ~70 行），基本不需要更新
- **已知限制**：只能在 Linux 上使用；无法真正打开文件或 IDE
- **推荐使用**：✅ 如果你在 Linux 上做纯命令行开发，它是必需的。不需要手动启用（默认已启用）。如果你在 Linux 上安装了 VS Code / Rider，可以使用对应的 IDE 集成 plugin 替代它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/NullSourceCodeAccess)
- [SourceCodeAccess 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Developer/SourceCodeAccess) — 此 plugin 实现的接口所在模块
