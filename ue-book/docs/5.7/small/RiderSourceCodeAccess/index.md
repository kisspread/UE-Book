# Rider Integration

> Allows access to source code in Rider.

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 否 |
| 模块 | RiderSourceCodeAccess (EditorNoCommandlet) |
| 创建时间 | 2020-02-22 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/RiderSourceCodeAccess) | |

## 用途

这个 plugin 是 **JetBrains Rider IDE 的源码访问集成**，实现了 UE 的 `ISourceCodeAccessor` 接口。

它解决的核心问题是：**让 UE 编辑器能够直接从编辑器内部打开 Rider IDE 并定位到对应的源码文件和行号**。当你在 UE 编辑器中点击 "Open Source Code" 或双击编译错误时，如果没有这个 plugin，编辑器不知道如何启动 Rider。有了它，Rider 会像 Visual Studio 一样无缝集成。

具体功能：
- **自动检测 Rider 安装路径**：支持 Windows（注册表 + JetBrains Toolbox）、Mac（mdfind + Applications）、Linux（`~/.local/share`）多种安装方式
- **打开 .sln 解决方案**：传统方式，Rider 打开 VS Solution 文件
- **打开 .uproject 直接项目**：Rider 的 uproject 原生支持模式（不需要生成 .sln）
- **定位到文件和行号**：从 UE 编辑器双击错误时，Rider 自动跳转到对应位置
- **批量打开多个源码文件**
- **自动生成 Solution 文件**：如果 .sln 不存在，会提示用户并自动调用 UE 的项目生成器
- **多版本 Rider 管理**：如果系统上装了多个版本的 Rider，每个版本都会注册为独立的源码访问器

## 使用场景

- 你使用 JetBrains Rider 作为 UE5 的 C++ IDE → 安装 Rider 后此 plugin **默认自动启用**，无需额外配置
- 你在 UE 编辑器中双击编译错误 → Rider 自动打开并定位到出错的源码行
- 你在 UE 编辑器中点击某个 C++ 类 → Rider 打开对应头文件
- 你系统上装了多个 Rider 版本（如 stable + EAP）→ 每个版本都会出现在编辑器的源码访问器列表中

## 蓝图用法

此 plugin **不暴露任何蓝图接口**。它是纯编辑器集成插件，所有交互通过 UE 编辑器的 Source Code Access 设置完成。

### 配置方式

1. **自动启用**：`EnabledByDefault=true`，安装 Rider 后无需手动启用
2. **选择源码访问器**：`Edit → Editor Preferences → Source Code → Source Code Editor` 中选择对应版本的 Rider
3. **Project Model 选择**：
   - `Rider xxx (installed/toolbox/custom)` — Sln 模式，生成 .sln 文件
   - `Rider xxx Uproject` — uproject 直接打开模式（推荐）

## C++ 用法

此 plugin 是编辑器基础设施，普通项目代码不需要直接引用它。但如果你需要扩展或定制 IDE 集成，以下是关键接口：

### 头文件引入

```cpp
#include "ISourceCodeAccessor.h"
```

### 核心接口

plugin 实现了 `ISourceCodeAccessor` 接口（来自 `SourceCodeAccess` 模块），所有方法：

```cpp
// 检查 Rider 是否已安装
bool FRiderSourceCodeAccessor::CanAccessSourceCode() const;

// 打开 Rider 并加载 .sln 或 .uproject
bool FRiderSourceCodeAccessor::OpenSolution();

// 打开指定文件并定位到行号（双击编译错误时调用）
bool FRiderSourceCodeAccessor::OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0);

// 批量打开源码文件
bool FRiderSourceCodeAccessor::OpenSourceFiles(const TArray<FString>& AbsoluteSourcePaths);
```

### 项目模型（EProjectModel）

```cpp
enum class EProjectModel
{
    Sln,      // 传统 .sln 模式，需要先生成 Solution 文件
    Uproject  // 直接用 .uproject 打开，Rider 自行解析项目结构
};
```

