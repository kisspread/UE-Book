# KDevelop Integration

> Allows access to source code in KDevelop.

| 属性 | 值 |
|---|---|
| 中文名 | KDevelop集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `KDevelopSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2014-11-04 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/KDevelopSourceCodeAccess) | |

## 用途

该插件为虚幻编辑器提供了与 **KDevelop IDE**（一款主要用于 Linux 的集成开发环境）的深度集成能力。它的核心作用是实现虚幻编辑器内的“源码访问”功能。当在虚幻编辑器中双击一个 C++ 错误、警告或函数名时，它能够自动启动或切换到 KDevelop，并直接定位到对应的源文件和行号，极大地提升了在 Linux 环境下使用 KDevelop 进行 UE C++ 开发的工作流程效率。它解决了编辑器与外部 IDE 之间的源码跳转问题。

## 使用场景

- **你是一位在 Linux 系统下工作的虚幻引擎 C++ 开发者**，习惯使用 **KDevelop** 作为主要的代码编辑和调试环境。
- 你需要从虚幻编辑器（如内容浏览器、调试输出窗口、蓝图节点）快速跳转到 KDevelop 中查看或编辑对应的 C++ 源代码。
- 你希望通过 UE 的“项目设置”中的“源代码编辑器”选项，将 KDevelop 设置为默认的源码访问器。

## 蓝图用法

该插件作为编辑器系统级的“源码访问器”实现，其核心功能（`ISourceCodeAccessor` 接口）通过虚幻编辑器内部机制调用，并未公开任何可通过蓝图节点直接调用的 `BlueprintCallable` 函数。其配置和使用完全在编辑器设置和 C++ 开发流程中完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无公开蓝图节点） | 功能通过编辑器设置和内部调用实现 | `FKDevelopSourceCodeAccessor` |

### 使用示例（蓝图描述）

无直接的蓝图使用场景。用户通过 **编辑器设置 (Editor Preferences) -> 通用 (General) -> 源代码编辑器 (Source Code Editor)** 选择 **KDevelop** 作为默认的编辑器即可。

## C++ 用法

作为系统插件，开发者通常无需直接在自己的游戏/项目代码中与之交互。其主要接口由编辑器自动调用。

### 头文件引入

```cpp
#include "ISourceCodeAccessor.h" // 核心接口所在
#include "KDevelopSourceCodeAccessModule.h" // 模块定义
```

### 基本用法

该插件的核心是实现 `ISourceCodeAccessor` 接口。以下展示了该接口定义的关键虚函数，编辑器会在需要时调用它们：

```cpp
// 来自 Source/KDevelopSourceCodeAccess/Private/KDevelopSourceCodeAccessor.h
class FKDevelopSourceCodeAccessor : public ISourceCodeAccessor
{
public:
    // 检查是否可以访问源码（KDevelop 是否存在且可运行）
    virtual bool CanAccessSourceCode() const override;

    // 在 KDevelop 中打开项目（.kdev4 文件）
    virtual bool OpenSolution() override;

    // 在 KDevelop 中打开指定文件并跳转到特定行和列
    virtual bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0) override;

    // 在 KDevelop 中打开多个源文件
    virtual bool OpenSourceFiles(const TArray<FString>& AbsoluteSourcePaths) override;

    // （可选）尝试将文件添加到当前 KDevelop 会话中
    virtual bool AddSourceFiles(const TArray<FString>& AbsoluteSourcePaths, const TArray<FString>& AvailableModules) override;
};
```

### 进阶用法

1.  **自定义集成**：如果你需要开发一个类似的编辑器插件来集成其他 IDE，可以参考 `FKDevelopSourceCodeAccessor` 的实现模式：继承 `ISourceCodeAccessor` 接口，并在 `IModuleInterface` 的 `StartupModule` 中将其注册到引擎的源码访问器系统。
2.  **路径查找**：插件内部通过 `CanRunKDevelop` 函数查找 KDevelop 可执行文件路径，通常依赖系统 PATH 环境变量。如果集成遇到问题，检查此部分逻辑。

## Demo 示例

一个极简的、模仿 KDevelop 插件结构的源码访问器插件框架。

### `FMyIdeAccessor.h`
```cpp
#pragma once
#include "ISourceCodeAccessor.h"

class FMyIdeAccessor : public ISourceCodeAccessor
{
public:
    virtual bool CanAccessSourceCode() const override { return true; /* 简单示例 */ }
    virtual bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber) override
    {
        // 在这里实现调用你的IDE并打开文件的逻辑
        // 例如：FPlatformProcess::CreateProc(TEXT("MyEditor"), *CommandLineArgs, ...);
        UE_LOG(LogTemp, Log, TEXT("Would open file: %s at line %d"), *FullPath, LineNumber);
        return true;
    }
    // ... 实现其他接口函数 ...
};
```

### `FMyIdeAccessorModule.h`
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyIdeAccessorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        MyAccessor = MakeShared<FMyIdeAccessor>();
        // 在此处注册 MyAccessor 到引擎的源码访问器系统（需要研究引擎内部注册方式）
    }
    virtual void ShutdownModule() override {}

private:
    TSharedPtr<FMyIdeAccessor> MyAccessor;
};
```

## 模块依赖

从 `Build.cs` 分析，该插件仅依赖 `HotReload` 模块，这是一个常见的编辑器功能模块，用于支持热重载。

| 模块 | 用途 |
|---|---|
| `HotReload` | 支持 C++ 代码的热重载功能，与源码访问集成相关。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移为 UE_LOGF 格式，属于日志系统维护。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 仓库目录结构重组，该插件随其他插件一同迁移。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件元数据中的外部链接使用 HTTPS。 |
| 2022-04-14 | `6f118cb9` | Add ShortNames to Code Access plugins to reduce the pressure on path length. Problem reported on UDN | 为代码访问插件添加短名称，以减少路径长度压力。 |

### 维护评价

- **创建时间**：该插件非常古老，创建于 2014 年，是早期为支持 Linux 开发者所做的生态建设之一。
- **近期更新**：最近的实质性功能更新很少。2022 和 2026 年的提交主要是代码风格统一、日志系统迁移和目录整理等全局维护工作，**未涉及新功能或重要错误修复**。
- **活跃度**：作为一款功能稳定的 **编辑器扩展**，其核心功能（调用 KDevelop）在创建后已基本完善。由于 KDevelop 本身用户群体相对特定，且插件接口稳定，因此低频率维护是正常的。
- **已知限制**：仅支持 **Linux** 平台。其有效性依赖于系统正确安装并配置了 KDevelop。
- **推荐使用**：**推荐**给所有在 Linux 上使用 KDevelop 进行 UE C++ 开发的开发者。它是一个“设置即遗忘”的工具，虽然更新不频繁，但依然履行其设计功能。请确保它在你的引擎版本中处于 **启用状态**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/KDevelopSourceCodeAccess)
- [官方文档]（无）