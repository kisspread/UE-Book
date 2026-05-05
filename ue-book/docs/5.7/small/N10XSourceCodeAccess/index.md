# 10X Editor Integration

> Allows access to source code in the 10X Editor .

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | ✅ |
| 包含内容 | ❌ |
| 模块 | N10XSourceCodeAccess (UncookedOnly) |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/N10XSourceCodeAccess) | |

## 用途

这个 plugin 为 Unreal Editor 提供与 [10X Editor](https://www.10xeditor.com/) 的源码访问集成。10X Editor 是一款 Windows 平台的代码编辑器（类似 Visual Studio），plugin 通过实现 `ISourceCodeAccessor` 接口，使 UE 编辑器能够：

- 点击编译错误/警告时直接在 10X 中打开对应文件并跳转到指定行
- 从 UE 编辑器的"打开 Visual Studio"按钮打开 10X Editor 及对应的 `.sln` 解决方案
- 批量打开源码文件

plugin 的工作原理是通过 Windows 注册表检测 10X Editor 的安装路径，然后通过 `FPlatformProcess::CreateProc` 启动 10X 进程并传递文件路径和行号参数。

## 使用场景

- 你在 Windows 上使用 10X Editor 作为主要 C++ 编辑器 → 启用此 plugin 即可让 UE 编辑器与 10X 联动
- 你从 UE 编辑器双击编译错误想直接跳到 10X 中的对应代码行 → 此 plugin 自动处理
- 你不想用 Visual Studio / Rider，偏好轻量级的 10X Editor → 这是官方提供的集成方案

## 蓝图用法

此 plugin 不暴露任何蓝图接口，纯编辑器功能集成。

## C++ 用法

此 plugin 是编辑器内部集成，不对外暴露公共 C++ API。以下仅供对内部实现感兴趣的开发者参考。

### 内部机制

10X Editor 的检测逻辑（`N10XSourceCodeAccessor.cpp`）：

```cpp
// 通过注册表检测 10X 安装路径
// 优先检查 shell 集成注册表项
const TCHAR* ClassesKey = TEXT("SOFTWARE\\Classes\\PureDevSoftware.10x.1\\shell\\open\\");
// 回退到安装目录注册表项
const TCHAR* InstallDirKey = TEXT("SOFTWARE\\PureDevSoftware\\10x\\");
```

跳转到指定行时，10X 使用 0-based 行号和列号（与 UE 的 1-based 不同），plugin 自动转换：

```cpp
// Column & line numbers are 1-based, 10X is 0 based
LineNumber = FMath::Max(LineNumber - 1, 0);
ColumnNumber = FMath::Max(ColumnNumber - 1, 0);
// 通过命令行参数传递: N10X.Editor.SetCursorPos((col, line))
Args.Add(FString::Printf(TEXT("N10X.Editor.SetCursorPos((%d,%d))"), ColumnNumber, LineNumber));
```

### 自定义 Source Code Accessor

如果你想为自己的编辑器编写类似集成，可以参考此 plugin 的结构：

1. 继承 `ISourceCodeAccessor` 接口
2. 在 `StartupModule()` 中通过 `IModularFeatures::Get().RegisterModularFeature(TEXT("SourceCodeAccessor"), ...)` 注册
3. 在 `ShutdownModule()` 中取消注册

## Demo 示例

此 plugin 无法通过代码示例演示。使用方式：

1. 在 Windows 上安装 [10X Editor](https://www.10xeditor.com/)
2. 确保 plugin 已启用（默认启用）：Edit → Plugins → 搜索 "10X"
3. 设置为默认源码访问器：Edit → Editor Preferences → General → Source Code → Source Code Editor → 选择 "10X Editor"
4. 在 Content Browser 中双击 C++ 类，或点击编译错误信息，即可在 10X 中打开

## 模块依赖

从 `N10XSourceCodeAccess.Build.cs` 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库（基础类型、文件路径等） |
| `SourceCodeAccess` | 源码访问器抽象接口（`ISourceCodeAccessor`） |
| `DesktopPlatform` | 桌面平台功能（注册表查询等） |
| `Projects` | 项目描述符访问 |
| `HotReload` | 热重载支持（仅 Editor 构建） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-03-25 | `3395567ae200` | PR #13018: Fix files not opening when file path contains spaces | Bug 修复：解决文件路径含空格时无法在 10X 中打开的问题 |
| 2024-10-07 | `d69a4c881695` | Fix 10x source code accessor to pull the correct solution file name | Bug 修复：修正获取 `.sln` 文件名的逻辑 |
| 2024-07-18 | `9eaacc953aa5` | [Backout] - CL34912307 | 回退一次 AutoRTFM 相关的代码迁移 |

### 维护评价

- **创建时间**: 2023-06-09，约 3 年前
- **最近更新**: 2025-03-25，约 1 年前有实质性 bug 修复
- **维护状态**: **维护中** — 更新频率较低但仍在修复问题
- **已知限制**: 仅支持 Windows 平台（`PlatformAllowList: Win64`），因为 10X Editor 是 Windows 专属编辑器
- **推荐**: 如果你使用 10X Editor，这是一个稳定可靠的官方集成 plugin，放心使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/N10XSourceCodeAccess)
- [10X Editor 官网](https://www.10xeditor.com/)
- [ISourceCodeAccessor 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Developer/SourceCodeAccess/Source/SourceCodeAccess/Public/ISourceCodeAccessor.h)