Uproject 模式下 `AddSourceFiles` 返回 `true`（Rider 通过文件系统监听自动更新项目），Sln 模式返回 `false`。

### 路径检测（RiderPathLocator）

`FRiderPathLocator::CollectAllPaths()` 会扫描所有已安装的 Rider：

| 平台 | 检测方式 |
|---|---|
| Windows | 注册表 `HKLM\SOFTWARE\JetBrains` + JetBrains Toolbox + 自定义路径 |
| Mac | `mdfind` 搜索 `Applications/` + JetBrains Toolbox |
| Linux | `~/.local/share/applications/` + JetBrains Toolbox |

## Demo 示例

此 plugin 没有可运行的 Demo——它是纯编辑器集成。如果你需要实现类似的 IDE 集成 plugin，参考以下骨架：

### Build.cs 依赖

```csharp
// 参考 RiderSourceCodeAccess.Build.cs
PrivateDependencyModuleNames.AddRange(new []
{
    "Core",
    "SourceCodeAccess",    // ISourceCodeAccessor 接口
    "DesktopPlatform",     // 平台相关操作
    "Projects",            // 项目信息
    "Json",                // 解析 Toolbox JSON
    "Slate",               // UI 通知
    "SlateCore"
});

if (Target.Type == TargetType.Editor)
{
    PrivateDependencyModuleNames.Add("UnrealEd");
    PrivateDependencyModuleNames.Add("GameProjectGeneration"); // 生成 .sln
}
```

### 注册 Source Code Accessor

```cpp
// 在模块 StartupModule 中
TSharedRef<FRiderSourceCodeAccessor> Accessor = MakeShareable(new FRiderSourceCodeAccessor());
Accessor->Init(InstallInfo, EProjectModel::Sln);
IModularFeatures::Get().RegisterModularFeature(
    FRiderSourceCodeAccessor::FeatureType(), &Accessor.Get());
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础功能（路径、进程、日志） |
| `SourceCodeAccess` | `ISourceCodeAccessor` 接口定义 |
| `DesktopPlatform` | 平台相关功能（文件对话框等） |
| `Projects` | 项目信息查询 |
| `Json` | 解析 JetBrains Toolbox 的 `product-info.json` 和 `history.json` |
| `Slate` / `SlateCore` | 通知 UI 和图标样式 |
| `UnrealEd` | 编辑器功能（仅 Editor target） |
| `GameProjectGeneration` | 生成 .sln 文件（仅 Editor target） |
| `EditorFramework` | UE 5.0+ 编辑器框架 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `dd92de3` | 修复 Mac 上 `mdfind` 搜索 Rider 路径时因匹配 Shader 编译调试文件导致的严重性能问题（从数分钟降到秒级） |
| 2023-11-27 | `391ea57` | 修复源码文件缺失的版权声明头 |
| 2023-11-27 | `873e77b` | 为 SourceCodeAccess 实现指定正确的图标样式集 |

### 维护评价

- **创建时间**：2020-02-22，已有 6+ 年历史
- **最近更新**：2025-09 有实质性修复（Mac 性能优化），说明仍在维护
- **更新频率**：较低，但 plugin 功能本身已经很稳定，不需要频繁更新
- **维护者**：JetBrains 官方（由 Epic 代为集成到引擎）
- **已知限制**：
  - Sln 模式仅在 Windows 上支持（`#if PLATFORM_WINDOWS`）
  - Uproject 模式跨平台，但标记为 Beta/Experimental（取决于 Rider 版本）
  - `SaveAllOpenDocuments()` 返回 `false`（无法从 UE 编辑器保存 Rider 中的文件）
- **推荐使用**：✅ **强烈推荐**——如果你用 Rider 做 UE 开发，这是必备 plugin

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/RiderSourceCodeAccess)
- [JetBrains 仓库](https://github.com/JetBrains/RiderSourceCodeAccess)
- [JetBrains Rider](https://www.jetbrains.com/rider/)
