# XCode Integration

> Allows access to source code in XCode.

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | XCodeSourceCodeAccess (UncookedOnly) |
| 创建时间 | 2014-04-23 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/XCodeSourceCodeAccess) | |

## 用途

这个 plugin 为 UE5 编辑器提供了 **Xcode 源码集成能力**。它实现了 `ISourceCodeAccessor` 接口，使得当用户在 UE 编辑器中点击 C++ 错误信息、蓝图反查源码等操作时，能够自动在 Xcode 中打开对应文件并定位到指定行号。

简单来说：它是 UE 编辑器和 Xcode 之间的"桥梁"——让你从编辑器一键跳转到 Xcode 中的源码位置。

该 plugin **仅在 macOS 上运行**，并且仅对 `UnrealFrontend` 和 `UnrealInsights` 两个程序生效（不包括主编辑器/游戏进程）。

### 核心机制

- 使用 macOS 的 **AppleScript** 来控制 Xcode（激活窗口、打开文件、跳转行号）
- 使用 `xed` 命令行工具（Xcode 自带）来打开文件并定位到具体行
- 支持区分引擎项目和"外部项目"（Foreign Project），自动定位正确的 `.xcworkspace` 路径

## 使用场景

- 你在 macOS 上开发 UE5 项目，使用 Xcode 作为主 IDE
- 你在 UnrealInsights 中查看性能数据，想快速跳转到相关源码
- 你在 UnrealFrontend 中遇到编译错误，想一键在 Xcode 中定位错误位置
- 你想从 UE 编辑器的调试信息中直接打开 Xcode 对应文件和行号

## 蓝图用法

本 plugin 没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是纯编辑器/工具层面的集成，通过 UE 的 `ISourceCodeAccessor` 模块化特性系统自动注册和使用。

用户无需在蓝图中做任何配置——只要 plugin 启用且 Xcode 已安装，编辑器会自动选择它作为源码访问器。

## C++ 用法

### 头文件引入

```cpp
#include "ISourceCodeAccessor.h"
#include "ISourceCodeAccessModule.h"
```

### 基本用法

本 plugin 主要通过模块化特性系统（Modular Features）自动工作。以下是其内部注册方式的参考：

```cpp
// 模块启动时注册为源码访问器（来自 XCodeSourceCodeAccessModule.cpp）
IModularFeatures::Get().RegisterModularFeature(TEXT("SourceCodeAccessor"), &XCodeSourceCodeAccessor);

// 关闭时注销
IModularFeatures::Get().UnregisterModularFeature(TEXT("SourceCodeAccessor"), &XCodeSourceCodeAccessor);
```

### 关键接口实现

`FXCodeSourceCodeAccessor` 实现了 `ISourceCodeAccessor` 的以下方法：

| 方法 | 说明 |
|---|---|
| `CanAccessSourceCode()` | 检查 Xcode 是否已安装（通过 `FPlatformMisc::GetXcodePath()`） |
| `OpenSolution()` | 打开项目的 `.xcworkspace` |
| `OpenFileAtLine()` | 使用 `xed -l <行号> <文件路径>` 命令在 Xcode 中打开文件并跳转到指定行 |
| `OpenSourceFiles()` | 通过系统默认应用打开源码文件 |
| `SaveAllOpenDocuments()` | 通过 AppleScript 调用 Xcode 的"保存所有文档"功能 |
| `DoesSolutionExist()` | 检查 `.xcworkspace` 文件是否存在 |

### 进阶用法

如果你需要编写自定义的源码访问器，可以参考本 plugin 的实现模式：

1. 实现 `ISourceCodeAccessor` 接口
2. 在模块 `StartupModule()` 中通过 `IModularFeatures` 注册
3. 在 `ShutdownModule()` 中注销

`GetSolutionPath()` 的逻辑值得参考——它能智能区分引擎源码项目和外部项目，自动构建正确的 workspace 路径：
- 引擎项目：`<RootDir>/UE5 (Mac).xcworkspace/contents.xcworkspacedata`
- 外部项目：`<ProjectDir>/<ProjectName> (Mac).xcworkspace/contents.xcworkspacedata`
- 如果现代命名的 workspace 不存在，会回退到旧格式 `<Name>.xcworkspace/contents.xcworkspacedata`

## Demo 示例

本 plugin 是一个完整的、开箱即用的参考实现。以下是创建类似源码访问器的最小模板：

```cpp
// MySourceCodeAccessor.h
#pragma once
#include "ISourceCodeAccessor.h"

class FMySourceCodeAccessor : public ISourceCodeAccessor
{
public:
    void Startup();
    void Shutdown();

    virtual bool CanAccessSourceCode() const override;
    virtual FName GetFName() const override;
    virtual FText GetNameText() const override;
    virtual FText GetDescriptionText() const override;
    virtual bool OpenSolution() override;
    virtual bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0) override;
    // ... 其他接口实现
};
```

```cpp
// MySourceCodeAccessModule.cpp
#include "Features/IModularFeatures.h"

void FMySourceCodeAccessModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(TEXT("SourceCodeAccessor"), &Accessor);
}

void FMySourceCodeAccessModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(TEXT("SourceCodeAccessor"), &Accessor);
}
```

Build.cs 依赖：
```csharp
PrivateDependencyModuleNames.AddRange(new string[] {
    "Core",
    "SourceCodeAccess",
    "DesktopPlatform"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `SourceCodeAccess` | 源码访问器接口定义（`ISourceCodeAccessor`） |
| `DesktopPlatform` | 平台相关功能（获取 Xcode 路径等） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2023-11-10 | `2267ffd9e4dc` | Improve source code lookup feature, using dsym if exists, and fix file path obtained from build machine | 改进了源码查找功能，支持使用 dSYM 符号文件，并修复了从构建机器获取文件路径的问题 |
| 2023-10-13 | `f59750d96859` | Fix for NavigateToFunctionSource crash/error, use xcode built in atos instead of UnrealAtoS as it can't handle universal build | 修复了导航到函数源码时的崩溃问题，改用 Xcode 内置的 `atos` 工具替代 UnrealAtoS |
| 2023-10-04 | `5fd6ad3d168a` | Fix Tools -> Open Xcode not working with modern Xcode | 修复了在新版 Xcode 中"工具 → 打开 Xcode"功能失效的问题 |

### 维护评价

- **年龄**：创建于 2014 年，已超过 10 年，属于"文物"级别的 plugin
- **最近更新**：最后实质性更新在 2023 年 11 月，距今约 2.5 年
- **维护状态**：**维护不活跃**——自 2023 年底以来没有新的功能性更新
- **稳定性**：代码量很小（约 250 行核心代码），逻辑简单稳定，不太需要频繁更新
- **限制**：
  - 仅支持 macOS 平台
  - 仅对 UnrealFrontend 和 UnrealInsights 生效
  - `OpenFileAtLine` 不支持列号定位（ColumnNumber 参数被忽略）
  - `AddSourceFiles` 始终返回 false（未实现）
- **推荐**：如果你在 macOS 上使用 Xcode 开发 UE5 且使用 UnrealInsights/UnrealFrontend，这个 plugin 是必需的。它默认启用，无需额外配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/XCodeSourceCodeAccess)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
