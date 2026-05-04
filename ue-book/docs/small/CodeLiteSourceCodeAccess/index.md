# CodeLite Integration

> Allows access to source code in CodeLite.

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | CodeLiteSourceCodeAccess (UncookedOnly) |
| 创建时间 | 2015-07-14 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/CodeLiteSourceCodeAccess) | |

## 用途

CodeLiteSourceCodeAccess 是 UE5 的源码编辑器集成插件，将 [CodeLite](https://codelite.org/) IDE 注册为 UE5 的源码访问器（Source Code Accessor）。当开发者在 Linux 上使用 CodeLite 作为 C/C++ IDE 时，这个插件让 UE5 编辑器能够直接：

- 打开 CodeLite 工作区（`.workspace` 文件）
- 从 UE5 编辑器中的代码引用（如编译错误、蓝图中的"Go To Definition"）直接跳转到源文件的指定行
- 批量打开源文件

**仅限 Linux 平台**（`PlatformAllowList: ["Linux"]`）。CodeLite 是一款开源的跨平台 C/C++ IDE，在 Linux 上是除 VSCode/CLion 之外的一个常见选择。

插件通过 UE5 的 `ISourceCodeAccessor` 接口和 `IModularFeatures` 系统注册自身，编辑器会自动发现并使用它作为源码跳转的后端。

## 使用场景

- 你在 Linux 上使用 CodeLite IDE 开发 UE5 项目 → 启用此插件，UE5 编辑器会自动将代码跳转操作路由到 CodeLite
- 你在 UE5 编辑器中看到编译错误，双击错误行 → 自动在 CodeLite 中打开对应文件并定位到出错行
- 你在蓝图中右键一个 C++ 节点选择"Go to Definition" → 在 CodeLite 中打开对应源文件

## 蓝图用法

本插件不暴露任何蓝图 API。它是编辑器基础设施级别的插件，对用户透明——启用后，所有涉及"打开源码"的编辑器操作会自动使用 CodeLite 作为后端。

## C++ 用法

本插件不需要直接的 C++ 调用。它通过 UE5 的模块化特性系统（Modular Features）自动注册，编辑器的 `ISourceCodeAccess` 模块会在启动时发现并使用它。

如果你需要在自己的工具中程序化地访问源码访问器，可以通过 `IModularFeatures` 查询：

### 头文件引入

```cpp
#include "Features/IModularFeatures.h"
#include "ISourceCodeAccessor.h"
```

### 基本用法

```cpp
// 获取已注册的源码访问器列表
if (IModularFeatures::Get().IsModularFeatureAvailable(TEXT("SourceCodeAccessor")))
{
    // 遍历所有已注册的源码访问器（CodeLite、VS Code、Rider 等）
    int32 NumAccessors = IModularFeatures::Get().GetModularFeatureImplementationCount(TEXT("SourceCodeAccessor"));
    for (int32 i = 0; i < NumAccessors; i++)
    {
        ISourceCodeAccessor& Accessor = static_cast<ISourceCodeAccessor&>(
            IModularFeatures::Get().GetModularFeatureImplementation(TEXT("SourceCodeAccessor"), i));
        
        UE_LOG(LogTemp, Log, TEXT("Accessor: %s"), *Accessor.GetNameText().ToString());
    }
}
```

> 来源：`Source/CodeLiteSourceCodeAccess/Private/CodeLiteSourceCodeAccessModule.cpp` 中的注册方式。

### 工作区路径检测逻辑

插件会根据项目类型自动确定 `.workspace` 文件路径：

1. **非独立项目**（Non-Foreign Project）：工作区路径设为引擎根目录下的 `UnrealEditor.workspace`
2. **独立项目**（Foreign Project）：工作区路径设为项目目录下的 `{ProjectName}.workspace`

```cpp
// 源码逻辑简化展示（来自 CodeLiteSourceCodeAccessor.cpp）
if (!FUProjectDictionary::GetDefault().IsForeignProject(CachedSolutionPath))
{
    // 引擎内建项目：使用引擎根目录
    CachedSolutionPath = FPaths::Combine(FPaths::RootDir(), TEXT("UnrealEditor.workspace"));
}
else
{
    // 外部项目：使用项目目录 + 项目名
    FString BaseName = FApp::HasProjectName() ? FApp::GetProjectName() : FPaths::GetBaseFilename(CachedSolutionPath);
    CachedSolutionPath = FPaths::Combine(CachedSolutionPath, BaseName + TEXT(".workspace"));
}
```

## Demo 示例

本插件没有对外的编程接口，使用方式完全通过 UE5 编辑器 UI 操作：

1. 在 Linux 上安装 CodeLite（`sudo apt install codelite` 或从官网下载）
2. 确保 CodeLite 可执行文件位于 `/usr/bin/codelite`
3. 在 UE5 编辑器中，前往 **Editor Preferences → Source Code**，将 Source Code Editor 选择为 **CodeLite**
4. 使用 UE5 的代码跳转功能（如双击编译错误、Go to Definition），CodeLite 会自动启动并打开对应文件

### 已知限制

- **CodeLite 路径硬编码**：插件将 CodeLite 可执行文件路径硬编码为 `/usr/bin/codelite`，如果你通过 snap 或手动安装在其他路径，需要修改源码（`CanRunCodeLite` 函数）或创建符号链接
- **AddSourceFiles 未实现**：无法通过 UE5 向 CodeLite 工作区动态添加文件（标记为 TODO，需要 D-Bus 支持）
- **SaveAllOpenDocuments 未实现**：无法从 UE5 触发 CodeLite 的全部保存（标记为 TODO，需要 D-Bus 支持）
- **版本兼容性**：内部名称显示为 "CodeLite 7/8.x"，可能未适配更新版本的 CodeLite

## 模块依赖

从 `CodeLiteSourceCodeAccess.Build.cs` 的依赖声明提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心库，基础类型和平台抽象 |
| `SourceCodeAccess` | 源码访问器接口定义（`ISourceCodeAccessor`） |
| `DesktopPlatform` | 桌面平台工具函数 |
| `HotReload` | 热重载支持（仅编辑器构建） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-03-13 | `b059f7b46335` | Fix trivial unreachable code warnings. | 编译警告修复，非功能性更新 |
| 2023-01-16 | `bbc37aa2f5e6` | Another batch iwyu updates to reduce number of includes used in files | IWYU（Include What You Use）头文件清理，属于代码卫生维护 |
| 2022-04-14 | `6f118cb92253` | Add ShortNames to Code Access plugins to reduce the pressure on path length | 为 Code Access 类插件添加短名称，解决路径长度问题 |

### 维护评价

- **年龄**：创建于 2015 年 7 月，已有超过 10 年历史（🏛️ 文物）
- **更新频率**：最近一次功能性更新要追溯到多年前，近 3 次提交均为非功能性维护（编译警告修复、头文件清理、路径长度优化）
- **活跃度**：**维护不活跃**。超过 2 年没有实质性功能更新
- **已知问题**：多个 TODO 注释表明功能未完成（AddSourceFiles、SaveAllOpenDocuments、进程检测方式需改进）
- **IsBetaVersion = true**：官方仍标记为 Beta 版本
- **作者**：社区贡献者 Cengiz Terzibas (yaakuro)，非 Epic 官方维护

**建议**：如果你在 Linux 上使用 CodeLite 开发 UE5 项目，这个插件仍然可以使用（基本的文件打开和行号跳转功能正常）。但要注意 CodeLite 路径硬编码问题，以及部分高级功能缺失。如果你使用其他 IDE（如 VS Code、Rider、CLion），应选择对应的源码访问插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/CodeLiteSourceCodeAccess)
- [CodeLite 官网](https://codelite.org/)
