# Visual Studio Code Integration

> Allows access to source code in Visual Studio Code.

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | VisualStudioCodeSourceCodeAccess (UncookedOnly) |
| 创建时间 | 2017-08-31 |
| 年龄标签 | 👴 老古董（~8.7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/VisualStudioCodeSourceCodeAccess) | |

## 用途

这个 plugin 是 UE5 编辑器与 Visual Studio Code 之间的**源码访问桥接器**。它实现了 `ISourceCodeAccessor` 接口，使得 UE 编辑器能够：

- 在 VS Code 中打开源码文件（支持定位到具体行号和列号）
- 打开 `.code-workspace` 工作区文件
- 在编译前自动保存 VS Code 中打开的文档

它**不是**一个代码编辑器插件，而是 UE 编辑器的 "Source Code Access" 框架的提供者（Provider）。当你在 UE 编辑器中双击某个 C++ 错误、或右键 "Go to Source" 时，编辑器通过这个框架找到对应的 IDE 并打开文件。本 plugin 将这个行为指向 VS Code。

## 使用场景

- 你使用 VS Code 作为 UE5 项目的主力 IDE（而非 Visual Studio / Rider）
- 你需要从 UE 编辑器的 Output Log 中双击编译错误直接跳转到 VS Code 中对应文件
- 你的团队在 Linux 或 macOS 上开发，VS Code 比 Visual Studio 更通用

## 蓝图用法

本 plugin 不暴露任何蓝图节点。它是纯编辑器级别的 IDE 集成，不参与游戏逻辑。

## C++ 用法

### 工作原理

本 plugin 通过 UE 的 Modular Features 系统注册为 `SourceCodeAccessor`。核心逻辑在 `FVisualStudioCodeSourceCodeAccessor` 类中：

**VS Code 可执行文件发现**（跨平台）：

| 平台 | 发现方式 |
|---|---|
| Windows | 读注册表 `HKCU/HKLM\SOFTWARE\Classes\Applications\Code.exe\shell\open\command` |
| Linux | 执行 `type -p code`，回退到 `/usr/bin/code` |
| macOS | 通过 `NSWorkspace` 查询 bundle ID `com.microsoft.VSCode` |

**工作区路径推导**：

- 引擎项目（非 Foreign Project）：`{RootDir}/UE5.code-workspace`
- 独立项目：`{ProjectDir}/{ProjectName}.code-workspace`

### 核心类

```cpp
// FVisualStudioCodeSourceCodeAccessor 继承 ISourceCodeAccessor
// 路径: Source/VisualStudioCodeSourceCodeAccess/Private/VisualStudioCodeSourceCodeAccessor.h

class FVisualStudioCodeSourceCodeAccessor : public ISourceCodeAccessor
{
    // 打开 VS Code 并定位到指定文件的行号/列号
    bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0);

    // 打开工作区
    bool OpenSolution();

    // 在 VS Code 中打开多个源码文件
    bool OpenSourceFiles(const TArray<FString>& AbsoluteSourcePaths);

    // 检测 VS Code 是否可用
    bool CanAccessSourceCode() const;
};
```

### 作为 Modular Feature 注册

```cpp
// Source/VisualStudioCodeSourceCodeAccess/Private/VisualStudioCodeSourceCodeAccessModule.cpp
void FVisualStudioCodeSourceCodeAccessModule::StartupModule()
{
    VisualStudioCodeSourceCodeAccessor->Startup();
    // 注册为 SourceCodeAccessor，UE 编辑器会自动发现
    IModularFeatures::Get().RegisterModularFeature(
        TEXT("SourceCodeAccessor"),
        &VisualStudioCodeSourceCodeAccessor.Get()
    );
}
```

### 如何切换到 VS Code

UE 编辑器中切换源码访问器的路径：

**Edit → Editor Preferences → General → Source Code → Source Code Editor**

在下拉菜单中选择 "Visual Studio Code"。只有已注册且可用的 accessors 才会出现在列表中。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `SourceCodeAccess` | `ISourceCodeAccessor` 接口定义框架 |
| `DesktopPlatform` | 平台相关的桌面操作（注册表查询等） |
| `HotReload` | 热重载支持（仅编辑器构建时依赖） |

使用者不需要手动添加这些依赖——本 plugin 自包含，不对外暴露公共 API。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-02-01 | `8a8968c` | Fix some dotnet warnings | 修复 .NET 相关的编译警告，无功能变更 |
| 2024-01-26 | `fde9624` | UnrealBuildTool: Remove VS2019 support | 移除 VS2019 支持，Build.cs 中 DTE key 仅保留 VS2022 |
| 2023-12-21 | `9cfbb6a` | Fix warnings in ModuleRules | 修复 Build.cs 中的警告，无功能变更 |

### 维护评价

- **创建时间**：2017-08-31，近 9 年历史
- **最近更新**：2024-02-01，距今超过 2 年
- **更新内容**：最近 3 次提交全部是编译警告修复和工具链清理，**无实质性功能更新**
- **代码规模**：仅 4 个源码文件（2 .h + 2 .cpp），非常小巧
- **平台支持**：Win64、Linux、Mac 三平台

⚠️ **超过 2 年没有实质性功能更新**。但考虑到本 plugin 功能单一且稳定（只是包装 `code` 命令行），这不一定是问题。它更像是一个"已完成"的基础设施工具。

✅ **推荐使用**：如果你用 VS Code 开发 UE5 项目，这是必装的 plugin。它默认启用，通常无需额外配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/VisualStudioCodeSourceCodeAccess)
- [ISourceCodeAccessor 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Developer/SourceCodeAccess/Public/ISourceCodeAccessor.h)
- 测试用例：无（本 plugin 无自动化测试）
